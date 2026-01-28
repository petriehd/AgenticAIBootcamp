# Lab 2: Low Code - Building with Langflow

## Overview

In this lab, you'll build a more sophisticated HR agent using DataStax Langflow's visual programming interface. You'll create flows that combine language models, tools, and data sources to handle complex HR queries. By the end, you'll have an API endpoint that can be integrated into other applications.

**Estimated Time**: 45-60 minutes

**Tools**: DataStax Langflow, IBM watsonx.ai

**Data**: HR Policy PDFs (vectorized), AstraDB with employee leave data

## Learning Objectives

By the end of this lab, you will be able to:
- Navigate the Langflow visual interface
- Create a basic chatbot flow with watsonx.ai
- Build an agent with tool capabilities
- Integrate vector databases for document search
- Connect to tabular data sources
- Create and test API endpoints
- Understand flow composition and data flow

## Prerequisites

- Completion of Lab 1
- Access to DataStax Astra DB account
- Access to IBM watsonx.ai
- HR Policy PDF documentation
- Basic understanding of APIs

## Architecture

In this lab, you'll build the following architecture:

```
User Input → Agent → Calculator Tool
                  → Vector DB (HR Docs)
                  → Tabular DB (Employee Data)
                  → watsonx.ai LLM
                  → Response
```

## Lab Steps

### Step 1: Access Langflow

1. Sign up or log in to DataStax Astra at [astra.datastax.com](https://astra.datastax.com)
2. Navigate to **Langflow** from the main menu
3. Click **Launch Langflow** to open the visual flow builder

You should now see the Langflow canvas where you can create flows.

### Step 2: Create a Basic Chatbot Flow

Let's start with a simple chatbot to understand the Langflow interface.

1. Click **New Flow**
2. Name it: `HR Basic Chatbot`
3. From the component panel on the left, drag the following components onto the canvas:
   - **Chat Input** (from Inputs section)
   - **IBM watsonx.ai** (from Models section)
   - **Chat Output** (from Outputs section)

4. Connect the components:
   - Connect **Chat Input** output to **watsonx.ai** input
   - Connect **watsonx.ai** output to **Chat Output** input

5. Configure the **watsonx.ai** component:
   - Click on the component to open settings
   - **Model**: Select `ibm/granite-13b-chat-v2`
   - **API Key**: Enter your watsonx.ai API key
   - **Project ID**: Enter your watsonx.ai project ID
   - **Parameters**:
     - Temperature: `0.7`
     - Max Tokens: `500`

6. Click **Run** to test the flow
7. In the chat interface, try: "Hello, I need help with HR questions"

**Key Observation**: This basic flow demonstrates how Langflow connects components visually. Data flows from left to right through the connections.

### Step 3: Create an Agent Flow with Calculator

Now let's create an agent that can use tools.

1. Create a new flow: `HR Agent with Tools`
2. Add the following components:
   - **Chat Input**
   - **Agent** (from Agents section)
   - **Calculator Tool** (from Tools section)
   - **Chat Output**

3. Connect the components:
   - Connect **Chat Input** to **Agent** input
   - Connect **Calculator Tool** to **Agent** tools input
   - Connect **Agent** output to **Chat Output**

4. Configure the **Agent** component:
   - **LLM**: Select **IBM watsonx.ai**
   - Configure watsonx.ai settings (same as Step 2)
   - **Agent Type**: `OpenAI Functions`
   - **System Message**: 
     ```
     You are an HR assistant that helps employees with calculations related 
     to their leave balances, salary, and benefits. Use the calculator tool 
     when mathematical operations are needed.
     ```

5. Test the agent:
   - "If I have 15 vacation days and use 7, how many do I have left?"
   - "Calculate 20% of 5000" (simulating benefits calculation)

**Key Observation**: The agent automatically decides when to use the calculator tool based on the query.

### Step 4: Add Vector Database for Document Search

Now let's add the ability to search through HR documentation.

1. In the same flow, add these components:
   - **Astra DB** (from Vector Stores section)
   - **Embeddings** (from Embeddings section)

2. Configure **Astra DB**:
   - **Database**: Select or create `hr_knowledge_base`
   - **Collection**: `hr_policies`
   - **Token**: Enter your Astra DB application token
   - **API Endpoint**: Your Astra DB API endpoint

3. Configure **Embeddings**:
   - **Provider**: Select `IBM watsonx.ai`
   - **Model**: `ibm/slate-125m-english-rtrvr`
   - **API Key**: Your watsonx.ai API key

4. Upload HR documents to vector database:
   - Click on **Astra DB** component
   - Select **Upload Documents**
   - Upload your HR policy PDFs
   - Wait for vectorization to complete

5. Connect **Astra DB** to **Agent** as a tool
6. Update the Agent's system message:
   ```
   You are an HR assistant that helps employees with HR-related queries. 
   You have access to:
   1. Company HR policies and documentation - use this to answer policy questions
   2. Calculator tool - use this for mathematical calculations
   
   Always cite your sources when providing information from HR policies.
   ```

7. Test with document queries:
   - "What is the company's vacation policy?"
   - "How do I submit a time-off request?"

### Step 5: Add Tabular Data Source

Now let's add access to employee data stored in a tabular format.

1. Add a new component:
   - **Astra DB Data API** (from Data Sources section)

2. Configure the Data API:
   - **Database**: Same as vector store
   - **Keyspace**: `hr_data`
   - **Table**: `employee_leave_balances`
   - **Token**: Your Astra DB token

3. Create a custom tool for querying employee data:
   - Add **Python Tool** component
   - Name it: `Get Employee Leave Balance`
   - Add the following code:

```python
from langflow import CustomComponent
from typing import Dict, Any

class GetEmployeeLeaveBalance(CustomComponent):
    display_name = "Get Employee Leave Balance"
    description = "Retrieves leave balance for an employee"
    
    def build_config(self):
        return {
            "employee_id": {
                "display_name": "Employee ID",
                "type": "str"
            }
        }
    
    def build(self, employee_id: str) -> Dict[str, Any]:
        # Query Astra DB for employee leave balance
        # This is a simplified example
        query = f"SELECT * FROM employee_leave_balances WHERE employee_id = '{employee_id}'"
        result = self.astra_db.execute(query)
        
        return {
            "employee_id": employee_id,
            "vacation_days": result.get("vacation_days", 0),
            "sick_days": result.get("sick_days", 0),
            "personal_days": result.get("personal_days", 0)
        }
```

4. Connect this tool to the Agent
5. Update the Agent's system message to include:
   ```
   3. Employee leave balance data - use this to check specific employee balances
      (requires employee ID)
   ```

### Step 6: Test Complete Agent

Test your agent with complex queries that require multiple tools:

**Test 1: Policy + Calculation**
```
User: According to company policy, how many vacation days do I get per year? 
      If I've used 8 days, how many do I have left?
Expected: Agent retrieves policy (20 days), then calculates (20 - 8 = 12)
```

**Test 2: Data Lookup + Calculation**
```
User: What is my current leave balance? My employee ID is EMP12345. 
      If I take 5 days off, how many will I have left?
Expected: Agent queries database, then performs calculation
```

**Test 3: Multi-source Query**
```
User: I want to take 10 days off next month. Check my balance (EMP12345) 
      and tell me if that's within policy limits.
Expected: Agent checks balance, references policy, provides answer
```

### Step 7: Add Third-Party Data Sources

Langflow supports integration with various enterprise systems. Let's explore available connectors:

1. In the component panel, explore:
   - **SAP Connector** (for SAP HR systems)
   - **ServiceNow Connector** (for IT service management)
   - **Salesforce Connector** (for CRM data)
   - **REST API** (for custom integrations)

2. For demonstration, add a **REST API** component:
   - **Endpoint**: `https://api.techcorp.example.com/hr/benefits`
   - **Method**: `GET`
   - **Headers**: Add authentication headers
   - **Description**: "Retrieves employee benefits information"

3. Connect to Agent as another tool

**Note**: In a production environment, you would configure these connectors with actual credentials and endpoints.

### Step 8: Create API Endpoint

Now let's expose your agent as an API that can be called from other applications.

1. Click on the **API** button in the top right
2. Select **Create Endpoint**
3. Configure the endpoint:
   - **Name**: `hr-agent-api`
   - **Description**: `HR Agent API for employee queries`
   - **Authentication**: Enable API key authentication
   - **Rate Limiting**: Set appropriate limits

4. Copy the generated endpoint URL and API key
5. Test the endpoint using curl:

```bash
curl -X POST https://your-langflow-instance.com/api/v1/run/hr-agent-api \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "input": "What is my leave balance? Employee ID: EMP12345",
    "tweaks": {}
  }'
```

6. Save the endpoint URL and API key for use in Lab 3

### Step 9: Monitor and Debug

Langflow provides built-in monitoring and debugging capabilities:

1. Click on **Logs** tab to view execution logs
2. Observe:
   - Which tools were called
   - Token usage
   - Response times
   - Errors or warnings

3. Use the **Debug Mode**:
   - Toggle debug mode in the top right
   - Run a query
   - See step-by-step execution with intermediate outputs

4. Optimize your flow:
   - Identify slow components
   - Reduce unnecessary tool calls
   - Adjust LLM parameters for better performance

### Step 10: Version and Export

1. Save your flow with a version:
   - Click **Save**
   - Add version tag: `v1.0`
   - Add description of changes

2. Export your flow:
   - Click **Export**
   - Choose **JSON format**
   - Save the file for backup or sharing

3. You can also export as:
   - **Python code** (to run standalone)
   - **Docker container** (for deployment)

## Key Takeaways

1. **Visual Programming**: Langflow's visual interface makes it easy to build complex agent workflows without extensive coding

2. **Component Composition**: Agents can combine multiple tools and data sources to handle sophisticated queries

3. **Vector + Tabular Data**: Combining vector databases (for documents) with tabular data (for structured information) provides comprehensive coverage

4. **Tool Selection**: Agents automatically select appropriate tools based on the query and available capabilities

5. **API Integration**: Langflow flows can be easily exposed as APIs for integration with other systems

6. **Enterprise Connectors**: Built-in connectors for SAP, ServiceNow, and other enterprise systems simplify integration

## Troubleshooting

**Issue**: Agent doesn't use the correct tool
- **Solution**: Improve tool descriptions. Make them more specific about when to use each tool.

**Issue**: Vector search returns irrelevant results
- **Solution**: Check embedding model configuration. Consider adjusting search parameters or re-indexing documents.

**Issue**: API endpoint returns errors
- **Solution**: Check authentication credentials. Verify all components are properly configured. Review logs for specific error messages.

**Issue**: Slow response times
- **Solution**: Enable caching for frequently accessed data. Optimize LLM parameters. Consider using smaller models for simple queries.

## Next Steps

Excellent work! You've built a sophisticated agent using Langflow that combines:
- Language models for natural language understanding
- Vector databases for document search
- Tabular databases for structured data
- Multiple tools for different capabilities
- API endpoints for external integration

In the next lab, you'll take this to the next level by implementing custom logic with LangGraph, including human-in-the-loop approval workflows for high-value requests.

**Continue to**: [Lab 3: Pro Code - Building with LangGraph](./lab3-pro-code-langgraph.md)

## Additional Resources

- [DataStax Langflow Documentation](https://docs.langflow.org/)
- [Astra DB Documentation](https://docs.datastax.com/en/astra/docs/)
- [IBM watsonx.ai Documentation](https://www.ibm.com/docs/en/watsonx-as-a-service)
- [Langflow Component Library](https://docs.langflow.org/components)