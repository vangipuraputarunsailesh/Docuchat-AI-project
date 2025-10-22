# 🧠 AI Knowledge Vault

An intelligent document processing and chat system that allows you to upload PDFs, web articles, and other documents, then chat with your knowledge base using AI-powered search and retrieval.

## ✨ Features

- **📁 Multi-format Document Support**: Upload PDFs, text files, markdown files, and web articles
- **🔍 Intelligent Search**: Vector-based similarity search using ChromaDB and Azure OpenAI embeddings
- **💬 Conversational AI**: Chat with your documents using Azure OpenAI GPT models
- **🧠 Memory System**: Maintains context from the last 5 interactions
- **📊 Document Management**: View uploaded files and knowledge base statistics
- **📥 Export Functionality**: Export chat history as CSV
- **🎨 Modern UI**: Beautiful Streamlit interface with responsive design

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Azure OpenAI account with API access
- Required Python packages (see requirements.txt)

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd ai-knowledge-vault
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Azure OpenAI credentials**
   - Copy `env_example.txt` to `.env`
   - Fill in your Azure OpenAI credentials:
   ```env
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_DEPLOYMENT_NAME=your-gpt-deployment-name
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=your-embedding-deployment-name
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

5. **Open your browser** and navigate to `http://localhost:8501`

## 🏗️ Architecture

### Core Components

1. **Document Processor** (`document_processor.py`)
   - Handles PDF, text, and web article processing
   - Splits documents into manageable chunks
   - Extracts metadata and content

2. **Vector Store** (`vector_store.py`)
   - Manages ChromaDB vector database
   - Handles embeddings using Azure OpenAI
   - Performs similarity searches

3. **Chat System** (`chat_system.py`)
   - Manages conversational AI with memory
   - Integrates with vector store for context retrieval
   - Handles conversation flow and responses

4. **Main Application** (`main.py`)
   - Streamlit web interface
   - File upload and management
   - Chat interface and history

### Tech Stack

- **Frontend**: Streamlit
- **Document Processing**: LangChain, PyPDF2, BeautifulSoup4
- **Vector Database**: ChromaDB
- **AI/ML**: Azure OpenAI (GPT + Embeddings)
- **Data Processing**: Pandas, NumPy

## 📖 Usage Guide

### 1. Upload Documents

- **File Upload**: Use the sidebar to upload PDF, TXT, or MD files
- **Web Articles**: Enter a URL to process web content
- **Multiple Files**: Upload multiple documents to build a comprehensive knowledge base

### 2. Chat with Your Knowledge

- **Ask Questions**: Type questions in the chat input
- **Sample Questions**: Use the provided sample questions as starting points
- **Source References**: View source documents that informed each response
- **Memory**: The system remembers the last 5 interactions for context

### 3. Manage Your Knowledge Base

- **View Statistics**: See how many document chunks are stored
- **Clear Data**: Clear the knowledge base or chat memory
- **Export History**: Download chat history as CSV

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key | Yes |
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI endpoint URL | Yes |
| `AZURE_OPENAI_API_VERSION` | API version (default: 2024-02-15-preview) | No |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | GPT model deployment name | Yes |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME` | Embeddings model deployment name | Yes |

### Customization

Edit `config.py` to modify:
- Chunk size and overlap for document processing
- Maximum file size limits
- Number of context chunks retrieved
- Memory history length

## 🎯 Use Cases

- **Research Assistant**: Upload research papers and ask questions
- **Document Q&A**: Chat with company documents, manuals, or reports
- **Knowledge Management**: Build a searchable knowledge base from various sources
- **Content Analysis**: Analyze and summarize multiple documents
- **Learning Tool**: Upload educational materials and ask questions

## 🔍 Example Questions

- "What are the main topics discussed in the documents?"
- "Can you summarize the key points from the uploaded files?"
- "What are the most important insights from the research papers?"
- "How do the different documents relate to each other?"
- "What are the conclusions or recommendations mentioned?"

## 🛠️ Development

### Project Structure

```
ai-knowledge-vault/
├── main.py                 # Main Streamlit application
├── document_processor.py   # Document processing logic
├── vector_store.py        # Vector database management
├── chat_system.py         # Chat and memory system
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── env_example.txt        # Environment variables template
└── README.md              # This file
```

### Adding New Features

1. **New Document Types**: Extend `DocumentProcessor` class
2. **Custom Embeddings**: Modify `VectorStore` class
3. **UI Components**: Add new Streamlit components in `main.py`
4. **Chat Features**: Extend `ChatSystem` class

## 🐛 Troubleshooting

### Common Issues

1. **Azure OpenAI Connection Error**
   - Verify your API key and endpoint
   - Check if your deployment names are correct
   - Ensure you have the right permissions

2. **Document Processing Fails**
   - Check file format is supported
   - Verify file size is within limits
   - Ensure file is not corrupted

3. **Memory Issues**
   - Large documents may consume significant memory
   - Consider reducing chunk size in config
   - Clear knowledge base if needed

### Getting Help

- Check the console output for error messages
- Verify all environment variables are set correctly
- Ensure all dependencies are installed

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For support, please open an issue in the repository or contact the development team.

---

**Built with ❤️ using Streamlit, LangChain, ChromaDB, and Azure OpenAI**
