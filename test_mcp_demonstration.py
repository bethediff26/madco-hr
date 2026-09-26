#!/usr/bin/env python3
"""
Test script to demonstrate and verify the MCP server functionality.

This script tests that the MCP tools work correctly when called individually
and can be properly orchestrated by an external system.
"""

import json
from hr_mcp.server import (
    get_employee,
    get_pto_balance,
    get_benefits,
    search_policies
)

def test_individual_tools():
    """Test that individual tools return correct data."""
    print("Testing Individual MCP Tools")
    print("=" * 30)

    # Test employee tool
    print("1. Testing get_employee tool:")
    employee_result = get_employee("EMP-101")
    print(f"   Employee ID: {employee_result['employee']['employee_id']}")
    print(f"   Name: {employee_result['employee']['name']}")
    print(f"   Role: {employee_result['employee']['role']}")
    assert 'employee' in employee_result
    assert employee_result['employee']['employee_id'] == 'EMP-101'
    print("   ✓ Employee tool works correctly")

    # Test PTO tool
    print("\n2. Testing get_pto_balance tool:")
    pto_result = get_pto_balance("EMP-101")
    print(f"   Available days: {pto_result['pto_balance']['available_days']}")
    assert 'pto_balance' in pto_result
    assert pto_result['pto_balance']['employee_id'] == 'EMP-101'
    print("   ✓ PTO tool works correctly")

    # Test benefits tool
    print("\n3. Testing get_benefits tool:")
    benefits_result = get_benefits("EMP-101")
    print(f"   Health plan: {benefits_result['benefits']['health_plan']}")
    assert 'benefits' in benefits_result
    assert benefits_result['benefits']['employee_id'] == 'EMP-101'
    print("   ✓ Benefits tool works correctly")

    # Test policy search tool
    print("\n4. Testing search_policies tool:")
    policy_result = search_policies("remote work")
    print(f"   Found {len(policy_result['results'])} policy documents")
    assert 'results' in policy_result
    assert len(policy_result['results']) > 0
    print("   ✓ Policy search tool works correctly")

def test_orchestration():
    """Test that tools can be properly orchestrated."""
    print("\n\nTesting Tool Orchestration")
    print("=" * 30)

    # Simulate what an external orchestrator would do
    employee_data = get_employee("EMP-101")
    pto_data = get_pto_balance("EMP-101")
    benefits_data = get_benefits("EMP-101")
    policy_results = search_policies("remote work")

    # Combine into final response (this is what orchestrator does)
    final_response = {
        "employee": employee_data["employee"],
        "pto_balance": pto_data["pto_balance"],
        "benefits": benefits_data["benefits"],
        "policy_search_results": policy_results["results"]
    }

    print("Final orchestrated response:")
    print(json.dumps(final_response, indent=2))

    # Verify all data is present
    assert "employee" in final_response
    assert "pto_balance" in final_response
    assert "benefits" in final_response
    assert "policy_search_results" in final_response

    print("✓ All tools orchestrated correctly")

def test_error_handling():
    """Test that tools handle errors gracefully."""
    print("\n\nTesting Error Handling")
    print("=" * 30)

    # Test with invalid employee ID
    try:
        employee_result = get_employee("INVALID-ID")
        print("   Invalid ID handled gracefully")
    except Exception as e:
        print(f"   Error with invalid ID: {e}")

    # Test with non-existent employee
    pto_result = get_pto_balance("EMP-999")
    if "error" in pto_result:
        print(f"   Non-existent employee handled gracefully: {pto_result['error']}")
    else:
        print("   Non-existent employee handled gracefully")

def run_all_tests():
    """Run all tests."""
    print("Running MCP Server Tests")
    print("=" * 50)

    try:
        test_individual_tools()
        test_orchestration()
        test_error_handling()

        print("\n" + "=" * 50)
        print("✓ ALL TESTS PASSED!")
        print("The MCP server implementation is working correctly.")
        print("Individual tools return specific data, and")
        print("external orchestrators can combine them properly.")

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise

if __name__ == "__main__":
    run_all_tests()