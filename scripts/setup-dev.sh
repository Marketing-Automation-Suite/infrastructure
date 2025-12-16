#!/bin/bash

# setup-dev.sh - Clone all service repositories as git submodules
# This script sets up the complete development environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Setting up Marketing Automation Suite development environment..."
echo ""

# Check if git is initialized
if [ ! -d "$PROJECT_ROOT/.git" ]; then
    echo "❌ Error: This directory is not a git repository."
    echo "   Please initialize git first: git init"
    exit 1
fi

# Create services directory if it doesn't exist
SERVICES_DIR="$PROJECT_ROOT/services"
mkdir -p "$SERVICES_DIR"

# GitHub organization
ORG="Marketing-Automation-Suite"

# List of repositories to clone
REPOS=(
    "xlam-server"
    "n8n-orchestration"
    "crm-twenty"
    "mautic-integration"
    "analytics-lightdash"
    "dashboard-streamlit"
    "shared-libraries"
)

echo "📦 Cloning service repositories as git submodules..."
echo ""

# Initialize submodules if .gitmodules exists
if [ -f "$PROJECT_ROOT/.gitmodules" ]; then
    echo "Initializing existing submodules..."
    git submodule update --init --recursive
else
    echo "⚠️  Warning: .gitmodules file not found."
    echo "   Creating submodules manually..."
    
    for repo in "${REPOS[@]}"; do
        REPO_URL="https://github.com/${ORG}/${repo}.git"
        REPO_PATH="$SERVICES_DIR/$repo"
        
        if [ -d "$REPO_PATH" ]; then
            echo "⏭️  Skipping $repo (already exists)"
        else
            echo "📥 Cloning $repo..."
            git submodule add "$REPO_URL" "$REPO_PATH" || {
                echo "⚠️  Repository $repo doesn't exist yet. Creating placeholder..."
                mkdir -p "$REPO_PATH"
                cd "$REPO_PATH"
                git init
                echo "# $repo" > README.md
                echo "Repository will be created at: $REPO_URL" >> README.md
                git add README.md
                git commit -m "Initial placeholder"
                cd "$PROJECT_ROOT"
            }
        fi
    done
fi

echo ""
echo "✅ Service repositories cloned successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Review and customize docker/.env.example"
echo "   2. Copy docker/.env.example to docker/.env.global"
echo "   3. Run: cd docker && docker compose up -d"
echo ""
echo "🎉 Development environment setup complete!"

