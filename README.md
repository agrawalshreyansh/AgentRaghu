# Agent Raghu

AI-powered document assistant that simplifies and summarizes documents.

## Quick Start

### 1. Setup Environment
```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Install Dependencies
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend (in new terminal)
cd frontend
pip install -r requirements.txt
```

### 3. Run
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
streamlit run app.py
```

Visit: `http://localhost:8501`

## Project Structure

```
Rag_Agent/
├── backend/           # FastAPI API
│   ├── app/
│   │   ├── agent/    # LangGraph agent
│   │   ├── api/      # API routes
│   │   ├── core/     # Config
│   │   └── rag/      # RAG components
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
