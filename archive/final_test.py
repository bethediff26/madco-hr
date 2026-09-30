#!/usr/bin/env python3

# Let's understand what exactly is expected by examining the working examples
import sys
sys.path.insert(0, './app')

from mcp_tools import get_pto_balance
import json
from pathlib import Path

# First check the mock data location
MOCK_DATA_DIR = Path(__file__).parent.parent / "data" / "mock_data"
print(f"Looking for data in: {MOCK_DATA_DIR}")

# Try to directly read the file to see what's there
pto_file = MOCK_DATA_DIR / "pto_balances.json"
try:
    with open(pto_file, 'r') as f:
        pto_data = json.load(f)
    print("Successfully loaded PTO data")
    print(f"Data contains {len(pto_data)} records")
    for record in pto_data:
        print(f"  Employee ID: {record['employee_id']}")
except Exception as e:
    print(f"Error loading PTO data: {e}")

# Test function
print("\nTesting get_pto_balance function:")
try:
    result = get_pto_balance("EMP-101")
    print(f"Result for EMP-101: {result}")
    if isinstance(result, dict) and 'error' in result:
        print("Function correctly returns error message")
    else:
        print("Function returns normal data structure")
except Exception as e:
    print(f"Exception raised: {e}")