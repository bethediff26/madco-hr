"""
MCP Server for HR Policy Assistant.
Exposes tools for the agent to interact with HR systems.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
from fastmcp import FastMCP

# Import MCP components
try:
    from mcp import Client, Server, Transport, StdioTransport
    from mcp.types import Tool, ToolResult, ToolCall, ToolError
    from mcp.server import server
except ImportError:
    # Fallback for when mcp is not installed - we'll create mock versions
    class MockTool:
        def __init__(self, name: str, description: str, input_schema: Dict[str, Any]):
            self.name = name
            self.description = description
            self.input_schema = input_schema

    class MockClient:
        async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "mock", "message": f"Mock tool {tool_name} called with {arguments}"}

    Tool = MockTool
    Client = MockClient

logger = logging.getLogger(__name__)

mcp = FastMCP("MadCo HR MCP Server")

# Mock HR data - in a real implementation this would connect to actual databases
MOCK_HR_DATA = {
    "employees": {
        "EMP-12345": {
            "name": "John Smith",
            "department": "Engineering",
            "position": "Senior Software Engineer",
            "manager_id": "EMP-67890",
            "pto_balance": 15,
            "benefits": ["health", "dental", "vision", "401k"],
            "remote_work_eligible": True
        },
        "EMP-67890": {
            "name": "Sarah Johnson",
            "department": "Engineering",
            "position": "Engineering Manager",
            "manager_id": "EMP-55555",
            "pto_balance": 12,
            "benefits": ["health", "dental", "vision", "401k", "wellness"],
            "remote_work_eligible": True
        }
    },
    "policies": {
        "remote_work": {
            "title": "Remote Work Policy",
            "content": "Employees may work remotely with manager approval. Must maintain 40 hours/week.",
            "sections": ["eligibility", "requirements", "approval_process"]
        },
        "pto": {
            "title": "Paid Time Off Policy",
            "content": "Employees receive 15 PTO days annually, with carryover options.",
            "sections": ["accrual", "usage", "request_process"]
        }
    }
}


def _get_employee_data(employee_id: str) -> Dict[str, Any]:
    """Return MCP employee data, falling back to the repository employee data."""
    if employee_id in MOCK_HR_DATA["employees"]:
        return MOCK_HR_DATA["employees"][employee_id]

    employees_file = Path(__file__).parent.parent / "data" / "mock_data" / "employees.json"
    try:
        with open(employees_file, "r", encoding="utf-8") as file:
            employees = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    employee = next((item for item in employees if item.get("employee_id") == employee_id), None)
    if not employee:
        return None

    role = employee.get("role", "")
    employment_type = None
    status = None
    extended_file = Path(__file__).parent.parent / "data" / "mock_data" / "employees_extended.json"
    try:
        with open(extended_file, "r", encoding="utf-8") as file:
            extended_employees = json.load(file)
        extended_employee = next(
            (item for item in extended_employees if item.get("employee_id") == employee_id),
            None,
        )
        if extended_employee:
            employment_type = extended_employee.get("employment_type")
            status = extended_employee.get("status")
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    pto_balance = 0
    pto_file = Path(__file__).parent.parent / "data" / "mock_data" / "pto_balances.json"
    try:
        with open(pto_file, "r", encoding="utf-8") as file:
            pto_records = json.load(file)
        pto_record = next((item for item in pto_records if item.get("employee_id") == employee_id), None)
        if pto_record:
            pto_balance = pto_record.get("available_days", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    return {
        "name": employee.get("name"),
        "department": employee.get("department"),
        "position": role,
        "location": employee.get("location"),
        "manager_id": employee.get("manager_id"),
        "employment_type": employment_type,
        "status": status,
        "remote_work_eligible": role.lower() not in {"security personnel", "manufacturing roles"},
        "pto_balance": pto_balance,
        "benefits": [],
    }

# Global MCP server instance
mcp_server = None

@dataclass
class ToolMetadata:
    """Metadata for MCP tools."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

# Define the available tools with their schemas
HR_TOOLS = [
    ToolMetadata(
        name="search_policy_documents",
        description="Search policy documents for specific terms or topics",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query for policy documents"},
                "limit": {"type": "integer", "description": "Maximum number of results to return"}
            },
            "required": ["query"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "doc_title": {"type": "string"},
                            "section": {"type": "string"},
                            "content": {"type": "string"},
                            "relevance_score": {"type": "number"}
                        }
                    }
                },
                "total_matches": {"type": "integer"}
            }
        }
    ),
    ToolMetadata(
        name="get_policy_section",
        description="Retrieve a specific section from a policy document",
        input_schema={
            "type": "object",
            "properties": {
                "policy_name": {"type": "string", "description": "Name of the policy"},
                "section": {"type": "string", "description": "Section to retrieve"}
            },
            "required": ["policy_name", "section"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "doc_title": {"type": "string"},
                "section": {"type": "string"}
            }
        }
    ),
    ToolMetadata(
        name="lookup_employee_profile",
        description="Lookup employee profile information",
        input_schema={
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID to lookup"},
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to return"
                }
            },
            "required": ["employee_id"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "employee_id": {"type": "string"},
                "name": {"type": "string"},
                "department": {"type": "string"},
                "position": {"type": "string"},
                "pto_balance": {"type": "integer"},
                "benefits": {"type": "array", "items": {"type": "string"}},
                "remote_work_eligible": {"type": "boolean"}
            }
        }
    ),
    ToolMetadata(
        name="check_pto_balance",
        description="Check an employee's current PTO balance",
        input_schema={
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID to check"}
            },
            "required": ["employee_id"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "employee_id": {"type": "string"},
                "pto_balance": {"type": "integer"},
                "pto_used": {"type": "integer"},
                "pto_available": {"type": "integer"}
            }
        }
    ),
    ToolMetadata(
        name="lookup_benefits_status",
        description="Lookup employee's benefits status",
        input_schema={
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID to lookup"},
                "benefit_type": {"type": "string", "description": "Specific benefit type (optional)"}
            },
            "required": ["employee_id"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "employee_id": {"type": "string"},
                "benefits": {"type": "array", "items": {"type": "string"}},
                "benefit_details": {
                    "type": "object",
                    "additionalProperties": {"type": "object"}
                }
            }
        }
    ),
    ToolMetadata(
        name="create_mock_hr_ticket",
        description="Create a mock HR ticket for demonstration purposes",
        input_schema={
            "type": "object",
            "properties": {
                "ticket_type": {"type": "string", "description": "Type of ticket (e.g., 'policy', 'request')"},
                "summary": {"type": "string", "description": "Brief summary of the ticket"},
                "details": {"type": "string", "description": "Detailed description"},
                "priority": {"type": "string", "description": "Ticket priority (low, medium, high)"},
                "assignee_id": {"type": "string", "description": "ID of assignee"}
            },
            "required": ["ticket_type", "summary", "details"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string"},
                "status": {"type": "string"},
                "created_at": {"type": "string"},
                "assignee_id": {"type": "string"}
            }
        }
    ),
    ToolMetadata(
        name="draft_hr_email",
        description="Draft an HR-related email template",
        input_schema={
            "type": "object",
            "properties": {
                "email_type": {"type": "string", "description": "Type of email (e.g., 'pto_request', 'policy_update')"},
                "recipient_name": {"type": "string", "description": "Name of recipient"},
                "template_data": {
                    "type": "object",
                    "description": "Data to populate in the template"
                }
            },
            "required": ["email_type", "recipient_name"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "template_used": {"type": "string"}
            }
        }
    ),
    ToolMetadata(
        name="check_policy_compliance",
        description="Check if a request or action is compliant with HR policies",
        input_schema={
            "type": "object",
            "properties": {
                "request_type": {"type": "string", "description": "Type of request (e.g., 'pto', 'remote_work')"},
                "employee_id": {"type": "string", "description": "Employee ID"},
                "request_data": {
                    "type": "object",
                    "description": "Data about the specific request"
                }
            },
            "required": ["request_type", "employee_id"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "is_compliant": {"type": "boolean"},
                "compliance_issues": {"type": "array", "items": {"type": "string"}},
                "recommendations": {"type": "array", "items": {"type": "string"}},
                "policy_reference": {"type": "string"}
            }
        }
    )
]

# Create actual MCP tools from metadata
def create_mcp_tools() -> List[Tool]:
    """Create MCP tool definitions from the HR_TOOLS metadata."""
    tools = []

    for tool_meta in HR_TOOLS:
        # This is a simplified version - in a real implementation this would be more sophisticated
        tools.append(Tool(
            name=tool_meta.name,
            description=tool_meta.description,
            input_schema=tool_meta.input_schema
        ))

    return tools

# Tool implementations
async def search_policy_documents(query: str, limit: int = 5) -> Dict[str, Any]:
    """Search policy documents for specific terms."""
    logger.info(f"Searching policies for query: {query}")

    # This would normally use RAG index or database
    results = []

    # Mock implementation
    for policy_name, policy_data in MOCK_HR_DATA["policies"].items():
        if query.lower() in policy_data["content"].lower():
            results.append({
                "doc_title": policy_data["title"],
                "section": "full_policy",
                "content": policy_data["content"],
                "relevance_score": 0.9
            })

    return {
        "results": results[:limit],
        "total_matches": len(results)
    }

async def get_policy_section(policy_name: str, section: str) -> Dict[str, Any]:
    """Retrieve a specific section from a policy document."""
    logger.info(f"Retrieving {section} section from {policy_name}")

    # Mock implementation
    if policy_name in MOCK_HR_DATA["policies"]:
        return {
            "content": f"Content of {section} section for {policy_name}",
            "doc_title": MOCK_HR_DATA["policies"][policy_name]["title"],
            "section": section
        }

    return {
        "content": "Policy not found",
        "doc_title": policy_name,
        "section": section
    }

async def lookup_employee_profile(employee_id: str, fields: List[str] = None) -> Dict[str, Any]:
    """Lookup employee profile information."""
    logger.info(f"Looking up employee profile for ID: {employee_id}")

    emp_data = _get_employee_data(employee_id)
    if emp_data:

        # Return only requested fields if specified
        if fields:
            result = {"employee_id": employee_id}
            for field in fields:
                if field in emp_data:
                    result[field] = emp_data[field]
            return result
        else:
            return emp_data

    return {
        "error": "Employee not found",
        "employee_id": employee_id
    }

async def check_pto_balance(employee_id: str) -> Dict[str, Any]:
    """Check an employee's current PTO balance."""
    logger.info(f"Checking PTO balance for employee ID: {employee_id}")

    emp = _get_employee_data(employee_id)
    if emp:
        return {
            "employee_id": employee_id,
            "pto_balance": emp["pto_balance"],
            "pto_used": 0,  # Mock implementation
            "pto_available": emp["pto_balance"]
        }

    return {
        "error": "Employee not found",
        "employee_id": employee_id
    }

async def lookup_benefits_status(employee_id: str, benefit_type: str = None) -> Dict[str, Any]:
    """Lookup employee's benefits status."""
    logger.info(f"Looking up benefits for employee ID: {employee_id}")

    emp = _get_employee_data(employee_id)
    if emp:

        benefits_file = Path(__file__).parent.parent / "data" / "mock_data" / "benefits.json"
        try:
            with open(benefits_file, "r", encoding="utf-8") as file:
                benefits_data = json.load(file)
            benefits_record = next(
                (item for item in benefits_data if item.get("employee_id") == employee_id),
                None,
            )
        except (FileNotFoundError, json.JSONDecodeError):
            benefits_record = None

        if benefits_record:
            enrolled = [benefits_record["health_plan"]]
            if benefits_record["dental_enrolled"]:
                enrolled.append("dental")
            if benefits_record["vision_enrolled"]:
                enrolled.append("vision")
            return {
                "employee_id": employee_id,
                "benefits": enrolled,
                "benefit_details": benefits_record,
            }

        # Return all benefits if no specific type requested
        if benefit_type is None:
            return {
                "employee_id": employee_id,
                "benefits": emp["benefits"],
                "benefit_details": {}
            }
        elif benefit_type in emp["benefits"]:
            return {
                "employee_id": employee_id,
                "benefits": [benefit_type],
                "benefit_details": {benefit_type: {"status": "active"}}
            }

    return {
        "error": "Employee or benefit not found",
        "employee_id": employee_id
    }

async def create_mock_hr_ticket(ticket_type: str, summary: str, details: str,
                              priority: str = "medium", assignee_id: str = None) -> Dict[str, Any]:
    """Create a mock HR ticket for demonstration purposes."""
    logger.info(f"Creating mock HR ticket: {summary}")

    # In a real implementation, this would create an actual ticket
    return {
        "ticket_id": f"TICKET-{hash(summary) % 10000:04d}",
        "status": "open",
        "created_at": "2026-09-22T22:38:37Z",
        "assignee_id": assignee_id,
        "ticket_type": ticket_type,
        "summary": summary,
        "details": details,
        "priority": priority
    }

async def draft_hr_email(email_type: str, recipient_name: str, template_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Draft an HR-related email template."""
    logger.info(f"Drafting {email_type} email for {recipient_name}")

    templates = {
        "pto_request": {
            "subject": f"PTO Request - {recipient_name}",
            "body": f"Dear {recipient_name},\n\nI am writing to request PTO time. Please review my request and let me know if you need any additional information.\n\nThank you,\nHR Team"
        },
        "policy_update": {
            "subject": "Important HR Policy Update",
            "body": f"Dear {recipient_name},\n\nWe have updated our HR policies. Please review the attached document for details.\n\nBest regards,\nHR Department"
        }
    }

    template = templates.get(email_type, {"subject": "HR Communication", "body": f"Hello {recipient_name},\n\nThis is a test message."})

    subject = (template_data.get("subject") if template_data and template_data.get("subject") else template["subject"])
    body = (template_data.get("body") if template_data and template_data.get("body") else template["body"])

    return {
        "subject": subject,
        "body": body,
        "template_used": email_type
    }

async def check_policy_compliance(request_type: str, employee_id: str, request_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Check if a request or action is compliant with HR policies."""
    logger.info(f"Checking policy compliance for {request_type} request from {employee_id}")

    employee_data = _get_employee_data(employee_id)
    if not employee_data:
        raise ValueError(f"Employee ID '{employee_id}' not found")
    if request_type not in {"pto", "remote_work", "expense"}:
        raise ValueError(f"Unsupported request type: {request_type}")

    # Mock implementation - in real system this would check against actual policies
    request_data = request_data or {}

    # Simple compliance checks
    issues = []
    recommendations = []

    if request_type == "pto":
        pto_days = request_data.get("days", 0)
        if pto_days > employee_data.get("pto_balance", 0):
            issues.append(f"Insufficient PTO balance. Available: {employee_data.get('pto_balance', 0)} days")

    if request_type == "remote_work":
        if not employee_data.get("remote_work_eligible", False):
            issues.append("Employee is not eligible for remote work")
        duration_weeks = request_data.get("duration_weeks") or request_data.get("weeks", 0)
        if duration_weeks and duration_weeks >= 4:
            recommendations.append("Out-of-state stays exceeding 4 weeks require Department VP approval and HR/Legal review due to multi-state tax and payroll implications")

    if request_type == "expense":
        recommendations.append("Confirm the applicable approval threshold and retain required receipts")

    return {
        "is_compliant": len(issues) == 0,
        "compliance_issues": issues,
        "recommendations": recommendations,
        "policy_reference": f"hr_{request_type}_policy.md"
    }

# MCP Server implementation
class HRPolicyMCP:
    """MCP Server for HR Policy Assistant tools."""

    def __init__(self):
        self.tools = create_mcp_tools()
        self.client = None

    async def start_server(self, transport_type: str = "stdio"):
        """Start the MCP server."""
        try:
            # This is where we'd set up the actual MCP server
            logger.info("Starting HR Policy MCP Server")

            # In a real implementation, this would use the proper MCP framework:
            # server = Server()
            # await server.start(transport)

            return True
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            return False

    async def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover available tools."""
        tool_list = []
        for tool in self.tools:
            tool_list.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            })
        return tool_list

# Initialize global MCP server
mcp_server = HRPolicyMCP()

# Export the tools that will be called by the agent
policy_rag = search_policy_documents
employee_lookup = lookup_employee_profile
pto_check = check_pto_balance
benefits_lookup = lookup_benefits_status
compliance_check = check_policy_compliance

logger.info("HR Policy MCP Server initialized")


# Register the canonical async handlers with the real MCP server.
for _tool in (
    search_policy_documents,
    get_policy_section,
    lookup_employee_profile,
    check_pto_balance,
    lookup_benefits_status,
    create_mock_hr_ticket,
    draft_hr_email,
    check_policy_compliance,
):
    mcp.add_tool(_tool)


if __name__ == "__main__":
    mcp.run(transport="stdio")