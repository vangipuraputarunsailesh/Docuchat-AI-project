import streamlit as st
import os
import tempfile
from typing import List, Dict
import pandas as pd
from datetime import datetime

# Import your custom modules
from document_processor import DocumentProcessor
from vector_store import VectorStore
from chat_system import ChatSystem
from config import SUPPORTED_EXTENSIONS

# ---------------------- ⚙️ Page Config ----------------------
st.set_page_config(
    page_title="DocuChat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- 🎨 Custom CSS ----------------------
st.markdown("""
<style>
/* Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f8faff 0%, #f3f6ff 100%);
    color: #222;
    font-family: "Segoe UI", Roboto, sans-serif;
}

/* Header */
.main-header {
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0.5rem;
    background: linear-gradient(90deg, #5b7cfa 0%, #8a56f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sub-header {
    text-align: center;
    font-size: 1.1rem;
    color: #555;
    margin-bottom: 2rem;
}

/* Chat Bubbles */
.chat-message {
    padding: 1rem 1.5rem;
    border-radius: 1rem;
    margin: 1rem 0;
    max-width: 85%;
    line-height: 1.6;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
    animation: fadeIn 0.4s ease;
}
.user-message {
    background-color: #e8f0fe;
    margin-left: auto;
    border: 1px solid #c9dafc;
}
.assistant-message {
    background-color: #f4e9ff;
    margin-right: auto;
    border: 1px solid #dec9ff;
}
.source-doc {
    background-color: #fafafa;
    padding: 0.5rem;
    border-radius: 0.5rem;
    margin-top: 0.4rem;
    border: 1px solid #e3e3e3;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #f6f8ff;
    border-right: 1px solid #e6e9f2;
}
.sidebar-header {
    font-size: 1.2rem;
    font-weight: 600;
    color: #333;
    margin-top: 1rem;
    margin-bottom: 0.3rem;
}

/* Buttons */
.stButton>button {
    border-radius: 10px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    color: white;
    font-weight: 600;
    border: none;
    padding: 0.5rem 1rem;
    transition: all 0.2s ease-in-out;
}
.stButton>button:hover {
    transform: scale(1.03);
    background: linear-gradient(90deg, #556de8, #693b9d);
}

/* Footer */
.footer {
    text-align: center;
    font-size: 0.9rem;
    margin-top: 3rem;
    padding: 1rem 0;
    color: #555;
}
.footer a {
    text-decoration: none;
    margin: 0 8px;
    color: #5b7cfa;
    transition: 0.2s ease-in-out;
}
.footer a:hover {
    color: #764ba2;
    text-decoration: underline;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# ---------------------- 🧠 Helper Functions ----------------------
def initialize_session_state():
    """Initialize app session variables."""
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = VectorStore()
    if 'document_processor' not in st.session_state:
        st.session_state.document_processor = DocumentProcessor()
    if 'chat_system' not in st.session_state:
        st.session_state.chat_system = ChatSystem(st.session_state.vector_store)
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'source_documents_cache' not in st.session_state:
        st.session_state.source_documents_cache = {}

def display_chat_message(role: str, content: str, source_docs: List[Dict] = None):
    """Display chat messages with styling."""
    if role == "user":
        st.markdown(f'<div class="chat-message user-message"><strong>🧑 You:</strong><br>{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message assistant-message"><strong>🤖 DocuChat:</strong><br>{content}</div>', unsafe_allow_html=True)
        if source_docs:
            with st.expander("📚 View Source Documents"):
                for i, doc in enumerate(source_docs):
                    st.markdown(f'<div class="source-doc"><strong>Source {i+1}:</strong><br>{doc["content"]}</div>', unsafe_allow_html=True)

# ---------------------- 💬 Main App ----------------------
def main():
    initialize_session_state()

    # Main Title
    st.markdown('<h1 class="main-header">💬 DocuChat</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your personal AI that understands and answers from your documents.</p>', unsafe_allow_html=True)

    # Sidebar Section
    with st.sidebar:
        st.markdown("### 💬 Welcome to DocuChat")
        st.markdown("_Ask questions, summarize, or extract insights from your documents — instantly._")

        st.markdown('<div class="sidebar-header">📁 Document Management</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Upload your PDFs, TXT, or MD files",
                                          type=[ext[1:] for ext in SUPPORTED_EXTENSIONS],
                                          accept_multiple_files=True)

        st.markdown('<div class="sidebar-header">🌐 Web Article</div>', unsafe_allow_html=True)
        web_url = st.text_input("Enter website URL:")
        if st.button("Process Web Article"):
            if web_url:
                with st.spinner("🔍 Extracting and embedding content..."):
                    docs = st.session_state.document_processor.process_web_article(web_url)
                    if docs and st.session_state.vector_store.add_documents(docs):
                        st.success(f"✅ Added {len(docs)} chunks from the article.")
                    else:
                        st.error("❌ Could not process this URL.")

        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file not in st.session_state.uploaded_files:
                    st.session_state.uploaded_files.append(uploaded_file)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    with st.spinner(f"📄 Processing {uploaded_file.name}..."):
                        docs = st.session_state.document_processor.process_file(tmp_path)
                        if docs and st.session_state.vector_store.add_documents(docs):
                            st.success(f"✅ {uploaded_file.name} added successfully!")
                        else:
                            st.error(f"❌ Failed to process {uploaded_file.name}.")
                    os.unlink(tmp_path)

        st.divider()
        info = st.session_state.vector_store.get_collection_info()
        if info["error"]:
            st.error(f"Error: {info['error']}")
        else:
            st.info(f"**Total Chunks in Knowledge Base:** {info['count']}")

        if st.button("🗑️ Clear Knowledge Base"):
            if st.session_state.vector_store.clear_collection():
                st.success("Knowledge base cleared.")
                st.rerun()
        if st.button("🧹 Clear Chat Memory"):
            st.session_state.chat_system.clear_memory()
            st.session_state.chat_history = []
            st.success("Chat memory cleared.")
            st.rerun()

    # Chat Area
    st.markdown("### 💬 Chat with Your Knowledge Base")
    user_input = st.chat_input("Ask something about your uploaded data...")

    for msg in st.session_state.chat_history:
        display_chat_message(msg["role"], msg["content"], msg.get("source_docs", []))

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input, "timestamp": datetime.now()})
        display_chat_message("user", user_input)

        with st.spinner("🤔 Thinking..."):
            result = st.session_state.chat_system.chat(user_input)
            if result["error"]:
                st.error(result["error"])
            else:
                source_docs = [
                    {"content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                     "metadata": doc.metadata}
                    for doc in result.get("source_documents", [])
                ]
                if source_docs:
                    st.session_state.source_documents_cache[user_input] = source_docs
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result["response"],
                    "source_docs": source_docs,
                    "timestamp": datetime.now()
                })
                display_chat_message("assistant", result["response"], source_docs)

    # Export Section
    with st.expander("📥 Export Chat or Explore Questions"):
        if st.session_state.chat_history:
            df = pd.DataFrame([
                {"Role": m["role"].title(), "Content": m["content"], "Timestamp": m["timestamp"].strftime("%Y-%m-%d %H:%M:%S")}
                for m in st.session_state.chat_history
            ])
            csv = df.to_csv(index=False)
            st.download_button("⬇️ Download Chat History (CSV)", csv,
                               file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                               mime="text/csv")

        st.markdown("#### 💡 Try asking:")
        st.markdown("- What are the main topics discussed?")
        st.markdown("- Summarize the key insights.")
        st.markdown("- How do the documents relate to each other?")
        st.markdown("- What are the conclusions or recommendations?")

    # ---------------------- 👣 Footer Branding ----------------------
    st.markdown("""
        <div class="footer">
            <p>🤖 <strong>DocuChat</strong> — Built by <strong>Tarun Sailesh Vangipurapu</strong> using <strong>Streamlit</strong>, <strong>LangChain</strong> & <strong>OpenAI</strong>.</p>
            <p>
                <a href="https://www.linkedin.com/in/tarun-sailesh-vangipurapu" target="_blank">💼 LinkedIn</a> |
                <a href="https://github.com/vangipuraputarunsailesh" target="_blank">💻 GitHub</a> |
                <a href="mailto:tarunsailesh9@gmail.com">📧 Email</a>
            </p>
        </div>
    """, unsafe_allow_html=True)

# Run app
if __name__ == "__main__":
    main()
