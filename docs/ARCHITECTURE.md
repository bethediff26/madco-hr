# MadCo HR Assistant - System Architecture

## 1. High-Level Architecture Overview

The MadCo HR Policy & Workflow Assistant is an agentic system that combines Retrieval-Augmented Generation (RAG) with Model Context Protocol (MCP) tool orchestration. It is designed with clean architectural boundaries to ensure modularity, low memory consumption (free-tier friendly), and high operational visibility.

```
┌────────────────────────────────────────────────────────────────────────┐
│                          Web Tier (app.py)                             │
│       Flask Web Application & Interactive UI with Demo Buttons         │
│          Endpoints: / (UI), /chat (Query API), /health (Status)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 Agent Orchestrator (agent/orchestrator.py)             │
│   • Intent Classification & Multi-step Workflow Routing                │
│   • State Management & Trace Logging (AgentTrace)                      │
│   • Safety Guardrails & Fallbacks                                      │
└──────────────────┬────────────────────────────────┬────────────────────┘
                   │                                │
                   ▼                                ▼
┌────────────────────────────────────┐ ┌─────────────────────────────────┐
│     Pure Python RAG Subsystem      │ │    Model Context Protocol (MCP) │
│       (rag/retrieval.py)           │ │        (hr_mcp/server.py)       │
│ • TF-IDF / BM25 In-Memory Store    │ │ FastMCP Server exposing tools:  │
│ • Targeted Document Query Routing  │ │  • get_employee                 │
│ • Grounded Policy Citations        │ │  • get_pto_balance              │
│ • Hallucination Defense Guardrail  │ │  • get_benefits                 │
│                                    │ │  • search_policies              │
│  Data Source: data/policies/       │ │  • check_policy_compliance      │
│  (*.md, *.pdf)                     │ │  • create_mock_hr_ticket        │
│                                    │ │  • draft_hr_email               │
│                                    │ │ Data: data/mock_data/*.json     │
└────────────────────────────────────┘ └─────────────────────────────────┘
```

---

## 2. Component Separation & Responsibilities

### 2.1 Web Layer (`app.py`, `wsgi.py`)
- **Framework**: Lightweight Flask application with zero external JavaScript framework dependencies.
- **UI**: Embedded responsive web client providing real-time chat, clickable agentic demo workflow buttons, status connectivity indicators, and grounded policy citation display.
- **API Surface**:
  - `GET /`: Renders the chat dashboard.
  - `POST /chat`: Receives `{"query": "..."}`, extracts context, executes orchestrator workflow, and returns structured response `{ status, message, citations, trace }`.
  - `GET /health`: Pre-checks MCP connectivity and returns service status.
- **WSGI Production Server**: `wsgi.py` exposes `app` for Gunicorn on production platforms like Render.

### 2.2 Agent Orchestrator (`agent/orchestrator.py`)
- **Intent Recognition**: Analyzes natural language queries to detect employee IDs (`EMP-xxx`), policy domains, and action verbs.
- **Workflow State Machine**: Routes requests to dedicated multi-step workflows:
  1. `employee_profile`: Formatted employee profile lookup.
  2. `pto_request_guidance`: Employee balance lookup + policy verification + Workday guidance.
  3. `remote_work_eligibility`: Role verification + state/international duration limits + policy compliance.
  4. `draft_hr_email`: Manager/employee resolution + tailored email draft + policy citations.
  5. `create_hr_ticket`: Mock ticket generation with priority and summary.
  6. `benefits_question_handling`: Employee benefits status lookup + plan guidance.
  7. `expense_compliance`: Spending limits and reimbursement approval tiers.
  8. `hr_case_triage`: Harassment, discrimination, ethics, and security incident escalation.
  9. `policy_search`: Direct RAG query for general policy questions.
- **Operational Traceability**: Generates an `AgentTrace` object capturing `tools_selected`, `tool_arguments`, `tool_outputs`, `retrieved_sources`, `final_basis`, and `escalation_decision`.

### 2.3 Model Context Protocol (MCP) (`hr_mcp/server.py`, `hr_mcp/client.py`)
- Built using Anthropic's `FastMCP` protocol.
- Client communicates in-process or via JSON-RPC.
- Exposes 7 tools:
  - `get_employee(employee_id)`: Profile attributes, role, manager ID, location.
  - `get_pto_balance(employee_id)`: Available, used, and accrued PTO days.
  - `get_benefits(employee_id)`: Enrolled health, dental, vision, and retirement plans.
  - `search_policies(query)`: Grounded policy search via RAG integration.
  - `check_policy_compliance(request_type, employee_id, request_data)`: Verifies request compliance against rules.
  - `create_mock_hr_ticket(ticket_type, summary, details, assignee_id, priority)`: Issues trackable HR ticket.
  - `draft_hr_email(email_type, recipient_name, template_data)`: Drafts structured, policy-grounded emails.

### 2.4 Pure Python RAG Subsystem (`rag/retrieval.py`, `rag/parser.py`)
- **Design Philosophy**: Zero C-extensions (`chromadb`, `onnxruntime`, `hnswlib` eliminated) to guarantee 100% compatibility with virtualized cloud environments (e.g. Render, Linux containers without AVX instruction support).
- **Indexing Engine**: `PurePythonPolicyStore` parses Markdown and PDF documents into sliding-window text chunks.
- **Targeted Query Routing**: Dynamically filters documents based on domain keywords (e.g., equipment queries route specifically to `equipment_policy.md`, PTO to `pto.md`) with stop-word suppression.
- **Guardrails**: Rejects out-of-corpus queries (e.g. general trivia, coding questions) with a polite refusal and empty citations.
- **Performance**: Pre-warms in `< 0.05 seconds` on server startup; RAM usage is `< 80MB`.

### 2.5 Mock Data Store (`data/mock_data/`)
- Structured JSON repositories:
  - `employees.json`: Core directory with roles, departments, locations, and manager linkages.
  - `employees_extended.json`: Employment type and active/leave status.
  - `pto_balances.json`: Detailed available, used, and accrued PTO balances.
  - `benefits.json`: Benefits enrollment records.
