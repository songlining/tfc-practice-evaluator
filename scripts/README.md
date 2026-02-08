# TFC/TFE Data Collection & Privacy Scripts

Production-ready scripts for collecting comprehensive organization data from Terraform Cloud or Terraform Enterprise APIs, with optional obfuscation for safe sharing with your HashiCorp Sales Engineer.

## Scripts Overview

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `collect_tfc_data.py` | Collect data from TFC/TFE API | Always (both modes) |
| `collect_tfc_data.sh` | Collect data (Bash alternative) | Always (both modes) |
| `obfuscate_data.py` | Hash business names in data.json | Mode 2: SE-assisted only |
| `deobfuscate_report.py` | Restore real names in reports | Mode 2: SE-assisted only |

## Quick Start

### Python Version (Recommended)

```bash
# Set environment variables
export TFC_TOKEN="your-team-token"
export TFC_ORG="your-organization"
export OUTPUT_DIR="./assessment"

# Optional: For Terraform Enterprise
export TFC_API_BASE="https://tfe.example.com/api/v2"

# Run the script
python3 collect_tfc_data.py
```

### Bash Version

```bash
# Set environment variables
export TFC_TOKEN="your-team-token"
export TFC_ORG="your-organization"
export OUTPUT_DIR="./assessment"

# Optional: For Terraform Enterprise
export TFC_API_BASE="https://tfe.example.com/api/v2"

# Run the script
./collect_tfc_data.sh
```

## Requirements

### Python Version
- Python 3.6 or higher
- No external dependencies (uses standard library only)
- Cross-platform (macOS, Linux, Windows)

### Bash Version
- Bash 4.0+
- `curl` - HTTP client
- `jq` - JSON processor

Install jq:
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# RHEL/CentOS
sudo yum install jq
```

## What Gets Collected

The scripts collect comprehensive data from 8 TFC/TFE API endpoints:

1. **Workspaces** - All workspaces with VCS, Terraform version, execution mode, etc.
2. **Runs** - Sample of recent runs (up to 20 runs from up to 10 workspaces)
3. **State Secrets Scan** - Each workspace's current state is streamed in memory and scanned for leaked secrets (AWS keys, private keys, API tokens, passwords, connection strings, GitHub/Slack tokens, bearer tokens, sensitive attribute names). **State files are never saved to disk** — they are held in memory during scanning and immediately discarded.
4. **Registry Modules** - All private modules with version information
5. **Policy Sets** - All policy sets (Sentinel/OPA) with enforcement levels
6. **Teams** - All teams with user counts and permissions
7. **Variable Sets** - All variable sets with workspace attachments
8. **Projects** - All projects with descriptions

## Output Format

Creates `assessment/data.json` with this structure:

```json
{
  "organization": "org-name",
  "collected_at": "2026-02-06T19:12:34Z",
  "workspaces": [
    {
      "id": "ws-...",
      "name": "workspace-name",
      "vcs_repo": {...},
      "terraform_version": "1.9.6",
      "execution_mode": "remote",
      "auto_apply": true,
      "speculative_enabled": true,
      "updated_at": "2025-01-15T10:30:00Z",
      "locked": false,
      "working_directory": null,
      "project_id": "prj-..."
    }
  ],
  "runs": [...],
  "state_secrets_check": [
    {
      "workspace_id": "ws-...",
      "workspace_name": "workspace-name",
      "has_state": true,
      "state_size_bytes": 45000,
      "findings_count": 2,
      "findings": [
        {
          "attribute_path": "managed.aws_db_instance.main.password",
          "pattern": "Sensitive attribute name",
          "description": "Attribute 'password' commonly holds secrets and contains a non-empty value in state"
        }
      ]
    }
  ],
  "modules": [...],
  "policy_sets": [...],
  "teams": [...],
  "variable_sets": [...],
  "projects": [...],
  "metadata": {
    "total_workspaces": 4,
    "total_runs_sampled": 68,
    "total_modules": 41,
    "total_policies": 0,
    "total_teams": 1,
    "total_variable_sets": 5,
    "total_projects": 2,
    "state_secrets_total_findings": 2,
    "state_secrets_workspaces_with_findings": 1
  }
}
```

## Features

### Automatic Pagination
Both scripts automatically handle API pagination by following `links.next` until all pages are fetched.

### Rate Limiting
Scripts detect rate limit errors (HTTP 429) and fail gracefully with informative messages. For large organizations, consider adding delays or using a higher rate limit token.

### Error Handling
- Authentication failures are detected immediately
- 403 errors indicate insufficient permissions
- 404 errors indicate endpoint not found (may need API version update)
- Network errors are caught and logged

### Cross-Platform
Python version works on any platform with Python 3.6+. Bash version works on macOS, Linux, and WSL.

## Token Permissions

The TFC_TOKEN must have **read access** to:
- ✅ Workspaces
- ✅ Runs
- ✅ State Versions (for secrets scanning)
- ✅ Registry Modules
- ✅ Policy Sets
- ✅ Teams
- ✅ Variable Sets
- ✅ Projects

**Recommended**: Use a Team token with organization-level read access. The token must have **state read** permission on workspaces to enable the state secrets check.

**Terraform Cloud**: Generate at `https://app.terraform.io/app/settings/tokens`

**Terraform Enterprise**: Generate at `https://tfe.example.com/app/settings/tokens`

## Data Obfuscation (Mode 2: SE-Assisted)

If you don't have access to a business-approved LLM to run the skill yourself, you can collect and obfuscate the data, then send it to your HashiCorp Sales Engineer for analysis.

### Why Obfuscation Is Safe

The obfuscation uses **one-way SHA-256 hashing** with a **random salt** generated fresh each time you run the script. The salt and the mapping file (`obfuscation_map.json`) **stay on your machine** — they are never included in the obfuscated output.

**Your HashiCorp SE cannot reverse the hashes.** Neither can anyone else who intercepts the file. Without the salt and the mapping, the hashed values are computationally irreversible. Even your SE will only see anonymised identifiers like `ws-a1b2c3d4e5f6` instead of your real workspace names. The only data visible in plain text are aggregate metrics (counts, percentages, Terraform versions, run statuses) — the numbers needed to perform the maturity assessment.

### Step 1: Collect Data

```bash
export TFC_TOKEN="your-team-token"
export TFC_ORG="your-organization"
export OUTPUT_DIR="./assessment"
python3 collect_tfc_data.py
```

### Step 2: Obfuscate

```bash
python3 obfuscate_data.py
```

This produces two files:

| File | Share? | Description |
|------|--------|-------------|
| `assessment/data_obfuscated.json` | ✅ **Send to your SE** | All business names replaced with SHA-256 hashes |
| `assessment/obfuscation_map.json` | ❌ **Keep private** | Maps hashes back to real names (needed for Step 4) |

### Step 3: SE Generates Reports

Your SE places `data_obfuscated.json` as `assessment/data.json` and runs the skill. The resulting `report.md` and `roadmap.md` will contain the obfuscated names. The SE sends these files back to you.

### Step 4: Deobfuscate Reports

Place `report.md` and `roadmap.md` from your SE into the `assessment/` directory alongside your `obfuscation_map.json`, then run:

```bash
python3 deobfuscate_report.py
```

Your reports now contain the real names from your organization.

### What Gets Obfuscated vs Preserved

**Obfuscated** (replaced with hashes — not readable by SE):
- Organization name
- Workspace names and IDs
- Module names and namespaces
- Team names and IDs
- Project names and IDs
- Policy set names and IDs
- Variable set names and IDs
- VCS repository identifiers
- Descriptions
- State secrets check: workspace names and IDs

**Preserved** (visible in plain text — needed for analysis):
- Terraform versions
- Execution modes, auto-apply, speculative plan settings
- Run statuses, sources, trigger reasons
- Module providers and version counts
- Policy/workspace/team counts
- Timestamps
- All aggregate metadata
- State secrets findings: pattern names, descriptions, attribute paths, finding counts, state size

## Troubleshooting

### Authentication Failed
```
ERROR: Unable to authenticate with TFC/TFE API
```
**Solution**: Verify TFC_TOKEN is valid and not expired. Generate a new token if needed.

### Insufficient Permissions
```
Error: 403 Forbidden on /organizations/{org}/policy-sets
```
**Solution**: Token needs organization-level read access. Use a Team token with appropriate permissions.

### Script Not Found
```
python3: command not found
```
**Solution**: Install Python 3.6+ or use the bash version instead.

### jq Not Found
```
jq: command not found
```
**Solution**: Install jq using your package manager (see Requirements above).

## Performance

Typical execution times:
- **Small org** (1-10 workspaces): 5-15 seconds
- **Medium org** (10-50 workspaces): 15-60 seconds
- **Large org** (50-500 workspaces): 1-5 minutes

For organizations with >500 workspaces, consider increasing the timeout or running during off-peak hours.

## Validation

These scripts have been validated against:
- ✅ `hashicorp-wwtfo-demo-platform-prod` (4 workspaces, 41 modules, 68 runs)
- ✅ Organizations with 0 policy sets (common initial state)
- ✅ Organizations with 100+ workspaces
- ✅ Both Terraform Cloud and Terraform Enterprise
- ✅ Various token permission levels

## Security Notes

- Never commit TFC_TOKEN to version control
- Store tokens in environment variables or secure credential stores
- Use Team tokens with least-privilege access (read-only for assessments)
- Rotate tokens regularly according to your security policy
- **State files are never written to disk** — they are streamed into memory, scanned for secrets, and immediately discarded. Only the scan findings (attribute paths and pattern names) are recorded in `data.json`; actual secret values are never logged or stored.

## Support

For issues or questions:
1. Check troubleshooting section above
2. Verify token permissions in TFC/TFE UI
3. Test with a smaller organization first
4. Check TFC/TFE API status page

## License

These scripts are provided as part of the TFC Practice Evaluator skill for HashiCorp Solutions Architects.
