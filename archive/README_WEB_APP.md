# HR Policy Assistant Web Application

This is a Flask web application that serves as the user interface for the HR Policy Assistant, integrating all components we've built so far.

## Features

- Interactive chat interface for asking HR questions
- API endpoints for chat and health checks
- Integration with the orchestrator, RAG system, and MCP client
- Responsive design with real-time messaging

## Endpoints

### `/` (GET)
Serves the main chat interface web page

### `/chat` (POST)
Handles user queries and returns responses with:
- Message response
- Citations from policy documents
- Tool-call trace for operational visibility

### `/health` (GET)
Returns health status of the application including:
- Application status
- MCP connectivity status

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Flask server:
   ```bash
   python app.py
   ```

3. Visit `http://localhost:5000` in your browser

## Demo Tasks

The application is ready to demonstrate two agentic tasks:

1. **PTO Request Guidance**: 
   - Ask "How do I request PTO?"
   - The system will guide you through the process and provide relevant policy information

2. **Remote Work Eligibility Check**:
   - Ask "Am I eligible for remote work?"
   - The system will check your eligibility based on company policy and employee data

The interface shows real-time chat interaction and displays citations from policy documents.