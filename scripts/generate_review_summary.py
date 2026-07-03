#!/usr/bin/env python3
"""Generate PR comment summarizing CloudNova IaC review findings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FINDINGS = [
    {
        "id": "ssh-open",
        "severity": "CRITICAL",
        "category": "Security",
        "issue": "SSH port 22 open to the internet (0.0.0.0/0)",
        "recommendation": "Deny inbound SSH from Internet; use Azure Bastion or VPN for admin access.",
        "patterns": ['source_address_prefix      = "*"'],
    },
    {
        "id": "public-storage",
        "severity": "CRITICAL",
        "category": "Security",
        "issue": "Storage account publicly accessible (blob access enabled)",
        "recommendation": "Set `allow_nested_items_to_be_public = false`; restrict network ACLs.",
        "patterns": ["allow_nested_items_to_be_public = true"],
    },
    {
        "id": "hardcoded-secrets",
        "severity": "CRITICAL",
        "category": "Security",
        "issue": "Hardcoded credentials in Terraform variables and connection strings",
        "recommendation": "Use Key Vault references; never commit password defaults.",
        "patterns": ['variable "sql_admin_password"', "connection_string"],
    },
    {
        "id": "weak-tls",
        "severity": "HIGH",
        "category": "Security",
        "issue": "HTTPS/TLS not enforced on storage and web app",
        "recommendation": "Enable HTTPS-only and TLS 1.2 minimum on all endpoints.",
        "patterns": [
            "enable_https_traffic_only       = false",
            "enable_https_traffic_only = false",
            "https_only          = false",
            "TLS1_0",
            'minimum_tls_version = "1.0"',
        ],
    },
    {
        "id": "oversized-vm",
        "severity": "HIGH",
        "category": "Cost",
        "issue": "Oversized VM (Standard_D8s_v3) for dev API worker",
        "recommendation": "Right-size to `Standard_B2s` in dev (~90% cost reduction).",
        "patterns": ["Standard_D8s_v3"],
    },
    {
        "id": "orphan-disk",
        "severity": "HIGH",
        "category": "Cost",
        "issue": "Orphaned 512 GB Premium managed disk (not attached to any VM)",
        "recommendation": "Delete unused disks or attach with a documented lifecycle policy.",
        "patterns": ["orphan_backup", "disk-old-backup"],
    },
    {
        "id": "premium-dev-skus",
        "severity": "MEDIUM",
        "category": "Cost",
        "issue": "Premium storage and/or P1v3 App Service in dev environment",
        "recommendation": "Use Standard_LRS and B1 SKU per CloudNova cost tiers.",
        "patterns": ['account_tier             = "Premium"', 'sku_name            = "P1v3"'],
    },
    {
        "id": "missing-tags",
        "severity": "MEDIUM",
        "category": "Governance",
        "issue": "Missing required CloudNova governance tags",
        "recommendation": "Apply Environment, Application, Company, ManagedBy, CostCenter, Owner.",
        "patterns": ["tags                = local.tags", "tags                     = local.tags"],
        "invert": True,
    },
    {
        "id": "bad-naming",
        "severity": "MEDIUM",
        "category": "Naming",
        "issue": "Non-standard resource naming (missing cn- prefix)",
        "recommendation": "Follow `cn-{appName}-{resourceType}` convention.",
        "patterns": ['naming_prefix         = "cn-'],
        "invert": True,
    },
    {
        "id": "ftps",
        "severity": "LOW",
        "category": "Security",
        "issue": "FTPS allowed on App Service",
        "recommendation": 'Set `ftps_state = "Disabled"`.',
        "patterns": ['ftps_state          = "AllAllowed"'],
    },
]


def load_standards(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def finding_matches(text: str, finding: dict) -> bool:
    invert = finding.get("invert", False)
    if finding["id"] == "hardcoded-secrets":
        has_secret = ('variable "sql_admin_password"' in text and "P@ss" in text) or (
            "connection_string" in text.lower() and "password" in text.lower()
        )
        return not has_secret if invert else has_secret
    if finding["id"] == "missing-tags":
        has_tags = "tags                = local.tags" in text or "tags                     = local.tags" in text
        return not has_tags
    if finding["id"] == "bad-naming":
        return 'naming_prefix         = "cn-' not in text and "local.naming_prefix" not in text
    matched = any(pattern in text for pattern in finding["patterns"])
    return not matched if invert else matched


def analyze_template(template_path: Path) -> list[dict]:
    text = template_path.read_text()
    return [finding for finding in FINDINGS if finding_matches(text, finding)]


def scan_template(template_path: Path) -> list[str]:
    text = template_path.read_text()
    hits: list[str] = []
    patterns = {
        'source_address_prefix      = "*"': "SSH open to internet (NSG)",
        "allow_nested_items_to_be_public = true": "Public blob access enabled",
        "enable_https_traffic_only       = false": "Storage HTTPS-only disabled",
        "enable_https_traffic_only = false": "Storage HTTPS-only disabled",
        "https_only          = false": "Web App HTTPS-only disabled",
        "TLS1_0": "Weak TLS version",
        'account_tier             = "Premium"': "Premium storage SKU",
        "Standard_D8s_v3": "Oversized VM SKU for dev",
        'default_action = "Allow"': "Permissive storage firewall",
        'ftps_state          = "AllAllowed"': "FTPS not restricted",
        "disable_password_authentication = false": "VM password authentication enabled",
    }
    for pattern, label in patterns.items():
        if pattern in text:
            hits.append(label)
    if (
        'destination_port_range     = "22"' in text
        and 'access                     = "Allow"' in text
        and 'source_address_prefix      = "*"' in text
    ):
        hits.append("SSH port exposed to internet")
    if 'variable "sql_admin_password"' in text and "P@ss" in text:
        hits.append("Hardcoded credential default")
    if "connection_string" in text.lower() and "password" in text.lower():
        hits.append("Plaintext password in connection string")
    if "orphan_backup" in text or "disk-old-backup" in text:
        hits.append("Orphaned managed disk (cost leak)")
    has_tags = "tags                = local.tags" in text or "tags                     = local.tags" in text
    if not has_tags:
        hits.append("No resource tags defined")
    return hits


def verdict(active: list[dict]) -> tuple[str, str]:
    critical = sum(1 for f in active if f["severity"] == "CRITICAL")
    high = sum(1 for f in active if f["severity"] == "HIGH")
    if critical:
        return "BLOCKED", f"**{critical} critical** and **{high} high** severity issue(s) must be fixed before merge."
    if high:
        return "WARNING", f"No critical issues, but **{high} high** severity issue(s) should be addressed."
    if active:
        return "ADVISORY", f"**{len(active)}** lower-severity issue(s) detected. Safe to merge with review."
    return "READY", "No known CloudNova anti-patterns detected. Ready for merge and deployment."


def render_markdown(
    template_path: Path,
    standards: dict,
    detected: list[str],
    active_findings: list[dict],
    checkov_summary: str | None = None,
) -> str:
    convention = standards.get("namingConvention", {}).get("pattern", "cn-{appName}-{resourceType}")
    status, status_detail = verdict(active_findings)
    status_emoji = {"BLOCKED": "🚫", "WARNING": "⚠️", "ADVISORY": "ℹ️", "READY": "✅"}[status]

    lines = [
        "## CloudNova — AI-Assisted IaC Review",
        "",
        f"{status_emoji} **Status: {status}** — {status_detail}",
        "",
        f"**Template reviewed:** `{template_path}`",
        "",
    ]

    if active_findings:
        lines.extend(
            [
                "### Detected issues",
                "",
                "| Severity | Category | Issue | Recommendation |",
                "|----------|----------|-------|----------------|",
            ]
        )
        for finding in active_findings:
            lines.append(
                f"| {finding['severity']} | {finding['category']} | {finding['issue']} | {finding['recommendation']} |"
            )
    else:
        lines.append("### Detected issues")
        lines.append("")
        lines.append("No CloudNova anti-patterns detected in this template.")

    lines.extend(["", "### Pattern matches in template", ""])
    if detected:
        lines.extend(f"- {item}" for item in detected)
    else:
        lines.append("- No pattern matches.")

    if checkov_summary:
        lines.extend(["", "### Checkov policy scan (excerpt)", "", "```", checkov_summary.strip(), "```"])

    fix_path = "`infra/terraform/fixed/`" if "flawed" in str(template_path) else "`infra/terraform/fixed/`"
    lines.extend(
        [
            "",
            "### CloudNova naming standard",
            "",
            f"Expected pattern: `{convention}`",
            "",
            "### Next steps",
            "",
        ]
    )
    if status == "BLOCKED":
        lines.extend(
            [
                f"1. Apply remediations — see {fix_path} for reference fixes",
                "2. Push commits to this PR — checks and this comment will update automatically",
                "3. Merge only after status is **READY** or **ADVISORY**",
                "4. Merge to `main` triggers Azure deployment via GitHub Actions",
            ]
        )
    else:
        lines.extend(
            [
                "1. Merge this PR to `main`",
                "2. GitHub Actions will run `terraform plan` and `terraform apply` to Azure",
                "3. Resources deploy from `infra/terraform/fixed/`",
            ]
        )

    lines.extend(["", "_Generated by `scripts/generate_review_summary.py` in the CloudNova CI pipeline._"])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--standards", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--checkov-file", type=Path, default=None)
    parser.add_argument("--fail-on-critical", action="store_true")
    args = parser.parse_args()

    if not args.template.exists():
        print(f"Template not found: {args.template}", file=sys.stderr)
        sys.exit(1)

    standards = load_standards(args.standards)
    detected = scan_template(args.template)
    active_findings = analyze_template(args.template)
    checkov_summary = args.checkov_file.read_text() if args.checkov_file and args.checkov_file.exists() else None

    markdown = render_markdown(args.template, standards, detected, active_findings, checkov_summary)

    if args.output:
        args.output.write_text(markdown)
    else:
        print(markdown)

    critical_count = sum(1 for f in active_findings if f["severity"] == "CRITICAL")
    if args.fail_on_critical and critical_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
