# 🚀 Streamlit UI Setup Guide

## Prerequisites

Before running the Streamlit UI, ensure:

1. ✅ **LM Studio is running** with `qwen2.5-7b-instruct-1m` model loaded
   - Start LM Studio
   - Load the model in Local Server tab
   - Server should run at `http://127.0.0.1:1234`

2. ✅ **Dependencies installed**
   ```bash
   uv sync
   ```

---

## Running the Streamlit App

### Option 1: Using uv (Recommended)

```bash
cd /Users/omkarpodey/rag_frmk
uv run streamlit run frontend/streamlit_app.py
```

### Option 2: Direct Python

```bash
cd /Users/omkarpodey/rag_frmk
streamlit run frontend/streamlit_app.py
```

---

## What You'll See

1. **Welcome Screen** - Initial prompt to create a session
2. **Sidebar** - Session management
   - Create new session
   - View session stats
   - Delete session

3. **Main Content** (after creating session)
   - **Left Panel**: Document management
     - Upload documents (PDF, TXT, MD, HTML)
     - View indexed documents
     - Document statistics
   
   - **Right Panel**: Chat interface
     - Chat messages with sources
     - Ask questions about documents
     - View source citations

---

## Workflow

### 1. Create Session
- Click "➕ New Session" in sidebar
- Session ID appears in sidebar

### 2. Upload Documents
- Click "Upload documents" in left panel
- Select multiple files (PDF, TXT, MD, HTML)
- Click "⬆️ Upload & Index"
- Wait for indexing to complete

### 3. Start Chatting
- Type question in chat input
- Get answers with source citations
- View sources by clicking expander

### 4. Manage Session
- View stats in sidebar
- Delete session when done
- Create new session for different documents

---

## File Structure

```
frontend/
├── streamlit_app.py          ← Main entry point
├── .streamlit/
│   └── config.toml          ← Streamlit config
├── utils/
│   ├── __init__.py
│   └── formatters.py        ← Formatting utilities
└── pages/                   ← (Future: multi-page setup)
```

---

## Environment Variables (Optional)

Create `.env` file in project root:

```bash
# Streamlit settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=false

# Backend settings
SESSIONS_DIR=sessions
LM_STUDIO_URL=http://127.0.0.1:1234
```

---

## Troubleshooting

### "Cannot connect to LM Studio"
- Make sure LM Studio is running
- Server should be at `http://127.0.0.1:1234`
- Verify model is loaded

### "Module not found" errors
- Run: `uv sync`
- Restart the app: `Ctrl+C` and run again

### Slow performance
- Use "Fast" config (in future versions)
- Reduce chunk size in backend config
- Use MiniLM embedder instead of BGE

### Session not found
- Session may have expired
- Create a new session
- Old sessions in `sessions/` directory can be deleted

---

## Performance Tips

1. **First Run**: Will download models (~1GB+)
   - Be patient on first startup
   - Models are cached locally

2. **Optimal Settings**:
   - Document size: Keep under 50MB per file
   - Concurrent uploads: 5-10 files at a time
   - Query timeout: 120 seconds

3. **Memory**: 
   - Requires ~4GB RAM minimum
   - 8GB+ recommended for smooth operation

---

## API Integration (Alternative)

If you don't want the UI, use the backend services directly:

```python
from backend.services import SessionManager, DocumentService, ChatService

manager = SessionManager()
doc_service = DocumentService(manager)
chat_service = ChatService(manager)

# Create session
session_id = manager.create_session()

# Upload & index
doc_service.upload_documents(session_id, files)
doc_service.index_session(session_id)

# Query
result = chat_service.query(session_id, "Your question")
```

See `docs/API.md` for complete API reference.

---

## Keyboard Shortcuts (Streamlit)

- `R` - Rerun app
- `C` - Clear cache
- `K` - Show keyboard shortcuts
- `Ctrl+C` - Stop server

---

## Next Steps

1. ✅ Start LM Studio with model loaded
2. ✅ Run: `uv run streamlit run frontend/streamlit_app.py`
3. ✅ Create a session
4. ✅ Upload documents
5. ✅ Start asking questions!

---

**Enjoy your local RAG chat experience! 🚀**
