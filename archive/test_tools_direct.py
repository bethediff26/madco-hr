import asyncio
# Adjust these imports based on where your tools or MCP server functions are defined
from app.mcp_server import get_employee, get_pto_balance, search_policy_documents

async def main():
    print("--- Testing Employee Lookup ---")
    try:
        emp = get_employee("EMP101")
        print("Result:", emp)
    except Exception as e:
        print("Error:", e)

    print("\n--- Testing PTO Balance ---")
    try:
        pto = get_pto_balance("EMP101")
        print("Result:", pto)
    except Exception as e:
        print("Error:", e)

    print("\n--- Testing Policy Search ---")
    try:
        # If search_policy_documents is async, await it; if sync, remove await
        policies = search_policy_documents("remote work")
        print("Result:", policies)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
