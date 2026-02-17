"""
Agent Nodes for LangGraph
Defines the processing nodes that make up the agent workflow
"""

import os
import re
from typing import Dict, Any
from agent_state import AgentState
from langflow_client import LangflowClient


# Initialize Langflow client
langflow_client = LangflowClient()


def check_privacy_access(state: AgentState) -> str:
    """
    Simple privacy check - looks for other employee names in the message.
    If user mentions another employee name, deny access.

    Args:
        state: Current agent state

    Returns:
        "proceed" if accessing own data, "denied" if trying to access others' data
    """
    messages = state.get("messages", [])
    if not messages:
        return "proceed"

    # Get content from the message object (not a dict)
    latest_message = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
    current_user_name = state.get("current_user_name", "")

    # Look for patterns where user asks about another employee by name
    # Matches phrases like "for Alice", "employee Bob Smith", "Bob's leave"
    name_patterns = [
        r"for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",        # "for Alice" or "for Alice Smith"
        r"employee\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",    # "employee Bob"
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'s\s+leave",    # "Bob's leave"
    ]

    for pattern in name_patterns:
        matches = re.findall(pattern, latest_message)
        for name in matches:
            if current_user_name and name.lower() != current_user_name.lower():
                state["agent_response"] = (
                    f"Access denied. You can only access your own leave information, "
                    f"not data for employee {name}."
                )
                state["error"] = "Unauthorized access attempt"
                return "denied"

    # No other employee names mentioned - proceed
    return "proceed"

async def call_langflow_node(state: AgentState) -> dict:
    """
    Node that calls the Langflow API to process the user's query.
    
    Args:
        state: Current agent state
    
    Returns:
        Partial state update with Langflow response and extracted data
    """
    messages = state.get("messages", [])
    if not messages:
        return {"error": "No messages to process"}
    
    latest_message = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
    
    updates = {}
    try:
        # Get structured response from Langflow
        response = langflow_client.query(latest_message)
        
        # Always set conversational response
        updates["agent_response"] = response.get("conversational_response", "No response")
        
        # Extract structured data if available (query_flag=false)
        if not response.get("query_flag", True) and response.get("data"):
            data = response["data"]
            
            # Populate state with structured data
            if data.get("employee_id"):
                updates["employee_id"] = data["employee_id"]
            if data.get("employee_name"):
                updates["current_user_name"] = data["employee_name"]
            if data.get("leave_balance") is not None:
                updates["leave_balance"] = data["leave_balance"]
            if data.get("leave_type"):
                updates["leave_type"] = data["leave_type"]
            if data.get("start_date"):
                updates["start_date"] = data["start_date"]
            if data.get("end_date"):
                updates["end_date"] = data["end_date"]
            if data.get("days_requested") is not None:
                updates["days_requested"] = data["days_requested"]
        
    
    except Exception as e:
        updates["error"] = str(e)
        updates["agent_response"] = "I encountered an error processing your request."
    
    return updates


async def check_approval_node(state: AgentState) -> dict:
    """
    Node that checks if the request requires approval based on business rules

    Args:
        state: Current agent state

    Returns:
        Partial state update with approval requirement flag
    """
    days_requested = state.get("days_requested", 0)
    threshold = int(os.getenv("APPROVAL_THRESHOLD_DAYS", 5))

    # Check if this is a leave request that exceeds threshold
    if days_requested and days_requested > threshold:
        return {"requires_approval": True, "approval_status": "pending"}
    else:
        return {"requires_approval": False, "approval_status": "auto_approved"}


async def human_approval_node(state: AgentState) -> dict:
    """
    Node that pauses execution and requests human approval
    This is the key human-in-the-loop functionality

    Args:
        state: Current agent state

    Returns:
        Partial state update with approval decision
    """
    print("\n" + "="*60)
    print("HUMAN APPROVAL REQUIRED")
    print("="*60)
    print(f"Employee Name: {state.get('current_user_name', 'Unknown')}")
    print(f"Leave Type: {state.get('leave_type', 'Unknown')}")
    print(f"Duration: {state.get('days_requested', 0)} days")
    print(f"Dates: {state.get('start_date', 'N/A')} to {state.get('end_date', 'N/A')}")
    print(f"Current Balance: {state.get('leave_balance', 'Unknown')} days")
    print("="*60)

    # Get human input
    while True:
        decision = input("\nApprove this request? (yes/no): ").strip().lower()
        if decision in ['yes', 'no']:
            break
        print("Please enter 'yes' or 'no'")

    reason = input("Reason (optional): ").strip()

    approval_status = "approved" if decision == "yes" else "rejected"
    approval_reason = reason if reason else "No reason provided"

    if approval_status == "approved":
        agent_response = (
            f"Your leave request for {state.get('days_requested')} days has been approved. "
            f"Reason: {approval_reason}"
        )
    else:
        agent_response = (
            f"Your leave request for {state.get('days_requested')} days has been rejected. "
            f"Reason: {approval_reason}"
        )

    print(f"\nDecision recorded: {approval_status}")
    print("="*60 + "\n")

    return {
        "approval_status": approval_status,
        "approval_reason": approval_reason,
        "agent_response": agent_response,
    }


async def finalize_node(state: AgentState) -> dict:
    """
    Final node that prepares the response for the user

    Args:
        state: Current agent state

    Returns:
        Partial state update with final response
    """
    # If auto-approved, add that information to the response
    if state.get("approval_status") == "auto_approved" and state.get("days_requested"):
        return {
            "agent_response": (
                f"{state.get('agent_response', '')} "
                f"Your request has been automatically approved."
            )
        }

    # Add any error information if present
    if state.get("error"):
        return {
            "agent_response": (
                f"Error: {state['error']}. "
                f"Please try again or contact support."
            )
        }

    return {}


def should_require_approval(state: AgentState) -> str:
    """
    Conditional edge function that determines the next node based on approval requirement

    Args:
        state: Current agent state

    Returns:
        Name of the next node to execute
    """
    if state.get("requires_approval", False):
        return "human_approval"
    return "finalize"
