#!/usr/bin/env python3
"""
TFC/TFE Data Obfuscation Script

Obfuscates business-sensitive information (names of workspaces, teams, modules,
projects, policies, variable sets, organization, VCS repos, etc.) in the collected
data.json so it can be safely shared with a HashiCorp Sales Engineer for analysis.

The script produces:
  - assessment/data_obfuscated.json  (safe to share with SE)
  - assessment/obfuscation_map.json  (KEEP PRIVATE - needed to deobfuscate reports)

Usage:
    python3 obfuscate_data.py [--input assessment/data.json] [--output-dir assessment]

The obfuscation_map.json is the ONLY file that maps hashed names back to real names.
NEVER share this file with anyone outside your organization.
"""

import json
import hashlib
import os
import sys
import argparse
from datetime import datetime


def make_hash(value, salt):
    """Create a deterministic, short hash for a given value."""
    if value is None:
        return None
    raw = hashlib.sha256(f"{salt}:{value}".encode()).hexdigest()[:12]
    return raw


def obfuscate_string(value, prefix, salt, mapping):
    """Obfuscate a string value and record the mapping."""
    if value is None:
        return None
    hashed = make_hash(value, salt)
    obfuscated = f"{prefix}-{hashed}"
    mapping[obfuscated] = value
    return obfuscated


def obfuscate_vcs_repo(vcs_repo, salt, mapping):
    """Obfuscate VCS repo identifiers while preserving structure."""
    if vcs_repo is None:
        return None

    result = dict(vcs_repo)

    # Obfuscate the repository identifier (e.g., "org/repo-name")
    if "identifier" in result and result["identifier"]:
        result["identifier"] = obfuscate_string(
            result["identifier"], "repo", salt, mapping
        )

    # Obfuscate oauth-token-id (contains no business info, but obfuscate for safety)
    if "oauth-token-id" in result and result["oauth-token-id"]:
        result["oauth-token-id"] = obfuscate_string(
            result["oauth-token-id"], "oauth", salt, mapping
        )

    # Obfuscate display-identifier if present
    if "display-identifier" in result and result["display-identifier"]:
        result["display-identifier"] = obfuscate_string(
            result["display-identifier"], "repo", salt, mapping
        )

    return result


def obfuscate_data(data, salt):
    """Obfuscate all business-sensitive fields in the collected data."""
    mapping = {}
    result = {}

    # Organization name
    result["organization"] = obfuscate_string(
        data.get("organization"), "org", salt, mapping
    )
    result["collected_at"] = data.get("collected_at")

    # Workspaces
    result["workspaces"] = []
    for ws in data.get("workspaces", []):
        obf_ws = dict(ws)
        obf_ws["id"] = obfuscate_string(ws.get("id"), "wsid", salt, mapping)
        obf_ws["name"] = obfuscate_string(ws.get("name"), "ws", salt, mapping)
        obf_ws["vcs_repo"] = obfuscate_vcs_repo(ws.get("vcs_repo"), salt, mapping)
        obf_ws["working_directory"] = (
            obfuscate_string(ws.get("working_directory"), "dir", salt, mapping)
            if ws.get("working_directory")
            else None
        )
        obf_ws["project_id"] = obfuscate_string(
            ws.get("project_id"), "prjid", salt, mapping
        )
        # Preserve non-sensitive fields as-is
        # terraform_version, execution_mode, auto_apply, speculative_enabled,
        # updated_at, locked - these are metrics, not business data
        result["workspaces"].append(obf_ws)

    # Runs
    result["runs"] = []
    for run in data.get("runs", []):
        obf_run = dict(run)
        obf_run["workspace_id"] = obfuscate_string(
            run.get("workspace_id"), "wsid", salt, mapping
        )
        obf_run["workspace_name"] = obfuscate_string(
            run.get("workspace_name"), "ws", salt, mapping
        )
        # Preserve: status, source, created_at, is_destroy, auto_apply,
        # trigger_reason - these are metrics
        result["runs"].append(obf_run)

    # Modules
    result["modules"] = []
    for mod in data.get("modules", []):
        obf_mod = dict(mod)
        obf_mod["id"] = obfuscate_string(mod.get("id"), "modid", salt, mapping)
        obf_mod["name"] = obfuscate_string(mod.get("name"), "mod", salt, mapping)
        obf_mod["namespace"] = obfuscate_string(
            mod.get("namespace"), "ns", salt, mapping
        )
        # Preserve: provider, version_statuses - these are metrics
        result["modules"].append(obf_mod)

    # Policy Sets
    result["policy_sets"] = []
    for ps in data.get("policy_sets", []):
        obf_ps = dict(ps)
        obf_ps["id"] = obfuscate_string(ps.get("id"), "psid", salt, mapping)
        obf_ps["name"] = obfuscate_string(ps.get("name"), "ps", salt, mapping)
        obf_ps["description"] = (
            obfuscate_string(ps.get("description"), "desc", salt, mapping)
            if ps.get("description")
            else None
        )
        # Preserve: policy_count, workspace_count, global, kind - these are metrics
        result["policy_sets"].append(obf_ps)

    # Teams
    result["teams"] = []
    for team in data.get("teams", []):
        obf_team = dict(team)
        obf_team["id"] = obfuscate_string(team.get("id"), "tmid", salt, mapping)
        obf_team["name"] = obfuscate_string(team.get("name"), "team", salt, mapping)
        # Preserve: users_count, organization_access, visibility - these are metrics
        result["teams"].append(obf_team)

    # Variable Sets
    result["variable_sets"] = []
    for vs in data.get("variable_sets", []):
        obf_vs = dict(vs)
        obf_vs["id"] = obfuscate_string(vs.get("id"), "vsid", salt, mapping)
        obf_vs["name"] = obfuscate_string(vs.get("name"), "vs", salt, mapping)
        obf_vs["description"] = (
            obfuscate_string(vs.get("description"), "desc", salt, mapping)
            if vs.get("description")
            else None
        )
        # Preserve: global, priority, workspace_count - these are metrics
        result["variable_sets"].append(obf_vs)

    # Projects
    result["projects"] = []
    for proj in data.get("projects", []):
        obf_proj = dict(proj)
        obf_proj["id"] = obfuscate_string(proj.get("id"), "prid", salt, mapping)
        obf_proj["name"] = obfuscate_string(proj.get("name"), "proj", salt, mapping)
        obf_proj["description"] = (
            obfuscate_string(proj.get("description"), "desc", salt, mapping)
            if proj.get("description")
            else None
        )
        result["projects"].append(obf_proj)

    # Metadata - preserve as-is (counts only, no business names)
    result["metadata"] = data.get("metadata", {})

    return result, mapping


def main():
    parser = argparse.ArgumentParser(
        description="Obfuscate business-sensitive data in TFC/TFE assessment data"
    )
    parser.add_argument(
        "--input",
        "-i",
        default=os.path.join(os.getenv("OUTPUT_DIR", "./assessment"), "data.json"),
        help="Path to input data.json (default: assessment/data.json)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=os.getenv("OUTPUT_DIR", "./assessment"),
        help="Output directory (default: assessment/)",
    )
    args = parser.parse_args()

    input_file = args.input
    output_dir = args.output_dir
    obfuscated_file = os.path.join(output_dir, "data_obfuscated.json")
    mapping_file = os.path.join(output_dir, "obfuscation_map.json")

    # Validate input
    if not os.path.exists(input_file):
        print(f"ERROR: Input file not found: {input_file}", file=sys.stderr)
        print("Run collect_tfc_data.py first to generate data.json", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # Load data
    print(f"Loading data from: {input_file}", file=sys.stderr)
    with open(input_file, "r") as f:
        data = json.load(f)

    # Generate a random salt for this obfuscation session
    salt = hashlib.sha256(os.urandom(32)).hexdigest()[:16]

    # Obfuscate
    print("Obfuscating business-sensitive fields...", file=sys.stderr)
    obfuscated_data, mapping = obfuscate_data(data, salt)

    # Save obfuscated data (safe to share)
    with open(obfuscated_file, "w") as f:
        json.dump(obfuscated_data, f, indent=2)
    print(f"Obfuscated data saved to: {obfuscated_file}", file=sys.stderr)

    # Save mapping (KEEP PRIVATE)
    mapping_output = {
        "created_at": datetime.now(tz=__import__("datetime").timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "salt": salt,
        "description": "This file maps obfuscated names back to real names. "
        "KEEP THIS FILE PRIVATE. Never share it outside your organization.",
        "mapping": mapping,
    }
    with open(mapping_file, "w") as f:
        json.dump(mapping_output, f, indent=2)
    print(f"Obfuscation mapping saved to: {mapping_file}", file=sys.stderr)

    # Summary
    print("", file=sys.stderr)
    print("========================================", file=sys.stderr)
    print("Obfuscation complete!", file=sys.stderr)
    print("========================================", file=sys.stderr)
    print(f"  Obfuscated entries: {len(mapping)}", file=sys.stderr)
    print("", file=sys.stderr)
    print("SHARE with your SE:    ", file=sys.stderr)
    print(f"  {obfuscated_file}", file=sys.stderr)
    print("", file=sys.stderr)
    print("KEEP PRIVATE (do NOT share):", file=sys.stderr)
    print(f"  {mapping_file}", file=sys.stderr)
    print("========================================", file=sys.stderr)


if __name__ == "__main__":
    main()
