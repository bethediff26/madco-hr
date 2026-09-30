#!/usr/bin/env python3
"""
Direct test of individual tools to verify they work.
"""

import sys
sys.path.insert(0, 'app')

def test_tools():
    """Test that individual tools can be imported and called."""

    print("Testing individual tool imports...")

    try:
        # Test importing the search_policies tool specifically
        from app.mcp_tools import search_policies
        print("✓ search_policies tool imported successfully")

        # Test calling it with a simple query
        result = search_policies(query="full-time employees PTO policy")
        print(f"✓ search_policies executed successfully, got: {type(result)}")
        if isinstance(result, dict):
            print(f"  Result keys: {list(result.keys())}")

    except Exception as e:
        print(f"✗ Error with search_policies: {e}")
        import traceback
        traceback.print_exc()

    try:
        # Test importing get_pto_balance tool
        from app.mcp_tools import get_pto_balance
        print("✓ get_pto_balance tool imported successfully")

        # Test calling it (this will likely fail due to mock data, but we just want to see if it loads)
        result = get_pto_balance(employee_id="EMP-101")
        print(f"✓ get_pto_balance executed successfully, got: {type(result)}")

    except Exception as e:
        print(f"✗ Error with get_pto_balance: {e}")
        # This might fail due to missing mock data, which is expected

if __name__ == "__main__":
    test_tools()