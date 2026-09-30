#!/usr/bin/env python3
"""
Test script to reproduce the HR agent conversational filler issue.
"""

import sys
import os

# Add the app directory to the Python path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.agent import HRAgent

def test_agent_behavior():
    """Test the agent's behavior with different queries."""

    # Initialize the agent
    agent = HRAgent()

    # Test cases that should trigger tool calls
    test_queries = [
        "What is the PTO balance for employee EMP-101?",
        "Show me benefits information for employee EMP-101",
        "Search for policies about remote work",
        "Get employee details for EMP-101"
    ]

    print("Testing HR Agent behavior:")
    print("=" * 50)

    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: '{query}'")
        print("-" * 30)

        try:
            result = agent.run(query)
            print(f"Response: {result['response']}")
            print(f"Traces: {result['traces']}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_agent_behavior()