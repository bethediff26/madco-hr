"""
Main entry point for the HR Policy Assistant.
"""

import asyncio
import logging
from typing import Optional
from agent.orchestrator import orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def process_query(user_query: str, employee_id: Optional[str] = None) -> dict:
    """
    Process a user query through the HR Policy Assistant.

    Args:
        user_query (str): The user's question or request
        employee_id (Optional[str]): Employee ID for personalized responses

    Returns:
        dict: Response from the assistant
    """
    try:
        result = await orchestrator.process_user_query(user_query, employee_id)
        return result
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return {
            "status": "error",
            "message": f"Failed to process query: {str(e)}"
        }

async def main():
    """Main function for interactive testing."""
    print("HR Policy Assistant - Interactive Mode")
    print("Type 'quit' to exit")
    print("=" * 40)

    while True:
        try:
            user_input = input("\nEnter your HR question: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if not user_input:
                continue

            # For demo purposes, we'll use a sample employee ID
            employee_id = "EMP-12345"

            print("Processing your request...")
            result = await process_query(user_input, employee_id)

            print("\n" + "=" * 40)
            print("Response:")
            print(result.get("message", "No response received"))

            if "citations" in result and result["citations"]:
                print("\nSources used:")
                for i, citation in enumerate(result["citations"], 1):
                    print(f"{i}. {citation.get('title', 'Unknown')} - {citation.get('source', 'Unknown')}")

            if "trace" in result:
                print("\nProcessing trace (for operational visibility):")
                trace = result["trace"]
                print(f"Intent: {trace['user_intent']}")
                print(f"Tools used: {', '.join(trace['tools_selected'])}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Run the interactive mode
    asyncio.run(main())