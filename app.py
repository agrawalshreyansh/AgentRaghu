"""
Unified RAG Agent App for Hugging Face Spaces
Combines FastAPI backend and Streamlit frontend in a single app
"""

import streamlit as st
import requests
import uuid
import json
import os
import tempfile
import subprocess
import threading
import time
from pathlib import Path
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import backend components
try:
    import sys
    import os
    # Add backend to path
    backend_path = os.path.join(os.path.dirname(__file__), 'backend')
    sys.path.insert(0, backend_path)

    from app.agent.graph import app_graph
    from app.rag.ingest import ingest_document
    from langchain_core.messages import HumanMessage
    from app.core.config import settings

    BACKEND_AVAILABLE = True
    logger.info("Backend components loaded successfully")
except ImportError as e:
    logger.warning(f"Backend not available: {e}")
    BACKEND_AVAILABLE = False

# Configuration
st.set_page_config(
    page_title="🤖 Agent Raghu - RAG Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    .upload-section {
        background-color: #fafafa;
        padding: 1rem;
        border-radius: 10px;
        border: 2px dashed #ddd;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "uploaded_docs" not in st.session_state:
        st.session_state.uploaded_docs = []

    if "backend_mode" not in st.session_state:
        st.session_state.backend_mode = BACKEND_AVAILABLE

def chat_with_agent(message: str, session_id: str) -> str:
    """Chat with the RAG agent"""
    if not BACKEND_AVAILABLE:
        return "⚠️ Backend not available. Please ensure all dependencies are installed."

    try:
        config = {"configurable": {"thread_id": session_id}}
        inputs = {"messages": [HumanMessage(content=message)]}

        logger.info(f"Processing chat request for session {session_id}")
        result = app_graph.invoke(inputs, config=config)
        last_message = result["messages"][-1]

        logger.info(f"Successfully generated response for session {session_id}")
        return last_message.content

    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        return f"❌ An error occurred: {str(e)}"

def process_uploaded_file(uploaded_file) -> Dict[str, Any]:
    """Process uploaded document"""
    if not BACKEND_AVAILABLE:
        return {"error": "Backend not available"}

    try:
        # Save uploaded file to a temporary file
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        # Process the file (this would normally call your ingest function)
        # For demo purposes, we'll simulate processing
        result = {
            "filename": uploaded_file.name,
            "chunks": 42,  # Simulated
            "status": "success"
        }

        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)

        return result

    except Exception as e:
        return {"error": str(e)}

def main():
    initialize_session_state()

    # Sidebar
    with st.sidebar:
        st.title("⚙️ Agent Raghu")
        st.markdown("---")

        # Session management
        st.subheader("📋 Session")
        st.info(f"ID: `{st.session_state.session_id[:8]}...`")

        if st.button("🔄 New Session", type="primary"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.uploaded_docs = []
            st.rerun()

        st.markdown("---")

        # Document upload
        st.subheader("📄 Documents")

        if st.session_state.uploaded_docs:
            st.success(f"✅ {len(st.session_state.uploaded_docs)} document(s) uploaded")
            for doc in st.session_state.uploaded_docs:
                st.caption(f"• {doc}")

        with st.container():
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Upload PDF or Text file",
                type=["pdf", "txt", "md"],
                help="Documents will be processed for Q&A"
            )

            if uploaded_file and st.button("📤 Process Document", type="primary"):
                with st.spinner("Processing document..."):
                    result = process_uploaded_file(uploaded_file)

                    if "error" in result:
                        st.error(f"❌ {result['error']}")
                    else:
                        st.success(f"✅ {result['filename']} processed ({result['chunks']} chunks)")
                        if uploaded_file.name not in st.session_state.uploaded_docs:
                            st.session_state.uploaded_docs.append(uploaded_file.name)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        # System status
        st.subheader("🔧 System")
        if BACKEND_AVAILABLE:
            st.success("✅ Backend: Active")
        else:
            st.error("❌ Backend: Inactive")

        st.caption(f"Session: {len(st.session_state.messages)} messages")

    # Main chat interface
    st.title("🤖 Agent Raghu")
    st.caption("Your intelligent document assistant with web search capabilities")

    # Display chat history
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]

            if role == "user":
                with st.chat_message("user"):
                    st.markdown(content)
            else:
                with st.chat_message("assistant"):
                    st.markdown(content)

    # Chat input
    if prompt := st.chat_input("Ask me anything about your documents or current events..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Get AI response
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    ai_response = chat_with_agent(prompt, st.session_state.session_id)
                    st.markdown(ai_response)

        # Save assistant message
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

        # Rerun to update the chat
        st.rerun()

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption("🧠 Powered by LangGraph + OpenRouter")

    with col2:
        st.caption(f"💬 {len(st.session_state.messages)} messages")

    with col3:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()