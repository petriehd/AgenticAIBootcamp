# Prerequisites and Setup Guide

This document outlines the setup requirements for organizers and participants of the Agentic AI Bootcamp.

## For Organizers

### Pre-Workshop Setup (Complete 1-2 weeks before)

#### 1. IBM Cloud and watsonx Setup

**watsonx Orchestrate Instances**
- Provision watsonx Orchestrate instances for all participants
- Create individual service credentials for each participant
- Document the instance URLs and access methods
- Test agent creation and tool import functionality

**watsonx.ai Setup**
- Create a watsonx.ai project for the workshop
- Generate API keys for participants
- Document the Project ID
- Set up appropriate resource quotas
- Test model access (granite-13b-chat-v2, slate-125m-english-rtrvr)

**Estimated Cost per Participant:**
- watsonx Orchestrate: Varies by plan
- watsonx.ai: Token-based pricing (estimate 100K tokens per participant)

#### 2. DataStax Astra DB Setup

**Database Preparation**
- Create Astra DB organization account
- Set up workshop database instances
- Create two collections per participant:
  - Vector collection: `hr_policies` (for document embeddings)
  - Tabular collection: `employee_leave_balances` (for structured data)
- Generate application tokens for each participant
- Document API endpoints

**Data Preparation**
- Prepare HR policy PDF documents (sample provided or custom)
- Create sample employee data CSV with fields:
  - employee_id
  - employee_name
  - vacation_days
  - sick_days
  - personal_days
  - department
- Pre-vectorize HR documents (optional, to save time)
- Load sample employee data into tabular collections

**Estimated Cost:**
- Free tier available (5GB storage, 20M reads/month)
- Paid tier if needed: ~$0.25/GB/month

#### 3. Langflow Setup

**Account Setup**
- Create DataStax Langflow organization account
- Provision workspace for participants
- Set up authentication method (SSO or individual accounts)
- Configure resource limits per user

**Pre-built Flows (Optional)**
- Create template flows for participants to import
- Test all component integrations
- Export flows as JSON for distribution

**Estimated Cost:**
- Included with DataStax Astra DB subscription
- Or standalone: Check DataStax pricing

#### 4. Sample Data and Assets

**HR Policy Documents**
Create or source HR policy PDFs covering:
- Vacation and leave policies
- Sick leave policies
- Personal day policies
- Time-off request procedures
- Benefits information
- Company holidays

**Sample Employee Data**
Create CSV with 50-100 sample employees:
```csv
employee_id,employee_name,department,vacation_days,sick_days,personal_days
EMP12345,John Doe,Engineering,15,10,3
EMP12346,Jane Smith,Marketing,20,10,5
...
```

**OpenAPI Specification**
Prepare HR Tools OpenAPI YAML (provided in Lab 1) or customize for your environment

#### 5. Network and Access

**Firewall Rules**
- Ensure participants can access:
  - cloud.ibm.com
  - astra.datastax.com
  - Langflow endpoints
  - GitHub (for cloning repository)

**VPN Requirements**
- Document any VPN requirements
- Provide VPN credentials if needed

**Proxy Configuration**
- Document proxy settings if required
- Test all tools work through corporate proxy

#### 6. Credentials Distribution

**Create Credentials Package for Each Participant:**

```
participant_credentials.txt
----------------------------
IBM Cloud Account: username@example.com
IBM Cloud Password: [provided separately]

watsonx Orchestrate URL: https://orchestrate-instance.cloud.ibm.com
watsonx.ai API Key: [unique per participant]
watsonx.ai Project ID: [shared or unique]

Astra DB API Endpoint: https://[database-id]-[region].apps.astra.datastax.com
Astra DB Application Token: [unique per participant]
Astra DB Keyspace: hr_data

Langflow URL: https://langflow.datastax.com
Langflow Username: participant@example.com
Langflow Password: [provided separately]
```

**Security Considerations:**
- Use password managers or secure distribution method
- Set credentials to expire after workshop
- Implement least-privilege access
- Monitor usage during workshop

#### 7. Testing and Validation

**One Week Before Workshop:**
- Test complete workflow with all three labs
- Verify all API endpoints are accessible
- Confirm data is loaded correctly
- Test with a pilot participant
- Document any issues and workarounds

**Day Before Workshop:**
- Final verification of all services
- Ensure all credentials are active
- Prepare backup credentials
- Test network connectivity at venue

#### 8. Support Materials

**Prepare:**
- Troubleshooting guide for common issues
- FAQ document
- Contact information for technical support
- Backup plans for service outages

---

## For Participants

### Before the Workshop (Complete 1 week before)

#### 1. Account Access Verification

**Receive from Organizers:**
- IBM Cloud credentials
- watsonx Orchestrate access URL
- watsonx.ai API key and Project ID
- Astra DB credentials and endpoints
- Langflow access credentials

**Verify Access:**
- Log in to IBM Cloud
- Access watsonx Orchestrate instance
- Verify watsonx.ai API key works
- Log in to Astra DB
- Access Langflow workspace

**If Issues:**
- Contact workshop organizers immediately
- Do not wait until workshop day

#### 2. Software Installation

**Required Software:**

**Python 3.8 or Higher**
```bash
# Verify installation
python --version  # or python3 --version

# If not installed:
# Windows: Download from python.org
# macOS: brew install python3
# Linux: sudo apt-get install python3
```

**Git**
```bash
# Verify installation
git --version

# If not installed:
# Windows: Download from git-scm.com
# macOS: brew install git
# Linux: sudo apt-get install git
```

**Code Editor (Recommended)**
- Visual Studio Code (recommended)
- PyCharm
- Or any text editor

**Web Browser**
- Chrome, Firefox, or Edge (latest version)
- Ensure JavaScript is enabled
- Disable ad blockers for workshop domains

#### 3. Network Requirements

**Verify Access to:**
- cloud.ibm.com
- astra.datastax.com
- github.com
- Any workshop-specific URLs provided

**Corporate Networks:**
- Check if VPN is required
- Verify proxy settings
- Test connectivity before workshop

#### 4. Pre-Workshop Setup (Optional but Recommended)

**Clone Workshop Repository:**
```bash
git clone https://github.com/[org]/agentic-ai-bootcamp.git
cd agentic-ai-bootcamp
```

**Set Up Python Environment (Lab 3):**
```bash
cd lab3-code
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Create .env File:**
```bash
cp .env.example .env
# Edit .env with your credentials (will be provided during workshop)
```

#### 5. Knowledge Prerequisites

**Required:**
- Basic understanding of AI and machine learning concepts
- Familiarity with web browsers and cloud services
- Ability to follow technical instructions

**Helpful but Not Required:**
- Python programming basics (for Lab 3)
- REST API concepts
- Experience with cloud platforms

#### 6. Hardware Requirements

**Minimum:**
- Laptop or desktop computer
- 8GB RAM
- 10GB free disk space
- Stable internet connection (5 Mbps or higher)
- Webcam and microphone (for virtual workshops)

**Recommended:**
- 16GB RAM
- 20GB free disk space
- Dual monitors (for following along)

#### 7. Workshop Day Checklist

**Bring/Have Ready:**
- Laptop with all software installed
- Power adapter and charging cable
- Credentials document (printed or digital)
- Notebook for taking notes
- Questions prepared

**Test Before Workshop:**
- Can you log in to all services?
- Is Python installed and working?
- Can you access the workshop repository?
- Is your internet connection stable?

---

## Quick Start Checklist

### Organizers

- [ ] Provision watsonx Orchestrate instances
- [ ] Create watsonx.ai project and API keys
- [ ] Set up Astra DB databases and collections
- [ ] Load sample HR data
- [ ] Create Langflow workspaces
- [ ] Prepare credentials packages
- [ ] Test complete workflow
- [ ] Distribute credentials to participants
- [ ] Prepare support materials

### Participants

- [ ] Receive and verify credentials
- [ ] Install Python 3.8+
- [ ] Install Git
- [ ] Install code editor
- [ ] Clone workshop repository
- [ ] Verify access to all services
- [ ] Set up Python environment (Lab 3)
- [ ] Test internet connectivity
- [ ] Review prerequisites documentation

---

## Troubleshooting Common Issues

### Cannot Access IBM Cloud
- Verify credentials are correct
- Check if account is activated
- Try incognito/private browsing mode
- Clear browser cache and cookies
- Contact organizers for new credentials

### Python Installation Issues
- Ensure Python 3.8 or higher
- Check PATH environment variable
- Try `python3` instead of `python`
- Reinstall Python if necessary

### Network Connectivity Problems
- Check firewall settings
- Verify proxy configuration
- Try different network (mobile hotspot)
- Contact IT support for corporate networks

### API Authentication Failures
- Verify API keys are correct
- Check for extra spaces in credentials
- Ensure credentials haven't expired
- Request new credentials from organizers

---

## Support Contacts

**During Workshop:**
- Technical Support: [email/slack channel]
- Instructor: [contact info]
- Teaching Assistants: [contact info]

**After Workshop:**
- GitHub Issues: [repository URL]
- Community Forum: [forum URL]
- Email Support: [email address]

---

## Cost Summary

### Organizer Costs (per participant)
- IBM watsonx Orchestrate: Variable (contact IBM)
- IBM watsonx.ai: ~$5-10 (token usage)
- DataStax Astra DB: Free tier or ~$5
- Langflow: Included with Astra DB
- **Total Estimated: $10-20 per participant**

### Participant Costs
- **Free** - All services provided by organizers
- Optional: Personal accounts for continued learning after workshop

---

## Post-Workshop Cleanup

### Organizers
- [ ] Revoke temporary credentials
- [ ] Archive workshop data
- [ ] Delete temporary databases (if applicable)
- [ ] Collect feedback
- [ ] Document lessons learned

### Participants
- [ ] Save your work to personal repository
- [ ] Export any flows or agents created
- [ ] Request extended access if continuing learning
- [ ] Provide feedback to organizers