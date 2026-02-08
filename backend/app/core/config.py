from pydantic_settings import BaseSettings
from typing import Optional

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
        env_file = ".env"
        case_sensitive = True

settings = Settings()
