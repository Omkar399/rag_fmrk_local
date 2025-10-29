# 🧠 Local Modular RAG Pipeline (Chroma-based, Cutting Edge)

A **fully local**, **modular**, and **experiment-friendly** Retrieval-Augmented Generation (RAG) pipeline.  
Designed for **rapid component swapping** (chunker, embedder, retriever, reranker, generator) and **offline operation** using open-source tools.

---

## ⚙️ Tech Stack

| Layer | Default Component | Alternatives |
|--------|-------------------|---------------|
| Loader | FSLoader (PDF/HTML/TXT) | Web loader, API ingestor |
| Chunker | SemanticChunker | SentenceChunker |
| Embedder | HuggingFace (`BAAI/bge-small-en-v1.5`) | `MiniLM-L6-v2`, `gte-base`, etc. |
| Vector Store | **Chroma (Persistent)** | FAISS, Milvus |
| Retriever | Hybrid (Dense + BM25 + RRF) | Dense only, Sparse only |
| Reranker | Local Cross-Encoder (`bge-reranker-base`) | None, `bge-reranker-large` |
| Compressor | Sentence-level with token budget | None |
| Generator (LLM) | Ollama (`llama3.1:8b`) | Mistral, Gemma, Llama-3-70B (local) |

---

## 📁 Folder Structure

```
app/
  interfaces.py          # abstract interfaces for modularity
  registry.py            # plugin registry (string → class)
  pipeline.py            # orchestration logic
  configs/
    default.yaml         # main config file
    fast.yaml            # lightweight CPU config
  components/
    loaders.py
    chunkers.py
    embedders.py
    stores.py
    retrievers.py
    rerankers.py
    compressors.py
    generators.py
    prompts.py
```

---

## 🧉 1. Interfaces

Defines the contracts for every stage of the pipeline.  
Each component implements a simple interface (`Loader`, `Chunker`, `Embedder`, etc.) so you can swap modules freely.

```python
class Loader(Protocol): ...
class Chunker(Protocol): ...
class Embedder(Protocol): ...
class VectorStore(Protocol): ...
class Retriever(Protocol): ...
class Reranker(Protocol): ...
class Compressor(Protocol): ...
class Generator(Protocol): ...
```

---

## 🧱 2. Registry (Plugin System)

Each component registers itself under a short name.

```python
@register("embed.hf")
class HFEmbedder(Embedder): ...
```

You can then create it dynamically:

```python
embedder = create("embed.hf", model_name="BAAI/bge-small-en-v1.5")
```

---

## ⚙️ 3. Configuration (YAML)

Change the pipeline behavior just by editing a config file.

```yaml
# app/configs/default.yaml
loader:
  component: "fs.loader"
  args: { data_dir: "data" }

chunker:
  component: "chunk.semantic"
  args: { chunk_size: 1000, overlap: 150 }

embedder:
  component: "embed.hf"
  args: { model_name: "BAAI/bge-small-en-v1.5" }

store:
  component: "store.chroma"
  args: { path: "./chroma_db", collection: "kb" }

retriever:
  component: "retriever.hybrid"
  args:
    dense_top_k: 40
    sparse_top_k: 40
    fused_top_k: 18
    rrf_constant: 60

reranker:
  component: "rerank.bge"
  args: { model_name: "BAAI/bge-reranker-base", top_k: 10 }

compressor:
  component: "compress.sentences"
  args: { token_budget: 6000 }

generator:
  component: "gen.ollama"
  args: { model: "llama3.1:8b", timeout: 120 }

prompt:
  system: |
    You are a careful assistant. Use only provided CONTEXT.
    Cite sources from meta.source. If missing, say you don't know.
```

To switch configurations:
```bash
python app/pipeline.py --config app/configs/fast.yaml
```

---

## 🧰 4. Components Overview

### 🔹 Loaders
- Load `.pdf`, `.txt`, `.md`, `.html`
- Clean text and attach metadata (`source` path)

### 🔹 Chunkers
- **SentenceChunker**: fixed windows + overlap  
- **SemanticChunker**: splits by topic drift using embeddings

### 🔹 Embedders
- Local `sentence-transformers` models (HuggingFace)
- Example: `BAAI/bge-small-en-v1.5` (384-d)

### 🔹 Vector Store
- **Chroma** with persistence (`./chroma_db`)
- Stores embeddings + documents + metadata
- Query by cosine similarity or dot product

### 🔹 Retrievers
- **DenseRetriever** (embeddings)
- **BM25Retriever** (keyword)
- **HybridRetriever** (RRF fusion)

### 🔹 Reranker
- Local `FlagEmbedding` cross-encoder (BGE reranker)
- Sorts top chunks by semantic match

### 🔹 Compressor
- Keeps top-scoring sentences under a token budget
- Reduces hallucination & latency

### 🔹 Generator
- Local Ollama model (`llama3.1:8b`, `mistral`, etc.)
- Receives query + compressed context → generates answer
- Includes source citations

---

## ⚡️ 5. Pipeline Flow

```
        ┌────────────┐
        │   Loader    │
        └──────┬──────┘
               │
          Chunker
               │
          Embedder
               │
          VectorStore (Chroma)
               │
          HybridRetriever
               │
          Reranker (BGE)
               │
          Compressor
               │
          Generator (LLM)
               ↓
          Response + Citations
```

---

## 🚀 6. Run the Pipeline

```bash
# install dependencies
pip install -U llama-index-core llama-index-embeddings-huggingface \
  llama-index-vector-stores-chroma chromadb \
  rank-bm25 FlagEmbedding sentence-transformers \
  unstructured pdfplumber beautifulsoup4 nltk

# optional: install Ollama for local LLMs
# mac/linux → https://ollama.com/download
# then pull your model
ollama pull llama3.1:8b

# run the pipeline
python app/pipeline.py
```

Then interact:
```
Q> What is this document about?
A> ...
```

---

## 🥪 7. Swapping Components

| Goal | Config Change |
|------|----------------|
| Faster CPU run | change embedder → `MiniLM-L6-v2` |
| Disable reranking | `reranker.component: rerank.noop` |
| Use dense-only search | `retriever.component: retriever.dense` |
| Use Mistral instead of Llama | `generator.args.model: mistral` |
| Larger context | `compressor.args.token_budget: 12000` |

---

## 🧠 8. Modern Features Implemented

✅ **Hybrid retrieval (dense + sparse)**  
✅ **RRF fusion**  
✅ **Cross-encoder reranking (BGE)**  
✅ **Context compression**  
✅ **Persistent local Chroma DB**  
✅ **Offline embeddings + LLM**  
✅ **Pluggable YAML configs**  
✅ **Clear interfaces for A/B testing**

---

## 📈 9. Evaluation Hooks (optional)

You can plug in `FaithfulnessEvaluator` from `llama_index.core.evaluation`
to score:
- *Faithfulness* (supported by retrieved context)
- *Context recall/precision*
- *Latency metrics*

---

## 💾 10. Example: Fast Config (CPU laptops)

```yaml
embedder:
  component: "embed.hf"
  args: { model_name: "sentence-transformers/all-MiniLM-L6-v2" }

reranker:
  component: "rerank.bge"
  args: { model_name: "BAAI/bge-reranker-v2-m3", top_k: 5 }

generator:
  component: "gen.ollama"
  args: { model: "mistral", timeout: 60 }

retriever:
  args:
    dense_top_k: 20
    sparse_top_k: 20
    fused_top_k: 10
```

---

## 🔒 11. Fully Offline Operation

After initial model downloads:
- Hugging Face models cached in `~/.cache/huggingface`
- Chroma stores data locally
- Ollama models cached under `~/.ollama/models`
- No network calls required ✅

---

## 📘 12. Roadmap Extensions

| Idea | Description |
|------|-------------|
| Add FAISS backend | Swap `store.chroma` → `store.faiss` |
| Add multi-agent retrieval | Implement planner + evidence agents |
| Add reranker ensembles | Chain multiple rerankers |
| Add evaluation dashboard | Track Recall@K, Faithfulness |
| Add JSON or structured generation | Use constrained decoding templates |

---

## 🧏️‍⚖️ Summary

This modular pipeline provides:

- **Composability** — swap any module via YAML.
- **Reproducibility** — deterministic configs.
- **Performance** — hybrid retrieval + reranking + compression.
- **Privacy** — all models and data local.
- **Flexibility** — research-friendly structure.

Ideal for **experimentation, benchmarking, or local assistants** that require RAG grounding without cloud dependencies.

---

## 🤩 License
MIT (recommended). All components use open models under permissive licenses.

