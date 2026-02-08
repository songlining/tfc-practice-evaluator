#!/usr/bin/env python3
"""
TFC/TFE Data Collection Script
Collects comprehensive organization data from Terraform Cloud or Terraform Enterprise API.

Usage:
    export TFC_TOKEN="your-token"
    export TFC_ORG="your-org"
    export TFC_API_BASE="https://app.terraform.io/api/v2"  # or TFE URL
    export OUTPUT_DIR="./assessment"
    python3 collect_tfc_data.py
"""

import urllib.request
import json
import os
import re
from datetime import datetime
import sys

# Configuration from environment variables
TFC_TOKEN = os.getenv("TFC_TOKEN")
TFC_ORG = os.getenv("TFC_ORG")
TFC_API_BASE = os.getenv("TFC_API_BASE", "https://app.terraform.io/api/v2")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./assessment")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "data.json")


def validate_config():
    """Validate required environment variables"""
    if not TFC_TOKEN:
        print("ERROR: TFC_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    if not TFC_ORG:
        print("ERROR: TFC_ORG environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_all_pages(endpoint):
    """Fetch all pages from a paginated endpoint"""
    results = []
    url = f"{TFC_API_BASE}{endpoint}"

    while url:
        print(f"Fetching: {url}", file=sys.stderr)
        try:
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Bearer {TFC_TOKEN}")
            req.add_header("Content-Type", "application/vnd.api+json")

            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())

            if "errors" in data:
                print(f"Error: {data['errors'][0]['detail']}", file=sys.stderr)
                break

            results.extend(data.get("data", []))

            # Check for next page
            url = data.get("links", {}).get("next")

        except Exception as e:
            print(f"Error fetching {url}: {e}", file=sys.stderr)
            break

    return results


def fetch_single(endpoint):
    """Fetch a single endpoint"""
    url = f"{TFC_API_BASE}{endpoint}"
    print(f"Fetching: {url}", file=sys.stderr)

    try:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {TFC_TOKEN}")
        req.add_header("Content-Type", "application/vnd.api+json")

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        if "errors" in data:
            print(f"Error: {data['errors'][0]['detail']}", file=sys.stderr)
            return []

        return data.get("data", [])

    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# State secrets scanning — on-the-fly, never written to disk
# ---------------------------------------------------------------------------

# Patterns that strongly indicate a leaked secret in state attributes.
# Each tuple: (pattern_name, compiled_regex, description)
SECRET_PATTERNS = [
    (
        "AWS Access Key",
        re.compile(r"(?<![A-Za-z0-9/+=])AKIA[0-9A-Z]{16}(?![A-Za-z0-9/+=])"),
        "AWS IAM access key ID",
    ),
    (
        "AWS Secret Key",
        re.compile(r"(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])"),
        "Potential AWS secret access key (40-char base64)",
    ),
    (
        "Private Key Block",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
        "PEM-encoded private key",
    ),
    (
        "Generic API Key Assignment",
        re.compile(
            r'(?i)(?:api[_-]?key|api[_-]?secret|api[_-]?token)\s*[:=]\s*["\']?[A-Za-z0-9/+=_\-]{16,}'
        ),
        "API key/secret/token assignment",
    ),
    (
        "Generic Password Assignment",
        re.compile(r'(?i)(?:password|passwd|pwd|secret)\s*[:=]\s*["\']?[^\s"\']{8,}'),
        "Password or secret assignment",
    ),
    (
        "GitHub Token",
        re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}"),
        "GitHub personal access token",
    ),
    (
        "Slack Token",
        re.compile(r"xox[bpas]-[0-9]{10,}-[A-Za-z0-9]+"),
        "Slack API token",
    ),
    (
        "Generic Bearer Token",
        re.compile(r"(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*"),
        "Bearer token in attribute value",
    ),
    (
        "Connection String with Credentials",
        re.compile(
            r"(?i)(?:mysql|postgres|postgresql|mongodb|redis|amqp|mssql)://[^:]+:[^@]+@"
        ),
        "Database/service connection string with embedded credentials",
    ),
]

# Keys in resource attributes that commonly hold sensitive values.
SENSITIVE_ATTRIBUTE_NAMES = {
    "password",
    "secret",
    "api_key",
    "api_secret",
    "api_token",
    "access_key",
    "secret_key",
    "private_key",
    "token",
    "auth_token",
    "master_password",
    "admin_password",
    "db_password",
    "connection_string",
    "client_secret",
    "signing_key",
    "encryption_key",
    "ssh_key",
    "tls_private_key",
    "secret_key_base",
}


def _scan_value_for_secrets(value, path, findings):
    """Recursively scan a JSON value for secret patterns. Never stores the value."""
    if isinstance(value, str):
        for pattern_name, regex, description in SECRET_PATTERNS:
            # Skip the generic 40-char pattern for very short or very long strings
            # to reduce false positives — only check it when the attribute name
            # also looks sensitive (handled separately).
            if pattern_name == "AWS Secret Key":
                continue
            if regex.search(value):
                findings.append(
                    {
                        "attribute_path": path,
                        "pattern": pattern_name,
                        "description": description,
                    }
                )
    elif isinstance(value, dict):
        for k, v in value.items():
            _scan_value_for_secrets(v, f"{path}.{k}", findings)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _scan_value_for_secrets(v, f"{path}[{i}]", findings)


def _check_sensitive_attribute_names(attributes, resource_path, findings):
    """Flag attributes whose *names* indicate a secret, regardless of regex match."""
    if not isinstance(attributes, dict):
        return
    for key, value in attributes.items():
        normalised = key.lower().replace("-", "_")
        if (
            normalised in SENSITIVE_ATTRIBUTE_NAMES
            and value
            and value not in (True, False, None, "")
        ):
            # Check it's not already redacted by the provider (e.g., "(sensitive value)")
            if isinstance(value, str) and value.strip().lower() in (
                "(sensitive value)",
                "(sensitive)",
            ):
                continue
            findings.append(
                {
                    "attribute_path": f"{resource_path}.{key}",
                    "pattern": "Sensitive attribute name",
                    "description": f"Attribute '{key}' commonly holds secrets and contains a non-empty value in state",
                }
            )


def scan_state_for_secrets(state_json):
    """
    Scan a Terraform state JSON blob (dict) for potential secrets.
    Returns a list of finding dicts.  The state_json is read-only and
    discarded by the caller — nothing is persisted.
    """
    findings = []
    resources = state_json.get("resources", [])
    for resource in resources:
        r_mode = resource.get("mode", "managed")
        r_type = resource.get("type", "unknown")
        r_name = resource.get("name", "unknown")
        resource_path = f"{r_mode}.{r_type}.{r_name}"

        for instance in resource.get("instances", []):
            attrs = instance.get("attributes", {})
            if attrs:
                _scan_value_for_secrets(attrs, resource_path, findings)
                _check_sensitive_attribute_names(attrs, resource_path, findings)

    # Also check outputs (root module outputs can contain secrets)
    outputs = state_json.get("outputs", {})
    for out_name, out_val in outputs.items():
        value = out_val.get("value") if isinstance(out_val, dict) else out_val
        _scan_value_for_secrets(value, f"output.{out_name}", findings)

    return findings


def fetch_state_and_scan(workspace_id, workspace_name):
    """
    Fetch the current state version for a workspace, stream-download the
    state JSON, scan for secrets, and return the findings.

    IMPORTANT: The state file is NEVER written to disk. It is held in memory
    only for the duration of the scan, then discarded.
    """
    # 1. Get current state version metadata (includes download URL)
    url = f"{TFC_API_BASE}/workspaces/{workspace_id}/current-state-version"
    print(f"  Checking state for workspace: {workspace_name}", file=sys.stderr)
    try:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {TFC_TOKEN}")
        req.add_header("Content-Type", "application/vnd.api+json")

        with urllib.request.urlopen(req) as response:
            sv_data = json.loads(response.read().decode())
    except Exception as e:
        # 404 = no state yet (new workspace), other errors = log and skip
        print(f"    No state available ({e})", file=sys.stderr)
        return {
            "workspace_id": workspace_id,
            "workspace_name": workspace_name,
            "has_state": False,
            "findings": [],
            "error": str(e),
        }

    if "data" not in sv_data:
        return {
            "workspace_id": workspace_id,
            "workspace_name": workspace_name,
            "has_state": False,
            "findings": [],
            "error": "No state data returned",
        }

    download_url = (
        sv_data["data"].get("attributes", {}).get("hosted-state-download-url")
    )
    state_size = sv_data["data"].get("attributes", {}).get("size", 0)

    if not download_url:
        return {
            "workspace_id": workspace_id,
            "workspace_name": workspace_name,
            "has_state": False,
            "findings": [],
            "error": "No download URL in state version",
        }

    # 2. Download state JSON into memory (never to disk)
    try:
        req = urllib.request.Request(download_url)
        req.add_header("Authorization", f"Bearer {TFC_TOKEN}")
        with urllib.request.urlopen(req) as response:
            state_bytes = response.read()
        state_json = json.loads(state_bytes.decode())
        # Immediately release the raw bytes
        del state_bytes
    except Exception as e:
        print(f"    Failed to download state ({e})", file=sys.stderr)
        return {
            "workspace_id": workspace_id,
            "workspace_name": workspace_name,
            "has_state": True,
            "findings": [],
            "error": f"Download failed: {e}",
        }

    # 3. Scan for secrets — state_json is read-only from here
    findings = scan_state_for_secrets(state_json)

    # 4. Discard state from memory
    del state_json

    finding_count = len(findings)
    if finding_count > 0:
        print(f"    ⚠️  Found {finding_count} potential secret(s)", file=sys.stderr)
    else:
        print(f"    ✅ No secrets detected", file=sys.stderr)

    return {
        "workspace_id": workspace_id,
        "workspace_name": workspace_name,
        "has_state": True,
        "state_size_bytes": state_size,
        "findings_count": finding_count,
        "findings": findings,
    }


def main():
    validate_config()

    print(f"Starting data collection for organization: {TFC_ORG}", file=sys.stderr)
    print(f"API Base: {TFC_API_BASE}", file=sys.stderr)
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"Timestamp: {timestamp}", file=sys.stderr)

    # 1. Collect all workspaces
    print("Collecting workspaces...", file=sys.stderr)
    workspaces_raw = fetch_all_pages(
        f"/organizations/{TFC_ORG}/workspaces?page[size]=100"
    )
    print(f"Found {len(workspaces_raw)} workspaces", file=sys.stderr)

    workspaces = [
        {
            "id": ws["id"],
            "name": ws["attributes"]["name"],
            "vcs_repo": ws["attributes"].get("vcs-repo"),
            "terraform_version": ws["attributes"].get("terraform-version"),
            "execution_mode": ws["attributes"].get("execution-mode"),
            "auto_apply": ws["attributes"].get("auto-apply"),
            "speculative_enabled": ws["attributes"].get("speculative-enabled"),
            "updated_at": ws["attributes"].get("updated-at"),
            "locked": ws["attributes"].get("locked"),
            "working_directory": ws["attributes"].get("working-directory"),
            "project_id": ws.get("relationships", {})
            .get("project", {})
            .get("data", {})
            .get("id"),
        }
        for ws in workspaces_raw
    ]

    # 2. Collect runs from up to 10 workspaces
    print("Collecting runs from sample workspaces...", file=sys.stderr)
    runs = []
    workspace_sample = workspaces_raw[: min(10, len(workspaces_raw))]

    for ws in workspace_sample:
        ws_id = ws["id"]
        ws_name = ws["attributes"]["name"]
        print(f"  Fetching runs for workspace: {ws_name} ({ws_id})", file=sys.stderr)

        ws_runs_raw = fetch_single(f"/workspaces/{ws_id}/runs?page[size]=20")

        for run in ws_runs_raw:
            runs.append(
                {
                    "workspace_id": ws_id,
                    "workspace_name": ws_name,
                    "status": run["attributes"].get("status"),
                    "source": run["attributes"].get("source"),
                    "created_at": run["attributes"].get("created-at"),
                    "is_destroy": run["attributes"].get("is-destroy"),
                    "auto_apply": run["attributes"].get("auto-apply"),
                    "trigger_reason": run["attributes"].get("trigger-reason"),
                }
            )

    print(f"Collected {len(runs)} runs", file=sys.stderr)

    # 3. State secrets check — stream each workspace's state, scan, discard
    print(
        "Scanning workspace states for secrets (on-the-fly, never stored)...",
        file=sys.stderr,
    )
    state_secrets_results = []
    for ws in workspaces_raw:
        ws_id = ws["id"]
        ws_name = ws["attributes"]["name"]
        result = fetch_state_and_scan(ws_id, ws_name)
        state_secrets_results.append(result)

    total_findings = sum(r.get("findings_count", 0) for r in state_secrets_results)
    ws_with_findings = sum(
        1 for r in state_secrets_results if r.get("findings_count", 0) > 0
    )
    print(
        f"State scan complete: {total_findings} finding(s) across {ws_with_findings} workspace(s)",
        file=sys.stderr,
    )

    print("Collecting registry modules...", file=sys.stderr)
    modules_raw = fetch_all_pages(
        f"/organizations/{TFC_ORG}/registry-modules?page[size]=100"
    )
    print(f"Found {len(modules_raw)} modules", file=sys.stderr)

    modules = [
        {
            "id": mod["id"],
            "name": mod["attributes"]["name"],
            "provider": mod["attributes"].get("provider"),
            "namespace": mod["attributes"].get("namespace"),
            "version_statuses": mod["attributes"].get("version-statuses", {}),
        }
        for mod in modules_raw
    ]

    print("Collecting policy sets...", file=sys.stderr)
    policy_sets_raw = fetch_all_pages(
        f"/organizations/{TFC_ORG}/policy-sets?page[size]=100"
    )
    print(f"Found {len(policy_sets_raw)} policy sets", file=sys.stderr)

    policy_sets = [
        {
            "id": ps["id"],
            "name": ps["attributes"]["name"],
            "description": ps["attributes"].get("description"),
            "policy_count": ps["attributes"].get("policy-count"),
            "workspace_count": ps["attributes"].get("workspace-count"),
            "global": ps["attributes"].get("global"),
            "kind": ps["attributes"].get("kind"),
        }
        for ps in policy_sets_raw
    ]

    print("Collecting teams...", file=sys.stderr)
    teams_raw = fetch_all_pages(f"/organizations/{TFC_ORG}/teams?page[size]=100")
    print(f"Found {len(teams_raw)} teams", file=sys.stderr)

    teams = [
        {
            "id": team["id"],
            "name": team["attributes"]["name"],
            "users_count": team["attributes"].get("users-count"),
            "organization_access": team["attributes"].get("organization-access"),
            "visibility": team["attributes"].get("visibility"),
        }
        for team in teams_raw
    ]

    print("Collecting variable sets...", file=sys.stderr)
    varsets_raw = fetch_all_pages(f"/organizations/{TFC_ORG}/varsets?page[size]=100")
    print(f"Found {len(varsets_raw)} variable sets", file=sys.stderr)

    varsets = [
        {
            "id": vs["id"],
            "name": vs["attributes"]["name"],
            "description": vs["attributes"].get("description"),
            "global": vs["attributes"].get("global"),
            "priority": vs["attributes"].get("priority"),
            "workspace_count": len(
                vs.get("relationships", {}).get("workspaces", {}).get("data", [])
            ),
        }
        for vs in varsets_raw
    ]

    print("Collecting projects...", file=sys.stderr)
    projects_raw = fetch_all_pages(f"/organizations/{TFC_ORG}/projects?page[size]=100")
    print(f"Found {len(projects_raw)} projects", file=sys.stderr)

    projects = [
        {
            "id": proj["id"],
            "name": proj["attributes"]["name"],
            "description": proj["attributes"].get("description"),
        }
        for proj in projects_raw
    ]

    # Build final structure
    print("Building final JSON structure...", file=sys.stderr)
    result = {
        "organization": TFC_ORG,
        "collected_at": timestamp,
        "workspaces": workspaces,
        "runs": runs,
        "state_secrets_check": state_secrets_results,
        "modules": modules,
        "policy_sets": policy_sets,
        "teams": teams,
        "variable_sets": varsets,
        "projects": projects,
        "metadata": {
            "total_workspaces": len(workspaces),
            "total_runs_sampled": len(runs),
            "total_modules": len(modules),
            "total_policies": len(policy_sets),
            "total_teams": len(teams),
            "total_variable_sets": len(varsets),
            "total_projects": len(projects),
            "state_secrets_total_findings": total_findings,
            "state_secrets_workspaces_with_findings": ws_with_findings,
        },
    }

    # Save to file
    with open(OUTPUT_FILE, "w") as f:
        json.dump(result, f, indent=2)

    print("", file=sys.stderr)
    print("========================================", file=sys.stderr)
    print("Data collection complete!", file=sys.stderr)
    print("========================================", file=sys.stderr)
    print(f"Output saved to: {OUTPUT_FILE}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Summary:", file=sys.stderr)
    print(f"  Workspaces: {len(workspaces)}", file=sys.stderr)
    print(f"  Runs (sampled): {len(runs)}", file=sys.stderr)
    print(
        f"  State secrets findings: {total_findings} across {ws_with_findings} workspace(s)",
        file=sys.stderr,
    )
    print(f"  Modules: {len(modules)}", file=sys.stderr)
    print(f"  Policy Sets: {len(policy_sets)}", file=sys.stderr)
    print(f"  Teams: {len(teams)}", file=sys.stderr)
    print(f"  Variable Sets: {len(varsets)}", file=sys.stderr)
    print(f"  Projects: {len(projects)}", file=sys.stderr)
    print("========================================", file=sys.stderr)


if __name__ == "__main__":
    main()
