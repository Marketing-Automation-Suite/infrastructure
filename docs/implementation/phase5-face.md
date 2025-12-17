# Phase 5: The Face - Dashboard Implementation

## Objectives

**MVP Dashboard:** Build production dashboard using React, HTML, and modern web technologies.

**Prototype Testing:** Use Streamlit dashboard for quick prototype testing and validation.

## MVP Dashboard (Production)

The production MVP dashboard will be built using:
- **React** - Modern frontend framework
- **HTML/CSS** - Core web technologies
- **Modern JavaScript** - ES6+ features
- **API Integration** - Connect to all backend services

### MVP Dashboard Features
- Chat interface for Admin Agent (natural language commands)
- Metrics dashboard (analytics visualization)
- Workflow management interface
- Wallet management (NFT integration)
- Upgrade system (tier management)
- Referrals system
- Revenue tracking

## dashboard-streamlit Repository (Prototype Testing)

**Purpose:** Quick prototype testing and validation before MVP development.

The Streamlit dashboard serves as a rapid prototyping tool to:
- Test API integrations
- Validate service connections
- Prototype UI/UX concepts
- Quick demos and proof-of-concept

### Setup Steps

1. Create repository: `Marketing-Automation-Suite/dashboard-streamlit`
2. Set up git submodule for `shared-libraries`
3. Build Streamlit app for prototype testing
4. Integrate with all services for validation

### App Structure

```
src/
├── app.py                    # Main Streamlit app
├── pages/
│   ├── chat_agent.py        # AI chat interface
│   ├── metrics.py           # Analytics dashboard
│   └── workflows.py         # Workflow management
└── components/
    ├── chat_interface.py
    └── metric_cards.py
```

### Chat Interface (chat_agent.py)

```python
import streamlit as st
from shared_libraries.api_clients.python.n8n_client import N8NClient

st.title("Admin Agent Chat")

# Initialize client
n8n = N8NClient(base_url=os.getenv("N8N_URL"))

# Chat interface
user_input = st.chat_input("Enter your command...")

if user_input:
    # Send to n8n webhook
    response = n8n.trigger_workflow(
        workflow_id="router",
        data={"prompt": user_input}
    )
    st.write(response)
```

### Metrics Dashboard (metrics.py)

```python
import streamlit as st
from shared_libraries.api_clients.python.crm_client import CRMClient

st.title("Marketing Metrics")

crm = CRMClient(base_url=os.getenv("CRM_TWENTY_URL"))

# Fetch metrics
leads = crm.get_leads()
st.metric("Total Leads", len(leads))
```

## Integration Points

1. **AI Function Calling Client** - From shared-libraries
2. **n8n Webhooks** - Trigger workflows
3. **CRM API** - Display lead metrics
4. **Lightdash** - Advanced analytics

## Milestone

✅ Full end-to-end demo working

