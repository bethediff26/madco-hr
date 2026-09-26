"""End-to-end tests for the real FastMCP stdio integration."""

import pytest

from hr_mcp.client import HRPolicyMCPClient


@pytest.mark.asyncio
async def test_mcp_discovers_and_calls_tools():
    client = HRPolicyMCPClient()
    assert await client.connect()
    try:
        tools = await client.list_tools()
        assert tools == [
            "search_policy_documents",
            "get_policy_section",
            "lookup_employee_profile",
            "check_pto_balance",
            "lookup_benefits_status",
            "create_mock_hr_ticket",
            "draft_hr_email",
            "check_policy_compliance",
        ]

        profile = await client.lookup_employee_profile("EMP-101")
        assert profile["name"] == "Alice Johnson"

        compliance = await client.check_policy_compliance(
            "pto", "EMP-101", {"days": 3}
        )
        assert compliance["is_compliant"] is True
    finally:
        await client.disconnect()
