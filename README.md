# 🧠 Local Modular RAG Pipeline

A **fully local**, **modular**, and **experiment-friendly** Retrieval-Augmented Generation (RAG) pipeline built with modern open-source components. Swap components freely via YAML configuration, run completely offline, and never send your data to the cloud.

## ✨ Features

- ✅ **Fully Modular** - Swap any component via YAML (embedder, chunker, retriever, reranker, LLM)
- ✅ **Hybrid Retrieval** - Dense (embeddings) + Sparse (BM25) with RRF fusion
- ✅ **Cross-Encoder Reranking** - BGE reranker for semantic relevance
- ✅ **Context Compression** - Intelligent sentence-level compression with token budgets
- ✅ **Local LLM Support** - Integrate with Ollama or use mock generator for testing
- ✅ **Persistent Storage** - Chroma vector store for reusable indexes
- ✅ **Offline-First** - Zero network dependencies after model downloads
- ✅ **Interactive CLI** - Query your knowledge base interactively
- ✅ **Production-Ready** - CLI arguments, logging, error handling

## 🚀 Quick Start

### 1. Prerequisites

- Python >=3.10
- `uv` package manager (install from https://github.com/astral-sh/uv)

### 2. Install Dependencies with `uv`

```bash
# Install all dependencies in one command
uv sync

# Or activate the environment for development
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate on Windows
```

### 3. Prepare Your Data

Create a `data/` directory with your documents:

```bash
mkdir data
# Add PDF, HTML, TXT, or MD files to data/
# Examples:
# - data/document.pdf
# - data/guide.md
# - data/webpage.html
```

### 4. Run the Pipeline

```bash
# Interactive mode (index, then query)
python -m app.pipeline

# Or with fast CPU config
python -m app.pipeline --config app/configs/fast.yaml

# Index and query directly
python -m app.pipeline --index --query "What is this about?"
```

## 📁 Project Structure

```
app/
├── __init__.py
├── interfaces.py          # Abstract interfaces for components
├── registry.py            # Plugin registration system
├── pipeline.py            # Main orchestration logic
├── components/
│   ├── __init__.py
│   ├── loaders.py         # Document loading (PDF, HTML, TXT, MD)
│   ├── chunkers.py        # Text splitting strategies
│   ├── embedders.py       # Text embeddings (HuggingFace)
│   ├── stores.py          # Vector storage (Chroma)
│   ├── retrievers.py      # Retrieval (Dense, BM25, Hybrid)
│   ├── rerankers.py       # Reranking (BGE, NoOp)
│   ├── compressors.py     # Context compression
│   ├── generators.py      # LLM generation (Ollama, Mock)
│   └── prompts.py         # Prompt templates
├── configs/
│   ├── default.yaml       # Full-featured config
│   └── fast.yaml          # CPU-optimized config
data/
├── document.pdf           # Your documents here
├── guide.md
└── webpage.html
chroma_db/                 # Persistent vector store (auto-created)
```

## ⚙️ Configuration

The pipeline is configured via YAML. Edit `app/configs/default.yaml` to customize:

### Default Configuration (Best Quality)

```yaml
loader: "load.fs"                    # Load from filesystem
chunker: "chunk.sentence"            # Split at sentence boundaries
embedder: "embed.hf"                 # HuggingFace embeddings
  model: "BAAI/bge-small-en-v1.5"   # BGE small model
store: "store.chroma"                # Persistent Chroma DB
retriever: "retriever.hybrid"        # Hybrid dense + sparse
  dense_top_k: 40
  sparse_top_k: 40
  fused_top_k: 10
reranker: "rerank.bge"               # BGE cross-encoder
compressor: "compress.sentences"     # Smart compression
generator: "gen.ollama"              # Local LLM via Ollama
  model: "llama3.1:8b"
```

### Fast Configuration (CPU-Optimized)

```yaml
embedder: "embed.minilm"             # Lightweight MiniLM
retriever: "retriever.dense"         # Dense only (faster)
reranker: "rerank.noop"              # Skip reranking
compressor: "compress.sentences"     # Still compress
generator: "gen.mock"                # Testing without LLM
```

### Swap Components Easily

| Goal | Change |
|------|--------|
| Use Mistral LLM | `generator.args.model: "mistral"` |
| Disable reranking | `reranker.component: "rerank.noop"` |
| CPU-only mode | Use `fast.yaml` config |
| Larger context budget | `compressor.args.token_budget: 12000` |

## 🎯 Usage Examples

### Interactive Mode

```bash
python -m app.pipeline

# Then at the prompt:
Q> index                    # Build the index
Q> What is this about?      # Query the knowledge base
Q> info                     # Show configuration
Q> exit                     # Exit
```

### Single Query

```bash
python -m app.pipeline --index --query "What are the main topics?"
```

### With Custom Config

```bash
python -m app.pipeline --config app/configs/fast.yaml --index
```

### Programmatic Usage

```python
from app.pipeline import RAGPipeline

# Create pipeline
pipeline = RAGPipeline("app/configs/default.yaml")

# Index documents
pipeline.index(clear_existing=True)

# Query
result = pipeline.query("What is this document about?")
print(result.answer)
print(result.source_citations)
```

## 📊 Pipeline Architecture

```
┌─────────────┐
│   Loader    │  Load PDF/HTML/TXT/MD files
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Chunker    │  Split into manageable pieces
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Embedder   │  Generate dense embeddings
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  Vector Store    │  Persistent Chroma DB
│  (Chroma)        │
└──────┬───────────┘
       │
       ├─────────────────────┬────────────────────┐
       │                     │                    │
       ▼                     ▼                    ▼
  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
  │Dense Search │  │ BM25 Search │  │  (Future)   │
  └────┬────────┘  └────┬────────┘  └─────┬───────┘
       │                │                  │
       └────────┬───────┴──────────────────┘
                │
                ▼
         ┌────────────────┐
         │ RRF Fusion     │  Combine results
         └────┬───────────┘
              │
              ▼
         ┌────────────────┐
         │   Reranker     │  Semantic relevance ranking
         │   (BGE)        │
         └────┬───────────┘
              │
              ▼
         ┌────────────────┐
         │ Compressor     │  Token-budget compression
         └────┬───────────┘
              │
              ▼
         ┌────────────────┐
         │  Generator     │  LLM answer generation
         │  (Ollama)      │  with source citations
         └────────────────┘
```

## 🔧 Advanced Configuration

### Using Different Embeddings

```yaml
embedder:
  component: "embed.minilm"
  args:
    model_name: "sentence-transformers/all-MiniLM-L6-v2"
```

### Disable Reranking (Faster)

```yaml
reranker:
  component: "rerank.noop"
  args:
    top_k: 5
```

### Different Chunking Strategy

```yaml
chunker:
  component: "chunk.fixed"  # or "chunk.semantic"
  args:
    chunk_size: 1024
    overlap: 200
```

## 📦 Installing Additional Models

### For BGE Embeddings (Recommended)

```bash
# Already included in dependencies
```

### For Ollama LLM Integration

```bash
# Install Ollama: https://ollama.com/download
ollama pull llama3.1:8b   # ~4.7GB
# or
ollama pull mistral       # ~5GB
ollama pull neural-chat   # ~4GB
```

### Verify Ollama is Running

```bash
# Should return "Ollama is running"
curl http://localhost:11434/api/tags
```

## 🧪 Testing

Run tests with:

```bash
pytest -v
```

Or with the mock generator for quick testing (no LLM needed):

```python
pipeline = RAGPipeline("app/configs/fast.yaml")  # Uses mock generator
pipeline.index()
result = pipeline.query("Test query")
print(result.answer)
```

## 🔍 Troubleshooting

### "Module not found" errors

```bash
# Reinstall dependencies
uv sync --reinstall
```

### Ollama connection errors

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

### Memory issues with large embeddings

Use the fast config with MiniLM:

```bash
python -m app.pipeline --config app/configs/fast.yaml
```

### No documents found

Ensure you have documents in the `data/` directory:

```bash
ls data/
# Should show: document.pdf, guide.md, etc.
```

## 📚 Architecture Decisions

### Why Chroma?
- ✅ Persistent storage (survives restarts)
- ✅ Easy setup (no external database)
- ✅ Supports Cosine similarity + other metrics
- ✅ Built-in Python integration

### Why Hybrid Retrieval?
- ✅ Dense: Captures semantic meaning
- ✅ Sparse (BM25): Catches keywords
- ✅ RRF Fusion: Balanced combination

### Why BGE Reranker?
- ✅ Cross-encoder model (more accurate than bi-encoder)
- ✅ Understands query-document pairs
- ✅ Significantly improves ranking

## 🎓 Learning Resources

- [LlamaIndex Core](https://docs.llamaindex.ai/)
- [Chroma DB](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [BGE Models](https://github.com/FlagOpen/FlagEmbedding)
- [Ollama](https://ollama.com/)

## 📋 Component Reference

### Loaders
- `load.fs` - Filesystem loader (PDF, HTML, TXT, MD)

### Chunkers
- `chunk.sentence` - Sentence boundary splitting
- `chunk.semantic` - Semantic drift detection
- `chunk.fixed` - Fixed-size chunks

### Embedders
- `embed.hf` - HuggingFace sentence-transformers (BGE small)
- `embed.minilm` - Lightweight MiniLM

### Vector Stores
- `store.chroma` - Persistent Chroma database

### Retrievers
- `retriever.dense` - Embedding-based retrieval
- `retriever.bm25` - Keyword-based retrieval
- `retriever.hybrid` - Combined with RRF fusion

### Rerankers
- `rerank.bge` - BGE cross-encoder reranking
- `rerank.noop` - No reranking (for speed)

### Compressors
- `compress.sentences` - Sentence selection with token budget
- `compress.noop` - No compression

### Generators
- `gen.ollama` - Local LLM via Ollama
- `gen.mock` - Mock generator for testing

## 🔐 Privacy & Offline Operation

- ✅ **No cloud dependencies** - Everything runs locally
- ✅ **Models cached locally** - HuggingFace models in `~/.cache/huggingface`
- ✅ **Data never leaves** - Vector store on your machine
- ✅ **Ollama LLM** - Runs on localhost:11434
- ✅ **Chroma persistence** - Your index stays local

## 📈 Performance Tips

1. **For fast CPU inference**: Use `app/configs/fast.yaml`
2. **For GPU acceleration**: Ensure PyTorch has CUDA support
3. **For large documents**: Increase chunk overlap
4. **For better quality**: Increase `reranker.top_k` and `compressor.token_budget`

## 🚀 Roadmap

- [ ] FAISS vector store backend
- [ ] Multi-document summarization
- [ ] Evaluation metrics (RAGAS)
- [ ] Document update/deletion workflows
- [ ] Web UI dashboard
- [ ] Streaming responses
- [ ] Multi-language support
- [ ] Custom knowledge graph integration

## 📝 License

MIT License - see LICENSE file

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional loaders (CSV, JSON, Markdown tables)
- More embedding models
- Performance optimizations
- Documentation improvements
- Test coverage

---

**Built with ❤️ for researchers, developers, and curious learners.**
