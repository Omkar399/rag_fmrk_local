"""Chat service for querying RAG pipeline with session context."""

import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.pipeline import RAGPipeline
from .session_manager import SessionManager


class ChatService:
    """Service for handling chat queries using session-specific documents.
    
    Integrates with SessionManager and RAGPipeline to provide:
    - Session-isolated queries
    - Automatic chat history management
    - Source tracking
    
    Example:
        >>> session_manager = SessionManager()
        >>> chat_service = ChatService(session_manager)
        >>> session_id = session_manager.create_session()
        >>> response = chat_service.query(session_id, "What is this about?")
        >>> print(response['answer'])
        >>> print(response['sources'])
    """
    
    def __init__(self, session_manager: SessionManager, config_path: str = None):
        """Initialize chat service.
        
        Args:
            session_manager: SessionManager instance
            config_path: Path to RAG pipeline config (default: default.yaml)
        """
        self.session_manager = session_manager
        self.config_path = config_path or "backend/app/configs/default.yaml"
    
    def query(
        self,
        session_id: str,
        query: str,
        save_to_history: bool = True
    ) -> Dict:
        """Execute a query using session-specific indexed documents.
        
        Args:
            session_id: Session ID
            query: User query text
            save_to_history: Whether to save to chat history (default: True)
        
        Returns:
            Dictionary with:
            - answer: Generated response
            - sources: List of source documents
            - session_id: Session ID
            - timestamp: When query was executed
        
        Example:
            >>> response = chat_service.query(session_id, "What is the main topic?")
            >>> print(response['answer'])
            'This paper discusses...'
            >>> print(response['sources'])
            ['paper.pdf', 'guide.md']
        """
        try:
            # Get session-specific Chroma DB path
            chroma_path = self.session_manager.get_chroma_db_path(session_id)
            
            # Load config
            import yaml
            from pathlib import Path
            
            config_path = Path(self.config_path)
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            
            # Create pipeline with default config
            from app.pipeline import RAGPipeline
            pipeline = RAGPipeline(self.config_path)
            
            # Manually reinitialize the vector store with session path
            from app.components.stores import ChromaVectorStore
            pipeline.vector_store = ChromaVectorStore(
                path=chroma_path,
                collection_name=config['store']['args'].get('collection_name', 'documents')
            )
            
            # Check if the vector store has data
            if pipeline.vector_store.get_count() == 0:
                return {
                    "error": "No documents indexed in this session. Please upload and index documents first.",
                    "session_id": session_id,
                }
            
            # IMPORTANT: Reinitialize the retriever with the new vector store
            from app.registry import Registry
            retriever_cfg = config.get("retriever", {})
            retriever_args = retriever_cfg.get("args", {}).copy()
            retriever_args["embedder"] = pipeline.embedder
            retriever_args["vector_store"] = pipeline.vector_store  # Use new vector store!
            
            pipeline.retriever = Registry.create(
                retriever_cfg.get("component", "retriever.hybrid"),
                **retriever_args
            )
            
            # Mark pipeline as indexed
            pipeline.is_indexed = True
            
            # Execute query
            result = pipeline.query(query)
            
            # Extract sources
            sources = result.source_citations if result.source_citations else []
            
            # Save to chat history if requested
            if save_to_history:
                self.session_manager.save_chat_message(
                    session_id,
                    "user",
                    query,
                    sources=sources
                )
                self.session_manager.save_chat_message(
                    session_id,
                    "assistant",
                    result.answer,
                    sources=sources
                )
            
            return {
                "answer": result.answer,
                "sources": sources,
                "session_id": session_id,
                "context_documents": len(result.context),
            }
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "session_id": session_id,
            }
    
    def get_chat_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session.
        
        Args:
            session_id: Session ID
        
        Returns:
            List of chat messages
            
        Example:
            >>> history = chat_service.get_chat_history(session_id)
            >>> for msg in history:
            ...     print(f"{msg['role']}: {msg['content']}")
        """
        return self.session_manager.get_chat_history(session_id)
    
    def clear_chat_history(self, session_id: str) -> None:
        """Clear chat history for a session.
        
        Args:
            session_id: Session ID
        """
        self.session_manager._save_chat_history(session_id, [])
    
    def get_session_context(self, session_id: str) -> Dict:
        """Get session information and indexed documents.
        
        Args:
            session_id: Session ID
        
        Returns:
            Dictionary with session info
            
        Example:
            >>> context = chat_service.get_session_context(session_id)
            >>> print(f"Documents: {context['documents']}")
            >>> print(f"Chunks indexed: {context['indexed_chunks']}")
        """
        info = self.session_manager.get_session_info(session_id)
        docs = self.session_manager.list_documents(session_id)
        
        return {
            "session_id": session_id,
            "created": info["created"],
            "documents": docs,
            "indexed_chunks": info["indexed_chunks"],
            "total_size_bytes": info.get("total_size_bytes", 0),
            "messages_count": len(self.get_chat_history(session_id)),
        }
