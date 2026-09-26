---
name: hr-ticket-creation-tool
description: New HR ticket creation MCP tool for employee support requests and issue tracking
metadata:
  type: project
---

The `create_mock_hr_ticket` function creates new HR support tickets in a mock database. It generates unique ticket IDs (e.g., TICK-XXXX), records the issue type, details, and initial "Open" status. Tickets are persisted to `data/mock_data/tickets.json`. The tool is registered as an MCP endpoint for use with the HRAssistant MCP server.

**Usage:**
```python
create_mock_hr_ticket("EMP-101", "PTO request", "Need to take sick leave next week")
# Returns: {
#   "ticket_id": "TICK-3847",
#   "status": "Open",
#   "message": "Ticket created successfully! Ticket ID: TICK-3847",
#   "employee_id": "EMP-101",
#   "issue_type": "PTO request",
#   "details": "Need to take sick leave next week"
# }
```

**Storage:**
- File: `data/mock_data/tickets.json` (stores ticket records)
- Each ticket has fields: ticket_id, employee_id, issue_type, details, status, created_at
