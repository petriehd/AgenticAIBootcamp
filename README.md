# AskHR: Agentic AI Bootcamp

## Overview

This bootcamp provides hands-on experience building an intelligent HR assistant system using different agentic AI technologies. Through three progressive labs, you'll learn to create an AskHR agent that helps employees interact with HR systems and access information efficiently.

## The Problem

TechCorp Inc., a global IT leader with a workforce of 100,000 employees, faces a significant challenge in managing its growing HR operations. As the company expanded, it struggled with efficiently handling employee profile updates, time-off requests, and benefits inquiries. Traditional HR systems were no longer sufficient to handle the volume and complexity of requests, leading to delays and employee frustration.

## The Solution

We will build an AskHR system that empowers employees to interact with HR systems and access information efficiently through conversational AI. The agent will:

- Answer HR-related questions using company documentation
- Retrieve employee data such as leave balances
- Process requests like time-off submissions
- Integrate with backend HR systems seamlessly

## Business Value

The usage of an AI-backed system to optimize the HR process can have multiple impacts, such as:

- Quicker resolution time
- Higher user satisfaction
- Increased revenue
- Reduction in employee burnout
- Improved data safety and more grounded responses without hallucinations
- Better brand experience

## Architecture

The AskHR agent leverages a multi-agent orchestration model that ensures intelligent reasoning, seamless action execution, and a responsive experience for employees. The architecture is built with watsonx Orchestrate enabling the HR agent to manage a wide range of HR-related queries and requests efficiently.

### Key Components

1. **HR Agent and App (IBM watsonx Orchestrate)**: The HR agent acts as the central orchestrator, managing user interactions and delegating tasks to appropriate tools.

2. **Knowledge Sources**: The agent retrieves relevant information from Company Benefits Knowledge documents to answer related queries.

3. **Tools**: A collection of reusable tools that perform specific HR-related tasks, such as:
   - Checking time-off balances
   - Submitting time-off requests
   - Updating personal details
   - Getting profile information

4. **Third Party Systems**: The agent communicates with a range of third party systems to fetch or update employee data, ensuring real-time synchronization and accuracy.

## Labs Overview

This bootcamp consists of three progressive labs, each building upon the previous one:

### Lab 1: No Code - Building with Orchestrate (45 minutes)

Learn to create your first AI agent using IBM watsonx Orchestrate's no-code interface. You'll:
- Create an HR agent
- Add knowledge sources from HR documentation
- Import and test HR tools
- Understand agent reasoning styles

**Tools**: watsonx Orchestrate  
**Data**: HR Policy PDF documentation

### Lab 2: Low Code - Building with Langflow (45 minutes)

Build a more sophisticated agent using Langflow's visual programming interface. You'll:
- Create a basic chatbot flow
- Add an agent with calculator tool
- Integrate database for document search
- Connect to data sources for employee information
- Set up API endpoints for external integration

**Tools**: DataStax Langflow, watsonx.ai  
**Data**: HR Policy PDFs, AstraDB with employee leave data

### Lab 3: Pro Code - Building with LangGraph (45 minutes)

Implement advanced agent logic with human-in-the-loop approval workflows using Python and LangGraph. You'll:
- Create custom agent state management
- Integrate with Langflow API endpoint
- Implement conditional logic for approval workflows
- Add human-in-the-loop for high-value requests

**Tools**: LangGraph, Python  
**Data**: Langflow API endpoint from Lab 2


## Getting Started

1. **Clone this repository**: `git clone https://github.com/petriehd/AgenticAIBootcamp`
2. **Verify access**: Ensure you can log in to all required services
3. **Review the use case**: Understand the AskHR scenario and architecture above
5. **Start Lab 1**: Progress sequentially through the labs - each builds upon the previous one

## Lab Structure

Each lab includes:
- Learning objectives
- Step-by-step instructions with screenshots
- Testing procedures
- Key takeaways
- Links to next steps

## Support

For questions or issues during the bootcamp:
- Review the troubleshooting section in each lab
- Check the FAQ document
- Contact your instructor or workshop facilitator

## Additional Resources

- [IBM watsonx Documentation](https://www.ibm.com/watsonx)
- [DataStax Langflow Documentation](https://docs.langflow.org/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

---

Ready to begin? Start with [Lab 1: No Code - Building with Orchestrate](./lab1-no-code-orchestrate.md)