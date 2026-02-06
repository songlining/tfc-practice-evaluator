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

### Trigger Phrases

Just ask Claude naturally:

- "Evaluate my TFC"
- "TFC health check"
- "Assess my Terraform Cloud"
- "How good is my TFC setup?"
- "TFC best practices review"
- "TFE maturity assessment"

### Example Session

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

## Data Collection Scripts

This skill includes production-ready data collection scripts:

| Script | Requirements | Best For |
|--------|--------------|----------|
| `scripts/collect_tfc_data.py` | Python 3.6+ (no dependencies) | Cross-platform, recommended |
| `scripts/collect_tfc_data.sh` | Bash, curl, jq | Unix/macOS systems |

Both scripts handle pagination, rate limiting, and errors gracefully.

## Output

The skill generates:
- `assessment/data.json` - Raw API data
- `assessment/report.md` - Detailed assessment report
- `assessment/roadmap.md` - Prioritized improvement roadmap

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
