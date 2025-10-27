import os
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from typing import List, Optional
import streamlit as st
import traceback
from config import (
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL_NAME,
    CHROMA_PERSIST_DIRECTORY
)

class VectorStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY,
            model=OPENAI_EMBEDDING_MODEL_NAME,
        )
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIRECTORY,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.vectorstore = None
        self.collection_name = "knowledge_vault"
    
    def initialize_vectorstore(self):
        """Initialize or load the vector store."""
        try:
            print("🔄 Initializing vector store...")
            self.vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=CHROMA_PERSIST_DIRECTORY
            )
            print("✅ Vector store initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Error initializing vector store: {str(e)}")
            st.error(f"Error initializing vector store: {str(e)}")
            return False
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to the vector store."""
        try:
            if not self.vectorstore:
                if not self.initialize_vectorstore():
                    return False

            self.vectorstore.add_documents(documents or [])
            return True
        except Exception:
            tb = traceback.format_exc()
            print("Error adding documents to vector store:\n", tb)
            try:
                st.error(f"Error adding documents to vector store: {tb}")
            except Exception:
                pass
            return False

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Perform similarity search and return relevant documents."""
        try:
            if not self.vectorstore:
                if not self.initialize_vectorstore():
                    return []
            
            # Perform similarity search
            results = self.vectorstore.similarity_search(query, k=k)
            return results
            
        except Exception as e:
            st.error(f"Error performing similarity search: {str(e)}")
            return []
    
    def get_collection_info(self) -> dict:
        """Get information about the collection."""
        try:
            if not self.vectorstore:
                if not self.initialize_vectorstore():
                    return {"count": 0, "error": "Failed to initialize"}
            
            # Get collection count
            collection = self.client.get_collection(self.collection_name)
            count = collection.count()
            
            return {"count": count, "error": None}
            
        except Exception as e:
            return {"count": 0, "error": str(e)}
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            if not self.vectorstore:
                if not self.initialize_vectorstore():
                    return False
            
            # Delete the collection and recreate it
            self.client.delete_collection(self.collection_name)
            self.vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=CHROMA_PERSIST_DIRECTORY
            )
            return True
            
        except Exception as e:
            st.error(f"Error clearing collection: {str(e)}")
            return False