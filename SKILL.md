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

Both data collection scripts have been validated against production TFC organizations (including `hashicorp-wwtfo-demo-platform-prod` with 41 modules, 4 workspaces) and handle:
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
- Registry Modules
- Policy Sets
- Teams
- Variable Sets
- Projects

A **Team token** with organization-level read access is recommended.

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
  - `/organizations/{org}/registry-modules`
  - `/organizations/{org}/policy-sets`
  - `/organizations/{org}/teams`
  - `/organizations/{org}/varsets`
  - `/organizations/{org}/projects`
- Handles rate limiting gracefully
- Saves consolidated output to `assessment/data.json`

**API Base URL Defaults**:
- Terraform Cloud: `https://app.terraform.io/api/v2` (default)
- Terraform Enterprise: `https://{TFE_URL}/api/v2` (set via TFC_API_BASE)

**Main agent waits** for `assessment/data.json` to be created, then proceeds to evaluation.

### Step 3: Analysis (Multiple Sub-Agents)

🤖 **SPAWN 5 PARALLEL SUB-AGENTS** (each analyzes one category):

1. **`gitops-evaluator-agent`**: Read `assessment/data.json`, analyze VCS integration metrics, calculate GitOps score using criteria from `research/PATTERNS.md`, return JSON with score and findings.

2. **`pmr-evaluator-agent`**: Read `assessment/data.json`, analyze module library metrics, calculate PMR score, return JSON with score and findings.

3. **`policy-evaluator-agent`**: Read `assessment/data.json` and `research/sentinel-policies.md`, analyze policy coverage, identify gaps (including custom policy needs), calculate Policy score, return JSON with score, findings, and gap analysis.

4. **`org-evaluator-agent`**: Read `assessment/data.json`, analyze team structure and organization, calculate Org score, return JSON with score and findings.

5. **`ops-evaluator-agent`**: Read `assessment/data.json`, analyze run health and operations, calculate Ops score, return JSON with score and findings.

**Main agent** collects all 5 results and consolidates into overall scores.

### Step 4: Report Synthesis (Sub-Agent Required)

🤖 **SPAWN SUB-AGENT**: `report-synthesizer-agent`

**Task**: "Generate comprehensive assessment report from all evaluation results. Create executive summary, category breakdowns, prioritized recommendations, and roadmap. Output to assessment/report.md and assessment/roadmap.md."

**Main agent** confirms report generation and displays summary to user.

### Step 5: Completion (Main Agent)

Main agent provides user with:
- Overall maturity score
- Link to `assessment/report.md`
- Link to `assessment/roadmap.md`
- Top 3 recommendations

Main agent context remains clean throughout - only orchestration and summary.

## Sub-Agent Architecture

⚠️ **MANDATORY**: This skill MUST use sub-agents. The main agent is an orchestrator only.

### Why Sub-Agents Are Required

1. **Context Management**: API responses can be 10-50KB per endpoint (e.g., 87KB data.json for 4 workspaces). Without sub-agents, the main agent's context would be polluted with raw JSON data.
2. **Parallel Processing**: Multiple evaluation categories can be analyzed simultaneously (5 parallel evaluations: GitOps, PMR, Policy, Org, Ops).
3. **Isolation**: Each sub-agent has a focused task and clean context.
4. **Error Recovery**: If one sub-agent fails, others can continue.
5. **Proven Performance**: Successfully evaluated `hashicorp-wwtfo-demo-platform-prod` (4 workspaces, 41 modules, 68 runs) in ~8 minutes with 7 parallel sub-agents.

### Sub-Agent Execution Order

```
Main Agent (Orchestrator)
    ↓
    ├─ [Step 1] Validate prerequisites (credentials, directory setup)
    ↓
    ├─ [Step 2] SPAWN → data-collector-agent
    │           └─ Fetches all API data → assessment/data.json
    ↓
    ├─ [Step 3] SPAWN (5 parallel) → evaluation agents
    │           ├─ gitops-evaluator-agent
    │           ├─ pmr-evaluator-agent
    │           ├─ policy-evaluator-agent
    │           ├─ org-evaluator-agent
    │           └─ ops-evaluator-agent
    │           └─ All return JSON with scores/findings
    ↓
    ├─ [Step 4] SPAWN → report-synthesizer-agent
    │           └─ Generates final reports
    ↓
    └─ [Step 5] Display summary to user
```

### Sub-Agent Definitions

| Sub-Agent | Spawned By | Input | Output | Tools |
|-----------|------------|-------|--------|-------|
| `data-collector-agent` | Main | Credentials, API URL | `assessment/data.json` | curl, jq |
| `gitops-evaluator-agent` | Main | `data.json`, `PATTERNS.md` | JSON: score + findings | read_file |
| `pmr-evaluator-agent` | Main | `data.json`, `PATTERNS.md` | JSON: score + findings | read_file |
| `policy-evaluator-agent` | Main | `data.json`, `PATTERNS.md`, `sentinel-policies.md` | JSON: score + gap analysis | read_file |
| `org-evaluator-agent` | Main | `data.json`, `PATTERNS.md` | JSON: score + findings | read_file |
| `ops-evaluator-agent` | Main | `data.json`, `PATTERNS.md` | JSON: score + findings | read_file |
| `report-synthesizer-agent` | Main | All evaluation results | `report.md`, `roadmap.md` | create_file |

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
  prompt: "Read assessment/data.json. Count workspaces with vcs_repo configured. Calculate percentage. Using research/PATTERNS.md scoring rubric, evaluate VCS Integration criterion and return JSON: {score: X, findings: ['...']}. Use ONLY read_file - NO MCP servers.",
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

Based on the successful evaluation of `hashicorp-wwtfo-demo-platform-prod`, here are critical insights:

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
- Parallel evaluations: **~5 minutes** (5 agents: GitOps, PMR, Policy, Org, Ops)
- Report synthesis: **~3 minutes** (1 agent: consolidation + writing)
- **Total: ~8 minutes**

**Scaling Estimates:**
- 10 workspaces: ~10 minutes
- 50 workspaces: ~15 minutes
- 100+ workspaces: ~20-30 minutes

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

**After Evaluations:**
- ✅ 5 evaluation JSON files exist (gitops, pmr, policy, org, ops)
- ✅ Each has a `score` field (numeric)
- ✅ Policy evaluation includes `gap_analysis` object

**After Report Synthesis:**
- ✅ `report.md` is >20 KB (comprehensive content)
- ✅ `roadmap.md` is >30 KB (detailed implementation plan)
- ✅ Overall score is 0-100 (not null)

### 8. Demo Platform Insights

**If evaluating a demo/sandbox platform (like wwtfo-demo):**

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

**Security Properties:**
- SHA-256 hashing with a per-session random salt
- Same name always maps to the same hash within a session (deterministic for consistency)
- Different sessions produce different hashes (salt changes)
- The `obfuscation_map.json` never leaves the customer environment
- Even with the obfuscated data, an attacker cannot reverse the hashes without the salt

### 9. Report Tailoring Strategies

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

### 10. Quick Wins to Always Recommend

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

## Proven Results

This skill has been successfully validated against real TFC organizations:

**Test Case: `hashicorp-wwtfo-demo-platform-prod`**
- Organization Size: 4 workspaces, 41 private modules, 68 runs sampled
- Data Collection: 87 KB `data.json` generated in ~30 seconds
- Evaluation: 5 parallel sub-agents completed in ~8 minutes
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

## Policy Gap Analysis

### Available (Not Yet Adopted)
- AWS CIS Benchmarks - recommend immediate adoption
- AWS Foundational Policies - recommend adoption

### Custom Development Needed
⚠️ **Healthcare Industry Detected**: HIPAA compliance policies required
- No registry policy available
- Estimated effort: 2-4 weeks
- Recommend: Engage HashiCorp Professional Services

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

- [HVD Terraform Adoption Guide](https://developer.hashicorp.com/validated-designs/terraform-operating-guides-adoption)
- [HVD Terraform Standardization Guide](https://developer.hashicorp.com/validated-designs/terraform-operating-guides-standardization)
- [HVD Terraform Scaling Guide](https://developer.hashicorp.com/validated-designs/terraform-operating-guides-scaling)
- [TFC API Documentation](https://developer.hashicorp.com/terraform/cloud-docs/api-docs)
- [TFE API Documentation](https://developer.hashicorp.com/terraform/enterprise/api-docs)
- [Terraform Registry Policies](https://registry.terraform.io/browse/policies)

## Skill Structure

```
tfc-practice-evaluator/
├── SKILL.md                          # This file - comprehensive documentation
├── scripts/                          # Production-ready scripts
│   ├── README.md                     # Script usage documentation
│   ├── collect_tfc_data.py          # Data collection - Python (recommended)
│   ├── collect_tfc_data.sh          # Data collection - Bash
│   ├── obfuscate_data.py            # Obfuscate data.json for SE-assisted mode
│   └── deobfuscate_report.py        # Deobfuscate reports after SE analysis
└── research/                         # Research documents (if present)
    ├── tfc-api.md                    # TFC API capabilities
    ├── hvd-criteria.md               # HVD maturity criteria
    ├── gitops-patterns.md            # GitOps best practices
    ├── sentinel-policies.md          # Policy-as-code patterns
    ├── onboarding-patterns.md        # Team onboarding patterns
    └── PATTERNS.md                   # Synthesized evaluation rubric

Output (created during execution):
assessment/
├── data.json                         # Raw TFC data (87 KB for demo org)
├── data_obfuscated.json              # Obfuscated data (Mode 2 only, safe to share)
├── obfuscation_map.json              # Hash-to-name mapping (Mode 2 only, KEEP PRIVATE)
├── gitops-eval.json                  # GitOps evaluation results
├── pmr-eval.json                     # PMR evaluation results
├── policy-eval.json                  # Policy evaluation + gap analysis
├── org-eval.json                     # Organization evaluation results
├── ops-eval.json                     # Operations evaluation results
├── report.md                         # Executive assessment report
└── roadmap.md                        # 6-month implementation roadmap
```

## Research Documents

This skill was built from these research documents (if available in `research/`):
- `research/tfc-api.md` - TFC API capabilities
- `research/hvd-criteria.md` - HVD maturity criteria
- `research/gitops-patterns.md` - GitOps best practices
- `research/sentinel-policies.md` - Policy-as-code patterns
- `research/onboarding-patterns.md` - Team onboarding patterns
- `research/PATTERNS.md` - Synthesized evaluation rubric
