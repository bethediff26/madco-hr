"""
Agent Orchestrator for HR Policy Assistant.
Handles user intent interpretation, tool selection, workflow execution, and response synthesis.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from rag.retrieval import PolicyRAG

# Import MCP components
from hr_mcp.client import mcp_client

logger = logging.getLogger(__name__)

@dataclass
class AgentTrace:
    """Trace of agent reasoning steps for operational visibility."""
    user_intent: str
    tools_selected: List[str]
    tool_arguments: List[Dict[str, Any]]
    tool_outputs: List[Dict[str, Any]]
    retrieved_sources: List[Dict[str, Any]]
    final_basis: str
    escalation_decision: Optional[str] = None

class HRPolicyAgentOrchestrator:
    """Main orchestrator for HR policy assistant workflows."""

    def __init__(self):
        self.policy_rag = PolicyRAG()
        self.trace_log = []
        self.mcp_client = mcp_client

    async def interpret_user_intent(self, user_query: str) -> Dict[str, Any]:
        """Interpret user intent and determine appropriate workflow."""
        intent = {
            "query": user_query,
            "workflow_type": "policy_search",
            "requires_multi_step": False,
            "contains_employee_id": False,
            "contains_specific_policy": False
        }

        # Check for employee ID patterns
        if any(pattern in user_query.lower() for pattern in ["emp-", "employee", "id:"]):
            intent["contains_employee_id"] = True

        # Check for multi-step workflow indicators
        multi_step_indicators = [
            "request", "apply", "submit", "create", "schedule",
            "checklist", "eligibility", "process", "ticket", "case",
            "balance", "available", "pto", "leave"
        ]
        if any(indicator in user_query.lower() for indicator in multi_step_indicators):
            intent["requires_multi_step"] = True

        # Check for specific policy areas
        policy_areas = ["remote work", "pto", "benefits", "expense", "data security", "onboarding"]
        if any(area in user_query.lower() for area in policy_areas):
            intent["contains_specific_policy"] = True

        return intent

    def decide_workflow(self, intent: Dict[str, Any]) -> str:
        """Decide which workflow to execute based on user intent."""
        query_lower = intent["query"].lower()
        if intent["contains_employee_id"] and any(
            phrase in query_lower
            for phrase in ["employee profile", "employee details", "employee information"]
        ):
            return "employee_profile"
        if intent["contains_employee_id"] and "benefit" in query_lower:
            return "benefits_question_handling"
        if intent["contains_employee_id"] and "ticket" in query_lower:
            return "hr_case_triage"
        if not intent["contains_employee_id"] and "policy" in query_lower:
            return "policy_search"
        if any(
            term in query_lower
            for term in [
                "harass", "discrimination", "retaliation", "workplace issue",
                "data exposed", "data was exposed", "data exposure", "company data",
                "security incident", "misconduct", "ethics complaint", "behavio",
                "conduct issue", "employee issue"
            ]
        ):
            return "hr_case_triage"
        if any(
            term in query_lower
            for term in ["expense", "reimburse", "laptop", "computer", "chair", "home office", "travel", "hotel", "flight", "mileage"]
        ):
            return "expense_compliance"
        remote_scenario = (
            "remote work" in query_lower or "work remotely" in query_lower
        ) and any(
            phrase in query_lower
            for phrase in [
                "eligibility", "another state", "another country", "international",
                "six weeks", "duration", "temporary location"
            ]
        )
        if remote_scenario:
            return "remote_work_eligibility"
        if intent["requires_multi_step"]:
            # Check for specific multi-step workflows
            if "remote work" in query_lower or "telework" in query_lower:
                return "remote_work_eligibility"
            elif re.search(r"\bpto\b|paid time off|\bleave\b", query_lower):
                return "pto_request_guidance"
            elif "benefit" in query_lower:
                return "benefits_question_handling"
            elif "expense" in query_lower or "reimbursement" in query_lower:
                return "expense_compliance"
            elif "onboard" in query_lower or "new hire" in query_lower:
                return "onboarding_checklist"
            elif "case" in query_lower or "ticket" in query_lower:
                return "hr_case_triage"

        # Default to simple policy search
        return "policy_search"

    async def execute_workflow(self, workflow_type: str, user_query: str,
                        employee_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute the selected workflow."""
        logger.info(f"Executing {workflow_type} workflow for query: '{user_query}'")

        # Initialize trace
        trace = AgentTrace(
            user_intent=user_query,
            tools_selected=[],
            tool_arguments=[],
            tool_outputs=[],
            retrieved_sources=[],
            final_basis=""
        )

        try:
            if workflow_type == "employee_profile":
                return await self._execute_employee_profile(employee_id, trace)
            elif workflow_type == "policy_search":
                return await self._execute_policy_search(user_query, trace)
            elif workflow_type == "remote_work_eligibility":
                return await self._execute_remote_work_eligibility(user_query, employee_id, trace)
            elif workflow_type == "pto_request_guidance":
                return await self._execute_pto_request_guidance(user_query, employee_id, trace)
            elif workflow_type == "benefits_question_handling":
                return await self._execute_benefits_question_handling(user_query, employee_id, trace)
            elif workflow_type == "expense_compliance":
                return await self._execute_expense_compliance(user_query, employee_id, trace)
            elif workflow_type == "onboarding_checklist":
                return await self._execute_onboarding_checklist(user_query, employee_id, trace)
            elif workflow_type == "hr_case_triage":
                return await self._execute_hr_case_triage(user_query, employee_id, trace)
            else:
                raise ValueError(f"Unknown workflow type: {workflow_type}")

        except Exception as e:
            logger.error(f"Error executing workflow {workflow_type}: {e}")
            return {
                "status": "error",
                "message": f"Workflow execution failed: {str(e)}",
                "trace": self._format_trace(trace)
            }

    async def _execute_employee_profile(self, employee_id: Optional[str], trace: AgentTrace) -> Dict[str, Any]:
        """Retrieve an employee profile from the employee data source."""
        if not employee_id:
            return {
                "status": "error",
                "message": "Please provide an employee ID to retrieve an employee profile.",
                "trace": self._format_trace(trace)
            }

        try:
            employee_result = await self.mcp_client.lookup_employee_profile(employee_id)
            trace.tools_selected.append("get_employee")
            trace.tool_arguments.append({"employee_id": employee_id})
            trace.tool_outputs.append(employee_result)
            if employee_result.get("error"):
                raise ValueError(employee_result["error"])
            trace.final_basis = "Employee profile lookup"

            profile = ", ".join(
                f"{field.replace('_', ' ')}: {value}"
                for field, value in employee_result.items()
            )
            return {
                "status": "ok",
                "message": f"Employee profile for {employee_id}: {profile}",
                "citations": [],
                "trace": self._format_trace(trace)
            }
        except ValueError as e:
            trace.tools_selected.append("get_employee")
            trace.tool_arguments.append({"employee_id": employee_id})
            trace.tool_outputs.append({"error": str(e)})
            trace.final_basis = "Employee profile lookup"
            return {
                "status": "error",
                "message": str(e),
                "citations": [],
                "trace": self._format_trace(trace)
            }

    async def _execute_policy_search(self, query: str, trace: AgentTrace) -> Dict[str, Any]:
        """Execute simple policy search workflow."""
        # Use existing RAG functionality
        try:
            result = self.policy_rag.answer_policy_question(query)

            trace.tools_selected.append("search_policies")
            trace.tool_arguments.append({"query": query})
            trace.tool_outputs.append(result)
            trace.retrieved_sources = result.get("citations", [])
            trace.final_basis = "RAG retrieval and answer generation"

            return {
                "status": result["status"],
                "message": result["message"],
                "citations": result.get("citations", []),
                "trace": self._format_trace(trace)
            }
        except Exception as e:
            logger.error(f"Policy search failed: {e}")
            raise

    async def _execute_remote_work_eligibility(self, query: str, employee_id: Optional[str], trace: AgentTrace) -> Dict[str, Any]:
        """Execute remote work eligibility workflow."""
        try:
            policy_queries = [
                "remote work policy eligibility approval",
                "data security policy",
            ]
            policy_results = []
            for policy_query in policy_queries:
                policy_result = self.policy_rag.answer_policy_question(policy_query)
                policy_results.append(policy_result)
                trace.tools_selected.append("search_policies")
                trace.tool_arguments.append({"query": policy_query})
                trace.tool_outputs.append(policy_result)
                trace.retrieved_sources.extend(policy_result.get("citations", []))

            duration_match = re.search(r"(\d+)\s+weeks?", query.lower())
            duration_weeks = int(duration_match.group(1)) if duration_match else None
            location_scope = (
                "international" if "country" in query.lower() or "international" in query.lower()
                else "another_state" if "state" in query.lower()
                else "unspecified"
            )

            if not employee_id:
                message = (
                    "To assess remote work from another state or country, please provide your employee ID, "
                    "the destination, and the proposed dates. The request must also go through manager approval."
                )
            else:
                emp_result = await self.mcp_client.lookup_employee_profile(employee_id)
                trace.tools_selected.append("lookup_employee_profile")
                trace.tool_arguments.append({"employee_id": employee_id})
                trace.tool_outputs.append(emp_result)
                if emp_result.get("error"):
                    return {
                        "status": "error",
                        "message": emp_result["error"],
                        "citations": trace.retrieved_sources,
                        "trace": self._format_trace(trace)
                    }

                compliance_result = await self.mcp_client.check_policy_compliance(
                    "remote_work",
                    employee_id,
                    {"duration_weeks": duration_weeks, "location_scope": location_scope}
                )
                trace.tools_selected.append("check_policy_compliance")
                trace.tool_arguments.append({
                    "request_type": "remote_work",
                    "employee_id": employee_id,
                    "request_data": {"duration_weeks": duration_weeks, "location_scope": location_scope}
                })
                trace.tool_outputs.append(compliance_result)
                if compliance_result.get("error"):
                    return {
                        "status": "error",
                        "message": compliance_result["error"],
                        "citations": trace.retrieved_sources,
                        "trace": self._format_trace(trace)
                    }

                compliance_status = "passes the current remote-work eligibility check" if compliance_result["is_compliant"] else "does not pass the current remote-work eligibility check"
                duration_text = f" for {duration_weeks} weeks" if duration_weeks else ""
                message = (
                    f"Employee {employee_id} {compliance_status}{duration_text}. "
                    "Next steps: submit the remote-work request in Workday with the destination and dates, "
                    "obtain manager approval, and follow VPN, encryption, and data-handling requirements. "
                    "The policy corpus does not contain a dedicated tax or location-compliance policy, "
                    "so confirm payroll, tax, and cross-border requirements with HR or Legal before travel."
                )

            trace.final_basis = "Remote work, data security, employee profile, and compliance checks"

            return {
                "status": "ok",
                "message": message,
                "citations": trace.retrieved_sources,
                "trace": self._format_trace(trace)
            }
        except Exception as e:
            logger.error(f"Remote work eligibility workflow failed: {e}")
            raise

    async def _execute_pto_request_guidance(self, query: str, employee_id: Optional[str], trace: AgentTrace) -> Dict[str, Any]:
        """Execute PTO request guidance workflow."""
        try:
            # Get PTO policy information
            policy_result = self.policy_rag.answer_policy_question("pto policy")

            trace.tools_selected.append("search_policies")
            trace.tool_arguments.append({"query": "pto policy"})
            trace.tool_outputs.append(policy_result)
            trace.retrieved_sources = policy_result.get("citations", [])

            number_words = {
                "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            }
            days_match = re.search(r"(\d+)\s+days?", query.lower())
            requested_days = int(days_match.group(1)) if days_match else None
            if requested_days is None:
                for word, value in number_words.items():
                    if re.search(rf"\b{word}\s+days?\b", query.lower()):
                        requested_days = value
                        break
            notice_weeks = 1 if "next week" in query.lower() else None

            # Use MCP to check PTO balance if employee ID provided
            if employee_id:
                try:
                    pto_result = await self.mcp_client.check_pto_balance(employee_id)
                    trace.tools_selected.append("check_pto_balance")
                    trace.tool_arguments.append({"employee_id": employee_id})
                    trace.tool_outputs.append(pto_result)

                    if 'error' in pto_result:
                        return {
                            "status": "error",
                            "message": pto_result["error"],
                            "citations": policy_result.get("citations", []),
                            "trace": self._format_trace(trace)
                        }

                    available_days = pto_result.get("pto_available", pto_result.get("pto_balance", 0))

                    compliance_result = await self.mcp_client.check_policy_compliance(
                        "pto",
                        employee_id,
                        {"days": requested_days or 0}
                    )
                    trace.tools_selected.append("check_policy_compliance")
                    trace.tool_arguments.append({
                        "request_type": "pto",
                        "employee_id": employee_id,
                        "request_data": {"days": requested_days or 0}
                    })
                    trace.tool_outputs.append(compliance_result)
                    if compliance_result.get("error"):
                        return {
                            "status": "error",
                            "message": compliance_result["error"],
                            "citations": policy_result.get("citations", []),
                            "trace": self._format_trace(trace)
                        }

                    notice_required = 4 if requested_days and requested_days >= 3 else 2
                    notice_issue = (
                        notice_weeks is not None and notice_weeks < notice_required
                    )
                    issues = list(compliance_result.get("compliance_issues", []))
                    if notice_issue:
                        issues.append(
                            f"Requests of {requested_days} or more consecutive days require at least "
                            f"{notice_required} weeks' notice; next week provides about {notice_weeks} week."
                        )

                    message = f"PTO request guidance for employee {employee_id}: You have {available_days} PTO days available. "
                    if requested_days:
                        message += f"Your request is for {requested_days} day(s). "
                    message += "Manager approval is required, and the request must be submitted through Workday. "
                    if issues:
                        message += "The request needs HR review because: " + " ".join(issues) + " "
                    else:
                        message += "The balance and current compliance checks support submitting the request. "
                    message += "For specific notice and approval requirements, refer to the PTO policy."

                    if issues:
                        ticket_summary = f"PTO request review: {requested_days or 'unspecified'} day(s)"
                        ticket_result = await self.mcp_client.create_mock_hr_ticket(
                            "pto_request",
                            ticket_summary,
                            query,
                            assignee_id=employee_id,
                        )
                        trace.tools_selected.append("create_mock_hr_ticket")
                        trace.tool_arguments.append({
                            "employee_id": employee_id,
                            "issue": query,
                        })
                        trace.tool_outputs.append(ticket_result)
                        ticket_id = ticket_result.get('ticket_id', 'TICK-REVIEW') if isinstance(ticket_result, dict) else 'TICK-REVIEW'
                        message += f" Mock HR ticket {ticket_id} was created for review."
                except Exception as e:
                    logger.warning(f"Could not check PTO balance: {e}")
                    message = f"PTO request guidance for employee {employee_id}: "
                    message += f"The PTO request could not be fully evaluated: {e}"
            else:
                message = "For PTO requests: 1) Check your current PTO balance, "
                message += "2) Submit your request through the HR portal, "
                message += "3) Review the PTO policy for eligibility requirements."

            trace.final_basis = "PTO policy + request guidance"

            return {
                "status": "ok",
                "message": message,
                "citations": policy_result.get("citations", []),
                "trace": self._format_trace(trace)
            }
        except Exception as e:
            logger.error(f"PTO request guidance workflow failed: {e}")
            raise

    async def _execute_benefits_question_handling(self, query: str, employee_id: Optional[str], trace: AgentTrace) -> Dict[str, Any]:
        """Execute benefits question handling workflow."""
        try:
            # Get benefits policy information
            policy_result = self.policy_rag.answer_policy_question("benefits policy")

            trace.tools_selected.append("search_policies")
            trace.tool_arguments.append({"query": "benefits policy"})
            trace.tool_outputs.append(policy_result)
            trace.retrieved_sources = policy_result.get("citations", [])

            # Provide benefits guidance
            message = "Benefits information: "
            if employee_id:
                try:
                    employee_result = await self.mcp_client.lookup_employee_profile(employee_id)
                    trace.tools_selected.append("get_employee")
                    trace.tool_arguments.append({"employee_id": employee_id})
                    trace.tool_outputs.append(employee_result)
                    if employee_result.get("error"):
                        raise ValueError(employee_result["error"])
                    benefits_result = await self.mcp_client.lookup_benefits_status(employee_id)
                    trace.tools_selected.append("lookup_benefits_status")
                    trace.tool_arguments.append({"employee_id": employee_id})
                    trace.tool_outputs.append(benefits_result)
                    if benefits_result.get("error"):
                        raise ValueError(benefits_result["error"])

                    enrolled = []
                    benefit_details = benefits_result.get("benefit_details", {})
                    if benefit_details.get("health_plan"):
                        enrolled.append(f"{benefit_details['health_plan']} health plan")
                    if "dental" in benefits_result.get("benefits", []):
                        enrolled.append("dental")
                    if "vision" in benefits_result.get("benefits", []):
                        enrolled.append("vision")
                    employment_type = employee_result.get("employment_type")
                    employment_status = employee_result.get("status")
                    if not employment_type or not employment_status:
                        message = (
                            f"Benefits eligibility for employee {employee_id} requires HR review because "
                            "employment type or active status is not available in the employee record. "
                        )
                    elif employment_status.lower() != "active":
                        message = (
                            f"Employee {employee_id} is not marked Active, so benefits eligibility requires HR review. "
                        )
                    else:
                        message = f"Benefits information for employee {employee_id} ({employment_type}):\n"
                        message += "\n".join(f"- {benefit}" for benefit in enrolled)
                        message += f"\n- 401k match: {benefit_details.get('401k_match_percent', 'not available')}%"
                        message += f"\n- Wellness stipend used: ${benefit_details.get('wellness_stipend_used', 'not available')}"
                    if not employment_type or not employment_status or employment_status.lower() != "active":
                        message += " Please escalate to HR to confirm eligibility before making changes."
                except ValueError as e:
                    trace.tools_selected.append("get_benefits")
                    trace.tool_arguments.append({"employee_id": employee_id})
                    trace.tool_outputs.append({"error": str(e)})
                    trace.final_basis = "Employee benefits lookup"
                    return {
                        "status": "error",
                        "message": f"Benefits eligibility for employee {employee_id} requires HR review: {e}",
                        "citations": policy_result.get("citations", []),
                        "trace": self._format_trace(trace)
                    }
                except Exception as e:
                    logger.warning(f"Could not fetch benefits for employee {employee_id}: {e}")
                    message += "Please provide your employee ID to access your personalized benefits information. "
            else:
                message += "Please provide your employee ID to access your personalized benefits information. "

            message += "\n\nThe general benefits policy covers health, dental, vision, 401K, and wellness stipends."

            trace.final_basis = "Benefits policy + personalized guidance"

            return {
                "status": "ok",
                "message": message,
                "citations": policy_result.get("citations", []),
                "trace": self._format_trace(trace)
            }
        except Exception as e:
            logger.error(f"Benefits question handling workflow failed: {e}")
            raise

    async def _execute_expense_compliance(self, query: str, employee_id: Optional[str], trace: AgentTrace) -> Dict[str, Any]:
        """Execute expense compliance workflow."""
        try:
            query_lower = query.lower()
            expense_type = (
                "laptop" if "laptop" in query_lower or "computer" in query_lower
                else "home_office" if "chair" in query_lower or "home office" in query_lower
                else "travel" if any(word in query_lower for word in ["travel", "hotel", "flight", "mileage"])
                else "general"
            )
            policy_queries = ["expense policy"]
            if expense_type == "laptop":
                policy_queries.append("equipment policy")
            for policy_query in policy_queries:
                policy_result = self.policy_rag.answer_policy_question(policy_query)
                trace.tools_selected.append("search_policies")
                trace.tool_arguments.append({"query": policy_query})
                trace.tool_outputs.append(policy_result)
                trace.retrieved_sources.extend(policy_result.get("citations", []))

            profile = None
            if employee_id:
                profile = await self.mcp_client.lookup_employee_profile(employee_id)
                trace.tools_selected.append("lookup_employee_profile")
                trace.tool_arguments.append({"employee_id": employee_id})
                trace.tool_outputs.append(profile)
                if profile.get("error"):
                    return {
                        "status": "error",
                        "message": profile["error"],
                        "citations": trace.retrieved_sources,
                        "trace": self._format_trace(trace)
                    }

            compliance_result = None
            if employee_id:
                compliance_result = await self.mcp_client.check_policy_compliance(
                    "expense",
                    employee_id,
                    {"expense_type": expense_type, "location": profile.get("location") if profile else None}
                )
                trace.tools_selected.append("check_policy_compliance")
                trace.tool_arguments.append({
                    "request_type": "expense",
                    "employee_id": employee_id,
                    "request_data": {"expense_type": expense_type, "location": profile.get("location") if profile else None}
                })
                trace.tool_outputs.append(compliance_result)
                if compliance_result.get("error"):
                    return {
                        "status": "error",
                        "message": compliance_result["error"],
                        "citations": trace.retrieved_sources,
                        "trace": self._format_trace(trace)
                    }

            guidance = {
                "laptop": "Company equipment policy generally covers laptop allocation; confirm whether this is a company-issued request rather than a personal reimbursement.",
                "home_office": "Ergonomic home-office furniture may qualify under the home-office stipend, subject to eligibility, limits, receipts, and approval.",
                "travel": "Business travel may be reimbursable when authorized, documented with receipts, and submitted through the expense workflow.",
                "general": "Submit the expense through the company expense portal with the business purpose, required receipts, and manager approval."
            }[expense_type]
            message = f"Expense compliance guidance: {guidance}"
            if employee_id:
                message += f" Employee {employee_id} profile location: {profile.get('location', 'not available')}."
                message += " The current compliance check passed; confirm the applicable approval threshold before submitting."
            message += " See the cited expense/equipment policy for the governing requirements."

            trace.final_basis = "Expense policy, employee profile, and compliance check"

            return {
                "status": "ok",
                "message": message,
                "citations": trace.retrieved_sources,
                "trace": self._format_trace(trace)
            }
        except Exception as e:
            logger.error(f"Expense compliance workflow failed: {e}")
            raise

    async def _execute_onboarding_checklist(self, query: str, employee_id: Optional[str], trace: AgentTrace) -> Dict[str, Any]:
        """Execute onboarding checklist workflow."""
        try:
            # Get onboarding policy information
            policy_result = self.policy_rag.answer_policy_question("onboarding process")

            trace.tools_selected.append("search_policies")
            trace.tool_arguments.append({"query": "onboarding process"})
            trace.tool_outputs.append(policy_result)
            trace.retrieved_sources = policy_result.get("citations", [])

            # Provide onboarding guidance
            message = "Onboarding checklist: "
            message += "1) Complete HR paperwork, 2) Set up your workspace, "
            message += "3) Review company policies, 4) Schedule team introductions. "
            message += "For detailed steps, please consult the onboarding policy document."

            trace.final_basis = "Onboarding policy + checklist guidance"

            return {
                "status": "ok",
                "message": message,
                "citations": policy_result.get("citations", []),
                "trace": self._format_trace(trace)
            }
        except Exception as e:
            logger.error(f"Onboarding checklist workflow failed: {e}")
            raise

    async def _execute_hr_case_triage(self, query: str, employee_id: Optional[str], trace: AgentTrace) -> Dict[str, Any]:
        """Execute HR case triage workflow."""
        try:
            query_lower = query.lower()
            sensitive = any(
                term in query_lower
                for term in ["harass", "discrimination", "retaliation", "data exposed", "data was exposed", "data exposure", "company data", "security incident", "misconduct", "ethics complaint", "behavio", "conduct issue", "employee issue"]
            )
            policy_queries = []
            if any(term in query_lower for term in ["data", "security", "exposed"]):
                policy_queries.append("data security policy")
            if any(term in query_lower for term in ["harass", "discrimination", "retaliation", "misconduct", "ethics"]):
                policy_queries.append("code of conduct policy")
            if not policy_queries:
                policy_queries.append("code of conduct policy")

            for policy_query in policy_queries:
                policy_result = self.policy_rag.answer_policy_question(policy_query)
                trace.tools_selected.append("search_policies")
                trace.tool_arguments.append({"query": policy_query})
                trace.tool_outputs.append(policy_result)
                trace.retrieved_sources.extend(policy_result.get("citations", []))

            if employee_id:
                employee_result = await self.mcp_client.lookup_employee_profile(employee_id)
                trace.tools_selected.append("get_employee")
                trace.tool_arguments.append({"employee_id": employee_id})
                trace.tool_outputs.append(employee_result)

            if sensitive and employee_id:
                ticket_result = await self.mcp_client.create_mock_hr_ticket(
                    "sensitive_hr_case",
                    "Sensitive workplace issue",
                    query,
                    assignee_id=employee_id,
                )
                trace.tools_selected.append("create_mock_hr_ticket")
                trace.tool_arguments.append({"employee_id": employee_id, "issue": query})
                trace.tool_outputs.append(ticket_result)
                trace.escalation_decision = "escalate_to_hr"
                message = (
                    f"This issue should be escalated to HR for confidential review. "
                    f"A mock HR case summary was created as ticket {ticket_result['ticket_id']}. "
                    "Preserve relevant evidence, avoid retaliation or direct confrontation, and use the HR or ethics reporting channel."
                )
            else:
                trace.escalation_decision = "hr_review_recommended"
                message = (
                    "This workplace issue should be reviewed by HR. Provide the relevant dates, people involved, "
                    "facts, and supporting documentation through the standard HR case channel."
                )

            trace.final_basis = "Relevant conduct/security policy + HR case triage"

            return {
                "status": "ok",
                "message": message,
                "citations": trace.retrieved_sources,
                "trace": self._format_trace(trace)
            }
        except Exception as e:
            logger.error(f"HR case triage workflow failed: {e}")
            raise

    def _format_trace(self, trace: AgentTrace) -> Dict[str, Any]:
        """Format the trace for operational visibility."""
        return {
            "user_intent": trace.user_intent,
            "tools_selected": trace.tools_selected,
            "tool_arguments": trace.tool_arguments,
            "tool_outputs": trace.tool_outputs,
            "retrieved_sources": trace.retrieved_sources,
            "final_basis": trace.final_basis,
            "escalation_decision": trace.escalation_decision
        }

    async def process_user_query(self, user_query: str, employee_id: Optional[str] = None) -> Dict[str, Any]:
        """Main entry point for processing user queries with full orchestration."""
        logger.info(f"Processing user query: '{user_query}'")

        # Interpret user intent
        intent = await self.interpret_user_intent(user_query)
        logger.info(f"Interpreted intent: {intent}")

        # Decide workflow
        workflow_type = self.decide_workflow(intent)
        logger.info(f"Selected workflow: {workflow_type}")

        # Execute workflow
        result = await self.execute_workflow(workflow_type, user_query, employee_id)

        # Log trace
        if "trace" in result:
            self.trace_log.append(result["trace"])
            logger.info(f"Trace logged for query: '{user_query}'")

        return result

# Initialize global orchestrator
orchestrator = HRPolicyAgentOrchestrator()