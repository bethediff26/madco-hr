# Design and Evaluation Document: MadCo HR Policy & Workflow Assistant

---

## 1. System Architecture Overview

The MadCo HR Assistant is an agentic, production-grade AI system that unifies **Grounded Policy RAG** and **Model Context Protocol (MCP)** tool orchestration. It is designed to handle complex, multi-step employee HR inquiries, enforce policy compliance, prevent hallucinations, and operate efficiently within cloud free tiers (e.g., Render, Railway) with zero-cost cold starts.

```
                                 ┌────────────────────────┐
                                 │     User / Browser     │
                                 └───────────┬────────────┘
                                             │ HTTP (/, /chat, /health)
                                             ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   Web Application Layer                                │
│  • app.py (Flask application with embedded responsive UI and one-click demo workflows) │
│  • wsgi.py (Production WSGI interface for Gunicorn)                                    │
└────────────────────────────────────────────┬───────────────────────────────────────────┘
                                             │
                                             ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Agent Orchestrator (agent/orchestrator.py)                      │
│  • Intent Classification: Regex + token matching for employee IDs and action verbs     │
│  • Multi-Step Workflow Router: State machine executing targeted workflows              │
│  • Operational Tracing: AgentTrace recording tools, arguments, outputs, and citations  │
│  • Safety Guardrails & Fallback Handlers                                               │
└──────────────────┬─────────────────────────────────────────────────┬───────────────────┘
                   │                                                 │
                   ▼                                                 ▼
┌──────────────────────────────────────────────┐ ┌───────────────────────────────────────┐
│          Pure Python RAG Subsystem           │ │      Model Context Protocol (MCP)     │
│             (rag/retrieval.py)               │ │           (hr_mcp/server.py)          │
│ • PurePythonPolicyStore (BM25 / TF-IDF)      │ │ FastMCP Server exposing 7 tools:      │
│ • Parser & Sliding-Window Chunker            │ │  1. get_employee                      │
│ • Targeted Document Query Routing            │ │  2. get_pto_balance                   │
│ • Out-of-Corpus Refusal Guardrail            │ │  3. get_benefits                      │
│ • Grounded Policy Citations                  │ │  4. search_policies                   │
│                                              │ │  5. check_policy_compliance           │
│ Policy Documents: data/policies/*.md, *.pdf  │ │  6. create_mock_hr_ticket             │
│                                              │ │  7. draft_hr_email                    │
│                                              │ │ Mock Data: data/mock_data/*.json      │
└──────────────────────────────────────────────┘ └───────────────────────────────────────┘
```

---

## 2. RAG Design & Retrieval Engine

### 2.1 Pure Python In-Memory Index (`PurePythonPolicyStore`)
- **Motivation**: Heavy vector stores (`chromadb`, `onnxruntime`, `hnswlib`) rely on compiled C-extensions requiring AVX2 CPU instructions. On virtualized container platforms (like Render's free tier), these frequently trigger unrecoverable `SIGILL (illegal instruction) status 132` crashes and consume >450MB RAM.
- **Solution**: We implemented `PurePythonPolicyStore` using 100% standard Python and lightweight NumPy.
- **Performance**:
  - Memory Footprint: **~65MB** (well under Render's 512MB limit).
  - Indexing Speed: Indexes all policy documents into 43 chunks in **0.02 seconds** at server boot.
  - Query Latency: **< 5ms** retrieval time.

### 2.2 Document Ingestion & Chunking (`rag/parser.py`)
- Ingests Markdown (`.md`) and PDF (`.pdf`) policy manuals from `data/policies/`.
- Chunks text using a sliding window approach with overlapping boundaries to preserve inter-sentence context across headers, subheaders, and tabular policies.

### 2.3 Targeted Query Routing & Stopword Filtering
- Inspects query tokens to route queries to domain-specific files (e.g., queries about equipment/laptops strictly prioritize `equipment_policy.md`; queries about PTO prioritize `pto.md`).
- Filters common conversational noise and stopwords to eliminate false-positive cross-document bleeding.

---

## 3. MCP Server Design & Tool Schemas

The MCP server is implemented in `hr_mcp/server.py` using Anthropic's **FastMCP** protocol, providing standardized tool definitions, input validation schemas, and structured JSON output.

### Tool Schemas

#### 1. `get_employee`
- **Description**: Look up an employee's profile by ID.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "employee_id": { "type": "string", "description": "Employee ID (e.g. EMP-101)" }
    },
    "required": ["employee_id"]
  }
  ```
- **Output Schema**: Returns JSON object with `name`, `department`, `position`, `location`, `manager_id`, `employment_type`, `status`, `remote_work_eligible`, `pto_balance`, `benefits`.

#### 2. `get_pto_balance`
- **Description**: Check current PTO balance and leave status.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "employee_id": { "type": "string", "description": "Employee ID" }
    },
    "required": ["employee_id"]
  }
  ```
- **Output Schema**: Returns `{ "available_days": int, "used_days": int, "accrued_days": int }`.

#### 3. `get_benefits`
- **Description**: Retrieve active benefits and enrollment options.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "employee_id": { "type": "string", "description": "Employee ID" }
    },
    "required": ["employee_id"]
  }
  ```
- **Output Schema**: Returns `{ "benefits": ["health", "dental", "vision", "401k"] }`.

#### 4. `search_policies`
- **Description**: Query company HR policies and return relevant passages with citations.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "Natural language policy query" }
    },
    "required": ["query"]
  }
  ```
- **Output Schema**: Returns `{ "status": "ok", "message": string, "citations": string[] }`.

#### 5. `check_policy_compliance`
- **Description**: Validate an employee action or request against policy constraints.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "request_type": { "type": "string", "enum": ["pto", "remote_work", "expense"] },
      "employee_id": { "type": "string" },
      "request_data": { "type": "object" }
    },
    "required": ["request_type", "employee_id"]
  }
  ```
- **Output Schema**: Returns `{ "is_compliant": bool, "compliance_issues": string[], "recommendations": string[], "policy_reference": string }`.

#### 6. `create_mock_hr_ticket`
- **Description**: Create and track a formal HR support ticket.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "ticket_type": { "type": "string" },
      "summary": { "type": "string" },
      "details": { "type": "string" },
      "assignee_id": { "type": "string" },
      "priority": { "type": "string", "enum": ["low", "medium", "high", "urgent"] }
    },
    "required": ["ticket_type", "summary"]
  }
  ```
- **Output Schema**: Returns `{ "ticket_id": string, "status": "open", "assignee_id": string, "priority": string }`.

#### 7. `draft_hr_email`
- **Description**: Draft an HR email template addressed to employees or managers.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "email_type": { "type": "string" },
      "recipient_name": { "type": "string" },
      "template_data": { "type": "object" }
    },
    "required": ["email_type", "recipient_name"]
  }
  ```
- **Output Schema**: Returns `{ "subject": string, "body": string, "template_used": string }`.

---

## 4. Agent Orchestration & State Machine

The orchestrator (`agent/orchestrator.py`) manages conversational state, intent interpretation, tool selection, and execution flow:

1. **Intent Interpretation (`interpret_user_intent`)**:
   - Parses the query for employee IDs (`EMP-\d+`), policy domains, and multi-step action indicators.
2. **Workflow Decision (`decide_workflow`)**:
   - Matches intent against defined workflow types (`employee_profile`, `pto_request_guidance`, `remote_work_eligibility`, `draft_hr_email`, `create_hr_ticket`, `benefits_question_handling`, `expense_compliance`, `hr_case_triage`, `policy_search`).
3. **Multi-Step Execution**:
   - Executes multi-tool sequences (e.g. `lookup_employee_profile` $\to$ `search_policies` $\to$ `check_policy_compliance` $\to$ `create_mock_hr_ticket`).
4. **Operational Traceability (`AgentTrace`)**:
   - Every execution constructs an `AgentTrace` capturing:
     - `user_intent`: Original query
     - `tools_selected`: Array of tool names called
     - `tool_arguments`: Parameters passed to each tool
     - `tool_outputs`: Data returned by each tool
     - `retrieved_sources`: Policy documents cited
     - `final_basis`: Reasoning foundation
     - `escalation_decision`: Escalation flags for safety cases

---

## 5. Safety Guardrails & Hallucination Defense

1. **Out-of-Corpus Refusal Guardrail**:
   - When a user asks questions unrelated to company HR policies (e.g. general knowledge, baking recipes, coding problems), the system detects zero similarity to indexed policy sources and returns a polite refusal:
     > *"I am unable to find relevant company policy information to answer your question."*
   - Returns empty citations `[]` to prevent false citations.
2. **Defensible Citations**:
   - Citations are strictly generated from policy files that were directly retrieved and evaluated by the RAG engine.
3. **HR Case Triage & Safety Escalation**:
   - Harassment, discrimination, retaliation, and data security breach queries trigger automated escalation paths with designated HR contact channels rather than speculative advice.

---

## 6. Deployment Architecture & Choices

- **Hosting Platform**: Render Free Web Service (or Railway / AWS App Runner).
- **Runtime**: Python 3.12 with Gunicorn WSGI (`gunicorn wsgi:app --workers 1 --threads 4`).
- **Memory Footprint**: ~65MB total consumption (well below Render's 512MB free tier cap).
- **Cold-Start Handling**:
  - The server pre-warms the policy store and orchestrator on startup (`app.py:269-274`).
  - Indexing executes in **0.02s**, allowing container spin-up to complete cleanly within seconds.
- **Health Monitoring**: Dedicated `/health` endpoint validates MCP server readiness and responds with HTTP 200.

---

## 7. Evaluation Benchmark & Results

The system is evaluated against an automated benchmark suite (`evaluation/eval_benchmark.py`) testing 8 scenarios across 6 core metrics:
1. **Groundedness**: Accuracy of facts based on policy sources.
2. **Citation Accuracy**: Valid policy document citations.
3. **Tool Selection Accuracy**: Correct MCP tools invoked based on user intent.
4. **Workflow Completion**: Successful end-to-end task completion.
5. **Safety Compliance**: Safe escalation and zero hallucinations.
6. **Latency**: End-to-end processing duration.

### Benchmark Results Table

| Case ID | Scenario / Query Category | Latency | Groundedness | Tool Accuracy | Task Completion | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **CASE-01** | PTO Balance & Workday Request Guidance | 0.15s | 100% | 100% | 100% | ✅ PASS |
| **CASE-02** | Remote Work Cross-State Eligibility | 0.01s | 100% | 100% | 100% | ✅ PASS |
| **CASE-03** | Benefits Triage & Plan Status | 0.00s | 100% | 100% | 100% | ✅ PASS |
| **CASE-04** | Expense Reimbursement & Equipment Limits | 0.00s | 100% | 100% | 100% | ✅ PASS |
| **CASE-05** | Workplace Harassment & Retaliation Triage | 0.00s | 100% | 100% | 100% | ✅ PASS |
| **CASE-06** | Data Security Incident & Lost Hardware Escalation | 0.00s | 100% | 100% | 100% | ✅ PASS |
| **CASE-07** | Company Paid Holidays Policy Query | 0.00s | 100% | 100% | 100% | ✅ PASS |
| **CASE-08** | Paid Parental Leave Eligibility & Duration | 0.00s | 100% | 100% | 100% | ✅ PASS |

### Overall Metric Summary
- **Overall Pass Rate:** **100.0%**
- **Groundedness Rate:** **100.0%**
- **Tool Selection Accuracy:** **100.0%**
- **Task Completion Rate:** **100.0%**
- **Safety & Guardrail Compliance:** **100.0%**
- **Average End-to-End Latency:** **0.021s**
