"""Answer generation components."""

from typing import Optional
from app.registry import register


@register("gen.lmstudio")
class LMStudioGenerator:
    """Generate answers using local LM Studio models."""
    
    def __init__(
        self,
        model: str = "qwen2.5-7b-instruct-1m",
        base_url: str = "http://127.0.0.1:1234",
        timeout: int = 120,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ):
        """Initialize LM Studio generator.
        
        Args:
            model: Model identifier (for reference, LM Studio uses loaded model)
            base_url: LM Studio server URL
            timeout: Request timeout in seconds
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
        """
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        try:
            import requests
            # Test connection
            self.client = None  # Will use requests directly
        except ImportError:
            raise ImportError("requests required for LM Studio generation")
    
    def generate(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate answer using LM Studio."""
        import requests
        
        if system_prompt is None:
            system_prompt = (
                "You are a helpful assistant. "
                "Use only the provided context to answer the question. "
                "If the context doesn't contain relevant information, say you don't know. "
                "Provide a clear, concise answer."
            )
        
        # Prepare messages in OpenAI format
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            }
        ]
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "stream": False
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract response from OpenAI-format response
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                return "Error: No response from LM Studio"
        
        except requests.exceptions.ConnectionError:
            return (
                f"Error: Cannot connect to LM Studio at {self.base_url}\n"
                f"Make sure LM Studio is running and the URL is correct.\n"
                f"Expected URL: http://127.0.0.1:1234"
            )
        except Exception as e:
            return f"Error generating response: {str(e)}"


@register("gen.ollama")
class OllamaGenerator:
    """Generate answers using local Ollama models."""
    
    def __init__(
        self,
        model: str = "llama3.1:8b",
        timeout: int = 120,
        base_url: str = "http://localhost:11434"
    ):
        """Initialize Ollama generator.
        
        Args:
            model: Ollama model name
            timeout: Request timeout in seconds
            base_url: Ollama server URL
        """
        self.model = model
        self.timeout = timeout
        self.base_url = base_url
        
        try:
            import requests
            # Test connection
            self.client = None  # Will lazy load on first use
        except ImportError:
            raise ImportError("requests required for Ollama generation")
    
    def generate(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate answer using Ollama."""
        import requests
        
        if system_prompt is None:
            system_prompt = (
                "You are a helpful assistant. "
                "Use only the provided context to answer the question. "
                "If the context doesn't contain relevant information, say you don't know. "
                "Provide a clear, concise answer."
            )
        
        # Prepare prompt
        prompt = f"{system_prompt}\n\n{context}\n\nQuestion: {query}\n\nAnswer:"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"


@register("gen.mock")
class MockGenerator:
    """Mock generator for testing (no external dependencies)."""
    
    def __init__(self, **kwargs):
        """Initialize mock generator."""
        pass
    
    def generate(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate a mock response."""
        return (
            f"Based on the provided context, here's an answer to '{query}':\n\n"
            f"The context contains information related to your query. "
            f"In real usage, a local LLM would generate a detailed response here."
        )

