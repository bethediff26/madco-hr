#!/usr/bin/env python3
"""
Minimal startup for MadCo HR Agent API to avoid memory issues.
"""

import os
# Set environment to reduce memory usage
os.environ['PYTHONHASHSEED'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from app.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    # Use pure python asyncio and h11 to avoid C-extension / AVX SIGILL crashes on Render
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        loop="asyncio",
        http="h11",
        workers=1,
        timeout_keep_alive=30,
        log_level="info"
    )