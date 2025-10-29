"""Document retrieval strategies."""

from typing import List, Tuple
from app.interfaces import Document
from app.registry import register


@register("retriever.dense")
class DenseRetriever:
    """Dense retriever using embeddings."""
    
    def __init__(self, embedder, vector_store, top_k: int = 10):
        """Initialize dense retriever.
        
        Args:
            embedder: Embedder component
            vector_store: Vector store component
            top_k: Number of results to return
        """
        self.embedder = embedder
        self.vector_store = vector_store
        self.top_k = top_k
    
    def retrieve(self, query: str, top_k: int = None) -> List[Tuple[Document, float]]:
        """Retrieve documents using dense embeddings."""
        k = top_k or self.top_k
        query_embedding = self.embedder.embed(query)
        results = self.vector_store.query(query_embedding, top_k=k)
        return results


@register("retriever.bm25")
class BM25Retriever:
    """BM25 sparse retriever (keyword-based)."""
    
    def __init__(self, documents: List[Document] = None):
        """Initialize BM25 retriever.
        
        Args:
            documents: Documents to index
        """
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            raise ImportError("rank-bm25 required for BM25 retrieval")
        
        self.documents = documents or []
        self.bm25 = None  # Lazy initialization
        self._build_index()
    
    def _build_index(self):
        """Build BM25 index."""
        from rank_bm25 import BM25Okapi
        
        # Only initialize if we have documents
        if not self.documents:
            self.bm25 = None
            return
        
        # Tokenize documents
        tokenized_docs = [
            doc.content.lower().split() for doc in self.documents
        ]
        
        self.bm25 = BM25Okapi(tokenized_docs)
    
    def update_documents(self, documents: List[Document]) -> None:
        """Update documents in index."""
        self.documents = documents
        self._build_index()
    
    def retrieve(self, query: str, top_k: int = 10) -> List[Tuple[Document, float]]:
        """Retrieve documents using BM25."""
        if not self.bm25 or not self.documents:
            return []
        
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        top_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )[:top_k]
        
        results = [
            (self.documents[i], float(scores[i])) for i in top_indices
        ]
        return results


@register("retriever.hybrid")
class HybridRetriever:
    """Hybrid retriever combining dense and sparse search with RRF."""
    
    def __init__(
        self,
        embedder,
        vector_store,
        documents: List[Document] = None,
        dense_top_k: int = 40,
        sparse_top_k: int = 40,
        fused_top_k: int = 10,
        rrf_constant: int = 60
    ):
        """Initialize hybrid retriever.
        
        Args:
            embedder: Embedder component
            vector_store: Vector store component
            documents: Documents for BM25 indexing
            dense_top_k: Top-k for dense retrieval
            sparse_top_k: Top-k for sparse (BM25) retrieval
            fused_top_k: Top-k after fusion
            rrf_constant: RRF constant (higher = more balanced)
        """
        self.dense_retriever = DenseRetriever(embedder, vector_store, dense_top_k)
        self.bm25_retriever = BM25Retriever(documents or [])
        self.fused_top_k = fused_top_k
        self.rrf_constant = rrf_constant
    
    def update_documents(self, documents: List[Document]) -> None:
        """Update documents in BM25 index."""
        self.bm25_retriever.update_documents(documents)
    
    def retrieve(self, query: str, top_k: int = None) -> List[Tuple[Document, float]]:
        """Retrieve using hybrid method with RRF fusion."""
        k = top_k or self.fused_top_k
        
        # Get dense results
        dense_results = self.dense_retriever.retrieve(query)
        
        # Get sparse results
        sparse_results = self.bm25_retriever.retrieve(query)
        
        # Apply RRF (Reciprocal Rank Fusion)
        fused_scores = self._rrf_fusion(
            dense_results, sparse_results
        )
        
        # Sort and return top-k
        sorted_results = sorted(
            fused_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:k]
        
        return [(doc, score) for doc, score in sorted_results]
    
    def _rrf_fusion(
        self,
        dense_results: List[Tuple[Document, float]],
        sparse_results: List[Tuple[Document, float]]
    ) -> dict:
        """Combine dense and sparse results using RRF."""
        fused = {}
        
        # Process dense results
        for rank, (doc, score) in enumerate(dense_results, 1):
            key = doc.content  # Use content as unique key
            rrf_score = 1.0 / (self.rrf_constant + rank)
            fused[key] = fused.get(key, 0) + rrf_score
        
        # Process sparse results
        for rank, (doc, score) in enumerate(sparse_results, 1):
            key = doc.content
            rrf_score = 1.0 / (self.rrf_constant + rank)
            fused[key] = fused.get(key, 0) + rrf_score
        
        # Reconstruct Document objects (take first occurrence)
        result_dict = {}
        for doc, _ in dense_results + sparse_results:
            if doc.content not in result_dict:
                result_dict[doc.content] = doc
        
        return {
            result_dict[content]: score
            for content, score in fused.items()
        }
