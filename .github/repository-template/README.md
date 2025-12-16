# Service Repository Template

This is a template for creating new service repositories in the Marketing-Automation-Suite organization.

## Repository Structure

Each service repository should follow this structure:

```
service-name/
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── docs/
│   ├── README.md
│   ├── API.md
│   └── DEPLOYMENT.md
├── .env.example
├── .gitignore
└── README.md
```

## Required Files

- `README.md` - Service overview and quick start
- `docs/API.md` - API documentation
- `docs/DEPLOYMENT.md` - Deployment instructions
- `.env.example` - Environment variable template
- `docker/Dockerfile` - Container image definition
- `k8s/deployment.yaml` - Kubernetes deployment manifest

## CI/CD

Each repository should have GitHub Actions workflows for:
- Testing
- Building Docker images
- Deployment

## Integration

Services communicate via APIs only. See `infrastructure/docs/api-contracts/` for API specifications.

