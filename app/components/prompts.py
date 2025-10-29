"""Prompt templates for RAG."""


class PromptTemplates:
    """Collection of prompt templates."""
    
    DEFAULT_SYSTEM = """You are a helpful, knowledgeable assistant.
You answer questions based on the provided context.
If the context doesn't contain relevant information, say you don't know.
Provide clear, concise, and accurate answers.
Always cite your sources when possible."""
    
    QA_SYSTEM = """You are an expert question-answering assistant.
Answer the user's question based strictly on the provided context.
If the answer cannot be found in the context, respond with "I don't have enough information to answer this question."
Structure your answer clearly with supporting evidence from the context."""
    
    SUMMARIZATION_SYSTEM = """You are a document summarization expert.
Summarize the provided context in a clear, concise manner.
Highlight the key points and main ideas.
Maintain factual accuracy and avoid adding information not in the context."""
    
    EXTRACTION_SYSTEM = """You are an information extraction specialist.
Extract relevant information from the context that answers the user's query.
Present the information in a structured format.
Only include information that is explicitly stated in the context."""
    
    @staticmethod
    def get_qa_prompt(context: str, query: str) -> str:
        """Generate a QA prompt."""
        return f"""{PromptTemplates.QA_SYSTEM}

Context:
{context}

Question: {query}

Answer:"""
    
    @staticmethod
    def get_summarization_prompt(context: str) -> str:
        """Generate a summarization prompt."""
        return f"""{PromptTemplates.SUMMARIZATION_SYSTEM}

Content to summarize:
{context}

Summary:"""
    
    @staticmethod
    def get_extraction_prompt(context: str, query: str) -> str:
        """Generate an extraction prompt."""
        return f"""{PromptTemplates.EXTRACTION_SYSTEM}

Context:
{context}

Query: {query}

Extracted Information:"""
    
    @staticmethod
    def get_custom_prompt(
        system_prompt: str,
        context: str,
        query: str
    ) -> str:
        """Generate a custom prompt."""
        return f"""{system_prompt}

Context:
{context}

Question: {query}

Answer:"""
