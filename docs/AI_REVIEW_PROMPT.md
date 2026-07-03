# CloudNova — AI Review Prompts

Copy into Cursor during the live demo.

## Full review (recommended for presentation)

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

## Security-focused prompt

```
Audit infra/terraform/flawed/ for CloudNova's top security risks:
- NSG rules exposing management ports to the internet
- Storage accounts with public access
- Credentials in variables, VM config, or connection strings
- TLS and HTTPS enforcement gaps

Map each finding to a Checkov rule ID if applicable.
Prioritize by exploitability.
```

## Cost / FinOps prompt

```
Analyze infra/terraform/flawed/ for CloudNova cost waste in a dev environment.
Identify over-provisioned VMs, unused disks, and premium SKUs that should be standard.
Compare against policies/naming-standards.json costTiers.
Estimate monthly CAD savings for each fix.
```

## Compare flawed vs fixed

```
Compare infra/terraform/flawed/ and infra/terraform/fixed/.
Produce a diff-style summary: what changed, why it matters, and how it addresses
CloudNova's security incident and cost waste problems.
```

## Pipeline integration prompt

```
Explain how .github/workflows/iac-review-deploy.yml implements shift-left security
for CloudNova. Which jobs block a flawed PR? What runs only after merge to main?
```
