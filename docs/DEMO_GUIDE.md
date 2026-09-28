# MadCo HR Assistant - Live Demo & Presentation Guide

## 1. Demo Overview

This guide walks through presenting the key capabilities of the MadCo HR Policy & Workflow Assistant in a live demonstration or recording.

---

## 2. Interactive Demo Workflows

The web UI contains pre-configured one-click demo buttons at the top of the interface:

### 🏖️ Demo 1: Multi-Step PTO Request & Manager Guidance
- **Query**:
  > `can you give me the pto balance for employee EMP-101 and guide me on requesting 3 days off next week?`
- **Agentic Workflow**:
  1. Identifies employee `EMP-101` and intent `pto_request_guidance`.
  2. Queries MCP `check_pto_balance` (finds 13 available days).
  3. Evaluates `check_policy_compliance` (verifies 3 days <= 13 available days).
  4. Retrieves policy rules from `pto.md` via RAG (manager approval and Workday process).
  5. Returns guidance with balance, compliance check, and policy citation (`pto.md`).
- **Trace Output**:
  - `tools_selected`: `["search_policies", "check_pto_balance", "check_policy_compliance"]`
  - `citations`: `["pto.md"]`

---

### 🌍 Demo 2: Remote Work Cross-State Eligibility
- **Query**:
  > `can employee EMP-102 work remotely from another state for six weeks?`
- **Agentic Workflow**:
  1. Identifies employee `EMP-102` (Bob Smith) and detects multi-step remote work intent.
  2. Queries MCP `lookup_employee_profile` (Engineering, remote eligible: True).
  3. Retrieves `remote_work_policy.md` section on out-of-state and duration rules.
  4. Evaluates `check_policy_compliance` against policy limits (note: 6 weeks exceeds typical standard thresholds).
  5. Returns clear eligibility guidance, required manager sign-off, and policy citation.
- **Trace Output**:
  - `tools_selected`: `["search_policies", "lookup_employee_profile", "check_policy_compliance"]`
  - `citations`: `["remote_work_policy.md"]`

---

### 💻 Demo 3: Expense Reimbursement Policy
- **Query**:
  > `what is the expense reimbursement limit for home office equipment for EMP-103?`
- **Agentic Workflow**:
  1. Evaluates expense policy inquiry with employee context.
  2. Retrieves `equipment_policy.md` and expense guidance.
  3. Returns precise dollar thresholds, approval workflows, and receipt retention guidelines.
- **Trace Output**:
  - `citations`: `["equipment_policy.md"]`

---

### ✉️ Demo 4: Tailored HR Email Drafting
- **Query**:
  > `draft an HR email for employee EMP-103 requesting PTO approval from manager`
- **Agentic Workflow**:
  1. Detects `draft_hr_email` intent and extracts `EMP-103` (Charlie Brown).
  2. Looks up manager via MCP `get_employee` (identifies manager `EMP-105`: Eve White).
  3. Retrieves PTO balance (10 days) and invokes MCP `draft_hr_email`.
  4. Produces a professionally formatted email draft with Subject, Sender, Recipient, and Workday compliance guidance.
- **Trace Output**:
  - `tools_selected`: `["get_employee", "draft_hr_email"]`
  - `citations`: `["pto.md"]`

---

### 🎫 Demo 5: Mock HR Ticket Creation
- **Query**:
  > `create a mock hr ticket for laptop replacement for EMP-101`
- **Agentic Workflow**:
  1. Routes to `create_hr_ticket`.
  2. Invokes MCP `create_mock_hr_ticket` with type `hardware_request`, assignee `EMP-101`, and summary.
  3. Returns a trackable mock ticket ID with status and assignee details.

---

### 🛡️ Demo 6: Safety Guardrails & Out-of-Corpus Refusal
- **Query**:
  > `how do I bake a chocolate cake?`
- **Agentic Workflow**:
  1. Runs guardrail filter in RAG retrieval.
  2. Detects query is out-of-corpus with zero relevant policy matches.
  3. Politely refuses to hallucinate and returns empty citations:
     > *"I am unable to find relevant company policy information to answer your question."*
- **Trace Output**:
  - `citations`: `[]`

---

## 3. Architecture & Operational Visibility Presentation Points

When explaining the system in a demo:
1. **Explain the MCP Tool Protocol**: Highlight how tools are cleanly defined as FastMCP tools and executed with schema validation.
2. **Show the Trace Object**: Show that every request records `tools_selected`, `tool_arguments`, and `final_basis` for auditability.
3. **Point out the Grounded Citations**: Explain that responses only cite files actually retrieved, preventing hallucination.
4. **Demonstrate Ultra-Fast Latency**: Show that responses return in milliseconds thanks to the in-memory pure Python architecture.
