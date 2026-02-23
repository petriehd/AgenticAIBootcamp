# Lab 3: Pro Code - Building with LangGraph

## Overview

In this lab, you'll expand on previous labs and implement more advanced agent logic using LangGraph and Python. You'll create a custom agent with state management and human-in-the-loop approval workflows. This lab demonstrates how to build implement agents programmatically with guardrails.

**Estimated Time**: 45 minutes

**Tools**: LangGraph, Python, Langflow API

**Data**: Langflow API endpoint from Lab 2

## Learning Objectives

By the end of this lab, you will be able to:
- Create custom agent state with LangGraph
- Implement state management for tracking conversation context
- Integrate with external APIs (Langflow endpoint)
- Build human-in-the-loop approval workflow guardrails
- Implement privacy guardrails to prevent unauthorized data access
- Handle conditional logic based on business rules

### Implementing the following Guardrails
**Leave Limit Approval**: Requires manager approval for leave requests exceeding the threshold


## Lab Steps
### Pre-requisites
1. Create a free Github account using the following link: https://github.com/signup
2. Enter the verification email sent to your email


### Step 1: Set Up Github CodeSpaces

1. Open the following Public Repo Template: 
    ```
    https://github.com/petriehd/AgenticAIBootcamp-Lab3-Starter
    ```
2. Select `Use this template` followed by `Open in a codespace`

    <img width="886" height="375" alt="image" src="https://github.com/user-attachments/assets/61638f2d-8b7e-4ea8-82af-07980fc8a739" />

    This has now created a hosted, uniform development environment with all required packages pre-installed

3. Test that it works by running main, and ensuring the python version is **3.11** using:
    ```
    python main.py
    ```

4. Open the `.env` file and enter the following details which were saved from lab 2:
    - Langflow_API_URL
    - Langflow_API_KEY
    - Organisation ID


### Step 2: Define Agent State

Create a file named `agent_state.py`:

```python
from typing import TypedDict, Annotated, Optional
from langgraph.graph import add_messages

class AgentState(TypedDict):
    """
    State object for the HR Agent.
    Tracks all relevant information throughout the conversation.
    """
    # Conversation history
    messages: Annotated[list, add_messages]

    # Current user information (from authentication/login)
    current_user_name: Optional[str]

    # Leave request details
    leave_type: Optional[str]  # Annual, sick, personal
    start_date: Optional[str]
    end_date: Optional[str]
    days_requested: Optional[int]
    leave_balance: Optional[int]

    # Leave approval workflow state
    requires_approval: bool
    approval_status: Optional[str]  # pending, approved, rejected
    approval_reason: Optional[str]

    # Agent response
    agent_response: Optional[str]

    # Error handling
    error: Optional[str]
```

**Key Concepts**:
- `TypedDict` provides type hints for state fields
- `Annotated[list, add_messages]` automatically manages message history
- State persists across all nodes in the graph
- Optional fields allow gradual state building

### Step 3: Create Langflow Integration

Create a file named `langflow_client.py`:

**Note**: This client now parses the structured JSON responses configured in Lab 2, enabling automatic state population in LangGraph.

```python
import requests
import os
import json
import uuid
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class LangflowClient:
    """
    Client for interacting with the Langflow endpoint created in Lab 2.
    Parses structured JSON responses to populate agent state.
    """

    def __init__(self):
        self.url = os.getenv("LANGFLOW_API_URL")
        self.api_key = os.getenv("LANGFLOW_API_KEY")
        self.org_id = os.getenv("LANGFLOW_ORG_ID")
        self.session_id = str(uuid.uuid4())
        self.enable_fallback = os.getenv("ENABLE_FALLBACK_PARSING", "true").lower() == "true"

    def query(self, message: str) -> Dict[str, Any]:
        """
        Send a query to the Langflow API and return parsed response.
        
        Returns:
            Dictionary containing:
            - conversational_response: Natural language response
            - query_flag: Boolean indicating if this is a simple query
            - data: Dictionary with structured fields (employee_id, leave_balance, etc.)
            - raw_text: Original response text (for fallback parsing)
        """
        payload = {
            "output_type": "chat",
            "input_type": "chat",
            "input_value": message,
            "session_id": self.session_id
        }

        headers = {
            "X-DataStax-Current-Org": self.org_id,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = requests.post(self.url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            # Extract the text response from Langflow output
            raw_text = result.get("outputs", [{}])[0].get("outputs", [{}])[0].get("results", {}).get("message", {}).get("text", "No response")
            
            # Try to parse as JSON
            try:
                parsed_json = json.loads(raw_text)
                
                # Validate expected structure
                if "conversational_response" in parsed_json and "query_flag" in parsed_json:
                    return {
                        "conversational_response": parsed_json.get("conversational_response", ""),
                        "query_flag": parsed_json.get("query_flag", True),
                        "data": parsed_json.get("data", {}),
                        "raw_text": raw_text,
                        "parsed": True
                    }
            except json.JSONDecodeError:
                # JSON parsing failed - will use fallback if enabled
                pass
            
            # Return raw text for fallback parsing
            return {
                "conversational_response": raw_text,
                "query_flag": True,
                "data": {},
                "raw_text": raw_text,
                "parsed": False
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error making API request: {e}")
        except Exception as e:
            raise Exception(f"Error processing response: {e}")


# Usage example
if __name__ == "__main__":
    client = LangflowClient()
    response = client.query("What is my leave balance?")
    print(f"Conversational: {response['conversational_response']}")
    print(f"Query Flag: {response['query_flag']}")
    print(f"Data: {response['data']}")
```

**Key Features**:
- **JSON Parsing**: Automatically parses structured responses from Lab 2
- **Fallback Support**: Returns raw text if JSON parsing fails
- **Type Safety**: Returns consistent dictionary structure
- **Error Handling**: Graceful degradation for malformed responses

### Step 4: Implement Agent Nodes

Create a file named `agent_nodes.py`:

**Important Changes**: The `call_langflow_node` now uses structured JSON data from the Langflow response instead of regex extraction. The `extract_leave_info()` function is kept as a fallback for backward compatibility.

**Key Updates**:
1. **Structured Data Extraction**: Directly uses the `data` object from JSON response
2. **Fallback Parsing**: Uses regex extraction only when `ENABLE_FALLBACK_PARSING=true` and JSON parsing fails
3. **Query Flag Handling**: Skips data extraction for simple queries (`query_flag=true`)

```python
async def call_langflow_node(state: AgentState) -> dict:
    """
    Node that calls the Langflow API to process the user's query.
    Now uses structured JSON responses from Lab 2.
    
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
        
        # Fallback to regex extraction if enabled and JSON parsing failed
        elif not response.get("parsed", True) and langflow_client.enable_fallback:
            leave_info = extract_leave_info(response.get("raw_text", ""))
            updates.update(leave_info)
    
    except Exception as e:
        updates["error"] = str(e)
        updates["agent_response"] = "I encountered an error processing your request."
    
    return updates


def extract_leave_info(text: str) -> Dict[str, Any]:
    """
    DEPRECATED: Fallback function for extracting leave info from natural language.
    Only used when ENABLE_FALLBACK_PARSING=true and JSON parsing fails.
    
    Extract leave request information from text using regex patterns.
    """
    info: Dict[str, Any] = {}
    
    # Extract number of days
    days_match = re.search(r'(\d+)\s*days?', text, re.IGNORECASE)
    if days_match:
        info["days_requested"] = int(days_match.group(1))
    
    # Extract leave type
    leave_types = ["vacation", "sick", "personal"]
    for leave_type in leave_types:
        if leave_type in text.lower():
            info["leave_type"] = leave_type
            break
    
    # Extract dates (YYYY-MM-DD format)
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    dates = re.findall(date_pattern, text)
    if len(dates) >= 2:
        info["start_date"] = dates[0]
        info["end_date"] = dates[1]
    
    return info
```

See the complete implementation in the accompanying `agent_nodes.py` file.

### Step 5: Build the LangGraph

Create a file named `hr_agent_graph.py`:

See the complete implementation in the accompanying `hr_agent_graph.py` file.

### Step 6: Implement Guardrails

The below logic will be added to `agent_nodes.py`

**Leave Limit Guardrail**: Requires human approval for leave requests exceeding the threshold

These functions handle the human-in-the-loop approval for extended leave requests:

```python
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
```

**Key Features**:
- **Leave Limits**: Human-in-the-loop approval workflow for extended leave requests
- **Clear Messaging**: Provides context for denial or approval decisions

### Step 7: Create Main Application

In `main.py`, clear the file.

See the complete implementation in the accompanying `main.py` file.

### Step 8: Test the Agent

Run your agent with different scenarios:

**Test 1: Simple Query (No Approval)**
```bash
python main.py
```
```
Enter your name: David Kim
You: What is my current leave balance?
```
Expected: Agent queries Langflow API, returns balance, no approval needed (accessing own data).

**Test 2: Small Leave Request (Auto-Approve)**
```bash
python main.py
```
```
Enter your name: David Kim
You: I want to take 3 days off next week for vacation.
```
Expected: Agent processes request, auto-approves (under threshold).

**Test 3: Large Leave Request (Requires Leave Approval)**
```bash
python main.py
```
```
Enter your name: David Kim
You: I need to take 10 days off in December for vacation.
```
Expected: Agent pauses, requests leave approval, processes based on decision.
