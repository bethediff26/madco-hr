"""
Flask web application for HR Policy Assistant.
"""

from flask import Flask, request, jsonify, render_template_string
import asyncio
import logging
from agent.orchestrator import orchestrator
from hr_mcp.client import mcp_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# HTML template for the chat interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>HR Policy Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .chat-container { border: 1px solid #ddd; height: 400px; overflow-y: scroll; padding: 10px; margin-bottom: 10px; }
        .message { margin: 10px 0; padding: 8px; border-radius: 4px; }
        .user-message { background-color: #e3f2fd; text-align: right; }
        .bot-message { background-color: #f5f5f5; line-height: 1.5; white-space: pre-wrap; }
        .sources { margin-top: 12px; padding-top: 8px; border-top: 1px solid #ddd; white-space: normal; }
        .sources-title { font-weight: bold; margin-bottom: 4px; }
        .sources ul { margin: 0; padding-left: 20px; }
        .input-container { display: flex; }
        #query { flex: 1; padding: 10px; }
        #submit { padding: 10px 20px; }
        .status { margin-top: 10px; padding: 10px; border-radius: 4px; }
        .connected { background-color: #d4edda; color: #155724; }
        .disconnected { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>HR Policy Assistant</h1>

    <div id="status" class="status">
        Checking MCP connectivity...
    </div>

    <div class="chat-container" id="chatContainer"></div>

    <div class="input-container">
        <input type="text" id="query" placeholder="Ask an HR policy question..." />
        <button id="submit" onclick="sendMessage()">Send</button>
    </div>

    <script>
        // Add message to chat
        function addMessage(message, isUser = false, citations = []) {
            const container = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            const messageText = document.createElement('div');
            messageText.textContent = message;
            messageDiv.appendChild(messageText);

            if (!isUser && citations.length > 0) {
                const sources = document.createElement('div');
                sources.className = 'sources';
                const title = document.createElement('div');
                title.className = 'sources-title';
                title.textContent = 'Sources';
                sources.appendChild(title);

                const list = document.createElement('ul');
                citations.forEach(citation => {
                    const item = document.createElement('li');
                    item.textContent = citation.title || citation.doc_title || citation.document || 'Unknown';
                    list.appendChild(item);
                });
                sources.appendChild(list);
                messageDiv.appendChild(sources);
            }

            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }

        // Send message to backend
        async function sendMessage() {
            const input = document.getElementById('query');
            const query = input.value.trim();

            if (!query) return;

            // Add user message to UI
            addMessage(query, true);
            input.value = '';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ query: query })
                });

                const data = await response.json();

                // Add bot response to UI
                addMessage(data.message, false, data.citations || []);
            } catch (error) {
                addMessage('Error: ' + error.message);
            }
        }

        // Check health status on page load
        async function checkHealth() {
            try {
                const response = await fetch('/health');
                const data = await response.json();

                const statusDiv = document.getElementById('status');
                if (data.status === 'healthy') {
                    statusDiv.className = 'status connected';
                    statusDiv.textContent = 'Connected to HR Policy Assistant - MCP Status: ' + (data.mcp_status || 'Unknown');
                } else {
                    statusDiv.className = 'status disconnected';
                    statusDiv.textContent = 'Disconnected from HR Policy Assistant';
                }
            } catch (error) {
                const statusDiv = document.getElementById('status');
                statusDiv.className = 'status disconnected';
                statusDiv.textContent = 'Error connecting to health endpoint';
            }
        }

        // Initialize on page load
        window.onload = function() {
            checkHealth();
            addMessage('Welcome to HR Policy Assistant! Ask me anything about company policies, benefits, PTO, etc.');
        };

        // Allow Enter key to send message
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
        data = request.get_json()
        query = data.get('query', '')

        if not query:
            return jsonify({'error': 'No query provided'}), 400

        # Process the query using our orchestrator
        # Extract an employee ID only when the query explicitly provides one.
        import re
        emp_match = re.search(r'(emp-\d+)', query.lower())
        employee_id = emp_match.group(1).upper() if emp_match else None

        async def process_query():
            try:
                return await orchestrator.process_user_query(query, employee_id)
            finally:
                await mcp_client.disconnect()

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
        logger.error(f"Error processing chat request: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    try:
        async def check_mcp():
            try:
                await mcp_client.connect()
                tools = await mcp_client.list_tools()
                return "connected" if tools else "unavailable"
            except Exception:
                logger.exception("MCP health check failed")
                return "unavailable"
            finally:
                await mcp_client.disconnect()

        mcp_status = asyncio.run(check_mcp())

        response = {
            'status': 'healthy',
            'mcp_status': mcp_status,
            'timestamp': None,
        }

        return jsonify(response)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

import os
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)