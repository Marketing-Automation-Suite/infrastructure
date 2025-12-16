# Phase 3: The Body - CRM and n8n Implementation

## Objectives

Deploy Twenty CRM and n8n, connect them via API.

## crm-twenty Repository

### Setup Steps

1. Create repository: `Marketing-Automation-Suite/crm-twenty`
2. Set up Twenty CRM (React + Node.js + Postgres)
3. Configure API endpoints
4. Document API in OpenAPI format

### API Endpoints Required

- `GET /api/leads` - List leads
- `POST /api/leads` - Create lead
- `PUT /api/leads/:id` - Update lead
- `GET /api/contacts` - List contacts
- `POST /api/contacts` - Create contact
- `GET /api/companies` - List companies

### Database Setup

```sql
-- Create database for Twenty CRM
CREATE DATABASE twenty_db;

-- Tables will be created by Twenty CRM migrations
```

## n8n-orchestration Repository

### Setup Steps

1. Create repository: `Marketing-Automation-Suite/n8n-orchestration`
2. Deploy n8n service
3. Configure connection to Postgres
4. Create test workflow

### n8n Configuration

```yaml
# Environment variables
DB_TYPE: postgresdb
DB_POSTGRESDB_HOST: postgres
DB_POSTGRESDB_PORT: 5432
DB_POSTGRESDB_DATABASE: n8n
DB_POSTGRESDB_USER: marketing
DB_POSTGRESDB_PASSWORD: marketing_password
```

### Test Workflow

Create a simple workflow that:
1. Receives webhook trigger
2. Calls Twenty CRM API to create a lead
3. Returns success response

## Connection Setup

### n8n → Twenty CRM

1. In n8n, create HTTP Request node
2. Configure to call `http://crm-twenty:3000/api/leads`
3. Use API credentials from environment variables
4. Test connection

## Milestone

✅ n8n can successfully create a lead in Twenty

