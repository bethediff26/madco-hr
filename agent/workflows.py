"""
Multi-step HR Workflows for the Agent Orchestrator.
"""

import logging
from typing import Dict, List, Any, Optional
from rag.retrieval import PolicyRAG
from hr_mcp.server import policy_rag

logger = logging.getLogger(__name__)

class HRWorkflows:
    """Collection of multi-step HR workflows."""

    def __init__(self):
        self.policy_rag = PolicyRAG()

    def remote_work_eligibility_workflow(self, employee_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Multi-step workflow for remote work eligibility.

        Args:
            employee_id: The employee's ID
            request_data: Data about the remote work request

        Returns:
            Dictionary with workflow results and trace
        """
        logger.info(f"Starting remote work eligibility workflow for employee {employee_id}")

        # Step 1: Check employee eligibility based on role and department
        try:
            eligibility_check = self.policy_rag.answer_policy_question(
                "remote work eligibility criteria"
            )

            # Step 2: Check current employment status
            employment_status = self.policy_rag.answer_policy_question(
                "employee employment status requirements"
            )

            # Step 3: Check department-specific policies
            dept_policy = self.policy_rag.answer_policy_question(
                "department specific remote work policies"
            )

            # Combine results
            message = (
                f"Remote Work Eligibility for Employee {employee_id}:\n\n"
                f"1. General Criteria: {eligibility_check.get('message', 'No information available')}\n"
                f"2. Employment Status: {employment_status.get('message', 'No information available')}\n"
                f"3. Department Policy: {dept_policy.get('message', 'No information available')}\n\n"
                "Recommendation: Please submit a formal remote work request through the HR portal."
            )

            return {
                "status": "ok",
                "message": message,
                "citations": eligibility_check.get("citations", []) +
                           employment_status.get("citations", []) +
                           dept_policy.get("citations", []),
                "workflow_step": "remote_work_eligibility"
            }

        except Exception as e:
            logger.error(f"Remote work eligibility workflow failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to process remote work eligibility: {str(e)}",
                "workflow_step": "remote_work_eligibility"
            }

    def pto_request_guidance_workflow(self, employee_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Multi-step workflow for PTO request guidance.

        Args:
            employee_id: The employee's ID
            request_data: Data about the PTO request

        Returns:
            Dictionary with workflow results and trace
        """
        logger.info(f"Starting PTO request guidance workflow for employee {employee_id}")

        try:
            # Step 1: Check current PTO balance (mock implementation)
            pto_balance = self.policy_rag.answer_policy_question(
                "current employee PTO balance policy"
            )

            # Step 2: Check PTO request procedure
            request_procedure = self.policy_rag.answer_policy_question(
                "PTO request submission process"
            )

            # Step 3: Check carryover policies
            carryover_policy = self.policy_rag.answer_policy_question(
                "PTO carryover policy"
            )

            # Combine results
            message = (
                f"PTO Request Guidance for Employee {employee_id}:\n\n"
                f"1. Current Balance: {pto_balance.get('message', 'No information available')}\n"
                f"2. Request Procedure: {request_procedure.get('message', 'No information available')}\n"
                f"3. Carryover Policy: {carryover_policy.get('message', 'No information available')}\n\n"
                "Recommendation: Submit your PTO request through the standard HR portal with proper notice."
            )

            return {
                "status": "ok",
                "message": message,
                "citations": pto_balance.get("citations", []) +
                           request_procedure.get("citations", []) +
                           carryover_policy.get("citations", []),
                "workflow_step": "pto_request_guidance"
            }

        except Exception as e:
            logger.error(f"PTO request guidance workflow failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to process PTO request guidance: {str(e)}",
                "workflow_step": "pto_request_guidance"
            }

    def benefits_question_handling_workflow(self, employee_id: str, question: str) -> Dict[str, Any]:
        """
        Multi-step workflow for handling benefits questions.

        Args:
            employee_id: The employee's ID
            question: The benefits-related question

        Returns:
            Dictionary with workflow results and trace
        """
        logger.info(f"Starting benefits question handling workflow for employee {employee_id}")

        try:
            # Step 1: Get general benefits information
            benefits_info = self.policy_rag.answer_policy_question(
                "general benefits overview"
            )

            # Step 2: Get specific benefit details (if question is about a specific benefit)
            if "health" in question.lower() or "medical" in question.lower():
                benefit_details = self.policy_rag.answer_policy_question(
                    "health insurance policy details"
                )
            elif "dental" in question.lower():
                benefit_details = self.policy_rag.answer_policy_question(
                    "dental insurance policy details"
                )
            elif "401k" in question.lower() or "retirement" in question.lower():
                benefit_details = self.policy_rag.answer_policy_question(
                    "401k retirement plan details"
                )
            else:
                benefit_details = {"message": "No specific benefit details available."}

            # Step 3: Get enrollment procedures
            enrollment_procedure = self.policy_rag.answer_policy_question(
                "benefits enrollment process"
            )

            # Combine results
            message = (
                f"Benefits Question Handling for Employee {employee_id}:\n\n"
                f"1. General Benefits: {benefits_info.get('message', 'No information available')}\n"
                f"2. Specific Details: {benefit_details.get('message', 'No specific details available')}\n"
                f"3. Enrollment Process: {enrollment_procedure.get('message', 'No information available')}\n\n"
                "Recommendation: For personalized benefits information, please use the employee portal."
            )

            return {
                "status": "ok",
                "message": message,
                "citations": benefits_info.get("citations", []) +
                           benefit_details.get("citations", []) +
                           enrollment_procedure.get("citations", []),
                "workflow_step": "benefits_question_handling"
            }

        except Exception as e:
            logger.error(f"Benefits question handling workflow failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to process benefits question handling: {str(e)}",
                "workflow_step": "benefits_question_handling"
            }

    def expense_compliance_workflow(self, employee_id: str, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Multi-step workflow for expense compliance.

        Args:
            employee_id: The employee's ID
            expense_data: Data about the expense

        Returns:
            Dictionary with workflow results and trace
        """
        logger.info(f"Starting expense compliance workflow for employee {employee_id}")

        try:
            # Step 1: Check general expense policy
            expense_policy = self.policy_rag.answer_policy_question(
                "expense reimbursement policy"
            )

            # Step 2: Check category-specific policies
            if "travel" in expense_data.get("category", "").lower():
                travel_policy = self.policy_rag.answer_policy_question(
                    "business travel expense policy"
                )
            elif "equipment" in expense_data.get("category", "").lower():
                equipment_policy = self.policy_rag.answer_policy_question(
                    "office equipment expense policy"
                )
            else:
                travel_policy = {"message": "No specific travel policy information."}
                equipment_policy = {"message": "No specific equipment policy information."}

            # Step 3: Check submission requirements
            submission_requirements = self.policy_rag.answer_policy_question(
                "expense report submission requirements"
            )

            # Combine results
            message = (
                f"Expense Compliance for Employee {employee_id}:\n\n"
                f"1. General Policy: {expense_policy.get('message', 'No information available')}\n"
                f"2. Category Policy: {travel_policy.get('message', 'No specific policy available')}\n"
                f"3. Submission Requirements: {submission_requirements.get('message', 'No information available')}\n\n"
                "Recommendation: Submit your expense report through the company portal with all required receipts."
            )

            return {
                "status": "ok",
                "message": message,
                "citations": expense_policy.get("citations", []) +
                           travel_policy.get("citations", []) +
                           submission_requirements.get("citations", []),
                "workflow_step": "expense_compliance"
            }

        except Exception as e:
            logger.error(f"Expense compliance workflow failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to process expense compliance: {str(e)}",
                "workflow_step": "expense_compliance"
            }

    def onboarding_checklist_workflow(self, employee_id: str, new_hire_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Multi-step workflow for onboarding checklist.

        Args:
            employee_id: The employee's ID
            new_hire_data: Data about the new hire

        Returns:
            Dictionary with workflow results and trace
        """
        logger.info(f"Starting onboarding checklist workflow for employee {employee_id}")

        try:
            # Step 1: Get general onboarding process
            onboarding_process = self.policy_rag.answer_policy_question(
                "onboarding process overview"
            )

            # Step 2: Check required documentation
            required_docs = self.policy_rag.answer_policy_question(
                "required onboarding documentation"
            )

            # Step 3: Check IT setup procedures
            it_setup = self.policy_rag.answer_policy_question(
                "IT setup and equipment provisioning"
            )

            # Combine results
            message = (
                f"Onboarding Checklist for Employee {employee_id}:\n\n"
                f"1. General Process: {onboarding_process.get('message', 'No information available')}\n"
                f"2. Required Documents: {required_docs.get('message', 'No information available')}\n"
                f"3. IT Setup: {it_setup.get('message', 'No information available')}\n\n"
                "Recommendation: Complete all onboarding steps in the employee portal and contact HR if you have questions."
            )

            return {
                "status": "ok",
                "message": message,
                "citations": onboarding_process.get("citations", []) +
                           required_docs.get("citations", []) +
                           it_setup.get("citations", []),
                "workflow_step": "onboarding_checklist"
            }

        except Exception as e:
            logger.error(f"Onboarding checklist workflow failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to process onboarding checklist: {str(e)}",
                "workflow_step": "onboarding_checklist"
            }

    def hr_case_triage_workflow(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Multi-step workflow for HR case triage.

        Args:
            case_data: Data about the HR case

        Returns:
            Dictionary with workflow results and trace
        """
        logger.info("Starting HR case triage workflow")

        try:
            # Step 1: Determine case severity
            severity_check = self.policy_rag.answer_policy_question(
                "HR case severity classification"
            )

            # Step 2: Check case categorization policies
            category_policy = self.policy_rag.answer_policy_question(
                "HR case categorization guidelines"
            )

            # Step 3: Check assignment procedures
            assignment_procedure = self.policy_rag.answer_policy_question(
                "HR case assignment process"
            )

            # Combine results
            message = (
                f"HR Case Triage:\n\n"
                f"1. Severity Classification: {severity_check.get('message', 'No information available')}\n"
                f"2. Category Guidelines: {category_policy.get('message', 'No information available')}\n"
                f"3. Assignment Process: {assignment_procedure.get('message', 'No information available')}\n\n"
                "Recommendation: Cases are assigned to appropriate HR specialists based on severity and category."
            )

            return {
                "status": "ok",
                "message": message,
                "citations": severity_check.get("citations", []) +
                           category_policy.get("citations", []) +
                           assignment_procedure.get("citations", []),
                "workflow_step": "hr_case_triage"
            }

        except Exception as e:
            logger.error(f"HR case triage workflow failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to process HR case triage: {str(e)}",
                "workflow_step": "hr_case_triage"
            }

# Initialize global workflows
workflows = HRWorkflows()