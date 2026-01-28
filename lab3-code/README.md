# Lab 3 Code - HR Agent with LangGraph

This directory contains the complete Python implementation for Lab 3 of the Agentic AI Bootcamp.

## Overview

This implementation demonstrates:
- Custom agent state management with LangGraph
- Integration with Langflow API endpoint from Lab 2
- Human-in-the-loop approval workflows
- Conditional logic based on business rules
- Production-ready error handling and logging

## File Structure

```
lab3-code/
├── agent_state.py          # State definition for the agent
├── langflow_client.py      # Langflow API integration
├── agent_nodes.py          # Graph node implementations
├── hr_agent_graph.py       # Graph construction and compilation
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
└── README.md              # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your credentials
# - LANGFLOW_API_URL: Your Langflow endpoint from Lab 2
# - LANGFLOW_API_KEY: Your Langflow API key
# - APPROVAL_THRESHOLD_DAYS: Number of days threshold (default: 5)
```

### 3. Run the Agent

**Interactive Mode** (default):
```bash
python main.py
```

**Demo Mode** (runs predefined scenarios):
```bash
python main.py demo
```

## Usage Examples

### Interactive Mode

```
$ python main.py

============================================================
HR AGENT - INTERACTIVE MODE
============================================================
Type 'quit' or 'exit' to end the session
Type 'help' for example queries
============================================================

Enter your Employee ID (or press Enter to skip): EMP12345

------------------------------------------------------------
You: What is my current leave balance?

============================================================
HR AGENT PROCESSING
============================================================
User: What is my current leave balance?
Employee ID: EMP12345
============================================================

[Agent processes request...]

============================================================
AGENT RESPONSE
============================================================
Your current leave balance is:
- Vacation days: 15
- Sick days: 10
- Personal days: 3
============================================================
```

### Demo Mode

Demo mode runs three predefined scenarios:
1. Check leave balance
2. Small leave request (auto-approved)
3. Large leave request (requires human approval)

```bash
python main.py demo
```

## Human-in-the-Loop Approval

When a leave request exceeds the threshold (default: 5 days), the agent will pause and request human approval:

```
============================================================
HUMAN APPROVAL REQUIRED
============================================================
Employee ID: EMP12345
Employee Name: John Doe
Leave Type: vacation
Duration: 10 days
Dates: 2024-12-20 to 2024-12-30
Current Balance: 15 days
============================================================

Approve this request? (yes/no): yes
Reason (optional): Approved for year-end vacation

Decision recorded: approved
============================================================
```

## Configuration

### Environment Variables

- `LANGFLOW_API_URL`: Langflow API endpoint from Lab 2
- `LANGFLOW_API_KEY`: API key for authentication
- `APPROVAL_THRESHOLD_DAYS`: Number of days that trigger approval (default: 5)
- `DEBUG`: Set to `true` to see detailed state information

### Approval Threshold

The approval threshold determines when human approval is required. Modify in `.env`:

```
APPROVAL_THRESHOLD_DAYS=5
```

Requests for more than this number of days will require human approval.

## Code Architecture

### State Management

The `AgentState` class defines all information tracked throughout the conversation:
- Conversation history
- Employee information
- Leave request details
- Approval workflow state
- Error handling

### Graph Structure

The agent workflow consists of four main nodes:

1. **call_langflow**: Calls the Langflow API to process the query
2. **check_approval**: Determines if approval is needed based on business rules
3. **human_approval**: Pauses for human decision (conditional)
4. **finalize**: Prepares the final response

### Conditional Logic

The graph uses conditional edges to route requests:
- If `days_requested > threshold` → Human approval required
- Otherwise → Auto-approve

## Troubleshooting

### Import Errors

If you see import errors for `langgraph` or `dotenv`:
```bash
pip install -r requirements.txt
```

### API Connection Errors

If the Langflow API call fails:
1. Verify `LANGFLOW_API_URL` in `.env`
2. Check `LANGFLOW_API_KEY` is correct
3. Ensure Langflow endpoint from Lab 2 is running
4. Test the endpoint with curl:
```bash
curl -X POST $LANGFLOW_API_URL \
  -H "Authorization: Bearer $LANGFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": "test"}'
```

### Approval Not Triggering

If human approval doesn't trigger when expected:
1. Check `APPROVAL_THRESHOLD_DAYS` in `.env`
2. Verify `days_requested` is being extracted correctly
3. Enable debug mode: `DEBUG=true` in `.env`

## Extending the Code

### Adding New Nodes

1. Define the node function in `agent_nodes.py`:
```python
async def my_custom_node(state: AgentState) -> AgentState:
    # Your logic here
    return state
```

2. Add to the graph in `hr_agent_graph.py`:
```python
workflow.add_node("my_node", my_custom_node)
workflow.add_edge("previous_node", "my_node")
```

### Adding New State Fields

1. Update `AgentState` in `agent_state.py`:
```python
class AgentState(TypedDict):
    # ... existing fields ...
    my_new_field: Optional[str]
```

2. Use in your nodes:
```python
state["my_new_field"] = "some value"
```

### Custom Approval Logic

Modify `should_require_approval` in `agent_nodes.py`:
```python
def should_require_approval(state: AgentState) -> str:
    # Add your custom logic
    if state.get("leave_type") == "sick" and state.get("days_requested", 0) > 3:
        return "human_approval"
    # ... existing logic ...
```

## Next Steps

After completing this lab:
1. Experiment with different approval thresholds
2. Add custom business rules
3. Integrate with real HR systems
4. Deploy as a web service with FastAPI
5. Add conversation history persistence
6. Implement multi-agent collaboration

## Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [Human-in-the-Loop Patterns](https://langchain-ai.github.io/langgraph/how-tos/human-in-the-loop/)