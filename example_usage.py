#!/usr/bin/env python3
"""Example usage of the Local Modular RAG Pipeline."""

import os
from app.pipeline import RAGPipeline


def example_basic_usage():
    """Basic RAG pipeline usage."""
    print("=" * 60)
    print("🧠 RAG Pipeline - Basic Example")
    print("=" * 60)
    
    # Create pipeline with default config
    pipeline = RAGPipeline("app/configs/default.yaml")
    
    # Show configuration
    print("\n📊 Pipeline Components:")
    components = {
        "Loader": pipeline.config["loader"]["component"],
        "Chunker": pipeline.config["chunker"]["component"],
        "Embedder": pipeline.config["embedder"]["component"],
        "Vector Store": pipeline.config["store"]["component"],
        "Retriever": pipeline.config["retriever"]["component"],
        "Reranker": pipeline.config["reranker"]["component"],
        "Compressor": pipeline.config["compressor"]["component"],
        "Generator": pipeline.config["generator"]["component"],
    }
    for name, component in components.items():
        print(f"  • {name}: {component}")
    
    # Note about indexing
    print("\n📝 Note: To use this pipeline, you need to:")
    print("  1. Add documents to the 'data/' directory")
    print("  2. Call pipeline.index(clear_existing=True)")
    print("  3. Call pipeline.query('Your question')")
    print("\n  Or run: python -m app.pipeline")


def example_with_mock_generator():
    """Example using mock generator (no Ollama needed)."""
    print("\n" + "=" * 60)
    print("🚀 Example with Mock Generator (No LLM Required)")
    print("=" * 60)
    
    # Use fast config which uses mock generator
    pipeline = RAGPipeline("app/configs/fast.yaml")
    
    print("\n✅ Pipeline created with mock generator")
    print("   (No Ollama installation needed for this config)")
    
    # Create sample data directory if needed
    if not os.path.exists("data"):
        print("\n📂 Creating data/ directory...")
        os.makedirs("data", exist_ok=True)
        
        # Create a sample document
        sample_doc = """
        # RAG Pipeline Documentation
        
        This is a modular RAG (Retrieval-Augmented Generation) pipeline.
        
        ## Key Features
        
        - Fully local and offline
        - Modular component architecture
        - Hybrid retrieval with RRF fusion
        - Cross-encoder reranking
        - Context compression
        
        ## Components
        
        The pipeline consists of several stages:
        1. Loader: Loads documents from disk
        2. Chunker: Splits documents into chunks
        3. Embedder: Generates embeddings
        4. Vector Store: Stores embeddings persistently
        5. Retriever: Retrieves relevant chunks
        6. Reranker: Ranks chunks by relevance
        7. Compressor: Compresses context
        8. Generator: Generates answers using LLM
        
        ## Usage
        
        python -m app.pipeline --index --query "Your question"
        """
        
        with open("data/README.md", "w") as f:
            f.write(sample_doc)
        print("   ✓ Created sample document: data/README.md")
    
    # Index documents
    print("\n📚 Indexing documents...")
    try:
        num_chunks = pipeline.index(clear_existing=True)
        print(f"   ✓ Indexed {num_chunks} chunks")
        
        # Query example
        query = "What are the key features of this pipeline?"
        print(f"\n❓ Query: {query}")
        
        result = pipeline.query(query)
        print(f"\n📚 Answer:\n{result.answer}")
        
        if result.source_citations:
            print(f"\n📖 Sources: {', '.join(result.source_citations)}")
    
    except Exception as e:
        print(f"   ⚠️  Error during indexing/query: {e}")
        print("   This is expected if Ollama is not running")


def example_programmatic_usage():
    """Programmatic usage example."""
    print("\n" + "=" * 60)
    print("💻 Programmatic Usage Example")
    print("=" * 60)
    
    print("""
# Create pipeline
from app.pipeline import RAGPipeline

pipeline = RAGPipeline("app/configs/default.yaml")

# Index documents
pipeline.index(clear_existing=True)

# Query
result = pipeline.query("What is this about?")
print(result.answer)
print(result.source_citations)
    """)


def example_config_swapping():
    """Example of swapping components via config."""
    print("\n" + "=" * 60)
    print("🔄 Component Swapping Examples")
    print("=" * 60)
    
    examples = [
        {
            "title": "Use MiniLM (lighter embeddings)",
            "config": "embedder.args.model_name: sentence-transformers/all-MiniLM-L6-v2"
        },
        {
            "title": "Disable reranking (faster)",
            "config": "reranker.component: rerank.noop"
        },
        {
            "title": "Use BM25-only retrieval",
            "config": "retriever.component: retriever.bm25"
        },
        {
            "title": "Use Mistral LLM",
            "config": "generator.args.model: mistral"
        },
        {
            "title": "Increase context budget",
            "config": "compressor.args.token_budget: 12000"
        },
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}")
        print(f"   Config: {example['config']}")


if __name__ == "__main__":
    example_basic_usage()
    example_with_mock_generator()
    example_programmatic_usage()
    example_config_swapping()
    
    print("\n" + "=" * 60)
    print("✅ For more help, run: python -m app.pipeline --help")
    print("=" * 60)
