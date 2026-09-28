# MadCo HR Policy & Workflow Assistant

An agentic, production-grade HR assistant that unifies **Grounded Policy RAG** and **Model Context Protocol (MCP)** tool orchestration. Designed for deployment on cloud free tiers (e.g. Render, Railway) with zero-cost cold starts, defensible guardrails, and full operational traceability.

---

## 🌟 Key Capabilities & Requirements Matrix

| Requirement | Implementation Details | Verification |
| :--- | :--- | :--- |
| **Grounded Policy RAG** | High-precision retrieval over Markdown & PDF policy documents with exact citations (`pto.md`, `remote_work_policy.md`, `equipment_policy.md`). | `test_rag_guardrails.py` |
| **MCP Integration** | FastMCP server exposing 7 tools (`get_employee`, `get_pto_balance`, `get_benefits`, `search_policies`, `check_policy_compliance`, `create_mock_hr_ticket`, `draft_hr_email`). Operational traces (`AgentTrace`) log every tool call. | `test_mcp_integration.py` |
| **End-to-End Agentic Tasks** | Multi-step workflows for PTO approval guidance, cross-state remote work eligibility, benefits triage, email drafting, and ticket creation. | One-click UI buttons & `app.py` |
| **Robust RAG Guardrails** | Out-of-corpus defense refuses to hallucinate and yields empty citations; targeted keyword routing suppresses noise. | `test_rag_guardrails.py` |
| **Modular Architecture** | Clean separation of Web App, Agent Orchestrator, MCP Client/Server, Pure Python RAG, and Mock Data. | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| **Free-Tier Deployment** | Pure Python implementation (<80MB RAM footprint, no C-extensions) eliminates Render AVX SIGILL 132 crashes and cold-start timeouts. | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) |
| **CI/CD Automation** | GitHub Actions pipeline runs on push/PR with compilation checks, MCP integration tests, app startup checks, and endpoint smoke tests. | `.github/workflows/ci.yml` |
| **Comprehensive Evaluation** | 100% pass rate across 8 benchmark scenarios testing Groundedness, Tool Accuracy, Completion, Safety, and Latency. | [evaluation/EVALUATION_REPORT.md](evaluation/EVALUATION_REPORT.md) |
| **Design & Demo Docs** | Full architectural guides, live presentation scripts, and sample workflows. | [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) |

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Flask Web Client (app.py)                       │
│    Endpoints: / (UI), /chat (Query API), /health (Readiness Status)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                Agent Orchestrator (agent/orchestrator.py)              │
│    • Intent Classification & Multi-Step Routing                        │
│    • State Machine Execution & Operational Trace Logging               │
└──────────────────┬────────────────────────────────┬────────────────────┘
                   │                                │
                   ▼                                ▼
┌────────────────────────────────────┐ ┌─────────────────────────────────┐
│     Pure Python RAG Subsystem      │ │   Model Context Protocol (MCP)  │
│        (rag/retrieval.py)          │ │       (hr_mcp/server.py)        │
│ • TF-IDF / BM25 In-Memory Store    │ │ FastMCP Server with tools:      │
│ • Targeted Document Query Routing  │ │  • get_employee                 │
│ • Grounded Policy Citations        │ │  • get_pto_balance              │
│ • Out-of-Corpus Refusal Guardrail  │ │  • get_benefits                 │
│                                    │ │  • search_policies              │
│ Policies: data/policies/           │ │  • check_policy_compliance      │
│ (*.md, *.pdf)                      │ │  • create_mock_hr_ticket        │
│                                    │ │  • draft_hr_email               │
└────────────────────────────────────┘ └─────────────────────────────────┘
```

For complete details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 🚀 Quickstart & Local Execution

### 1. Installation
```bash
git clone https://github.com/bethediff26/madco-hr.git
cd madco-hr
pip install -r requirements.txt
```

### 2. Run the Web Application
```bash
python app.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser.

### 3. Run with Gunicorn (Production)
```bash
gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 1 --threads 4
```

---

## 🧪 Testing & Evaluation

### Run Test Suite
```bash
# Run all unit and integration tests
python -m pytest test_mcp_integration.py test_rag_guardrails.py test_agent_orchestrator.py -v
```

### Run Evaluation Benchmark
```bash
python evaluation/eval_benchmark.py
```

**Benchmark Results:**
- **Overall Pass Rate:** 100.0%
- **Groundedness Rate:** 100.0%
- **Tool Selection Accuracy:** 100.0%
- **Task Completion Rate:** 95.9%
- **Safety & Guardrail Compliance:** 100.0%
- **Average Latency:** 0.023s

See [evaluation/EVALUATION_REPORT.md](evaluation/EVALUATION_REPORT.md) for individual scenario metrics.

---

## 🌐 Cloud Deployment (Render / Railway)

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --threads 4`
- **Health Check Path:** `/health`
- **Memory Footprint:** ~65MB (well below Render's 512MB free tier limit)
- **Cold Start Time:** < 2.5 seconds (in-memory index pre-warms in 0.02s)

Detailed deployment configuration is available in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## 🎬 Live Demo Workflows

The web UI provides one-click demo buttons for primary agentic workflows:
1. **🏖️ Task 1: PTO Balance & Request (EMP-101)**: Multi-step balance check, policy verification, and Workday submission instructions.
2. **🌍 Task 2: Remote Work Eligibility (EMP-102)**: Cross-state remote work evaluation, duration threshold checks, and manager sign-off guidance.
3. **💻 Task 3: Expense Policy (EMP-103)**: Home office stipend limits, receipt requirements, and approval tiers.
4. **✉️ Task 4: Tailored Manager Email**: Formulates manager approval emails citing current balances and Workday steps.
5. **🎫 Task 5: Mock HR Ticket Creation**: Direct ticket generation with category, priority, and summary.

For the full demo presentation script, see [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md).