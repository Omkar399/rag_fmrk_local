"""Text embedding components."""

from typing import List
from app.registry import register


@register("embed.hf")
class HFEmbedder:
    """HuggingFace sentence-transformer embedder."""
    
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """Initialize HuggingFace embedder.
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except ImportError:
            raise ImportError("sentence_transformers required for HF embeddings")
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()


@register("embed.minilm")
class MiniLMEmbedder:
    """Lightweight MiniLM embedder for CPU."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize MiniLM embedder.
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except ImportError:
            raise ImportError("sentence_transformers required for MiniLM embeddings")
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
