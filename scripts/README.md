# TFC/TFE Data Collection Scripts

Production-ready scripts for collecting comprehensive organization data from Terraform Cloud or Terraform Enterprise APIs.

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

The scripts collect comprehensive data from 7 TFC/TFE API endpoints:

1. **Workspaces** - All workspaces with VCS, Terraform version, execution mode, etc.
2. **Runs** - Sample of recent runs (up to 20 runs from up to 10 workspaces)
3. **Registry Modules** - All private modules with version information
4. **Policy Sets** - All policy sets (Sentinel/OPA) with enforcement levels
5. **Teams** - All teams with user counts and permissions
6. **Variable Sets** - All variable sets with workspace attachments
7. **Projects** - All projects with descriptions

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
    "total_projects": 2
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
- ✅ Registry Modules
- ✅ Policy Sets
- ✅ Teams
- ✅ Variable Sets
- ✅ Projects

**Recommended**: Use a Team token with organization-level read access.

**Terraform Cloud**: Generate at `https://app.terraform.io/app/settings/tokens`

**Terraform Enterprise**: Generate at `https://tfe.example.com/app/settings/tokens`

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

## Support

For issues or questions:
1. Check troubleshooting section above
2. Verify token permissions in TFC/TFE UI
3. Test with a smaller organization first
4. Check TFC/TFE API status page

## License

These scripts are provided as part of the TFC Practice Evaluator skill for HashiCorp Solutions Architects.
