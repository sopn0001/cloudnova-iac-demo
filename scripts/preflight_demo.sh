#!/usr/bin/env bash
# CloudNova live demo pre-flight — run 30 minutes before presenting.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

echo "=== CloudNova Live Demo Pre-flight ==="
echo ""

# Tools
command -v python3 >/dev/null && pass "python3 found" || fail "python3 not found"
command -v terraform >/dev/null && pass "terraform found ($(terraform version | head -1))" || fail "terraform not found — brew install terraform"
command -v az >/dev/null && pass "azure-cli found" || warn "azure-cli not found (optional unless running terraform plan)"

# Generate fresh AI review backup
python3 scripts/generate_review_summary.py \
  --template infra/terraform/flawed/main.tf \
  --standards policies/naming-standards.json \
  --output ai-review-summary.md
pass "Generated ai-review-summary.md (backup for live demo)"

# Terraform validate
for dir in flawed fixed; do
  (cd "infra/terraform/$dir" && terraform init -backend=false -input=false >/dev/null 2>&1 && terraform validate >/dev/null)
  pass "terraform validate: infra/terraform/$dir"
done

# Checkov (optional)
if command -v checkov >/dev/null; then
  checkov -d infra/terraform/flawed --framework terraform --quiet --compact 2>/dev/null | head -20 || true
  pass "checkov scan completed (review output above)"
else
  warn "checkov not installed — pip install checkov (optional for live demo)"
fi

# Backup artifacts
mkdir -p demo-backup
cp ai-review-summary.md demo-backup/
cp docs/AI_REVIEW_FINDINGS.md demo-backup/
checkov -d infra/terraform/flawed --framework terraform --compact 2>/dev/null > demo-backup/checkov-flawed.txt || echo "(checkov not run)" > demo-backup/checkov-flawed.txt
pass "Backup artifacts saved to demo-backup/"

echo ""
echo "=== Pre-flight complete ==="
echo ""
echo "Open these before presenting:"
echo "  1. infra/terraform/flawed/main.tf"
echo "  2. infra/terraform/fixed/main.tf  (split editor)"
echo "  3. ai-review-summary.md           (backup tab)"
echo "  4. docs/AI_REVIEW_PROMPT.md       (copy prompt from here)"
echo "  5. GitHub PR Actions tab          (screenshot backup)"
echo ""
echo "See docs/LIVE_DEMO.md for the minute-by-minute script."
