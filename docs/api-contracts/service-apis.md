# Service API Contracts

This document defines the API contracts between all services in the Marketing Automation Suite.

## Core Principle

**Services must never access each other's databases directly. Only via API.**

## API Standards

### REST APIs
- Use OpenAPI/Swagger specifications
- Version endpoints: `/v1/`, `/v2/`
- Standard HTTP methods (GET, POST, PUT, DELETE, PATCH)
- JSON request/response bodies
- Standard HTTP status codes

### Authentication
- API keys for service-to-service communication
- OAuth2/JWT for user authentication
- Secrets stored in environment variables

## Service APIs

### xlam-server

**Base URL:** `http://xlam-server:8000`

**Endpoints:**
- `POST /v1/chat/completions` - OpenAI-compatible chat completion
- `GET /v1/functions` - List available functions
- `GET /health` - Health check

**Function Calling:**
- Uses XML-tag format: `<tools>...</tools>`
- Returns JSON with function name and parameters

### n8n-orchestration

**Base URL:** `http://n8n:5678`

**Endpoints:**
- `POST /webhook/:workflow-id` - Trigger workflow via webhook
- `GET /api/v1/workflows` - List workflows
- `GET /healthz` - Health check

### crm-twenty

**Base URL:** `http://crm-twenty:3000`

**Endpoints:**
- `GET /api/leads` - List leads
- `POST /api/leads` - Create lead
- `PUT /api/leads/:id` - Update lead
- `GET /api/contacts` - List contacts
- `POST /api/contacts` - Create contact
- `GET /api/companies` - List companies

### mautic-integration

**Base URL:** `http://mautic:8080`

**Endpoints:**
- `POST /api/contacts/new` - Create contact
- `POST /api/emails/:id/send` - Send email
- `GET /api/campaigns` - List campaigns

### analytics-lightdash

**Base URL:** `http://lightdash:3001`

**Endpoints:**
- `GET /api/v1/projects` - List projects
- `GET /api/v1/metrics` - Get metrics
- Read-only access to Postgres (read replica)

### dashboard-streamlit

**Base URL:** `http://dashboard-streamlit:8501`

**Endpoints:**
- Web interface only (no API)
- Communicates with other services via their APIs

## API Versioning

- URL-based versioning: `/v1/`, `/v2/`
- Breaking changes require new version
- Maintain backward compatibility for at least one version

## Error Handling

All APIs should return consistent error responses:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

## Rate Limiting

- Default: 100 requests/minute per service
- Configurable per service
- Return `429 Too Many Requests` when exceeded

