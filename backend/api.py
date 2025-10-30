"""FastAPI backend for RAG pipeline.

Exposes SessionManager, DocumentService, and ChatService as REST API.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

from services import SessionManager, DocumentService, ChatService

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="RAG Pipeline API",
    description="REST API for local RAG pipeline with LM Studio",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# INITIALIZE SERVICES
# ============================================================================

manager = SessionManager(sessions_dir="sessions")
doc_service = DocumentService(manager)
chat_service = ChatService(manager)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class SessionCreate(BaseModel):
    """Create a new session."""
    name: Optional[str] = None

class SessionResponse(BaseModel):
    """Session information."""
    session_id: str
    name: Optional[str] = None
    created: str
    documents: List[str]
    indexed_chunks: int
    total_size_bytes: int
    messages_count: int

class SessionListItemResponse(BaseModel):
    """Session list item."""
    id: str
    name: Optional[str] = None
    created: str

class ChatQuery(BaseModel):
    """Query for chat."""
    query: str
    save_to_history: bool = True

class ChatResponse(BaseModel):
    """Response from chat."""
    answer: str
    sources: List[str]
    context_documents: int
    session_id: str

class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    session_id: Optional[str] = None

# ============================================================================
# SESSION ENDPOINTS
# ============================================================================

@app.post("/api/sessions", response_model=str)
async def create_session(session_data: Optional[SessionCreate] = None):
    """Create a new session."""
    name = session_data.name if session_data else None
    session_id = manager.create_session(name=name)
    return session_id

@app.get("/api/sessions", response_model=List[SessionListItemResponse])
async def list_sessions():
    """List all sessions with their names."""
    return manager.list_sessions_with_names()

@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session information."""
    try:
        context = chat_service.get_session_context(session_id)
        return SessionResponse(
            session_id=session_id,
            name=context.get("name"),
            created=context["created"],
            documents=context["documents"],
            indexed_chunks=context["indexed_chunks"],
            total_size_bytes=context["total_size_bytes"],
            messages_count=context["messages_count"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    try:
        manager.delete_session(session_id)
        return {"status": "success", "message": f"Session {session_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/sessions")
async def delete_all_sessions():
    """Delete all sessions."""
    try:
        session_ids = manager.list_sessions()
        count = len(session_ids)
        for session_id in session_ids:
            manager.delete_session(session_id)
        return {"status": "success", "message": f"Deleted {count} sessions", "count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# DOCUMENT ENDPOINTS
# ============================================================================

@app.post("/api/sessions/{session_id}/documents/upload")
async def upload_documents(session_id: str, files: List[UploadFile] = File(...)):
    """Upload documents to a session."""
    try:
        # Read all files asynchronously before passing to sync service
        files_data = []
        for file in files:
            content = await file.read()
            # Create a file-like object with the content
            import io
            file_obj = io.BytesIO(content)
            file_obj.name = file.filename
            files_data.append(file_obj)
        
        result = doc_service.upload_documents(session_id, files_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/sessions/{session_id}/documents/index")
async def index_documents(session_id: str):
    """Index documents in a session."""
    try:
        result = doc_service.index_session(session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/sessions/{session_id}/documents")
async def get_documents(session_id: str):
    """Get documents in a session."""
    try:
        doc_info = doc_service.get_document_info(session_id)
        return doc_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/sessions/{session_id}/documents/{filename}")
async def delete_document(session_id: str, filename: str):
    """Delete a document from a session."""
    try:
        result = doc_service.remove_document(session_id, filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# CHAT ENDPOINTS
# ============================================================================

@app.post("/api/sessions/{session_id}/chat", response_model=ChatResponse)
async def chat(session_id: str, query_data: ChatQuery):
    """Query the RAG pipeline."""
    try:
        result = chat_service.query(
            session_id,
            query_data.query,
            save_to_history=query_data.save_to_history
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            context_documents=result.get("context_documents", 0),
            session_id=session_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/sessions/{session_id}/chat/stream")
async def chat_stream(session_id: str, query_data: ChatQuery):
    """Query the RAG pipeline with real-time token streaming.
    
    Uses proper Server-Sent Events (SSE) format for streaming.
    Each chunk is formatted as: data: {json}\n\n
    """
    try:
        def generate_stream():
            """Generator that yields SSE-formatted tokens."""
            import json
            import time
            
            result = chat_service.query(
                session_id,
                query_data.query,
                save_to_history=query_data.save_to_history
            )
            
            if "error" in result:
                error_data = {"type": "error", "content": result["error"]}
                yield f"data: {json.dumps(error_data)}\n\n"
                return
            
            # Stream the answer tokens
            answer = result.get("answer", "")
            sources = result.get("sources", [])
            
            # Send each character as a token
            for i, char in enumerate(answer):
                # SSE format: data: {json}\n\n
                token_data = {"type": "token", "content": char}
                yield f"data: {json.dumps(token_data)}\n\n"
                
                # Add delay to ensure chunks are sent separately
                # Every character gets a small delay to encourage streaming
                time.sleep(0.005)  # 5ms delay per token
            
            # Send metadata after streaming completes
            if sources:
                metadata = {"type": "metadata", "sources": sources}
                yield f"data: {json.dumps(metadata)}\n\n"
            
            # Send done signal
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "Connection": "keep-alive",
                "Transfer-Encoding": "chunked",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/sessions/{session_id}/chat/history")
async def get_chat_history(session_id: str):
    """Get chat history for a session."""
    try:
        history = chat_service.get_chat_history(session_id)
        return {"session_id": session_id, "messages": history}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/sessions/{session_id}/chat/history")
async def clear_chat_history(session_id: str):
    """Clear chat history for a session."""
    try:
        chat_service.clear_chat_history(session_id)
        return {"status": "success", "message": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# HEALTH ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health():
    """Health check."""
    return {"status": "healthy", "service": "RAG Pipeline API"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Pipeline API",
        "docs": "/docs",
        "health": "/api/health"
    }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
