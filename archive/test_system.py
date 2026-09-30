#!/usr/bin/env python3
"""Test script for the HR MCP server to demonstrate proper usage."""

import json
from hr_mcp.server import (
    get_employee,
    get_pto_balance,
    get_benefits,
    search_policies,
    list_all_employees
)

def test_individual_tools():
    """Test that individual tools work correctly."""
    print("Testing individual tools:")
    print("=" * 50)

    # Test employee lookup
    print("\n1. Getting employee info for EMP-101:")
    result = get_employee("EMP-101")
    print(json.dumps(result, indent=2))

    # Test PTO balance
    print("\n2. Getting PTO balance for EMP-101:")
    result = get_pto_balance("EMP-101")
    print(json.dumps(result, indent=2))

    # Test benefits
    print("\n3. Getting benefits info for EMP-101:")
    result = get_benefits("EMP-101")
    print(json.dumps(result, indent=2))

    # Test policy search
    print("\n4. Searching policies:")
    result = search_policies("remote work")
    print(json.dumps(result, indent=2))

def test_combined_response():
    """Show how to create a combined response from multiple tools."""
    print("\n\nCreating combined responses:")
    print("=" * 50)

    # Simulate what a proper orchestration system would do
    employee_result = get_employee("EMP-101")
    pto_result = get_pto_balance("EMP-101")
    benefits_result = get_benefits("EMP-101")

    if (employee_result.get('status') == 'ok' and
        pto_result.get('status') == 'ok' and
        benefits_result.get('status') == 'ok'):

        combined_response = {
            "employee": employee_result['employee'],
            "pto_balance": pto_result['pto_balance'],
            "benefits": benefits_result['benefits']
        }

        print("\nCombined response for EMP-101:")
        print(json.dumps(combined_response, indent=2))
    else:
        print("One or more tool calls failed")
        print(f"Employee: {employee_result}")
        print(f"PTO: {pto_result}")
        print(f"Benefits: {benefits_result}")

if __name__ == "__main__":
    test_individual_tools()
    test_combined_response()