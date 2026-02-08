from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
import uuid
from app.rag.ingest import ingest_document
from app.agent.graph import app_graph
from langchain_core.messages import HumanMessage
from app.core.limiter import limiter

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("5/minute")
async def chat_endpoint(request: Request, chat_request: ChatRequest):
    """
    Chat with the agent.
    """
    config = {"configurable": {"thread_id": chat_request.session_id}}
    
    # Invoke LangGraph
    # We maintain state via LangGraph's checkpointer if configured, 
    # but for this simple version, we might pass full history if we weren't using checkpointer.
    # 'app_graph' here is stateless unless we attach a checkpointer. 
    # For a quick MVP without specific persistence setup in graph.py, we just pass the new message.
    # Ideally, we should add a checkpointer (e.g. MemorySaver) to the graph.py
    
    inputs = {"messages": [HumanMessage(content=chat_request.message)]}
    
    try:
        # Note: Without a checkpointer, this 'thread_id' config won't persist state across calls 
        # unless we explicitly handle history. 
        # For this "fresh chat session" requirement, we'd need that.
        # Let's assume we'll update graph.py to use MemorySaver or similar for the next step 
        # or just return the single turn response for now.
        result = await app_graph.ainvoke(inputs, config=config)
        
        last_message = result["messages"][-1]
        return ChatResponse(response=last_message.content, session_id=chat_request.session_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document for RAG.
    """
    try:
        result = ingest_document(file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def list_sessions():
    """
    List active sessions (Placeholder).
    """
    return {"sessions": ["default", "session-1"]}
