from langchain_openai import ChatOpenAI
from app.core.config import settings

def get_llm(model: str = settings.OPENROUTER_MODEL, temperature: float = 0, timeout: int = 60):
    """
    Returns a ChatOpenAI instance configured for OpenRouter.
    
    Args:
        model: The model to use (default from settings)
        temperature: Temperature for response randomness (0-1)
        timeout: Request timeout in seconds (default 60)
    """
    return ChatOpenAI(
        model=model,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=temperature,
        timeout=timeout,
        request_timeout=timeout,
    )
