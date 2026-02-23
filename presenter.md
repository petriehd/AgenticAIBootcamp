# Presenter Guide

## Lab 1: No Code - watsonx Orchestrate

### Step 3.2 - Agent Creation Options
**Show all three creation methods:**
- **Build with AI**: Quick agent generation (mention ongoing improvements)
- **Catalogue**: Pre-built domain-specific agents available in Orchestrate
- **Create from scratch**: Full customization (proceed with this option)

### Step 3.3 - Agent Description
**Emphasize importance:** Agent descriptions enable inter-agent communication and define agent capabilities.

### Step 3.5 - Agent Styles
**Explain reasoning styles:** Briefly cover available styles and why ReAct is selected for this use case.

### Step 4.4 - Data Sources
**Demonstrate options:** Show available data sources and mention third-party integration capabilities.

### Step 4.6 - Document Description
**Reiterate importance:** Document descriptions improve retrieval accuracy and context understanding.

### Step 5 - Testing
**Highlight response components:**
- Reasoning traces
- Tools/data used
- Citations

### Step 6.3 - Tool Integration
**Explore tool options:**
- Show pre-built tool catalogue
- Review product-specific tooling in catalogue
- Mention agentic workflow nodes (note: deeper exploration available in advanced sessions)

---

## Lab 2: Low Code - Langflow

### Introduction
**IBM's AI Principles:** Explain Open, Trusted, Targeted, and Empowering principles. Position Langflow as embodying the Open principle.

### Step 2.3 - Flow Builder UI
**Navigate the interface:**
- Components panel
- Bundles

### Step 2.4 - Node Connections
**Explain connection system:** Colored dots indicate compatible connection types.

### Step 2.6 - Global Variables
**Demonstrate configuration:** Show global variables screen and explain their importance for reusability.

### Step 2.6 - Model Selection
**Discuss model options:**
- Instruct models for agentic workflows
- Model sizing considerations
- Vision capabilities
- etc

### Step 3.3 - Tool Mode
**Enable tool functionality:** Demonstrate converting components to tool mode and connecting to agent's toolbelt.

### Step 3.4 - Variable Usage
**Apply global variables:** Use previously configured variables in the flow.

### Step 3.5 - Calculator Testing
**Compare query types:**
- Simple expression: `10+10`
- Word problem: "If I have ten apples at one dollar each, what's the total?"

**Key point:** Update tool descriptions to handle natural language math problems.

### Step 3.11 - Tool Differentiation
**Demonstrate duplication issue:**
1. Test flow without updating tool slug/description
2. Show agent confusion between duplicate AstraDB nodes
3. Update slug and description to resolve

### Step 6 - API Integration
**Emphasize interoperability:** JSON enables system integration and external connectivity.

---

## Lab 3: Pro Code - LangGraph

### Introduction
**Transition to code:** Explain progression from no-code to low-code to pro-code. Emphasize when programmatic control is necessary.

### Step 1 - GitHub Codespaces Setup
**Demonstrate environment:**
- Show template repository structure
- Explain Codespaces benefits (uniform environment, pre-installed dependencies)
- Verify Python 3.11 installation
- Configure `.env` file with Lab 2 credentials

### Step 2 - Agent State
**Explain state management:**
- `TypedDict` for type safety
- `Annotated[list, add_messages]` for automatic message history
- State persistence across graph nodes
- Optional fields for flexible state building


### Step 3 - Langflow Integration
**Highlight API integration:**
- Consuming Lab 2's API endpoint
- JSON parsing for structured data extraction


### Step 4 - Agent Nodes
**Explain node architecture:**
- `call_langflow_node`: API integration and data extraction
- `check_approval_node`: Business rule evaluation
- `human_approval_node`: Human-in-the-loop workflow
- `finalize_node`: Response preparation

**Key concept:** Each node performs a specific function and updates state.

### Step 5 - Graph Construction
**Build the workflow:**
- Entry point configuration
- Node connections and edges
- Conditional routing based on approval requirements
- END state definition

### Step 6 - Guardrails Implementation
**Demonstrate approval workflow:**
- Threshold configuration (5 days default)
- Conditional logic: `days_requested > threshold`
- Human approval prompt with request details
- Approval/rejection handling

**Test scenario:** Request 6 days leave to trigger approval workflow.

### Step 7 - Testing
**Run test scenarios:**
1. Simple query (no approval needed)
2. Small leave request (auto-approved)
3. Large leave request (human approval triggered)
