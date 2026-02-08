# Agent Raghu - Frontend

Streamlit-based UI for Agent Raghu document assistant.

## Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your backend API URL
```

3. **Run**
```bash
streamlit run app.py
```

## Environment Variables

- `API_BASE_URL`: Backend API endpoint (default: `http://localhost:8000`)

## Features

- 💬 Clean chat interface
- 📄 Document upload
- 💾 Browser-based chat history
- 🔄 Session management

## Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Set `API_BASE_URL` in secrets

### Docker
```bash
docker build -t agent-raghu-frontend .
docker run -p 8501:8501 -e API_BASE_URL=https://your-api.com agent-raghu-frontend
```
