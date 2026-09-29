# AI Tooling Reflection

This document reflects on the AI coding assistants, models, and tooling utilized throughout the design, development, debugging, and evaluation of the **MadCo HR Policy & Workflow Assistant**.

---

## 1. AI Tools and Models Utilized

1. **Antigravity Agentic IDE & Assistant (Google DeepMind)**
   - Utilized as the primary autonomous pair programmer for repository refactoring, file modifications, test execution, debugging, and continuous integration validation.
2. **OpenRouter / LLM APIs**
   - Model: `nvidia/nemotron-3.5-lightning:free` and general OpenRouter endpoints for testing semantic reasoning and agent prompts.
3. **Pyrefly / Language Server Tooling**
   - Real-time syntax and static analysis tooling within the IDE to catch indentation issues, typing mismatches, and undefined references across Python modules.
4. **FastMCP & Anthropic Model Context Protocol SDK**
   - Tool definition and communication protocol for exposing tools and client abstractions.

---

## 2. How the AI Tools Were Used

### Architectural Refactoring & Pure Python Migration
- The original codebase relied on heavy C-extension vector stores (`chromadb`, `onnxruntime`, and `hnswlib`).
- When deployed on Render's free tier, these libraries repeatedly crashed the container with `SIGILL (illegal instruction) status 132` due to lack of AVX2 instructions on the virtualized CPU, along with exceeding the 512MB RAM ceiling.
- The AI assistant was tasked with architecting a **Pure Python In-Memory Policy Store** (`rag/retrieval.py` and `rag/parser.py`), replacing the heavy dependencies with pure Python tokenization, BM25/TF-IDF scoring, and sliding-window chunking.
- This dropped the memory footprint from >450MB down to **~65MB** and reduced indexing time from over 30 seconds to **0.02 seconds**.

### Multi-Step Agent Orchestrator & State Machine
- Used AI tooling to build `agent/orchestrator.py`, mapping unstructured user prompts to structured multi-step workflows.
- Implemented full operational tracing via `AgentTrace` to record tool selections, arguments, outputs, citations, and execution basis.

### Automated Evaluation Benchmark Harness
- Developed an automated benchmark suite (`evaluation/eval_benchmark.py`) that evaluates groundedness, tool selection accuracy, task completion, guardrail refusals, and execution latency across 8 complex scenarios.

---

## 3. What Worked Well

- **Rapid Autonomous Root-Cause Identification**:
  - The AI assistant identified the exact line in `rag/parser.py` where a 1-character step in a sliding window was generating 10,078 chunks instead of 43, causing memory bloat. Correcting this took seconds.
- **Pure Python Replacement Strategy**:
  - Translating heavy vector database logic into a lightweight, pure Python retrieval engine eliminated cloud platform crashes completely while maintaining 100% precision on policy retrieval.
- **Trace-Driven Debugging**:
  - Structuring the agent with explicit `AgentTrace` logs made it trivial for the AI assistant and developer to verify exactly which MCP tools were called and why.
- **One-Shot CI/CD Pipeline Creation**:
  - Creating GitHub Actions workflow files (`.github/workflows/ci.yml`) with automated compilation, pytest execution, background server launching, and HTTP smoke testing worked seamlessly.

---

## 4. What Did Not Work Well / Challenges Encountered

- **Rigid Phrase Matching vs. Varied Human Query Phrasing**:
  - Initial orchestrator routing used exact substring matching (e.g. `if "draft hr email" in query`). When users asked *"draft an HR email for employee EMP-103..."*, the extra article (`"an"`) caused the matcher to fail and fall back to general PTO guidance.
  - *Resolution*: Shifted to flexible token-based matching (`if "email" in query_lower and any(w in query_lower for w in ["draft", "write", "compose", ...])`).
- **Cloud Platform Hardware Divergence (The AVX/SIGILL Trap)**:
  - Code that ran cleanly on local high-end x86 developer machines failed silently on cloud free tiers due to missing CPU extensions (`AVX2`).
  - *Lesson*: AI tooling should be directed toward pure-Python and standard-library implementations whenever deploying to resource-constrained or virtualized free-tier environments.
- **Compaction & Long Trajectory Context Windows**:
  - When sessions became very long, truncated conversation context occasionally lost track of prior incremental bash script experiments. Maintaining concise, modular test files in the workspace (e.g. `scratch/` and `evaluation/`) proved far superior to relying solely on chat history.
