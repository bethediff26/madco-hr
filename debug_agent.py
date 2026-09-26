#!/usr/bin/env python3
"""
Debug script to understand why policy search isn't being triggered properly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.agent import HRAgent
from app.prompts import AGENT_SYSTEM_PROMPT

def debug_agent():
    """Debug what happens when we run the agent with your query."""

    print("Debugging HR Agent Tool Call Recognition")
    print("=" * 50)

    # Create agent instance
    agent = HRAgent()

    # Test query that should trigger policy search
    test_query = "What is the PTO policy for full-time employees?"

    print(f"Test Query: {test_query}")
    print("\nAvailable tools:")
    for tool_name, tool_func in agent.tools.items():
        doc = tool_func.__doc__ if tool_func.__doc__ else "No documentation"
        print(f"  {tool_name}: {doc}")

    print("\n" + "=" * 50)
    print("Running agent with query...")

    try:
        result = agent.run(test_query, max_iterations=2)
        print(f"\nFinal Response: {result['response']}")
        print(f"Traces: {result['traces']}")
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_agent()