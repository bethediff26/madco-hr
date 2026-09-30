#!/usr/bin/env python3
"""
Simple test to debug the exact issue with policy search queries.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.ollama_client import LLMClient

def test_parsing():
    """Test the parsing logic directly."""

    client = LLMClient()

    # Test cases that should be parsed properly
    test_cases = [
        '{"tool": "search_policies", "arguments": {"query": "full-time employees PTO policy"}}',
        '{"name": "search_policies", "arguments": {"query": "full-time employees PTO policy"}}',
        'Provide employee ID or query.',
        '{"tool": "get_pto_balance", "arguments": {"employee_id": "EMP-101"}}'
    ]

    print("Testing parsing logic:")
    print("=" * 40)

    for i, case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {case}")
        result = client.parse_tool_call(case)
        print(f"Parsed: {result}")

if __name__ == "__main__":
    test_parsing()