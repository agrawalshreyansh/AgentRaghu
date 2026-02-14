import os
from functools import lru_cache
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import settings

# Module-level cache for embeddings and vector store
_embeddings_instance = None
_vector_store_instance = None

@lru_cache(maxsize=1)
def get_embeddings():
    """
    Returns cached HuggingFace Embeddings instance.
    Using 'all-MiniLM-L6-v2' which is a good balance of speed and quality.
    """
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        # Pre-warm the model
        _embeddings_instance.embed_query("warmup")
    return _embeddings_instance

def get_vector_store():
    """
    Returns the FAISS vector store instance (cached).
    Note: Returns new instance if documents were added via ingest.
    """
    global _vector_store_instance
    embeddings = get_embeddings()
    
    vector_store_path = Path(settings.CHROMA_PERSIST_DIRECTORY) / "faiss_index"
    
    # Return cached instance if available and not invalidated
    if vector_store_path.exists() and _vector_store_instance is not None:
        try:
            return _vector_store_instance
        except Exception:
            pass
    
    # Try to load existing vector store
    if vector_store_path.exists():
        try:
            _vector_store_instance = FAISS.load_local(
                str(vector_store_path),
                embeddings,
                allow_dangerous_deserialization=True
            )
            return _vector_store_instance
        except Exception:
            # If loading fails, create a new one
            pass
    
    # Create new empty vector store with a dummy document
    from langchain_core.documents import Document
    dummy_doc = Document(page_content="Initialization document", metadata={"source": "init"})
    _vector_store_instance = FAISS.from_documents([dummy_doc], embeddings)
    
    # Save it
    os.makedirs(vector_store_path.parent, exist_ok=True)
    _vector_store_instance.save_local(str(vector_store_path))
    
    return _vector_store_instance
