#!/usr/bin/env bash
# Configure GitHub Actions secrets and workflow permissions.
# Prerequisites: gh auth login (run once: gh auth login -h github.com -p https -w)

set -euo pipefail

REPO="sopn0001/cloudnova-iac-demo"
AZURE_CLIENT_ID="95549284-68b6-4a40-afb6-4db00f3887f7"
AZURE_TENANT_ID="0f69441c-29e3-4293-9c7a-c6b8ec38e66e"
AZURE_SUBSCRIPTION_ID="1539b06f-7167-4e7d-a533-c342e2c6cdb4"

if ! gh auth status &>/dev/null; then
  echo "Not logged in to GitHub. Run: gh auth login -h github.com -p https -w"
  exit 1
fi

SSH_KEY="${HOME}/.ssh/id_rsa.pub"
if [[ ! -f "$SSH_KEY" ]]; then
  SSH_KEY="${HOME}/.ssh/id_ed25519.pub"
fi
if [[ ! -f "$SSH_KEY" ]]; then
  echo "No SSH public key found. Generate one with: ssh-keygen -t ed25519"
  exit 1
fi

echo "Setting repository secrets..."
gh secret set AZURE_CLIENT_ID --repo "$REPO" --body "$AZURE_CLIENT_ID"
gh secret set AZURE_TENANT_ID --repo "$REPO" --body "$AZURE_TENANT_ID"
gh secret set AZURE_SUBSCRIPTION_ID --repo "$REPO" --body "$AZURE_SUBSCRIPTION_ID"
gh secret set SSH_PUBLIC_KEY --repo "$REPO" --body "$(cat "$SSH_KEY")"

# if [ -n "${OPENAI_API_KEY:-}" ]; then
#   gh secret set OPENAI_API_KEY --repo "$REPO" --body "$OPENAI_API_KEY"
#   echo "OPENAI_API_KEY secret set (live AI reviews enabled)"
# else
#   echo "OPENAI_API_KEY not set in shell — PR reviews will use rule-based fallback"
# fi

echo "Enabling workflow write permissions (required for PR comments)..."
gh api -X PUT "repos/${REPO}/actions/permissions/workflow" \
  -f default_workflow_permissions=write \
  -F can_approve_pull_request_reviews=true

echo ""
echo "Done. Verify at:"
echo "  https://github.com/${REPO}/settings/secrets/actions"
