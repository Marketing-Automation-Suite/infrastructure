# Phase 5: The Face - Dashboard Implementation

## Objectives

Build Streamlit dashboard with chat interface and metrics.

## dashboard-streamlit Repository

### Setup Steps

1. Create repository: `Marketing-Automation-Suite/dashboard-streamlit`
2. Set up git submodule for `shared-libraries`
3. Build Streamlit app
4. Integrate with all services

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

