# CloudNova — Live Demo Runbook

**Use this document during your presentation.** Keep it open on a second monitor or printed.

---

## 30 minutes before — run pre-flight

```bash
cd "/Users/idrissop/Documents/Algonquin College/Cloud Development and Operations/Applied Projects/AI Project and Presentation"
chmod +x scripts/preflight_demo.sh
./scripts/preflight_demo.sh
```

This validates Terraform, generates `ai-review-summary.md`, and saves backups to `demo-backup/`.

---

## Window layout (set up before you start)

| Window / tab | What to show |
|--------------|--------------|
| **Slides** | PowerPoint / Google Slides (Acts 1 & 6) |
| **Cursor — Tab 1** | `infra/terraform/flawed/main.tf` |
| **Cursor — Tab 2** | `infra/terraform/fixed/main.tf` |
| **Cursor — Tab 3** | `ai-review-summary.md` (backup — do not show unless needed) |
| **Cursor — Chat** | Empty, ready for AI prompt |
| **Terminal** | Project root (optional Checkov live run) |
| **Browser** | GitHub PR + Actions tab (screenshot backup if no WiFi) |

**Tip:** Increase editor font size (View → Appearance → Font Size) so the audience can read the code.

---

## Minute-by-minute script (12–15 min)

### 0:00–4:00 — Act 1: Business problem (slides only)

**Say:**  
*"CloudNova — 4 DevOps engineers, 20+ Terraform deploys a week, one senior reviewer, PRs stuck for days."*

**Say:**  
*"Last quarter: public storage for 3 weeks. Oversized VMs. Forgotten disks."*

**Show slides 2–5** from `docs/PRESENTATION_SLIDES.md`:
- 23% of incidents = misconfigurations
- $4.44M average breach cost
- 29% cloud spend wasted

**Transition:**  
*"Let me show you the exact PR that would cause these problems."*

---

### 4:00–5:00 — Act 2: Show the flawed code (live — no typing)

**Switch to Cursor** → `infra/terraform/flawed/main.tf`

Scroll slowly and **point at these three blocks** (do not explain everything):

**1. Public storage (~line 14)**
```hcl
allow_nested_items_to_be_public = true
```
*"This is what burned CloudNova for three weeks."*

**2. Open SSH port (~lines 45–56)**
```hcl
source_address_prefix      = "*"
destination_port_range     = "22"
```
*"SSH open to the entire internet."*

**3. Oversized VM + orphan disk (~lines 86 and 114)**
```hcl
size = "Standard_D8s_v3"
```
```hcl
resource "azurerm_managed_disk" "orphan_backup" {
  disk_size_gb = 512
```
*"Production-sized VM in dev, plus a disk nothing is attached to."*

**Say:**  
*"A senior engineer might catch one of these. A rushed Friday PR? All three slip through."*

---

### 5:00–10:00 — Act 3: LIVE AI review (main demo moment)

**Switch to Cursor Chat.** Copy-paste this prompt **exactly** (also in `docs/AI_REVIEW_PROMPT.md`):

```
You are a senior DevOps engineer at CloudNova, a mid-size SaaS company.
The team deploys Terraform 20+ times per week. A rushed PR must be reviewed before merge.

Review infra/terraform/flawed/ for:
1. Security risks — open ports, public storage, secrets, TLS/HTTPS
2. Cost waste — oversized VM, orphan disks, premium SKUs in dev
3. Naming and governance per policies/naming-standards.json

For each finding provide:
- Severity (CRITICAL / HIGH / MEDIUM / LOW)
- Category (Security / Cost / Governance / Naming)
- Exact file and resource
- Risk in plain language (reference CloudNova's past public-storage incident)
- Concrete Terraform fix

End with estimated monthly cost savings if fixed for dev.
```

**While AI responds, say:**  
*"In seconds we get what used to take the senior engineer an hour — security, cost, and governance in one pass."*

**When results appear, highlight only these 4:**
1. CRITICAL — SSH open to internet
2. CRITICAL — public storage
3. HIGH — Standard_D8s_v3 oversized for dev
4. HIGH — orphan 512 GB disk

**Say:**  
*"AI explains the why, not just the what. It references CloudNova's naming standard and estimates cost impact."*

#### FALLBACK if AI is slow or WiFi fails

> *"Let me show you the output we generated in our pipeline earlier."*

Open `ai-review-summary.md` or `docs/AI_REVIEW_FINDINGS.md` — same content, same story.

---

### 10:00–12:00 — Act 4: Policy-as-code + CI/CD (live terminal OR screenshot)

**Say:**  
*"AI is the fast first pass. The pipeline enforces rules on every PR — no exceptions."*

**Option A — Live terminal (30 seconds):**

```bash
checkov -d infra/terraform/flawed --framework terraform --compact | head -30
```

Point at FAILED checks for storage and network.

**Option B — No terminal:** Show `.github/workflows/iac-review-deploy.yml` and walk through jobs:

| Job | What it does |
|-----|--------------|
| `validate-terraform` | Syntax check |
| `security-scan` | Checkov policy-as-code |
| `ai-review` | Posts summary on PR |
| `deploy-dev` | Only runs after merge to main |

**Option C — Screenshot:** Show a green GitHub Actions run + PR comment (prepare night before).

**Say:**  
*"Shift-left — catch it in code, before Azure."*

---

### 12:00–14:00 — Act 5: Show the fix (split screen)

**Open split view:** flawed `main.tf` left | fixed `main.tf` right

Walk through **3 quick diffs only:**

| Flawed | Fixed |
|--------|-------|
| `allow_nested_items_to_be_public = true` | `= false` |
| SSH `access = "Allow"` from `*` | `access = "Deny"` from Internet |
| `size = "Standard_D8s_v3"` | `size = "Standard_B2s"` |
| `orphan_backup` disk exists | disk removed |

**Say:**  
*"Same workload. Roughly $400+ a month saved in dev. No public exposure."*

**Optional live plan (only if Azure is set up and you rehearsed):**

```bash
cd infra/terraform/fixed
terraform plan -var="app_name=saasapi" -var="environment=dev" \
  -var="resource_group_name=rg-cloudnova-dev" \
  -var="key_vault_id=..." -var="ssh_public_key=..."
```

Otherwise show a `terraform plan` screenshot — perfectly acceptable.

---

### 14:00–15:00 — Act 6: Close

**Say:**  
*"AI doesn't replace DevOps — it removes the bottleneck. Policy-as-code and CI/CD are the guardrails. CloudNova catches the open port, the public storage, and the oversized VM before merge — not three weeks later."*

**Skills named:** Terraform · AI-assisted review · Checkov · GitHub Actions · Azure governance

---

## Emergency fallback matrix

| Problem | What to do |
|---------|------------|
| WiFi down | Use `ai-review-summary.md` + screenshots in `demo-backup/` |
| Cursor AI slow | Say *"while it thinks..."* → show pre-generated summary → return to AI result if it finishes |
| `checkov` not installed | Show `demo-backup/checkov-flawed.txt` or workflow YAML only |
| Azure / terraform plan fails | Skip deploy; say *"pipeline runs plan on merge"* — show GitHub screenshot |
| Projector can't show code | Zoom editor to 150%; use high-contrast theme |

---

## Night-before checklist

```
[ ] ./scripts/preflight_demo.sh passes
[ ] Slides built from docs/PRESENTATION_SLIDES.md
[ ] GitHub repo pushed; PR open with green Actions run (screenshot saved)
[ ] ai-review-summary.md regenerated
[ ] Cursor logged in and AI working
[ ] flawed/main.tf + fixed/main.tf tabs open
[ ] Rehearse once out loud (time it — aim for 12 min)
[ ] Laptop charged; HDMI adapter tested in classroom if possible
```

---

## What NOT to do live

- Do **not** run `terraform apply` on the flawed template
- Do **not** improvise a new prompt — use the one above
- Do **not** read every line of AI output — highlight 4 findings only
- Do **not** panic if one step fails — fallbacks are pre-built

---

## One-line elevator pitch (if short on time)

*"CloudNova's DevOps team uses AI plus Checkov in GitHub Actions to catch open SSH ports, public storage, and oversized VMs in Terraform before merge — turning a 3-day manual review bottleneck into a 90-second automated guardrail."*
