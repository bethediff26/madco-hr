# Deployed Service Information

## 1. Public Deployed URLs

- **Application Live URL**: [https://madco-hr-agent.onrender.com](https://madco-hr-agent.onrender.com)
- **Health Check Endpoint**: [https://madco-hr-agent.onrender.com/health](https://madco-hr-agent.onrender.com/health)
- **Chat API Endpoint**: `POST https://madco-hr-agent.onrender.com/chat`


---

## 2. Health Endpoint Specification

- **Method**: `GET /health`
- **Sample Output**:
  ```json
  {
    "service": "MadCo HR Assistant",
    "status": "healthy",
    "mcp_status": "connected (7 tools)"
  }
  ```
- **Readiness Verification**: Validates that the Flask application is up, the in-memory policy store is indexed, and all 7 FastMCP tools are connected.

---

## 3. Free-Tier Cold-Start Notes & Performance

### 15-Minute Inactivity Spin-Down
- **Hosting Provider Behavior**: Render's free tier spins down web services to zero instances after **15 minutes of inactivity**.
- **Cold-Start Duration**: When a user accesses the URL after the instance has spun down, Render provisions a container and boots the service. This initial wake-up typically takes **30–50 seconds**.

### In-Memory Pre-Warming (< 50ms Response After Boot)
- Once the container launches, `app.py` automatically pre-warms the policy store and orchestrator on server startup (`app.py:269-274`).
- The Pure Python policy engine builds the entire index in **0.02 seconds**.
- Subsequent user interactions, chat queries, and tool evaluations execute with sub-50ms latency.
- Total memory usage remains stable at **~65MB**, well below Render's 512MB RAM ceiling, completely eliminating out-of-memory terminations.
