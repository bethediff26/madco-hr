#!/usr/bin/env python3
"""
Direct test of the search_policies tool from hr_mcp/server.py
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from hr_mcp.server import search_policies

def test_search_policies_tool():
    """Test the search_policies MCP tool directly."""
    print("=== Testing search_policies MCP tool ===")

    try:
        # Test with a sample query like 'remote work'
        print("1. Testing search_policies('remote work')...")
        results = search_policies("remote work")

        if "results" in results and results["results"]:
            print(f"   ✓ Found {len(results['results'])} results")
            for i, result in enumerate(results['results']):
                print(f"     {i+1}. {result['doc_title']} - {result['section']}")
                print(f"        Score: {result['relevance_score']:.4f}")
                # Show first 100 characters of snippet
                snippet = result['snippet'][:100] + "..." if len(result['snippet']) > 100 else result['snippet']
                print(f"        Snippet: {snippet}")
        else:
            print("   ⚠ No results found")
            if "error" in results:
                print(f"     Error: {results['error']}")

        # Test with another query
        print("\n2. Testing search_policies('pto policy')...")
        results2 = search_policies("pto policy")

        if "results" in results2 and results2["results"]:
            print(f"   ✓ Found {len(results2['results'])} results")
            for i, result in enumerate(results2['results']):
                print(f"     {i+1}. {result['doc_title']} - {result['section']}")
                print(f"        Score: {result['relevance_score']:.4f}")
        else:
            print("   ⚠ No results found")
            if "error" in results2:
                print(f"     Error: {results2['error']}")

        print("\n✓ search_policies tool test completed successfully!")
        return True

    except Exception as e:
        print(f"✗ Error testing search_policies tool: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_search_policies_tool()
    if not success:
        sys.exit(1)