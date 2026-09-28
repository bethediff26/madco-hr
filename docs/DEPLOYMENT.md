# Free-Tier Cloud Deployment Guide (Render, Railway, etc.)

## 1. Overview
The MadCo HR Assistant is engineered specifically for reliable operation on cloud free tiers (such as Render Free Web Service, Railway Starter, or AWS App Runner). It requires no external vector databases, no GPU resources, and keeps memory consumption well below the 512MB free-tier threshold.

---

## 2. Render Deployment Instructions

### Service Configuration
- **Environment**: Python 3
- **Repository**: `https://github.com/bethediff26/madco-hr`
- **Branch**: `main`
- **Build Command**:
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
  ```
  *(Alternatively: `python app.py`)*

---

## 3. Environment Variables

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `PORT` | Auto | `5000` | Port assigned by Render / hosting provider. |
| `OPENAI_API_KEY` | Optional | `""` | API key if connecting to external LLMs. Fallbacks operate deterministically without it. |
| `FLASK_ENV` | Optional | `production` | Production environment flag. |
| `PYTHONUNBUFFERED` | Optional | `1` | Ensures real-time stdout/stderr logging. |

---

## 4. Cold-Start Behavior & Pre-Warming

Free-tier instances on Render spin down to zero after 15 minutes of inactivity. When a new request arrives, a cold start occurs.

### Architectural Optimizations for Cold Starts:
1. **Pre-Warmed In-Memory Index**:
   - `app.py` pre-initializes the orchestrator and policy store on application startup (`app.py:269-274`).
   - The pure Python policy parser indexes all 43 policy chunks in **0.02 seconds**.
   - Cold starts complete and become ready to serve traffic in `< 2.5 seconds`.
2. **Zero Heavy C-Extensions**:
   - By eliminating `onnxruntime`, `hnswlib`, and `chromadb`, we avoid SIGILL 132 crashes (illegal instruction crashes caused by CPU architectures without AVX2) and reduce RAM consumption from >450MB down to **~65MB**.
3. **Health Check Endpoint**:
   - Render's health check can be pointed to `/health`, which checks MCP client connectivity and returns HTTP 200 immediately.
