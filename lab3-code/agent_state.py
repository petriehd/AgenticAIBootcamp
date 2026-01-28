"""
Agent State Definition for HR Agent
Defines the state structure that persists across all nodes in the LangGraph
"""

from typing import TypedDict, Annotated, Optional
from langgraph.graph import add_messages


class AgentState(TypedDict):
    """
    State object for the HR Agent.
    Tracks all relevant information throughout the conversation.
    """
    # Conversation history - automatically managed by LangGraph
    messages: Annotated[list, add_messages]
    
    # Employee information
    employee_id: Optional[str]
    employee_name: Optional[str]
    
    # Leave request details
    leave_type: Optional[str]  # vacation, sick, personal
    start_date: Optional[str]
    end_date: Optional[str]
    days_requested: Optional[int]
    leave_balance: Optional[int]
    
    # Approval workflow state
    requires_approval: bool
    approval_status: Optional[str]  # pending, approved, rejected
    approval_reason: Optional[str]
    
    # Agent response
    agent_response: Optional[str]
    
    # Error handling
    error: Optional[str]

# Made with Bob
