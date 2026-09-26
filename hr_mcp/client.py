"""FastMCP client for the MadCo HR MCP server."""

import logging
import os
from pathlib import Path
from typing import Any, Dict

from fastmcp import Client
from fastmcp.client.transports import StdioTransport

logger = logging.getLogger(__name__)


class HRPolicyMCPClient:
    """Client that communicates with the HR MCP server over stdio."""

    def __init__(self, server_command: str = None):
        repository_root = Path(__file__).parent.parent
        self.server_command = server_command or os.getenv(
            "MCP_SERVER_COMMAND",
            str(repository_root / "env" / "bin" / "python"),
        )
        self.server_args = ["-m", "hr_mcp.server"]
        self.repository_root = repository_root
        self.client = None
        self.is_connected = False

    async def connect(self) -> bool:
        """Start the MCP server subprocess and initialize the protocol session."""
        try:
            transport = StdioTransport(
                command=self.server_command,
                args=self.server_args,
                cwd=str(self.repository_root),
            )
            self.client = Client(transport)
            await self.client.__aenter__()
            self.is_connected = True
            logger.info("Connected to HR Policy MCP Server over stdio")
            return True
        except Exception:
            logger.exception("Failed to connect to HR Policy MCP Server")
            self.client = None
            self.is_connected = False
            return False

    async def disconnect(self):
        """Close the MCP protocol session and server subprocess."""
        if self.client is not None:
            try:
                await self.client.__aexit__(None, None, None)
            except Exception:
                logger.warning("MCP client shutdown encountered an error", exc_info=True)
        self.client = None
        self.is_connected = False

    async def list_tools(self) -> list[str]:
        """Discover tools from the connected MCP server."""
        if not self.is_connected:
            await self.connect()
        if self.client is None:
            raise RuntimeError("MCP client is not connected")
        return [tool.name for tool in await self.client.list_tools()]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a discovered MCP tool and normalize its structured result."""
        if not self.is_connected:
            await self.connect()
        if self.client is None:
            raise RuntimeError("MCP client is not connected")

        result = await self.client.call_tool(tool_name, arguments)
        if result.is_error:
            return {"status": "error", "error": str(result.content)}
        if result.structured_content is not None:
            return result.structured_content
        return {"content": [item.model_dump() for item in result.content]}

    async def search_policy_documents(self, query: str, limit: int = 5) -> Dict[str, Any]:
        return await self.call_tool("search_policy_documents", {"query": query, "limit": limit})

    async def get_policy_section(self, policy_name: str, section: str) -> Dict[str, Any]:
        return await self.call_tool("get_policy_section", {"policy_name": policy_name, "section": section})

    async def lookup_employee_profile(self, employee_id: str, fields: list = None) -> Dict[str, Any]:
        arguments = {"employee_id": employee_id}
        if fields is not None:
            arguments["fields"] = fields
        return await self.call_tool("lookup_employee_profile", arguments)

    async def check_pto_balance(self, employee_id: str) -> Dict[str, Any]:
        return await self.call_tool("check_pto_balance", {"employee_id": employee_id})

    async def lookup_benefits_status(self, employee_id: str, benefit_type: str = None) -> Dict[str, Any]:
        arguments = {"employee_id": employee_id}
        if benefit_type is not None:
            arguments["benefit_type"] = benefit_type
        return await self.call_tool("lookup_benefits_status", arguments)

    async def create_mock_hr_ticket(self, ticket_type: str, summary: str, details: str,
                                    priority: str = "medium", assignee_id: str = None) -> Dict[str, Any]:
        return await self.call_tool("create_mock_hr_ticket", {
            "ticket_type": ticket_type,
            "summary": summary,
            "details": details,
            "priority": priority,
            "assignee_id": assignee_id,
        })

    async def draft_hr_email(self, email_type: str, recipient_name: str,
                             template_data: Dict[str, Any] = None) -> Dict[str, Any]:
        return await self.call_tool("draft_hr_email", {
            "email_type": email_type,
            "recipient_name": recipient_name,
            "template_data": template_data,
        })

    async def check_policy_compliance(self, request_type: str, employee_id: str,
                                      request_data: Dict[str, Any] = None) -> Dict[str, Any]:
        arguments = {
            "request_type": request_type,
            "employee_id": employee_id,
        }
        if request_data is not None:
            arguments["request_data"] = request_data
        return await self.call_tool("check_policy_compliance", arguments)


mcp_client = HRPolicyMCPClient()


async def initialize_mcp_client():
    """Initialize the shared MCP client."""
    return await mcp_client.connect()