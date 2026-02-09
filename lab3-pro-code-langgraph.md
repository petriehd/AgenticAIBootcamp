# Lab 3: Pro Code - Building with LangGraph

## Overview

In this lab, you'll implement advanced agent logic using LangGraph and Python. You'll create a custom agent with state management and human-in-the-loop approval workflows. This lab demonstrates how to build production-ready agentic systems with fine-grained control over agent behavior.

**Estimated Time**: 45 minutes

**Tools**: LangGraph, Python, Langflow API

**Data**: Langflow API endpoint from Lab 2

## Learning Objectives

By the end of this lab, you will be able to:
- Create custom agent state with LangGraph
- Implement state management for tracking conversation context
- Integrate with external APIs (Langflow endpoint)
- Build human-in-the-loop approval workflows for multiple scenarios
- Implement privacy guardrails to prevent unauthorized data access
- Handle conditional logic based on business rules
- Deploy and test a production-ready agent

## Prerequisites

- Completion of Lab 2
- Python 3.8 or higher installed
- Langflow API endpoint and credentials from Lab 2
- Basic Python programming knowledge
- Familiarity with async/await patterns

## Why Guardrails Matter

In Lab 2, we built a powerful HR agent that can access employee leave balances. However, there's a security gap: **any user can query any employee's leave balance** simply by providing a different employee ID. This is a significant privacy concern.

In this lab, we'll implement two critical guardrails:

1. **Privacy Protection**: Before accessing leave balance data, we verify if the user is authorized to view that data. If a user attempts to access another employee's information, a human-in-the-loop approval is required.

2. **Leave Request Limits**: Extended leave requests (over a configurable threshold) require manager approval before processing.

These guardrails demonstrate how LangGraph enables fine-grained control over agent behavior that isn't possible with simpler agent frameworks.

## Architecture

In this lab, you'll build the following architecture:

```
User Request → LangGraph Agent → AgentState (tracks context)
                                → Langflow API (agent logic)
                                → Privacy Check (leave balance access)
                                → Human Approval (if accessing others' data)
                                → Leave Limit Check (days requested)
                                → Human Approval (if over threshold)
                                → Response
```

**Key Guardrails**:
1. **Privacy Protection**: Prevents users from accessing other employees' leave balances without authorization
2. **Leave Limit Approval**: Requires manager approval for leave requests exceeding the threshold

## Lab Steps

### Step 1: Set Up Python Environment

1. Create a new directory for your project:
```bash
mkdir hr-agent-langgraph
cd hr-agent-langgraph
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install langgraph langchain langchain-openai requests python-dotenv
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

    # Current user information (the person making the request)
    current_user_id: Optional[str]
    current_user_name: Optional[str]

    # Target employee information (whose data is being accessed)
    target_employee_id: Optional[str]
    target_employee_name: Optional[str]

    # Privacy check (accessing other's data)
    is_accessing_own_data: bool
    privacy_approval_status: Optional[str]  # pending, approved, rejected
    privacy_approval_reason: Optional[str]

    # Leave request details
    leave_type: Optional[str]  # vacation, sick, personal
    start_date: Optional[str]
    end_date: Optional[str]
    days_requested: Optional[int]
    leave_balance: Optional[int]

    # Leave limit approval workflow
    requires_leave_approval: bool
    leave_approval_status: Optional[str]  # pending, approved, rejected
    leave_approval_reason: Optional[str]

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
    Client for interacting with the Langflow API.
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

Update your `.env` file with the additional configuration:
```
LANGFLOW_API_URL=https://aws-us-east-2.langflow.datastax.com/lf/<your-project-id>/api/v1/run/<your-flow-id>
LANGFLOW_API_KEY=your_api_key_here
LANGFLOW_ORG_ID=your_org_id_here
APPROVAL_THRESHOLD_DAYS=5
```

### Step 4: Implement Agent Nodes

Create a file named `agent_nodes.py`:

See the complete implementation in the accompanying `agent_nodes.py` file.

### Step 5: Build the LangGraph

Create a file named `hr_agent_graph.py`:

See the complete implementation in the accompanying `hr_agent_graph.py` file.

### Step 6: Implement Human-in-the-Loop Guardrails

The human-in-the-loop functionality is the key differentiator in this lab. We implement two types of guardrails:

1. **Privacy Guardrail**: Prevents unauthorized access to other employees' leave balances
2. **Leave Limit Guardrail**: Requires approval for leave requests exceeding the threshold

#### Privacy Check Logic

```python
def check_privacy_access(state: AgentState) -> str:
    """
    Determines if the user is trying to access another employee's data.
    """
    current_user = state.get("current_user_id")
    target_employee = state.get("target_employee_id")

    # If no target specified, assume accessing own data
    if not target_employee:
        return "own_data"

    # Check if accessing own data
    if current_user == target_employee:
        return "own_data"

    # Accessing someone else's data - requires approval
    return "other_employee_data"
```

#### Privacy Approval Node

```python
async def privacy_approval_node(state: AgentState) -> AgentState:
    """
    Pauses execution and requests approval for accessing another employee's data.
    This is a critical security guardrail to prevent unauthorized data access.
    """
    print("\n" + "="*60)
    print("⚠️  PRIVACY CHECK - AUTHORIZATION REQUIRED")
    print("="*60)
    print(f"Requesting User: {state.get('current_user_name', 'Unknown')} ({state.get('current_user_id', 'Unknown')})")
    print(f"Attempting to access data for: {state.get('target_employee_name', 'Unknown')} ({state.get('target_employee_id', 'Unknown')})")
    print("-"*60)
    print("This request is attempting to access another employee's")
    print("leave balance information. This requires authorization.")
    print("="*60)

    # Get human input
    while True:
        decision = input("\nAuthorize this data access? (yes/no): ").lower()
        if decision in ['yes', 'no']:
            break
        print("Please enter 'yes' or 'no'")

    reason = input("Reason for decision: ")

    state["privacy_approval_status"] = "approved" if decision == "yes" else "rejected"
    state["privacy_approval_reason"] = reason if reason else "No reason provided"

    if decision == "no":
        state["agent_response"] = "Access denied. You are not authorized to view this employee's leave balance."

    return state
```

#### Leave Limit Approval Logic

```python
def should_require_leave_approval(state: AgentState) -> str:
    """
    Determines if human approval is required for leave duration.
    """
    days_requested = state.get("days_requested", 0)
    threshold = int(os.getenv("APPROVAL_THRESHOLD_DAYS", 5))

    if days_requested and days_requested > threshold:
        return "approval_required"
    return "auto_approve"
```

#### Leave Limit Approval Node

```python
async def leave_approval_node(state: AgentState) -> AgentState:
    """
    Pauses execution and requests human approval for extended leave.
    """
    print("\n" + "="*50)
    print("LEAVE APPROVAL REQUIRED")
    print("="*50)
    print(f"Employee: {state.get('target_employee_name', 'Unknown')}")
    print(f"Leave Type: {state.get('leave_type', 'Unknown')}")
    print(f"Duration: {state.get('days_requested', 0)} days")
    print(f"Dates: {state.get('start_date')} to {state.get('end_date')}")
    print(f"Current Balance: {state.get('leave_balance', 0)} days")
    print("="*50)

    # Get human input
    while True:
        decision = input("\nApprove this leave request? (yes/no): ").lower()
        if decision in ['yes', 'no']:
            break
        print("Please enter 'yes' or 'no'")

    reason = input("Reason (optional): ")

    state["leave_approval_status"] = "approved" if decision == "yes" else "rejected"
    state["leave_approval_reason"] = reason if reason else "No reason provided"

    return state
```

**Key Features**:
- **Privacy Protection**: Catches attempts to access other employees' data before the query is executed
- **Audit Trail**: Records who requested access and the authorization decision
- **Leave Limits**: Maintains the existing approval workflow for extended leave requests
- **Clear Messaging**: Provides context for each approval decision

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
Current User ID: EMP12345
You: What is my current leave balance?
```
Expected: Agent queries Langflow API, returns balance, no approval needed (accessing own data).

**Test 2: Accessing Another Employee's Data (Privacy Check)**
```bash
python main.py
```
```
Current User ID: EMP12345
You: What is the leave balance for employee EMP67890?
```
Expected: Agent pauses for privacy approval. If denied, access is blocked. If approved, query proceeds.

**Test 3: Small Leave Request (Auto-Approve)**
```bash
python main.py
```
```
Current User ID: EMP12345
You: I want to take 3 days off next week for vacation.
```
Expected: Agent processes request, auto-approves (under threshold).

**Test 4: Large Leave Request (Requires Leave Approval)**
```bash
python main.py
```
```
Current User ID: EMP12345
You: I need to take 10 days off in December for vacation.
```
Expected: Agent pauses, requests leave approval, processes based on decision.

**Test 5: Manager Checking Team Member's Balance (Both Guardrails)**
```bash
python main.py
```
```
Current User ID: MGR001
You: What is the leave balance for EMP12345? They want to take 10 days off.
```
Expected: First triggers privacy approval (accessing another's data), then if approved, triggers leave approval (over threshold).

**Test 6: Error Handling**
```bash
python main.py
```
```
You: Submit leave request without providing employee ID
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
logger.info(f"Processing request for employee {employee_id}")
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
    employee_id: str

@app.post("/agent")
async def run_agent(request: AgentRequest):
    result = await agent_graph.ainvoke({
        "messages": [{"role": "user", "content": request.message}],
        "employee_id": request.employee_id
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
    employee_id: Optional[str]
    requires_approval: bool
```
- State persists across all nodes
- Each node can read and update state
- Type hints ensure data consistency

### Graph Structure
```python
# Add all nodes
graph.add_node("parse_request", parse_request_node)
graph.add_node("check_privacy", check_privacy_node)
graph.add_node("privacy_approval", privacy_approval_node)
graph.add_node("call_langflow", call_langflow_node)
graph.add_node("check_leave_approval", check_leave_approval_node)
graph.add_node("leave_approval", leave_approval_node)
graph.add_node("finalize", finalize_node)

# Privacy check - first guardrail
graph.add_conditional_edges(
    "check_privacy",
    check_privacy_access,
    {
        "own_data": "call_langflow",           # Accessing own data - proceed
        "other_employee_data": "privacy_approval"  # Accessing others - require approval
    }
)

# Leave limit check - second guardrail
graph.add_conditional_edges(
    "check_leave_approval",
    should_require_leave_approval,
    {
        "approval_required": "leave_approval",
        "auto_approve": "finalize"
    }
)
```
- **Privacy Check** runs first to catch unauthorized access attempts
- **Leave Limit Check** runs after to handle extended leave requests
- Each guardrail has its own approval workflow

### Human-in-the-Loop (Multiple Guardrails)
```python
# Privacy guardrail
async def privacy_approval_node(state: AgentState) -> AgentState:
    decision = input("Authorize access to this employee's data? (yes/no): ")
    state["privacy_approval_status"] = "approved" if decision == "yes" else "rejected"
    return state

# Leave limit guardrail
async def leave_approval_node(state: AgentState) -> AgentState:
    decision = input("Approve this leave request? (yes/no): ")
    state["leave_approval_status"] = "approved" if decision == "yes" else "rejected"
    return state
```
- **Privacy approval**: Prevents unauthorized access to others' data
- **Leave approval**: Controls extended leave requests
- Both capture decisions and reasoning for audit trails

## Key Takeaways

1. **State Management**: LangGraph's state management provides a clean way to track context across agent interactions

2. **Privacy Guardrails**: Implementing access controls prevents unauthorized data access - a critical security consideration for any agent handling sensitive employee data

3. **Multiple Guardrails**: Complex workflows may require multiple human-in-the-loop checkpoints (privacy + leave limits in our case)

4. **Conditional Logic**: Business rules can be implemented as conditional edges, enabling complex workflows

5. **Human-in-the-Loop**: Critical decisions can be routed to humans while maintaining automated processing for routine tasks

6. **API Integration**: External services (like Langflow) can be seamlessly integrated as nodes in the graph

7. **Production Ready**: LangGraph provides features like checkpointing, error handling, and monitoring for production deployments

8. **Flexibility**: Full control over agent behavior allows customization for specific business requirements

## Troubleshooting

**Issue**: Privacy check not triggering
- **Solution**: Verify that `current_user_id` and `target_employee_id` are being correctly parsed from the user's request. Check the `check_privacy_access` logic.

**Issue**: Agent doesn't pause for leave approval
- **Solution**: Check the `should_require_leave_approval` logic. Verify `APPROVAL_THRESHOLD_DAYS` configuration in `.env` file.

**Issue**: Langflow API calls fail
- **Solution**: Verify API URL, key, and org ID in `.env`. Check network connectivity. Ensure headers include `X-DataStax-Current-Org`. Review Langflow logs.

**Issue**: State not persisting between nodes
- **Solution**: Ensure all nodes return updated state. Check that state keys match the TypedDict definition.

**Issue**: Async errors
- **Solution**: Ensure all async functions are properly awaited. Use `asyncio.run()` for top-level execution.

**Issue**: User can still access others' data after denial
- **Solution**: Ensure the privacy approval node sets `agent_response` with a denial message when access is rejected, and the workflow routes to finalize without calling Langflow.

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