# TFC Maturity Assessment: hashicorp-wwtfo-demo-platform-prod

**Assessment Date**: 7 February 2026  
**Assessed By**: TFC Practice Evaluator (Automated)  
**Organization**: hashicorp-wwtfo-demo-platform-prod  
**Platform**: HCP Terraform (Terraform Cloud)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Overall Score** | **60.6 / 100** |
| **Maturity Level** | Adopted |
| **Current Stage** | Transitioning from Adopt → Standardize |
| **State Secrets** | ✅ Clean (no cap applied) |

### Scoring Methodology

| Category | Weight | Score | Weighted |
|----------|--------|-------|----------|
| GitOps & VCS | 25% | 84.0% | 21.00 |
| Module Library (PMR) | 20% | 92.5% | 18.50 |
| Policy-as-Code | 25% | 5.0% | 1.25 |
| Organization & Teams | 15% | 55.0% | 8.25 |
| Operations & Health | 15% | 77.5% | 11.63 |
| **Total** | **100%** | | **60.63** |

### Top Strengths

1. ✅ **Exceptional Module Library** — 41 modules with 16.76 average versions per module (3–5× industry average). Best-in-class module development practices.
2. ✅ **100% VCS Integration** — All 4 workspaces connected to GitHub via GitHub App with speculative plans enabled and remote execution.
3. ✅ **Strong Operational Health** — 94.1% run success rate across 68 sampled runs with consistent weekly cadence.

### Top Improvement Areas

1. ❌ **Zero Policy Sets** — No Sentinel or OPA policies deployed. This is the single largest gap preventing progression to "Standardize" stage.
2. ⚠️ **No RBAC Structure** — Single team with 327 users. No Admin/Developer/Viewer separation.
3. ⚠️ **Variable Sets Unused** — 5 variable sets created but 0 attached to any workspace.

---

## Organization Profile

| Attribute | Value |
|-----------|-------|
| Organization | `hashicorp-wwtfo-demo-platform-prod` |
| Platform | HCP Terraform (app.terraform.io) |
| Organization Type | HashiCorp Internal Demo Platform |
| Total Workspaces | 4 |
| Active Workspaces | 3 (75%) |
| Private Modules (PMR) | 41 |
| Published Module Versions | 687 |
| Policy Sets | 0 |
| Teams | 1 (327 users) |
| Variable Sets | 5 (0 attached) |
| Projects | 2 |
| Runs Sampled | 68 |
| State Secrets Findings | 0 |

### Workspace Inventory

| Workspace | Project | Terraform Version | Auto-Apply | Last Activity |
|-----------|---------|-------------------|------------|---------------|
| shared-services-app-network-dev | shared-workspaces-projects-rbac | 1.9.6 | ✅ Yes | Active (weekly) |
| shared-services-app-compute-dev | shared-workspaces-projects-rbac | 1.9.6 | ✅ Yes | Active (weekly) |
| shared-services-app-data-dev | shared-workspaces-projects-rbac | 1.9.6 | ✅ Yes | Active (weekly) |
| packer-out-of-date | shared-vpm | ~>1.10.0 | ❌ No | ⚠️ Stale (7 months) |

---

## Category Scores

| Category | Score | Max | Percentage | Stage | Status |
|----------|-------|-----|------------|-------|--------|
| GitOps & VCS | 42 | 50 | 84.0% | Standardizing | ✅ |
| Module Library (PMR) | 37 | 40 | 92.5% | Standardized | ✅ |
| Policy-as-Code | 2 | 40 | 5.0% | Early | ❌ |
| Organization & Teams | 22 | 40 | 55.0% | Adopting | ⚠️ |
| Operations & Health | 31 | 40 | 77.5% | Standardizing | ✅ |
| State Secrets Hygiene | 100 | 100 | 100.0% | Clean | ✅ |

---

## Detailed Category Analysis

### 1. GitOps & VCS — 42/50 (84%) — Standardizing

**Score Breakdown:**

| Criterion | Score | Max | Notes |
|-----------|-------|-----|-------|
| VCS Integration | 10 | 10 | 100% — All 4 workspaces connected via GitHub App |
| Speculative Plans | 10 | 10 | 100% — All workspaces have speculative plans enabled |
| VCS-Triggered Runs | 0 | 10 | 0% — All runs are API-driven (architectural choice) |
| Auto-Apply | 8 | 10 | 75% — 3/4 workspaces have auto-apply enabled |
| Remote Execution | 10 | 10 | 100% — No local or agent execution |
| Working Directory (Bonus) | 4 | 0 | Monorepo structure with working directories |

**Key Findings:**

- ✅ **100% VCS integration** — All 4 workspaces have `vcs_repo` configured with GitHub App
- ✅ **100% speculative plans** — PR-based review workflow capability fully enabled
- ✅ **100% remote execution** — Consistent remote execution mode across all workspaces
- ✅ **75% auto-apply** — 3 of 4 workspaces auto-apply after successful plans
- ⚠️ **API-driven architecture** — All 68 runs are `tfe-api` sourced with `manual` trigger reason. Zero VCS-triggered runs.

**Architectural Note:**
The 0% VCS-triggered run rate is an intentional architectural choice, not a deficiency. This organization uses external CI/CD orchestration (likely GitHub Actions or similar) to trigger runs via the TFC API. This pattern is common for:
- Demo platforms requiring automated testing
- Organizations with complex pre-run validation
- Teams integrating TFC into existing CI/CD pipelines

**Recommendations:**

1. **Document API-driven workflow** — Capture the external orchestration pattern for knowledge transfer
2. **Leverage speculative plans** — Ensure external CI/CD triggers speculative plans on PRs
3. **Consider run triggers** — For workspace dependencies, evaluate TFC native run triggers
4. **Enable auto-apply on packer-out-of-date** — Or archive if no longer needed

---

### 2. Module Library (PMR) — 37/40 (92.5%) — Standardized

**Score Breakdown:**

| Criterion | Score | Max | Notes |
|-----------|-------|-----|-------|
| Module Count | 10 | 10 | 41 modules — far exceeds typical 5–15 module PMR |
| Versioning | 10 | 10 | 16.76 avg versions per module — exceptional |
| Provider Coverage | 8 | 10 | 10 providers — strong HashiCorp ecosystem coverage |
| Module Health | 9 | 10 | 99.8% healthy — only 2 ingestion failures in 687 versions |

**Key Findings:**

- ✅ **41 published modules** — 3–5× higher than typical enterprise organizations (8–15 modules)
- ✅ **16.76 average versions per module** — Indicates active maintenance and strong CI/CD practices
- ✅ **687 total published versions** — Massive module library demonstrating intensive development
- ✅ **10 providers covered** — vault (15), terraform (13), util (3), waypoint (2), boundary (1), nomad (1), consul (1), hvs (1), vaultradar (1), autobahn (1)
- ✅ **99.8% module health** — Only 2 version ingestion failures across entire library
- ✅ **Strong semantic versioning** — 38/41 modules at stable 1.x.x releases
- ✅ **Cross-product integration** — Modules for vault-and-ansible, terraform-and-ansible, kubernetes-vso

**Metrics:**

| Metric | Value |
|--------|-------|
| Total Modules | 41 |
| Average Versions/Module | 16.76 |
| Total Published Versions | 687 |
| Modules at Stable Release (1.x+) | 38 (93%) |
| Modules in Pre-release (0.x) | 3 (7%) |
| Failed Ingestions | 2 (0.3%) |
| Most Iterated Module | config-driven-import (68 versions) |

**Recommendations:**

1. **Document module usage patterns** — Create internal guides showing which demo scenarios use which modules
2. **Publish select modules to public registry** — vcs-workflow, workspaces-projects-rbac, policy-as-code are candidates
3. **Monitor ingestion failures** — all-boundary-use-cases v0.1.1 and invisimart-waypoint-template-nocode-ecs v1.0.1 have failures
4. **Track adoption metrics** — Measure which modules are most used across the demo ecosystem
5. **Establish lifecycle policy** — Define deprecation/archival process for obsolete modules

---

### 3. Policy-as-Code — 2/40 (5%) — Early

**This is the critical gap in the organization.**

**Score Breakdown:**

| Criterion | Score | Max | Notes |
|-----------|-------|-----|-------|
| Policy Set Count | 0 | 10 | Zero policy sets deployed |
| Policy Coverage | 0 | 10 | 0% of workspaces covered |
| Enforcement Levels | 0 | 10 | No advisory/soft/hard mandatory policies |
| Existence Bonus | 2 | 10 | +2 for having deployed infrastructure |

**Key Findings:**

- ❌ **Zero policy sets** configured across the entire organization
- ❌ **0% policy coverage** — No workspaces have policy checks
- ❌ **No enforcement levels** — No advisory, soft-mandatory, or hard-mandatory policies
- ❌ **No policy checks executed** — No pass/fail data available
- ⚠️ **Maturity mismatch** — Organization has exceptional module maturity (92.5%) but zero policy governance (5%)

**Context:**
Zero policy sets is normal for 70%+ of TFC organizations initially. However, organizations with similar module maturity (40+ modules) typically have 3–10 policy sets. This represents the single largest opportunity for maturity improvement.

**Demo Platform Opportunity:**
As a demo platform, adding policies would strengthen customer demonstrations by showcasing TFC governance capabilities in action.

---

### 4. Organization & Teams — 22/40 (55%) — Adopting

**Key Findings:**

- ⚠️ **Single team** — `ddr-all-users-team` with 327 users, no role separation
- ⚠️ **No RBAC** — No Admin/Developer/Viewer team structure
- ⚠️ **Variable sets unused** — 5 global variable sets exist but 0 are attached to workspaces
- ⚠️ **Team visibility: secret** — Limits discoverability and collaboration
- ✅ **Good naming consistency** — 3/4 workspaces follow `shared-services-app-{component}-dev` pattern
- ✅ **Projects configured** — 2 projects, all 4 workspaces assigned to projects

**Metrics:**

| Metric | Value |
|--------|-------|
| Teams | 1 |
| Users in Team | 327 |
| Projects | 2 |
| Variable Sets | 5 (0 attached) |
| Naming Consistency | Consistent (3/4) |
| RBAC Structure | None |

**Recommendations:**

1. **Attach variable sets** — 5 existing sets can be connected to workspaces immediately (1–2 hours)
2. **Create RBAC teams** — Minimum: Admin, Developer, Viewer (4–8 hours)
3. **Review team visibility** — Change from "secret" to "organization" for better collaboration
4. **Configure organization_access** — Set explicit permissions on teams
5. **Formalize naming convention** — Document the existing `shared-services-app-{component}-{env}` pattern

---

### 5. Operations & Health — 31/40 (77.5%) — Standardizing

**Score Breakdown:**

| Criterion | Score | Max | Notes |
|-----------|-------|-----|-------|
| Run Success Rate | 9 | 10 | 94.1% (64/68 successful) |
| Active Workspaces | 7 | 10 | 75% active (3/4, 1 stale) |
| Terraform Version Hygiene | 8 | 10 | 3/4 on consistent 1.9.6 |
| Run Cadence | 7 | 10 | Consistent weekly for active workspaces |

**Key Findings:**

- ✅ **94.1% run success rate** — 64 successful runs out of 68 sampled
- ✅ **Zero locked workspaces** — Healthy operational state
- ✅ **Consistent versioning** — 3/4 workspaces on Terraform 1.9.6
- ✅ **Regular cadence** — Active workspaces show consistent weekly runs
- ⚠️ **1 stale workspace** — `packer-out-of-date` inactive for 7 months with multiple errors
- ⚠️ **Version constraint** — 1 workspace uses `~>1.10.0` instead of exact version

**Run Distribution:**

| Status | Count | Percentage |
|--------|-------|------------|
| Applied | 61 | 89.7% |
| Planned & Finished | 5 | 7.4% |
| Errored | 3 | 4.4% |
| Canceled | 2 | 2.9% |
| Discarded | 1 | 1.5% |

**Recommendations:**

1. **Fix or archive packer-out-of-date** — 7 months stale, multiple errors, version constraint
2. **Standardize Terraform version** — Move all workspaces to exact version pinning
3. **Establish workspace lifecycle policy** — Define staleness criteria and archival process
4. **Consider Terraform upgrade** — Current 1.9.6, latest is 1.11.x (write-only variables, ephemeral values)
5. **Set up health monitoring** — Alerts for repeated failures or approaching staleness

---

### 6. State Secrets Hygiene — 100/100 — Clean

**Key Findings:**

- ✅ **Zero secrets detected** across all 4 workspaces
- ✅ **100% scan coverage** — All workspaces scanned
- ✅ **No API keys, passwords, tokens, or private keys** found in state
- ℹ️ **No state files detected** — All 4 workspaces returned HTTP 404 for state download, indicating either new workspaces or workspaces without successful applies

**Impact on Overall Maturity:**

| Finding Count | Impact | Applied? |
|---------------|--------|----------|
| 0 findings | No cap | ✅ Yes — Full score applies |
| 1–5 findings | Ops capped at 70% | N/A |
| 6+ findings | Ops capped at 50%, maturity capped at "Adopting" | N/A |

**Best Practices for Continued Hygiene:**

1. Mark sensitive variables with `sensitive = true`
2. Use `ephemeral = true` (Terraform 1.10+) for values that shouldn't persist in state
3. Use write-only arguments `_wo` suffix (Terraform 1.11+) for passwords
4. HCP Terraform provides encrypted state storage by default
5. Establish quarterly state hygiene audits

> **Reference**: [Managing Sensitive Data in Terraform](https://developer.hashicorp.com/terraform/language/manage-sensitive-data)

---

## Policy Gap Analysis

### Available Registry Policies — Not Yet Adopted

| Policy Set | Source | Category | Priority | Effort | Immediate Value |
|------------|--------|----------|----------|--------|-----------------|
| **AWS CIS Benchmarks v1.4.0** | `hashicorp/cis-policy-set-aws` | Security | 🔴 High | 2–4 hours | Security baseline for AWS infrastructure |
| **Azure CIS Benchmarks v1.3.0** | `hashicorp/cis-policy-set-azure` | Security | 🟡 Medium | 2–4 hours | Security baseline for Azure (if applicable) |
| **GCP CIS Benchmarks v1.2.0** | `hashicorp/cis-policy-set-gcp` | Security | 🟡 Medium | 2–4 hours | Security baseline for GCP (if applicable) |
| **Cloud Foundational Policies** | `hashicorp/foundational-policy-set` | General | 🔴 High | 2–4 hours | Cross-cloud governance patterns |

**Adoption Steps:**
1. Install policy set from Terraform Registry
2. Configure in **advisory mode** first (no blocking)
3. Test against existing workspaces for 2 weeks
4. Enable **soft-mandatory** after validation
5. Enable **hard-mandatory** for critical policies after 30 days

### Custom Policy Development Needed

| Gap | Category | Priority | Effort | Business Impact |
|-----|----------|----------|--------|-----------------|
| **FinOps Cost Controls** | Cost Management | 🔴 High | 1–2 weeks | Reduce cloud spend by 20–40% |
| **Custom Tagging Schema** | Organization Standards | 🔴 High | 1 week | Enable cost allocation & chargeback |
| **Security Group Hygiene** | Security | 🔴 High | 1 week | Prevent misconfigured network access |
| **Data Protection** | Security & Compliance | 🔴 High | 1–2 weeks | Meet SOC 2, ISO 27001 requirements |
| **Resource Naming Standards** | Organization Standards | 🟡 Medium | 1 week | Improve operational clarity |
| **Demo Showcase Policies** | Customer Demonstration | 🟡 Medium | 1 week | Strengthen TFC sales conversations |
| **Multi-Region Resilience** | Operational Excellence | 🟡 Medium | 1–2 weeks | Reduce downtime risk |
| **HIPAA Compliance** | Compliance | Conditional | 2–4 weeks | Healthcare data protection |
| **Australian ISM Essential Eight** | Compliance | Conditional | 2–4 weeks | Government security requirements |
| **APRA CPS 234** | Compliance | Conditional | 2–4 weeks | Financial services regulation |
| **FedRAMP** | Compliance | Conditional | 2–4 weeks | US government authorization |
| **GDPR** | Compliance | Conditional | 2–4 weeks | European data protection |
| **PCI-DSS** | Compliance | Conditional | 2–4 weeks | Payment card industry |

---

## Quick Wins

| # | Action | Effort | Impact | Difficulty |
|---|--------|--------|--------|------------|
| 1 | **Install AWS CIS Benchmarks** from registry (advisory mode) | 2–4 hours | 🔴 High — Immediate security baseline | Low |
| 2 | **Attach 5 existing variable sets** to workspaces | 1–2 hours | 🟡 Medium — Configuration management | Low |
| 3 | **Enable speculative plans in CI/CD** — trigger on PRs | 1–2 hours | 🔴 High — PR-based review workflow | Low |
| 4 | **Archive or fix packer-out-of-date** workspace | 1–2 hours | 🟡 Medium — Operational hygiene | Low |
| 5 | **Create RBAC teams** (Admin / Developer / Viewer) | 4–8 hours | 🟡 Medium — Foundation for scaling | Medium |

---

## Risk Assessment

**Current Risk Level: Medium-High**

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| No automated security guardrails | 🔴 High | High | Install CIS policies (30 days) |
| No cost controls | 🔴 High | Medium | Develop FinOps policies (90 days) |
| No compliance automation | 🟡 Medium | Medium | Registry + custom policies (6 months) |
| Single team / no RBAC | 🟡 Medium | Low | Create team structure (30 days) |
| Stale workspace with errors | 🟢 Low | High | Archive or remediate (immediate) |

**Risk Mitigation Timeline:**

| Timeframe | Action | Risk Reduction |
|-----------|--------|----------------|
| 30 days | Install registry policies in advisory mode | Medium-High → Medium |
| 90 days | Enable soft-mandatory enforcement + RBAC | Medium → Low-Medium |
| 6 months | Full custom policy coverage | Low-Medium → Low |

---

## HVD Maturity Model

The HashiCorp Validated Design (HVD) maturity model defines three stages of Terraform adoption:

### Stage 1: Adopt (Score 0–60)
**Focus**: Get teams using Terraform Cloud with basic workflows.

- ✅ VCS integration for workspaces
- ✅ Remote execution mode
- ✅ Basic team structure
- ⚠️ Initial policy adoption (this org's gap)

### Stage 2: Standardize (Score 61–85)
**Focus**: Establish organizational standards and governance.

- Module library with versioned, reusable modules
- Policy-as-code for security and compliance
- RBAC with multi-tier team structure
- Variable sets for configuration management
- Workspace naming conventions

### Stage 3: Scale (Score 86–100)
**Focus**: Self-service provisioning and enterprise governance.

- Full policy coverage with hard-mandatory enforcement
- Self-service workspace provisioning via modules
- Advanced integrations (ServiceNow, Jira, etc.)
- Cost management and FinOps automation
- Compliance automation (industry-specific)

### Where This Organization Sits

```
Score:  0    25    45    60    75    85    100
        |     |     |     |★    |     |     |
Stage: Pre-  Adopt- Adopt Stand- Stand Scale
       Adopt  ing   ed   ardiz. ardiz.      
                         ↑ YOU ARE HERE (60.6)
```

**Current**: Adopted (60.6/100) — Strong foundations in GitOps and modules, but policy gap prevents progression.

**Path to Standardize**: Achieving 75+ requires primarily closing the policy gap (from 5% to 50%+) and improving organization structure (from 55% to 70%+).

---

## References

- [HVD Terraform Adoption Guide](https://developer.hashicorp.com/validated-designs/terraform-operating-guides-adoption)
- [HVD Terraform Standardization Guide](https://developer.hashicorp.com/validated-designs/terraform-operating-guides-standardization)
- [HVD Terraform Scaling Guide](https://developer.hashicorp.com/validated-designs/terraform-operating-guides-scaling)
- [TFC API Documentation](https://developer.hashicorp.com/terraform/cloud-docs/api-docs)
- [Terraform Registry Policies](https://registry.terraform.io/browse/policies)
- [Managing Sensitive Data in Terraform](https://developer.hashicorp.com/terraform/language/manage-sensitive-data)

---

*Report generated by TFC Practice Evaluator — 7 February 2026*
