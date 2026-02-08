#!/bin/bash
#
# TFC/TFE Data Collection Script (Bash version)
# Collects comprehensive organization data from Terraform Cloud or Terraform Enterprise API.
#
# Usage:
#     export TFC_TOKEN="your-token"
#     export TFC_ORG="your-org"
#     export TFC_API_BASE="https://app.terraform.io/api/v2"  # or TFE URL
#     export OUTPUT_DIR="./assessment"
#     ./collect_tfc_data.sh

set -euo pipefail

# Configuration from environment variables
TFC_TOKEN="${TFC_TOKEN:-}"
TFC_ORG="${TFC_ORG:-}"
TFC_API_BASE="${TFC_API_BASE:-https://app.terraform.io/api/v2}"
OUTPUT_DIR="${OUTPUT_DIR:-./assessment}"
OUTPUT_FILE="${OUTPUT_DIR}/data.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Validate required environment variables
if [ -z "$TFC_TOKEN" ]; then
    echo "ERROR: TFC_TOKEN environment variable not set" >&2
    exit 1
fi

if [ -z "$TFC_ORG" ]; then
    echo "ERROR: TFC_ORG environment variable not set" >&2
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Function to make API calls with pagination support
fetch_all_pages() {
    local endpoint=$1
    local temp_file="/tmp/tfc_fetch_$$.json"
    echo "[]" > "$temp_file"

    local url="${TFC_API_BASE}${endpoint}"

    while [ -n "$url" ]; do
        echo "Fetching: $url" >&2
        response=$(curl -s -H "Authorization: Bearer $TFC_TOKEN" -H "Content-Type: application/vnd.api+json" "$url")

        # Check for errors
        if echo "$response" | jq -e '.errors' > /dev/null 2>&1; then
            echo "Error fetching $url: $(echo "$response" | jq -r '.errors[0].detail')" >&2
            break
        fi

        # Extract data and append to results
        page_data=$(echo "$response" | jq -c '.data // []')
        if [ "$page_data" != "[]" ]; then
            current=$(cat "$temp_file")
            echo "$current" | jq -c ". + $page_data" > "$temp_file"
        fi

        # Check for next page
        next_url=$(echo "$response" | jq -r '.links.next // empty')
        if [ -n "$next_url" ]; then
            url="$next_url"
        else
            url=""
        fi
    done

    cat "$temp_file"
    rm -f "$temp_file"
}

# Function to make single API call
fetch_single() {
    local endpoint=$1
    local url="${TFC_API_BASE}${endpoint}"

    echo "Fetching: $url" >&2
    response=$(curl -s -H "Authorization: Bearer $TFC_TOKEN" -H "Content-Type: application/vnd.api+json" "$url")

    # Check for errors
    if echo "$response" | jq -e '.errors' > /dev/null 2>&1; then
        echo "Error fetching $url: $(echo "$response" | jq -r '.errors[0].detail')" >&2
        echo "[]"
    else
        echo "$response" | jq -c '.data // []'
    fi
}

echo "Starting data collection for organization: $TFC_ORG" >&2
echo "API Base: $TFC_API_BASE" >&2
echo "Timestamp: $TIMESTAMP" >&2

# 1. Collect all workspaces
echo "Collecting workspaces..." >&2
workspaces=$(fetch_all_pages "/organizations/${TFC_ORG}/workspaces?page[size]=100")
workspace_count=$(echo "$workspaces" | jq 'length')
echo "Found $workspace_count workspaces" >&2

# Extract simplified workspace data
workspaces_simplified=$(echo "$workspaces" | jq '[.[] | {
    id: .id,
    name: .attributes.name,
    vcs_repo: .attributes["vcs-repo"],
    terraform_version: .attributes["terraform-version"],
    execution_mode: .attributes["execution-mode"],
    auto_apply: .attributes["auto-apply"],
    speculative_enabled: .attributes["speculative-enabled"],
    updated_at: .attributes["updated-at"],
    locked: .attributes.locked,
    working_directory: .attributes["working-directory"],
    project_id: .relationships.project.data.id
}]')

# 2. Collect runs from up to 10 workspaces
echo "Collecting runs from sample workspaces..." >&2
runs="[]"
workspace_sample=$(echo "$workspaces" | jq -r '.[0:10] | .[].id')

for ws_id in $workspace_sample; do
    ws_name=$(echo "$workspaces" | jq -r ".[] | select(.id == \"$ws_id\") | .attributes.name")
    echo "  Fetching runs for workspace: $ws_name ($ws_id)" >&2
    ws_runs=$(fetch_single "/workspaces/${ws_id}/runs?page[size]=20")
    ws_runs_simplified=$(echo "$ws_runs" | jq --arg wsid "$ws_id" --arg wsname "$ws_name" '[.[] | {
        workspace_id: $wsid,
        workspace_name: $wsname,
        status: .attributes.status,
        source: .attributes.source,
        created_at: .attributes["created-at"],
        is_destroy: .attributes["is-destroy"],
        auto_apply: .attributes["auto-apply"],
        trigger_reason: .attributes["trigger-reason"]
    }]')
    runs=$(echo "[$runs, $ws_runs_simplified]" | jq -c 'add | flatten')
done

run_count=$(echo "$runs" | jq 'length')
echo "Collected $run_count runs" >&2

# 3. State secrets check — stream each workspace's state, scan on-the-fly, never store
echo "Scanning workspace states for secrets (on-the-fly, never stored)..." >&2
state_secrets="[]"
total_state_findings=0
ws_with_findings=0

for ws_id in $(echo "$workspaces" | jq -r '.[].id'); do
    ws_name=$(echo "$workspaces" | jq -r ".[] | select(.id == \"$ws_id\") | .attributes.name")
    echo "  Checking state for workspace: $ws_name" >&2

    sv_response=$(curl -s -H "Authorization: Bearer $TFC_TOKEN" \
        -H "Content-Type: application/vnd.api+json" \
        "${TFC_API_BASE}/workspaces/${ws_id}/current-state-version" 2>/dev/null)

    download_url=$(echo "$sv_response" | jq -r '.data.attributes["hosted-state-download-url"] // empty' 2>/dev/null)

    if [ -z "$download_url" ]; then
        echo "    No state available" >&2
        entry=$(jq -n --arg wsid "$ws_id" --arg wsname "$ws_name" '{
            workspace_id: $wsid,
            workspace_name: $wsname,
            has_state: false,
            findings: []
        }')
        state_secrets=$(echo "[$state_secrets, [$entry]]" | jq -c 'add | flatten')
        continue
    fi

    state_size=$(echo "$sv_response" | jq -r '.data.attributes.size // 0')

    state_json=$(curl -s -H "Authorization: Bearer $TFC_TOKEN" "$download_url" 2>/dev/null)

    findings="[]"

    scan_result=$(echo "$state_json" | jq -c '
        def scan_attrs(path; attrs):
            (attrs | to_entries[]
             | select(.value != null and .value != "" and .value != false and .value != true)
             | select(.key | test("(?i)^(password|passwd|pwd|secret|api_key|api_secret|api_token|access_key|secret_key|private_key|token|auth_token|master_password|admin_password|db_password|connection_string|client_secret|signing_key|encryption_key|ssh_key|tls_private_key|secret_key_base)$"))
             | select(.value | type == "string")
             | select(.value | test("^\\(sensitive") | not)
             | {attribute_path: (path + "." + .key), pattern: "Sensitive attribute name",
                description: ("Attribute \(.key) commonly holds secrets and contains a non-empty value in state")}),
            (attrs | to_entries[]
             | select(.value != null and (.value | type == "string"))
             | select(.value | test("AKIA[0-9A-Z]{16}|-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----|(?i)(api[_-]?key|api[_-]?secret|api[_-]?token)\\s*[:=]\\s*|(?i)(password|passwd|pwd|secret)\\s*[:=]\\s*|(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}|xox[bpas]-[0-9]{10,}-|(?i)bearer\\s+[A-Za-z0-9._~+/-]+=*|(?i)(mysql|postgres|postgresql|mongodb|redis|amqp|mssql)://[^:]+:[^@]+@"))
             | {attribute_path: (path + "." + .key), pattern: "Secret pattern match",
                description: "Value matches a known secret pattern"});

        [(.resources // [] | .[] |
            . as $r |
            (.instances // [] | .[] |
                (.attributes // {} | to_entries[] | select(.value != null)) as $dummy |
                scan_attrs(($r.mode // "managed") + "." + ($r.type // "unknown") + "." + ($r.name // "unknown"); .attributes // {})
            )),
         (.outputs // {} | to_entries[] |
            select(.value.value != null and (.value.value | type == "string")) |
            select(.value.value | test("AKIA[0-9A-Z]{16}|-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----|(?i)(api[_-]?key|api[_-]?secret|api[_-]?token)\\s*[:=]\\s*|(?i)(password|passwd|pwd|secret)\\s*[:=]\\s*|(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}|xox[bpas]-[0-9]{10,}-|(?i)bearer\\s+[A-Za-z0-9._~+/-]+=*|(?i)(mysql|postgres|postgresql|mongodb|redis|amqp|mssql)://[^:]+:[^@]+@")) |
            {attribute_path: ("output." + .key), pattern: "Secret pattern match",
             description: "Output value matches a known secret pattern"})]' 2>/dev/null || echo "[]")

    unset state_json

    finding_count=$(echo "$scan_result" | jq 'length')

    if [ "$finding_count" -gt 0 ]; then
        echo "    ⚠️  Found $finding_count potential secret(s)" >&2
        total_state_findings=$((total_state_findings + finding_count))
        ws_with_findings=$((ws_with_findings + 1))
    else
        echo "    ✅ No secrets detected" >&2
    fi

    entry=$(jq -n --arg wsid "$ws_id" --arg wsname "$ws_name" \
        --argjson has_state true \
        --argjson state_size "$state_size" \
        --argjson count "$finding_count" \
        --argjson findings "$scan_result" '{
        workspace_id: $wsid,
        workspace_name: $wsname,
        has_state: $has_state,
        state_size_bytes: $state_size,
        findings_count: $count,
        findings: $findings
    }')
    state_secrets=$(echo "[$state_secrets, [$entry]]" | jq -c 'add | flatten')
done

echo "State scan complete: $total_state_findings finding(s) across $ws_with_findings workspace(s)" >&2

# 4. Collect registry modules
echo "Collecting registry modules..." >&2
modules=$(fetch_all_pages "/organizations/${TFC_ORG}/registry-modules?page[size]=100")
module_count=$(echo "$modules" | jq 'length')
echo "Found $module_count modules" >&2

modules_simplified=$(echo "$modules" | jq '[.[] | {
    id: .id,
    name: .attributes.name,
    provider: .attributes.provider,
    namespace: .attributes.namespace,
    version_statuses: .attributes["version-statuses"]
}]')

# 5. Collect policy sets
echo "Collecting policy sets..." >&2
policy_sets=$(fetch_all_pages "/organizations/${TFC_ORG}/policy-sets?page[size]=100")
policy_count=$(echo "$policy_sets" | jq 'length')
echo "Found $policy_count policy sets" >&2

policy_sets_simplified=$(echo "$policy_sets" | jq '[.[] | {
    id: .id,
    name: .attributes.name,
    description: .attributes.description,
    policy_count: .attributes["policy-count"],
    workspace_count: .attributes["workspace-count"],
    global: .attributes.global,
    kind: .attributes.kind
}]')

# 6. Collect teams
echo "Collecting teams..." >&2
teams=$(fetch_all_pages "/organizations/${TFC_ORG}/teams?page[size]=100")
team_count=$(echo "$teams" | jq 'length')
echo "Found $team_count teams" >&2

teams_simplified=$(echo "$teams" | jq '[.[] | {
    id: .id,
    name: .attributes.name,
    users_count: .attributes["users-count"],
    organization_access: .attributes["organization-access"],
    visibility: .attributes.visibility
}]')

# 7. Collect variable sets
echo "Collecting variable sets..." >&2
varsets=$(fetch_all_pages "/organizations/${TFC_ORG}/varsets?page[size]=100")
varset_count=$(echo "$varsets" | jq 'length')
echo "Found $varset_count variable sets" >&2

varsets_simplified=$(echo "$varsets" | jq '[.[] | {
    id: .id,
    name: .attributes.name,
    description: .attributes.description,
    global: .attributes.global,
    priority: .attributes.priority,
    workspace_count: (.relationships.workspaces.data // [] | length)
}]')

# 8. Collect projects
echo "Collecting projects..." >&2
projects=$(fetch_all_pages "/organizations/${TFC_ORG}/projects?page[size]=100")
project_count=$(echo "$projects" | jq 'length')
echo "Found $project_count projects" >&2

projects_simplified=$(echo "$projects" | jq '[.[] | {
    id: .id,
    name: .attributes.name,
    description: .attributes.description
}]')

# Build final JSON structure
echo "Building final JSON structure..." >&2
final_json=$(jq -n \
    --arg org "$TFC_ORG" \
    --arg timestamp "$TIMESTAMP" \
    --argjson workspaces "$workspaces_simplified" \
    --argjson runs "$runs" \
    --argjson state_secrets "$state_secrets" \
    --argjson modules "$modules_simplified" \
    --argjson policy_sets "$policy_sets_simplified" \
    --argjson teams "$teams_simplified" \
    --argjson varsets "$varsets_simplified" \
    --argjson projects "$projects_simplified" \
    --argjson ws_count "$workspace_count" \
    --argjson mod_count "$module_count" \
    --argjson pol_count "$policy_count" \
    --argjson team_count "$team_count" \
    --argjson run_count "$run_count" \
    --argjson varset_count "$varset_count" \
    --argjson proj_count "$project_count" \
    --argjson state_findings "$total_state_findings" \
    --argjson state_ws_findings "$ws_with_findings" \
    '{
        organization: $org,
        collected_at: $timestamp,
        workspaces: $workspaces,
        runs: $runs,
        state_secrets_check: $state_secrets,
        modules: $modules,
        policy_sets: $policy_sets,
        teams: $teams,
        variable_sets: $varsets,
        projects: $projects,
        metadata: {
            total_workspaces: $ws_count,
            total_runs_sampled: $run_count,
            total_modules: $mod_count,
            total_policies: $pol_count,
            total_teams: $team_count,
            total_variable_sets: $varset_count,
            total_projects: $proj_count,
            state_secrets_total_findings: $state_findings,
            state_secrets_workspaces_with_findings: $state_ws_findings
        }
    }')

# Save to file
echo "$final_json" | jq '.' > "$OUTPUT_FILE"

echo "" >&2
echo "========================================" >&2
echo "Data collection complete!" >&2
echo "========================================" >&2
echo "Output saved to: $OUTPUT_FILE" >&2
echo "" >&2
echo "Summary:" >&2
echo "  Workspaces: $workspace_count" >&2
echo "  Runs (sampled): $run_count" >&2
echo "  State secrets findings: $total_state_findings across $ws_with_findings workspace(s)" >&2
echo "  Modules: $module_count" >&2
echo "  Policy Sets: $policy_count" >&2
echo "  Teams: $team_count" >&2
echo "  Variable Sets: $varset_count" >&2
echo "  Projects: $project_count" >&2
echo "========================================" >&2
