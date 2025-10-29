"""Document service for uploading and indexing documents."""

import sys
import shutil
from pathlib import Path
from typing import List, Dict, BinaryIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.pipeline import RAGPipeline
from .session_manager import SessionManager


class DocumentService:
    """Service for handling document uploads and indexing per session.
    
    Handles:
    - Document upload to session storage
    - Document indexing (chunking, embedding, storage)
    - Document removal
    - Session document management
    
    Example:
        >>> session_manager = SessionManager()
        >>> doc_service = DocumentService(session_manager)
        >>> session_id = session_manager.create_session()
        >>> doc_service.upload_documents(session_id, [file1, file2])
        >>> doc_service.index_session(session_id)
    """
    
    ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".html"}
    MAX_FILE_SIZE_MB = 50
    
    def __init__(self, session_manager: SessionManager, config_path: str = None):
        """Initialize document service.
        
        Args:
            session_manager: SessionManager instance
            config_path: Path to RAG pipeline config
        """
        self.session_manager = session_manager
        self.config_path = config_path or "backend/app/configs/default.yaml"
    
    def upload_documents(
        self,
        session_id: str,
        files: List[BinaryIO]
    ) -> Dict:
        """Upload documents to session storage.
        
        Args:
            session_id: Session ID
            files: List of file objects (Streamlit UploadedFile or file-like objects)
        
        Returns:
            Dictionary with upload results
            
        Example:
            >>> result = doc_service.upload_documents(session_id, files)
            >>> print(result['uploaded_count'])
            2
            >>> print(result['uploaded_files'])
            ['paper.pdf', 'guide.md']
        """
        docs_path = self.session_manager.get_documents_path(session_id)
        uploaded_files = []
        errors = []
        
        for file in files:
            try:
                # Get filename - support both Streamlit UploadedFile (.name) and regular files (.filename)
                filename = getattr(file, "name", None) or getattr(file, "filename", None)
                if not filename:
                    errors.append({"filename": "unknown", "error": "File must have name or filename attribute"})
                    continue
                
                # Validate file
                error = self._validate_file(file)
                if error:
                    errors.append({"filename": filename, "error": error})
                    continue
                
                # Save file
                file_path = docs_path / filename
                with open(file_path, "wb") as f:
                    f.write(file.read())
                
                uploaded_files.append(filename)
            
            except Exception as e:
                filename = getattr(file, "name", None) or getattr(file, "filename", None) or "unknown"
                errors.append({"filename": filename, "error": str(e)})
        
        return {
            "uploaded_count": len(uploaded_files),
            "uploaded_files": uploaded_files,
            "errors": errors,
            "session_id": session_id,
        }
    
    def index_session(self, session_id: str) -> Dict:
        """Index all documents in a session.
        
        Performs:
        - Load documents from session directory
        - Chunk into pieces
        - Generate embeddings
        - Store in session-specific Chroma DB
        
        Args:
            session_id: Session ID
        
        Returns:
            Dictionary with indexing results
            
        Example:
            >>> result = doc_service.index_session(session_id)
            >>> print(result['status'])
            'success'
            >>> print(result['chunks_indexed'])
            42
        """
        try:
            # Get document paths
            docs_path = self.session_manager.get_documents_path(session_id)
            chroma_path = self.session_manager.get_chroma_db_path(session_id)
            
            if not any(docs_path.iterdir()):
                return {
                    "status": "error",
                    "error": "No documents in session",
                    "session_id": session_id,
                }
            
            # Temporarily change the data directory in pipeline config
            # by creating a session-specific config
            import tempfile
            import yaml
            
            # Load default config
            config_path = Path(self.config_path)
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            
            # Create session-specific pipeline
            pipeline = RAGPipeline(self.config_path)
            
            # Override paths for this session
            pipeline.loader.data_dir = str(docs_path)
            pipeline.vector_store.path = chroma_path
            pipeline.vector_store.collection = None  # Reset collection
            
            # Reinitialize vector store with session path
            from app.components.stores import ChromaVectorStore
            pipeline.vector_store = ChromaVectorStore(
                path=chroma_path,
                collection_name="documents"
            )
            
            # Index documents
            num_chunks = pipeline.index(clear_existing=True)
            
            # Get indexed documents
            indexed_docs = [f.name for f in docs_path.iterdir() if f.is_file()]
            
            # Update session metadata
            self.session_manager.update_session_metadata(
                session_id,
                indexed_chunks=num_chunks,
                documents=indexed_docs
            )
            
            return {
                "status": "success",
                "chunks_indexed": num_chunks,
                "documents_indexed": indexed_docs,
                "session_id": session_id,
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "session_id": session_id,
            }
    
    def remove_document(self, session_id: str, filename: str) -> Dict:
        """Remove a document from session and re-index.
        
        Args:
            session_id: Session ID
            filename: Document filename to remove
        
        Returns:
            Dictionary with result
        """
        try:
            docs_path = self.session_manager.get_documents_path(session_id)
            file_path = docs_path / filename
            
            if not file_path.exists():
                return {
                    "status": "error",
                    "error": f"Document not found: {filename}",
                    "session_id": session_id,
                }
            
            # Remove file
            file_path.unlink()
            
            # Re-index remaining documents
            result = self.index_session(session_id)
            result["removed_file"] = filename
            
            return result
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "session_id": session_id,
            }
    
    def get_document_info(self, session_id: str) -> Dict:
        """Get information about documents in a session.
        
        Args:
            session_id: Session ID
        
        Returns:
            Dictionary with document information
        """
        docs_path = self.session_manager.get_documents_path(session_id)
        documents = []
        total_size = 0
        
        if docs_path.exists():
            for file_path in docs_path.iterdir():
                if file_path.is_file():
                    size = file_path.stat().st_size
                    documents.append({
                        "filename": file_path.name,
                        "size_bytes": size,
                        "extension": file_path.suffix,
                    })
                    total_size += size
        
        return {
            "session_id": session_id,
            "documents": documents,
            "document_count": len(documents),
            "total_size_bytes": total_size,
        }
    
    def _validate_file(self, file) -> str:
        """Validate file for upload.
        
        Args:
            file: File object (Streamlit UploadedFile or file-like object)
        
        Returns:
            Error message if invalid, empty string if valid
        """
        # Check extension - support both .name (Streamlit) and .filename
        filename = getattr(file, "name", None) or getattr(file, "filename", None)
        if not filename:
            return "File must have name or filename attribute"
        
        ext = Path(filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            return f"File type not allowed: {ext}. Allowed: {self.ALLOWED_EXTENSIONS}"
        
        # Check size
        if hasattr(file, "seek") and hasattr(file, "tell"):
            try:
                file.seek(0, 2)  # Seek to end
                size_bytes = file.tell()
                file.seek(0)  # Seek to start
                
                if size_bytes > self.MAX_FILE_SIZE_MB * 1024 * 1024:
                    return f"File too large: {size_bytes / (1024*1024):.1f}MB (max: {self.MAX_FILE_SIZE_MB}MB)"
            except:
                # If seek fails, skip size check (some file objects don't support it)
                pass
        
        return ""  # Valid
