#!/usr/bin/env python3
"""Simple test script to query LM Studio directly."""

import sys
from app.components.generators import LMStudioGenerator


def main():
    """Test LM Studio connection and generation."""
    print("=" * 70)
    print("🧪 LM Studio Connection Test")
    print("=" * 70)
    
    # Initialize generator
    print("\n📍 Initializing LM Studio generator...")
    try:
        gen = LMStudioGenerator(
            model="qwen2.5-7b-instruct-1m",
            base_url="http://127.0.0.1:1234",
            timeout=120
        )
        print(f"   ✅ Generator initialized")
        print(f"   • Model: {gen.model}")
        print(f"   • URL: {gen.base_url}")
        print(f"   • Max tokens: {gen.max_tokens}")
        print(f"   • Temperature: {gen.temperature}")
    except Exception as e:
        print(f"   ❌ Error initializing generator: {e}")
        sys.exit(1)
    
    # Prepare test query
    print("\n📝 Preparing test query...")
    query = "What is Python programming?"
    context = """
    Python is a high-level, interpreted programming language known for its simplicity and readability.
    Created by Guido van Rossum, Python emphasizes code readability and allows developers to express 
    concepts in fewer lines of code than would be possible in languages such as C++ or Java.
    It supports multiple programming paradigms including procedural, object-oriented, and functional programming.
    Python is widely used in web development, data science, artificial intelligence, automation, and more.
    """
    
    print(f"   • Query: {query}")
    print(f"   • Context: {len(context)} characters")
    
    # Generate response
    print("\n🔄 Querying LM Studio...")
    print("   (This may take 10-30 seconds on CPU)...\n")
    
    try:
        answer = gen.generate(
            query=query,
            context=context,
            system_prompt="You are a helpful assistant. Answer based on the context provided."
        )
        
        print("=" * 70)
        print("✅ SUCCESS! LM Studio is working!\n")
        print("📚 RESPONSE:")
        print("-" * 70)
        print(answer)
        print("-" * 70)
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error generating response: {e}")
        print("\nTroubleshooting:")
        print("  • Is LM Studio running? (check Local Server tab)")
        print("  • Is the model loaded? (qwen2.5-7b-instruct-1m)")
        print("  • Is the server at http://127.0.0.1:1234?")
        sys.exit(1)


if __name__ == "__main__":
    main()
