"""
HR Agent Graph Construction
Builds the LangGraph workflow with all nodes and edges
"""

from langgraph.graph import StateGraph, END
from agent_state import AgentState
from agent_nodes import (
    call_langflow_node,
    check_approval_node,
    human_approval_node,
    finalize_node,
    should_require_approval
)


def create_agent_graph():
    """
    Creates and compiles the HR agent graph
    
    Returns:
        Compiled LangGraph workflow
    """
    # Initialize the graph with our state schema
    workflow = StateGraph(AgentState)

    # Add nodes to the graph
    workflow.add_node("call_langflow", call_langflow_node)
    workflow.add_node("check_approval", check_approval_node)
    workflow.add_node("human_approval", human_approval_node)
    workflow.add_node("finalize", finalize_node)

    # Set entry point to call_langflow
    workflow.set_entry_point("call_langflow")

    # Call Langflow -> Check if approval needed
    workflow.add_edge("call_langflow", "check_approval")

    # Check Approval -> Conditional routing
    # If approval required -> Human Approval
    # If auto-approved -> Finalize
    workflow.add_conditional_edges(
        "check_approval",
        should_require_approval,
        {
            "human_approval": "human_approval",
            "finalize": "finalize"
        }
    )

    # Human Approval -> Finalize
    workflow.add_edge("human_approval", "finalize")

    # Finalize -> End
    workflow.add_edge("finalize", END)
    
    # Compile the graph
    return workflow.compile()


def visualize_graph(graph):
    """
    Visualize the graph structure (requires graphviz)
    
    Args:
        graph: Compiled LangGraph workflow
    """
    try:
        from IPython.display import Image, display
        display(Image(graph.get_graph().draw_mermaid_png()))
    except ImportError:
        print("Graph visualization requires IPython and graphviz")
        print("Install with: pip install ipython graphviz")

# Made with Bob
