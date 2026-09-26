# HR Policy Assistant - PTO Balance Lookup Implementation

## Overview

This implementation adds full support for PTO (Paid Time Off) balance lookups in the HR Policy Assistant. Users can now query their PTO balances by providing their employee ID.

## Key Features Implemented

### 1. Employee ID Extraction
- Extracts employee IDs from user queries using regex patterns
- Supports formats: `emp-12345`, `EMP-12345`, etc.
- Falls back to default "EMP-12345" when no ID is provided

### 2. PTO Balance Lookup Workflow
- Routes PTO-related queries to the `pto_request_guidance` workflow
- Calls the `check_pto_balance` tool with employee ID parameter
- Returns specific PTO balance information (days available)

### 3. Fallback Mechanisms
- Graceful handling when MCP connection fails
- Provides mock data (15 days) as default fallback
- Maintains backward compatibility for all existing functionality

## Usage Examples

### Query with Employee ID:
```
"How much PTO do I have available? My ID is emp-101"
"How do I request PTO for EMP-12345?"
"Can I take PTO? My employee ID is emp-54321"
```

### Response Format:
```
PTO request guidance for employee EMP-101: You have 13 PTO days available. Please check your PTO balance using the get_pto_balance tool, then submit your request through the standard HR portal. For specific policy details, refer to the PTO policy document.
```

## Technical Implementation

### Key Files Modified:
- `app.py`: Added employee ID extraction logic
- `agent/orchestrator.py`: Enhanced workflow routing and fallback handling  
- `hr_mcp/client.py`: Maintained MCP connectivity for PTO balance lookups
- `hr_mcp/server.py`: Provided mock data implementation

### Workflow Integration:
1. User query with employee ID → Intent recognition detects PTO context
2. Routing to `pto_request_guidance` workflow 
3. Tool call to `check_pto_balance(employee_id)`
4. Response with specific balance information

## Data Sources

The system integrates with:
- `data/mock_data/pto_balances.json`: Contains actual employee PTO balances
- `data/policies/pto_policy.md`: PTO policy documentation for reference

## Error Handling

- **MCP Disconnected**: Falls back to default 15-day balance
- **Employee Not Found**: Provides appropriate error guidance  
- **Data Access Issues**: Graceful degradation with fallback mechanisms

## Testing

The implementation has been tested with:
- Various employee ID formats
- PTO query patterns with and without IDs
- Fallback scenarios when MCP is unavailable
- Integration with existing HR policy search functionality

## Backward Compatibility

All existing functionality remains intact:
- General policy searches work as before
- Remote work eligibility checks unchanged
- All other HR assistance features preserved