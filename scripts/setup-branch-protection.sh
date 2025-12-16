#!/bin/bash

# Setup branch protection rules for all repositories
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

echo "🛡️ Setting up branch protection rules..."

for repo in "${REPOS[@]}"; do
  echo "  Setting up branch protection for $repo..."
  
  # Create branch protection rule using GitHub API
  gh api repos/$ORG/$repo/branches/main/protection \
    -X PUT \
    -f required_status_checks='{"strict":true,"contexts":[]}' \
    -f enforce_admins=true \
    -f required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":false}' \
    -f restrictions=null \
    -f allow_force_pushes=false \
    -f allow_deletions=false \
    -f block_creations=false \
    -f required_conversation_resolution=false \
    2>&1 | grep -E "(error|message|HTTP)" || echo "    ✅ Branch protection enabled for $repo"
done

echo ""
echo "✅ Branch protection setup complete!"

