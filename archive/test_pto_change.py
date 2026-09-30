#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from mcp_tools import get_pto_balance

# Test with an existing employee ID (should work)
print("Testing with existing employee ID (EMP-101):")
result = get_pto_balance("EMP-101")
print(f"Result: {result}")

# Test with another existing employee ID
print("\nTesting with existing employee ID (EMP-103):")
result = get_pto_balance("EMP-103")
print(f"Result: {result}")

# Test with a non-existing employee ID (should return error message now)
print("\nTesting with non-existing employee ID (EMP-999):")
result = get_pto_balance("EMP-999")
print(f"Result: {result}")

# Test with another non-existing employee ID
print("\nTesting with another non-existing employee ID (EMP-106):")
result = get_pto_balance("EMP-106")
print(f"Result: {result}")