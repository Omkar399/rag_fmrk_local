"""Session management for isolated document contexts."""

import os
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class SessionManager:
    """Manage user sessions with isolated Chroma DB and document storage.
    
    Each session has:
    - Unique session ID (UUID)
    - Isolated Chroma vector DB
    - Document storage directory
    - Metadata file
    - Chat history file
    
    Example:
        >>> manager = SessionManager()
        >>> session_id = manager.create_session()
        >>> manager.list_documents(session_id)
        []
        >>> manager.get_session_info(session_id)
        {'session_id': '...', 'created': '...', 'documents': []}
    """
    
    def __init__(self, sessions_dir: str = "sessions"):
        """Initialize session manager.
        
        Args:
            sessions_dir: Root directory for storing sessions
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def create_session(self, name: Optional[str] = None) -> str:
        """Create a new session with isolated storage.
        
        Args:
            name: Optional name for the session
        
        Returns:
            Session ID (UUID string)
            
        Example:
            >>> session_id = manager.create_session(name="My Research")
            >>> print(session_id)
            '550e8400-e29b-41d4-a716-446655440000'
        """
        session_id = str(uuid.uuid4())
        session_path = self.sessions_dir / session_id
        
        # Create directories
        (session_path / "chroma_db").mkdir(parents=True, exist_ok=True)
        (session_path / "documents").mkdir(parents=True, exist_ok=True)
        
        # Create metadata
        metadata = {
            "session_id": session_id,
            "name": name,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "documents": [],
            "indexed_chunks": 0,
            "total_size_bytes": 0,
        }
        
        self._save_metadata(session_id, metadata)
        
        # Create empty chat history
        self._save_chat_history(session_id, [])
        
        return session_id
    
    def get_session_path(self, session_id: str) -> Path:
        """Get the root path for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Path object for session directory
        """
        session_path = self.sessions_dir / session_id
        if not session_path.exists():
            raise ValueError(f"Session not found: {session_id}")
        return session_path
    
    def get_chroma_db_path(self, session_id: str) -> str:
        """Get Chroma DB path for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Absolute path to session's chroma_db directory
            
        Example:
            >>> path = manager.get_chroma_db_path(session_id)
            >>> print(path)
            '/path/to/sessions/550e8400.../chroma_db'
        """
        return str(self.get_session_path(session_id) / "chroma_db")
    
    def get_documents_path(self, session_id: str) -> Path:
        """Get documents directory path for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Path to session's documents directory
        """
        return self.get_session_path(session_id) / "documents"
    
    def list_documents(self, session_id: str) -> List[str]:
        """List all documents in a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of document filenames
            
        Example:
            >>> docs = manager.list_documents(session_id)
            >>> print(docs)
            ['paper.pdf', 'guide.md']
        """
        docs_path = self.get_documents_path(session_id)
        if not docs_path.exists():
            return []
        return [f.name for f in docs_path.iterdir() if f.is_file()]
    
    def get_session_info(self, session_id: str) -> Dict:
        """Get session information.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dictionary with session metadata
            
        Example:
            >>> info = manager.get_session_info(session_id)
            >>> print(info)
            {
                'session_id': '...',
                'created': '2025-01-15T10:30:00',
                'documents': ['paper.pdf'],
                'indexed_chunks': 42
            }
        """
        return self._load_metadata(session_id)
    
    def update_session_metadata(
        self,
        session_id: str,
        indexed_chunks: int,
        documents: List[str]
    ) -> None:
        """Update session metadata after indexing.
        
        Args:
            session_id: Session ID
            indexed_chunks: Number of chunks after indexing
            documents: List of indexed document names
        """
        metadata = self._load_metadata(session_id)
        metadata.update({
            "updated": datetime.now().isoformat(),
            "indexed_chunks": indexed_chunks,
            "documents": documents,
            "total_size_bytes": sum(
                (self.get_documents_path(session_id) / doc).stat().st_size
                for doc in documents
            )
        })
        self._save_metadata(session_id, metadata)
    
    def get_chat_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of chat messages
            
        Example:
            >>> history = manager.get_chat_history(session_id)
            >>> for msg in history:
            ...     print(f"{msg['role']}: {msg['content']}")
        """
        return self._load_chat_history(session_id)
    
    def save_chat_message(
        self,
        session_id: str,
        role: str,
        content: str,
        sources: Optional[List[str]] = None
    ) -> None:
        """Save a message to chat history.
        
        Args:
            session_id: Session ID
            role: "user" or "assistant"
            content: Message content
            sources: Optional list of source documents
        """
        history = self._load_chat_history(session_id)
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        if sources:
            message["sources"] = sources
        
        history.append(message)
        self._save_chat_history(session_id, history)
    
    def list_sessions(self) -> List[str]:
        """List all session IDs.
        
        Returns:
            List of session IDs
        """
        # Create sessions directory if it doesn't exist
        if not self.sessions_dir.exists():
            self.sessions_dir.mkdir(parents=True, exist_ok=True)
            return []
        
        return [d.name for d in self.sessions_dir.iterdir() if d.is_dir()]
    
    def list_sessions_with_names(self) -> List[Dict[str, Optional[str]]]:
        """List all sessions with their IDs and names.
        
        Returns:
            List of dicts with 'id' and 'name' keys
        """
        # Create sessions directory if it doesn't exist
        if not self.sessions_dir.exists():
            self.sessions_dir.mkdir(parents=True, exist_ok=True)
            return []
        
        sessions = []
        for session_dir in self.sessions_dir.iterdir():
            if session_dir.is_dir():
                session_id = session_dir.name
                try:
                    metadata = self._load_metadata(session_id)
                    sessions.append({
                        "id": session_id,
                        "name": metadata.get("name"),
                        "created": metadata.get("created", "")
                    })
                except:
                    # If metadata can't be loaded, still include the session
                    sessions.append({
                        "id": session_id,
                        "name": None,
                        "created": ""
                    })
        
        # Sort by creation time (most recent first)
        sessions.sort(key=lambda x: x.get("created", ""), reverse=True)
        return sessions
    
    def delete_session(self, session_id: str) -> None:
        """Delete a session and all its data.
        
        Args:
            session_id: Session ID
            
        Warning:
            This permanently deletes all documents and chat history!
        """
        session_path = self.get_session_path(session_id)
        shutil.rmtree(session_path)
    
    def cleanup_old_sessions(self, max_age_days: int = 30) -> List[str]:
        """Delete sessions older than max_age_days.
        
        Args:
            max_age_days: Maximum session age in days
            
        Returns:
            List of deleted session IDs
        """
        from datetime import timedelta
        
        deleted = []
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        
        for session_id in self.list_sessions():
            metadata = self._load_metadata(session_id)
            created = datetime.fromisoformat(metadata["created"])
            
            if created < cutoff_time:
                self.delete_session(session_id)
                deleted.append(session_id)
        
        return deleted
    
    def _load_metadata(self, session_id: str) -> Dict:
        """Load session metadata file."""
        metadata_path = self.get_session_path(session_id) / "metadata.json"
        if not metadata_path.exists():
            raise ValueError(f"Metadata not found for session: {session_id}")
        
        with open(metadata_path, "r") as f:
            return json.load(f)
    
    def _save_metadata(self, session_id: str, metadata: Dict) -> None:
        """Save session metadata file."""
        metadata_path = self.get_session_path(session_id) / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
    
    def _load_chat_history(self, session_id: str) -> List[Dict]:
        """Load chat history file."""
        history_path = self.get_session_path(session_id) / "chat_history.json"
        if not history_path.exists():
            return []
        
        with open(history_path, "r") as f:
            return json.load(f)
    
    def _save_chat_history(self, session_id: str, history: List[Dict]) -> None:
        """Save chat history file."""
        history_path = self.get_session_path(session_id) / "chat_history.json"
        with open(history_path, "w") as f:
            json.dump(history, f, indent=2)
