import os
import pickle
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import settings

def get_embeddings():
    """
    Returns HuggingFace Embeddings (free, local).
    Using 'all-MiniLM-L6-v2' which is a good balance of speed and quality.
    """
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

def get_vector_store():
    """
    Returns the FAISS vector store instance.
    """
    embeddings = get_embeddings()
    
    vector_store_path = Path(settings.CHROMA_PERSIST_DIRECTORY) / "faiss_index"
    
    # Try to load existing vector store
    if vector_store_path.exists():
        try:
            vector_store = FAISS.load_local(
                str(vector_store_path),
                embeddings,
                allow_dangerous_deserialization=True
            )
            return vector_store
        except Exception:
            # If loading fails, create a new one
            pass
    
    # Create new empty vector store with a dummy document
    from langchain_core.documents import Document
    dummy_doc = Document(page_content="Initialization document", metadata={"source": "init"})
    vector_store = FAISS.from_documents([dummy_doc], embeddings)
    
    # Save it
    os.makedirs(vector_store_path.parent, exist_ok=True)
    vector_store.save_local(str(vector_store_path))
    
    return vector_store
