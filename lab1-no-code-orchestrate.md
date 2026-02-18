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


## Lab Steps

### Pre Requisite - Sign up to IBM Cloud
1. Using the following link, create an IBMid: https://www.ibm.com/account/reg/us-en/signup?formid=urx-19776&a=@OIDC_CLIENT_ID@&Target=https%3A//www.ibm.com/internet-of-things/
2. Check your email for an activation code
3. Enter the code in the box
4. You now have an IBMid. If done correctly, you will receive an email stating your IBMid is correct

### Step 1: Access watsonx Orchestrate

1. Log in to IBM Cloud at [cloud.ibm.com](https://cloud.ibm.com)
2. Navigate to the hamburger menu (top left)
3. Go to **Resource List**
4. Open the **AI/Machine Learning** section
5. Locate your **watsonx Orchestrate** service and click to open
6. Click the **Launch watsonx Orchestrate** button

### Step 2: Open Agent Builder

1. Once in watsonx Orchestrate, locate the hamburger menu in the top left
2. Select **Build**

You should now see the Agent Builder interface where you can create and manage agents.

### Step 3: Create Your First Agent

1. Click the **Create agent** button
2. Choose the **Create from scratch** option
2. Provide the following details:
   - **Agent Name**: `HR Assistant`
   - **Agent Description**: 
     ```
     An intelligent HR assistant that helps employees with HR-related queries, 
     including benefits information and leave balances. This agent has access to company HR policies and can 
     perform HR operations through integrated tools.
     ```

**Important**: The agent description is crucial as it helps the agent understand its role and capabilities. A well-written description improves the agent's ability to respond appropriately to user queries.

4. Click **Create** to create your agent
5. Scroll down to **Agent style** and select **ReAct** 

### Step 4: Add Knowledge Source

Knowledge sources allow your agent to access and retrieve information from documents to answer user questions.

1. In your agent's config page, navigate to the **Knowledge** tab
2. Click **Add source**
3. Choose **New knowledge**
4. Scroll down to select **Upload files**
5. From the documents folder in this repo, upload the HR Policy PDF document:
   - Click **Upload file**
   - Select the `Employee-Benefits.pdf` file

6. Configure the knowledge source:
   - **Knowledge Source Name**: `Company Employee Benefits`
   - **Description**: 
     ```
     Comprehensive benefits information and
     documentation. Use this source to answer questions about HR policies, 
     benefits, and procedures.
     ```

7. Click **Save**

The system will now upload the document, making it searchable by the agent.
**Note**, a notification **Knowledge is ready** will appear when document has finished uploading

### Step 5: Test Knowledge

Before adding tools, let's test if the agent can retrieve information from the knowledge source.

1. Using the **Preview** tab to the right
2. Try asking questions like:
   - What is the company's vacation policy?
   - What benefits does the company offer?
   - What are some of the wellness benefits?

Observe how the agent retrieves relevant information from the uploaded document and provides answers.

**Key Observation**: Notice that the agent cites the source of information, providing transparency about where the answer came from.

### Step 6: Import HR Tools

Tools extend your agent's capabilities by allowing it to perform actions, not just answer questions.

1. Navigate to the **Toolset** tab
2. Click **Add tool**
3. Select **OpenAPI**
4. From the documents folder in this repo, upload the **hr.yaml** file:
5. Review and select all of the operations
6. Click **Done**


### Step 7: Test your new Agent

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


