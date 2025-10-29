"""Context compression components."""

from typing import List
from app.interfaces import Document
from app.registry import register


@register("compress.sentences")
class SentenceCompressor:
    """Compress context to fit token budget using sentence selection."""
    
    def __init__(self, token_budget: int = 6000):
        """Initialize sentence compressor.
        
        Args:
            token_budget: Maximum tokens in compressed context
        """
        self.token_budget = token_budget
    
    def compress(
        self,
        documents: List[Document],
        query: str = "",
        token_budget: int = None
    ) -> str:
        """Compress documents into context string."""
        budget = token_budget or self.token_budget
        
        try:
            import nltk
            # Try to download punkt_tab first (newer), fall back to punkt
            try:
                nltk.download("punkt_tab", quiet=True)
            except:
                nltk.download("punkt", quiet=True)
            
            from nltk.tokenize import sent_tokenize
        except ImportError:
            raise ImportError("nltk required for sentence compression")
        
        # Collect all sentences from documents
        sentences = []
        for doc in documents:
            sents = sent_tokenize(doc.content)
            for sent in sents:
                sentences.append({
                    "text": sent,
                    "source": doc.metadata.get("source", "unknown")
                })
        
        # Simple greedy selection: take sentences until budget exceeded
        compressed = []
        current_tokens = 0
        
        for sent_obj in sentences:
            sent = sent_obj["text"]
            # Rough estimate: 1 token ≈ 4 characters
            sent_tokens = len(sent) / 4
            
            if current_tokens + sent_tokens <= budget:
                compressed.append(sent)
                current_tokens += sent_tokens
            else:
                break
        
        # Format context with source citations
        context = "\n\n".join(compressed)
        if context:
            context = f"Context:\n{context}"
        
        return context


@register("compress.noop")
class NoOpCompressor:
    """No-op compressor that concatenates all documents."""
    
    def __init__(self, token_budget: int = 6000):
        """Initialize no-op compressor."""
        self.token_budget = token_budget
    
    def compress(
        self,
        documents: List[Document],
        query: str = "",
        token_budget: int = None
    ) -> str:
        """Return all documents concatenated."""
        context = "\n\n".join(
            [doc.content for doc in documents]
        )
        
        if context:
            context = f"Context:\n{context}"
        
        return context
