"""Main RAG pipeline orchestration."""

import os
import yaml
from typing import Optional, Dict, Any
from app.registry import Registry
from app.interfaces import Document, QueryResult

# Import all components to register them
from app.components import loaders, chunkers, embedders, stores, retrievers, rerankers, compressors, generators


class RAGPipeline:
    """Modular RAG pipeline orchestrator."""
    
    def __init__(self, config_path: str = "app/configs/default.yaml"):
        """Initialize pipeline from config.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self._initialize_components()
    
    @staticmethod
    def _load_config(config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config not found: {config_path}")
        
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    
    def _initialize_components(self):
        """Initialize all pipeline components from config."""
        # Loader
        loader_cfg = self.config.get("loader", {})
        self.loader = Registry.create(
            loader_cfg.get("component", "load.fs"),
            **loader_cfg.get("args", {})
        )
        
        # Chunker
        chunker_cfg = self.config.get("chunker", {})
        self.chunker = Registry.create(
            chunker_cfg.get("component", "chunk.sentence"),
            **chunker_cfg.get("args", {})
        )
        
        # Embedder
        embedder_cfg = self.config.get("embedder", {})
        self.embedder = Registry.create(
            embedder_cfg.get("component", "embed.hf"),
            **embedder_cfg.get("args", {})
        )
        
        # Vector Store
        store_cfg = self.config.get("store", {})
        self.vector_store = Registry.create(
            store_cfg.get("component", "store.chroma"),
            **store_cfg.get("args", {})
        )
        
        # Retriever (needs embedder and vector store)
        retriever_cfg = self.config.get("retriever", {})
        retriever_args = retriever_cfg.get("args", {}).copy()
        retriever_args["embedder"] = self.embedder
        retriever_args["vector_store"] = self.vector_store
        
        self.retriever = Registry.create(
            retriever_cfg.get("component", "retriever.hybrid"),
            **retriever_args
        )
        
        # Reranker
        reranker_cfg = self.config.get("reranker", {})
        self.reranker = Registry.create(
            reranker_cfg.get("component", "rerank.bge"),
            **reranker_cfg.get("args", {})
        )
        
        # Compressor
        compressor_cfg = self.config.get("compressor", {})
        self.compressor = Registry.create(
            compressor_cfg.get("component", "compress.sentences"),
            **compressor_cfg.get("args", {})
        )
        
        # Generator
        generator_cfg = self.config.get("generator", {})
        self.generator = Registry.create(
            generator_cfg.get("component", "gen.mock"),
            **generator_cfg.get("args", {})
        )
        
        # System prompt
        prompt_cfg = self.config.get("prompt", {})
        self.system_prompt = prompt_cfg.get("system", "")
        
        # Pipeline state
        self.documents = []
        self.is_indexed = False
    
    def index(self, clear_existing: bool = False) -> int:
        """Index documents into vector store.
        
        Args:
            clear_existing: Clear existing index before indexing
        
        Returns:
            Number of documents indexed
        """
        if clear_existing:
            self.vector_store.clear()
        
        # Load documents
        print("📂 Loading documents...")
        self.documents = self.loader.load()
        print(f"  ✓ Loaded {len(self.documents)} documents")
        
        if not self.documents:
            print("  ⚠️  No documents found to index")
            return 0
        
        # Chunk documents
        print("✂️  Chunking documents...")
        chunks = self.chunker.chunk(self.documents)
        print(f"  ✓ Created {len(chunks)} chunks")
        
        # Generate embeddings
        print("🔢 Generating embeddings...")
        chunk_contents = [chunk.content for chunk in chunks]
        embeddings = self.embedder.embed_batch(chunk_contents)
        print(f"  ✓ Generated {len(embeddings)} embeddings")
        
        # Store embeddings
        print("💾 Storing in vector database...")
        self.vector_store.add(chunks, embeddings)
        print(f"  ✓ Stored {len(chunks)} chunks")
        
        # Update retriever with documents
        if hasattr(self.retriever, "update_documents"):
            self.retriever.update_documents(chunks)
        
        self.is_indexed = True
        return len(chunks)
    
    def query(self, query_text: str) -> QueryResult:
        """Run a query through the pipeline.
        
        Args:
            query_text: User query
        
        Returns:
            QueryResult with answer and context
        """
        if not self.is_indexed:
            raise RuntimeError("Pipeline not indexed. Call index() first.")
        
        print(f"\n❓ Query: {query_text}")
        
        # Retrieve relevant documents
        print("🔍 Retrieving documents...")
        retrieved = self.retriever.retrieve(query_text)
        retrieved_docs = [doc for doc, _ in retrieved]
        print(f"  ✓ Retrieved {len(retrieved_docs)} documents")
        
        # Rerank documents
        print("🔄 Reranking documents...")
        reranked = self.reranker.rerank(query_text, retrieved_docs)
        reranked_docs = [doc for doc, _ in reranked]
        print(f"  ✓ Reranked to {len(reranked_docs)} documents")
        
        # Compress context
        print("📦 Compressing context...")
        context = self.compressor.compress(reranked_docs, query_text)
        print(f"  ✓ Compressed context ({len(context)} chars)")
        
        # Generate answer
        print("✍️  Generating answer...")
        answer = self.generator.generate(
            query_text,
            context,
            system_prompt=self.system_prompt
        )
        print(f"  ✓ Generated answer")
        
        # Extract source citations
        sources = list(set(
            doc.metadata.get("source", "unknown") for doc in reranked_docs
        ))
        
        return QueryResult(
            answer=answer,
            context=reranked_docs,
            source_citations=sources
        )
    
    def interactive_mode(self):
        """Run pipeline in interactive mode."""
        print("\n🧠 RAG Pipeline - Interactive Mode")
        print("=" * 50)
        print("Commands:")
        print("  'index' - Build/rebuild the index")
        print("  'info' - Show pipeline info")
        print("  'exit' - Exit")
        print("  Or ask a question to query the knowledge base")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\nQ> ").strip()
                
                if not user_input:
                    continue
                elif user_input.lower() == "exit":
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == "index":
                    num_chunks = self.index(clear_existing=True)
                    print(f"\n✅ Indexed {num_chunks} chunks")
                elif user_input.lower() == "info":
                    self._print_info()
                else:
                    result = self.query(user_input)
                    print(f"\n📚 Answer:\n{result.answer}")
                    if result.source_citations:
                        print(f"\n📖 Sources: {', '.join(result.source_citations)}")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def _print_info(self):
        """Print pipeline information."""
        print("\n📊 Pipeline Configuration:")
        print(f"  Loader: {self.config['loader']['component']}")
        print(f"  Chunker: {self.config['chunker']['component']}")
        print(f"  Embedder: {self.config['embedder']['component']}")
        print(f"  Vector Store: {self.config['store']['component']}")
        print(f"  Retriever: {self.config['retriever']['component']}")
        print(f"  Reranker: {self.config['reranker']['component']}")
        print(f"  Compressor: {self.config['compressor']['component']}")
        print(f"  Generator: {self.config['generator']['component']}")
        
        if self.is_indexed:
            print(f"\n  Indexed Documents: {len(self.documents)}")
            print(f"  Store Size: {self.vector_store.get_count() if hasattr(self.vector_store, 'get_count') else 'N/A'}")
        else:
            print("\n  ⚠️  Not indexed yet")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Local Modular RAG Pipeline")
    parser.add_argument(
        "--config",
        default="app/configs/default.yaml",
        help="Path to config file"
    )
    parser.add_argument(
        "--index",
        action="store_true",
        help="Index documents on startup"
    )
    parser.add_argument(
        "--query",
        help="Run a single query and exit"
    )
    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = RAGPipeline(config_path=args.config)
    
    # Index if requested
    if args.index:
        print("Building index...")
        pipeline.index(clear_existing=True)
    
    # Query if provided
    if args.query:
        result = pipeline.query(args.query)
        print(f"\nAnswer:\n{result.answer}")
        if result.source_citations:
            print(f"\nSources: {', '.join(result.source_citations)}")
    else:
        # Interactive mode
        pipeline.interactive_mode()


if __name__ == "__main__":
    main()
