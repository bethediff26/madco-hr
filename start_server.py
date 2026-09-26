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
    # Use minimal configuration to avoid OOM errors
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=1,  # Only one worker to reduce memory usage
        timeout_keep_alive=30,
        log_level="info"
    )