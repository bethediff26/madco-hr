"""
Flask web application for HR Policy Assistant.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, render_template_string
import asyncio
import logging
import re
from hr_mcp.client import mcp_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# HTML template for the chat interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MadCo HR Policy & Workflow Assistant</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 860px; margin: 0 auto; padding: 24px 16px; background: #fafafa; color: #212529; }
        h1 { margin-bottom: 8px; color: #1e293b; }
        p.subtitle { color: #64748b; margin-top: 0; margin-bottom: 16px; }
        .demos { background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; }
        .demos-title { font-size: 0.9em; font-weight: 600; color: #475569; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
        .demo-btn { background: #ffffff; border: 1px solid #94a3b8; border-radius: 6px; padding: 6px 12px; margin: 4px 4px 4px 0; font-size: 0.85em; cursor: pointer; transition: all 0.15s ease-in-out; color: #1e293b; }
        .demo-btn:hover { background: #e2e8f0; border-color: #64748b; }
        .chat-container { border: 1px solid #e2e8f0; border-radius: 8px; height: 420px; overflow-y: auto; padding: 16px; margin-bottom: 12px; background: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .message { margin: 12px 0; padding: 12px 16px; border-radius: 8px; max-width: 85%; }
        .user-message { background-color: #2563eb; color: #ffffff; margin-left: auto; text-align: left; }
        .bot-message { background-color: #f8fafc; border: 1px solid #e2e8f0; color: #1e293b; line-height: 1.6; white-space: pre-wrap; margin-right: auto; }
        .sources { margin-top: 12px; padding-top: 8px; border-top: 1px solid #e2e8f0; font-size: 0.9em; }
        .sources-title { font-weight: 600; color: #475569; margin-bottom: 4px; }
        .sources ul { margin: 0; padding-left: 20px; color: #64748b; }
        .input-container { display: flex; gap: 8px; }
        #query { flex: 1; padding: 12px 16px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 1em; outline: none; }
        #query:focus { border-color: #2563eb; }
        #submit { padding: 12px 24px; background: #2563eb; color: white; border: none; border-radius: 6px; font-size: 1em; font-weight: 500; cursor: pointer; }
        #submit:hover { background: #1d4ed8; }
        #submit:disabled { background: #94a3b8; cursor: not-allowed; }
        .status { margin-top: 12px; padding: 10px 14px; border-radius: 6px; font-size: 0.9em; font-weight: 500; }
        .connected { background-color: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
        .disconnected { background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
        .spinner { display: inline-block; width: 12px; height: 12px; border: 2px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: #fff; animation: spin 1s ease-in-out infinite; margin-left: 6px; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <h1>MadCo HR Policy & Workflow Assistant</h1>
    <p class="subtitle">Agentic HR Assistant with Grounded Policy RAG and MCP System Integration</p>

    <div class="demos">
        <div class="demos-title">Agentic Demo Workflows (Click to run):</div>
        <button class="demo-btn" onclick="runDemo('can you give me the pto balance for employee EMP-101 and guide me on requesting 3 days off next week?')">🏖️ Task 1: PTO Balance & Request (EMP-101)</button>
        <button class="demo-btn" onclick="runDemo('can employee EMP-102 work remotely from another state for six weeks?')">🌍 Task 2: Remote Work Eligibility (EMP-102)</button>
        <button class="demo-btn" onclick="runDemo('what is the expense reimbursement limit for home office equipment for EMP-103?')">💻 Task 3: Expense Policy (EMP-103)</button>
    </div>

    <div class="chat-container" id="chatContainer"></div>

    <div class="input-container">
        <input type="text" id="query" placeholder="Ask about HR policy, PTO balances, remote work eligibility, or benefits..." />
        <button id="submit" onclick="sendMessage()">Send</button>
    </div>

    <div id="status" class="status">
        Checking connectivity...
    </div>

    <script>
        function addMessage(message, isUser = false, citations = []) {
            const container = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            const messageText = document.createElement('div');
            messageText.textContent = message;
            messageDiv.appendChild(messageText);

            if (!isUser && citations && citations.length > 0) {
                const sources = document.createElement('div');
                sources.className = 'sources';
                const title = document.createElement('div');
                title.className = 'sources-title';
                title.textContent = 'Grounded Policy Citations:';
                sources.appendChild(title);

                const list = document.createElement('ul');
                citations.forEach(citation => {
                    const item = document.createElement('li');
                    const text = typeof citation === 'string' ? citation : (citation.title || citation.doc_title || citation.document || JSON.stringify(citation));
                    item.textContent = text;
                    list.appendChild(item);
                });
                sources.appendChild(list);
                messageDiv.appendChild(sources);
            }

            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('query');
            const submitBtn = document.getElementById('submit');
            const query = input.value.trim();

            if (!query) return;

            addMessage(query, true);
            input.value = '';
            input.disabled = true;
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Thinking<span class="spinner"></span>';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });

                if (!response.ok) {
                    const errText = await response.text();
                    let errMsg = `Server returned status ${response.status}`;
                    try {
                        const errJson = JSON.parse(errText);
                        errMsg = errJson.error || errJson.message || errMsg;
                    } catch (_) {
                        if (errText) errMsg += `: ${errText.substring(0, 100)}`;
                    }
                    addMessage('Error: ' + errMsg);
                    return;
                }

                const data = await response.json();
                addMessage(data.message || 'No response available', false, data.citations || []);
            } catch (error) {
                addMessage('Network Error: ' + error.message);
            } finally {
                input.disabled = false;
                submitBtn.disabled = false;
                submitBtn.textContent = 'Send';
                input.focus();
            }
        }

        function runDemo(promptText) {
            document.getElementById('query').value = promptText;
            sendMessage();
        }

        async function checkHealth() {
            const statusDiv = document.getElementById('status');
            try {
                const response = await fetch('/health');
                const data = await response.json();

                if (data.status === 'healthy') {
                    statusDiv.className = 'status connected';
                    statusDiv.textContent = '● System Healthy | MCP Tools: ' + (data.mcp_status || 'connected');
                } else {
                    statusDiv.className = 'status disconnected';
                    statusDiv.textContent = '● Service degraded: ' + (data.error || 'Check server logs');
                }
            } catch (error) {
                statusDiv.className = 'status disconnected';
                statusDiv.textContent = '● Unable to reach health endpoint';
            }
        }

        window.onload = function() {
            checkHealth();
            addMessage('Welcome to MadCo HR Assistant! Ask about company policies, check PTO balances, verify remote work eligibility, or click any demo workflow above to begin.');
        };

        document.getElementById('query').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Serve the main chat interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests."""
    try:
        data = request.get_json(silent=True) or {}
        query = data.get('query', '')

        if not query:
            return jsonify({'status': 'error', 'message': 'No query provided', 'citations': []}), 400

        # Extract employee ID if present
        emp_match = re.search(r'(emp-\d+)', query.lower())
        employee_id = emp_match.group(1).upper() if emp_match else None

        async def process_query():
            from agent.orchestrator import orchestrator
            return await orchestrator.process_user_query(query, employee_id)

        result = asyncio.run(process_query())

        # Return structured response
        response = {
            'message': result.get('message', 'No response available'),
            'citations': result.get('citations', []),
            'status': result.get('status', 'ok')
        }

        # Add trace information if available
        if 'trace' in result:
            response['trace'] = result['trace']

        return jsonify(response)

    except Exception as e:
        logger.exception("Error processing chat request")
        return jsonify({
            'status': 'error',
            'message': f"Request could not be processed: {str(e)}",
            'citations': []
        }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    try:
        async def check_mcp():
            try:
                if not mcp_client.is_connected:
                    await mcp_client.connect()
                tools = await mcp_client.list_tools()
                return f"connected ({len(tools)} tools)" if tools else "connected"
            except Exception as e:
                logger.warning(f"MCP health check warning: {e}")
                return "in_process"

        mcp_status = asyncio.run(check_mcp())

        response = {
            'status': 'healthy',
            'mcp_status': mcp_status,
            'service': 'MadCo HR Assistant',
        }

        return jsonify(response)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# Pre-warm orchestrator and policy index on server startup
try:
    from agent.orchestrator import orchestrator
    logger.info("Orchestrator and Policy RAG successfully pre-warmed on server startup")
except Exception as e:
    logger.warning(f"Orchestrator pre-warm warning: {e}")

import os
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)