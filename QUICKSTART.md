# ⚡ Quick Start Guide

Get your RAG pipeline running in **5 minutes**!

## Step 1: Install with `uv` (30 seconds)

```bash
# If you don't have uv installed:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
cd /path/to/rag_frmk
uv sync
```

## Step 2: Add Your Documents (1 minute)

```bash
# Create data directory
mkdir -p data

# Add your documents (PDF, HTML, TXT, MD)
cp /path/to/your/documents/* data/

# Or create a simple test document
cat > data/test.md << 'EOF'
# Test Document

This is a sample document for the RAG pipeline.

## Features
- Local execution
- Modular design
- Easy to customize

## Usage
Just add your documents and run the pipeline!
EOF
```

## Step 3: Run Interactive Mode (1 minute)

```bash
# Start the pipeline
python -m app.pipeline

# At the prompt, type:
Q> index                    # Build the index (first time)
Q> What is this document?   # Ask your question
Q> exit                     # Exit
```

## Step 4: Test with Fast Config (Optional)

```bash
# Use lightweight models for testing (no LLM needed)
python -m app.pipeline --config app/configs/fast.yaml --index

# Then query
Q> Your question here
```

## Advanced: Command-Line Usage

```bash
# Index and query in one command
python -m app.pipeline --index --query "What is the main topic?"

# With custom config
python -m app.pipeline --config app/configs/fast.yaml --index

# View help
python -m app.pipeline --help
```

## For Full LLM Integration

Only needed if you want real LLM responses (optional for testing):

```bash
# Install Ollama from https://ollama.com/download
ollama pull llama3.1:8b

# Ollama will run on http://localhost:11434
# The pipeline will automatically use it
```

## 📊 What Happens

When you run the pipeline:

1. **Loader** 📂 - Reads all documents from `data/`
2. **Chunker** ✂️ - Splits into chunks (512 chars default)
3. **Embedder** 🔢 - Creates embeddings (BGE small model)
4. **Vector Store** 💾 - Saves to local Chroma DB
5. **Query Time:**
   - **Retriever** 🔍 - Finds relevant chunks (hybrid dense+sparse)
   - **Reranker** 🔄 - Ranks by relevance (BGE cross-encoder)
   - **Compressor** 📦 - Fits into context budget
   - **Generator** ✍️ - Generates answer (Ollama or mock)

## 🎯 Configuration

Switch components by editing config files:

```yaml
# app/configs/default.yaml
embedder:
  component: "embed.hf"
  args:
    model_name: "BAAI/bge-small-en-v1.5"
```

Common tweaks:

| Need | Change |
|------|--------|
| Faster inference | Use `fast.yaml` |
| Better quality | Increase `reranker.top_k` |
| More context | Increase `compressor.token_budget` |
| CPU only | Use MiniLM embedder + noop reranker |

## 📁 Directory Structure (After First Run)

```
data/                  # Your documents
├── document1.pdf
├── guide.md
└── ...

chroma_db/            # Vector store (auto-created)
├── chroma.sqlite
└── ...

app/                  # Pipeline code
├── pipeline.py
├── components/
├── configs/
└── ...
```

## ✅ Test It Works

```bash
# Quick test (< 1 min, no LLM needed)
python example_usage.py

# It creates data/README.md and indexes it
# Then queries the pipeline
```

## 🆘 Troubleshooting

**"No documents found"**
```bash
# Make sure data directory has files
ls data/
# Should show: document.pdf, guide.md, etc.
```

**"Module not found"**
```bash
# Reinstall dependencies
uv sync --reinstall
```

**"Connection refused" (Ollama)**
```bash
# This is OK! The mock generator will be used for fast.yaml
# For real LLM responses:
ollama pull llama3.1:8b
# Ollama automatically runs in background
```

## 🚀 Next Steps

1. **Read the full README** - Detailed documentation
2. **Explore configs** - See `app/configs/` for examples
3. **Swap components** - Try different embedders/rerankers
4. **Add more docs** - The pipeline scales to hundreds of documents
5. **Integrate LLM** - Set up Ollama for real responses

---

**Need help?** Check out the full README.md or see example_usage.py
