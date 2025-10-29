"""Reranking components."""

from typing import List, Tuple
from app.interfaces import Document
from app.registry import register


@register("rerank.bge")
class BGEReranker:
    """BGE cross-encoder reranker for semantic relevance."""
    
    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-base",
        top_k: int = 10
    ):
        """Initialize BGE reranker.
        
        Args:
            model_name: HuggingFace cross-encoder model
            top_k: Number of results to return
        """
        self.model_name = model_name
        self.top_k = top_k
        try:
            from FlagEmbedding import FlagReranker
            self.reranker = FlagReranker(model_name, use_fp16=True)
        except ImportError:
            raise ImportError("FlagEmbedding required for BGE reranking")
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: int = None
    ) -> List[Tuple[Document, float]]:
        """Rerank documents by relevance to query."""
        k = top_k or self.top_k
        
        if not documents:
            return []
        
        # Prepare query-document pairs
        pairs = [[query, doc.content] for doc in documents]
        
        # Get scores
        scores = self.reranker.compute_score(pairs)
        
        # Sort by score
        sorted_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )
        
        # Return top-k with scores
        results = [
            (documents[i], float(scores[i]))
            for i in sorted_indices[:k]
        ]
        
        return results


@register("rerank.noop")
class NoOpReranker:
    """No-op reranker that returns documents as-is."""
    
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
        """Return documents without reranking."""
        k = top_k or self.top_k
        # Return documents with dummy scores
        return [(doc, 1.0) for doc in documents[:k]]
