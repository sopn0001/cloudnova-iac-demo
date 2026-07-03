# CloudNova — AI Review Findings

**Company:** CloudNova (mid-size SaaS)  
**Template reviewed:** `infra/terraform/flawed/`  
**Reviewer:** AI assistant (Cursor) + Checkov policy-as-code  
**Scenario:** Rushed dev-environment PR before merge

---

## Executive Summary

CloudNova's flawed Terraform deploys a storage account, API worker VM, App Service, and networking. It contains **10 issues** spanning security, cost, and governance — exactly the problems that caused their real incidents last quarter.

**Do not deploy `infra/terraform/flawed/`.** Use `infra/terraform/fixed/` after review.

---

## Findings

### 1. CRITICAL — SSH open to the internet

| Field | Value |
|-------|-------|
| **Location** | `azurerm_network_security_group.main` — rule `SSH-From-Internet` |
| **Risk** | Port 22 accessible from `0.0.0.0/0`; brute-force and lateral movement |
| **Fix** | Deny inbound SSH from Internet; use Bastion or private access |

### 2. CRITICAL — Public storage account

| Field | Value |
|-------|-------|
| **Location** | `azurerm_storage_account.main` — `allow_nested_items_to_be_public = true` |
| **Risk** | Same class of incident CloudNova had for 3 weeks |
| **Fix** | Set to `false`; `default_action = "Deny"` on network rules |

### 3. CRITICAL — Hardcoded credentials

| Field | Value |
|-------|-------|
| **Location** | `variable "sql_admin_password"` default; VM `admin_password`; App Service connection string |
| **Risk** | Secrets in Git history and Terraform state |
| **Fix** | Key Vault references; SSH keys for VM; no password defaults |

### 4. HIGH — Oversized VM for dev

| Field | Value |
|-------|-------|
| **Location** | `azurerm_linux_virtual_machine.main` — `size = "Standard_D8s_v3"` |
| **Cost impact** | ~$280+/mo CAD vs ~$30 for `Standard_B2s` |
| **Fix** | Right-size per `policies/naming-standards.json` cost tiers |

### 5. HIGH — Orphaned managed disk

| Field | Value |
|-------|-------|
| **Location** | `azurerm_managed_disk.orphan_backup` — 512 GB Premium, unattached |
| **Cost impact** | ~$40+/mo idle with no workload |
| **Fix** | Delete or attach with documented lifecycle |

### 6. HIGH — HTTPS/TLS not enforced

| Field | Value |
|-------|-------|
| **Location** | Storage + Web App |
| **Fix** | HTTPS-only, TLS 1.2 minimum |

### 7. MEDIUM — Premium SKUs in dev

| Resource | Current | Recommended (dev) |
|----------|---------|-------------------|
| Storage | Premium_LRS | Standard_LRS |
| App Service | P1v3 | B1 |
| VM OS disk | Premium 256 GB | Standard 64 GB |

### 8. MEDIUM — Missing governance tags

Required per CloudNova standard: `Environment`, `Application`, `Company`, `ManagedBy`, `CostCenter`, `Owner`

### 9. MEDIUM — Non-standard naming

| Current | Expected |
|---------|----------|
| `vnet-saasapi` | `cn-saasapi-dev-vnet` |
| `vm-saasapi` | `cn-saasapi-dev-vm` |
| `storage*` | `cnsaasapidevst*` |

### 10. LOW — FTPS allowed on App Service

Set `ftps_state = "Disabled"`.

---

## Remediation summary

| Finding | Fixed in `infra/terraform/fixed/` |
|---------|-------------------------------------|
| Open SSH | NSG denies SSH from Internet |
| Public storage | Blob access disabled, network deny |
| Credentials | Key Vault + SSH keys |
| Oversized VM | `Standard_B2s` in dev |
| Orphan disk | Removed |
| Premium dev SKUs | Standard_LRS, B1 |
| Tags / naming | `cn-*` prefix + governance tags |

---

## AI vs traditional tooling

| Capability | Checkov | AI-assisted review |
|------------|---------|-------------------|
| Known misconfigurations | Yes | Yes |
| Cost reasoning ("D8s_v3 is overkill for dev") | No | Yes |
| Business context (CloudNova incident) | No | Yes |
| Remediation code generation | No | Yes |
| Plain-language explanation for PR author | No | Yes |

---

## Estimated monthly savings (dev environment)

| Item | Flawed | Fixed | Savings |
|------|--------|-------|---------|
| VM (D8s_v3 → B2s) | ~$280 | ~$30 | ~$250 |
| Orphan disk | ~$40 | $0 | ~$40 |
| Premium storage | ~$25 | ~$5 | ~$20 |
| P1v3 App Service | ~$150 | ~$15 | ~$135 |
| **Total (approx.)** | | | **~$445/mo** |

*Estimates vary by region; use Azure Pricing Calculator for presentation.*
