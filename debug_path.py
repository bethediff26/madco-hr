#!/usr/bin/env python3

import sys
import os
from pathlib import Path

print("=== Debugging Path Resolution ===")

# Show current working directory
print(f"Current working directory: {os.getcwd()}")

# Show where this script is located
script_path = Path(__file__).resolve()
print(f"This script location: {script_path}")

# Show the app directory
app_dir = Path(__file__).parent / "app"
print(f"App directory: {app_dir}")
print(f"App directory exists: {app_dir.exists()}")

# Show data directory
data_dir = Path(__file__).parent / "data"
print(f"Data directory: {data_dir}")
print(f"Data directory exists: {data_dir.exists()}")

# Show mock_data directory
mock_data_dir = data_dir / "mock_data"
print(f"Mock data directory: {mock_data_dir}")
print(f"Mock data directory exists: {mock_data_dir.exists()}")

if mock_data_dir.exists():
    print("Files in mock_data:")
    for f in mock_data_dir.iterdir():
        print(f"  {f.name}")

# Test the path from within app
sys.path.insert(0, str(app_dir))
print("\n=== Testing path resolution from app ===")

try:
    # Try to import mcp_tools
    from mcp_tools import MOCK_DATA_DIR

    print(f"MOCK_DATA_DIR from mcp_tools: {MOCK_DATA_DIR}")
    print(f"MOCK_DATA_DIR exists: {MOCK_DATA_DIR.exists()}")

    if MOCK_DATA_DIR.exists():
        print("Files in MOCK_DATA_DIR:")
        for f in MOCK_DATA_DIR.iterdir():
            print(f"  {f.name}")

except Exception as e:
    print(f"Error importing mcp_tools: {e}")

# Test direct path construction
print("\n=== Testing direct path construction ===")
try:
    # Try to construct path the same way as mcp_tools.py does
    test_path = Path(__file__).parent.parent / "data" / "mock_data"
    print(f"Direct construction path: {test_path}")
    print(f"Direct construction exists: {test_path.exists()}")

    if test_path.exists():
        print("Files in direct path:")
        for f in test_path.iterdir():
            print(f"  {f.name}")

except Exception as e:
    print(f"Error with direct path construction: {e}")