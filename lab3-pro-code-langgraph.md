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

## Prerequisites

- Access to Github CodeSpaces
- Langflow API endpoint and credentials from Lab 2

## Architecture

In this lab, you'll build the following architecture:

```
User Request → LangGraph Agent → Privacy Check (deny if other employee name mentioned)
                                     ↓ (if proceed)
                                → Langflow API (agent logic)
                                → Leave Limit Check (days requested)
                                → Human Approval (if over threshold)
                                → Response
```

**Key Guardrails**:
1. **Privacy Protection**: Automatically denies access if user mentions another employee's name in their request
2. **Leave Limit Approval**: Requires manager approval for leave requests exceeding the threshold


## Lab Steps

### Step 1: Set Up Github CodeSpaces

# Need to add in codespaces

3. Install required packages:
```bash
pip install langgraph langchain requests python-dotenv
```

4. Create a `.env` file for configuration:
```bash
touch .env
```

5. Add your credentials to `.env`:
```
LANGFLOW_API_URL=https://aws-us-east-2.langflow.datastax.com/lf/<your-project-id>/api/v1/run/<your-flow-id>
LANGFLOW_API_KEY=your_api_key_here
LANGFLOW_ORG_ID=your_org_id_here
APPROVAL_THRESHOLD_DAYS=5
```

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

```python
import requests
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

class LangflowClient:
    """
    Client for interacting with the Langflow endpoint created in lab 2.
    """

    def __init__(self):
        self.url = os.getenv("LANGFLOW_API_URL")
        self.api_key = os.getenv("LANGFLOW_API_KEY")
        self.org_id = os.getenv("LANGFLOW_ORG_ID")
        self.session_id = str(uuid.uuid4())

    def query(self, message: str) -> str:
        """
        Send a query to the Langflow API and return the response.
        """
        payload = {
            "output_type": "chat",
            "input_type": "chat",
            "input_value": message
        }
        payload["session_id"] = self.session_id

        headers = {
            "X-DataStax-Current-Org": self.org_id,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = requests.request("POST", self.url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()
            # Extract the text response from Langflow output
            return result.get("outputs", [{}])[0].get("outputs", [{}])[0].get("results", {}).get("message", {}).get("text", "No response")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error making API request: {e}")
        except ValueError as e:
            raise Exception(f"Error parsing response: {e}")


# Usage example
if __name__ == "__main__":
    client = LangflowClient()
    response = client.query("What is the leave policy?")
    print(response)
```

### Step 4: Implement Agent Nodes

Create a file named `agent_nodes.py`:

See the complete implementation in the accompanying `agent_nodes.py` file.

### Step 5: Build the LangGraph

Create a file named `hr_agent_graph.py`:

See the complete implementation in the accompanying `hr_agent_graph.py` file.

### Step 6: Implement Guardrails

The below logic will be added to `agent_nodes.py`

1. **Privacy Guardrail**: Automatically denies access if user mentions another employee's name
2. **Leave Limit Guardrail**: Requires human approval for leave requests exceeding the threshold

#### Privacy Check

This is a simple function that checks if the user's message contains any employee name other than their own. If it does, access is denied:

```python
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

    latest_message = messages[-1].content
    current_user_name = state.get("current_user_name", "")

    # Look for patterns where user asks about another employee by name
    # Matches phrases like "for Alice", "employee Bob Smith", "Bob's leave"
    import re
    name_patterns = [
        r"for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",        # "for Alice" or "for Alice Smith"
        r"employee\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",    # "employee Bob"
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'s\s+leave",    # "Bob's leave"
    ]

    for pattern in name_patterns:
        matches = re.findall(pattern, latest_message)
        for name in matches:
            if name.lower() != current_user_name.lower():
                state["agent_response"] = (
                    f"Access denied. You can only access your own leave information, "
                    f"not data for employee {name}."
                )
                state["error"] = "Unauthorized access attempt"
                return "denied"

    # No other employee names mentioned - proceed
    return "proceed"
```

#### Leave Approval Logic

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
- **Privacy Protection**: Automatically denies attempts to access other employees' data
- **No Manual Approval for Privacy**: Privacy violations are blocked immediately, not sent for approval
- **Leave Limits**: Human-in-the-loop approval workflow for extended leave requests
- **Clear Messaging**: Provides context for denial or approval decisions

### Step 7: Create Main Application

Create a file named `main.py`:

See the complete implementation in the accompanying `main.py` file.

### Step 8: Test the Agent

Run your agent with different scenarios:

**Test 1: Simple Query - Own Data (No Approval)**
```bash
python main.py
```
```
Enter your name: Alice
You: What is my current leave balance?
```
Expected: Agent queries Langflow API, returns balance, no approval needed (accessing own data).

**Test 2: Accessing Another Employee's Data (Privacy Check - Automatic Denial)**
```bash
python main.py
```
```
Enter your name: Alice
You: What is the leave balance for employee Bob?
```
Expected: Agent immediately denies access with message: "Access denied. You can only access your own leave information, not data for employee Bob."

**Test 3: Small Leave Request (Auto-Approve)**
```bash
python main.py
```
```
Enter your name: Alice
You: I want to take 3 days off next week for vacation.
```
Expected: Agent processes request, auto-approves (under threshold).

**Test 4: Large Leave Request (Requires Leave Approval)**
```bash
python main.py
```
```
Enter your name: Alice
You: I need to take 10 days off in December for vacation.
```
Expected: Agent pauses, requests leave approval, processes based on decision.

**Test 5: Manager Checking Team Member's Balance (Privacy Denial)**
```bash
python main.py
```
```
Enter your name: Carol
You: What is the leave balance for Alice?
```
Expected: Access is immediately denied because Carol is trying to access Alice's data. In a real system, you would implement role-based access control to allow managers to view their team members' data.

**Test 6: Error Handling**
```bash
python main.py
```
```
You: Submit leave request without providing employee name
```
Expected: Agent handles gracefully, requests missing information.

### Step 9: Add Logging and Monitoring

Enhance your agent with logging:

```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'agent_log_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Add to your nodes
logger.info(f"Processing request for employee {employee_name}")
logger.warning(f"Approval required for {days_requested} days")
logger.error(f"Error calling Langflow API: {str(e)}")
```

### Step 10: Deploy and Scale

For production deployment:

1. **Containerize with Docker**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

2. **Add API Server**:
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AgentRequest(BaseModel):
    message: str
    employee_name: str

@app.post("/agent")
async def run_agent(request: AgentRequest):
    result = await agent_graph.ainvoke({
        "messages": [{"role": "user", "content": request.message}],
        "current_user_name": request.employee_name
    })
    return {"response": result["agent_response"]}
```

3. **Add Persistence**:
```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Add checkpointing for conversation history
checkpointer = SqliteSaver.from_conn_string("agent_checkpoints.db")
agent_graph = create_agent_graph(checkpointer=checkpointer)
```

## Understanding the Code

Let's break down the key components:

### State Management
```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    current_user_name: Optional[str]
    requires_approval: bool
```
- State persists across all nodes
- Each node can read and update state
- Type hints ensure data consistency

### Graph Structure
```python
# Add all nodes
workflow.add_node("call_langflow", call_langflow_node)
workflow.add_node("check_approval", check_approval_node)
workflow.add_node("human_approval", human_approval_node)
workflow.add_node("finalize", finalize_node)

# Start with privacy check as conditional entry point
workflow.set_conditional_entry_point(
    check_privacy_access,
    {
        "proceed": "call_langflow",
        "denied": "finalize"
    }
)

# Leave limit check - second guardrail
workflow.add_conditional_edges(
    "check_approval",
    should_require_approval,
    {
        "human_approval": "human_approval",
        "finalize": "finalize"
    }
)
```
- **Privacy Check** runs first as a conditional entry point - no separate node needed!
- **Leave Limit Check** runs after Langflow to handle extended leave requests
- Privacy violations are blocked immediately before any processing; leave approvals go through human review

### Privacy Guardrail (Simple & Automatic)
```python
def check_privacy_access(state: AgentState) -> str:
    """Check if message contains another employee's name"""
    latest_message = messages[-1]["content"]
    current_user_name = state.get("current_user_name", "")

    # Look for patterns where user asks about another employee by name
    name_patterns = [
        r"for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"employee\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'s\s+leave",
    ]

    for pattern in name_patterns:
        matches = re.findall(pattern, latest_message)
        for name in matches:
            if name.lower() != current_user_name.lower():
                state["agent_response"] = "Access denied..."
                return "denied"

    return "proceed"
```
- **Simple**: Regex patterns to detect other employee names in the message
- **Automatic denial**: No nodes, no complex logic - just check and route
- **Efficient**: Blocks unauthorized requests before calling any APIs
- **Leave approval**: Controls extended leave requests
- Both capture decisions and reasoning for audit trails

## Key Takeaways

1. **State Management**: LangGraph's state management provides a clean way to track context across agent interactions

2. **Privacy Guardrails**: Implementing automatic access controls prevents unauthorized data access - a critical security consideration for any agent handling sensitive employee data

3. **Automatic vs Manual Guardrails**: Some guardrails (like privacy) should automatically deny access, while others (like leave approvals) benefit from human-in-the-loop review

4. **Conditional Logic**: Business rules can be implemented as conditional edges, enabling complex workflows with different paths based on context

5. **Human-in-the-Loop**: Critical business decisions (like approving extended leave) can be routed to humans while maintaining automated processing for routine tasks and security violations

6. **API Integration**: External services (like Langflow) can be seamlessly integrated as nodes in the graph

7. **Production Ready**: LangGraph provides features like checkpointing, error handling, and monitoring for production deployments

8. **Flexibility**: Full control over agent behavior allows customization for specific business requirements and security policies

## Troubleshooting

**Issue**: Privacy check not denying access to other employees' data
- **Solution**: Verify that `current_user_name` is set when the conversation starts (from authentication). Check the regex patterns match the name formats used in your messages. Test by adding a print statement in `check_privacy_access` to see what names are being matched.

**Issue**: Agent doesn't pause for leave approval
- **Solution**: Check the `should_require_approval` logic and verify `APPROVAL_THRESHOLD_DAYS` in `.env` file. Ensure `days_requested` is being extracted correctly from the Langflow response (check the `extract_leave_info` function).

**Issue**: Langflow API calls fail
- **Solution**: Verify API URL, key, and org ID in `.env`. Check network connectivity. Ensure headers include `X-DataStax-Current-Org`. Review Langflow logs.

**Issue**: State not persisting between nodes
- **Solution**: Ensure all nodes return updated state. Check that state keys match the TypedDict definition in `agent_state.py`.

**Issue**: Privacy check bypassed or not working
- **Solution**: Verify the conditional entry point is set correctly with `set_conditional_entry_point(check_privacy_access, {...})`. Make sure `current_user_name` is provided in the initial state when invoking the graph.

## Next Steps

Congratulations! You've completed all three labs and built a comprehensive HR agent system:

1. **Lab 1**: No-code agent with Orchestrate
2. **Lab 2**: Low-code agent with Langflow
3. **Lab 3**: Pro-code agent with LangGraph

You now have the skills to:
- Build agents at different complexity levels
- Integrate multiple data sources and tools
- Implement business logic and approval workflows
- Deploy production-ready agentic systems

### Further Enhancements

Consider adding:
- Multi-agent collaboration (multiple specialized agents)
- Advanced memory systems (long-term conversation history)
- Streaming responses for better UX
- Integration with enterprise systems (SAP, Workday, etc.)
- Analytics and reporting dashboards
- A/B testing for agent improvements

## Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [Human-in-the-Loop Patterns](https://langchain-ai.github.io/langgraph/how-tos/human-in-the-loop/)
- [Production Deployment Guide](https://langchain-ai.github.io/langgraph/deployment/)

## Code Files

All code for this lab is available in the `lab3-code/` directory:
- `agent_state.py` - State definition
- `langflow_client.py` - Langflow API integration
- `agent_nodes.py` - Graph node implementations
- `hr_agent_graph.py` - Graph construction
- `main.py` - Main application
- `requirements.txt` - Python dependencies
- `.env.example` - Environment configuration template