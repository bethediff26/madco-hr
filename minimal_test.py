#!/usr/bin/env python3
"""
Minimal test to verify tool calling logic works without complex dependencies.
"""

import json

# Test the parsing function directly
def test_tool_call_parsing():
    """Test that we can parse tool calls correctly."""

    # This is what a typical LLM response might look like
    test_responses = [
        '{"tool": "search_policies", "arguments": {"query": "full-time employees PTO policy"}}',
        '{"name": "search_policies", "arguments": {"query": "full-time employees PTO policy"}}',
        '```json\n{"tool": "search_policies", "arguments": {"query": "full-time employees PTO policy"}}\n```',
        '{"tool": "get_pto_balance", "arguments": {"employee_id": "EMP-101"}}'
    ]

    print("Testing tool call parsing logic...")

    for i, response in enumerate(test_responses):
        try:
            # This simulates the parsing logic from ollama_client.py
            if response.strip().startswith('```json'):
                # Extract JSON from markdown code block
                lines = response.strip().split('\n')
                json_str = '\n'.join(lines[1:-1])  # Remove first and last lines
            else:
                json_str = response

            parsed = json.loads(json_str)
            print(f"Test {i+1}: ✓ Parsed successfully - {parsed}")

        except Exception as e:
            print(f"Test {i+1}: ✗ Failed - {e}")

    print("\nParsing tests completed!")

if __name__ == "__main__":
    test_tool_call_parsing()