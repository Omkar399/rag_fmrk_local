# 🧠 Local Modular RAG Pipeline

A **fully local**, **modular**, and **production-ready** Retrieval-Augmented Generation (RAG) system with a **modern Next.js UI**, **FastAPI backend**, and **LM Studio integration**. Build powerful chat applications with your own documents—no cloud, no API keys, complete offline operation.

## ✨ Features

- ✅ **Modern Web UI** - Beautiful Next.js + Tailwind CSS + shadcn/ui interface with dark mode
- ✅ **Session Management** - Isolated document contexts per user session
- ✅ **Document Upload** - Upload PDFs/TXT/MD/HTML directly in the UI
- ✅ **Local LLM** - Integrate with LM Studio or Ollama for private inference
- ✅ **Modular Backend** - Swap components via YAML (embedder, chunker, retriever, reranker)
- ✅ **Hybrid Retrieval** - Dense (embeddings) + Sparse (BM25) with RRF fusion
- ✅ **Fast Performance** - Optimized for speed (250-300 token generations, ~0.2s temperature)
- ✅ **Markdown Support** - Rich formatting in chat (lists, code blocks, bold, etc.)
- ✅ **REST API** - FastAPI backend for easy integration
- ✅ **Persistent Storage** - Chroma vector store with session isolation
- ✅ **Offline-First** - Zero network dependencies after setup

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
│       ├── chroma_db/                # Vector index
│       ├── metadata.json             # Session info
│       └── chat_history.json         # Messages
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

1. **Create a Session** - Click "New Chat" to start
2. **Upload Documents** - Drag & drop or click to upload PDFs/TXT/MD files
3. **Index Documents** - Click "Index Documents" to process and embed
4. **Ask Questions** - Type queries and get AI responses with source citations
5. **View Sources** - See which documents the answer came from

## ⚙️ Configuration

Edit `backend/app/configs/default.yaml` to customize:

### Production Config (Best Quality)
```yaml
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
```

### CPU-Optimized Config
```yaml
embedder:
  component: "embed.minilm"
retriever:
  component: "retriever.dense"
reranker:
  component: "rerank.noop"
```

## 🔌 REST API

Use the FastAPI backend directly without the UI:

### Create Session
```bash
curl -X POST http://localhost:8000/api/sessions
# Returns: "abc123def456..."
```

### Upload Documents
```bash
curl -X POST http://localhost:8000/api/sessions/{session_id}/documents/upload \
  -F "files=@document.pdf"
```

### Index Documents
```bash
curl -X POST http://localhost:8000/api/sessions/{session_id}/documents/index
```

### Query
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
│  SentenceChunker │  Split by sentences
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

## 📊 Performance Optimizations

- **Max Tokens**: Reduced to 300 tokens (50-70% faster, same quality)
- **Temperature**: 0.2 for deterministic, faster decoding
- **Reranking**: Disabled (uses `rerank.noop`) - embeddings already high quality
- **Retriever**: Reduced to top 5 documents
- **Compression**: Intelligent sentence selection with token budgets

See `PERFORMANCE_OPTIMIZATIONS.md` for details.

## 🚀 Roadmap

- [ ] Streaming chat responses
- [ ] Document management (delete, update)
- [ ] Export chat history
- [ ] Multi-user support
- [ ] Analytics dashboard
- [ ] Voice input/output
- [ ] Image understanding
- [ ] Custom knowledge graphs

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
