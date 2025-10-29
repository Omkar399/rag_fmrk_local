# 🎯 LM Studio Setup Guide

Your RAG pipeline is now configured to use **LM Studio** with `qwen2.5-7b-instruct-1m`.

## 📋 Setup Steps

### 1. Install LM Studio

Download from: https://lmstudio.ai/

Or via command line:
```bash
# macOS
brew install lmstudio

# Or download directly from https://lmstudio.ai/download
```

### 2. Load the Model in LM Studio

1. Open **LM Studio**
2. Click the **Models** tab (left sidebar)
3. Search for: `qwen2.5-7b-instruct-1m`
4. Click **Download** (about 7.7GB)
5. Wait for download to complete
6. Once downloaded, click the **Local Server** tab (rocket icon)
7. Select the model: `qwen2.5-7b-instruct-1m`
8. Click **Start Server**

Expected output:
```
LM Studio Server running at http://127.0.0.1:1234
Model: qwen2.5-7b-instruct-1m loaded
Ready for API calls
```

### 3. Verify the Connection

```bash
# Test if LM Studio is running
curl http://127.0.0.1:1234/v1/models

# Should return:
# {"object":"list","data":[{"id":"qwen2.5-7b-instruct-1m","object":"model"}]}
```

### 4. Run Your RAG Pipeline

```bash
# Make sure you're in the project directory
cd /Users/omkarpodey/rag_frmk

# The pipeline is now configured for LM Studio
uv run python3 -m app.pipeline --index --query "Your question"
```

---

## ⚙️ Configuration

The pipeline is configured in `app/configs/default.yaml`:

```yaml
generator:
  component: "gen.lmstudio"
  args:
    model: "qwen2.5-7b-instruct-1m"
    base_url: "http://127.0.0.1:1234"
    timeout: 120
    max_tokens: 1000
    temperature: 0.7
```

### Customize Settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `model` | qwen2.5-7b-instruct-1m | Model identifier |
| `base_url` | http://127.0.0.1:1234 | LM Studio server URL |
| `timeout` | 120 | Request timeout (seconds) |
| `max_tokens` | 1000 | Max response length |
| `temperature` | 0.7 | Sampling temperature (0-1) |

---

## 🧪 Test It Works

1. **Start LM Studio Server** (load model and click Start)

2. **In another terminal**, run:
```bash
uv run python3 -m app.pipeline
```

3. **At the prompt**:
```
Q> index                    # Build index from data/
Q> What is this about?      # Query with LM Studio
Q> exit
```

Expected flow:
```
🔍 Retrieving documents...
  ✓ Retrieved 5 documents
✍️  Generating answer...
  ✓ Generated answer

📚 Answer:
[Real LM Studio response here]
```

---

## 🆘 Troubleshooting

### "Cannot connect to LM Studio at http://127.0.0.1:1234"

**Solution**: Make sure LM Studio is running with the model loaded:
1. Open LM Studio
2. Go to **Local Server** tab
3. Select model: `qwen2.5-7b-instruct-1m`
4. Click **Start Server**

### Model Won't Download

**Solution**: 
- Check internet connection
- Model is ~7.7GB, ensure you have space
- Try downloading from LM Studio UI directly

### Slow Response Generation

**Solution**: 
- This is normal for local inference
- `qwen2.5-7b` on CPU takes 10-30 seconds per response
- For faster responses, use GPU acceleration in LM Studio settings

### Want to Use a Different Model?

**Solution**: Update `app/configs/default.yaml`:

```yaml
generator:
  args:
    model: "your-model-name"  # Change this
```

Then load that model in LM Studio and restart the server.

---

## 📊 Alternative Models for LM Studio

| Model | Size | Speed | Quality | Command |
|-------|------|-------|---------|---------|
| qwen2.5-7b-instruct | 7.7GB | Medium | High | ✅ Currently using |
| mistral-7b-instruct | 7.4GB | Fast | Good | Change in YAML |
| neural-chat-7b | 7.4GB | Fast | Good | Change in YAML |
| llama2-7b-chat | 6.7GB | Fast | Good | Change in YAML |
| qwen2.5-14b-instruct | 14GB | Slow | Very High | Requires more VRAM |

---

## 🎯 Usage with LM Studio

### Interactive Mode
```bash
uv run python3 -m app.pipeline
Q> index              # Build index
Q> Your question      # Get answer from LM Studio
Q> exit
```

### Single Query
```bash
uv run python3 -m app.pipeline --index --query "What is this document about?"
```

### Python API
```python
from app.pipeline import RAGPipeline

pipeline = RAGPipeline("app/configs/default.yaml")
pipeline.index()

result = pipeline.query("Your question")
print(result.answer)
print(result.source_citations)
```

---

## 🔗 Useful Links

- **LM Studio**: https://lmstudio.ai/
- **Qwen Models**: https://github.com/QwenLM/Qwen2.5
- **OpenAI API Docs**: https://platform.openai.com/docs/api-reference/chat/create

---

## 📝 Quick Reference

**Start LM Studio Server:**
1. Open LM Studio
2. Local Server tab → Select model → Start Server
3. Server runs at `http://127.0.0.1:1234`

**Run RAG Pipeline:**
```bash
cd /Users/omkarpodey/rag_frmk
uv run python3 -m app.pipeline
```

**That's it!** Your pipeline now uses LM Studio for local inference. 🚀
