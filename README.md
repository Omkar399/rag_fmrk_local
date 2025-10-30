# 🧠 Local Modular RAG Pipeline

A **fully local**, **modular**, and **production-ready** Retrieval-Augmented Generation (RAG) system with a **modern Next.js UI**, **FastAPI backend**, and **LM Studio integration**. Build powerful chat applications with your own documents—no cloud, no API keys, complete offline operation.

## ✨ Features

### 🎨 User Interface
- ✅ **Modern Web UI** - Beautiful Next.js + Tailwind CSS + shadcn/ui interface with dark mode
- ✅ **Streaming Responses** - Real-time token-by-token streaming with visual feedback
- ✅ **Session Management** - Named sessions with persistent storage and easy identification
- ✅ **Document Upload** - Drag & drop PDFs/TXT/MD/HTML directly in the UI
- ✅ **Markdown Support** - Rich formatting in chat (lists, code blocks, bold, tables, etc.)
- ✅ **Session Cleanup** - Clear all sessions with confirmation dialog

### 🧠 RAG Pipeline
- ✅ **Smart Chunking** - Token-based chunking (300-600 tokens) with semantic boundary detection
- ✅ **Rich Metadata** - Source paths, section titles, timestamps, doc types, and auto-summaries
- ✅ **Hybrid Retrieval** - Dense (embeddings) + Sparse (BM25) with RRF fusion
- ✅ **Local LLM** - Integrate with LM Studio or Ollama for private inference
- ✅ **Auto-Recovery** - ChromaDB and model cache corruption detection and recovery
- ✅ **Modular Backend** - Swap components via YAML (embedder, chunker, retriever, reranker)

### 🚀 Performance & Privacy
- ✅ **Fast Performance** - Optimized for speed (250-300 token generations, ~0.2s temperature)
- ✅ **Persistent Storage** - Chroma vector store with session isolation
- ✅ **Offline-First** - Zero network dependencies after setup, completely local
- ✅ **REST API** - FastAPI backend with Server-Sent Events (SSE) streaming

## 📁 Project Structure

```
rag_frmk/
├── backend/                          # Python FastAPI backend
│   ├── api.py                        # REST API endpoints
│   ├── app/
│   │   ├── interfaces.py             # Component protocols
│   │   ├── registry.py               # Plugin system
│   │   ├── pipeline.py               # RAG orchestration
│   │   ├── components/
│   │   │   ├── loaders.py            # Document loading
│   │   │   ├── chunkers.py           # Text splitting
│   │   │   ├── embedders.py          # Embeddings (BGE)
│   │   │   ├── stores.py             # Chroma vector store
│   │   │   ├── retrievers.py         # Dense/BM25/Hybrid
│   │   │   ├── rerankers.py          # BGE reranking
│   │   │   ├── generators.py         # LM Studio/Ollama
│   │   │   └── prompts.py            # Prompt templates
│   │   └── configs/
│   │       ├── default.yaml          # Production config
│   │       └── fast.yaml             # CPU-optimized config
│   └── services/
│       ├── session_manager.py        # Session lifecycle
│       ├── document_service.py       # Upload & indexing
│       ├── chat_service.py           # Query interface
│       └── storage_service.py        # File operations
│
├── frontend/
│   ├── nextjs/                       # Modern Next.js UI
│   │   ├── app/
│   │   │   ├── page.tsx              # Main chat interface
│   │   │   ├── layout.tsx            # Root layout
│   │   │   └── globals.css           # Global styles
│   │   ├── lib/
│   │   │   ├── api.ts                # API client (Axios)
│   │   │   └── store.ts              # State (Zustand)
│   │   ├── components/ui/            # shadcn/ui components
│   │   ├── package.json              # Node dependencies
│   │   └── tailwind.config.ts        # Tailwind config
│   │
│   └── docs/
│       ├── API.md                    # REST API documentation
│       ├── LMSTUDIO_SETUP.md         # LM Studio setup guide
│       └── LMSTUDIO_QUICK_START.txt  # Quick reference
│
├── sessions/                         # Session data (git-ignored)
│   └── {session-id}/
│       ├── documents/                # Uploaded files
│       ├── chroma_db/                # Vector index (auto-recovered if corrupted)
│       ├── metadata.json             # Session info (name, created, docs, chunks)
│       └── chat_history.json         # Full chat messages with sources
│
├── pyproject.toml                    # uv dependencies
├── run_all.sh                        # Start backend + frontend
├── NEXTJS_SETUP.md                   # Frontend setup guide
└── PERFORMANCE_OPTIMIZATIONS.md      # Optimization details
```

## 🚀 Quick Start

### Prerequisites

- **Python** >=3.10
- **Node.js** >=18.16.0
- **uv** package manager (https://github.com/astral-sh/uv)
- **LM Studio** (https://lmstudio.ai/) - for local LLM inference

### 1. Install Backend Dependencies

```bash
cd /Users/omkarpodey/rag_frmk
uv sync
```

### 2. Install Frontend Dependencies

```bash
cd frontend/nextjs
npm install
```

### 3. Setup LM Studio

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Load a model (e.g., `qwen2.5-7b-instruct-1m`)
3. Start the local server on `http://127.0.0.1:1234`

Verify it's running:
```bash
curl http://localhost:1234/v1/models
```

### 4. Start Backend & Frontend

**Option A: Use the provided script**
```bash
bash run_all.sh
```

**Option B: Start manually in separate terminals**

Terminal 1 - Backend:
```bash
cd /Users/omkarpodey/rag_frmk
uv run python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
cd /Users/omkarpodey/rag_frmk/frontend/nextjs
npm run dev
```

### 5. Open in Browser

Visit: **http://localhost:3000**

## 💬 Using the Chat Interface

1. **Create a Named Session** - Click "New Chat", give it a memorable name like "Research Notes"
2. **Upload Documents** - Drag & drop or click to upload PDFs/TXT/MD/HTML files
3. **Index Documents** - Click "Index Documents" to process with smart chunking
4. **Ask Questions** - Type queries and watch responses stream in real-time
5. **View Sources** - See which documents and sections the answer came from
6. **Manage Sessions** - Switch between named sessions in the sidebar
7. **Clear Sessions** - Use "Clear All Sessions" button to reset everything

## ⚙️ Configuration

Edit `backend/app/configs/default.yaml` to customize:

### Production Config (Best Quality)
```yaml
chunker:
  component: "chunk.smart-boundary"
  args:
    chunk_size_tokens: 450          # 300-600 token chunks
    overlap_percentage: 0.12        # 12% overlap for context
    model_name: "sentence-transformers/all-MiniLM-L6-v2"

retriever:
  component: "retriever.hybrid"
  args:
    dense_top_k: 15
    sparse_top_k: 15
    fused_top_k: 5

reranker:
  component: "rerank.noop"    # Optimized: skip expensive reranking
  args:
    top_k: 5

generator:
  component: "gen.lmstudio"
  args:
    model: "qwen2.5-7b-instruct-1m"
    base_url: "http://127.0.0.1:1234"
    max_tokens: 300            # Optimized for speed
    temperature: 0.2           # Deterministic responses
    # Note: streaming=True handled automatically for real-time responses
```

### CPU-Optimized Config (Fast)
```yaml
chunker:
  component: "chunk.smart-boundary"
  args:
    chunk_size_tokens: 300          # Smaller chunks for speed
    overlap_percentage: 0.10        # 10% overlap
    model_name: "sentence-transformers/all-MiniLM-L6-v2"

embedder:
  component: "embed.minilm"         # Lightweight embedder
retriever:
  component: "retriever.dense"      # Dense only (faster than hybrid)
reranker:
  component: "rerank.noop"          # Skip reranking
```

## 🔌 REST API

Use the FastAPI backend directly without the UI:

### Session Management

**Create Named Session**
```bash
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"name": "Research Papers"}'
# Returns: "abc123def456..."
```

**List All Sessions**
```bash
curl http://localhost:8000/api/sessions
# Returns: [{"id": "abc...", "name": "Research Papers", "created": "2025-10-30T..."}, ...]
```

**Delete All Sessions**
```bash
curl -X DELETE http://localhost:8000/api/sessions
```

### Document Operations

**Upload Documents**
```bash
curl -X POST http://localhost:8000/api/sessions/{session_id}/documents/upload \
  -F "files=@document.pdf"
```

**Index Documents**
```bash
curl -X POST http://localhost:8000/api/sessions/{session_id}/documents/index
```

### Chat (Streaming)

**Stream Response (SSE)**
```bash
curl -N http://localhost:8000/api/sessions/{session_id}/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this about?", "save_to_history": true}'
# Streams: data: {"type": "token", "content": "The"}
#          data: {"type": "token", "content": " document"}
#          data: {"type": "metadata", "sources": ["doc.pdf"]}
#          data: [DONE]
```

**Non-Streaming Query**
```bash
curl -X POST http://localhost:8000/api/sessions/{session_id}/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this about?"}'
```

See `docs/API.md` for complete endpoint documentation.

## 🎯 Pipeline Architecture

```
Upload Documents
       │
       ▼
┌──────────────────┐
│  FSLoader        │  Load PDF/HTML/TXT/MD
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  SmartBoundaryChunker  Token-based (300-600) + metadata
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  BGEEmbedder     │  Generate embeddings
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  ChromaVectorStore  Session-specific index
└────────┬─────────┘
         │
         ├──────────────────┬──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
    DenseRetriever   BM25Retriever      (RRF Fusion)
         │                  │                  │
         └──────────┬───────┴──────────────────┘
                    │
                    ▼
           ┌────────────────┐
           │  NoOpReranker  │  (Skip for speed)
           └────────┬───────┘
                    │
                    ▼
           ┌────────────────┐
           │ Compressor     │  Token budget compression
           └────────┬───────┘
                    │
                    ▼
           ┌────────────────┐
           │ LMStudioGenerator  Local LLM inference
           └────────────────┘
```

## 🔧 Component Reference

### Loaders
- `load.fs` - Filesystem (PDF, HTML, TXT, MD)

### Chunkers
- `chunk.smart-boundary` - Token-based with semantic boundary detection (headings, paragraphs, lists, code)
- `chunk.sentence` - Sentence boundaries
- `chunk.semantic` - Semantic drift detection
- `chunk.fixed` - Fixed size chunks

### Embedders
- `embed.hf` - BGE (BAAI/bge-small-en-v1.5)
- `embed.minilm` - Lightweight MiniLM

### Retrievers
- `retriever.dense` - Embedding search
- `retriever.bm25` - Keyword search
- `retriever.hybrid` - Combined with RRF

### Rerankers
- `rerank.bge` - BGE cross-encoder
- `rerank.noop` - No reranking (fast)

### Generators
- `gen.lmstudio` - LM Studio (http://127.0.0.1:1234)
- `gen.ollama` - Ollama (http://localhost:11434)
- `gen.mock` - Mock (testing)

## 🔍 Troubleshooting

### "Cannot connect to LM Studio"
```bash
# Verify LM Studio is running
curl http://localhost:1234/v1/models

# If not running, start LM Studio app
# or restart from terminal:
# python -m lmstudio server
```

### "No documents indexed"
1. Check documents uploaded successfully in UI
2. Click "Index Documents" button
3. Wait for indexing to complete (watch backend logs)

### Module not found errors
```bash
cd /Users/omkarpodey/rag_frmk
uv sync --reinstall
```

### Frontend won't connect to backend
```bash
# Check backend is running on port 8000
lsof -i :8000

# Check NEXT_PUBLIC_API_URL environment variable
echo $NEXT_PUBLIC_API_URL  # Should be http://localhost:8000
```

## 📊 Performance & Technical Highlights

### Smart Chunking
- **Token-based**: 300-600 tokens per chunk (not characters) for optimal context
- **Semantic boundaries**: Respects headings, paragraphs, lists, and code blocks
- **Rich metadata**: Every chunk includes source path, section title, timestamp, doc type, and auto-summary
- **Overlap**: 10-15% overlap between chunks to preserve context

### Streaming Architecture
- **Server-Sent Events (SSE)**: Real-time token streaming from backend to frontend
- **Visual feedback**: Blinking cursor effect before streaming starts
- **Token-by-token**: Each token displayed as received for smooth UX
- **Error handling**: Graceful fallback for non-streaming generators

### Robustness
- **Auto-recovery**: Detects and fixes corrupted ChromaDB and model cache
- **Session safety**: Directories auto-created if missing
- **Type safety**: Full TypeScript on frontend, type hints on backend

### Performance Optimizations
- **Max Tokens**: 300 tokens (50-70% faster, same quality)
- **Temperature**: 0.2 for deterministic, faster decoding
- **Reranking**: Disabled (uses `rerank.noop`) - embeddings already high quality
- **Retriever**: Top 5 documents after hybrid fusion
- **Compression**: Intelligent sentence selection with token budgets

See `PERFORMANCE_OPTIMIZATIONS.md` for details.

## 🚀 Roadmap

### ✅ Completed
- [x] Streaming chat responses (SSE with visual feedback)
- [x] Session naming and management
- [x] Smart token-based chunking
- [x] Rich metadata storage
- [x] Clear all sessions functionality
- [x] Auto-recovery for corrupted data

### 🔜 Coming Soon
- [ ] Document management (delete individual docs, update)
- [ ] Export chat history (JSON/Markdown)
- [ ] Multi-user support with authentication
- [ ] Analytics dashboard (usage stats, performance metrics)
- [ ] Voice input/output
- [ ] Image understanding (OCR, vision models)
- [ ] Custom knowledge graphs
- [ ] Advanced filtering (by date, doc type, etc.)

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional document loaders
- More embedding models
- Performance optimizations
- UI/UX enhancements
- Documentation

---

**Built with ❤️ for researchers, developers, and curious learners.**
