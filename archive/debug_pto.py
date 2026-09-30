#!/usr/bin/env python3

import sys
import os
import json
from pathlib import Path

# Set up the path to the app directory
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

# Mock data and policy directory path (under data/ subdirectory)
MOCK_DATA_DIR = Path(__file__).parent.parent / "data" / "mock_data"
print(f"Mock data dir: {MOCK_DATA_DIR}")
print(f"Dir exists: {MOCK_DATA_DIR.exists()}")

if MOCK_DATA_DIR.exists():
    print("Files in mock data directory:")
    for f in MOCK_DATA_DIR.iterdir():
        print(f"  {f.name}")

# Test file loading directly
pto_file = MOCK_DATA_DIR / "pto_balances.json"
print(f"\nPTO file path: {pto_file}")
print(f"PTO file exists: {pto_file.exists()}")

if pto_file.exists():
    try:
        with open(pto_file, 'r') as f:
            pto_data = json.load(f)
        print("Successfully loaded PTO data")
        print(f"Data length: {len(pto_data)}")
        for record in pto_data:
            print(f"  Employee ID: {record['employee_id']}")
    except Exception as e:
        print(f"Error loading PTO data: {e}")

# Test with a specific employee ID
test_employee = "EMP-101"
print(f"\nLooking for employee: {test_employee}")

if pto_file.exists():
    try:
        with open(pto_file, 'r') as f:
            pto_data = json.load(f)

        record = next((r for r in pto_data if r["employee_id"] == test_employee), None)
        print(f"Found record: {record}")

        if record is None:
            print("No record found - this should be handled by our new logic")
        else:
            print("Record found successfully")

    except Exception as e:
        print(f"Error in search: {e}")