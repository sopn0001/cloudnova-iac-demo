# CloudNova — Presentation Demo Script

**Title:** Catching Misconfigurations Before They Ship: AI-Assisted IaC Review for a DevOps Team  
**Duration:** 12–15 minutes  
**IaC tool:** Terraform only (Azure)

---

## Before class — setup checklist

1. Push this repo to GitHub.
2. Configure Azure OIDC for GitHub Actions (see `README.md`).
3. Open `infra/terraform/flawed/main.tf` in Cursor.
4. Have `docs/AI_REVIEW_FINDINGS.md` and `docs/PRESENTATION_SLIDES.md` ready.
5. Optional: open a PR to show the sticky AI review comment in GitHub.

---

## Act 1 — Business problem: CloudNova (4 min)

**Say:**  
*"Meet CloudNova — a mid-size SaaS company. Four DevOps engineers manage all infrastructure as Terraform and deploy more than 20 times a week. One senior engineer manually reviews every pull request. He's the bottleneck — reviews sit for days."*

**Say:**  
*"Last quarter, a rushed merge left a storage account publicly accessible for three weeks before anyone noticed. They also found oversized VMs and forgotten disks burning budget."*

**Show slide:** `docs/PRESENTATION_SLIDES.md` — Slide 2–4 (evidence with citations)

**Key stats to mention:**
- ~23% of cloud security incidents stem from **misconfigurations**; ~82% of those are **human error** (Exabeam / industry surveys)
- Gartner: the majority of cloud security failures are the **customer's preventable fault** at the configuration stage
- IBM 2025: average breach cost **$4.44M**; misconfiguration breaches take **~186 days** to detect
- Flexera 2026: **29% of IaaS/PaaS spend is wasted** — idle compute (~35%) and over-provisioned instances (~25%)

**Say:**  
*"CloudNova doesn't need to hire another senior engineer. They need to catch security risks, cost waste, and governance violations in code — before merge."*

---

## Act 2 — The flawed Terraform PR (1 min)

**Say:**  
*"Here's a typical rushed PR — a dev environment for CloudNova's SaaS API. It looks innocent."*

**Show:** `infra/terraform/flawed/main.tf`

**Point at three headline issues without fixing yet:**
1. NSG rule — SSH from `*` (open port)
2. Storage — `allow_nested_items_to_be_public = true`
3. VM — `Standard_D8s_v3` + orphaned 512 GB Premium disk

---

## Act 3 — AI-assisted review (5 min)

**Say:**  
*"We use AI as a first-pass senior reviewer — instant, consistent, and available 24/7."*

### Live demo — paste into Cursor

```
You are reviewing Terraform for CloudNova, a mid-size SaaS company.

Review infra/terraform/flawed/ for:
1. Security risks (open ports, public storage, secrets, TLS)
2. Cost waste (oversized VM, orphan disks, premium SKUs in dev)
3. Naming/governance per policies/naming-standards.json

List findings by severity with concrete Terraform fixes.
Estimate monthly cost impact for the dev environment.
```

**Highlight AI output:**
- SSH port 22 open to `0.0.0.0/0` — **critical**
- Public storage — mirrors CloudNova's real incident
- `Standard_D8s_v3` vs `Standard_B2s` — cost story
- Orphan disk — forgotten resource leak
- Missing `cn-` naming prefix and tags

**Backup:** `docs/AI_REVIEW_FINDINGS.md` if live AI is slow.

---

## Act 4 — Policy-as-code + CI/CD guardrails (3 min)

**Say:**  
*"AI is the fast first pass. Policy-as-code and CI/CD are the guardrails that enforce rules on every PR — no exceptions."*

**Show:** `.github/workflows/iac-review-deploy.yml`

| Job | Purpose |
|-----|---------|
| `validate-terraform` | `terraform validate` on flawed + fixed |
| `security-scan` | Checkov against `policies/checkov.yaml` |
| `ai-review` | Posts CloudNova review summary on PR |
| `deploy-dev` | `terraform plan` + `apply` on merge to `main` |

**Say:**  
*"This is shift-left security — catch misconfigurations in code, before they reach Azure."*

**Optional:** Show PR comment from `scripts/generate_review_summary.py`.

---

## Act 5 — Remediation and deploy (2 min)

**Show:** `infra/terraform/fixed/main.tf` side-by-side with flawed.

| Problem | Fix |
|---------|-----|
| SSH open to internet | NSG denies SSH from Internet |
| Public storage | `allow_nested_items_to_be_public = false`, network deny |
| Oversized VM | `Standard_B2s` in dev |
| Orphan disk | Removed entirely |
| Hardcoded secrets | Key Vault app settings |
| No tags / bad naming | `cn-saasapi-dev-*` + governance tags |

**Show:** GitHub Actions green run or `terraform plan` screenshot.

---

## Act 6 — Wrap-up (1 min)

**Say:**  
*"AI doesn't replace DevOps engineers — it removes the bottleneck. Combined with policy-as-code and CI/CD, CloudNova catches the open port, the public storage, and the oversized VM before merge — not three weeks later on the bill."*

**Skills demonstrated:**
- Infrastructure as Code (Terraform on Azure)
- AI-assisted code review (Cursor)
- Policy-as-code (Checkov)
- Cloud governance (naming, tags)
- DevOps CI/CD pipelines (GitHub Actions)

---

## Q&A prep

| Question | Answer |
|----------|--------|
| Can AI deploy directly? | No — AI reviews; humans merge; pipeline deploys |
| What if AI misses something? | Checkov + `terraform validate` + human review |
| Why Terraform? | CloudNova's stack; portable, industry-standard HCL |
| Cost of this approach? | Near-zero tooling cost; prevents 29% waste category |
