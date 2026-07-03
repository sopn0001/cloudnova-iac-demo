# CloudNova — Presentation Slide Outline

Use this for PowerPoint / Google Slides. Cite sources on each evidence slide.

---

## Slide 1 — Title

**Catching Misconfigurations Before They Ship**  
AI-Assisted Terraform Review for CloudNova  
*CDEV2400 Applied Project*

---

## Slide 2 — Meet CloudNova

**CloudNova** — mid-size B2B SaaS company

- 4-person DevOps team
- All infrastructure as **Terraform**
- **20+ deployments per week**
- 1 senior engineer reviews every PR → **bottleneck**

**The pain:**
- PR reviews sit for **days**
- Last quarter: **public storage account** exposed for **3 weeks**
- Discovery: **oversized VMs** + **forgotten disks** on the bill

---

## Slide 3 — Security: Misconfigurations dominate

| Stat | Figure |
|------|--------|
| Cloud incidents from misconfigurations | **~23%** |
| Misconfigurations caused by human error | **~82%** |
| Cloud security failures that are preventable customer misconfig | **Majority** (Gartner 2025–2026) |

**Sources:**
- Exabeam — cloud misconfiguration research
- Gartner — cloud security failure predictions
- Blue Team / industry compliance surveys

**Talking point:** Not software bugs — **preventable config mistakes in IaC**.

---

## Slide 4 — Security: Breaches are slow and expensive

| Stat | Figure |
|------|--------|
| Global average breach cost (2025) | **$4.44 million** |
| Time to identify misconfiguration breach | **~186 days** |
| Time to contain | **~65 additional days** |

**Sources:**
- IBM Cost of a Data Breach Report 2025
- Fidelis Security / Sprinto breach timeline analysis

**Talking point:** CloudNova's 3-week exposure is lucky — average is **6 months**.

---

## Slide 5 — Cost: The cloud bill leak

| Stat | Figure |
|------|--------|
| IaaS/PaaS spend wasted (2026) | **29%** (first increase in 5 years) |
| Top waste: idle compute | **~35%** |
| Top waste: over-provisioned instances | **~25%** |

**Sources:**
- Flexera 2026 State of the Cloud Report
- TechInformed / SpendArk FinOps analysis

**Talking point:** CloudNova's D8s_v3 dev VM and orphan disk are textbook waste.

---

## Slide 6 — The fix: Shift left on IaC

**Industry recommendation (2026 IaC security program):**

1. Pre-merge scanning of Terraform
2. Policy-as-code in CI/CD
3. Secret detection in IaC files
4. Drift detection post-deploy

**Source:** Waldo Security — IaC security best practices

**Our solution:** AI review + Checkov + GitHub Actions **before merge**

---

## Slide 7 — Demo architecture

```
Developer PR → AI Review (Cursor) → Checkov Scan → terraform validate
                    ↓                      ↓
              PR comment              Block/warn on policy
                    ↓
              Merge to main → terraform plan → terraform apply → Azure
```

---

## Slide 8 — What we catch (demo findings)

| # | Finding | Severity |
|---|---------|----------|
| 1 | SSH port 22 open to internet | CRITICAL |
| 2 | Public storage account | CRITICAL |
| 3 | Hardcoded credentials | CRITICAL |
| 4 | Oversized VM (D8s_v3 in dev) | HIGH |
| 5 | Orphan 512 GB Premium disk | HIGH |
| 6 | Missing governance tags | MEDIUM |

---

## Slide 9 — Results for CloudNova

**Before:** 3-day PR reviews, incidents found weeks later, 29% waste category  
**After:** Instant AI first pass, automated policy gates, deploy only remediated code

**Tools:** Terraform · Cursor AI · Checkov · GitHub Actions · Azure

---

## Slide 10 — Q&A

- AI assists — humans approve
- Policy-as-code enforces — no exceptions
- Shift left — catch in code, not in production

---

## Alternative titles (if your group prefers)

| Angle | Title |
|-------|-------|
| Security (recommended) | Catching Misconfigurations Before They Ship |
| Velocity | From Bottleneck to Guardrail: Cutting Manual Terraform Review Time with AI |
| FinOps | Stopping the Cloud-Bill Leak at the Code Stage |
