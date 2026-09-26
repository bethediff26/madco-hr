from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging

# Initialize FastAPI app
app = FastAPI(title="MadCo HR Agent API", version="1.0.0")

# Configure logging to reduce memory footprint
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Add CORS Middleware
async def cors_middleware(request):
    """CORS middleware for the FastAPI app."""
    response = await request.call()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


# Alternative: Use FastAPI's built-in CORSMiddleware
# app.add_middleware(CORSMiddleware,
#                    allow_origins=["*"],
#                    allow_methods=["*"],
#                    allow_headers=["*"])


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
        # Create agent instance only when needed (lazy loading)
        from app.agent import HRAgent
        agent = HRAgent()
        result = agent.run(request.query)

        return QueryResponse(
            response=result["response"],
            traces=result["traces"]
        )
    except Exception as e:
        # Log the full exception for debugging
        import traceback
        error_msg = f"Error in chat_api: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)  # Use proper logging

        # Return a more informative error response
        return {
            "error": str(e),
            "status": "failed"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
