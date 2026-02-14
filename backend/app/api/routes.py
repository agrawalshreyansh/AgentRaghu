from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
import uuid
import logging
from app.rag.ingest import ingest_document
from app.agent.graph import app_graph
from langchain_core.messages import HumanMessage
from app.core.limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat_endpoint(request: Request, chat_request: ChatRequest):
    """
    Chat with the agent.
    """
    config = {"configurable": {"thread_id": chat_request.session_id}}
    inputs = {"messages": [HumanMessage(content=chat_request.message)]}

    try:
        logger.info(f"Processing chat request for session {chat_request.session_id}")
        result = await app_graph.ainvoke(inputs, config=config)
        last_message = result["messages"][-1]
        logger.info(f"Successfully generated response for session {chat_request.session_id}")
        return ChatResponse(response=last_message.content, session_id=chat_request.session_id)

    except TimeoutError as e:
        logger.error(f"Timeout error for session {chat_request.session_id}: {e}")
        raise HTTPException(status_code=504, detail="Request timed out. Please try again.")
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

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
