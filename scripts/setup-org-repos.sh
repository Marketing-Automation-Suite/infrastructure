#!/bin/bash

# Setup script for all repositories in the organization
# This script configures branch protection, labels, and other settings

ORG="Marketing-Automation-Suite"
REPOS=(
  "infrastructure"
  "xlam-server"
  "n8n-orchestration"
  "crm-twenty"
  "mautic-integration"
  "analytics-lightdash"
  "dashboard-streamlit"
  "shared-libraries"
)

# Standard labels for all repositories
LABELS=(
  "bug:FF0000:Bug or issue with the code"
  "enhancement:00FF00:New feature or enhancement"
  "documentation:0066FF:Documentation improvements"
  "question:FF9900:Question or discussion"
  "help wanted:FF00FF:Help needed from the community"
  "good first issue:00FFFF:Good for newcomers"
  "priority: high:FF0000:High priority item"
  "priority: medium:FF9900:Medium priority item"
  "priority: low:00FF00:Low priority item"
  "wontfix:808080:Will not be fixed"
  "duplicate:808080:Duplicate issue"
  "invalid:808080:Invalid issue"
)

echo "🚀 Setting up repositories in $ORG organization..."

for repo in "${REPOS[@]}"; do
  echo ""
  echo "📦 Setting up $repo..."
  
  # Create labels
  for label in "${LABELS[@]}"; do
    IFS=':' read -r name color desc <<< "$label"
    gh label create "$name" \
      --repo "$ORG/$repo" \
      --color "$color" \
      --description "$desc" \
      --force 2>/dev/null || echo "  Label '$name' already exists or created"
  done
  
  echo "  ✅ Labels configured for $repo"
done

echo ""
echo "✅ All repositories configured!"

