# 🤖 Agent Raghu - RAG Agent

A powerful RAG (Retrieval-Augmented Generation) agent that can chat with your documents and search the web for current information.

## Features

- 📄 **Document Q&A**: Upload PDFs, text files, and markdown documents
- 🔍 **Web Search**: Automatically searches the web for current events and real-time data
- 🧠 **Intelligent Routing**: Uses AI to decide whether to search documents or the web
- 💬 **Chat Interface**: Clean, modern chat UI built with Streamlit
- 🔄 **Session Management**: Persistent chat sessions with browser storage
- 🚀 **FastAPI Backend**: Robust API with LangGraph orchestration

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI + LangGraph
- **LLM**: OpenRouter (Grok-4-fast)
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **Vector Store**: FAISS
- **Web Search**: Serper API

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Rag_Agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

## Deployment to Hugging Face Spaces

### Step 1: Prepare Your Files
Ensure you have these files in your repository root:
- `app.py` (unified Streamlit app)
- `requirements.txt`
- `backend/` folder (entire backend code)
- `.env` (with your API keys)

### Step 2: Create Hugging Face Space
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Choose:
   - **Space name**: `rag-agent` or your preferred name
   - **License**: MIT
   - **SDK**: `Streamlit`
   - **Visibility**: Public or Private

### Step 3: Upload Your Code
1. **Clone your space locally** or use the web editor
2. **Upload all files** from your project
3. **Make sure `.env` contains your API keys**

### Step 4: Configure Space Settings
In your Space settings:
- **Hardware**: Choose based on your needs (CPU Basic for testing)
- **Storage**: Enable persistent storage if needed
- **Secrets**: Add your API keys as secrets instead of `.env` for security

### Step 5: Deploy
HF Spaces will automatically:
- Install dependencies from `requirements.txt`
- Run `streamlit run app.py`
- Make your app available at `https://yourusername-rag-agent.hf.space`

## Alternative Deployment Options

### Docker Deployment
```bash
# Build the image
docker build -t rag-agent .

# Run the container
docker run -p 8000:8000 -p 8501:8501 rag-agent
```

### Manual Deployment
- **Backend**: Deploy FastAPI to Railway/Render/Fly.io
- **Frontend**: Deploy Streamlit to Hugging Face Spaces

## Environment Variables

Create a `.env` file with:

```env
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=x-ai/grok-4-fast
SERPER_API_KEY=your_serper_key
```

## API Endpoints

- `GET /` - Health check
- `POST /api/chat` - Chat with the agent
- `POST /api/upload` - Upload documents
- `GET /api/sessions` - List sessions

## How It Works

1. **Document Upload**: Files are processed and stored in a FAISS vector database
2. **Query Routing**: AI decides whether to search documents or web
3. **Retrieval**: Relevant document chunks are retrieved using semantic search
4. **Generation**: LLM generates responses using retrieved context
5. **Web Search**: For current events, Serper API provides real-time information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use and modify!

---

**Built with ❤️ for document analysis and intelligent Q&A**
│   └── requirements.txt
├── frontend/          # Streamlit UI
│   ├── app.py
│   └── requirements.txt
├── .env.example       # Environment template
├── .gitignore
└── DEPLOYMENT.md      # Deployment guide
```

## Features

- 📄 Upload PDFs, text files, markdown
- 🤖 AI chat powered by OpenRouter
- 🔍 Web search via Serper
- 💾 Browser-based chat history
- 🚀 Easy deployment

## Environment Variables

All variables are in `.env`:

```env
# Backend
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=x-ai/grok-4-fast
SERPER_API_KEY=your_key

# Frontend
API_BASE_URL=http://localhost:8000
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Railway, Render, and other deployment options.

## Tech Stack

- **Backend:** FastAPI, LangChain, LangGraph, FAISS, HuggingFace
- **Frontend:** Streamlit, Browser localStorage
- **LLM:** OpenRouter (Grok-4-fast)

## License

MIT
