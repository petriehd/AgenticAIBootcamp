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
- Build human-in-the-loop approval workflows
- Handle conditional logic based on business rules
- Deploy and test a production-ready agent

## Prerequisites

- Completion of Lab 2
- Python 3.8 or higher installed
- Langflow API endpoint and credentials from Lab 2
- Basic Python programming knowledge
- Familiarity with async/await patterns

## Architecture

In this lab, you'll build the following architecture:

```
User Request → LangGraph Agent → AgentState (tracks context)
                                → Langflow API (agent logic)
                                → Conditional Logic (approval check)
                                → Human Approval (if needed)
                                → Response
```

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
LANGFLOW_API_URL=https://your-langflow-instance.com/api/v1/run/hr-agent-api
LANGFLOW_API_KEY=your_api_key_here
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
    
    # Employee information
    employee_id: Optional[str]
    employee_name: Optional[str]
    
    # Leave request details
    leave_type: Optional[str]  # vacation, sick, personal
    start_date: Optional[str]
    end_date: Optional[str]
    days_requested: Optional[int]
    leave_balance: Optional[int]
    
    # Approval workflow
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

See the complete implementation in the accompanying `langflow_client.py` file.

### Step 4: Implement Agent Nodes

Create a file named `agent_nodes.py`:

See the complete implementation in the accompanying `agent_nodes.py` file.

### Step 5: Build the LangGraph

Create a file named `hr_agent_graph.py`:

See the complete implementation in the accompanying `hr_agent_graph.py` file.

### Step 6: Implement Human-in-the-Loop

The human-in-the-loop functionality is the key differentiator in this lab. Let's understand how it works:

**Approval Logic**:
```python
def should_require_approval(state: AgentState) -> str:
    """
    Determines if human approval is required based on business rules.
    """
    days_requested = state.get("days_requested", 0)
    threshold = int(os.getenv("APPROVAL_THRESHOLD_DAYS", 5))
    
    if days_requested > threshold:
        return "approval_required"
    return "auto_approve"
```

**Human Approval Node**:
```python
async def human_approval_node(state: AgentState) -> AgentState:
    """
    Pauses execution and requests human approval.
    """
    print("\n" + "="*50)
    print("APPROVAL REQUIRED")
    print("="*50)
    print(f"Employee: {state.get('employee_name', 'Unknown')}")
    print(f"Leave Type: {state.get('leave_type', 'Unknown')}")
    print(f"Duration: {state.get('days_requested', 0)} days")
    print(f"Dates: {state.get('start_date')} to {state.get('end_date')}")
    print(f"Current Balance: {state.get('leave_balance', 0)} days")
    print("="*50)
    
    # Get human input
    while True:
        decision = input("\nApprove this request? (yes/no): ").lower()
        if decision in ['yes', 'no']:
            break
        print("Please enter 'yes' or 'no'")
    
    reason = input("Reason (optional): ")
    
    state["approval_status"] = "approved" if decision == "yes" else "rejected"
    state["approval_reason"] = reason if reason else "No reason provided"
    
    return state
```

**Key Features**:
- Pauses agent execution
- Displays all relevant information
- Captures human decision
- Records approval reason for audit trail

### Step 7: Create Main Application

Create a file named `main.py`:

See the complete implementation in the accompanying `main.py` file.

### Step 8: Test the Agent

Run your agent with different scenarios:

**Test 1: Simple Query (No Approval)**
```bash
python main.py
```
```
You: What is my current leave balance? Employee ID: EMP12345
```
Expected: Agent queries Langflow API, returns balance, no approval needed.

**Test 2: Small Leave Request (Auto-Approve)**
```bash
python main.py
```
```
You: I want to take 3 days off next week for vacation. Employee ID: EMP12345
```
Expected: Agent processes request, auto-approves (under threshold).

**Test 3: Large Leave Request (Requires Approval)**
```bash
python main.py
```
```
You: I need to take 10 days off in December for vacation. Employee ID: EMP12345
```
Expected: Agent pauses, requests human approval, processes based on decision.

**Test 4: Error Handling**
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
graph.add_node("call_langflow", call_langflow_node)
graph.add_node("check_approval", check_approval_node)
graph.add_node("human_approval", human_approval_node)

graph.add_conditional_edges(
    "check_approval",
    should_require_approval,
    {
        "approval_required": "human_approval",
        "auto_approve": "finalize"
    }
)
```
- Nodes represent processing steps
- Edges define flow between nodes
- Conditional edges enable branching logic

### Human-in-the-Loop
```python
async def human_approval_node(state: AgentState) -> AgentState:
    decision = input("Approve this request? (yes/no): ")
    state["approval_status"] = "approved" if decision == "yes" else "rejected"
    return state
```
- Pauses execution for human input
- Captures decision and reasoning
- Resumes execution after approval

## Key Takeaways

1. **State Management**: LangGraph's state management provides a clean way to track context across agent interactions

2. **Conditional Logic**: Business rules can be implemented as conditional edges, enabling complex workflows

3. **Human-in-the-Loop**: Critical decisions can be routed to humans while maintaining automated processing for routine tasks

4. **API Integration**: External services (like Langflow) can be seamlessly integrated as nodes in the graph

5. **Production Ready**: LangGraph provides features like checkpointing, error handling, and monitoring for production deployments

6. **Flexibility**: Full control over agent behavior allows customization for specific business requirements

## Troubleshooting

**Issue**: Agent doesn't pause for approval
- **Solution**: Check the `should_require_approval` logic. Verify threshold configuration in `.env` file.

**Issue**: Langflow API calls fail
- **Solution**: Verify API URL and key in `.env`. Check network connectivity. Review Langflow logs.

**Issue**: State not persisting between nodes
- **Solution**: Ensure all nodes return updated state. Check that state keys match the TypedDict definition.

**Issue**: Async errors
- **Solution**: Ensure all async functions are properly awaited. Use `asyncio.run()` for top-level execution.

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