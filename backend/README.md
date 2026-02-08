# Agent Raghu - Backend

FastAPI-based RAG agent with document processing and web search.

## Setup

1. **Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run**
```bash
uvicorn app.main:app --reload
```

## Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `OPENROUTER_MODEL`: Model to use (default: `x-ai/grok-4-fast`)
- `SERPER_API_KEY`: Serper API key for web search

## API Endpoints

- `GET /`: Health check
- `POST /api/chat`: Chat with the agent
- `POST /api/upload`: Upload documents
- `GET /api/sessions`: List sessions

## Features

- 🤖 LLM integration via OpenRouter
- 📄 Document processing (PDF, TXT, MD)
- 🔍 Web search via Serper
- 💾 FAISS vector store
- 🔒 Rate limiting (5 req/min)

## Deployment

### Railway/Render
1. Connect GitHub repo
2. Set environment variables
3. Deploy

### Docker
```bash
docker build -t agent-raghu-backend .
docker run -p 8000:8000 --env-file .env agent-raghu-backend
```
