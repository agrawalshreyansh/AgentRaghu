import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag.vector_store import get_vector_store
from app.core.config import settings

def ingest_document(file: UploadFile):
    """
    Ingests a document (PDF or text) into the vector store.
    """
    # Save uploaded file to a temporary file
    suffix = Path(file.filename).suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        if suffix.lower() == ".pdf":
            loader = PyPDFLoader(tmp_path)
        elif suffix.lower() in [".txt", ".md"]:
            loader = TextLoader(tmp_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        documents = loader.load()
        
        # Split text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        
        # Add to vector store
        vector_store = get_vector_store()
        vector_store.add_documents(splits)
        
        # Save the updated index
        vector_store_path = Path(settings.CHROMA_PERSIST_DIRECTORY) / "faiss_index"
        vector_store.save_local(str(vector_store_path))
        
        # Clear the cached vector store so next call reloads it
        import app.rag.vector_store as vs
        vs._vector_store_instance = None
        
        return {"filename": file.filename, "chunks": len(splits), "status": "success"}

    finally:
        # Cleanup temp file
        Path(tmp_path).unlink(missing_ok=True)
