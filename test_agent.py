#!/usr/bin/env python3
"""Test script to verify the HRAgent is working correctly."""

from app.agent import HRAgent

def test_pto_policy_query():
    """Test the agent with a PTO policy question."""
    agent = HRAgent()

    query = "What is the PTO policy for full-time employees?"

    print("=" * 60)
    print(f"Query: {query}")
    print("=" * 60)

    try:
        result = agent.run(user_query=query, max_iterations=3)

        response = result.get("response", "")
        traces = result.get("traces", [])

        print("\n--- Response ---")
        print(response[:500] if response else "No response generated")
        print("\n" + "=" * 60)
        print("--- Traces ---")
        for i, trace in enumerate(traces, 1):
            print(f"\nStep {i}: {trace.get('type', 'unknown')}")
            if trace.get("tool"):
                print(f"  Tool: {trace['tool']}")
                print(f"  Args: {trace.get('args', {})}")
            else:
                print(f"  Content: {trace.get('content', 'N/A')[:200]}")

        iterations = result.get("iterations_completed", 0)
        print("\n" + "=" * 60)
        print(f"Iterations completed: {iterations}")
        print("=" * 60)

    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pto_policy_query()
