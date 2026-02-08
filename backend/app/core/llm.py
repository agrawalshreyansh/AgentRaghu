from langchain_openai import ChatOpenAI
from app.core.config import settings

def get_llm(model: str = settings.OPENROUTER_MODEL, temperature: float = 0):
    """
    Returns a ChatOpenAI instance configured for OpenRouter.
    """
    return ChatOpenAI(
        model=model,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=temperature,
    )
