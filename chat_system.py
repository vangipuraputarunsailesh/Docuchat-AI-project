from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_core.runnables.history import RunnableWithMessageHistory
from typing import List, Dict, Any
import streamlit as st
import json
from pathlib import Path
from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL_NAME,
    MAX_MEMORY_HISTORY,
    MAX_CONTEXT_CHUNKS,
    OPENAI_TEMPERATURE
)


# Strict QA prompt: force the model to answer only from the provided context.
STRICT_QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are a helpful and confident AI assistant. Answer the question based ONLY on the information in the provided CONTEXT below."
        " Answer clearly and directly. If the user asks for confirmation (like 'are you sure?'), confidently confirm your answer if it's based on the context."
        " If the answer cannot be found in the CONTEXT, politely state that the information is not available in the uploaded documents."
        "\n\nCONTEXT:\n{context}\n\nQUESTION:\n{question}\n\nANSWER:"
    )
)


# ✅ Small wrapper to make memory compatible with RunnableWithMessageHistory
class MemoryWrapper:
    def __init__(self, memory):
        self.memory = memory

    @property
    def messages(self):
        # Return chat messages from ConversationBufferWindowMemory
        return self.memory.chat_memory.messages

    def add_message(self, message):
        # Add messages correctly to the wrapped memory
        self.memory.chat_memory.add_message(message)
        # Persist full chat to disk after every new message
        try:
            mem_file = Path("chat_memory.json")
            msgs = []
            for m in self.memory.chat_memory.messages:
                if isinstance(m, HumanMessage):
                    role = "user"
                elif isinstance(m, AIMessage):
                    role = "assistant"
                else:
                    role = "system"
                msgs.append({"role": role, "content": m.content})
            with mem_file.open("w", encoding="utf-8") as f:
                json.dump(msgs, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add_messages(self, messages):
        # RunnableWithMessageHistory may call add_messages; forward to underlying memory
        for message in messages:
            self.add_message(message)


class ChatSystem:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=OPENAI_MODEL_NAME,
            temperature=OPENAI_TEMPERATURE,
            max_tokens=1000
        )

        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # Load persisted memory from disk (if present)
        try:
            mem_file = Path("chat_memory.json")
            if mem_file.exists():
                with mem_file.open("r", encoding="utf-8") as f:
                    saved = json.load(f)
                for item in saved:
                    role = item.get("role")
                    content = item.get("content", "")
                    if role == "user":
                        self.memory.chat_memory.add_message(HumanMessage(content=content))
                    elif role == "assistant":
                        self.memory.chat_memory.add_message(AIMessage(content=content))
        except Exception:
            # ignore load errors and continue with empty memory
            pass

        # Initialize conversation chain
        self.conversation_chain = None
        self._initialize_conversation_chain()

    def _initialize_conversation_chain(self):
        """Initialize the conversational retrieval chain."""
        try:
            print("🔄 Checking vector store...")
            if not self.vector_store.vectorstore:
                print("❌ Vector store not initialized - trying to initialize...")
                if not self.vector_store.initialize_vectorstore():
                    print("❌ Failed to initialize vector store")
                    return

            print("🔄 Initializing conversation chain...")
            base_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.vector_store.vectorstore.as_retriever(
                    search_kwargs={"k": MAX_CONTEXT_CHUNKS}
                ),
                return_source_documents=True,
                verbose=False
            )

            # ✅ Wrap memory with a compatibility layer
            wrapped_memory = MemoryWrapper(self.memory)

            self.conversation_chain = RunnableWithMessageHistory(
                base_chain,
                lambda session_id: wrapped_memory,  # use wrapped memory
                input_messages_key="question",
                history_messages_key="chat_history",
                output_messages_key="answer",  # ✅ fix for multiple output keys
            )

            print("✅ Conversation chain initialized successfully")

        except Exception as e:
            print(f"❌ Error initializing conversation chain: {str(e)}")
            st.error(f"Error initializing conversation chain: {str(e)}")

    def chat(self, user_input: str, source_filter: str = None) -> Dict[str, Any]:
        """Process user input and return AI response."""
        try:
            if not self.conversation_chain:
                return {
                    "response": "Sorry, the chat system is not properly initialized. Please check your configuration.",
                    "source_documents": [],
                    "error": "Chat system not initialized"
                }

            # Quick pre-filter: ignore short pleasantries/acknowledgements
            try:
                plain = (user_input or "").strip().lower()
            except Exception:
                plain = ""

            # Common greetings and pleasantries
            GREETINGS = {
                "hi", "hello", "hey", "good morning", "good afternoon", "good evening"
            }

            PLEASANTRIES = {
                "ok",
                "okay",
                "thanks",
                "thank you",
                "thankyou",
                "thx",
                "thanks!",
                "thankyou!",
                "bye",
                "goodbye"
            }

            # If the user greets, reply politely (skip retrieval/QA)
            if plain in GREETINGS:
                try:
                    prompt = (
                        "The user greeted you with: '" + (user_input or "") + "'. "
                        "Reply briefly and politely in one sentence, and invite them to ask about their uploaded documents."
                    )
                    ai_msg = self.llm.invoke([HumanMessage(content=prompt)])
                    reply = getattr(ai_msg, "content", None) or "Hello! How can I help with your uploaded documents today?"
                except Exception:
                    reply = "Hello! How can I help with your uploaded documents today?"
                return {"response": reply, "source_documents": [], "error": None}

            # If it's a simple acknowledgement/pleasantry, acknowledge politely
            if plain in PLEASANTRIES or len(plain) <= 2:
                try:
                    prompt = (
                        "The user wrote an acknowledgement: '" + (user_input or "") + "'. "
                        "Reply with a short friendly acknowledgement (one sentence) and invite them to ask anything about their uploaded documents."
                    )
                    ai_msg = self.llm.invoke([HumanMessage(content=prompt)])
                    reply = getattr(ai_msg, "content", None) or "You're welcome! If you have more questions about your documents, just ask."
                except Exception:
                    reply = "You're welcome! If you have more questions about your documents, just ask."
                return {"response": reply, "source_documents": [], "error": None}

            # For debugging & control: perform retrieval first so we can decide to refuse
            try:
                retriever = self.vector_store.vectorstore.as_retriever(search_kwargs={"k": MAX_CONTEXT_CHUNKS})
                retrieved_docs = retriever.get_relevant_documents(user_input)
                # If a source_filter (upload_id or filename) is provided, restrict retrieved docs
                # Only filter if source_filter is not None (when "All Documents" is selected, source_filter is None)
                if source_filter is not None:
                    # Prefer upload_id match (new metadata), fallback to filename match
                    filtered = [d for d in retrieved_docs if (d.metadata or {}).get("upload_id") == source_filter]
                    if not filtered:
                        # Fallback: try matching by source filename
                        filtered = [d for d in retrieved_docs if (d.metadata or {}).get("source") == source_filter]
                    # Only apply filter if we actually found matching documents
                    # This prevents filtering out everything when upload_id doesn't exist
                    if filtered:
                        retrieved_docs = filtered
            except Exception:
                retrieved_docs = []

            # If retrieval returned nothing or content is too small, refuse to answer to avoid hallucination
            MIN_RELEVANT_CHARS = 50
            total_chars = sum(len((d.page_content or "").strip()) for d in retrieved_docs)
            if not retrieved_docs or total_chars < MIN_RELEVANT_CHARS:
                return {
                    "response": "I don't know the answer to that based on the uploaded documents. I can only answer questions supported by the provided documents.",
                    "source_documents": [],
                    "error": None
                }

            # Prepend a strict instruction so the LLM uses ONLY the retrieved documents.
            question_with_instruction = (
                "Use ONLY the provided retrieved documents to answer the question. "
                "If the answer cannot be found in those documents, reply exactly: 'I don't know the answer based on the provided documents.' Do not provide any additional information. "
                f"Question: {user_input}"
            )

            result = self.conversation_chain.invoke(
                {"question": question_with_instruction},
                config={"configurable": {"session_id": "default_session"}}
            )

            # Return retrieved docs alongside the model answer for easier debugging
            return {
                "response": result.get("answer"),
                "source_documents": result.get("source_documents", []) or retrieved_docs,
                "error": None
            }

        except Exception as e:
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "source_documents": [],
                "error": str(e)
            }

    def get_chat_history(self) -> List[Dict[str, str]]:
        """Get the current chat history."""
        try:
            history = []
            for message in self.memory.chat_memory.messages:
                if isinstance(message, HumanMessage):
                    history.append({"role": "user", "content": message.content})
                elif isinstance(message, AIMessage):
                    history.append({"role": "assistant", "content": message.content})
            return history
        except Exception as e:
            st.error(f"Error getting chat history: {str(e)}")
            return []

    def clear_memory(self):
        """Clear the conversation memory."""
        try:
            self.memory.clear()
            st.success("Chat memory cleared successfully!")
        except Exception as e:
            st.error(f"Error clearing memory: {str(e)}")

    def get_context_info(self, query: str) -> Dict[str, Any]:
        """Get context information for a query without generating a response."""
        try:
            if not self.vector_store.vectorstore:
                return {"documents": [], "error": "Vector store not initialized"}

            # Perform similarity search
            documents = self.vector_store.similarity_search(query, k=MAX_CONTEXT_CHUNKS)

            context_info = {
                "documents": [
                    {
                        "content": (
                            doc.page_content[:200] + "..."
                            if len(doc.page_content) > 200
                            else doc.page_content
                        ),
                        "metadata": doc.metadata,
                        "relevance_score": "N/A"
                    }
                    for doc in documents
                ],
                "error": None
            }

            return context_info

        except Exception as e:
            return {"documents": [], "error": str(e)}
