"""Abstract interfaces for modular RAG components."""

from typing import Protocol, Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Document:
    """Represents a document chunk."""
    content: str
    metadata: Dict[str, Any]


@dataclass
class QueryResult:
    """Represents a query result with context and answer."""
    answer: str
    context: List[Document]
    source_citations: List[str]


class Loader(Protocol):
    """Protocol for document loaders."""
    
    def load(self) -> List[Document]:
        """Load documents from source."""
        ...


class Chunker(Protocol):
    """Protocol for text chunking."""
    
    def chunk(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        ...


class Embedder(Protocol):
    """Protocol for text embedding."""
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        ...
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        ...


class VectorStore(Protocol):
    """Protocol for vector storage."""
    
    def add(self, documents: List[Document], embeddings: List[List[float]]) -> None:
        """Add documents and embeddings to store."""
        ...
    
    def query(self, embedding: List[float], top_k: int = 10) -> List[Tuple[Document, float]]:
        """Query store by embedding, return (document, score) pairs."""
        ...
    
    def clear(self) -> None:
        """Clear all data from store."""
        ...


class Retriever(Protocol):
    """Protocol for document retrieval."""
    
    def retrieve(self, query: str, top_k: int = 10) -> List[Tuple[Document, float]]:
        """Retrieve relevant documents for query."""
        ...


class Reranker(Protocol):
    """Protocol for reranking retrieved documents."""
    
    def rerank(
        self, 
        query: str, 
        documents: List[Document], 
        top_k: int = 10
    ) -> List[Tuple[Document, float]]:
        """Rerank documents by relevance to query."""
        ...


class Compressor(Protocol):
    """Protocol for context compression."""
    
    def compress(
        self,
        documents: List[Document],
        query: str,
        token_budget: int = 6000
    ) -> str:
        """Compress documents into a context string respecting token budget."""
        ...


class Generator(Protocol):
    """Protocol for answer generation."""
    
    def generate(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate answer based on query and context."""
        ...
