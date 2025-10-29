"""Reranking components."""

from typing import List, Tuple
from app.interfaces import Document
from app.registry import register
import warnings
import torch

# Suppress tokenizer warnings from FlagEmbedding
warnings.filterwarnings("ignore", message=".*XLMRobertaTokenizerFast.*")


@register("rerank.bge")
class BGEReranker:
    """BGE cross-encoder reranker for semantic relevance - optimized for speed."""
    
    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-base",
        top_k: int = 10,
        use_gpu: bool = True,
        batch_size: int = 32
    ):
        """Initialize BGE reranker with GPU acceleration.
        
        Args:
            model_name: HuggingFace cross-encoder model
            top_k: Number of results to return
            use_gpu: Whether to use GPU if available
            batch_size: Batch size for processing (higher = faster but more memory)
        """
        self.model_name = model_name
        self.top_k = top_k
        self.batch_size = batch_size
        self.use_gpu = use_gpu and torch.cuda.is_available()
        
        try:
            from FlagEmbedding import FlagReranker
            # Enable GPU and optimize for speed
            self.reranker = FlagReranker(
                model_name, 
                use_fp16=True,
                device="cuda" if self.use_gpu else "cpu"
            )
        except ImportError:
            raise ImportError("FlagEmbedding required for BGE reranking")
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: int = None
    ) -> List[Tuple[Document, float]]:
        """Rerank documents by relevance to query - optimized."""
        k = top_k or self.top_k
        
        if not documents:
            return []
        
        # ⚡ OPTIMIZATION 1: Skip reranking for small result sets
        if len(documents) <= 3:
            return [(doc, 1.0) for doc in documents]
        
        # ⚡ OPTIMIZATION 2: Only rerank top 50 documents max
        docs_to_rerank = documents[:50]
        
        # Prepare query-document pairs
        pairs = [[query, doc.content] for doc in docs_to_rerank]
        
        # ⚡ OPTIMIZATION 3: Batch processing for speed
        scores = self.reranker.compute_score(
            pairs,
            batch_size=self.batch_size,
            max_length=512  # Limit token length
        )
        
        # Sort by score
        sorted_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )
        
        # Return top-k with scores
        results = [
            (docs_to_rerank[i], float(scores[i]))
            for i in sorted_indices[:k]
        ]
        
        return results


@register("rerank.noop")
class NoOpReranker:
    """No-op reranker that returns documents as-is - ultra-fast."""
    
    def __init__(self, top_k: int = 10):
        """Initialize no-op reranker.
        
        Args:
            top_k: Number of results to return
        """
        self.top_k = top_k
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: int = None
    ) -> List[Tuple[Document, float]]:
        """Return documents without reranking - instant response."""
        k = top_k or self.top_k
        # Return documents with dummy scores
        return [(doc, 1.0) for doc in documents[:k]]
