# Docker Deployment Guide

## Prerequisites

- Docker Desktop installed (8GB+ RAM recommended for AI model inference)
- Git installed
- Basic command-line knowledge

## Initial Setup

1. **Clone the infrastructure repository:**
```bash
git clone https://github.com/Marketing-Automation-Suite/infrastructure.git
cd infrastructure
```

2. **Set up all service repositories:**
```bash
./scripts/setup-dev.sh
```

3. **Configure environment variables:**
```bash
cp docker/env.example docker/.env.global
# Edit docker/.env.global with your settings
```

## Starting Services

### Start Infrastructure Only (Postgres, Redis)
```bash
cd docker
docker compose up -d postgres redis
```

### Start All Services
```bash
cd docker
docker compose --profile services up -d
```

### Start Specific Service
```bash
cd docker
docker compose --profile services up -d xlam-server
```

## Stopping Services

```bash
cd docker
docker compose down
```

## Viewing Logs

```bash
cd docker
docker compose logs -f [service-name]
```

## Health Checks

All services include health check endpoints:
- Postgres: `pg_isready`
- Redis: `redis-cli ping`
- Services: `/health` endpoint

## Troubleshooting

### Services won't start
1. Check Docker Desktop has enough resources (8GB+ RAM)
2. Verify ports aren't already in use
3. Check logs: `docker compose logs`

### Database connection issues
1. Verify Postgres is healthy: `docker compose ps`
2. Check environment variables in `.env.global`
3. Verify network connectivity: `docker network inspect marketing-network`

