"""
MadCo HR Assistant Agent
Provides agent-based tools for HR operations and employee assistance.
"""

import json
import logging
import time
import asyncio
from app.prompts import AGENT_SYSTEM_PROMPT
from app.ollama_client import LLMClient
from hr_mcp.client import mcp_client


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """Bridge the synchronous legacy agent API to the real MCP client."""
    async def invoke():
        try:
            await mcp_client.connect()
            return await mcp_client.call_tool(tool_name, arguments)
        finally:
            await mcp_client.disconnect()

    return asyncio.run(invoke())


def _get_employee(employee_id: str) -> dict:
    return _call_mcp_tool("lookup_employee_profile", {"employee_id": employee_id})


def _get_pto_balance(employee_id: str) -> dict:
    return _call_mcp_tool("check_pto_balance", {"employee_id": employee_id})


def _get_benefits(employee_id: str) -> dict:
    return _call_mcp_tool("lookup_benefits_status", {"employee_id": employee_id})


def _search_policies(query: str) -> dict:
    return _call_mcp_tool("search_policy_documents", {"query": query, "limit": 5})


def _create_mock_hr_ticket(employee_id: str, issue: str) -> dict:
    return _call_mcp_tool("create_mock_hr_ticket", {
        "ticket_type": "hr_request",
        "summary": issue,
        "details": issue,
        "assignee_id": employee_id,
    })


def _draft_hr_email(recipient: str, subject: str, body: str) -> dict:
    return _call_mcp_tool("draft_hr_email", {
        "email_type": "custom",
        "recipient_name": recipient,
        "template_data": {"subject": subject, "body": body},
    })


class HRAgent:
    """
    HR Agent that interacts with employee data and policy resources.

    The agent will:
    - Access employee information through MCP tools
    - Look up PTO balances and benefits eligibility
    - Search company policies with citations
    - Draft emails and create mock tickets when needed
    """

    def __init__(self):
        """Initialize the HR Agent with LLMClient and tool mappings."""
        self.client = None  # Will be initialized during run() to save memory

        # Tool mapping dictionary for the agent to call
        self.tools = {
            'get_employee': _get_employee,
            'get_pto_balance': _get_pto_balance,
            'get_benefits': _get_benefits,
            'search_policies': _search_policies,
            'create_mock_hr_ticket': _create_mock_hr_ticket,
            'draft_hr_email': _draft_hr_email,
        }

        logger.info("HRAgent initialized with 6 available tools")

    def run(self, user_query: str, max_iterations: int = 3) -> dict:
        """
        Execute the main reasoning loop for the HR agent.

        Args:
            user_query: The user's question or task
            max_iterations: Maximum number of iterations/tool calls before giving up

        Returns:
            Dictionary containing final response and operational traces
        """
        # Initialize client if not already done (to save memory at startup)
        if self.client is None:
            from app.ollama_client import LLMClient
            self.client = LLMClient()

        # System prompt defining available tools
        def get_tool_desc(name):
            desc = self.tools[name].__doc__.strip().replace('\n', ' ') if self.tools[name].__doc__ else f"Function: {name}"
            return f"{name}: {desc}"

        tools_str = "\n".join([get_tool_desc(name) for name in self.tools])
        # Use str.replace instead of .format() because AGENT_SYSTEM_PROMPT contains literal quotes {"tool"...}
        # that confuse the .format() parser when it tries to find format specifiers
        system_prompt = AGENT_SYSTEM_PROMPT.replace('{tools}', tools_str)

        # Add explicit instruction to always output tool calls for specific queries
        system_prompt += "\n\nIMPORTANT: For any query that requires specific employee data, PTO information, benefits details, or policy searches, you MUST immediately call the appropriate tool(s) using the JSON format. Do not provide conversational filler responses."

        # Add an additional constraint to make tool calling mandatory for specific queries
        system_prompt += "\n\nCRITICAL: If a query requires information from one of the available tools (employee details, PTO balance, benefits info, or policy searches), you MUST output a JSON tool call. You cannot respond with general statements or greetings."

        # Add strict enforcement rule to prevent any conversational text
        system_prompt += "\n\nSTRICT RULE: You must never output any conversational filler text (like 'I'm ready to help', 'Let me assist you', etc.). Your entire response must be either a JSON tool call or a direct answer to the query."

        # Add explicit enforcement for tool calling when data is required
        system_prompt += "\n\nENFORCEMENT: If your previous response contained only conversational text and no valid JSON tool call, you will be penalized. You must output valid JSON tool calls immediately when specific data is required."

        # Add specific examples to help the LLM understand tool usage patterns
        system_prompt += "\n\nEXAMPLES:"
        system_prompt += "\n- 'What is the PTO balance for employee EMP-101?' → {'tool': 'get_pto_balance', 'arguments': {'employee_id': 'EMP-101'}}"
        system_prompt += "\n- 'What are the benefits for part-time employees?' → {'tool': 'get_benefits', 'arguments': {'employee_type': 'part-time'}}"
        system_prompt += "\n- 'What is the PTO policy for full-time employees?' → {'tool': 'search_policies', 'arguments': {'query': 'full-time employees PTO policy'}}"
        system_prompt += "\n- 'Can you help me with my benefits enrollment?' → {'tool': 'search_policies', 'arguments': {'query': 'benefits enrollment'}}"

        # Initialize conversation history with system prompt
        messages = [{"role": "system", "content": system_prompt}]

        # Track traces for step-by-step recording
        traces = []

        iteration = 0
        last_tool_call = None
        last_tool_key = None  # Track the last tool call to avoid re-executing same tool with same args

        while iteration < max_iterations:
            iteration += 1

            # Prepare the full prompt from conversation history
            prompt = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in messages])

            logger.info(f"--- Iteration {iteration} ---")
            logger.info(f"Prompt: {prompt[:200]}...")

            # Generate response from LLM (without passing system_prompt as second arg since it's already in messages)
            # Note: generate_response doesn't accept system_prompt param - removed to avoid errors
            response = self.client.generate_response(prompt)

            logger.info(f"LLM Response: {response[:200]}...")

            # Strictly enforce that responses containing only conversational text are rejected
            # Clean the response to check for pure conversational text
            cleaned_response = response.strip()

            # Check if response is just conversational filler (without any JSON tool call)
            if cleaned_response.lower() in ["i'm ready to help", "i'm here to assist", "hello", "hi", "hey", "good day", "how can i help", "what can i do for you", "i'd be happy to help", "let me assist you"]:
                logger.warning("Response contained only conversational text - treating as invalid")
                # Return an error message instead of continuing
                return {
                    "response": "Error: Please rephrase your query to include specific information needed. I must call a tool to provide accurate information.",
                    "traces": traces,
                    "error": "invalid_response_format"
                }

            # Parse for tool calls (format: {"tool": "name", "arguments": {...}})
            tool_call = self.client.parse_tool_call(response)

            # Check if we have a valid tool call to execute
            if tool_call is not None and isinstance(tool_call, dict):
                # Safeguard: Prevent re-executing the exact same tool with the exact same arguments
                current_key = f"{tool_call.get('tool', '')}_{json.dumps(tool_call.get('arguments', {}), sort_keys=True)}"
                if last_tool_call is not None and current_key == last_tool_key:
                    logger.warning(f"Preventing infinite loop: would re-execute same tool with same args")

                    # Record that we detected a loop condition and will treat response as final answer
                    traces.append({
                        "step": iteration,
                        "type": "loop_detected",
                        "tool": tool_call["tool"],
                        "args": tool_call.get("arguments", {}),
                        "message": "Prevented infinite loop by detecting repeated tool call"
                    })

                    # Treat the LLM response as final answer (it should have corrected itself)
                    logger.info("Tool call would create loop - treating response as final answer")
                    return {
                        "response": response,
                        "traces": traces
                    }

                last_tool_key = current_key
                last_tool_call = tool_call

                logger.info(f"LLM requested tool call: {tool_call}")

                # Record action step in traces
                traces.append({
                    "step": iteration,
                    "type": "tool_call",
                    "tool": tool_call["tool"],
                    "args": tool_call.get("arguments", {})
                })

                # Execute the tool
                try:
                    tool_result = self._call_tool(tool_call["tool"], tool_call.get("arguments", {}))

                    logger.info(f"Tool '{tool_call['tool']}' completed with result: {tool_result}")

                    # Check for errors or empty results - prevent re-execution loop
                    if not tool_result:
                        logger.warning(f"Tool '{tool_call['tool']}' returned empty result")
                except Exception as e:
                    logger.error(f"Error executing tool '{tool_call['tool']}': {e}")
                    tool_result = {"error": str(e)}

                # Append tool result to conversation context
                messages.append({
                    "role": "user",
                    "content": f"[Tool Result for {tool_call['tool']}]: {json.dumps(tool_result, indent=2)}"
                })

                # After executing a tool, we need to get the LLM's final synthesized response
                # Prepare the full prompt from conversation history including the tool result
                final_prompt = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in messages])

                logger.info(f"--- Generating final response after tool execution ---")
                logger.info(f"Final Prompt: {final_prompt[:200]}...")

                # Generate the final LLM response with tool results included
                final_response = self.client.generate_response(final_prompt)

                logger.info(f"Final LLM Response: {final_response[:200]}...")

                # Record the final answer in traces
                traces.append({
                    "step": iteration,
                    "type": "final_answer",
                    "content": final_response
                })

                return {
                    "response": final_response,
                    "traces": traces
                }

            else:
                logger.info("No tool call detected or invalid format - treating response as final answer")

                # Record final answer in traces
                traces.append({
                    "step": iteration,
                    "type": "final_answer",
                    "content": response
                })

                return {
                    "response": response,
                    "traces": traces
                }

        # Max iterations reached - return latest response with traces
        logger.warning(f"Maximum iterations ({max_iterations}) reached")

        final_step = traces[-1] if traces else {"step": 0, "type": "final_answer", "content": ""}

        return {
            "response": final_step.get("content", ""),
            "traces": traces,
            "iterations_completed": iteration
        }

    def _call_tool(self, tool_name: str, arguments: dict) -> dict:
        """
        Call a registered tool and return structured JSON output.

        Args:
            tool_name: Name of the tool to invoke (e.g., 'get_employee')
            arguments: Dictionary of arguments to pass to the tool

        Returns:
            Tool result as a dictionary or None if tool not found

        Raises:
            ValueError: If tool doesn't exist or has invalid arguments
        """
        # Validate that tool exists in registered tools
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}. Available tools: {list(self.tools.keys())}")

        # Call the tool with provided arguments
        logger.info(f"Calling tool: {tool_name} with args: {arguments}")
        result = self.tools[tool_name](**arguments)

        logger.info(f"Tool '{tool_name}' completed successfully")
        return result

    def generate_response(self, context: dict) -> str:
        """
        Generate a response based on available tools and context.

        Args:
            context: Dictionary containing user query and tool outputs

        Returns:
            Formatted text response including policy citations when applicable
        """
        # This method would normally call the LLM via self.client with the full context
        # For now, return a simple placeholder that indicates it's working properly

        logger.info(f"Generating response for context: {context}")

        # In a real implementation, this would call self.client.generate_response()
        # but since we're focusing on tool execution flow, we'll return a placeholder
        return "Response generation completed successfully with tool integration."
