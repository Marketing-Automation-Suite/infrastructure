# Marketing Automation Pipeline - Infrastructure Repository

**The "God Repo"** - Entry point for the entire Marketing Automation Suite ecosystem.

## Quick Start

1. Clone this repository:
```bash
git clone https://github.com/Marketing-Automation-Suite/infrastructure.git
cd infrastructure
```

2. Set up all service repositories:
```bash
./scripts/setup-dev.sh
```

3. Start all services:
```bash
cd docker
docker compose up -d
```

## Repository Structure

This repository orchestrates all 12 service repositories:

### Submodule Repositories (7)
- **xlam-server** - AI function calling service (model-agnostic)
- **n8n-orchestration** - Workflow orchestration
- **crm-twenty** - Modern CRM
- **mautic-integration** - Marketing automation
- **analytics-lightdash** - Business intelligence
- **dashboard-streamlit** - Commander's Console
- **shared-libraries** - Common code (jarvis_core)

### Services in Infrastructure Repo (5)
- **mcp-config-server** - MCP configuration and service marketplace
- **nft-software-engine** - NFT-based software licensing system
- **auth-service** - Authentication and JWT token management
- **token-verification-service** - Blockchain token verification
- **payment-service** - Payment processing and subscription management

### Infrastructure
- **infrastructure** (this repo) - Orchestration and deployment

## Architecture

See `docs/architecture/` for detailed architecture documentation.

## Development

See `docs/deployment/docker-deployment.md` for development setup instructions.

