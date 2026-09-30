#!/usr/bin/env python3
"""
Simple direct test of the HR agent functionality without server overhead.
"""

import sys
import os
sys.path.insert(0, 'app')

# Test the core functionality directly
from app.agent import HRAgent

def test_policy_search():
    """Test policy search functionality directly."""
    print("Testing policy search functionality...")

    try:
        # Create agent instance
        agent = HRAgent()
        print("Agent created successfully")

        # Test query that should trigger policy search
        query = "What is the PTO policy for full-time employees?"
        print(f"Running query: {query}")

        result = agent.run(query, max_iterations=2)
        print("Result:", result)

        return True

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_policy_search()
    if success:
        print("✓ Policy search test PASSED")
    else:
        print("✗ Policy search test FAILED")