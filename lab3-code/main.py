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


async def run_agent(user_message: str, employee_id: str = None):
    """
    Run the HR agent with a user message
    
    Args:
        user_message: The user's query
        employee_id: Optional employee ID
    """
    # Create the agent graph
    agent_graph = create_agent_graph()
    
    # Initialize state
    initial_state: AgentState = {
        "messages": [{"role": "user", "content": user_message}],
        "employee_id": employee_id,
        "employee_name": None,
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
    print("HR AGENT PROCESSING")
    print("="*60)
    print(f"User: {user_message}")
    if employee_id:
        print(f"Employee ID: {employee_id}")
    print("="*60 + "\n")
    
    # Run the agent
    try:
        result = await agent_graph.ainvoke(initial_state)
        
        # Display the result
        print("\n" + "="*60)
        print("AGENT RESPONSE")
        print("="*60)
        print(result.get("agent_response", "No response generated"))
        print("="*60 + "\n")
        
        # Display state information for debugging
        if os.getenv("DEBUG", "false").lower() == "true":
            print("\nDEBUG - Final State:")
            print(f"  Employee ID: {result.get('employee_id')}")
            print(f"  Leave Balance: {result.get('leave_balance')}")
            print(f"  Days Requested: {result.get('days_requested')}")
            print(f"  Leave Type: {result.get('leave_type')}")
            print(f"  Approval Status: {result.get('approval_status')}")
            print(f"  Error: {result.get('error')}")
            print()
        
        return result
        
    except Exception as e:
        print(f"\nError running agent: {str(e)}")
        return None


async def interactive_mode():
    """
    Run the agent in interactive mode
    """
    print("\n" + "="*60)
    print("HR AGENT - INTERACTIVE MODE")
    print("="*60)
    print("Type 'quit' or 'exit' to end the session")
    print("Type 'help' for example queries")
    print("="*60 + "\n")
    
    employee_id = input("Enter your Employee ID (or press Enter to skip): ").strip()
    if not employee_id:
        employee_id = None
    
    while True:
        print("\n" + "-"*60)
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("\nGoodbye!")
            break
        
        if user_input.lower() == 'help':
            print("\nExample queries:")
            print("  - What is my current leave balance?")
            print("  - I want to take 3 days off next week for vacation")
            print("  - Submit a vacation request for December 20-27")
            print("  - What is the company's vacation policy?")
            print("  - How many sick days do I have left?")
            continue
        
        if not user_input:
            continue
        
        await run_agent(user_input, employee_id)


async def demo_mode():
    """
    Run predefined demo scenarios
    """
    print("\n" + "="*60)
    print("HR AGENT - DEMO MODE")
    print("="*60)
    print("Running predefined scenarios to demonstrate capabilities")
    print("="*60 + "\n")
    
    scenarios = [
        {
            "name": "Scenario 1: Check Leave Balance",
            "message": "What is my current leave balance?",
            "employee_id": "EMP12345"
        },
        {
            "name": "Scenario 2: Small Leave Request (Auto-Approve)",
            "message": "I want to take 3 days off next week for vacation",
            "employee_id": "EMP12345"
        },
        {
            "name": "Scenario 3: Large Leave Request (Requires Approval)",
            "message": "I need to take 10 days off in December for vacation",
            "employee_id": "EMP12345"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"{scenario['name']}")
        print(f"{'='*60}")
        
        await run_agent(scenario["message"], scenario["employee_id"])
        
        if i < len(scenarios):
            input("\nPress Enter to continue to next scenario...")


def main():
    """
    Main entry point
    """
    import sys
    
    # Check if running in demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        asyncio.run(demo_mode())
    else:
        asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()

# Made with Bob
