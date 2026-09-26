#!/usr/bin/env python3
"""
Demonstration of how an external orchestrator would use the MCP server tools.

This shows the proper way to use MCP tools:
1. Individual tools are called separately
2. An external orchestrator combines the results into a final response
3. Each tool returns only its specific data, not combined responses
"""

import json
from hr_mcp.server import (
    get_employee,
    get_pto_balance,
    get_benefits,
    search_policies
)

def demo_orchestration():
    """Demonstrate how an external orchestrator would use the MCP tools."""

    print("MCP Tool Orchestration Demo")
    print("=" * 40)
    print("This shows how external systems would properly use MCP tools")
    print()

    # Simulate what an external orchestrator does
    print("Step 1: Get employee information")
    employee_data = get_employee("EMP-101")
    print(f"Employee data retrieved: {employee_data['employee']['name']}")

    print("\nStep 2: Get PTO balance")
    pto_data = get_pto_balance("EMP-101")
    print(f"PTO available: {pto_data['pto_balance']['available_days']} days")

    print("\nStep 3: Get benefits information")
    benefits_data = get_benefits("EMP-101")
    print(f"Benefits: Health plan {benefits_data['benefits']['health_plan']}")

    print("\nStep 4: Search policies")
    policy_results = search_policies("remote work")
    print(f"Found {len(policy_results['results'])} policy documents")

    print("\nStep 5: Combine all data into final response (orchestrator's job)")

    # The orchestrator combines all the individual tool results
    final_response = {
        "employee": employee_data["employee"],
        "pto_balance": pto_data["pto_balance"],
        "benefits": benefits_data["benefits"],
        "policy_search_results": policy_results["results"],
        "summary": f"Employee {employee_data['employee']['name']} has {pto_data['pto_balance']['available_days']} PTO days available and is enrolled in {benefits_data['benefits']['health_plan']} health plan."
    }

    print(json.dumps(final_response, indent=2))
    print()
    print("This demonstrates the correct MCP pattern:")
    print("- Tools are called individually by external systems")
    print("- Each tool returns only its specific data")
    print("- The orchestrator combines results into a meaningful response")
    print("- This is how MCP servers should be designed and used")

if __name__ == "__main__":
    demo_orchestration()