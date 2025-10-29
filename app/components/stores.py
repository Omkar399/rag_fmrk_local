"""Vector storage backends."""

import os
from typing import List, Tuple
from app.interfaces import Document
from app.registry import register


@register("store.chroma")
class ChromaVectorStore:
    """Persistent vector store using Chroma."""
    
    def __init__(self, path: str = "./chroma_db", collection_name: str = "documents"):
        """Initialize Chroma vector store.
        
        Args:
            path: Directory for persistent storage
            collection_name: Name of the collection
        """
        self.path = path
        self.collection_name = collection_name
        
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Ensure path exists
            os.makedirs(path, exist_ok=True)
            
            # Initialize client with persistent storage
            self.client = chromadb.PersistentClient(path=path)
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except ImportError:
            raise ImportError("chromadb required for Chroma vector store")
    
    def add(self, documents: List[Document], embeddings: List[List[float]]) -> None:
        """Add documents and their embeddings to store."""
        ids = [f"doc_{i}" for i in range(len(documents))]
        metadatas = [doc.metadata for doc in documents]
        contents = [doc.content for doc in documents]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas
        )
    
    def query(
        self,
        embedding: List[float],
        top_k: int = 10
    ) -> List[Tuple[Document, float]]:
        """Query store by embedding."""
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        
        documents_with_scores = []
        if results and results["documents"]:
            for i, (doc_text, metadata, distance) in enumerate(
                zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )
            ):
                # Convert distance to similarity (cosine distance to similarity)
                similarity = 1 - distance
                doc = Document(content=doc_text, metadata=metadata)
                documents_with_scores.append((doc, similarity))
        
        return documents_with_scores
    
    def clear(self) -> None:
        """Clear all data from store."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def get_count(self) -> int:
        """Get number of documents in store."""
        return self.collection.count()
