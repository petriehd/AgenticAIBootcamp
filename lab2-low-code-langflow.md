# Lab 2: Low Code - Building with Langflow

## Overview

In this lab, you'll build a more complex HR agent using Langflow's visual interface. You'll create flows that combine language models, tools, and data sources to handle complex HR queries. By the end, you'll have an API endpoint that can be integrated into other applications.

**Estimated Time**: 45-60 minutes

**Tools**: Langflow, IBM watsonx.ai

**Data**: HR Policy PDFs, AstraDB with employee leave data

## Learning Objectives

By the end of this lab, you will be able to:
- Navigate the Langflow visual interface
- Create a basic chatbot flow with watsonx.ai
- Build an agent with tool capabilities
- Integrate vector databases for document search
- Connect to tabular data sources
- Understand flow composition and data flow


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


### Step 2: Create a Basic Assistant Flow

Let's start with a simple Assistant to understand the Langflow interface.

1. Click **New Flow**
2. Select **Blank Flow**
2. Name it: `HR Assistant`
3. From the component panel on the left, drag the following components onto the canvas:
   - **Chat Input** 
   - **IBM watsonx.ai** 
   - **Chat Output** 

4. Connect the components:
   - Connect **Chat Input** output to **watsonx.ai** input
   - Connect **watsonx.ai** output to **Chat Output** input

5. Configure the **watsonx.ai** component:
   - **API Endpoint**: Select `https://au-syd.ml.cloud.ibm.com`
   - **Project ID**: Enter your provided Project ID
   - **API Key**: Enter your provided watsonx.ai API key
   - **Model**: Select `llama/llama-3-3-90b-vision-instruct`

6. Click **Run** to test the flow

### Step 3: Add tools and data

1. Add the following components:
   - **Agent** 
   - **Calculator Tool** 

3. Connect the components:
   - Connect **Chat Input** to **Agent** input
   - Select **Calculator** and turn on **Tool Mode**, then connect **Calculator** to **Agent** tools input
   - Connect **Agent** output to **Chat Output**

4. Configure the **Agent** component:
   - **Model Provider**: Select **IBM watsonx.ai**
   - Configure watsonx.ai settings (same as Step 2)
   - **Agent Instructions**:
     ```
      You are an HR assistant that can search company documentation, search leave balances, and helps employees with calculations related to their leave balances, salary, and benefits.
      When a user requests leave, always confirm the details back in your response including: the number of days, the type of leave (e.g. vacation, sick, personal), and the start and end dates in YYYY-MM-DD format.
     ```

5. Test the agent with basic maths questions

**Key Observation**: The agent automatically decides when to use the calculator tool based on the query.

Now let's add HR documentation.

6. In the same flow, add a new component:
   - **Astra DB** 

7. Configure **Astra DB**:
   - **Database**: Select or create `hr_knowledge_base`
   - **Collection**: `hr_policies`
   - **Token**: Use the provided Application Token

8. Connect **Astra DB** to **Agent** as a tool


9. Test it out in the playgroud

Now let's add access to employee data stored in a tabular format.

10. Add another **Astra DB** component 

11. Configure **Astra DB**:
   - **Database**: Select or create `hr_knowledge_base`
   - **Collection**: `employee_leave_balances`
   - **Token**: Use the provided Application Token
   a. Update **Tool** by clicking **Actions**
   b. Select **Search Documents** 
   c. Update slug to **search_tabular_data**
   d. Update description to:
   `
   Search tabular data in AstraDB
   `


13. Give it a test

### Step 5: Test Complete Agent

Test your agent with complex queries that require multiple tools

### Step 6: Create API Endpoint

Now let's expose your agent as an API that can be called from other applications.

1. Click on the **Share** button in the top right
2. Select **API access**
3. Copy the generated endpoint URL and API key
4. Test the endpoint using curl:

```bash
curl -X POST https://your-langflow-instance.com/api/v1/run/hr-agent-api \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "input": "What is Jordan's leave balance?",
    "tweaks": {}
  }'
```

6. Save the endpoint URL and API key for use in Lab 3


## Next Steps

Excellent work! You've built a sophisticated agent using Langflow that combines:
- Language models for natural language understanding
- Vector databases for document search
- Tabular databases for structured data
- Multiple tools for different capabilities
- API endpoints for external integration

In the next lab, you'll take this to the next level by implementing custom logic with LangGraph, including human-in-the-loop approval workflows for high-value requests.

**Continue to**: [Lab 3: Pro Code - Building with LangGraph](./lab3-pro-code-langgraph.md)

