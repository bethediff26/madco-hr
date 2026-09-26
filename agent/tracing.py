"""
Agent Tracing and Logging for Operational Visibility.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class AgentTrace:
    """Detailed trace of agent reasoning steps for operational visibility."""

    timestamp: str
    user_query: str
    workflow_type: str
    tools_selected: List[str]
    tool_arguments: List[Dict[str, Any]]
    tool_outputs: List[Dict[str, Any]]
    retrieved_sources: List[Dict[str, Any]]
    final_basis: str
    escalation_decision: Optional[str] = None
    status: str = "success"
    error_message: Optional[str] = None

class AgentTracer:
    """Handles tracing and logging of agent operations."""

    def __init__(self):
        self.traces: List[AgentTrace] = []

    def log_trace(self, trace: AgentTrace) -> None:
        """Log a trace entry."""
        self.traces.append(trace)
        logger.info(f"Agent Trace - Workflow: {trace.workflow_type}, Query: {trace.user_query[:50]}...")

    def get_latest_trace(self) -> Optional[AgentTrace]:
        """Get the most recent trace."""
        return self.traces[-1] if self.traces else None

    def format_trace_for_display(self, trace: AgentTrace) -> str:
        """Format trace for user display or logging."""
        formatted = f"""
=== Agent Operation Trace ===
Timestamp: {trace.timestamp}
User Query: {trace.user_query}
Workflow Type: {trace.workflow_type}
Status: {trace.status}
Final Basis: {trace.final_basis}

Tools Selected:
"""
        for i, tool in enumerate(trace.tools_selected):
            formatted += f"  {i+1}. {tool}\n"

        formatted += "\nRetrieved Sources:\n"
        for i, source in enumerate(trace.retrieved_sources[:3]):  # Limit to first 3
            formatted += f"  {i+1}. {source.get('doc_title', 'Unknown')} - {source.get('section', 'Unknown')}\n"

        if trace.escalation_decision:
            formatted += f"\nEscalation Decision: {trace.escalation_decision}\n"

        if trace.error_message:
            formatted += f"\nError: {trace.error_message}\n"

        formatted += "=============================\n"
        return formatted

    def export_traces(self, filename: str = None) -> str:
        """Export all traces to JSON format."""
        trace_data = [asdict(trace) for trace in self.traces]
        json_data = json.dumps(trace_data, indent=2, default=str)

        if filename:
            with open(filename, 'w') as f:
                f.write(json_data)

        return json_data

# Initialize global tracer
tracer = AgentTracer()