# Your Setup — sopn0001/cloudnova-iac-demo

**Repo:** https://github.com/sopn0001/cloudnova-iac-demo  
**Azure subscription:** MOC DS - 10269  
**Status:** App Registration created — finish steps below

---

## Already done

| Item | Value |
|------|-------|
| GitHub repo | [sopn0001/cloudnova-iac-demo](https://github.com/sopn0001/cloudnova-iac-demo) |
| Local git commit | Created on branch `main` |
| App Registration | `github-cloudnova-iac` |
| **AZURE_CLIENT_ID** | `95549284-68b6-4a40-afb6-4db00f3887f7` |
| **AZURE_TENANT_ID** | `0f69441c-29e3-4293-9c7a-c6b8ec38e66e` |
| **AZURE_SUBSCRIPTION_ID** | `1539b06f-7167-4e7d-a533-c342e2c6cdb4` |
| App object ID (for federated creds) | `79656c79-719c-4e8c-8908-0b5c7d2ed00a` |

---

## Step 1 — Push code to GitHub (do this first)

In Terminal:

```bash
cd "/Users/idrissop/Documents/Algonquin College/Cloud Development and Operations/Applied Projects/AI Project and Presentation"

git branch -M main
git remote add origin https://github.com/sopn0001/cloudnova-iac-demo.git
git push -u origin main
```

If prompted, sign in to GitHub (browser or personal access token).

**Verify:** Refresh https://github.com/sopn0001/cloudnova-iac-demo — you should see all project files.

---

## Step 2 — Finish Azure OIDC (run in Terminal)

```bash
APP_ID="95549284-68b6-4a40-afb6-4db00f3887f7"
OBJECT_ID="79656c79-719c-4e8c-8908-0b5c7d2ed00a"
SUB_ID="1539b06f-7167-4e7d-a533-c342e2c6cdb4"

# Create service principal
az ad sp create --id "$APP_ID"

# Federated credential — push to main branch
az ad app federated-credential create --id "$OBJECT_ID" --parameters '{
  "name": "github-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:sopn0001/cloudnova-iac-demo:ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}'

# Federated credential — deploy job uses environment: dev
az ad app federated-credential create --id "$OBJECT_ID" --parameters '{
  "name": "github-environment-dev",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:sopn0001/cloudnova-iac-demo:environment:dev",
  "audiences": ["api://AzureADTokenExchange"]
}'

# Grant Contributor at subscription scope (required for Terraform to create the resource group)
az role assignment create \
  --assignee "$APP_ID" \
  --role Contributor \
  --scope "/subscriptions/$SUB_ID"
```

---

## Step 3 — Add GitHub secrets

Go to: https://github.com/sopn0001/cloudnova-iac-demo/settings/secrets/actions

Click **New repository secret** for each:

| Secret name | Value |
|-------------|-------|
| `AZURE_CLIENT_ID` | `95549284-68b6-4a40-afb6-4db00f3887f7` |
| `AZURE_TENANT_ID` | `0f69441c-29e3-4293-9c7a-c6b8ec38e66e` |
| `AZURE_SUBSCRIPTION_ID` | `1539b06f-7167-4e7d-a533-c342e2c6cdb4` |
| `SSH_PUBLIC_KEY` | Run below, paste full output |

Get SSH public key:

```bash
cat ~/.ssh/id_rsa.pub
```

Copy the **entire line** starting with `ssh-rsa ...`

---

## Step 4 — Create GitHub environment (required for deploy)

Go to: https://github.com/sopn0001/cloudnova-iac-demo/settings/environments

1. Click **New environment**
2. Name: `dev`
3. Click **Configure environment**
4. (Optional) Add yourself as required reviewer for demo control
5. Save

---

## Step 5 — Test the PR review flow (live demo)

```bash
cd "/Users/idrissop/Documents/Algonquin College/Cloud Development and Operations/Applied Projects/AI Project and Presentation"

git checkout main
git pull
git checkout -b demo/flawed-infrastructure

# Trigger PR workflow
echo "" >> infra/terraform/flawed/main.tf
git add infra/terraform/flawed/main.tf
git commit -m "feat: CloudNova dev environment PR for review"
git push -u origin demo/flawed-infrastructure
```

On GitHub:
1. Open **Pull request** → base: `main` ← compare: `demo/flawed-infrastructure`
2. Watch **Actions** tab (~2 min)
3. On the PR, find the comment: **CloudNova — AI-Assisted IaC Review** with 🚫 **BLOCKED**

---

## Step 6 — Merge and deploy to Azure

After showing the BLOCKED review in your presentation:

1. Open `infra/terraform/fixed/main.tf` side-by-side — explain fixes
2. **Merge** the PR (or merge a clean PR to `main`)
3. Watch **Actions** → `Deploy to Azure (fixed Terraform)` job
4. Verify in Azure Portal → `rg-cloudnova-dev`

---

## Step 7 — Optional: PR with READY status

For a green ✅ review comment:

```bash
git checkout main
git pull
git checkout -b demo/apply-fixes
git commit --allow-empty -m "fix: apply CloudNova review remediations"
git push -u origin demo/apply-fixes
```

Open PR → comment shows **✅ READY** → merge to deploy.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `git push` asks for password | Use GitHub personal access token as password, or sign in via GitHub Desktop |
| Azure login fails | Run `az login` |
| Deploy job: OIDC error | Re-run Step 2 federated credentials — both `main` and `environment:dev` are required |
| Deploy job: SSH key error | Ensure `SSH_PUBLIC_KEY` secret is the full `ssh-rsa AAAA...` line |
| No PR comment | Check repo Settings → Actions → General → Workflow permissions = **Read and write** |
| `ai-review` red X on flawed PR | **Expected** — critical issues block merge by design |

---

## Quick checklist

```
[x] Step 1: git push to GitHub
[x] Step 2: Azure OIDC + resource group commands
[x] Step 3: Four GitHub secrets added
[x] Step 4: GitHub environment "dev" created
[ ] Step 5: Open demo PR — see BLOCKED comment
[ ] Step 6: Merge to main — Azure deploy succeeds
```

---

## Presentation day

```bash
./scripts/preflight_demo.sh
```

Then follow `docs/LIVE_DEMO.md`.
