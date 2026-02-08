# Agent Raghu

AI-powered document assistant that simplifies and summarizes any type of document.

## Project Structure

```
Rag_Agent/
├── frontend/          # Streamlit UI
│   ├── app.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── backend/           # FastAPI API
│   ├── app/
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── README.md
└── DEPLOYMENT.md
```

## Quick Start

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with backend URL
streamlit run app.py
```

## Features

- 📄 **Document Processing**: Upload PDFs, text files, markdown
- 🤖 **AI Chat**: Powered by OpenRouter (Grok-4-fast)
- 🔍 **Web Search**: Real-time information via Serper
- 💾 **Browser Storage**: Chat history saved locally
- 🚀 **Easy Deployment**: Separate frontend/backend for flexible hosting

## Documentation

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
- [Deployment Guide](DEPLOYMENT.md)

## Tech Stack

**Backend:**
- FastAPI
- LangChain + LangGraph
- FAISS vector store
- HuggingFace embeddings
- OpenRouter LLM

**Frontend:**
- Streamlit
- Browser localStorage
- Responsive UI

## License

MIT
