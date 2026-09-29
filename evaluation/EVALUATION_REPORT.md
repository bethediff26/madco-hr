# Agentic HR Assistant - Evaluation Benchmark Report

**Generated:** 2026-09-29 00:28:36 UTC  
**Overall Pass Rate:** 100.0%  
**Average Latency:** 0.024s  

## Metric Summary

| Metric | Score / Result | Description |
| :--- | :--- | :--- |
| **Groundedness Rate** | **100.0%** | Grounded in verified policy sources |
| **Tool Selection Accuracy** | **100.0%** | Appropriate MCP tools selected based on intent |
| **Task Completion Rate** | **95.9%** | End-to-end multi-step task completion |
| **Safety & Guardrail Compliance**| **100%** | Defensible policy escalation, zero hallucinations |
| **Average End-to-End Latency** | **0.024s** | Fast sub-second in-process MCP & RAG retrieval |

## Detailed Test Case Results

| ID | Category | Latency | Groundedness | Tool Accuracy | Completion | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| CASE-01 | PTO Guidance | 0.174s | 100% | 100% | 100% | ✅ PASS |
| CASE-02 | Remote Work Eligibility | 0.005s | 100% | 100% | 100% | ✅ PASS |
| CASE-03 | Benefits Triage | 0.005s | 100% | 100% | 100% | ✅ PASS |
| CASE-04 | Expense Compliance | 0.001s | 100% | 100% | 100% | ✅ PASS |
| CASE-05 | Safety & Harassment Triage | 0.0s | 100% | 100% | 67% | ✅ PASS |
| CASE-06 | Data Security Incident | 0.0s | 100% | 100% | 100% | ✅ PASS |
| CASE-07 | Holiday Policy RAG | 0.003s | 100% | 100% | 100% | ✅ PASS |
| CASE-08 | Parental Leave Policy | 0.0s | 100% | 100% | 100% | ✅ PASS |
