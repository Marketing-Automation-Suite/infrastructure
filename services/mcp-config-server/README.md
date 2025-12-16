# MCP Configuration Server

Service marketplace and configuration system for external marketing services. Enables agentic discovery, configuration, and management of integrations through MCP tools.

## Features

- **Service Marketplace**: Discover available integrations
- **Agentic Configuration**: AI-guided setup process
- **Plugin Architecture**: Extensible connector system
- **Secure Storage**: Encrypted credential management
- **Connection Testing**: Automatic validation

## Quick Start

```bash
# Using Docker
docker compose up -d mcp-config-server

# Access API
curl http://localhost:8001/health
```

## Architecture

The server provides MCP tools that can be called by the AI agent to:
- Discover available services
- Configure service credentials
- Test connections
- Manage configurations

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn src.server:app --host 0.0.0.0 --port 8001
```

## Service Connectors

Connectors are located in `src/connectors/`. Each connector implements the `BaseConnector` interface.

## Service Definitions

Service metadata is defined in YAML files in `src/registry/service_definitions/`.

