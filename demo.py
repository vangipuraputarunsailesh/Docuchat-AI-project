#!/usr/bin/env python3
"""
Demo script for AI Knowledge Vault
This script demonstrates the core functionality without the Streamlit UI
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from document_processor import DocumentProcessor
from vector_store import VectorStore
from chat_system import ChatSystem

def demo_document_processing():
    """Demonstrate document processing functionality."""
    print("📄 Document Processing Demo")
    print("-" * 30)
    
    processor = DocumentProcessor()
    
    # Create a sample text file
    sample_text = """
    Artificial Intelligence (AI) is a branch of computer science that aims to create 
    intelligent machines that can perform tasks that typically require human intelligence.
    
    Machine Learning is a subset of AI that focuses on algorithms that can learn and 
    make decisions from data without being explicitly programmed.
    
    Deep Learning is a subset of machine learning that uses neural networks with multiple 
    layers to model and understand complex patterns in data.
    
    Natural Language Processing (NLP) is a field of AI that focuses on the interaction 
    between computers and humans through natural language.
    
    Computer Vision is a field of AI that enables computers to interpret and understand 
    visual information from the world.
    """
    
    # Save sample text to file
    sample_file = "sample_ai_document.txt"
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write(sample_text)
    
    print(f"Created sample document: {sample_file}")
    
    # Process the document
    documents = processor.process_file(sample_file)
    print(f"Processed into {len(documents)} chunks")
    
    # Display first chunk
    if documents:
        print(f"\nFirst chunk preview:")
        print(f"Content: {documents[0].page_content[:100]}...")
        print(f"Metadata: {documents[0].metadata}")
    
    return documents, sample_file

def demo_vector_store(documents):
    """Demonstrate vector store functionality."""
    print("\n🗄️ Vector Store Demo")
    print("-" * 30)
    
    vector_store = VectorStore()
    
    # Initialize vector store
    if vector_store.initialize_vectorstore():
        print("✅ Vector store initialized")
    else:
        print("❌ Failed to initialize vector store")
        return None
    
    # Add documents
    if vector_store.add_documents(documents):
        print(f"✅ Added {len(documents)} documents to vector store")
    else:
        print("❌ Failed to add documents to vector store")
        return None
    
    # Get collection info
    info = vector_store.get_collection_info()
    if info["error"]:
        print(f"❌ Error getting collection info: {info['error']}")
    else:
        print(f"📊 Total chunks in knowledge base: {info['count']}")
    
    # Test similarity search
    test_queries = [
        "What is machine learning?",
        "Explain deep learning",
        "What is natural language processing?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = vector_store.similarity_search(query, k=2)
        if results:
            print(f"Found {len(results)} relevant chunks")
            for i, doc in enumerate(results):
                print(f"  {i+1}. {doc.page_content[:80]}...")
        else:
            print("No results found")
    
    return vector_store

def demo_chat_system(vector_store):
    """Demonstrate chat system functionality."""
    print("\n💬 Chat System Demo")
    print("-" * 30)
    
    if not vector_store:
        print("❌ Vector store not available for chat demo")
        return
    
    chat_system = ChatSystem(vector_store)
    
    # Test questions
    test_questions = [
        "What is artificial intelligence?",
        "How does machine learning work?",
        "What are the different types of AI?",
        "Can you explain deep learning in simple terms?"
    ]
    
    for question in test_questions:
        print(f"\n❓ Question: {question}")
        response = chat_system.chat(question)
        
        if response["error"]:
            print(f"❌ Error: {response['error']}")
        else:
            print(f"🤖 Answer: {response['response']}")
            if response["source_documents"]:
                print(f"📚 Sources: {len(response['source_documents'])} documents referenced")
    
    # Test memory
    print(f"\n🧠 Chat History: {len(chat_system.get_chat_history())} messages")

def cleanup_demo_files(sample_file):
    """Clean up demo files."""
    try:
        os.remove(sample_file)
        print(f"\n🧹 Cleaned up demo file: {sample_file}")
    except FileNotFoundError:
        pass

def main():
    """Main demo function."""
    print("🧠 AI Knowledge Vault - Demo Mode")
    print("=" * 50)
    print("This demo shows the core functionality without requiring Azure OpenAI setup.")
    print("For full functionality, configure Azure OpenAI credentials and run: streamlit run main.py")
    print("=" * 50)
    
    try:
        # Demo document processing
        documents, sample_file = demo_document_processing()
        
        # Demo vector store (this will fail without Azure OpenAI, but we can show the structure)
        print("\n⚠️  Note: Vector store demo requires Azure OpenAI configuration")
        print("   To test vector store functionality:")
        print("   1. Set up Azure OpenAI credentials in .env file")
        print("   2. Run: streamlit run main.py")
        
        # Demo chat system (this will also fail without Azure OpenAI)
        print("\n⚠️  Note: Chat system demo requires Azure OpenAI configuration")
        print("   To test chat functionality:")
        print("   1. Set up Azure OpenAI credentials in .env file")
        print("   2. Run: streamlit run main.py")
        
        # Cleanup
        cleanup_demo_files(sample_file)
        
        print("\n✅ Demo completed successfully!")
        print("\nTo run the full application:")
        print("1. Configure Azure OpenAI credentials in .env file")
        print("2. Run: streamlit run main.py")
        print("3. Open http://localhost:8501 in your browser")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Please check your installation and try again.")

if __name__ == "__main__":
    main()
