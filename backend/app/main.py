from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

load_dotenv()

app = FastAPI(
    title="RAG Agent API",
    description="API for RAG-based agent with Web Search",
    version="0.1.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes import router as api_router
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "RAG Agent API is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
