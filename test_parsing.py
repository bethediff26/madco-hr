#!/usr/bin/env python3
"""
Test parsing functionality without making LLM API calls.
"""

import sys
import os
import json

# Add the app directory to the Python path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.ollama_client import LLMClient

def test_parsing():
    """Test parsing of tool calls."""

    client = LLMClient()

    # Test cases for parsing
    test_cases = [
        '{"tool": "get_pto_balance", "arguments": {"employee_id": "EMP-101"}}',
        '```json\n{"tool": "get_employee", "arguments": {"employee_id": "EMP-101"}}\n```',
        'Some text before {"tool": "search_policies", "arguments": {"query": "remote work"}} some text after',
        'Hello, this is a conversation, not a tool call.',
        '{"name": "get_benefits", "arguments": {"employee_id": "EMP-101"}}',  # Alternative format
        '```{"tool": "get_pto_balance", "arguments": {"employee_id": "EMP-101"}}```',
    ]

    print("Testing parsing of tool calls:")
    print("=" * 50)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Input: {test_case}")
        result = client.parse_tool_call(test_case)
        print(f"Parsed result: {result}")

        if result is None:
            print("❌ No valid tool call found")
        else:
            print("✅ Valid tool call parsed")

if __name__ == "__main__":
    test_parsing()