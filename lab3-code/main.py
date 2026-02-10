"""
Main Application for HR Agent
Runs the LangGraph agent with human-in-the-loop capabilities
"""

import asyncio
import os
from dotenv import load_dotenv
from hr_agent_graph import create_agent_graph
from agent_state import AgentState

# Load environment variables
load_dotenv()


async def run_agent(user_message: str, employee_name: str = None):
    """
    Run the HR agent with a user message

    Args:
        user_message: The user's query
        employee_name: Optional employee name
    """
    # Create the agent graph
    agent_graph = create_agent_graph()

    # Initialize state
    initial_state: AgentState = {
        "messages": [{"role": "user", "content": user_message}],
        "current_user_name": employee_name,
        "leave_type": None,
        "start_date": None,
        "end_date": None,
        "days_requested": None,
        "leave_balance": None,
        "requires_approval": False,
        "approval_status": None,
        "approval_reason": None,
        "agent_response": None,
        "error": None
    }
    
    print("\n" + "="*60)
    print("HR AGENT PROCESSING\n")
    print(f"User: {user_message}")
    
    # Run the agent
    try:
        result = await agent_graph.ainvoke(initial_state)
        
        # Display the result
        print("\n" + "="*60)
        print("AGENT RESPONSE\n")
        print(result.get("agent_response", "No response generated"))
        
        return result
        
    except Exception as e:
        print(f"\nError running agent: {str(e)}")
        return None


async def interactive_mode():
    print("HR AGENT")
    print("Type 'quit' or 'exit' to end the session\n")
    
    employee_name = input("Enter your name: ").strip()
    if not employee_name:
        employee_name = None

    while True:
        print("\n" + "-"*60)
        user_input = input("You: ").strip()

        if user_input.lower() in ['quit', 'exit']:
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        await run_agent(user_input, employee_name)

def main():
    """
    Main entry point
    """
    import sys
    
    asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()

# Made with Bob
