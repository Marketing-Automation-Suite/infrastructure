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

This repository orchestrates all 11 service repositories:

- **infrastructure** (this repo) - Orchestration and deployment
- **xlam-server** - AI function calling service (model-agnostic)
- **n8n-orchestration** - Workflow orchestration
- **crm-twenty** - Modern CRM
- **mautic-integration** - Marketing automation
- **analytics-lightdash** - Business intelligence
- **dashboard-streamlit** - Commander's Console
- **mcp-config-server** - MCP configuration and service marketplace
- **nft-software-engine** - NFT-based software licensing system
- **shared-libraries** - Common code (jarvis_core)

## Architecture

See `docs/architecture/` for detailed architecture documentation.

## Development

See `docs/deployment/docker-deployment.md` for development setup instructions.

