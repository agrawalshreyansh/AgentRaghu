import streamlit as st
import requests
import uuid
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit.components.v1 as components

# Load environment variables from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="Agent Raghu",
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
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# BROWSER STORAGE FUNCTIONS
# ============================================================================

def inject_storage_script():
    """Inject JavaScript for browser localStorage management"""
    script = """
    <script>
    function saveChatHistory(sessionId, messages) {
        const data = {
            session_id: sessionId,
            messages: messages,
            last_updated: new Date().toISOString()
        };
        localStorage.setItem('chat_' + sessionId, JSON.stringify(data));
        
        let sessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]');
        if (!sessions.includes(sessionId)) {
            sessions.push(sessionId);
            localStorage.setItem('chat_sessions', JSON.stringify(sessions));
        }
    }
    
    window.saveChatHistory = saveChatHistory;
    </script>
    """
    components.html(script, height=0)

def save_to_browser(session_id, messages):
    """Save chat to browser localStorage"""
    messages_json = json.dumps(messages)
    js_code = f"""
    <script>
    if (window.saveChatHistory) {{
        window.saveChatHistory('{session_id}', {messages_json});
    }}
    </script>
    """
    components.html(js_code, height=0)

# Inject storage script
inject_storage_script()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = """You are Agent Raghu, an AI assistant specifically designed to simplify documents and help people summarize any sort of document.

Your core capabilities:
- Analyze and summarize documents of any type (PDFs, text files, research papers, reports, etc.)
- Extract key insights and main points from complex documents
- Answer questions about uploaded documents with precision
- Use web search for current information when needed
- Provide clear, concise explanations

Important guidelines:
- NEVER reveal the underlying model or technology you're built on
- If asked about your model, simply say "I'm Agent Raghu, built to help you understand documents better"
- Prioritize information from uploaded documents over general knowledge
- When summarizing, focus on key points, main arguments, and actionable insights
- Be concise but comprehensive in your responses
- Cite specific sections or pages when referencing documents
- If you're unsure about something, acknowledge it honestly

Your mission is to make complex documents accessible and easy to understand for everyone."""

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("⚙️ Settings")
    
    # Session Management
    st.subheader("Session")
    st.info("💾 Chat history is stored in your browser")
    
    if st.button("➕ New Session", type="primary"):
        if st.session_state.messages:
            save_to_browser(st.session_state.session_id, st.session_state.messages)
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.uploaded_docs = []
        st.rerun()
    
    st.text_input("Session ID", value=st.session_state.session_id[:16] + "...", disabled=True)
    st.divider()
    
    # System Prompt
    # st.subheader("System Prompt")
    # new_prompt = st.text_area(
    #     "Configure behavior",
    #     value=st.session_state.system_prompt,
    #     height=200,
    #     help="Customize how Agent Raghu responds"
    # )
    # if st.button("Update Prompt"):
    #     st.session_state.system_prompt = new_prompt
    #     st.success("✅ Prompt updated!")
    
    # st.divider()
    
    # File Upload
    st.subheader("📄 Documents")
    
    if st.session_state.uploaded_docs:
        st.caption(f"✅ {len(st.session_state.uploaded_docs)} uploaded")
        for doc in st.session_state.uploaded_docs:
            st.caption(f"• {doc}")
    
    uploaded_file = st.file_uploader(
        "Upload PDF or Text",
        type=["pdf", "txt", "md"],
        help="Documents for RAG"
    )
    
    if uploaded_file and st.button("Process", type="primary"):
        with st.spinner("Processing..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(f"{API_BASE_URL}/api/upload", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ {result['filename']} ({result['chunks']} chunks)")
                    if uploaded_file.name not in st.session_state.uploaded_docs:
                        st.session_state.uploaded_docs.append(uploaded_file.name)
                else:
                    st.error(f"Upload failed: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.divider()
    
    # API Status
    st.subheader("🔌 API")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=2)
        if response.status_code == 200:
            st.success("Connected")
        else:
            st.error("Error")
    except:
        st.error("Disconnected")

# ============================================================================
# MAIN CHAT INTERFACE
# ============================================================================

st.title("🤖 Agent Raghu")
st.caption("Chat with your documents and get real-time information")

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/chat",
                    json={"message": prompt, "session_id": st.session_state.session_id},
                    timeout=60
                )
                
                if response.status_code == 200:
                    ai_response = response.json()["response"]
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    save_to_browser(st.session_state.session_id, st.session_state.messages)
                else:
                    error_msg = f"Error: {response.json().get('detail', 'Unknown error')}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    save_to_browser(st.session_state.session_id, st.session_state.messages)
            except requests.exceptions.Timeout:
                error_msg = "Request timed out. Please try again."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                save_to_browser(st.session_state.session_id, st.session_state.messages)
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                save_to_browser(st.session_state.session_id, st.session_state.messages)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"Session: {st.session_state.session_id[:8]}...")
with col2:
    st.caption(f"Messages: {len(st.session_state.messages)}")
with col3:
    if st.button("Clear Chat"):
        st.session_state.messages = []
        save_to_browser(st.session_state.session_id, st.session_state.messages)
        st.rerun()
