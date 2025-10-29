#!/usr/bin/env python3
"""
🚀 RAG Framework - Run Frontend & Backend

This script starts both the Streamlit frontend and any required backend services.
"""

import subprocess
import sys
import time
import os
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print startup header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("=" * 70)
    print("  🚀 RAG Framework - Starting Frontend & Backend")
    print("=" * 70)
    print(f"{Colors.ENDC}\n")

def check_lmstudio():
    """Check if LM Studio is running."""
    try:
        import urllib.request
        import urllib.error
        import json
        
        # Try to fetch available models
        response = urllib.request.urlopen("http://127.0.0.1:1234/v1/models", timeout=3)
        
        # Check response status
        if response.status != 200:
            raise Exception(f"Unexpected status code: {response.status}")
        
        # Parse JSON response
        data = json.loads(response.read().decode('utf-8'))
        
        # Check if we got models
        if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
            models = [m.get('id', 'Unknown') for m in data['data']]
            print(f"{Colors.GREEN}✅ LM Studio is running at http://127.0.0.1:1234{Colors.ENDC}")
            print(f"{Colors.GREEN}   Available models: {', '.join(models[:3])}")
            if len(models) > 3:
                print(f"{Colors.GREEN}   ... and {len(models) - 3} more{Colors.ENDC}")
            else:
                print(f"{Colors.ENDC}", end="")
            return True
        else:
            raise Exception("No models available in response")
            
    except urllib.error.URLError as e:
        print(f"{Colors.YELLOW}⚠️  LM Studio is NOT running!{Colors.ENDC}")
        print(f"{Colors.YELLOW}   Connection error: {e.reason}{Colors.ENDC}")
    except urllib.error.HTTPError as e:
        print(f"{Colors.YELLOW}⚠️  LM Studio error!{Colors.ENDC}")
        print(f"{Colors.YELLOW}   HTTP {e.code}: {e.reason}{Colors.ENDC}")
    except TimeoutError:
        print(f"{Colors.YELLOW}⚠️  LM Studio is NOT responding!{Colors.ENDC}")
        print(f"{Colors.YELLOW}   Connection timeout after 3 seconds{Colors.ENDC}")
    except json.JSONDecodeError:
        print(f"{Colors.YELLOW}⚠️  LM Studio response invalid!{Colors.ENDC}")
        print(f"{Colors.YELLOW}   Could not parse JSON response{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  LM Studio check failed!{Colors.ENDC}")
        print(f"{Colors.YELLOW}   Error: {str(e)}{Colors.ENDC}")
    
    print(f"{Colors.YELLOW}   Please start LM Studio before running queries:{Colors.ENDC}")
    print(f"{Colors.YELLOW}   - Open LM Studio{Colors.ENDC}")
    print(f"{Colors.YELLOW}   - Load model: qwen2.5-7b-instruct-1m{Colors.ENDC}")
    print(f"{Colors.YELLOW}   - Click 'Start Server' in Local Server tab{Colors.ENDC}")
    print(f"{Colors.YELLOW}   - Server runs at http://127.0.0.1:1234{Colors.ENDC}\n")
    return False

def start_frontend():
    """Start Streamlit frontend."""
    print(f"{Colors.BLUE}📱 Starting Streamlit Frontend...{Colors.ENDC}")
    
    # Get the workspace root
    root = Path(__file__).parent
    frontend_app = root / "frontend" / "streamlit_app.py"
    
    if not frontend_app.exists():
        print(f"{Colors.RED}❌ Frontend app not found at {frontend_app}{Colors.ENDC}")
        sys.exit(1)
    
    # Start Streamlit using uv run
    cmd = [
        "uv",
        "run",
        "streamlit",
        "run",
        str(frontend_app),
        "--logger.level=info",
        "--client.showErrorDetails=true"
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=str(root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"{Colors.GREEN}✅ Streamlit started (PID: {process.pid}){Colors.ENDC}")
        print(f"{Colors.CYAN}   🌐 Frontend URL: http://localhost:8501{Colors.ENDC}\n")
        return process
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to start Streamlit: {e}{Colors.ENDC}")
        sys.exit(1)

def print_startup_info():
    """Print startup information."""
    print(f"{Colors.BOLD}{Colors.GREEN}")
    print("=" * 70)
    print("  ✅ READY!")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    print(f"{Colors.CYAN}📱 Frontend (Streamlit):{Colors.ENDC}")
    print(f"   🌐 http://localhost:8501\n")
    print(f"{Colors.CYAN}🔌 Backend Services:{Colors.ENDC}")
    print(f"   ✅ Session Management")
    print(f"   ✅ Document Processing")
    print(f"   ✅ RAG Pipeline\n")
    print(f"{Colors.CYAN}🤖 LLM Service:{Colors.ENDC}")
    print(f"   🔗 LM Studio: http://127.0.0.1:1234")
    print(f"   📦 Model: qwen2.5-7b-instruct-1m\n")
    print(f"{Colors.YELLOW}💡 Tips:{Colors.ENDC}")
    print(f"   • Create a new session in the sidebar")
    print(f"   • Upload documents (PDF, TXT, MD, HTML)")
    print(f"   • Start chatting!\n")
    print(f"{Colors.YELLOW}⏹️  To stop: Press Ctrl+C{Colors.ENDC}\n")

def main():
    """Main entry point."""
    print_header()
    
    # Check if LM Studio is running
    lmstudio_running = check_lmstudio()
    
    if not lmstudio_running:
        print(f"{Colors.YELLOW}Continuing anyway... you can start LM Studio later.{Colors.ENDC}\n")
    
    # Start frontend
    frontend_process = start_frontend()
    
    # Wait a bit for frontend to start
    time.sleep(3)
    
    print_startup_info()
    
    try:
        # Wait for frontend process
        frontend_process.wait()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⏹️  Shutting down...{Colors.ENDC}")
        frontend_process.terminate()
        frontend_process.wait()
        print(f"{Colors.GREEN}✅ Shutdown complete{Colors.ENDC}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
