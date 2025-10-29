"""Text chunking strategies."""

from typing import List
from app.interfaces import Document
from app.registry import register


@register("chunk.sentence")
class SentenceChunker:
    """Split documents into chunks at sentence boundaries."""
    
    def __init__(self, chunk_size: int = 512, overlap: int = 100):
        """Initialize sentence chunker.
        
        Args:
            chunk_size: Target characters per chunk
            overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, documents: List[Document]) -> List[Document]:
        """Chunk documents at sentence boundaries."""
        try:
            import nltk
            # Try to download punkt_tab first (newer), fall back to punkt
            try:
                nltk.download("punkt_tab", quiet=True)
            except:
                nltk.download("punkt", quiet=True)
            
            from nltk.tokenize import sent_tokenize
        except ImportError:
            raise ImportError("nltk required for sentence chunking")
        
        chunked = []
        for doc in documents:
            sentences = sent_tokenize(doc.content)
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) <= self.chunk_size:
                    current_chunk += " " + sentence
                else:
                    if current_chunk:
                        chunked.append(
                            Document(
                                content=current_chunk.strip(),
                                metadata=doc.metadata.copy()
                            )
                        )
                        # Create overlap
                        overlap_size = min(
                            self.overlap,
                            len(current_chunk)
                        )
                        current_chunk = current_chunk[-overlap_size:]
                    current_chunk += " " + sentence
            
            if current_chunk:
                chunked.append(
                    Document(
                        content=current_chunk.strip(),
                        metadata=doc.metadata.copy()
                    )
                )
        
        return chunked


@register("chunk.semantic")
class SemanticChunker:
    """Split documents by semantic similarity (topic drift)."""
    
    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 100,
        similarity_threshold: float = 0.5,
        embedder=None
    ):
        """Initialize semantic chunker.
        
        Args:
            chunk_size: Target characters per chunk
            overlap: Overlap between chunks
            similarity_threshold: Threshold for semantic similarity
            embedder: Optional pre-configured embedder
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.similarity_threshold = similarity_threshold
        self.embedder = embedder
    
    def chunk(self, documents: List[Document]) -> List[Document]:
        """Chunk documents using semantic similarity."""
        if self.embedder is None:
            # Lazy import to avoid circular dependency
            from app.components.embedders import HFEmbedder
            self.embedder = HFEmbedder(model_name="BAAI/bge-small-en-v1.5")
        
        try:
            import nltk
            # Try to download punkt_tab first (newer), fall back to punkt
            try:
                nltk.download("punkt_tab", quiet=True)
            except:
                nltk.download("punkt", quiet=True)
            
            from nltk.tokenize import sent_tokenize
        except ImportError:
            raise ImportError("nltk required for semantic chunking")
        
        chunked = []
        for doc in documents:
            sentences = sent_tokenize(doc.content)
            if not sentences:
                continue
            
            chunks = self._semantic_split(sentences, doc)
            chunked.extend(chunks)
        
        return chunked
    
    def _semantic_split(self, sentences: List[str], original_doc: Document) -> List[Document]:
        """Split sentences by semantic coherence."""
        chunks = []
        current_chunk = ""
        current_sentences = []
        
        for i, sentence in enumerate(sentences):
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
                current_sentences.append(sentence)
            else:
                # Check semantic similarity before splitting
                if current_sentences:
                    chunks.append(
                        Document(
                            content=current_chunk.strip(),
                            metadata=original_doc.metadata.copy()
                        )
                    )
                current_chunk = sentence
                current_sentences = [sentence]
        
        if current_chunk:
            chunks.append(
                Document(
                    content=current_chunk.strip(),
                    metadata=original_doc.metadata.copy()
                )
            )
        
        return chunks


@register("chunk.fixed")
class FixedSizeChunker:
    """Split documents into fixed-size chunks."""
    
    def __init__(self, chunk_size: int = 512, overlap: int = 100):
        """Initialize fixed-size chunker.
        
        Args:
            chunk_size: Characters per chunk
            overlap: Character overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, documents: List[Document]) -> List[Document]:
        """Chunk documents using fixed sizes."""
        chunked = []
        
        for doc in documents:
            text = doc.content
            chunks_text = []
            
            for i in range(0, len(text), self.chunk_size - self.overlap):
                chunk = text[i : i + self.chunk_size]
                if chunk:
                    chunks_text.append(chunk)
            
            for chunk_text in chunks_text:
                chunked.append(
                    Document(
                        content=chunk_text,
                        metadata=doc.metadata.copy()
                    )
                )
        
        return chunked
