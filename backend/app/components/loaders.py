"""Document loaders for various file formats."""

import os
import glob
from pathlib import Path
from typing import List, Dict, Any
from app.interfaces import Document
from app.registry import register


@register("load.fs")
class FSLoader:
    """Load documents from filesystem (PDF, HTML, TXT, MD)."""
    
    SUPPORTED_FORMATS = {".pdf", ".html", ".txt", ".md"}
    
    def __init__(self, data_dir: str = "data"):
        """Initialize filesystem loader."""
        self.data_dir = data_dir
    
    def load(self) -> List[Document]:
        """Load all supported files from data directory."""
        documents = []
        
        if not os.path.exists(self.data_dir):
            return documents
        
        for ext in self.SUPPORTED_FORMATS:
            pattern = os.path.join(self.data_dir, f"**/*{ext}")
            for filepath in glob.glob(pattern, recursive=True):
                try:
                    if ext == ".pdf":
                        docs = self._load_pdf(filepath)
                    elif ext == ".html":
                        docs = self._load_html(filepath)
                    else:  # .txt, .md
                        docs = self._load_text(filepath)
                    documents.extend(docs)
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")
        
        return documents
    
    @staticmethod
    def _load_pdf(filepath: str) -> List[Document]:
        """Load PDF file."""
        try:
            import pdfplumber
            documents = []
            with pdfplumber.open(filepath) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        documents.append(
                            Document(
                                content=text,
                                metadata={
                                    "source": filepath,
                                    "page": page_num + 1,
                                    "file_type": "pdf"
                                }
                            )
                        )
            return documents
        except ImportError:
            raise ImportError("pdfplumber required for PDF loading")
    
    @staticmethod
    def _load_html(filepath: str) -> List[Document]:
        """Load HTML file."""
        try:
            from bs4 import BeautifulSoup
            with open(filepath, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text(separator="\n")
                # Clean whitespace
                lines = (line.strip() for line in text.splitlines())
                text = "\n".join(line for line in lines if line)
                
                return [
                    Document(
                        content=text,
                        metadata={
                            "source": filepath,
                            "file_type": "html"
                        }
                    )
                ]
        except ImportError:
            raise ImportError("beautifulsoup4 required for HTML loading")
    
    @staticmethod
    def _load_text(filepath: str) -> List[Document]:
        """Load TXT or MD file."""
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
            file_type = "md" if filepath.endswith(".md") else "txt"
            return [
                Document(
                    content=text,
                    metadata={
                        "source": filepath,
                        "file_type": file_type
                    }
                )
            ]
