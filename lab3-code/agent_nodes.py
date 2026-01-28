"""
Agent Nodes for LangGraph
Defines the processing nodes that make up the agent workflow
"""

import os
from typing import Dict, Any
from agent_state import AgentState
from langflow_client import LangflowClient


# Initialize Langflow client
langflow_client = LangflowClient()


async def call_langflow_node(state: AgentState) -> AgentState:
    """
    Node that calls the Langflow API to process the user's query
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with Langflow response
    """
    # Get the latest user message
    messages = state.get("messages", [])
    if not messages:
        state["error"] = "No messages to process"
        return state
    
    latest_message = messages[-1]["content"]
    employee_id = state.get("employee_id")
    
    # Call Langflow API
    result = await langflow_client.query_agent(latest_message, employee_id)
    
    if not result.get("success"):
        state["error"] = result.get("error", "Unknown error")
        state["agent_response"] = "I encountered an error processing your request."
        return state
    
    # Update state with response and any extracted data
    state["agent_response"] = result.get("response", "")
    
    # Update state with any extracted information
    if result.get("employee_id"):
        state["employee_id"] = result["employee_id"]
    if result.get("leave_balance") is not None:
        state["leave_balance"] = result["leave_balance"]
    if result.get("days_requested") is not None:
        state["days_requested"] = result["days_requested"]
    if result.get("leave_type"):
        state["leave_type"] = result["leave_type"]
    if result.get("start_date"):
        state["start_date"] = result["start_date"]
    if result.get("end_date"):
        state["end_date"] = result["end_date"]
    
    return state


async def check_approval_node(state: AgentState) -> AgentState:
    """
    Node that checks if the request requires approval based on business rules
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with approval requirement flag
    """
    days_requested = state.get("days_requested", 0)
    threshold = int(os.getenv("APPROVAL_THRESHOLD_DAYS", 5))
    
    # Check if this is a leave request that exceeds threshold
    if days_requested and days_requested > threshold:
        state["requires_approval"] = True
        state["approval_status"] = "pending"
    else:
        state["requires_approval"] = False
        state["approval_status"] = "auto_approved"
    
    return state


async def human_approval_node(state: AgentState) -> AgentState:
    """
    Node that pauses execution and requests human approval
    This is the key human-in-the-loop functionality
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with approval decision
    """
    print("\n" + "="*60)
    print("HUMAN APPROVAL REQUIRED")
    print("="*60)
    print(f"Employee ID: {state.get('employee_id', 'Unknown')}")
    print(f"Employee Name: {state.get('employee_name', 'Unknown')}")
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
    
    # Update state with decision
    state["approval_status"] = "approved" if decision == "yes" else "rejected"
    state["approval_reason"] = reason if reason else "No reason provided"
    
    # Update agent response based on decision
    if state["approval_status"] == "approved":
        state["agent_response"] = (
            f"Your leave request for {state.get('days_requested')} days has been approved. "
            f"Reason: {state['approval_reason']}"
        )
    else:
        state["agent_response"] = (
            f"Your leave request for {state.get('days_requested')} days has been rejected. "
            f"Reason: {state['approval_reason']}"
        )
    
    print(f"\nDecision recorded: {state['approval_status']}")
    print("="*60 + "\n")
    
    return state


async def finalize_node(state: AgentState) -> AgentState:
    """
    Final node that prepares the response for the user
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with final response
    """
    # If auto-approved, add that information to the response
    if state.get("approval_status") == "auto_approved" and state.get("days_requested"):
        state["agent_response"] = (
            f"{state.get('agent_response', '')} "
            f"Your request has been automatically approved."
        )
    
    # Add any error information if present
    if state.get("error"):
        state["agent_response"] = (
            f"Error: {state['error']}. "
            f"Please try again or contact support."
        )
    
    return state


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

# Made with Bob
