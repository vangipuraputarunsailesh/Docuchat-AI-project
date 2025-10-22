import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration (Direct API)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
OPENAI_EMBEDDING_MODEL_NAME = os.getenv("OPENAI_EMBEDDING_MODEL_NAME", "text-embedding-ada-002")

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY = "./chroma_db"

# Document Processing Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_FILE_SIZE_MB = 50

# Chat Configuration
MAX_MEMORY_HISTORY = 5
MAX_CONTEXT_CHUNKS = 5

# Supported file types
SUPPORTED_EXTENSIONS = ['.pdf', '.txt', '.md', '.docx']
