#!/usr/bin/env python3
"""
Memory-optimized FastAPI server for MadCo HR Agent API
"""

import os
# Set environment variables to reduce memory usage
os.environ['PYTHONHASHSEED'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TensorFlow logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging

# Configure logging early
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="MadCo HR Agent API", version="1.0.0")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str = Field(..., example="What is the PTO policy for full-time employees?")
    user_id: str | None = Field(default=None, example="EMP101")

class QueryResponse(BaseModel):
    response: str
    traces: list[dict]
    status: str = "success"

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "MadCo HR Assistant"
    }

@app.post("/api/chat")
async def chat_api(request: QueryRequest):
    """Chat endpoint to query HR information."""
    try:
        # Import only when needed to reduce memory footprint at startup
        from app.agent import HRAgent
        agent = HRAgent()
        result = agent.run(request.query)

        return QueryResponse(
            response=result["response"],
            traces=result["traces"]
        )
    except Exception as e:
        import traceback
        error_msg = f"Error in chat_api: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)

        return {
            "error": str(e),
            "status": "failed"
        }

if __name__ == "__main__":
    import uvicorn
    # Use minimal configuration to reduce memory usage
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1,
        timeout_keep_alive=30
    )