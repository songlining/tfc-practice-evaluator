---
name: tfc-practice-evaluator
description: Evaluate HCP Terraform (Terraform Cloud) or Terraform Enterprise organization adoption maturity against HashiCorp Validated Designs (HVD). Generates actionable recommendations for improving GitOps practices, module usage, policy enforcement, and team onboarding. Use when user says "evaluate my TFC", "evaluate my TFE", "TFC health check", "TFE health check", "TFC/TFE maturity assessment", "assess my Terraform Cloud", "assess my Terraform Enterprise", "how good is my TFC/TFE setup", or "TFC/TFE best practices review".
---

# TFC/TFE Practice Evaluator

## Overview

This skill evaluates a customer's HCP Terraform (Terraform Cloud) or Terraform Enterprise organization against HashiCorp Validated Designs (HVD) best practices. It produces a comprehensive maturity assessment with:

- **Overall maturity score** aligned to Adopt → Standardize → Scale stages
- **Category scores** for GitOps, Modules, Policies, Organization, and Operations
- **Gap analysis** identifying missing policies (including when custom development is needed)
- **Prioritized recommendations** with business value justification
- **Roadmap** for maturity progression

## Operating Modes

This skill supports **two operating modes** to accommodate customers with and without access to a business-approved LLM:

### Mode 1: Self-Service (Customer has LLM access)

The customer runs everything end-to-end on their own machine using their own LLM/agent:

```
Customer Environment:
  1. Set credentials (TFC_TOKEN, TFC_ORG)
  2. Run /tfc-practice-evaluator
  3. Skill collects data → analyzes → generates report.md + roadmap.md
  4. Done — all data stays in customer environment
```

### Mode 2: SE-Assisted (Customer has NO LLM access)

The customer collects data, obfuscates it, and sends it to the HashiCorp Sales Engineer (SE) for analysis:

```
Customer Environment:              SE Environment:
  1. Set credentials                  
  2. Run collect_tfc_data.py          
  3. Run obfuscate_data.py            
     ├─ data_obfuscated.json ──────► 4. SE receives obfuscated data
     └─ obfuscation_map.json          5. SE runs the skill analysis
        (KEEP PRIVATE)                6. SE sends back report.md + roadmap.md
                                         (with obfuscated names)
  7. Place report files in             
     assessment/ directory             
  8. Run deobfuscate_report.py         
     ├─ report.md (real names)         
     └─ roadmap.md (real names)        
  9. Done                              
```

**Privacy guarantee**: The obfuscation uses SHA-256 hashing with a random salt. The `obfuscation_map.json` (which maps hashes back to real names) never leaves the customer's environment. Even if a third party intercepts the obfuscated data, they cannot determine any business-specific information — only the aggregate metrics (counts, percentages, versions) are visible.

## Implementation

This skill includes **production-ready, battle-tested scripts** in the `scripts/` directory:

### Data Collection Scripts

**`scripts/collect_tfc_data.py`** (Recommended)
- Pure Python 3.6+ (no external dependencies)
- Uses only standard library: `urllib`, `json`, `os`, `datetime`
- ~300 lines, well-structured and maintainable
- Cross-platform (macOS, Linux, Windows)

**`scripts/collect_tfc_data.sh`**
- Bash + curl + jq
- ~250 lines
- Optimized for Unix-like systems
- Requires: `curl`, `jq`

### Data Privacy Scripts (Mode 2: SE-Assisted)

**`scripts/obfuscate_data.py`**
- Pure Python 3.6+ (no external dependencies)
- SHA-256 hashing with random salt for each session
- Obfuscates all business-identifiable names (workspaces, teams, modules, projects, policies, VCS repos, organization)
- Preserves metrics/counts (the data needed for analysis)
- Outputs: `data_obfuscated.json` (safe to share) + `obfuscation_map.json` (keep private)

**`scripts/deobfuscate_report.py`**
- Pure Python 3.6+ (no external dependencies)
- Replaces obfuscated tokens in report/roadmap files with real names
- Uses longest-match-first replacement to avoid partial substitutions
- Processes all `.md` files in the assessment directory

### DOCX Conversion Script (Optional)

**`scripts/convert_to_docx.py`**
- Converts `assessment/report.md` and `assessment/roadmap.md` to `.docx` format
- Professional formatting: cover page, page numbers, styled headings, tables
- Handles all Markdown features used in reports (headings, bold, italic, tables, lists, code blocks, blockquotes, links)
- **Requires**: `pip install python-docx` (the only external dependency in this skill)
- Cross-platform (macOS, Linux, Windows)

```bash
# Install dependency (one-time)
pip install python-docx

# Convert reports to DOCX
python3 scripts/convert_to_docx.py

# Or specify custom directories
python3 scripts/convert_to_docx.py --input-dir ./assessment --output-dir ./assessment
```

> **Note**: DOCX conversion is optional. The primary output format is Markdown (`.md`). Use this script when stakeholders require Word documents (e.g., for executive presentations, email attachments, or document management systems).

Both data collection scripts have been validated against production TFC organizations and handle:
- ✅ Pagination automatically (follows `links.next`)
- ✅ Rate limiting gracefully (fail-safe on 429 errors)
- ✅ Authentication validation
- ✅ Error conditions with proper logging
- ✅ Both TFC (app.terraform.io) and TFE endpoints
- ✅ Organizations with 0-500+ workspaces

### Script Output Format

Both scripts produce identical JSON structure at `assessment/data.json`:

```json
{
  "organization": "org-name",
  "collected_at": "2026-02-06T19:12:34Z",
  "workspaces": [...],
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

## CRITICAL EXECUTION RULES

⚠️ **USE PROVIDED SCRIPTS**: Use the working scripts in `scripts/` directory for data collection. They are production-ready and handle all edge cases.

⚠️ **SUB-AGENT ARCHITECTURE**: This skill MUST use sub-agents for data collection and analysis operations to keep the main agent's context clean and focused. The main agent orchestrates only.

⚠️ **NO MCP SERVERS**: Do NOT use any Model Context Protocol (MCP) servers during execution. Use only the provided scripts and native tools.

## Prerequisites

### Required Environment Variables

```bash
export TFC_TOKEN="your-team-token"    # TFC/TFE Team or User token
export TFC_ORG="your-organization"    # TFC/TFE organization name
export TFE_URL="https://tfe.example.com"  # TFE URL (optional, only for Terraform Enterprise)
```

**Note**: If you're using Terraform Cloud (app.terraform.io), you don't need to set `TFE_URL`. If any required variables are missing when running the skill, you will be prompted to provide them interactively.

### Token Permissions Required

The token needs **read access** to:
- Workspaces
- Runs  
- State Versions (for secrets scanning)
- Registry Modules
- Policy Sets
- Teams
- Variable Sets
- Projects

A **Team token** with organization-level read access is recommended. The token must have **state read** permission on workspaces to enable the state secrets check.

**For Terraform Enterprise**: Ensure your TFE instance is accessible and the token has the same organization-level read permissions.

### Required Tools

**Option 1: Python (Recommended)**
- Python 3.6+ (no external dependencies required)
- Uses standard library: `urllib`, `json`, `os`

**Option 2: Bash**
- `curl` - HTTP client for API calls
- `jq` - JSON processor (install via `brew install jq` or `apt install jq`)

⚠️ **Tool Restrictions**:
- USE: Provided scripts (`collect_tfc_data.py` or `collect_tfc_data.sh`)
- DO NOT USE: Any MCP servers (mcp_* tools) - they introduce unpredictable context pollution
- Reason: Production-validated scripts handle all edge cases (pagination, rate limits, errors)

## Quick Start

### Mode 1: Self-Service (Customer Has LLM Access)

#### For Terraform Cloud (HCP Terraform)

```bash
# 1. Set environment variables
export TFC_TOKEN="your-team-token"
export TFC_ORG="your-organization"
export OUTPUT_DIR="./assessment"

# 2. Invoke the skill
/tfc-practice-evaluator

# The skill will:
# - Validate prerequisites
# - Run scripts/collect_tfc_data.py (or .sh)
# - Spawn evaluation sub-agents
# - Generate report.md and roadmap.md
```

#### For Terraform Enterprise

```bash
# 1. Set environment variables
export TFC_TOKEN="your-team-token"
export TFC_ORG="your-organization"
export TFC_API_BASE="https://tfe.example.com/api/v2"
export OUTPUT_DIR="./assessment"

# 2. Invoke the skill
/tfc-practice-evaluator
```

#### Manual Script Execution (for testing)

```bash
# Python version
cd skills/tfc-practice-evaluator
export TFC_TOKEN="..." TFC_ORG="..." OUTPUT_DIR="../../assessment"
python3 scripts/collect_tfc_data.py

# Bash version
./scripts/collect_tfc_data.sh
```

**Interactive Mode**: If you don't set these variables beforehand, the skill will prompt you for the required information during execution.

### Mode 2: SE-Assisted (Customer Has No LLM Access)

#### Step A: Customer Collects & Obfuscates Data

```bash
# 1. Set environment variables
export TFC_TOKEN="your-team-token"
export TFC_ORG="your-organization"
export OUTPUT_DIR="./assessment"

# Optional: For Terraform Enterprise
export TFC_API_BASE="https://tfe.example.com/api/v2"

# 2. Collect data
cd skills/tfc-practice-evaluator
python3 scripts/collect_tfc_data.py

# 3. Obfuscate data (hashes all business names)
python3 scripts/obfuscate_data.py

# 4. Send ONLY data_obfuscated.json to your HashiCorp SE
#    KEEP obfuscation_map.json PRIVATE — do NOT share it
```

#### Step B: SE Runs Analysis

The SE places `data_obfuscated.json` as `assessment/data.json` and runs the skill (Mode 1) to generate `report.md` and `roadmap.md`. The SE sends these report files back to the customer.

#### Step C: Customer Deobfuscates Reports

```bash
# 1. Place report.md and roadmap.md from your SE into assessment/
# 2. Run deobfuscation (replaces hashed names with real names)
python3 scripts/deobfuscate_report.py

# 3. Open assessment/report.md and assessment/roadmap.md — they now contain your real names
```

## What Gets Evaluated

### 1. GitOps & VCS Maturity
- VCS integration percentage
- Speculative plan usage (PR-based workflow)
- VCS-triggered vs manual runs
- Auto-apply configuration
- Remote execution mode

### 2. Module Library (PMR)
- Private Module Registry module count
- Module versioning practices
- Module adoption across workspaces
- Provider coverage

### 3. Policy-as-Code
- Policy set count and coverage
- Enforcement level distribution
- Policy categories (security, cost, compliance)
- Policy check pass rates
- **Gap analysis**: Identifies when custom policies are needed

### 4. Organization & Teams
- Team structure and RBAC
- Project organization
- Variable set usage
- Workspace naming consistency

### 5. Operations & Health
- Run success rates
- Run frequency
- Terraform version hygiene
- Active workspace percentage

### 6. State Secrets Hygiene
- Scans each workspace's current Terraform state **on-the-fly** (state is never downloaded to disk)
- Detects leaked secrets: AWS keys, private keys, API tokens, passwords, database connection strings, GitHub/Slack tokens, bearer tokens
- Flags resource attributes with sensitive names (`password`, `secret_key`, `api_token`, etc.) that contain non-empty values
- Checks root module outputs for secret patterns
- Provides remediation advice per [HashiCorp sensitive data best practices](https://developer.hashicorp.com/terraform/language/manage-sensitive-data):
  - Mark variables and outputs as `sensitive = true` to redact from CLI/UI
  - Use `ephemeral = true` (Terraform 1.10+) to omit values from state entirely
  - Use write-only arguments (`_wo` suffix, Terraform 1.11+) to pass secrets without persisting
  - Store state remotely with encryption at rest (HCP Terraform, S3 with `encrypt`, GCS with KMS)
  - Rotate any credentials found in state immediately

## Execution Flow

> The execution flow below applies to **Mode 1 (Self-Service)** and to the SE's side in **Mode 2 (SE-Assisted)**. In Mode 2, the SE receives `data_obfuscated.json` and treats it as `assessment/data.json` — the rest of the flow is identical.

### Step 1: Prerequisite Validation (Main Agent)

**Main agent performs ONLY**:
- Check if `TFC_TOKEN` is set, prompt if missing
- Check if `TFC_ORG` is set, prompt if missing
- Check if `TFE_URL` is set for TFE, prompt if missing
- Create `assessment/` directory
- Store credentials in environment for sub-agents

**DO NOT** perform API calls or validation tests in the main agent.

### Step 2: Data Collection (Sub-Agent Required)

🤖 **SPAWN SUB-AGENT**: `data-collector-agent`

**Task**: "Use the working script at scripts/collect_tfc_data.py to collect TFC/TFE organization data. The script handles authentication, pagination, rate limiting, and saves to assessment/data.json."

**Sub-agent execution**:

```bash
cd /path/to/skills/tfc-practice-evaluator
export TFC_TOKEN="$TFC_TOKEN"
export TFC_ORG="$TFC_ORG"
export TFC_API_BASE="$TFC_API_BASE"
export OUTPUT_DIR="../../assessment"

# Run the production-validated script
python3 scripts/collect_tfc_data.py
```

**The script automatically**:
- Determines API base URL (TFC vs TFE from TFC_API_BASE)
- Tests authentication
- Fetches all required endpoints with pagination:
  - `/organizations/{org}/workspaces`
  - `/workspaces/{id}/runs` (sampled from up to 10 workspaces)
  - `/workspaces/{id}/current-state-version` → `hosted-state-download-url` (all workspaces, streamed in memory, never saved to disk)
  - `/organizations/{org}/registry-modules`
  - `/organizations/{org}/policy-sets`
  - `/organizations/{org}/teams`
  - `/organizations/{org}/varsets`
  - `/organizations/{org}/projects`
- Scans each workspace state for leaked secrets on-the-fly
- Handles rate limiting gracefully
- Saves consolidated output to `assessment/data.json` (state file contents are **never** included — only the scan findings)

**API Base URL Defaults**:
- Terraform Cloud: `https://app.terraform.io/api/v2` (default)
- Terraform Enterprise: `https://{TFE_URL}/api/v2` (set via TFC_API_BASE)

**Main agent waits** for `assessment/data.json` to be created, then proceeds to research and evaluation.

### Step 2.5: Platform Research (Sub-Agent Required)

🤖 **SPAWN SUB-AGENT**: `platform-research-agent`

**Task**: "Research the latest HCP Terraform platform features, HVD Operating Guide documents, and module lifecycle best practices. Use web search tools to gather current information. Output structured JSON to assessment/platform-research.json."

**Why this step exists**: Platform features evolve rapidly (e.g., Stacks GA'd in 2025, Actions GA'd in Dec 2025, Search GA'd in Terraform 1.14). Hardcoded feature status becomes stale. This agent ensures every assessment uses **current** information.

**Sub-agent execution**:

The `platform-research-agent` MUST use web search tools (e.g., `websearch`, `webfetch`) to research the following topics and return structured JSON:

**Research Topics:**

1. **HVD Operating Guides** — Search `developer.hashicorp.com/validated-designs` for:
   - Current Terraform Operating Guide titles and URLs (Adoption, Standardization, Scaling)
   - Whether any new Terraform HVD guides have been published
   - Current status labels (e.g., "(Beta)" suffix on Scaling guide)

2. **Platform Feature Availability** — For each feature, search for current GA/Beta/Preview status:
   - **Terraform Stacks**: Multi-deployment orchestration. Search: `"Terraform Stacks" GA release site:hashicorp.com`
   - **Terraform Search**: Discover & bulk-import unmanaged resources. Search: `"Terraform search" GA "Terraform 1.14" site:hashicorp.com`
   - **Terraform Actions**: Day 2 operations (Ansible, Lambda). Search: `"Terraform actions" GA "Day 2" site:hashicorp.com`
   - **Terraform MCP Server**: AI-assisted Terraform workflows. Search: `"Terraform MCP server" beta OR GA site:hashicorp.com`
   - **Any new features announced** at recent HashiConf or blog posts

3. **Module Lifecycle Features** — Search `developer.hashicorp.com/terraform/cloud-docs/registry` for:
   - Module deprecation and revocation availability (which HCP Terraform editions?)
   - Test-integrated module publishing status
   - Explorer feature capabilities

4. **Latest Terraform CLI Version** — Search for the latest stable Terraform CLI release version

**Expected Output** (`assessment/platform-research.json`):

```json
{
  "research_timestamp": "2026-02-09T10:00:00Z",
  "research_quality": "full|partial|fallback",
  "hvd_guides": {
    "adoption": {"title": "Terraform: Operating Guide for Adoption", "url": "https://...", "status": "GA"},
    "standardization": {"title": "Terraform: Operating Guide for Standardization", "url": "https://...", "status": "GA"},
    "scaling": {"title": "Terraform: Operating Guide for Scaling", "url": "https://...", "status": "Beta"},
    "solution_design": {"title": "Terraform: Solution Design Guide", "url": "https://...", "status": "GA"}
  },
  "platform_features": {
    "stacks": {"name": "Terraform Stacks", "status": "GA|Beta|Preview", "description": "...", "doc_url": "https://...", "min_terraform_version": null},
    "search": {"name": "Terraform Search", "status": "GA|Beta|Preview", "description": "...", "doc_url": "https://...", "min_terraform_version": "1.14"},
    "actions": {"name": "Terraform Actions", "status": "GA|Beta|Preview", "description": "...", "doc_url": "https://...", "min_terraform_version": "1.14"},
    "mcp_server": {"name": "Terraform MCP Server", "status": "GA|Beta|Preview", "description": "...", "doc_url": "https://...", "min_terraform_version": null}
  },
  "module_lifecycle": {
    "deprecation": {"available": true, "edition": "Standard+", "doc_url": "https://..."},
    "revocation": {"available": true, "edition": "Premium", "doc_url": "https://..."},
    "test_integrated_publishing": {"available": true, "doc_url": "https://..."},
    "explorer": {"available": true, "doc_url": "https://..."}
  },
  "latest_terraform_version": "1.14.x"
}
```

**Fallback behavior**: If web search is unavailable or returns poor results, the agent MUST still return valid JSON with `"research_quality": "fallback"` using these known-good defaults:
- HVD Adoption: `https://developer.hashicorp.com/validated-designs/terraform-operating-guides-adoption`
- HVD Standardization: `https://developer.hashicorp.com/validated-designs/terraform-operating-guides-standardization`
- HVD Scaling: `https://developer.hashicorp.com/validated-designs/terraform-operating-guides-scaling`
- Stacks docs: `https://developer.hashicorp.com/terraform/cloud-docs/stacks`
- Search docs: `https://developer.hashicorp.com/terraform/cloud-docs/workspaces/import`
- Actions docs: `https://developer.hashicorp.com/terraform/language/invoke-actions`
- MCP Server docs: `https://developer.hashicorp.com/terraform/mcp-server`

**Main agent** waits for `assessment/platform-research.json`, then proceeds to evaluation.

### Step 3: Analysis (Multiple Sub-Agents)

🤖 **SPAWN 6 PARALLEL SUB-AGENTS** (each analyzes one category):

1. **`gitops-evaluator-agent`**: Read `assessment/data.json` and `assessment/platform-research.json`. Analyze VCS integration metrics, calculate GitOps score using the scoring rubric defined in the Scoring Model section below. Additionally:
   - Check for automation opportunities: if low VCS-triggered run % but high API-triggered runs, recommend evaluating **Terraform Actions** for Day 2 operations (status from platform research)
   - If low VCS integration %, recommend **Terraform Search** for discovering and bulk-importing unmanaged resources (status from platform research)
   - If multi-environment patterns detected (prod/staging/dev workspace naming, project-based environment separation), note as a candidate for **Terraform Stacks** evaluation
   - Return JSON with score, findings, and `feature_opportunities` array

2. **`pmr-evaluator-agent`**: Read `assessment/data.json` and `assessment/platform-research.json`. Analyze module library metrics, calculate PMR score. Additionally:
   - **Operating Model Detection**: Determine if the organization follows a **Service Catalog** or **Infrastructure Franchise** pattern based on:
     - High module count relative to workspaces + centralized team structure → Service Catalog
     - Distributed teams + diverse providers + policy guardrails → Infrastructure Franchise
   - **Module Lifecycle Assessment**: Using platform research data, evaluate:
     - Module deprecation/revocation practices (are retired modules deprecated or just abandoned?)
     - Publishing workflow (branch-based with PMR tests vs tag-based with VCS pipelines)
     - Version constraint practices (are consumers using pessimistic constraints `~>`?)
     - Module update automation (Renovate/Dependabot configured?)
   - **Explorer Usage**: Check if Explorer is being used for module usage visibility
   - Return JSON with score, findings, `operating_model` classification, and `module_lifecycle` assessment

3. **`policy-evaluator-agent`**: Read `assessment/data.json`, analyze policy coverage using the Policy Gap Handling section below, identify gaps (including custom policy needs), calculate Policy score, return JSON with score, findings, and gap analysis.

4. **`org-evaluator-agent`**: Read `assessment/data.json`, analyze team structure and organization, calculate Org score, return JSON with score and findings.

5. **`ops-evaluator-agent`**: Read `assessment/data.json`, analyze run health and operations, calculate Ops score, return JSON with score and findings.

6. **`state-secrets-evaluator-agent`**: Read `assessment/data.json` `state_secrets_check` section, summarise findings per workspace, calculate State Secrets score (0 findings = perfect, any finding = critical), provide remediation recommendations referencing https://developer.hashicorp.com/terraform/language/manage-sensitive-data, return JSON with score, findings, and remediation plan.

**Main agent** collects all 6 results and consolidates into overall scores.

### Step 4: Report Synthesis (Sub-Agent Required)

🤖 **SPAWN SUB-AGENT**: `report-synthesizer-agent`

**Task**: "Generate comprehensive assessment report from all evaluation results AND `assessment/platform-research.json`. Create executive summary, category breakdowns, prioritized recommendations, and roadmap. Output to assessment/report.md and assessment/roadmap.md."

**The report MUST include these sections** (in addition to standard category scores and recommendations):

1. **HVD Document Citations**: Reference specific HVD Operating Guide titles by name in recommendations (e.g., "As described in the *Terraform: Operating Guide for Standardization*, module versioning should follow..."). Use URLs from `platform-research.json`.

2. **Operating Model Analysis**: Based on `pmr-evaluator-agent`'s `operating_model` classification, include a section explaining whether the organization follows a **Service Catalog** or **Infrastructure Franchise** pattern, with this comparison table:

   | Dimension | Service Catalog | Infrastructure Franchise |
   |-----------|----------------|--------------------------|
   | Primary UX | Vending portal (UI, ServiceNow, etc.) | Custom workflow (Git, API/CLI, CI/CD, etc.) |
   | What can be built? | Standard modules only | Anything via IaC within defined guardrails |
   | Customization | Limited (via module parameters) | Unlimited (within policy guardrails) |
   | Primary security model | Validated modules | Guardrails (policy-as-code, etc.) |
   | Target persona | Any — including business users, PMs | Development teams, SRE, etc. |

3. **Platform Feature Opportunities**: Based on `gitops-evaluator-agent`'s `feature_opportunities` and platform research data, recommend relevant features with their current status (GA/Beta/Preview). Only include features whose status is GA or Beta. Include doc URLs from research.

4. **Module Lifecycle & Publishing Recommendations**: Based on `pmr-evaluator-agent`'s `module_lifecycle` assessment:
   - Deprecation/revocation workflow recommendations
   - Publishing workflow improvements (branch-based vs tag-based)
   - Version constraint best practices (pessimistic constraints `~>`)
   - Automated update tooling (Renovate/Dependabot)
   - Explorer for module usage visibility
   - Workspace notifications for run events

**Main agent** confirms report generation and displays summary to user.

### Step 5: DOCX Conversion (Optional — Main Agent)

**After report synthesis**, the main agent checks if `python-docx` is available and offers DOCX conversion:

```bash
# Check if python-docx is installed
python3 -c "import docx" 2>/dev/null && echo "available" || echo "unavailable"
```

- If **available**: Run `python3 scripts/convert_to_docx.py` to generate `assessment/report.docx` and `assessment/roadmap.docx`
- If **unavailable**: Inform user that DOCX conversion is available by installing `python-docx`: `pip install python-docx`

This step is non-blocking — the assessment is complete regardless of DOCX conversion.

### Step 6: Completion (Main Agent)

Main agent provides user with:
- Overall maturity score
- Link to `assessment/report.md` (and `assessment/report.docx` if generated)
- Link to `assessment/roadmap.md` (and `assessment/roadmap.docx` if generated)
- Top 3 recommendations

Main agent context remains clean throughout - only orchestration and summary.

## Sub-Agent Architecture

⚠️ **MANDATORY**: This skill MUST use sub-agents. The main agent is an orchestrator only.

### Why Sub-Agents Are Required

1. **Context Management**: API responses can be 10-50KB per endpoint (e.g., 87KB data.json for 4 workspaces). Without sub-agents, the main agent's context would be polluted with raw JSON data.
2. **Parallel Processing**: Multiple evaluation categories can be analyzed simultaneously (6 parallel evaluations: GitOps, PMR, Policy, Org, Ops, State Secrets).
3. **Isolation**: Each sub-agent has a focused task and clean context.
4. **Error Recovery**: If one sub-agent fails, others can continue.
5. **Proven Performance**: Successfully evaluated production organizations (e.g., 4 workspaces, 41 modules, 68 runs) in ~10 minutes with 8 parallel sub-agents.

### Sub-Agent Execution Order

```
Main Agent (Orchestrator)
    ↓
    ├─ [Step 1] Validate prerequisites (credentials, directory setup)
    ↓
    ├─ [Step 2] SPAWN → data-collector-agent
    │           └─ Fetches all API data + scans states for secrets → assessment/data.json
    ↓
    ├─ [Step 2.5] SPAWN → platform-research-agent
    │             └─ Researches latest HVD docs, platform features, module lifecycle
    │                 → assessment/platform-research.json
    ↓
    ├─ [Step 3] SPAWN (6 parallel) → evaluation agents
    │           ├─ gitops-evaluator-agent  (reads data.json + platform-research.json)
    │           ├─ pmr-evaluator-agent     (reads data.json + platform-research.json)
    │           ├─ policy-evaluator-agent
    │           ├─ org-evaluator-agent
    │           ├─ ops-evaluator-agent
    │           └─ state-secrets-evaluator-agent
    │           └─ All return JSON with scores/findings
    ↓
    ├─ [Step 4] SPAWN → report-synthesizer-agent
    │           └─ Reads all evals + platform-research.json → final reports
    ↓
    ├─ [Step 5] (Optional) Convert .md → .docx if python-docx available
    ↓
    └─ [Step 6] Display summary to user
```

### Sub-Agent Definitions

| Sub-Agent | Spawned By | Input | Output | Tools |
|-----------|------------|-------|--------|-------|
| `data-collector-agent` | Main | Credentials, API URL | `assessment/data.json` | curl, jq |
| `platform-research-agent` | Main | Web search queries | `assessment/platform-research.json` | websearch, webfetch |
| `gitops-evaluator-agent` | Main | `data.json`, `platform-research.json` | JSON: score + findings + feature_opportunities | read_file |
| `pmr-evaluator-agent` | Main | `data.json`, `platform-research.json` | JSON: score + findings + operating_model + module_lifecycle | read_file |
| `policy-evaluator-agent` | Main | `data.json` | JSON: score + gap analysis | read_file |
| `org-evaluator-agent` | Main | `data.json` | JSON: score + findings | read_file |
| `ops-evaluator-agent` | Main | `data.json` | JSON: score + findings | read_file |
| `state-secrets-evaluator-agent` | Main | `data.json` (`state_secrets_check`) | JSON: score + findings + remediation | read_file |
| `report-synthesizer-agent` | Main | All evaluation results, `platform-research.json` | `report.md`, `roadmap.md` | create_file |

### Sub-Agent Communication Protocol

**Main → Sub-Agent**:
- Provide clear, single-purpose task description
- Specify input file locations
- Specify exact output format (JSON, Markdown, etc.)
- Set clear success criteria

**Sub-Agent → Main**:
- Sub-agents return ONLY structured output (JSON or file paths)
- No verbose explanations in sub-agent responses
- Main agent parses and consolidates

### Example Sub-Agent Spawn

```
Main Agent: runSubagent(
  prompt: "Read assessment/data.json. Count workspaces with vcs_repo configured. Calculate percentage. Using the scoring rubric from the Scoring Model section of SKILL.md, evaluate VCS Integration criterion and return JSON: {score: X, findings: ['...']}. Use ONLY read_file - NO MCP servers.",
  description: "GitOps Evaluation"
)
```

## Scoring Model

### Category Weights

| Category | Weight | Primary Stage |
|----------|--------|---------------|
| GitOps & VCS | 25% | Adopt |
| Module Library | 20% | Standardize |
| Policy-as-Code | 25% | Scale |
| Organization | 15% | All |
| Operations | 15% | All |

**State Secrets Hygiene** is evaluated as a **critical overlay** rather than a weighted category. Any findings act as a maturity cap:

| State Secrets Findings | Impact |
|------------------------|--------|
| 0 findings | No impact — full score applies |
| 1-5 findings | Warning flag in report; Operations score capped at 70% |
| 6+ findings | Critical flag; Operations score capped at 50%; overall maturity capped at "Adopting" |

This ensures that leaked secrets in state are treated as a blocking issue regardless of how well other categories score.

### Score Interpretation

| Score | Maturity Level | Stage |
|-------|----------------|-------|
| 0-25 | Early | Pre-Adopt |
| 26-45 | Adopting | Adopt |
| 46-60 | Adopted | Adopt Complete |
| 61-75 | Standardizing | Standardize |
| 76-85 | Standardized | Standardize Complete |
| 86-95 | Scaling | Scale |
| 96-100 | Mature | Scale Complete |

## Policy Gap Handling

### Registry Policies Available

The skill checks for adoption of available registry policies:
- AWS CIS Benchmarks (`hashicorp/cis-policy-set-aws`)
- Azure CIS Benchmarks (`hashicorp/cis-policy-set-azure`)
- GCP CIS Benchmarks (`hashicorp/cis-policy-set-gcp`)
- Cloud Foundational policies

### Custom Policy Flags

When customer needs are NOT covered by registry, the report flags:

```markdown
## Custom Policy Development Needed

| Gap | Reason | Priority | Estimated Effort |
|-----|--------|----------|------------------|
| HIPAA Compliance | Healthcare industry, no registry policy | High | 2-4 weeks |
| Australian ISM | Government requirement, no registry policy | High | 2-4 weeks |
| FedRAMP | US Government requirement, no registry policy | High | 2-4 weeks |
| GDPR | European data protection, no registry policy | High | 2-4 weeks |
| PCI-DSS | Financial services, no registry policy | High | 2-4 weeks |
| FinOps Cost Controls | No cost policies in registry | Medium | 1-2 weeks |
| Custom Tagging Schema | Organization-specific requirements | Medium | 1 week |
```

## Lessons Learned from Production Use

Based on successful evaluations of production TFC organizations, here are critical insights:

### 1. Token Security & Handling

**What Worked:**
- ✅ Collect credentials interactively using `AskUserQuestion` tool
- ✅ Store credentials in environment variables for sub-agent access
- ✅ Never write tokens to files or logs

**Pattern:**
```
Main Agent → AskUserQuestion (collects token) → Environment variable → Sub-agents inherit
```

**Never:**
- ❌ Hardcode tokens in scripts
- ❌ Pass tokens as command-line arguments (visible in `ps`)
- ❌ Write tokens to temporary files
- ❌ Include tokens in error messages or logs

### 2. Execution Time Breakdown

**Measured Performance (4 workspaces, 41 modules):**
- Data collection: **~30 seconds** (Python script)
- Platform research: **~1-2 minutes** (web search for latest HVD docs, features, module lifecycle)
- Parallel evaluations: **~5 minutes** (6 agents: GitOps, PMR, Policy, Org, Ops, State Secrets)
- Report synthesis: **~3 minutes** (1 agent: consolidation + writing)
- **Total: ~10 minutes**

**Scaling Estimates:**
- 10 workspaces: ~12 minutes
- 50 workspaces: ~17 minutes
- 100+ workspaces: ~25-35 minutes

**Bottlenecks:**
- Run sampling (20 runs × 10 workspaces = 200 API calls)
- Policy evaluation with extensive gap analysis
- Report synthesis (largest output files)

### 3. Common Organizational Patterns

**Zero Policy Sets is NORMAL:**
- 70%+ of TFC orgs have 0 policy sets initially
- Don't treat this as an error—it's the primary opportunity
- Frame as "greenfield opportunity for governance"

**API-Driven Architecture:**
- Many orgs have 100% VCS integration but 0% VCS-triggered runs
- This indicates external CI/CD orchestration (GitHub Actions, Jenkins, etc.)
- Not a failure—it's an architectural choice worth understanding

**Module Versioning Signals Maturity:**
- Average versions per module is a leading indicator
- <2 versions = modules are new or unused
- 5-10 versions = active maintenance
- 15+ versions = intensive development practice (demo platforms, shared libraries)

**Variable Sets Often Unconfigured:**
- Many orgs create variable sets but never attach them to workspaces
- Check `workspace_count` in variable set data
- Flag as "quick win" opportunity

### 4. Localization & Compliance Context (Critical!)

**Every region has unique compliance requirements.** This skill should be adapted to local regulatory frameworks.

**Example: Australian Region** (use as localization template for other regions)

When evaluating for Australian customers, check for:

**Compliance Requirements:**
- Government/Defense → Australian ISM Essential Eight
- Financial Services → APRA CPS 234, PCI DSS
- Healthcare → Privacy Act 1988, My Health Records Act
- All → Data sovereignty (ap-southeast-2 residency)

**Customer-Specific Pattern:**
| Customer Type | Compliance | Priority Policy Gaps |
|---------------|------------|---------------------|
| Government Agencies | ISM, Government | Data residency, encryption at rest, audit logging |
| Financial Institutions | APRA CPS 234 | DR validation, change management, incident response |
| Large Enterprises | FinOps | Cost controls, tagging standards, unused resource detection |
| All Customers | Data Sovereignty | Region restrictions (ap-southeast-2 only) |

**Report Customization:**
- Use Australian terminology (e.g., "Defence" not "Defense")
- Reference ACSC, APRA, OAIC (not NIST, FedRAMP)
- Provide effort estimates in AUD (not USD)
- Consider AEST/AEDT time zones for implementation windows

---

**Adapting for Other Regions:**

Use the Australian example above as a template. Replace with local equivalents:

| Region | Compliance Frameworks | Cloud Regions | Regulators |
|--------|----------------------|---------------|------------|
| **US** | FedRAMP, NIST, HIPAA, SOC 2 | us-east-1, us-gov-west-1 | NIST, FedRAMP PMO |
| **EU** | GDPR, NIS2, DORA, C5 | eu-west-1, eu-central-1 | ENISA, National regulators |
| **UK** | NCSC Cyber Essentials, FCA | eu-west-2 (London) | NCSC, FCA |
| **Singapore** | PDPA, MTCS | ap-southeast-1 | IMDA, MAS |
| **Canada** | PIPEDA, Provincial laws | ca-central-1 | OPC |

**Localization Steps:**
1. **Research customer's industry** → Find industry-specific regulators
2. **Identify geographic location** → Research data sovereignty laws
3. **Check existing compliance programs** → Ask what they're certified for
4. **Review cloud footprint** → Which regions are they deploying to?
5. **Consult local HashiCorp teams** → Local SAs know regional requirements

### 5. Sub-Agent Prompt Patterns That Work

**Effective Sub-Agent Prompts Include:**

1. **Clear Input Specification:**
   ```
   "Read assessment/data.json which contains {specific structure}"
   ```

2. **Explicit Scoring Rubric:**
   ```
   "Score using these criteria:
   - VCS Integration: 100% = 10 pts, 80%+ = 8 pts, <60% = 4 pts"
   ```

3. **Exact Output Format:**
   ```
   "Return JSON: {score: X, findings: [...], stage: '...'}"
   ```

4. **Tool Restrictions:**
   ```
   "Use ONLY read_file - NO MCP servers, NO API calls"
   ```

5. **Success Criteria:**
   ```
   "Complete when: JSON file created at assessment/gitops-eval.json"
   ```

**Example Effective Prompt:**
```
Read assessment/data.json. Count workspaces with vcs_repo configured.
Calculate percentage. Using these criteria:
- 100% VCS integration = 10/10 points
- 80-99% = 8/10 points
- 60-79% = 6/10 points
- <60% = 4/10 points

Return JSON:
{
  "score": X,
  "findings": ["...", "..."],
  "stage": "Adopt|Standardize|Scale"
}

Save to assessment/gitops-eval.json. Use ONLY read_file - NO MCP servers.
```

### 6. Error Handling Patterns

**Common Issues and Solutions:**

**Issue:** `workspace_count: null` in API response
**Solution:** Default to 0 or calculate from relationships data

**Issue:** Organizations with 0 workspaces
**Solution:** Skip run sampling, still evaluate PMR/policies/teams

**Issue:** Rate limiting (HTTP 429)
**Solution:** Fail gracefully with informative message (don't retry indefinitely)

**Issue:** Missing TFC_TOKEN on script execution
**Solution:** Validate in Python script `validate_config()`, exit early with clear error

**Issue:** macOS-specific bash syntax (`head -n -1`)
**Solution:** Use Python version (cross-platform) or test bash on macOS first

### 7. Output Validation Checkpoints

**After Data Collection:**
- ✅ `assessment/data.json` exists and is >10 KB
- ✅ `metadata.total_workspaces` matches expected count
- ✅ At least one category has data (modules OR workspaces OR teams)

**After Platform Research:**
- ✅ `assessment/platform-research.json` exists and is valid JSON
- ✅ `research_quality` field is present (`full`, `partial`, or `fallback`)
- ✅ `hvd_guides` object has at least `adoption` and `standardization` entries
- ✅ `platform_features` object has at least `stacks`, `search`, `actions` entries

**After Evaluations:**
- ✅ 6 evaluation JSON files exist (gitops, pmr, policy, org, ops, state-secrets)
- ✅ Each has a `score` field (numeric)
- ✅ Policy evaluation includes `gap_analysis` object
- ✅ State secrets evaluation includes `findings` array and `remediation` recommendations

**After Report Synthesis:**
- ✅ `report.md` is >20 KB (comprehensive content)
- ✅ `roadmap.md` is >30 KB (detailed implementation plan)
- ✅ Overall score is 0-100 (not null)

**After DOCX Conversion (optional):**
- ✅ `report.docx` exists if `python-docx` was available
- ✅ `roadmap.docx` exists if `python-docx` was available
- ✅ DOCX files open correctly in Word/Google Docs/LibreOffice

### 8. Demo Platform Insights

**If evaluating a demo/sandbox platform:**

**Expect:**
- High module count (41+ modules for demos)
- High versioning (15+ avg versions)
- Low workspace count (3-5 workspaces)
- Zero policy sets (demos focus on features, not governance)
- API-driven runs (automated testing/demos)

**Opportunity:**
- Position as "governance showcase opportunity"
- Recommend: "Your demo platform should demonstrate TFC governance capabilities to customers"
- Frame: "Add policies to show Australian compliance automation (ISM, APRA)"

**Don't:**
- Criticize low workspace count (it's a demo, not production)
- Expect production-grade RBAC (demos often have single team)
- Flag API-driven architecture as a problem (intentional for automation)

### 9. Data Obfuscation Details (Mode 2)

**What Gets Obfuscated** (business-identifiable information):

| Field | Example Original | Example Obfuscated |
|-------|------------------|-------------------|
| Organization name | `acme-corp-prod` | `org-a1b2c3d4e5f6` |
| Workspace names | `aws-networking-prod` | `ws-f7e8d9c0b1a2` |
| Workspace IDs | `ws-AbCdEf123456` | `wsid-1a2b3c4d5e6f` |
| Module names | `terraform-aws-vpc` | `mod-b3c4d5e6f7a8` |
| Team names | `platform-engineering` | `team-c5d6e7f8a9b0` |
| Project names | `infrastructure` | `proj-d7e8f9a0b1c2` |
| Policy set names | `aws-cis-benchmarks` | `ps-e9f0a1b2c3d4` |
| Variable set names | `aws-credentials` | `vs-f1a2b3c4d5e6` |
| VCS repo identifiers | `acme/infra-modules` | `repo-a3b4c5d6e7f8` |
| Descriptions | `Production VPC module` | `desc-b5c6d7e8f9a0` |

**What Gets Preserved** (metrics needed for analysis):

| Field | Reason |
|-------|--------|
| `terraform_version` | Version hygiene analysis |
| `execution_mode` | GitOps maturity scoring |
| `auto_apply` | Workflow pattern analysis |
| `speculative_enabled` | PR workflow analysis |
| `updated_at` | Activity/staleness detection |
| `locked` | Operational health |
| Run `status`, `source`, `trigger_reason` | Run pattern analysis |
| Module `provider`, `version_statuses` | Module maturity scoring |
| Policy `policy_count`, `workspace_count`, `global`, `kind` | Policy coverage analysis |
| Team `users_count`, `organization_access`, `visibility` | RBAC analysis |
| Variable set `global`, `priority`, `workspace_count` | Configuration management analysis |
| All `metadata` counts | Summary statistics |
| State secrets `findings` (pattern names, descriptions, attribute paths) | Security analysis — technical patterns, not business names |
| State secrets `findings_count`, `has_state`, `state_size_bytes` | Aggregate metrics |

**Security Properties:**
- SHA-256 hashing with a per-session random salt
- Same name always maps to the same hash within a session (deterministic for consistency)
- Different sessions produce different hashes (salt changes)
- The `obfuscation_map.json` never leaves the customer environment
- Even with the obfuscated data, an attacker cannot reverse the hashes without the salt

### 10. Report Tailoring Strategies

**For Sales/Pre-Sales:**
- Lead with business value (cost savings, audit time reduction)
- Use customer-specific examples (name their industry)
- Include competitive context ("Industry leaders have...")
- Provide TCO/ROI estimates

**For Post-Sales/Technical:**
- Lead with technical gaps (policy gaps, RBAC structure)
- Provide implementation scripts/examples
- Include terraform code snippets for quick wins
- Offer office hours for complex gaps (ISM, APRA policies)

**For Executive Stakeholders:**
- One-page executive summary (overall score + top 3 priorities)
- Visual maturity model (current → target state)
- Risk framing (compliance gaps, audit findings)
- Investment required (time, budget, resources)

### 11. Quick Wins to Always Recommend

Regardless of organization maturity, these are **always** actionable:

1. **Adopt AWS CIS Benchmarks** (2-4 hours, high impact)
   - Available in registry
   - Advisory mode first (no blocking)
   - Immediate security baseline

2. **Enable Speculative Plans** (1-2 hours, high impact)
   - If VCS integrated but speculative_enabled=false
   - Enables PR-based review workflow
   - Zero cost, high value

3. **Attach Existing Variable Sets** (1-2 hours, medium impact)
   - If variable sets exist but workspace_count=0
   - Quick configuration management win
   - Shows immediate value

4. **Create RBAC Teams** (4-8 hours, medium impact)
   - If only 1 team exists
   - Admin / Developer / Viewer separation
   - Foundation for scaling

5. **Implement Tagging Standards** (1 week, high impact)
   - Custom policy (not in registry)
   - Enables cost allocation
   - Required for FinOps maturity

6. **Enable Terraform Search for Resource Inventory** (1-2 hours, medium impact)
   - Requires Terraform 1.14+ — check current version hygiene
   - Discovers unmanaged resources across cloud accounts
   - Enables bulk import into Terraform management
   - Zero cost if already on compatible version

7. **Evaluate Terraform Stacks for Multi-Environment Deployments** (4-8 hours assessment, high impact)
   - If multi-environment patterns detected (prod/staging/dev workspace naming)
   - Reduces workspace sprawl with coordinated multi-deployment orchestration
   - GA feature — production ready

8. **Implement Module Deprecation for Retired Modules** (1-2 hours, medium impact)
   - If unused/abandoned modules detected in PMR
   - Mark as deprecated (Standard edition) to warn consumers
   - Prevents teams from adopting outdated modules

9. **Connect Terraform MCP Server to AI Coding Assistant** (1-2 hours, low impact)
   - ⚠️ Beta feature — evaluate for non-production use first
   - Enables AI-assisted Terraform workflows (plan, apply, module search)
   - Developer experience improvement for teams using AI coding tools

## Proven Results

This skill has been successfully validated against real TFC organizations:

**Test Case: Internal Demo Platform**
- Organization Size: 4 workspaces, 41 private modules, 68 runs sampled
- Data Collection: 87 KB `data.json` generated in ~30 seconds
- Evaluation: 6 parallel sub-agents completed in ~10 minutes
- Output: 39 KB `report.md`, 49 KB `roadmap.md`
- Results:
  - Overall Score: 60.5/100 (Adopting → Standardizing)
  - Category Scores:
    - PMR: 37/40 (92.5%) - Standardized
    - GitOps: 42/50 (84%) - Standardizing
    - Operations: 31/40 (77.5%) - Strong
    - Organization: 22/40 (55%) - Adopting
    - **Policy: 2/40 (5%) - Critical Gap Identified**
  - Gap Analysis: Identified 6 available registry policies + 13 custom policy requirements
  - Roadmap: 6-month implementation plan with prioritized recommendations

**Key Insights Discovered:**
- Exceptional module versioning (16.76 avg versions per module)
- 100% VCS integration but 0% VCS-triggered runs (API-driven architecture)
- Zero policy sets deployed (major opportunity for governance)
- Regional compliance requirements (ISM, APRA CPS 234) flagged for custom development

This real-world validation proves the skill can handle production TFC organizations and deliver actionable, business-aligned recommendations for enterprise customers across all regions and industries.

## Example Report Output

```markdown
# TFC Maturity Assessment: Acme Corp

## Executive Summary

| Metric | Value |
|--------|-------|
| **Overall Score** | 58/100 |
| **Maturity Level** | Standardizing |
| **Current Stage** | Transitioning from Adopt to Standardize |

### Top Strengths
1. ✅ 85% VCS integration
2. ✅ Active team structure with 5 teams
3. ✅ Consistent workspace naming

### Top Improvement Areas
1. ⚠️ No Sentinel policies configured
2. ⚠️ Only 2 modules in PMR
3. ⚠️ 35% stale workspaces (no runs in 90 days)

## Category Scores

| Category | Score | Level |
|----------|-------|-------|
| GitOps & VCS | 72/100 | Standardizing |
| Module Library | 28/100 | Adopting |
| Policy-as-Code | 15/100 | Early |
| Organization | 68/100 | Standardizing |
| Operations | 62/100 | Adopted |

## State Secrets Findings

| Severity | Count |
|----------|-------|
| 🔴 Secrets in state | 3 |
| 🟡 Sensitive attribute names | 7 |
| Workspaces affected | 2 / 12 |

### Critical: Secrets Found in Terraform State

| Workspace | Finding | Attribute Path |
|-----------|---------|----------------|
| `aws-production` | AWS Secret Key pattern | `managed.aws_iam_access_key.deploy.secret` |
| `aws-production` | Password assignment | `managed.aws_db_instance.main.password` |
| `aws-staging` | Connection string with credentials | `managed.aws_db_instance.staging.endpoint` |

### Remediation (Priority: Immediate)

1. **Rotate compromised credentials** — All secrets found in state must be assumed compromised
2. **Mark sensitive variables**: Add `sensitive = true` to variable and output declarations
3. **Use ephemeral values** (Terraform 1.10+): Add `ephemeral = true` to omit from state entirely
4. **Use write-only arguments** (Terraform 1.11+): Use `_wo` suffixed arguments for passwords
5. **Enable state encryption**: Store state in HCP Terraform or S3 with `encrypt = true`

> Reference: [Managing Sensitive Data in Terraform](https://developer.hashicorp.com/terraform/language/manage-sensitive-data)

## Policy Gap Analysis

### Available (Not Yet Adopted)
- AWS CIS Benchmarks - recommend immediate adoption
- AWS Foundational Policies - recommend adoption

### Custom Development Needed
⚠️ **Healthcare Industry Detected**: HIPAA compliance policies required
- No registry policy available
- Estimated effort: 2-4 weeks
- Recommend: Engage HashiCorp Professional Services

## Operating Model Analysis

**Detected Pattern: Infrastructure Franchise**

Your organization exhibits an Infrastructure Franchise operating model — development teams build custom IaC within policy guardrails rather than consuming pre-built modules from a vending portal.

| Dimension | Service Catalog | Infrastructure Franchise |
|-----------|----------------|--------------------------|
| Primary UX | Vending portal (UI, ServiceNow) | **Custom workflow (Git, API/CLI, CI/CD)** ← You |
| What can be built? | Standard modules only | **Anything via IaC within guardrails** ← You |
| Customization | Limited (module parameters) | **Unlimited (within policy guardrails)** ← You |
| Primary security model | Validated modules | **Guardrails (policy-as-code)** ← You |
| Target persona | Business users, PMs | **Development teams, SRE** ← You |

> As described in the *Terraform: Operating Guide for Standardization*, organizations following the Infrastructure Franchise pattern should prioritize policy-as-code guardrails and module versioning standards.

## Platform Feature Opportunities

Based on your organization's patterns and the current HCP Terraform platform capabilities:

| Feature | Status | Relevance | Recommendation |
|---------|--------|-----------|----------------|
| **Terraform Stacks** | GA | High — Multi-environment patterns detected (prod/staging/dev) | Evaluate for multi-deployment orchestration |
| **Terraform Search** | GA | Medium — Some unmanaged resources suspected | Use to discover and bulk-import unmanaged resources |
| **Terraform Actions** | GA | Medium — Day 2 operational needs identified | Evaluate for configuration management workflows |
| **Terraform MCP Server** | Beta | Low — Developer experience enhancement | Consider for AI-assisted Terraform workflows |

> Feature status sourced from live platform research at time of assessment.

## Module Lifecycle & Publishing

### Current State
- 2 modules in PMR, no deprecation practices observed
- No test-integrated publishing detected
- No version constraint standards enforced

### Recommendations

1. **Implement module deprecation workflow** — Mark retired modules as deprecated (available in Standard edition) rather than deleting them. This preserves history and warns consumers. ([Manage Module Versions](https://developer.hashicorp.com/terraform/cloud-docs/registry/manage-module-versions))

2. **Adopt branch-based publishing with PMR tests** — Use branch-based publishing to run module tests before publication. This ensures only validated modules reach consumers. ([Test-Integrated Publishing](https://developer.hashicorp.com/terraform/cloud-docs/registry/test))

3. **Enforce pessimistic version constraints** — Require all module consumers to use `~>` constraints (e.g., `~> 2.0`) to allow patch updates while preventing breaking changes. ([Version Constraints](https://developer.hashicorp.com/terraform/language/expressions/version-constraints))

4. **Use Explorer for module usage visibility** — Explorer provides a dashboard of which workspaces consume which modules and at what versions. ([Explorer](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/explorer))

5. **Configure automated update tooling** — For organizations with 15+ modules, set up Renovate or Dependabot to automatically create PRs when module versions update. ([Renovate Terraform Support](https://docs.renovatebot.com/modules/manager/terraform/))

## Recommendations

### Immediate (30 days)
1. **Adopt AWS CIS policies from registry**
   - Effort: 2-4 hours
   - Impact: Security baseline established

2. **Enable speculative plans on all VCS workspaces**
   - Effort: 1-2 hours
   - Impact: PR-based review workflow

### Short-term (90 days)
1. **Build PMR with 5 core modules**
   - VPC, EC2, S3, IAM, Security Groups
   - Effort: 2-4 weeks
   - Impact: 60% reduction in code duplication

2. **Develop HIPAA policy set**
   - Custom development required
   - Effort: 2-4 weeks
   - Impact: Compliance automation

### Medium-term (6 months)
1. **Enable self-service workspace provisioning**
2. **Expand PMR to 15+ modules**
3. **Implement FinOps policies**
```

## Report Template

The `report-synthesizer-agent` MUST produce a report following this section structure. Sections marked **(conditional)** are only included when the data supports them.

```
# TFC Maturity Assessment: {Organization Name}

## Executive Summary
- Overall Score table (score, maturity level, stage)
- Top Strengths (3 items)
- Top Improvement Areas (3 items)

## Category Scores
- Table: Category | Score | Level

## State Secrets Findings
- Summary table (severity counts, workspaces affected)
- Critical findings table (workspace, finding, attribute path)
- Remediation steps with Terraform version-specific advice
- Link to HashiCorp sensitive data docs

## Operating Model Analysis (conditional)
- Detected pattern: Service Catalog or Infrastructure Franchise
- Comparison table with "← You" markers on detected pattern
- HVD Operating Guide citation for the detected pattern
- INCLUDE when: pmr-evaluator returns operating_model classification

## Platform Feature Opportunities (conditional)
- Table: Feature | Status | Relevance | Recommendation
- Only include GA or Beta features
- Feature status from platform-research.json (live research)
- INCLUDE when: gitops-evaluator returns feature_opportunities array with 1+ items

## Module Lifecycle & Publishing (conditional)
- Current state summary
- Numbered recommendations with doc links:
  - Module deprecation/revocation workflow
  - Publishing workflow (branch-based vs tag-based)
  - Pessimistic version constraints (~>)
  - Explorer for usage visibility
  - Automated update tooling (Renovate/Dependabot)
- INCLUDE when: organization has 1+ modules in PMR

## Policy Gap Analysis
- Available (Not Yet Adopted) — registry policies
- Custom Development Needed — with effort estimates

## Recommendations
- Immediate (30 days) — with effort and impact
- Short-term (90 days) — with effort and impact
- Medium-term (6 months) — strategic items
- HVD citations in recommendation text (e.g., "As described in the *Terraform: Operating Guide for Adoption*...")

## References
- HVD Operating Guide links (from platform-research.json)
- Platform feature doc links (from platform-research.json)
- Module lifecycle doc links (from platform-research.json)
- TFC/TFE API documentation links
```

**Conditional Section Logic:**
- If `operating_model` is null or undetermined → omit Operating Model Analysis section
- If `feature_opportunities` is empty → omit Platform Feature Opportunities section
- If 0 modules in PMR → omit Module Lifecycle section (recommend PMR adoption instead)
- If platform research quality is `"fallback"` → add footnote: "Platform feature status based on cached data; verify current status at developer.hashicorp.com"

## Troubleshooting

### Token Authentication Failed

```
ERROR: Unable to authenticate with TFC/TFE API
```

**Solution**: Verify `TFC_TOKEN` is valid and not expired.
- **Terraform Cloud**: Generate new token in TFC UI → User Settings → Tokens
- **Terraform Enterprise**: Generate new token in your TFE instance → User Settings → Tokens

### Insufficient Permissions

```
ERROR: 403 Forbidden on /organizations/{org}/policy-sets
```

**Solution**: Token needs organization-level read access. Use a Team token from a team with "Manage Policies" permission.

### Invalid TFE URL

```
ERROR: Cannot connect to TFE instance
```

**Solution**: Verify `TFE_URL` is correct and accessible. The URL should be in the format `https://tfe.example.com` without `/api/v2` suffix. Ensure your network can reach the TFE instance.

### Rate Limiting

```
ERROR: 429 Too Many Requests
```

**Solution**: The skill implements exponential backoff. For large organizations, assessment may take longer.

### Large Organization Timeout

For organizations with >500 workspaces, data collection may timeout. Run with increased timeout:

```bash
TFC_TIMEOUT=300 /tfc-practice-evaluator
```

## References

### HVD Operating Guides
- [HVD Terraform Adoption Guide](https://developer.hashicorp.com/validated-designs/terraform-operating-guides-adoption)
- [HVD Terraform Standardization Guide](https://developer.hashicorp.com/validated-designs/terraform-operating-guides-standardization)
- [HVD Terraform Scaling Guide](https://developer.hashicorp.com/validated-designs/terraform-operating-guides-scaling)
- [HVD Terraform Solution Design Guide](https://developer.hashicorp.com/validated-designs)

### Platform Features
- [Terraform Stacks](https://developer.hashicorp.com/terraform/cloud-docs/stacks) — Multi-deployment orchestration
- [Terraform Search](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/import) — Discover and bulk-import unmanaged resources
- [Terraform Actions](https://developer.hashicorp.com/terraform/language/invoke-actions) — Day 2 operations
- [Terraform MCP Server](https://developer.hashicorp.com/terraform/mcp-server) — AI-assisted Terraform workflows

### Module Lifecycle
- [Manage Module Versions](https://developer.hashicorp.com/terraform/cloud-docs/registry/manage-module-versions) — Deprecation and revocation
- [Test-Integrated Publishing](https://developer.hashicorp.com/terraform/cloud-docs/registry/test) — Module testing before publication
- [Explorer](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/explorer) — Module usage visibility
- [Version Constraints](https://developer.hashicorp.com/terraform/language/expressions/version-constraints) — Pessimistic constraints
- [Workspace Notifications](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings/notifications) — Slack, Teams, Email, webhooks
- [Renovate Terraform Support](https://docs.renovatebot.com/modules/manager/terraform/) — Automated module update PRs

### API & General
- [TFC API Documentation](https://developer.hashicorp.com/terraform/cloud-docs/api-docs)
- [TFE API Documentation](https://developer.hashicorp.com/terraform/enterprise/api-docs)
- [Terraform Registry Policies](https://registry.terraform.io/browse/policies)
- [Managing Sensitive Data in Terraform](https://developer.hashicorp.com/terraform/language/manage-sensitive-data)

> **Note**: The `platform-research-agent` fetches current URLs at runtime via web search. The links above are fallback references that were accurate as of the last skill update.

## Skill Structure

```
tfc-practice-evaluator/
├── SKILL.md                          # This file - comprehensive documentation
├── scripts/                          # Production-ready scripts
│   ├── README.md                     # Script usage documentation
│   ├── collect_tfc_data.py          # Data collection - Python (recommended)
│   ├── collect_tfc_data.sh          # Data collection - Bash
│   ├── obfuscate_data.py            # Obfuscate data.json for SE-assisted mode
│   ├── deobfuscate_report.py        # Deobfuscate reports after SE analysis
│   └── convert_to_docx.py          # Convert .md reports to .docx (optional, requires python-docx)
├── sample/                           # Sample output files
│   ├── report.md                     # Example assessment report
│   └── obfuscation_map.json         # Example obfuscation map structure
├── tests/                            # Test suite
│   └── test_state_scan.py           # State secrets scanner tests

Output (created during execution):
assessment/
├── data.json                         # Raw TFC data (87 KB for demo org)
├── platform-research.json            # Live platform research results (HVD, features, lifecycle)
├── data_obfuscated.json              # Obfuscated data (Mode 2 only, safe to share)
├── obfuscation_map.json              # Hash-to-name mapping (Mode 2 only, KEEP PRIVATE)
├── gitops-eval.json                  # GitOps evaluation results
├── pmr-eval.json                     # PMR evaluation results
├── policy-eval.json                  # Policy evaluation + gap analysis
├── org-eval.json                     # Organization evaluation results
├── ops-eval.json                     # Operations evaluation results
├── state-secrets-eval.json           # State secrets evaluation results
├── report.md                         # Executive assessment report
├── report.docx                       # Executive assessment report (DOCX, optional)
├── roadmap.md                        # 6-month implementation roadmap
└── roadmap.docx                      # 6-month implementation roadmap (DOCX, optional)
```

