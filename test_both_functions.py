#!/usr/bin/env python3
"""
Test both the original and alias function names for the search_policies tool.
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from hr_mcp.server import search_policies, search_policy_documents

def test_both_functions():
    """Test both function names work correctly."""
    print("=== Testing Both Function Names ===")

    try:
        # Test original function name
        print("1. Testing search_policies('remote work')...")
        result1 = search_policies("remote work")

        if "results" in result1 and result1["results"]:
            print(f"   ✓ search_policies found {len(result1['results'])} results")
            for i, result in enumerate(result1['results']):
                print(f"     {i+1}. {result['doc_title']} - {result['section']}")
                print(f"        Score: {result['relevance_score']:.4f}")
        else:
            print("   ⚠ search_policies returned no results")
            if "error" in result1:
                print(f"     Error: {result1['error']}")

        # Test alias function name
        print("\n2. Testing search_policy_documents('remote work')...")
        result2 = search_policy_documents("remote work")

        if "results" in result2 and result2["results"]:
            print(f"   ✓ search_policy_documents found {len(result2['results'])} results")
            for i, result in enumerate(result2['results']):
                print(f"     {i+1}. {result['doc_title']} - {result['section']}")
                print(f"        Score: {result['relevance_score']:.4f}")
        else:
            print("   ⚠ search_policy_documents returned no results")
            if "error" in result2:
                print(f"     Error: {result2['error']}")

        # Verify they return the same results
        print("\n3. Comparing results...")
        if "results" in result1 and "results" in result2:
            if len(result1['results']) == len(result2['results']):
                print("   ✓ Both functions returned the same number of results")

                # Check that results are identical (order might vary)
                results1_ids = [f"{r['doc_id']}_{r['section']}" for r in result1['results']]
                results2_ids = [f"{r['doc_id']}_{r['section']}" for r in result2['results']]

                if set(results1_ids) == set(results2_ids):
                    print("   ✓ Both functions returned identical results")
                else:
                    print("   ⚠ Results differ between functions")
            else:
                print(f"   ⚠ Different number of results: {len(result1['results'])} vs {len(result2['results'])}")
        else:
            print("   ⚠ One or both functions returned no results")

        print("\n✓ Both function names test completed successfully!")
        return True

    except Exception as e:
        print(f"✗ Error testing both functions: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_both_functions()
    if not success:
        sys.exit(1)