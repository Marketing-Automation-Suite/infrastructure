#!/bin/bash

# update-all.sh - Update all git submodule repositories
# This script pulls the latest changes from all service repositories

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔄 Updating all service repositories..."
echo ""

# Check if .gitmodules exists
if [ ! -f "$PROJECT_ROOT/.gitmodules" ]; then
    echo "❌ Error: .gitmodules file not found."
    echo "   Please run ./scripts/setup-dev.sh first"
    exit 1
fi

# Update all submodules
echo "📥 Pulling latest changes from all repositories..."
git submodule update --remote --recursive

echo ""
echo "✅ All service repositories updated!"
echo ""
echo "📋 Updated repositories:"
git submodule status

