import os
import PyPDF2
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List, Optional
import streamlit as st
from config import CHUNK_SIZE, CHUNK_OVERLAP, SUPPORTED_EXTENSIONS, MAX_FILE_SIZE_MB

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
    
    def process_pdf(self, file_path: str) -> List[Document]:
        """Process PDF file and return list of document chunks."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                # Split text into chunks
                chunks = self.text_splitter.split_text(text)
                
                # Create Document objects
                documents = []
                for i, chunk in enumerate(chunks):
                    doc = Document(
                        page_content=chunk,
                        metadata={
                            "source": file_path,
                            "page": i + 1,
                            "type": "pdf"
                        }
                    )
                    documents.append(doc)
                
                return documents
                
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return []
    
    def process_text_file(self, file_path: str) -> List[Document]:
        """Process text file and return list of document chunks."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create Document objects
            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": file_path,
                        "chunk": i + 1,
                        "type": "text"
                    }
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            st.error(f"Error processing text file: {str(e)}")
            return []
    
    def process_web_article(self, url: str) -> List[Document]:
        """Process web article and return list of document chunks."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create Document objects
            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": url,
                        "chunk": i + 1,
                        "type": "web"
                    }
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            st.error(f"Error processing web article: {str(e)}")
            return []
    
    def process_file(self, file_path: str) -> List[Document]:
        """Process file based on its extension."""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self.process_pdf(file_path)
        elif file_extension in ['.txt', '.md']:
            return self.process_text_file(file_path)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            return []
    
    def validate_file(self, file_path: str) -> bool:
        """Validate if file can be processed."""
        if not os.path.exists(file_path):
            return False
        
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension not in SUPPORTED_EXTENSIONS:
            return False
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({MAX_FILE_SIZE_MB} MB)")
            return False
        
        return True
