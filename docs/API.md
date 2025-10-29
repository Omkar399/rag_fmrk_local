# 📚 RAG Backend API Documentation

Complete API reference for using the RAG pipeline backend with session support. This allows you to integrate the RAG system into any application without using the Streamlit UI.

---

## 🎯 Overview

The RAG backend provides three main services:

1. **SessionManager** - Session lifecycle management
2. **DocumentService** - Document upload and indexing
3. **ChatService** - Query and chat operations

All services support **session isolation**, meaning each user/context can have completely separate document indexes.

---

## 📋 Table of Contents

1. [SessionManager API](#sessionmanager-api)
2. [DocumentService API](#documentservice-api)
3. [ChatService API](#chatservice-api)
4. [Usage Examples](#usage-examples)
5. [Error Handling](#error-handling)
6. [Integration Guide](#integration-guide)

---

## SessionManager API

**Module:** `backend.services.session_manager`

**Purpose:** Manage user sessions with isolated storage and metadata.

### Class: `SessionManager`

#### Constructor

```python
SessionManager(sessions_dir: str = "sessions")
```

**Parameters:**
- `sessions_dir` (str): Root directory for storing sessions (default: "sessions")

**Example:**
```python
from backend.services import SessionManager

manager = SessionManager(sessions_dir="sessions")
```

---

### Method: `create_session()`

Create a new session with isolated storage.

```python
session_id = manager.create_session() -> str
```

**Returns:** UUID string (session ID)

**Creates:**
- Unique session directory
- Empty Chroma vector DB
- Empty documents directory
- metadata.json file
- chat_history.json file

**Example:**
```python
session_id = manager.create_session()
# Returns: "550e8400-e29b-41d4-a716-446655440000"

# Session directory created:
# sessions/550e8400-e29b-41d4-a716-446655440000/
#   ├── chroma_db/
#   ├── documents/
#   ├── metadata.json
#   └── chat_history.json
```

---

### Method: `get_chroma_db_path(session_id)`

Get the Chroma DB path for a session.

```python
path = manager.get_chroma_db_path(session_id) -> str
```

**Parameters:**
- `session_id` (str): Session ID

**Returns:** Absolute path to session's Chroma DB directory

**Example:**
```python
path = manager.get_chroma_db_path(session_id)
# Returns: "/path/to/sessions/550e8400-e29b-41d4-a716-446655440000/chroma_db"
```

---

### Method: `get_documents_path(session_id)`

Get the documents directory path for a session.

```python
path = manager.get_documents_path(session_id) -> Path
```

**Parameters:**
- `session_id` (str): Session ID

**Returns:** pathlib.Path to session's documents directory

**Example:**
```python
path = manager.get_documents_path(session_id)
# Returns: PosixPath('/path/to/sessions/550e8400.../documents')
```

---

### Method: `list_documents(session_id)`

List all documents in a session.

```python
docs = manager.list_documents(session_id) -> List[str]
```

**Parameters:**
- `session_id` (str): Session ID

**Returns:** List of document filenames

**Example:**
```python
docs = manager.list_documents(session_id)
# Returns: ['paper.pdf', 'guide.md', 'notes.txt']
```

---

### Method: `get_session_info(session_id)`

Get complete session metadata.

```python
info = manager.get_session_info(session_id) -> Dict
```

**Parameters:**
- `session_id` (str): Session ID

**Returns:** Dictionary with metadata

**Dictionary Structure:**
```python
{
    "session_id": "550e8400-...",
    "created": "2025-01-15T10:30:00.123456",
    "updated": "2025-01-15T10:45:00.654321",
    "documents": ["paper.pdf", "guide.md"],
    "indexed_chunks": 42,
    "total_size_bytes": 1048576
}
```

**Example:**
```python
info = manager.get_session_info(session_id)
print(f"Created: {info['created']}")
print(f"Documents: {info['documents']}")
print(f"Chunks indexed: {info['indexed_chunks']}")
```

---

### Method: `update_session_metadata(session_id, indexed_chunks, documents)`

Update session metadata after indexing.

```python
manager.update_session_metadata(
    session_id: str,
    indexed_chunks: int,
    documents: List[str]
) -> None
```

**Parameters:**
- `session_id` (str): Session ID
- `indexed_chunks` (int): Number of chunks
- `documents` (List[str]): List of document names

**Note:** Usually called by DocumentService automatically.

---

### Method: `get_chat_history(session_id)`

Get chat history for a session.

```python
history = manager.get_chat_history(session_id) -> List[Dict]
```

**Parameters:**
- `session_id` (str): Session ID

**Returns:** List of chat messages

**Message Structure:**
```python
{
    "role": "user",  # or "assistant"
    "content": "What is this paper about?",
    "timestamp": "2025-01-15T10:35:00",
    "sources": ["paper.pdf"]  # optional
}
```

**Example:**
```python
history = manager.get_chat_history(session_id)
for msg in history:
    print(f"{msg['role']}: {msg['content']}")
```

---

### Method: `save_chat_message(session_id, role, content, sources)`

Save a message to chat history.

```python
manager.save_chat_message(
    session_id: str,
    role: str,
    content: str,
    sources: Optional[List[str]] = None
) -> None
```

**Parameters:**
- `session_id` (str): Session ID
- `role` (str): "user" or "assistant"
- `content` (str): Message text
- `sources` (List[str], optional): Source documents

**Example:**
```python
manager.save_chat_message(
    session_id,
    "user",
    "What is the main topic?",
    sources=["paper.pdf"]
)
```

---

### Method: `list_sessions()`

List all session IDs.

```python
sessions = manager.list_sessions() -> List[str]
```

**Returns:** List of session IDs

**Example:**
```python
sessions = manager.list_sessions()
# Returns: ["550e8400-...", "661f9511-...", "772g0622-..."]
```

---

### Method: `delete_session(session_id)`

Delete a session and all its data.

```python
manager.delete_session(session_id) -> None
```

**Parameters:**
- `session_id` (str): Session ID

**Warning:** This permanently deletes all documents and chat history!

**Example:**
```python
manager.delete_session(session_id)
# Session directory completely removed
```

---

### Method: `cleanup_old_sessions(max_age_days)`

Delete sessions older than max_age_days.

```python
deleted = manager.cleanup_old_sessions(max_age_days: int = 30) -> List[str]
```

**Parameters:**
- `max_age_days` (int): Maximum session age in days (default: 30)

**Returns:** List of deleted session IDs

**Example:**
```python
deleted = manager.cleanup_old_sessions(max_age_days=7)
print(f"Cleaned up {len(deleted)} sessions")
```

---

## DocumentService API

**Module:** `backend.services.document_service`

**Purpose:** Handle document uploads and indexing.

### Class: `DocumentService`

#### Constructor

```python
DocumentService(session_manager: SessionManager, config_path: str = None)
```

**Parameters:**
- `session_manager` (SessionManager): SessionManager instance
- `config_path` (str): Path to RAG config (default: "backend/app/configs/default.yaml")

**Example:**
```python
from backend.services import DocumentService

doc_service = DocumentService(manager)
```

---

### Method: `upload_documents(session_id, files)`

Upload documents to a session.

```python
result = doc_service.upload_documents(
    session_id: str,
    files: List[BinaryIO]
) -> Dict
```

**Parameters:**
- `session_id` (str): Session ID
- `files` (List[BinaryIO]): File objects with .filename and .read()

**Returns:** Dictionary with upload results

**Result Structure:**
```python
{
    "uploaded_count": 2,
    "uploaded_files": ["paper.pdf", "guide.md"],
    "errors": [],  # or list of {"filename": ..., "error": ...}
    "session_id": "550e8400-..."
}
```

**Supported Formats:** `.pdf`, `.txt`, `.md`, `.html` (max 50MB each)

**Example:**
```python
# With Flask file upload
result = doc_service.upload_documents(
    session_id,
    request.files.getlist('files')
)

if result['errors']:
    print(f"Errors: {result['errors']}")
else:
    print(f"Uploaded: {result['uploaded_files']}")
```

---

### Method: `index_session(session_id)`

Index all documents in a session.

Performs: Load → Chunk → Embed → Store in Chroma

```python
result = doc_service.index_session(session_id) -> Dict
```

**Parameters:**
- `session_id` (str): Session ID

**Returns:** Dictionary with indexing results

**Result Structure (Success):**
```python
{
    "status": "success",
    "chunks_indexed": 42,
    "documents_indexed": ["paper.pdf", "guide.md"],
    "session_id": "550e8400-..."
}
```

**Result Structure (Error):**
```python
{
    "status": "error",
    "error": "No documents in session",
    "session_id": "550e8400-..."
}
```

**Example:**
```python
result = doc_service.index_session(session_id)
if result['status'] == 'success':
    print(f"Indexed {result['chunks_indexed']} chunks")
else:
    print(f"Error: {result['error']}")
```

---

### Method: `remove_document(session_id, filename)`

Remove a document and re-index.

```python
result = doc_service.remove_document(
    session_id: str,
    filename: str
) -> Dict
```

**Parameters:**
- `session_id` (str): Session ID
- `filename` (str): Document filename

**Returns:** Dictionary with result (same as index_session)

**Example:**
```python
result = doc_service.remove_document(session_id, "old_paper.pdf")
print(f"Removed and re-indexed: {result['chunks_indexed']} chunks")
```

---

### Method: `get_document_info(session_id)`

Get information about session documents.

```python
info = doc_service.get_document_info(session_id) -> Dict
```

**Parameters:**
- `session_id` (str): Session ID

**Returns:** Dictionary with document information

**Structure:**
```python
{
    "session_id": "550e8400-...",
    "documents": [
        {
            "filename": "paper.pdf",
            "size_bytes": 1048576,
            "extension": ".pdf"
        },
        ...
    ],
    "document_count": 2,
    "total_size_bytes": 2097152
}
```

**Example:**
```python
info = doc_service.get_document_info(session_id)
for doc in info['documents']:
    print(f"{doc['filename']}: {doc['size_bytes']} bytes")
```

---

## ChatService API

**Module:** `backend.services.chat_service`

**Purpose:** Handle queries and chat interactions.

### Class: `ChatService`

#### Constructor

```python
ChatService(session_manager: SessionManager, config_path: str = None)
```

**Parameters:**
- `session_manager` (SessionManager): SessionManager instance
- `config_path` (str): Path to RAG config

**Example:**
```python
from backend.services import ChatService

chat_service = ChatService(manager)
```

---

### Method: `query(session_id, query, save_to_history)`

Execute a query using session documents.

```python
result = chat_service.query(
    session_id: str,
    query: str,
    save_to_history: bool = True
) -> Dict
```

**Parameters:**
- `session_id` (str): Session ID
- `query` (str): User query text
- `save_to_history` (bool): Save to history (default: True)

**Returns:** Dictionary with response

**Result Structure (Success):**
```python
{
    "answer": "This paper discusses...",
    "sources": ["paper.pdf", "guide.md"],
    "session_id": "550e8400-...",
    "context_documents": 2
}
```

**Result Structure (Error):**
```python
{
    "error": "Error message",
    "session_id": "550e8400-..."
}
```

**Example:**
```python
result = chat_service.query(session_id, "What is the main topic?")

if 'error' in result:
    print(f"Error: {result['error']}")
else:
    print(f"Answer: {result['answer']}")
    print(f"Sources: {', '.join(result['sources'])}")
```

---

### Method: `get_chat_history(session_id)`

Get chat history for a session.

```python
history = chat_service.get_chat_history(session_id) -> List[Dict]
```

**Parameters:**
- `session_id` (str): Session ID

**Returns:** List of chat messages

**Example:**
```python
history = chat_service.get_chat_history(session_id)
for msg in history:
    print(f"{msg['role']}: {msg['content']}")
    if 'sources' in msg:
        print(f"  Sources: {msg['sources']}")
```

---

### Method: `get_session_context(session_id)`

Get session information and document stats.

```python
context = chat_service.get_session_context(session_id) -> Dict
```

**Parameters:**
- `session_id` (str): Session ID

**Returns:** Dictionary with session context

**Structure:**
```python
{
    "session_id": "550e8400-...",
    "created": "2025-01-15T10:30:00",
    "documents": ["paper.pdf", "guide.md"],
    "indexed_chunks": 42,
    "total_size_bytes": 2097152,
    "messages_count": 5
}
```

**Example:**
```python
context = chat_service.get_session_context(session_id)
print(f"Session created: {context['created']}")
print(f"Documents: {len(context['documents'])}")
print(f"Chat messages: {context['messages_count']}")
```

---

## Usage Examples

### Example 1: Complete Workflow

```python
from backend.services import (
    SessionManager,
    DocumentService,
    ChatService
)

# 1. Initialize services
manager = SessionManager()
doc_service = DocumentService(manager)
chat_service = ChatService(manager)

# 2. Create session
session_id = manager.create_session()
print(f"Created session: {session_id}")

# 3. Upload documents
result = doc_service.upload_documents(session_id, uploaded_files)
print(f"Uploaded: {result['uploaded_files']}")

# 4. Index documents
index_result = doc_service.index_session(session_id)
print(f"Indexed {index_result['chunks_indexed']} chunks")

# 5. Query
response = chat_service.query(session_id, "What is this about?")
print(f"Answer: {response['answer']}")
print(f"Sources: {response['sources']}")

# 6. Get history
history = chat_service.get_chat_history(session_id)
print(f"Chat history: {len(history)} messages")
```

---

### Example 2: Flask Integration

```python
from flask import Flask, request, jsonify
from backend.services import (
    SessionManager,
    DocumentService,
    ChatService
)

app = Flask(__name__)
manager = SessionManager()
doc_service = DocumentService(manager)
chat_service = ChatService(manager)

@app.route('/session/create', methods=['POST'])
def create_session():
    session_id = manager.create_session()
    return jsonify({"session_id": session_id})

@app.route('/documents/upload/<session_id>', methods=['POST'])
def upload_documents(session_id):
    files = request.files.getlist('files')
    result = doc_service.upload_documents(session_id, files)
    return jsonify(result)

@app.route('/documents/index/<session_id>', methods=['POST'])
def index_documents(session_id):
    result = doc_service.index_session(session_id)
    return jsonify(result)

@app.route('/chat/query/<session_id>', methods=['POST'])
def query(session_id):
    data = request.json
    result = chat_service.query(session_id, data['query'])
    return jsonify(result)

@app.route('/chat/history/<session_id>', methods=['GET'])
def get_history(session_id):
    history = chat_service.get_chat_history(session_id)
    return jsonify({"messages": history})

if __name__ == '__main__':
    app.run(debug=True)
```

---

### Example 3: FastAPI Integration

```python
from fastapi import FastAPI, File, UploadFile
from backend.services import (
    SessionManager,
    DocumentService,
    ChatService
)

app = FastAPI()
manager = SessionManager()
doc_service = DocumentService(manager)
chat_service = ChatService(manager)

@app.post("/session/create")
async def create_session():
    session_id = manager.create_session()
    return {"session_id": session_id}

@app.post("/documents/upload/{session_id}")
async def upload_documents(session_id: str, files: list[UploadFile]):
    result = doc_service.upload_documents(session_id, files)
    return result

@app.post("/documents/index/{session_id}")
async def index_documents(session_id: str):
    result = doc_service.index_session(session_id)
    return result

@app.post("/chat/query/{session_id}")
async def query(session_id: str, query: str):
    result = chat_service.query(session_id, query)
    return result

@app.get("/chat/history/{session_id}")
async def get_history(session_id: str):
    history = chat_service.get_chat_history(session_id)
    return {"messages": history}
```

---

## Error Handling

### Common Errors and Handling

```python
# Error: Session not found
try:
    info = manager.get_session_info("invalid_id")
except ValueError as e:
    print(f"Error: {e}")  # "Session not found: invalid_id"

# Error: Document upload failed
result = doc_service.upload_documents(session_id, files)
if result['errors']:
    for error in result['errors']:
        print(f"{error['filename']}: {error['error']}")

# Error: Query failed
result = chat_service.query(session_id, query)
if 'error' in result:
    print(f"Query failed: {result['error']}")
```

---

## Integration Guide

### Using with a FastAPI Backend

1. Install dependencies:
```bash
uv sync
```

2. Create API routes:
```python
# api.py
from fastapi import FastAPI
from backend.services import SessionManager, DocumentService, ChatService

app = FastAPI()
manager = SessionManager()
doc_service = DocumentService(manager)
chat_service = ChatService(manager)

# Add endpoints as shown in examples above
```

3. Run server:
```bash
uv run uvicorn api:app --reload
```

---

### Using in a Desktop Application

```python
# main.py
from backend.services import (
    SessionManager,
    DocumentService,
    ChatService
)

def main():
    manager = SessionManager()
    doc_service = DocumentService(manager)
    chat_service = ChatService(manager)
    
    # Your application logic here
```

---

**API documentation complete!** For UI integration, see `docs/ARCHITECTURE.md`.
