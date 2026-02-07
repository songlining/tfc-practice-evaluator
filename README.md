# TFC/TFE Practice Evaluator

[![Claude Skill](https://img.shields.io/badge/Claude-Skill-7C3AED?logo=anthropic&logoColor=white)](https://github.com/songlining/tfc-practice-evaluator)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/songlining/tfc-practice-evaluator?style=social)](https://github.com/songlining/tfc-practice-evaluator)

> Evaluate your HCP Terraform (Terraform Cloud) or Terraform Enterprise organization against HashiCorp Validated Designs (HVD) best practices.

A Claude AI skill that analyzes your TFC/TFE organization and provides:

- **Maturity Score** aligned to Adopt → Standardize → Scale stages
- **Category Assessments** for GitOps, Modules, Policies, Organization, and Operations
- **Gap Analysis** identifying missing policies and configurations
- **Prioritized Recommendations** with business value justification
- **Roadmap** for maturity progression

## Two Operating Modes

| Mode | Who Runs Analysis | When to Use |
|------|-------------------|-------------|
| **Mode 1: Self-Service** | Customer | Customer has a business-approved LLM/agent |
| **Mode 2: SE-Assisted** | HashiCorp SE | Customer has no LLM access; data is obfuscated for privacy |

## Quick Install

### One-liner Installation

```bash
# Clone to your Claude skills directory
git clone https://github.com/songlining/tfc-practice-evaluator.git ~/.claude/skills/tfc-practice-evaluator
```

### Manual Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/songlining/tfc-practice-evaluator.git
   ```

2. Copy to your Claude skills directory:
   ```bash
   cp -r tfc-practice-evaluator ~/.claude/skills/
   ```

3. Restart Claude (or VS Code with Claude extension) to load the skill.

### Verify Installation

The skill will be available when you see it listed in your Claude skills, or you can invoke it directly:
```
"Evaluate my TFC organization"
```

## Usage

### Prerequisites

Set your TFC/TFE credentials as environment variables:

```bash
# Required
export TFC_TOKEN="your-team-or-user-token"
export TFC_ORG="your-organization-name"

# Optional (for Terraform Enterprise only)
export TFE_URL="https://tfe.example.com"
```

### Mode 1: Self-Service (Customer Has LLM Access)

Just ask Claude naturally:

- "Evaluate my TFC"
- "TFC health check"
- "Assess my Terraform Cloud"
- "How good is my TFC setup?"
- "TFC best practices review"
- "TFE maturity assessment"

```
You: Evaluate my TFC organization

Claude: I'll analyze your Terraform Cloud organization against HashiCorp 
        Validated Designs. Let me collect the data...

        📊 Assessment Complete!
        
        Overall Maturity: Standardize (67%)
        
        ✅ GitOps:       82% - Strong VCS integration
        ⚠️ Modules:      45% - Limited PMR adoption
        ❌ Policies:     20% - Missing critical policies
        ✅ Organization: 75% - Good team structure
        ✅ Operations:   85% - Healthy run patterns
        
        Top 3 Recommendations:
        1. Enable Sentinel policies for security guardrails
        2. Migrate CLI/API workspaces to VCS-driven
        3. Publish common modules to Private Registry
```

### Mode 2: SE-Assisted (Customer Has No LLM Access)

For customers without a business-approved LLM, the workflow splits into three phases with built-in data privacy:

#### Phase 1: Customer Collects & Obfuscates Data

```bash
# 1. Set credentials
export TFC_TOKEN="your-team-token"
export TFC_ORG="your-organization"
export OUTPUT_DIR="./assessment"

# 2. Collect data from TFC/TFE API
python3 scripts/collect_tfc_data.py

# 3. Obfuscate all business-identifiable names
python3 scripts/obfuscate_data.py

# 4. Send ONLY assessment/data_obfuscated.json to your HashiCorp SE
#    KEEP assessment/obfuscation_map.json PRIVATE
```

#### Phase 2: SE Runs Analysis

The HashiCorp SE receives the obfuscated data file, places it as `assessment/data.json`, and runs the skill to generate `report.md` and `roadmap.md`. The SE sends these report files back to the customer.

#### Phase 3: Customer Deobfuscates Reports

```bash
# 1. Place report.md and roadmap.md from your SE into assessment/
# 2. Restore real names
python3 scripts/deobfuscate_report.py

# 3. Your reports now contain real workspace, team, module names
```

**Privacy Guarantee**: All business names (workspaces, teams, modules, projects, policies, VCS repos, organization) are replaced with SHA-256 hashes. The mapping file that can reverse these hashes never leaves your environment. Even if a third party intercepts the obfuscated data, they see only aggregate metrics — no business-identifiable information.

## What Gets Evaluated

| Category | Metrics Analyzed |
|----------|------------------|
| **GitOps** | VCS integration %, speculative plans, auto-apply, execution mode |
| **Modules** | PMR module count, versioning, workspace adoption |
| **Policies** | Policy coverage, enforcement levels, pass rates |
| **Organization** | Team structure, RBAC, project organization, variable sets |
| **Operations** | Run success rates, frequency, Terraform version hygiene |

## Token Permissions

Your TFC/TFE token needs **read access** to:
- Workspaces
- Runs
- Registry Modules
- Policy Sets
- Teams
- Variable Sets
- Projects

A Team token with organization-level read access is recommended.

## Scripts

| Script | Purpose | Requirements |
|--------|---------|--------------|
| `scripts/collect_tfc_data.py` | Collect data from TFC/TFE API | Python 3.6+ (no dependencies) |
| `scripts/collect_tfc_data.sh` | Collect data (Bash alternative) | Bash, curl, jq |
| `scripts/obfuscate_data.py` | Obfuscate business names for SE-assisted mode | Python 3.6+ (no dependencies) |
| `scripts/deobfuscate_report.py` | Restore real names in reports after SE analysis | Python 3.6+ (no dependencies) |

All scripts use Python standard library only — no `pip install` required.

## Output

### Mode 1 (Self-Service)

- `assessment/data.json` - Raw API data
- `assessment/report.md` - Detailed assessment report
- `assessment/roadmap.md` - Prioritized improvement roadmap

### Mode 2 (SE-Assisted) — Additional Files

- `assessment/data_obfuscated.json` - Obfuscated data (safe to share with SE)
- `assessment/obfuscation_map.json` - Hash-to-name mapping (**keep private**)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE) - see LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/songlining/tfc-practice-evaluator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/songlining/tfc-practice-evaluator/discussions)

## Related Resources

- [HashiCorp Validated Designs](https://developer.hashicorp.com/validated-designs)
- [Terraform Cloud Documentation](https://developer.hashicorp.com/terraform/cloud-docs)
- [Claude Skills Documentation](https://docs.anthropic.com/)

---

Made with ❤️ for the Terraform community
