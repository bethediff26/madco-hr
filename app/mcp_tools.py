"""
MadCo HR Assistant MCP Tools
Provides mock data access and policy search capabilities for the HRAgent.
"""

import json
import os
from pathlib import Path
from typing import Any


# Mock data and policy directory path (under data/ subdirectory)
MOCK_DATA_DIR = Path(__file__).parent.parent / "data" / "mock_data"
POLICIES_DIR = Path(__file__).parent.parent / "data" / "policies"


def get_employee(employee_id: str) -> dict:
    """
    Retrieve employee profile information by ID.

    Args:
        employee_id: Unique employee identifier (e.g., "EMP-101")

    Returns:
        Dictionary containing employee information including name, role,
        department, location, and hire date.

    Raises:
        ValueError: If employee ID not found in the database.
    """
    # Load employee data from JSON file
    employees_file = MOCK_DATA_DIR / "employees.json"
    try:
        with open(employees_file, 'r') as f:
            employees = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        raise ValueError(f"Employee ID '{employee_id}' not found")

    # Find employee by ID
    employee = next(
        (emp for emp in employees if emp["employee_id"] == employee_id),
        None
    )

    if employee is None:
        raise ValueError(f"Employee ID '{employee_id}' not found in system")

    extended_employee = employee
    extended_file = MOCK_DATA_DIR / "employees_extended.json"
    try:
        with open(extended_file, 'r') as f:
            extended_employees = json.load(f)
        extended_employee = next(
            (emp for emp in extended_employees if emp["employee_id"] == employee_id),
            employee
        )
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    result = {
        "name": employee["name"],
        "role": employee["role"],
        "department": employee["department"],
        "location": employee["location"],
        "hire_date": employee["hire_date"],
        "tenure_years": _calculate_tenure(employee["hire_date"]),
    }
    for field in ("employment_type", "status"):
        if field in extended_employee:
            result[field] = extended_employee[field]
    return result


def _calculate_tenure(hire_date: str) -> float:
    """Calculate tenure in years from hire date string."""
    from datetime import datetime
    try:
        hire = datetime.strptime(hire_date, "%Y-%m-%d")
        today = datetime(2026, 9, 19)
        days_since_hire = (today - hire).days
        return round(days_since_hire / 365.25, 2)
    except ValueError:
        return 0.0


def get_pto_balance(employee_id: str) -> dict:
    """
    Retrieve PTO balance information for an employee.

    Args:
        employee_id: Unique employee identifier (e.g., "EMP-101")

    Returns:
        Dictionary containing PTO details including annual allocation,
        used days, pending days, and available days.

        If employee ID not found, returns a dictionary with error message
        instead of raising an exception.
    """
    # Load PTO data from JSON file
    pto_file = MOCK_DATA_DIR / "pto_balances.json"
    try:
        with open(pto_file, 'r') as f:
            pto_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"error": f"PTO data not found for employee ID '{employee_id}'"}

    # Find PTO record by employee ID
    record = next(
        (r for r in pto_data if r["employee_id"] == employee_id),
        None
    )

    if record is None:
        return {"error": f"Employee ID '{employee_id}' does not exist"}

    return {
        "employee_id": record["employee_id"],
        "annual_allocation_days": record["annual_allocation_days"],
        "used_days": record["used_days"],
        "pending_days": record["pending_days"],
        "available_days": record["available_days"],
        "utilization_rate": round(record["used_days"] / record["annual_allocation_days"] * 100, 2) if record["annual_allocation_days"] > 0 else 0,
    }


def get_benefits(employee_id: str) -> dict:
    """
    Retrieve benefits coverage information for an employee.

    Args:
        employee_id: Unique employee identifier (e.g., "EMP-101")

    Returns:
        Dictionary containing health insurance tier, dental/vision enrollment,
        401k match percentage, and wellness stipend usage.

    Raises:
        ValueError: If employee ID not found in the database.
    """
    # Load benefits data from JSON file
    benefits_file = MOCK_DATA_DIR / "benefits.json"
    try:
        with open(benefits_file, 'r') as f:
            benefits_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        raise ValueError(f"Benefits data not found for employee ID '{employee_id}'")

    # Find benefits record by employee ID
    record = next(
        (b for b in benefits_data if b["employee_id"] == employee_id),
        None
    )

    if record is None:
        raise ValueError(f"Benefits data not found for employee ID '{employee_id}'")

    return {
        "employee_id": record["employee_id"],
        "health_plan": record["health_plan"],
        "dental_enrolled": record["dental_enrolled"],
        "vision_enrolled": record["vision_enrolled"],
        "401k_match_percent": record["401k_match_percent"],
        "wellness_stipend_used": record["wellness_stipend_used"],
    }


def search_policies(query: str) -> dict:
    """
    Search policy documents for relevant content based on query.

    Args:
        query: Search query string (supports partial matching)

    Returns:
        Dictionary containing matching policy sections, document titles,
        and source file citations. Matches are ranked by relevance.

    Raises:
        ValueError: If no policies directory found.
    """
    results = {
        "query": query,
        "matches": [],
        "citations": [],
        "total_count": 0,
    }
    query_terms = [term for term in query.lower().split() if term]

    # Check if policies directory exists
    if not POLICIES_DIR.exists():
        raise ValueError("No policy documents found. Ensure policies directory exists.")

    # Read all markdown files from policies directory
    md_files = list(POLICIES_DIR.glob("*.md"))
    results["total_count"] = len(md_files)

    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if query matches any section heading or text content
            lines = content.split('\n')
            matching_lines = []
            policy_title = Path(file_path).stem  # e.g., "pto_policy"

            for i, line in enumerate(lines):
                line_lower = line.lower()
                query_matches = query_terms and all(term in line_lower for term in query_terms)

                # Match section headings (e.g., "## 1. Purpose")
                if line.startswith('## '):
                    heading = line[3:].strip()
                    if query_matches:
                        results["matches"].append({
                            "title": f"{policy_title}: {heading}",
                            "section": heading,
                            "document": str(file_path.relative_to(POLICIES_DIR)),
                            "relevance_score": 1.0,
                        })

                        # Collect a few lines after the heading
                        for j in range(i + 1, min(i + 8, len(lines))):
                            matching_lines.append(lines[j].strip())
                elif query_matches:
                    # Match query terms in policy content outside headings
                    results["matches"].append({
                        "title": f"{policy_title}: {line[:100]}...",
                        "section": None,
                        "document": str(file_path.relative_to(POLICIES_DIR)),
                        "relevance_score": 0.8,
                    })
                    matching_lines.append(line.strip())

            if matching_lines:
                results["matches"].append({
                    "title": policy_title + ": Summary",
                    "section": ", ".join(matching_lines[:5]),
                    "document": str(file_path.relative_to(POLICIES_DIR)),
                    "relevance_score": 0.9,
                })

        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

    # Sort matches by relevance score
    results["matches"] = sorted(results["matches"], key=lambda x: x["relevance_score"], reverse=True)

    # Limit results to top 5 matches
    if len(results["matches"]) > 5:
        results["matches"] = results["matches"][:5]

    seen_documents = set()
    for match in results["matches"]:
        document = match["document"]
        if document not in seen_documents:
            results["citations"].append({
                "document": document,
                "title": match["title"],
                "relevance_score": match["relevance_score"],
            })
            seen_documents.add(document)

    return results


def create_mock_hr_ticket(employee_id: str, issue: str) -> dict:
    """
    Create a mock HR support ticket and return confirmation.

    Args:
        employee_id: Unique employee identifier (e.g., "EMP-101")
        issue: Brief description of the employee's issue

    Returns:
        Dictionary containing ticket confirmation with ticket_id, status,
        and timestamp information.

    Raises:
        ValueError: If employee ID not found or issue is invalid.
    """
    if not issue or not issue.strip():
        raise ValueError("Issue must be provided")

    # Validate employee ID
    try:
        _ = get_employee(employee_id)
    except ValueError:
        raise ValueError(f"Employee ID '{employee_id}' not found")

    # Generate mock ticket ID based on current timestamp and employee ID
    from datetime import datetime

    # Create deterministic ticket ID based on input
    base_numbers = f"{int(employee_id.split('-')[1])}{len(issue)}{datetime.now().year}"
    ticket_num = int(base_numbers[-4:]) + 1000  # Start from TICK-1001

    ticket_id = f"TICK-{ticket_num:04d}"

    return {
        "ticket_id": ticket_id,
        "status": "created",
        "employee_id": employee_id,
        "issue": issue,
        "created_at": datetime.now().isoformat(),
        "assigned_to": "HR Support Team",
    }


def draft_hr_email(recipient: str, subject: str, body: str) -> dict:
    """
    Draft an HR email and return confirmation with the draft details.

    Args:
        recipient: Email address of the recipient
        subject: Email subject line
        body: Email message body

    Returns:
        Dictionary containing status confirmation and the draft object with
        to, subject, and body fields.

    Raises:
        ValueError: If any required parameter is missing or empty.
    """
    # Validate inputs
    recipient = recipient.strip() if isinstance(recipient, str) else recipient
    subject = subject.strip() if isinstance(subject, str) else subject
    body = body.strip() if isinstance(body, str) else body

    if not recipient or not subject or not body:
        raise ValueError("Recipient, subject, and body must be provided")
    if "@" not in recipient or " " in recipient or "." not in recipient.rsplit("@", 1)[-1]:
        raise ValueError("Recipient must be a valid email address")

    return {
        "status": "success",
        "draft": {
            "to": recipient,
            "subject": subject,
            "body": body,
        },
    }
