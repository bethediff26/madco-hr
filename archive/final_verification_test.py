#!/usr/bin/env python3
"""
Final verification test that mimics what should happen in the actual system.
"""

import sys
sys.path.insert(0, 'app')

from app.prompts import AGENT_SYSTEM_PROMPT
from app.ollama_client import LLMClient

def test_system_prompt():
    """Test that our system prompt has the right content."""
    print("=== Testing System Prompt ===")
    print("System prompt contains search_policies example:", "search_policies" in AGENT_SYSTEM_PROMPT)
    print("System prompt contains tool examples:", "EXAMPLES:" in AGENT_SYSTEM_PROMPT)

    # Show first part of system prompt
    lines = AGENT_SYSTEM_PROMPT.split('\n')
    for i, line in enumerate(lines[:20]):
        if 'EXAMPLE' in line or 'tool' in line.lower() or 'search_policies' in line:
            print(f"  {i}: {line}")
    print("...")

def test_client_initialization():
    """Test that we can initialize the LLM client."""
    print("\n=== Testing LLM Client ===")
    try:
        client = LLMClient()
        print("✓ LLMClient initialized successfully")
        return True
    except Exception as e:
        print(f"✗ LLMClient failed: {e}")
        return False

def test_tool_call_parsing():
    """Test parsing of tool calls like the agent would do."""
    print("\n=== Testing Tool Call Parsing ===")

    # Test cases that should work
    test_cases = [
        '{"tool": "search_policies", "arguments": {"query": "full-time employees PTO policy"}}',
        '{"name": "search_policies", "arguments": {"query": "full-time employees PTO policy"}}'
    ]

    from app.ollama_client import LLMClient

    client = LLMClient()
    for i, case in enumerate(test_cases):
        try:
            result = client.parse_tool_call(case)
            print(f"✓ Test {i+1}: {result}")
        except Exception as e:
            print(f"✗ Test {i+1} failed: {e}")

if __name__ == "__main__":
    test_system_prompt()
    test_client_initialization()
    test_tool_call_parsing()

    print("\n=== All Tests Completed ===")