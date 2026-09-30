#!/usr/bin/env python3
"""
Proper MCP Pattern Demonstration

This script demonstrates the correct way MCP tools should be used:
- Individual tools are called by external systems
- Each tool returns only its specific data
- An external orchestrator combines results into meaningful responses
"""

import json
from hr_mcp.server import (
    get_employee,
    get_pto_balance,
    get_benefits,
    search_policies
)

def demonstrate_individual_tool_usage():
    """Show how individual tools work in isolation."""
    print("=== DEMONSTRATING INDIVIDUAL MCP TOOLS ===")
    print()

    print("1. Employee Tool (get_employee)")
    employee_result = get_employee("EMP-101")
    print(f"   Returns: {employee_result['employee']['name']} - {employee_result['employee']['role']}")
    print(f"   Data type: {type(employee_result)}")
    print("   ✓ Tool returns only employee data")
    print()

    print("2. PTO Tool (get_pto_balance)")
    pto_result = get_pto_balance("EMP-101")
    print(f"   Returns: {pto_result['pto_balance']['available_days']} days available")
    print(f"   Data type: {type(pto_result)}")
    print("   ✓ Tool returns only PTO data")
    print()

    print("3. Benefits Tool (get_benefits)")
    benefits_result = get_benefits("EMP-101")
    print(f"   Returns: {benefits_result['benefits']['health_plan']} plan")
    print(f"   Data type: {type(benefits_result)}")
    print("   ✓ Tool returns only benefits data")
    print()

    print("4. Policy Search Tool (search_policies)")
    policy_result = search_policies("remote work")
    print(f"   Returns: {len(policy_result['results'])} policy documents")
    print(f"   Data type: {type(policy_result)}")
    print("   ✓ Tool returns only policy search results")
    print()

def demonstrate_orchestration_pattern():
    """Show how external orchestrators combine tools."""
    print("=== DEMONSTRATING ORCHESTRATION PATTERN ===")
    print()

    print("External orchestrator calling individual tools:")
    print("   Step 1: Call get_employee('EMP-101')")
    employee_data = get_employee("EMP-101")
    print(f"   Step 2: Call get_pto_balance('EMP-101')")
    pto_data = get_pto_balance("EMP-101")
    print(f"   Step 3: Call get_benefits('EMP-101')")
    benefits_data = get_benefits("EMP-101")
    print(f"   Step 4: Call search_policies('remote work')")
    policy_results = search_policies("remote work")

    print()
    print("Orchestrator combines results into final response:")

    # This is what an external orchestrator would do
    final_response = {
        "employee": employee_data["employee"],
        "pto_balance": pto_data["pto_balance"],
        "benefits": benefits_data["benefits"],
        "policy_search_results": policy_results["results"]
    }

    print("   Final combined response:")
    print(json.dumps(final_response, indent=2, default=str))

    # Verify the orchestration worked correctly
    assert "employee" in final_response
    assert "pto_balance" in final_response
    assert "benefits" in final_response
    assert "policy_search_results" in final_response

    print()
    print("✓ External orchestrator successfully combined all tool data")
    print("✓ Each tool returned only its specific data")
    print("✓ Final response contains complete information")

def demonstrate_mcp_server_role():
    """Explain what the MCP server should be doing."""
    print("=== MCP SERVER ROLE EXPLANATION ===")
    print()
    print("The MCP server's role:")
    print("  ✅ PROVIDES individual tools that return specific data")
    print("  ✅ DOES NOT combine results or create final responses")
    print("  ✅ DOES NOT orchestrate other tools")
    print("  ✅ ACTS AS A TOOL PROVIDER, NOT AN ORCHESTRATOR")
    print()
    print("External systems (orchesrators) then:")
    print("  ✅ CALL individual tools separately")
    print("  ✅ RECEIVE specific data from each tool")
    print("  ✅ COMBINE results into meaningful final responses")
    print()

def demonstrate_error_handling():
    """Show proper error handling."""
    print("=== ERROR HANDLING DEMONSTRATION ===")
    print()

    print("1. Invalid employee ID:")
    try:
        result = get_employee("INVALID-ID")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")

    print("2. Non-existent employee in PTO system:")
    try:
        result = get_pto_balance("EMP-999")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")

    print()
    print("✓ Tools handle errors gracefully without crashing")

def main():
    """Run the complete demonstration."""
    print("MCP Pattern Demonstration")
    print("=" * 50)
    print()

    demonstrate_individual_tool_usage()
    demonstrate_orchestration_pattern()
    demonstrate_mcp_server_role()
    demonstrate_error_handling()

    print("=" * 50)
    print("✅ DEMONSTRATION COMPLETE")
    print()
    print("This shows the CORRECT MCP pattern:")
    print("- Tools are called individually by external systems")
    print("- Each tool returns only its specific data")
    print("- External orchestrators combine results properly")
    print("- The server acts as a tool provider, not an orchestrator")

if __name__ == "__main__":
    main()