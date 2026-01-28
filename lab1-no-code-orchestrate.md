# Lab 1: No Code - Building with Orchestrate

## Overview

In this lab, you'll create your first AI agent using IBM watsonx Orchestrate's no-code interface. You'll build an AskHR agent that can answer employee questions using HR documentation and execute HR-related tasks through integrated tools.

**Estimated Time**: 45 minutes

**Tools**: IBM watsonx Orchestrate

**Data**: HR Policy PDF documentation

## Learning Objectives

By the end of this lab, you will be able to:
- Navigate the watsonx Orchestrate interface
- Create and configure an AI agent
- Add knowledge sources to your agent
- Import and test tools using OpenAPI specifications
- Understand different agent reasoning styles
- Test your agent with various HR queries

## Prerequisites

- Access to IBM Cloud account
- Access to a watsonx Orchestrate instance
- HR Policy PDF documentation (provided)

## Architecture

In this lab, you'll build the following architecture:

```
Employee Query → HR Agent → Knowledge Source (HR Docs)
                         → Tools (HR Operations)
                         → Response
```

## Lab Steps

### Step 1: Access watsonx Orchestrate

1. Log in to IBM Cloud at [cloud.ibm.com](https://cloud.ibm.com)
2. Navigate to the hamburger menu (top left)
3. Go to **Resource List**
4. Open the **AI/Machine Learning** section
5. Locate your **watsonx Orchestrate** service and click to open
6. Click the **Launch watsonx Orchestrate** button

### Step 2: Open Agent Builder

1. Once in watsonx Orchestrate, locate the hamburger menu
2. Click on the down arrow next to **Build**
3. Select **Agent Builder**

You should now see the Agent Builder interface where you can create and manage agents.

### Step 3: Create Your First Agent

1. Click the **Create agent** button
2. Provide the following details:
   - **Agent Name**: `HR Assistant`
   - **Agent Description**: 
     ```
     An intelligent HR assistant that helps employees with HR-related queries, 
     including benefits information, leave balances, time-off requests, and 
     profile updates. This agent has access to company HR policies and can 
     perform HR operations through integrated tools.
     ```

**Important**: The agent description is crucial as it helps the agent understand its role and capabilities. A well-written description improves the agent's ability to respond appropriately to user queries.

3. **Agent Style**: Select **Default**
   - **Default**: Uses a straightforward approach to answer questions
   - **ReAct**: Uses reasoning and action cycles for more complex problem-solving

For this lab, we'll use the Default style, which is suitable for most HR queries.

4. Click **Create** to create your agent

### Step 4: Add Knowledge Source

Knowledge sources allow your agent to access and retrieve information from documents to answer user questions.

1. In your agent's configuration page, navigate to the **Knowledge** tab
2. Click **Add knowledge source**
3. Upload the HR Policy PDF document:
   - Click **Upload file**
   - Select the `hr-policies.pdf` file
   - Wait for the upload to complete

4. Configure the knowledge source:
   - **Knowledge Source Name**: `Company HR Policies`
   - **Description**: 
     ```
     Comprehensive HR policies including benefits information, leave policies, 
     time-off procedures, employee conduct guidelines, and company benefits 
     documentation. Use this source to answer questions about HR policies, 
     benefits, and procedures.
     ```

5. Click **Save**

The system will now process and vectorize the document, making it searchable by the agent.

### Step 5: Test Knowledge Retrieval

Before adding tools, let's test if the agent can retrieve information from the knowledge source.

1. Navigate to the **Preview** tab
2. Try asking questions like:
   - "What is the company's vacation policy?"
   - "How many sick days do employees get?"
   - "What benefits does the company offer?"
   - "How do I request time off?"

Observe how the agent retrieves relevant information from the HR policies document and provides answers.

**Key Observation**: Notice that the agent cites the source of information, providing transparency about where the answer came from.

### Step 6: Import HR Tools

Tools extend your agent's capabilities by allowing it to perform actions, not just answer questions.

1. Navigate to the **Tools** tab
2. Click **Import tool**
3. Select **OpenAPI specification**
4. Upload or paste the HR Tools OpenAPI YAML specification:

```yaml
openapi: 3.0.0
info:
  title: HR Management API
  version: 1.0.0
  description: API for managing employee HR operations
servers:
  - url: https://api.techcorp.example.com/hr/v1
paths:
  /employees/{employee_id}/leave-balance:
    get:
      summary: Get employee leave balance
      description: Retrieves the current leave balance for an employee
      operationId: getLeaveBalance
      parameters:
        - name: employee_id
          in: path
          required: true
          schema:
            type: string
          description: The unique identifier of the employee
      responses:
        '200':
          description: Leave balance retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  employee_id:
                    type: string
                  vacation_days:
                    type: number
                  sick_days:
                    type: number
                  personal_days:
                    type: number
  /employees/{employee_id}/time-off:
    post:
      summary: Submit time-off request
      description: Submits a new time-off request for an employee
      operationId: submitTimeOff
      parameters:
        - name: employee_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                start_date:
                  type: string
                  format: date
                end_date:
                  type: string
                  format: date
                leave_type:
                  type: string
                  enum: [vacation, sick, personal]
                reason:
                  type: string
      responses:
        '201':
          description: Time-off request submitted successfully
  /employees/{employee_id}/profile:
    get:
      summary: Get employee profile
      description: Retrieves employee profile information
      operationId: getEmployeeProfile
      parameters:
        - name: employee_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Profile retrieved successfully
```

5. Review the imported tools and their descriptions
6. Click **Save**

### Step 7: Configure Tool Descriptions

For each imported tool, ensure it has a clear description:

1. **Get Leave Balance**:
   ```
   Retrieves the current leave balance for an employee, including vacation days, 
   sick days, and personal days remaining.
   ```

2. **Submit Time Off**:
   ```
   Submits a time-off request for an employee. Requires start date, end date, 
   leave type, and optional reason.
   ```

3. **Get Employee Profile**:
   ```
   Retrieves employee profile information including name, department, position, 
   and contact details.
   ```

### Step 8: Test the Complete Agent

Now test your agent with queries that require both knowledge retrieval and tool usage:

1. Navigate to the **Preview** tab
2. Try these test scenarios:

**Scenario 1: Knowledge Query**
```
User: What is the company's vacation policy?
Expected: Agent retrieves information from HR policies document
```

**Scenario 2: Tool Usage**
```
User: What is my current leave balance? My employee ID is EMP12345
Expected: Agent uses the getLeaveBalance tool
```

**Scenario 3: Combined Query**
```
User: I want to take vacation next week. How many days do I have left? 
      My employee ID is EMP12345
Expected: Agent checks leave balance and references vacation policy
```

**Scenario 4: Action Request**
```
User: Submit a vacation request for December 20-27. My employee ID is EMP12345
Expected: Agent uses submitTimeOff tool
```

### Step 9: Understand Agent Reasoning

1. In the Preview panel, observe the **Reasoning** section
2. Notice how the agent:
   - Analyzes the user's query
   - Decides whether to use knowledge sources or tools
   - Selects the appropriate tool
   - Formats the response

3. Try asking: "How do I request time off and what is my current balance?"
   - Observe how the agent breaks down the query
   - See how it uses multiple sources (knowledge + tool)

### Step 10: Refine Agent Behavior

Based on your testing, you may want to refine your agent:

1. Go back to **Agent Settings**
2. Update the agent description to be more specific
3. Add instructions for handling edge cases:
   ```
   When users ask about leave balances, always request their employee ID if 
   not provided. When submitting time-off requests, confirm the details before 
   submission. Always cite sources when providing policy information.
   ```

4. Save and test again

## Key Takeaways

1. **Agent Description Matters**: A clear, comprehensive agent description helps the agent understand its role and respond appropriately

2. **Knowledge Sources**: Vectorized documents enable semantic search, allowing the agent to find relevant information even when queries don't match exact keywords

3. **Tools Extend Capabilities**: OpenAPI specifications make it easy to integrate external systems and give agents the ability to perform actions

4. **Agent Reasoning**: The Default agent style is suitable for straightforward queries, while ReAct is better for complex, multi-step reasoning

5. **Testing is Crucial**: Always test your agent with various scenarios to ensure it behaves as expected

## Troubleshooting

**Issue**: Agent doesn't find information in the knowledge source
- **Solution**: Ensure the document was fully processed. Check the knowledge source status. Try rephrasing your query.

**Issue**: Tools aren't being called
- **Solution**: Verify the OpenAPI specification is valid. Ensure tool descriptions clearly indicate when to use each tool.

**Issue**: Agent provides incorrect information
- **Solution**: Review and improve the agent description. Add more specific instructions. Check if the knowledge source contains the correct information.

## Next Steps

Congratulations! You've created your first AI agent using watsonx Orchestrate. You've learned how to:
- Configure an agent with knowledge sources
- Import tools using OpenAPI specifications
- Test and refine agent behavior

In the next lab, you'll build a more sophisticated agent using Langflow's visual programming interface, adding vector databases and tabular data sources.

**Continue to**: [Lab 2: Low Code - Building with Langflow](./lab2-low-code-langflow.md)

## Additional Resources

- [watsonx Orchestrate Documentation](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [Agent Builder Best Practices](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [OpenAPI Specification Guide](https://swagger.io/specification/)