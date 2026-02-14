#!/usr/bin/env python3
"""
Unified runner for RAG Agent application.
Starts both the FastAPI backend and Streamlit frontend.
"""

import subprocess
import sys
import os
import signal
import time
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent

# Use virtual environment Python if available
PYTHON_EXEC = os.path.join(PROJECT_ROOT, ".venv", "bin", "python")
if not os.path.exists(PYTHON_EXEC):
    PYTHON_EXEC = sys.executable  # Fallback to current Python

def main():
    print("=" * 60)
    print("RAG Agent - Unified Application Launcher")
    print("=" * 60)
    
    # Get ports from environment or use defaults
    backend_port = int(os.getenv("BACKEND_PORT", 8000))
    frontend_port = int(os.getenv("FRONTEND_PORT", 8501))
    
    # Start FastAPI backend
    print(f"\n🚀 Starting FastAPI backend on port {backend_port}...")
    backend_process = subprocess.Popen([
        PYTHON_EXEC, "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", str(backend_port),
        "--reload"
    ], cwd=PROJECT_ROOT / "backend")
    
    print(f"✅ Backend started (PID: {backend_process.pid})")
    
    # Give backend a moment to start
    time.sleep(2)
    
    # Start Streamlit frontend
    print(f"\n🚀 Starting Streamlit frontend on port {frontend_port}...")
    
    # Set environment variable for API base URL
    frontend_env = os.environ.copy()
    frontend_env["API_BASE_URL"] = f"http://localhost:{backend_port}"
    
    frontend_process = subprocess.Popen([
        PYTHON_EXEC, "-m", "streamlit",
        "run", "app.py",
        "--server.port", str(frontend_port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ], cwd=PROJECT_ROOT / "frontend", env=frontend_env)
    
    print(f"✅ Frontend started (PID: {frontend_process.pid})")
    
    print("\n" + "=" * 60)
    print("✨ RAG Agent is now running!")
    print("=" * 60)
    print(f"📡 Backend API:  http://localhost:{backend_port}")
    print(f"🖥️  Frontend UI:  http://localhost:{frontend_port}")
    print(f"📚 API Docs:     http://localhost:{backend_port}/docs")
    print("=" * 60)
    print("\n⚠️  Press Ctrl+C to stop both services\n")
    
    # Handle graceful shutdown
    def shutdown(signum, frame):
        print("\n\n🛑 Shutting down RAG Agent...")
        print("Stopping backend...")
        backend_process.terminate()
        print("Stopping frontend...")
        frontend_process.terminate()
        
        # Wait for processes to end
        try:
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("⚠️  Forcing shutdown...")
            backend_process.kill()
            frontend_process.kill()
        
        print("✅ All services stopped. Goodbye!")
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    
    # Wait for processes (keeps script running)
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        shutdown(None, None)

if __name__ == "__main__":
    main()
