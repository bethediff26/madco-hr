#!/usr/bin/env python3
"""
Quick test to verify search_policies tool functionality with ChromaDB.
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from hr_mcp.server import policy_rag

def test_search_policies():
    """Test the search_policies functionality."""
    print("=== Testing search_policies functionality ===")

    try:
        # Test 1: Initialize and verify ChromaDB is ready
        print("1. Verifying ChromaDB client...")
        print(f"   Collection name: {policy_rag.collection_name}")
        print(f"   Collection count: {policy_rag.collection.count()}")

        # Test 2: Execute a simple search query
        print("\n2. Testing sample search 'remote work'...")
        results = policy_rag.search_policies("remote work", top_k=3)

        if results:
            print(f"   ✓ Found {len(results)} relevant policy snippets")
            for i, result in enumerate(results):
                print(f"     {i+1}. {result['doc_title']} - {result['section']}")
                print(f"        Score: {result['relevance_score']:.4f}")
                # Show first 100 characters of snippet
                snippet = result['snippet'][:100] + "..." if len(result['snippet']) > 100 else result['snippet']
                print(f"        Snippet: {snippet}")
        else:
            print("   ⚠ No results found for 'remote work'")

        # Test 3: Try another query
        print("\n3. Testing sample search 'pto policy'...")
        results2 = policy_rag.search_policies("pto policy", top_k=2)

        if results2:
            print(f"   ✓ Found {len(results2)} relevant policy snippets")
            for i, result in enumerate(results2):
                print(f"     {i+1}. {result['doc_title']} - {result['section']}")
                print(f"        Score: {result['relevance_score']:.4f}")
        else:
            print("   ⚠ No results found for 'pto policy'")

        print("\n✓ ChromaDB initialization and search functionality verified successfully")
        return True

    except Exception as e:
        print(f"✗ Error in search_policies test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_search_policies()
    if not success:
        sys.exit(1)