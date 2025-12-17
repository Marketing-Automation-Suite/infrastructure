# System Overview

## Architecture Philosophy

**"Dumb Pipes, Smart Endpoints"** - The infrastructure (Docker/K8s) manages connections, while the AI function calling service handles decision-making.

## Core Components

### The "Brain" Repositories
- **infrastructure** - Orchestration and deployment (this repo)
- **xlam-server** - AI function calling service (model-agnostic)
- **n8n-orchestration** - Workflow orchestration

### The "Business" Repositories
- **crm-twenty** - Modern CRM (Source of Truth)
- **mautic-integration** - Marketing automation
- **analytics-lightdash** - Business intelligence

### The "Interface" Repositories
- **MVP Dashboard** - Production dashboard (React/HTML) - *To be implemented*
- **dashboard-streamlit** - Prototype testing dashboard (Streamlit) - *For quick testing and validation*
- **shared-libraries** - Common code (jarvis_core)

## Service Communication

All services communicate via well-defined APIs. Services never access each other's databases directly.

## Data Flow

1. User command → MVP Dashboard (React) or Streamlit Prototype
2. Dashboard → n8n (webhook)
3. n8n → AI Server (function call request)
4. AI Server → n8n (function result)
5. n8n → CRM/Mautic (API calls)
6. Results → Dashboard → User

**Note:** The Streamlit dashboard (`dashboard-streamlit`) is used for rapid prototype testing and API validation. The production MVP will use a React-based dashboard.

See `diagrams/` for detailed architecture diagrams.

