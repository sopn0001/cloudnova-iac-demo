# CloudNova — AI-Assisted Terraform Review & Deployment

**CDEV2400 Applied Project**

> **Catching Misconfigurations Before They Ship:** AI-assisted IaC review for CloudNova, a mid-size SaaS company whose DevOps team needs automated security, cost, and governance checks on Terraform **before** every merge.

## The scenario

CloudNova has 4 DevOps engineers, deploys 20+ times/week via Terraform, and relies on one senior engineer for manual PR review. Last quarter a rushed merge left **public storage** exposed for 3 weeks. They also found **oversized VMs** and **forgotten disks** on the bill.

This project demonstrates catching those issues — open ports, public storage, cost waste — **in code**, using AI + policy-as-code + CI/CD.

## What's in this repo

```
├── infra/terraform/
│   ├── flawed/          # Intentionally bad CloudNova dev stack (demo only)
│   └── fixed/           # Remediated template (deploy this)
├── policies/
│   ├── checkov.yaml     # Policy-as-code
│   └── naming-standards.json
├── scripts/
│   └── generate_review_summary.py
├── docs/
│   ├── DEMO_SCRIPT.md           # 12–15 min presentation guide
│   ├── PRESENTATION_SLIDES.md   # Slide outline + citations
│   ├── AI_REVIEW_FINDINGS.md    # Pre-written AI review results
│   └── AI_REVIEW_PROMPT.md      # Copy-paste Cursor prompts
└── .github/workflows/
    └── iac-review-deploy.yml
```

## CloudNova resources (Terraform)

| Resource | Flawed issue | Fixed approach |
|----------|--------------|----------------|
| NSG | SSH port 22 open to `*` | Deny SSH from Internet |
| Storage | Public blob access | Private, HTTPS, network deny |
| VM | `Standard_D8s_v3` + password auth | `Standard_B2s` + SSH key |
| Managed disk | 512 GB orphan (cost leak) | Removed |
| App Service | P1v3, no HTTPS, secrets in code | B1, HTTPS, Key Vault |

## Quick start

### 1. AI review (no Azure needed)

```bash
python3 scripts/generate_review_summary.py \
  --template infra/terraform/flawed/main.tf \
  --standards policies/naming-standards.json \
  --output ai-review-summary.md
```

Open `infra/terraform/flawed/main.tf` in Cursor — prompt in `docs/AI_REVIEW_PROMPT.md`.

### 2. Validate Terraform

```bash
cd infra/terraform/flawed && terraform init -backend=false && terraform validate
cd ../fixed && terraform init -backend=false && terraform validate
```

### 3. Policy-as-code scan

```bash
pip install checkov
checkov -d infra/terraform/ --framework terraform
```

## Azure deployment

### Prerequisites

```bash
brew install terraform azure-cli
az login
az account set --subscription "<your-subscription-id>"
```

### Deploy fixed template

```bash
cd infra/terraform/fixed
SUB_ID=$(az account show --query id -o tsv)

terraform init
terraform plan -var="ssh_public_key=$(cat ~/.ssh/id_rsa.pub)"
```

## CI/CD integration (GitHub → PR comment → Azure)

**Full setup guide:** `docs/SETUP_GITHUB_AZURE.md`

### Flow

1. **Open PR** with changes to `infra/terraform/flawed/main.tf`
2. **GitHub Actions** runs `terraform validate`, Checkov, and `generate_review_summary.py`
3. **PR comment** posted automatically — 🚫 BLOCKED if critical issues found
4. **Apply review** — fix code, push to PR (comment updates)
5. **Merge to `main`** → `terraform apply` deploys `infra/terraform/fixed/` to Azure

### GitHub secrets required

| Secret | Purpose |
|--------|---------|
| `AZURE_CLIENT_ID` | OIDC app registration |
| `AZURE_TENANT_ID` | Entra ID tenant |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription |
| `SSH_PUBLIC_KEY` | VM SSH key for fixed template |

## Presentation

- **GitHub + Azure setup:** `docs/SETUP_GITHUB_AZURE.md` ← **integration guide**
- **Live demo runbook:** `docs/LIVE_DEMO.md`
- **Demo script:** `docs/DEMO_SCRIPT.md`
- **Slides:** `docs/PRESENTATION_SLIDES.md`
- **Findings backup:** `docs/AI_REVIEW_FINDINGS.md`

### Pre-flight (30 min before presenting)

```bash
./scripts/preflight_demo.sh
```

## Cleanup

```bash
cd infra/terraform/fixed && terraform destroy  # same -var flags as plan
az group delete --name rg-cloudnova --yes
```
