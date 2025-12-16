#!/bin/bash

# health-check.sh - Check health of all services
# This script verifies that all services are running and healthy

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCKER_DIR="$PROJECT_ROOT/docker"

echo "🏥 Checking service health..."
echo ""

# Check if docker-compose is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

cd "$DOCKER_DIR"

# Check if services are running
echo "📊 Service Status:"
docker compose ps

echo ""
echo "🔍 Health Checks:"

# Check Postgres
if docker compose ps postgres | grep -q "Up"; then
    if docker compose exec -T postgres pg_isready -U marketing > /dev/null 2>&1; then
        echo "✅ Postgres: Healthy"
    else
        echo "❌ Postgres: Unhealthy"
    fi
else
    echo "⚠️  Postgres: Not running"
fi

# Check Redis
if docker compose ps redis | grep -q "Up"; then
    if docker compose exec -T redis redis-cli ping | grep -q "PONG"; then
        echo "✅ Redis: Healthy"
    else
        echo "❌ Redis: Unhealthy"
    fi
else
    echo "⚠️  Redis: Not running"
fi

# Check other services
SERVICES=("xlam-server" "n8n" "crm-twenty" "mautic" "lightdash" "dashboard-streamlit")

for service in "${SERVICES[@]}"; do
    if docker compose ps "$service" | grep -q "Up"; then
        echo "✅ $service: Running"
    else
        echo "⚠️  $service: Not running"
    fi
done

echo ""
echo "✅ Health check complete!"

