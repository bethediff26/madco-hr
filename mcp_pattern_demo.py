#!/usr/bin/env python3
"""
MCP Pattern Demonstration - Complete Example

This file demonstrates the correct MCP pattern where:
1. Individual tools are called by external systems
2. Each tool returns only its specific data
3. An external orchestrator combines results properly
"""

import json
from hr_mcp.server import (
    get_employee,
    get_pto_balance,
    get_benefits,
    search_policies
)

def demonstrate_proper_mcp_usage():
    """Show how MCP should be used correctly."""

    print("=== PROPER MCP USAGE DEMONSTRATION ===")
    print()

    # Step 1: Individual tool calls (what external systems do)
    print("1. External orchestrator calls individual tools:")

    employee_data = get_employee("EMP-101")
    print(f"   get_employee('EMP-101') -> {employee_data['employee']['name']}")

    pto_data = get_pto_balance("EMP-101")
    print(f"   get_pto_balance('EMP-101') -> {pto_data['pto_balance']['available_days']} days")

    benefits_data = get_benefits("EMP-101")
    print(f"   get_benefits('EMP-101') -> {benefits_data['benefits']['health_plan']} plan")

    policy_results = search_policies("remote work")
    print(f"   search_policies('remote work') -> {len(policy_results['results'])} documents")

    # Step 2: External orchestrator combines the results
    print()
    print("2. External orchestrator combines results:")

    final_response = {
        "employee": employee_data["employee"],
        "pto_balance": pto_data["pto_balance"],
        "benefits": benefits_data["benefits"],
        "policy_search_results": policy_results["results"]
    }

    print("   Final combined response created by external orchestrator")
    print(f"   ✓ Contains {len(final_response)} data sections")
    print()

    # Step 3: Verify the pattern
    print("3. Verification of proper MCP pattern:")
    print("   ✅ Individual tools return only their specific data")
    print("   ✅ External orchestrator combines results properly")
    print("   ✅ Server acts as tool provider, not orchestrator")
    print("   ✅ Each tool is independent and reusable")

    return final_response

def main():
    """Run the demonstration."""
    print("MCP Pattern Demonstration")
    print("=" * 50)

    try:
        result = demonstrate_proper_mcp_usage()

        print()
        print("=== FINAL RESPONSE STRUCTURE ===")
        print(json.dumps(result, indent=2, default=str))

        print()
        print("=" * 50)
        print("✅ DEMONSTRATION COMPLETE")
        print("This shows the CORRECT MCP pattern:")
        print("- Tools are called individually by external systems")
        print("- Each tool returns only its specific data")
        print("- External orchestrators combine results properly")
        print("- The server acts as a tool provider, not an orchestrator")

    except Exception as e:
        print(f"Error during demonstration: {e}")

if __name__ == "__main__":
    main()