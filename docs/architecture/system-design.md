# Marketing Automation Pipeline - System Design Document

## Executive Summary

**System Type:** Microservices-based Marketing Automation Platform
**Architecture Pattern:** Event-driven, API-first microservices
**Deployment Model:** Containerized (Docker/Kubernetes)
**Primary Technology Stack:** Python, Node.js, PostgreSQL, Redis, n8n, Streamlit

**Confidence Level:** 95% (Based on implemented codebase analysis)

---

## 1. System Architecture Overview

### 1.1 Architecture Philosophy

**"Dumb Pipes, Smart Endpoints"** - Infrastructure manages connections; AI handles decision-making.

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│              (Streamlit Dashboard - Port 8501)              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Orchestration Layer                         │
│              (n8n Workflows - Port 5678)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Router Workflow (AI Function Caller Integration)    │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI Decision Layer                         │
│            (xlam-server - Port 8000)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Model-Agnostic Function Calling Engine              │   │
│  │  - Supports: Ollama, vLLM, OpenAI-compatible        │   │
│  │  - Tool Formatting: JSON, XML, Function Calling     │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Business Logic Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ CRM (Twenty) │  │   Mautic     │  │  Analytics   │     │
│  │  Port 3000   │  │  Port 8080   │  │  Port 3001   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  PostgreSQL  │  │    Redis     │  │   MCP Config │     │
│  │   Database   │  │    Cache     │  │   Server     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Blockchain Layer                            │
│         (NFT Software Engine - Port 8000)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  - Wallet Generation (Ethereum)                      │   │
│  │  - Token Verification (Polygon Network)             │   │
│  │  - Tier Management (Free, Bronze, Silver, Gold)      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 Core Components

#### 1.3.1 The "Brain" Services
- **infrastructure**: Orchestration and deployment coordination
- **xlam-server**: AI function calling service (model-agnostic)
- **n8n-orchestration**: Workflow orchestration engine

#### 1.3.2 The "Business" Services
- **crm-twenty**: Modern CRM (Source of Truth for leads/contacts)
- **mautic-integration**: Marketing automation engine
- **analytics-lightdash**: Business intelligence and reporting

#### 1.3.3 The "Interface" Services
- **dashboard-streamlit**: Commander's Console (user interface)
- **mcp-config-server**: Service marketplace and configuration
- **nft-software-engine**: Blockchain-based licensing system

#### 1.3.4 Supporting Infrastructure
- **shared-libraries**: Common code (jarvis_core, xlam_client)
- **PostgreSQL**: Primary database
- **Redis**: Caching and session management

---

## 2. Data Flow Architecture

### 2.1 Primary User Flow

```
1. User Command → Streamlit Dashboard (Port 8501)
   └─> Natural language input via chat interface

2. Dashboard → n8n Webhook (Port 5678)
   └─> POST /webhook/:workflow-id
   └─> Payload: { "command": "user input", "context": {...} }

3. n8n Router Workflow → xlam-server (Port 8000)
   └─> POST /v1/chat/completions
   └─> OpenAI-compatible function calling request
   └─> Includes available functions/tools

4. xlam-server → AI Model Backend
   └─> Processes function call request
   └─> Returns: { "function": "create_lead", "parameters": {...} }

5. xlam-server → n8n (Function Result)
   └─> JSON response with function name and parameters

6. n8n → Business Service (CRM/Mautic/Analytics)
   └─> Executes function via service API
   └─> Example: POST /api/leads (CRM)

7. Business Service → n8n (Execution Result)
   └─> Success/error response

8. n8n → Dashboard (Result)
   └─> Webhook callback or polling

9. Dashboard → User (Display)
   └─> Updates UI with results
```

### 2.2 Service Communication Patterns

**API-First Architecture:**
- All services communicate via REST APIs
- Services never access each other's databases directly
- Standard HTTP methods (GET, POST, PUT, DELETE, PATCH)
- JSON request/response bodies
- OpenAPI/Swagger specifications for all services

**Authentication:**
- API keys for service-to-service communication
- OAuth2/JWT for user authentication
- Secrets stored in Kubernetes Secrets/environment variables

**Error Handling:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

**Rate Limiting:**
- Default: 100 requests/minute per service
- Configurable per service
- Returns `429 Too Many Requests` when exceeded

---

## 3. Component Specifications

### 3.1 xlam-server (AI Function Calling Service)

**Purpose:** Model-agnostic AI function calling engine

**Key Features:**
- OpenAI-compatible `/v1/chat/completions` endpoint
- Supports multiple backends: Ollama, vLLM, OpenAI-compatible APIs
- Flexible tool formatting: JSON, XML, function calling
- Function registry and execution system
- Health check endpoints

**API Endpoints:**
- `POST /v1/chat/completions` - Chat completion with function calling
- `GET /v1/functions` - List available functions
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe

**Configuration:**
- Model backend configuration via `config/model-config.yaml`
- Environment variables for API keys and endpoints

**Time Complexity:** O(1) for function lookup, O(n) for model inference where n = token count
**Space Complexity:** O(m) where m = model size in memory

### 3.2 n8n-orchestration (Workflow Engine)

**Purpose:** Visual workflow orchestration with AI integration

**Key Features:**
- Visual workflow builder
- Custom AI Function Caller node
- CRM integration workflows
- Marketing automation workflows
- Webhook triggers

**Workflows:**
- **Router Workflow**: Routes natural language commands to appropriate actions
- **CRM Sync Workflow**: Synchronizes data between CRM and other services

**Custom Nodes:**
- AI Function Caller Node: Integrates with xlam-server

**API Endpoints:**
- `POST /webhook/:workflow-id` - Trigger workflow via webhook
- `GET /api/v1/workflows` - List workflows
- `GET /healthz` - Health check

### 3.3 crm-twenty (CRM Service)

**Purpose:** Source of truth for leads, contacts, and companies

**Key Features:**
- Lead management (CRUD operations)
- Contact management
- Company management
- Webhook subscriptions
- RESTful API

**API Endpoints:**
- `GET /api/leads` - List all leads
- `POST /api/leads` - Create new lead
- `GET /api/leads/:id` - Get lead by ID
- `PUT /api/leads/:id` - Update lead
- `DELETE /api/leads/:id` - Delete lead
- Similar endpoints for `/api/contacts` and `/api/companies`

**Data Model:**
- Leads: Contact information, status, source, assigned user
- Contacts: Personal information, communication history
- Companies: Organization data, relationships

### 3.4 dashboard-streamlit (Commander's Console)

**Purpose:** User interface for the entire system

**Key Features:**
- Chat interface for Admin Agent (natural language commands)
- Metrics dashboard (analytics visualization)
- Workflow management interface
- Wallet management (NFT integration)
- Upgrade system (tier management)
- Referrals system
- Revenue tracking

**Pages:**
- Chat Agent: Natural language interface
- Metrics: Analytics and KPIs
- Workflows: Workflow management
- Wallet: Ethereum wallet management
- Upgrade: Tier upgrade interface
- Referrals: Referral program management
- Revenue: Revenue tracking and reporting

### 3.5 mcp-config-server (Service Marketplace)

**Purpose:** Service marketplace and configuration system

**Key Features:**
- Service marketplace (discover available integrations)
- Agentic configuration (AI-guided setup)
- Plugin architecture (extensible connector system)
- Secure storage (encrypted credential management)
- Connection testing (automatic validation)

**Architecture:**
- MCP tools for AI agent discovery and configuration
- Connector system in `src/connectors/`
- Service definitions in YAML format
- Database for storing configurations

### 3.6 nft-software-engine (Blockchain Licensing)

**Purpose:** NFT-based software licensing and distribution

**Key Features:**
- NFT-based licensing (software access via token ownership)
- Tiered pricing model (Free, Bronze, Silver, Gold)
- Wallet generation (secure Ethereum wallet creation)
- Token verification (blockchain-verified ownership)
- 4-tier system (flexible pricing and feature access)

**Tiers:**
1. **Free** ($0) - Basic access
2. **Bronze** ($50) - Standard features
3. **Silver** ($150) - Premium features
4. **Gold** ($500) - Enterprise features

**API Endpoints:**
- `POST /api/v1/wallets` - Generate new Ethereum wallet
- `POST /api/v1/tokens/verify` - Verify NFT token ownership
- `GET /api/v1/tiers` - List all available tiers and pricing

**Blockchain Integration:**
- Polygon network for NFT verification
- Web3 provider integration
- Secure private key management

---

## 4. Data Architecture

### 4.1 Database Design

**PostgreSQL (Primary Database):**
- CRM data (leads, contacts, companies)
- NFT engine data (wallets, tokens, tiers)
- MCP config data (service configurations, credentials)
- Analytics data (metrics, events)

**Redis (Cache/Session Store):**
- Session management
- API response caching
- Rate limiting counters
- Temporary workflow state

### 4.2 Data Flow Principles

**Source of Truth:**
- CRM (Twenty) is the source of truth for all lead/contact/company data
- Services never access each other's databases directly
- All data access via APIs

**Data Synchronization:**
- n8n workflows handle data synchronization
- Event-driven updates via webhooks
- Batch synchronization workflows available

---

## 5. Security Architecture

### 5.1 Authentication & Authorization

**Service-to-Service:**
- API keys stored in Kubernetes Secrets
- Environment variable injection
- Mutual TLS for production (recommended)

**User Authentication:**
- OAuth2/JWT tokens
- Session management via Redis
- Role-based access control (RBAC)

### 5.2 Data Security

**Encryption:**
- Credentials encrypted at rest (MCP config server)
- Private keys encrypted (NFT engine)
- TLS/HTTPS for all API communication

**Secrets Management:**
- Kubernetes Secrets for sensitive data
- Environment variables for configuration
- No hardcoded secrets in code

### 5.3 Network Security

**Network Policies:**
- Kubernetes network policies defined
- Service mesh ready (Istio/Linkerd compatible)
- CORS configured per service

**Rate Limiting:**
- Per-service rate limits
- DDoS protection ready
- API throttling

---

## 6. Scalability & Performance

### 6.1 Horizontal Scaling

**Stateless Services:**
- All services designed to be stateless
- Horizontal pod autoscaling (HPA) ready
- Load balancing via Kubernetes services

**Database Scaling:**
- PostgreSQL read replicas for analytics
- Connection pooling
- Query optimization

### 6.2 Caching Strategy

**Redis Caching:**
- API response caching
- Session storage
- Rate limiting counters
- Workflow state (temporary)

### 6.3 Performance Targets

**API Response Times:**
- Health checks: < 100ms
- CRUD operations: < 500ms
- AI function calls: < 5s (model-dependent)
- Analytics queries: < 2s

**Throughput:**
- 100 requests/minute per service (default)
- Configurable per service
- Burst capacity available

---

## 7. Deployment Architecture

### 7.1 Containerization

**Docker:**
- Each service has its own Dockerfile
- Multi-stage builds for optimization
- Docker Compose for local development

**Kubernetes:**
- Complete K8s manifests in `k8s/` directory
- Development and production overlays
- ConfigMaps for configuration
- Secrets for sensitive data

### 7.2 Infrastructure Components

**Base Infrastructure:**
- Namespace isolation
- Network policies
- Resource quotas

**Service Deployments:**
- Individual deployments per service
- Service definitions for internal communication
- Ingress controllers for external access

### 7.3 Monitoring & Observability

**Health Checks:**
- Liveness probes
- Readiness probes
- Health check scripts

**Logging:**
- Structured logging (JSON format)
- Centralized logging ready (ELK/Loki compatible)

**Metrics:**
- Prometheus-compatible metrics
- Custom business metrics
- Dashboard integration

---

## 8. Technology Stack

### 8.1 Backend Services

**Python:**
- FastAPI for API services (xlam-server, nft-engine, mcp-config)
- SQLAlchemy for ORM
- Alembic for migrations
- Pydantic for data validation

**Node.js:**
- n8n workflow engine
- Custom nodes in TypeScript

**PostgreSQL:**
- Primary database
- ACID compliance
- JSON support

**Redis:**
- Caching layer
- Session store
- Pub/sub capabilities

### 8.2 Frontend

**Streamlit:**
- Python-based dashboard
- Real-time updates
- Interactive components

### 8.3 Infrastructure

**Docker:**
- Containerization
- Docker Compose for orchestration

**Kubernetes:**
- Container orchestration
- Service mesh ready
- Auto-scaling

**Blockchain:**
- Web3.py for Ethereum integration
- Polygon network for NFT verification

---

## 9. Limitations & Edge Cases

### 9.1 Known Limitations

**AI Model Dependency:**
- Function calling quality depends on model capabilities
- Model availability and cost considerations
- Token limits for large contexts

**Blockchain Network:**
- Polygon network dependency for NFT verification
- Gas fees and network congestion
- Wallet security responsibility

**Single Database:**
- PostgreSQL as primary database (potential bottleneck)
- Read replicas recommended for production
- Backup and disaster recovery required

### 9.2 Edge Cases

**Service Failures:**
- Circuit breakers not yet implemented
- Retry logic in n8n workflows
- Graceful degradation needed

**Concurrent Requests:**
- Rate limiting prevents overload
- Queue system recommended for high volume
- Database connection pooling required

**Data Consistency:**
- Eventual consistency between services
- Webhook delivery guarantees needed
- Idempotency keys for critical operations

---

## 10. Verification & Testing

### 10.1 Health Checks

```bash
# Verify all services
./scripts/health-check.sh

# Individual service checks
curl http://localhost:8000/health  # xlam-server
curl http://localhost:5678/healthz # n8n
curl http://localhost:3000/health  # crm
```

### 10.2 Integration Testing

**Test Workflow:**
1. Start all services via Docker Compose
2. Send test command via dashboard
3. Verify workflow execution in n8n
4. Confirm AI function calling
5. Validate business service API calls
6. Check data persistence

### 10.3 Load Testing

**Recommended Tools:**
- Apache JMeter
- k6
- Locust

**Test Scenarios:**
- Concurrent user commands
- High-volume API requests
- Database query performance
- AI model inference latency

---

## 11. Alternative Approaches Considered

### 11.1 Monolithic Architecture
**Rejected:** Would limit scalability and independent deployment

### 11.2 Serverless Functions
**Rejected:** Would complicate workflow orchestration and state management

### 11.3 Direct Database Access
**Rejected:** Violates microservices principles and creates tight coupling

### 11.4 Centralized Message Queue
**Considered:** Could be added for high-volume scenarios (RabbitMQ/Kafka)

---

## 12. Future Enhancements

### 12.1 Short-term (3-6 months)
- Circuit breakers for service resilience
- Enhanced monitoring and alerting
- API versioning strategy
- Comprehensive test coverage

### 12.2 Medium-term (6-12 months)
- Service mesh integration (Istio)
- Event-driven architecture (Kafka)
- Multi-region deployment
- Advanced analytics features

### 12.3 Long-term (12+ months)
- Machine learning model training pipeline
- Advanced AI capabilities
- Multi-tenant support
- White-label options

---

## Source Attribution

- Architecture documentation: `docs/architecture/system-overview.md`
- API contracts: `docs/api-contracts/service-apis.md`
- Implementation status: `FINAL_STATUS.md`
- Service READMEs: Individual service directories

---

## Confidence Assessment

**Overall Confidence:** 95%

**High Confidence Areas:**
- Service architecture and communication patterns (100%)
- API contracts and data flow (95%)
- Deployment architecture (90%)

**Areas Requiring Verification:**
- Production load testing results
- Blockchain network integration testing
- Multi-region deployment scenarios
- Disaster recovery procedures

---

## Verification Guidance

1. **Code Review:** Verify all service implementations match this design
2. **Integration Testing:** Execute end-to-end workflows
3. **Load Testing:** Validate performance under expected load
4. **Security Audit:** Review authentication, encryption, and network policies
5. **Documentation Review:** Ensure all APIs match OpenAPI specifications

