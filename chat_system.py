from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_core.runnables.history import RunnableWithMessageHistory
from typing import List, Dict, Any
import streamlit as st
from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL_NAME,
    MAX_MEMORY_HISTORY,
    MAX_CONTEXT_CHUNKS
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


class ChatSystem:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=OPENAI_MODEL_NAME,
            temperature=0.7,
            max_tokens=1000
        )

        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            k=MAX_MEMORY_HISTORY,
            memory_key="chat_history",
            return_messages=True
        )

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

    def chat(self, user_input: str) -> Dict[str, Any]:
        """Process user input and return AI response."""
        try:
            if not self.conversation_chain:
                return {
                    "response": "Sorry, the chat system is not properly initialized. Please check your configuration.",
                    "source_documents": [],
                    "error": "Chat system not initialized"
                }

            # Get response from conversation chain
            result = self.conversation_chain.invoke(
                {"question": user_input},
                config={"configurable": {"session_id": "default_session"}}
            )

            return {
                "response": result["answer"],
                "source_documents": result.get("source_documents", []),
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
