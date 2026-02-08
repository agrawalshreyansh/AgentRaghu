from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG Agent API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # LLM Settings
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str = "openai/gpt-3.5-turbo" # Default or whatever is preferred
    
    # Search Settings
    SERPER_API_KEY: Optional[str] = None
    
    # Vector DB Settings
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    CHROMA_SERVER_NOFILE: Optional[int] = None
    
    class Config:
        # Load .env from project root (two levels up from this file)
        env_file = str(Path(__file__).parent.parent.parent.parent / ".env")
        case_sensitive = True

settings = Settings()
