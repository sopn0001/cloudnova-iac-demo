# CloudNova Business Scenario

Reference document for the presentation business-problem segment.

## Company profile

**CloudNova** is a mid-size B2B SaaS company. Their platform serves hundreds of enterprise customers. Infrastructure runs entirely on **Microsoft Azure**, managed as **Terraform** by a **4-person DevOps team**.

## Operating model

- **20+ Terraform deployments per week** across dev, staging, and production
- **One senior engineer** manually reviews every infrastructure PR
- Junior engineers wait **days** for review — velocity suffers
- No dedicated security team reviewing IaC line-by-line

## Incidents that motivate this project

### Security — public storage (last quarter)

A rushed Friday merge deployed a storage account with public blob access enabled. Nobody noticed for **three weeks**. A security scan finally flagged anonymous read access to customer backup metadata.

**Root cause:** Human review missed `allow_nested_items_to_be_public = true` in a 200-line Terraform PR.

### Cost — oversized and forgotten resources

FinOps review discovered:
- Dev API workers running on **Standard_D8s_v3** (production-sized)
- A **512 GB Premium managed disk** left over from a decommissioned VM — still billing monthly
- **Premium_LRS** storage where Standard would suffice

## What CloudNova needs

Automatic pre-merge review for:

1. **Security** — open ports, public endpoints, secrets in code, weak TLS
2. **Cost** — right-sizing, orphan resources, dev vs prod SKU tiers
3. **Governance** — naming (`cn-{app}-{env}-{type}`), required tags, policy compliance

**Without hiring another senior engineer.**

## Our solution

| Layer | Tool | Role |
|-------|------|------|
| First pass | Cursor AI | Instant contextual review with remediation |
| Enforcement | Checkov | Policy-as-code — blocks known misconfigurations |
| Pipeline | GitHub Actions | validate → scan → review comment → deploy |
| Deploy target | Azure | `rg-cloudnova-dev` via OIDC |

## Evidence for slides (with sources)

### Misconfigurations dominate cloud security

- **~23%** of cloud security incidents stem from misconfigurations
- **~82%** of misconfigurations caused by human error, not software flaws
- Gartner: through 2025–2026, the **overwhelming majority** of cloud security failures will be the customer's own preventable fault

*Sources: Exabeam, industry cloud security surveys, Gartner predictions*

### Breaches are expensive and slow to detect

- IBM 2025: global average data breach cost **$4.44 million**
- Misconfiguration-driven breaches: **~186 days** to identify, **~65 days** to contain

*Sources: IBM Cost of a Data Breach Report 2025, Fidelis Security, Sprinto*

### Cloud waste is rising

- Flexera 2026 State of the Cloud: **29%** of IaaS/PaaS spend wasted (first increase in 5 years)
- Top drivers: **idle compute (~35%)**, **over-provisioned instances (~25%)**

*Sources: Flexera 2026, TechInformed, SpendArk*

### Industry fix: shift left on IaC

A 2026 IaC security program should include:
- Pre-merge scanning of Terraform / ARM / Bicep
- Policy-as-code in CI/CD
- Secret detection in IaC files
- Post-deploy drift detection

*Source: Waldo Security — IaC security best practices*

## Demo PR narrative

> *"Jake, a CloudNova platform engineer, opens PR #847: 'Add dev environment for saas-api.' It's Friday 4pm. The senior reviewer is on vacation. The PR includes storage, a VM, networking, and App Service. AI + Checkov review it in 90 seconds. The open SSH rule, public storage, and D8s_v3 VM are flagged before anyone merges."*

That narrative drives Acts 2–5 in `DEMO_SCRIPT.md`.
