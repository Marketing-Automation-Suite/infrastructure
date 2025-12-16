#!/bin/bash

# verify-setup.sh - Verify Phase 1 setup is complete
# This script checks that all required files and structure are in place

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔍 Verifying Phase 1 setup..."
echo ""

ERRORS=0

# Check required files
REQUIRED_FILES=(
    "README.md"
    ".gitignore"
    ".gitmodules"
    "CHANGELOG.md"
    "docker/docker-compose.yml"
    "docker/docker-compose.override.yml"
    "docker/env.example"
    "scripts/setup-dev.sh"
    "scripts/update-all.sh"
    "scripts/health-check.sh"
    "docs/architecture/system-overview.md"
    "docs/deployment/docker-deployment.md"
    "k8s/base/namespace.yaml"
    "k8s/base/network-policies.yaml"
    "k8s/base/resource-quotas.yaml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""

# Check scripts are executable
EXECUTABLE_SCRIPTS=(
    "scripts/setup-dev.sh"
    "scripts/update-all.sh"
    "scripts/health-check.sh"
)

for script in "${EXECUTABLE_SCRIPTS[@]}"; do
    if [ -x "$PROJECT_ROOT/$script" ]; then
        echo "✅ $script (executable)"
    else
        echo "❌ $script (not executable)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""

# Validate docker-compose
echo "🔍 Validating docker-compose configuration..."
cd "$PROJECT_ROOT/docker"
if docker compose config --quiet > /dev/null 2>&1; then
    echo "✅ docker-compose.yml is valid"
else
    echo "❌ docker-compose.yml has errors"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# Check .gitmodules has all 7 repositories
echo "🔍 Checking .gitmodules..."
if [ -f "$PROJECT_ROOT/.gitmodules" ]; then
    SUBMODULE_COUNT=$(grep -c "\[submodule" "$PROJECT_ROOT/.gitmodules" || echo "0")
    if [ "$SUBMODULE_COUNT" -eq 7 ]; then
        echo "✅ .gitmodules has 7 submodules"
    else
        echo "⚠️  .gitmodules has $SUBMODULE_COUNT submodules (expected 7)"
    fi
else
    echo "❌ .gitmodules not found"
    ERRORS=$((ERRORS + 1))
fi

echo ""

if [ $ERRORS -eq 0 ]; then
    echo "✅ Phase 1 setup verification complete! All checks passed."
    echo ""
    echo "📋 Next steps:"
    echo "   1. Run: ./scripts/setup-dev.sh (to clone service repos)"
    echo "   2. Copy docker/env.example to docker/.env.global"
    echo "   3. Run: cd docker && docker compose up -d postgres redis"
    exit 0
else
    echo "❌ Verification failed with $ERRORS error(s)"
    exit 1
fi

