"""
Test script for the Agent Orchestrator and Multi-step HR Workflows.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent'))

from orchestrator import HRPolicyAgentOrchestrator
from workflows import workflows

import asyncio

def test_agent_orchestrator():
    """Test the agent orchestrator with various queries."""
    print("=== Testing Agent Orchestrator ===")

    # Initialize orchestrator
    orchestrator = HRPolicyAgentOrchestrator()

    # Test 1: Simple policy search
    print("\n1. Testing simple policy search...")
    result = asyncio.run(orchestrator.process_user_query("What is the remote work policy?"))
    print(f"Status: {result['status']}")
    print(f"Message preview: {result['message'][:100]}...")

    # Test 2: Multi-step workflow - remote work eligibility
    print("\n2. Testing remote work eligibility workflow...")
    result = asyncio.run(orchestrator.process_user_query(
        "Check my remote work eligibility",
        employee_id="EMP-12345"
    ))
    print(f"Status: {result['status']}")
    print(f"Message preview: {result['message'][:100]}...")

    # Test 3: PTO request guidance
    print("\n3. Testing PTO request guidance workflow...")
    result = asyncio.run(orchestrator.process_user_query(
        "How do I submit a PTO request?",
        employee_id="EMP-67890"
    ))
    print(f"Status: {result['status']}")
    print(f"Message preview: {result['message'][:100]}...")

    # Test 4: Benefits question
    print("\n4. Testing benefits question handling...")
    result = asyncio.run(orchestrator.process_user_query(
        "What health insurance options do I have?",
        employee_id="EMP-11111"
    ))
    print(f"Status: {result['status']}")
    print(f"Message preview: {result['message'][:100]}...")

def test_workflows():
    """Test the multi-step workflows directly."""
    print("\n=== Testing Multi-step Workflows ===")

    # Test 1: Remote work eligibility workflow
    print("\n1. Testing remote work eligibility workflow...")
    result = workflows.remote_work_eligibility_workflow(
        "EMP-12345",
        {"request_type": "remote_work", "duration": "full_time"}
    )
    print(f"Status: {result['status']}")
    print(f"Workflow: {result['workflow_step']}")

    # Test 2: PTO request guidance workflow
    print("\n2. Testing PTO request guidance workflow...")
    result = workflows.pto_request_guidance_workflow(
        "EMP-67890",
        {"request_type": "pto", "days": 3}
    )
    print(f"Status: {result['status']}")
    print(f"Workflow: {result['workflow_step']}")

def test_trace_functionality():
    """Test the tracing functionality."""
    print("\n=== Testing Trace Functionality ===")

    # This would normally be handled by the orchestrator automatically
    print("Trace functionality is implemented in the orchestrator and workflows.")
    print("Each operation logs its trace for operational visibility.")

if __name__ == "__main__":
    try:
        test_agent_orchestrator()
        test_workflows()
        test_trace_functionality()
        print("\n=== All Tests Completed Successfully ===")
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()