from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool
from app.core.config import settings

def get_search_tool():
    """
    Returns a Tool instance for Serper search.
    """
    if not settings.SERPER_API_KEY:
        raise ValueError("SERPER_API_KEY is not set in environment variables.")

    search = GoogleSerperAPIWrapper(serper_api_key=settings.SERPER_API_KEY)
    
    return Tool(
        name="web_search",
        func=search.run,
        description="Useful for when you need to answer questions about current events or specific data not found in documents."
    )
