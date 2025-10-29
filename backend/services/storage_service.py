"""Storage service for file operations."""

from pathlib import Path
from typing import BinaryIO


class StorageService:
    """Service for file storage operations.
    
    Handles basic file I/O operations for sessions.
    """
    
    @staticmethod
    def save_file(file_path: Path, content: BinaryIO) -> None:
        """Save file to disk.
        
        Args:
            file_path: Path where to save file
            content: File content (binary)
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content.read())
    
    @staticmethod
    def read_file(file_path: Path) -> bytes:
        """Read file from disk.
        
        Args:
            file_path: Path to file
        
        Returns:
            File content as bytes
        """
        with open(file_path, "rb") as f:
            return f.read()
    
    @staticmethod
    def delete_file(file_path: Path) -> None:
        """Delete file from disk.
        
        Args:
            file_path: Path to file
        """
        if file_path.exists():
            file_path.unlink()
    
    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """Get file size in bytes.
        
        Args:
            file_path: Path to file
        
        Returns:
            File size in bytes
        """
        if file_path.exists():
            return file_path.stat().st_size
        return 0
