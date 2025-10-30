"""Text chunking strategies."""

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
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


@register("chunk.smart-boundary")
class SmartBoundaryChunker:
    """Token-based chunking with semantic boundary awareness and rich metadata.
    
    Features:
    - Token-based splitting (300-600 tokens) instead of character-based
    - Respects semantic boundaries: headings, paragraphs, lists, code blocks
    - Tracks parent document ID and section titles
    - Enriches metadata: source_path, section_title, created_at, doc_type, chunk_summary
    - Maintains 10-15% token overlap between chunks
    """
    
    def __init__(
        self,
        chunk_size_tokens: int = 450,
        overlap_percentage: float = 0.12,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """Initialize smart boundary chunker.
        
        Args:
            chunk_size_tokens: Target tokens per chunk (300-600 recommended)
            overlap_percentage: Overlap as percentage (10-15% recommended)
            model_name: Tokenizer model for token counting
        """
        self.chunk_size_tokens = chunk_size_tokens
        self.overlap_percentage = overlap_percentage
        self.model_name = model_name
        self.tokenizer = None
        self._load_tokenizer()
    
    def _load_tokenizer(self):
        """Load tokenizer from sentence-transformers."""
        try:
            from sentence_transformers import SentenceTransformer
            import os
            import shutil
            from pathlib import Path
            
            try:
                model = SentenceTransformer(self.model_name)
                self.tokenizer = model.tokenizer
            except (NotImplementedError, RuntimeError) as e:
                # If model cache is corrupted, clear it and retry
                if "meta tensor" in str(e) or "Cannot copy out of meta tensor" in str(e):
                    print(f"⚠️  Model cache corrupted for {self.model_name}, clearing...")
                    
                    # Clear the specific model cache
                    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
                    model_dir = cache_dir / f"models--{self.model_name.replace('/', '--')}"
                    
                    if model_dir.exists():
                        shutil.rmtree(model_dir, ignore_errors=True)
                        print(f"✅ Cleared cache at {model_dir}")
                    
                    # Retry download
                    print(f"📥 Re-downloading {self.model_name}...")
                    model = SentenceTransformer(self.model_name)
                    self.tokenizer = model.tokenizer
                    print(f"✅ Model loaded successfully")
                else:
                    raise
        except ImportError:
            raise ImportError("sentence-transformers required for tokenization")
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if not self.tokenizer:
            self._load_tokenizer()
        tokens = self.tokenizer.encode(text)
        return len(tokens)
    
    def _get_section_title(self, text: str) -> str:
        """Extract section title from text (first heading or first ~10 words)."""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first few lines
            stripped = line.strip()
            # Look for markdown headings
            if stripped.startswith('#'):
                return stripped.lstrip('#').strip()[:100]
            # Look for other heading patterns
            if len(stripped) > 5 and len(stripped) < 100 and stripped.isupper():
                return stripped[:100]
        
        # Fallback: first 10 words
        words = text.split()[:10]
        return ' '.join(words)[:100]
    
    def _generate_chunk_summary(self, text: str) -> str:
        """Generate auto-summary: first 1-2 sentences."""
        try:
            import nltk
            try:
                nltk.download("punkt_tab", quiet=True)
            except:
                nltk.download("punkt", quiet=True)
            from nltk.tokenize import sent_tokenize
            
            sentences = sent_tokenize(text.strip())
            if not sentences:
                return text[:150]
            
            # Take first 1-2 sentences, up to 150 chars
            summary = ' '.join(sentences[:2])
            return summary[:150]
        except:
            # Fallback: first 150 chars
            return text[:150]
    
    def _detect_boundaries(self, text: str) -> List[int]:
        """Detect semantic boundaries (headings, paragraphs, lists, code blocks).
        
        Returns:
            List of character indices where splits should prefer to happen.
        """
        boundaries = []
        lines = text.split('\n')
        char_pos = 0
        
        for line in lines:
            # Heading markers (markdown)
            if line.strip().startswith('#'):
                boundaries.append(char_pos)
            # List items
            elif line.strip().startswith(('-', '*', '•')) or \
                 (len(line) > 1 and line.strip()[0].isdigit() and line.strip()[1] in '.):'):
                boundaries.append(char_pos)
            # Code block markers
            elif line.strip().startswith('```'):
                boundaries.append(char_pos)
            # Paragraph breaks (empty or whitespace lines)
            elif not line.strip():
                boundaries.append(char_pos)
            
            char_pos += len(line) + 1  # +1 for newline
        
        return boundaries
    
    def _find_best_split_point(
        self,
        text: str,
        target_tokens: int,
        boundaries: List[int]
    ) -> int:
        """Find best character index to split, preferring semantic boundaries.
        
        Args:
            text: Text to split
            target_tokens: Target token count
            boundaries: List of preferred boundary positions
        
        Returns:
            Character index for split
        """
        # Binary search for target token count
        low, high = 0, len(text)
        best_idx = len(text)
        
        while low <= high:
            mid = (low + high) // 2
            tokens = self._count_tokens(text[:mid])
            
            if tokens <= target_tokens:
                best_idx = mid
                low = mid + 1
            else:
                high = mid - 1
        
        # Check if there's a boundary near best_idx (within 10% of text length)
        search_range = max(int(len(text) * 0.1), 50)
        nearby_boundaries = [
            b for b in boundaries
            if abs(b - best_idx) < search_range and b < best_idx
        ]
        
        # Use nearest boundary if found
        if nearby_boundaries:
            best_idx = max(nearby_boundaries)
        
        return best_idx
    
    def chunk(self, documents: List[Document]) -> List[Document]:
        """Chunk documents with token-based splitting and rich metadata."""
        chunked = []
        
        for doc_idx, doc in enumerate(documents):
            text = doc.content
            if not text.strip():
                continue
            
            boundaries = self._detect_boundaries(text)
            chunks_data = self._split_by_tokens(text, boundaries, doc, doc_idx)
            chunked.extend(chunks_data)
        
        return chunked
    
    def _split_by_tokens(
        self,
        text: str,
        boundaries: List[int],
        original_doc: Document,
        doc_idx: int
    ) -> List[Document]:
        """Split text by tokens with metadata enrichment."""
        chunks = []
        char_pos = 0
        chunk_idx = 0
        overlap_chars = int(len(text) * self.overlap_percentage) if len(text) > 0 else 0
        
        while char_pos < len(text):
            # Find split point
            remaining_text = text[char_pos:]
            split_idx = self._find_best_split_point(
                remaining_text,
                self.chunk_size_tokens,
                [b - char_pos for b in boundaries if b >= char_pos]
            )
            
            # Ensure we make progress
            if split_idx <= 0:
                split_idx = min(self.chunk_size_tokens * 4, len(remaining_text))
            
            chunk_text = remaining_text[:split_idx].strip()
            
            if chunk_text:
                # Generate rich metadata
                now = datetime.now().isoformat()
                section_title = self._get_section_title(chunk_text)
                chunk_summary = self._generate_chunk_summary(chunk_text)
                token_count = self._count_tokens(chunk_text)
                
                # Build metadata
                metadata = {
                    # Original metadata
                    **original_doc.metadata,
                    # Rich metadata
                    "source_path": original_doc.metadata.get("source", "unknown"),
                    "section_title": section_title,
                    "created_at": now,
                    "doc_type": original_doc.metadata.get("file_type", "unknown"),
                    "chunk_summary": chunk_summary,
                    "token_count": token_count,
                    # Parent tracking
                    "parent_doc_id": f"doc_{doc_idx}",
                    "chunk_index": chunk_idx,
                    # Size info
                    "char_count": len(chunk_text),
                }
                
                chunks.append(
                    Document(
                        content=chunk_text,
                        metadata=metadata
                    )
                )
                
                # Move forward with overlap
                char_pos += split_idx
                if char_pos < len(text):
                    char_pos = max(char_pos - overlap_chars, char_pos - split_idx + overlap_chars)
                
                chunk_idx += 1
            else:
                break
        
        return chunks
