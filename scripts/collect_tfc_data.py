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
from datetime import datetime
import sys

# Configuration from environment variables
TFC_TOKEN = os.getenv('TFC_TOKEN')
TFC_ORG = os.getenv('TFC_ORG')
TFC_API_BASE = os.getenv('TFC_API_BASE', 'https://app.terraform.io/api/v2')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', './assessment')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'data.json')

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

            if 'errors' in data:
                print(f"Error: {data['errors'][0]['detail']}", file=sys.stderr)
                break

            results.extend(data.get('data', []))

            # Check for next page
            url = data.get('links', {}).get('next')

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

        if 'errors' in data:
            print(f"Error: {data['errors'][0]['detail']}", file=sys.stderr)
            return []

        return data.get('data', [])

    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return []

def main():
    validate_config()

    print(f"Starting data collection for organization: {TFC_ORG}", file=sys.stderr)
    print(f"API Base: {TFC_API_BASE}", file=sys.stderr)
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"Timestamp: {timestamp}", file=sys.stderr)

    # 1. Collect all workspaces
    print("Collecting workspaces...", file=sys.stderr)
    workspaces_raw = fetch_all_pages(f"/organizations/{TFC_ORG}/workspaces?page[size]=100")
    print(f"Found {len(workspaces_raw)} workspaces", file=sys.stderr)

    workspaces = [{
        'id': ws['id'],
        'name': ws['attributes']['name'],
        'vcs_repo': ws['attributes'].get('vcs-repo'),
        'terraform_version': ws['attributes'].get('terraform-version'),
        'execution_mode': ws['attributes'].get('execution-mode'),
        'auto_apply': ws['attributes'].get('auto-apply'),
        'speculative_enabled': ws['attributes'].get('speculative-enabled'),
        'updated_at': ws['attributes'].get('updated-at'),
        'locked': ws['attributes'].get('locked'),
        'working_directory': ws['attributes'].get('working-directory'),
        'project_id': ws.get('relationships', {}).get('project', {}).get('data', {}).get('id')
    } for ws in workspaces_raw]

    # 2. Collect runs from up to 10 workspaces
    print("Collecting runs from sample workspaces...", file=sys.stderr)
    runs = []
    workspace_sample = workspaces_raw[:min(10, len(workspaces_raw))]

    for ws in workspace_sample:
        ws_id = ws['id']
        ws_name = ws['attributes']['name']
        print(f"  Fetching runs for workspace: {ws_name} ({ws_id})", file=sys.stderr)

        ws_runs_raw = fetch_single(f"/workspaces/{ws_id}/runs?page[size]=20")

        for run in ws_runs_raw:
            runs.append({
                'workspace_id': ws_id,
                'workspace_name': ws_name,
                'status': run['attributes'].get('status'),
                'source': run['attributes'].get('source'),
                'created_at': run['attributes'].get('created-at'),
                'is_destroy': run['attributes'].get('is-destroy'),
                'auto_apply': run['attributes'].get('auto-apply'),
                'trigger_reason': run['attributes'].get('trigger-reason')
            })

    print(f"Collected {len(runs)} runs", file=sys.stderr)

    # 3. Collect registry modules
    print("Collecting registry modules...", file=sys.stderr)
    modules_raw = fetch_all_pages(f"/organizations/{TFC_ORG}/registry-modules?page[size]=100")
    print(f"Found {len(modules_raw)} modules", file=sys.stderr)

    modules = [{
        'id': mod['id'],
        'name': mod['attributes']['name'],
        'provider': mod['attributes'].get('provider'),
        'namespace': mod['attributes'].get('namespace'),
        'version_statuses': mod['attributes'].get('version-statuses', {})
    } for mod in modules_raw]

    # 4. Collect policy sets
    print("Collecting policy sets...", file=sys.stderr)
    policy_sets_raw = fetch_all_pages(f"/organizations/{TFC_ORG}/policy-sets?page[size]=100")
    print(f"Found {len(policy_sets_raw)} policy sets", file=sys.stderr)

    policy_sets = [{
        'id': ps['id'],
        'name': ps['attributes']['name'],
        'description': ps['attributes'].get('description'),
        'policy_count': ps['attributes'].get('policy-count'),
        'workspace_count': ps['attributes'].get('workspace-count'),
        'global': ps['attributes'].get('global'),
        'kind': ps['attributes'].get('kind')
    } for ps in policy_sets_raw]

    # 5. Collect teams
    print("Collecting teams...", file=sys.stderr)
    teams_raw = fetch_all_pages(f"/organizations/{TFC_ORG}/teams?page[size]=100")
    print(f"Found {len(teams_raw)} teams", file=sys.stderr)

    teams = [{
        'id': team['id'],
        'name': team['attributes']['name'],
        'users_count': team['attributes'].get('users-count'),
        'organization_access': team['attributes'].get('organization-access'),
        'visibility': team['attributes'].get('visibility')
    } for team in teams_raw]

    # 6. Collect variable sets
    print("Collecting variable sets...", file=sys.stderr)
    varsets_raw = fetch_all_pages(f"/organizations/{TFC_ORG}/varsets?page[size]=100")
    print(f"Found {len(varsets_raw)} variable sets", file=sys.stderr)

    varsets = [{
        'id': vs['id'],
        'name': vs['attributes']['name'],
        'description': vs['attributes'].get('description'),
        'global': vs['attributes'].get('global'),
        'priority': vs['attributes'].get('priority'),
        'workspace_count': len(vs.get('relationships', {}).get('workspaces', {}).get('data', []))
    } for vs in varsets_raw]

    # 7. Collect projects
    print("Collecting projects...", file=sys.stderr)
    projects_raw = fetch_all_pages(f"/organizations/{TFC_ORG}/projects?page[size]=100")
    print(f"Found {len(projects_raw)} projects", file=sys.stderr)

    projects = [{
        'id': proj['id'],
        'name': proj['attributes']['name'],
        'description': proj['attributes'].get('description')
    } for proj in projects_raw]

    # Build final structure
    print("Building final JSON structure...", file=sys.stderr)
    result = {
        'organization': TFC_ORG,
        'collected_at': timestamp,
        'workspaces': workspaces,
        'runs': runs,
        'modules': modules,
        'policy_sets': policy_sets,
        'teams': teams,
        'variable_sets': varsets,
        'projects': projects,
        'metadata': {
            'total_workspaces': len(workspaces),
            'total_runs_sampled': len(runs),
            'total_modules': len(modules),
            'total_policies': len(policy_sets),
            'total_teams': len(teams),
            'total_variable_sets': len(varsets),
            'total_projects': len(projects)
        }
    }

    # Save to file
    with open(OUTPUT_FILE, 'w') as f:
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
    print(f"  Modules: {len(modules)}", file=sys.stderr)
    print(f"  Policy Sets: {len(policy_sets)}", file=sys.stderr)
    print(f"  Teams: {len(teams)}", file=sys.stderr)
    print(f"  Variable Sets: {len(varsets)}", file=sys.stderr)
    print(f"  Projects: {len(projects)}", file=sys.stderr)
    print("========================================", file=sys.stderr)

if __name__ == '__main__':
    main()
