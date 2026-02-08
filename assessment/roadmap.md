# Implementation Roadmap: hashicorp-wwtfo-demo-platform-prod

**Created**: 7 February 2026  
**Organization**: hashicorp-wwtfo-demo-platform-prod  
**Current Score**: 60.6/100 (Adopted)  
**6-Month Target**: 75+/100 (Standardizing)  
**12-Month Target**: 85+/100 (Standardized)

---

## Executive Summary

This roadmap provides a structured path to advance the `hashicorp-wwtfo-demo-platform-prod` organization from **Adopted** (60.6/100) to **Standardizing** (75+) within 6 months. The primary lever is policy adoption, which currently scores 5% and accounts for 25% of the overall weight.

### Timeline Overview

```
Month:    1         2         3         4         5         6         12
          |         |         |         |         |         |         |
Phase 1:  |████████|
          Immediate (30 days)
          +5-8 pts: Policies, Variable Sets, RBAC

Phase 2:            |█████████████████|
                    Short-term (90 days)
                    +8-12 pts: Custom Policies, Lifecycle, GitOps

Phase 3:                                |█████████████████████████████|
                    Medium-term (6 months)
                    +5-8 pts: Compliance, Advanced Governance

Phase 4:                                                              |→
                    Long-term Vision (12 months)
                    Target: 85+ (Standardized)

Score:    60.6 ──→ 66 ──→ 72 ──→ 75+ ──→ 78 ──→ 82 ──→ 85+
```

### Impact by Category

| Category | Current | 30-Day | 90-Day | 6-Month | 12-Month |
|----------|---------|--------|--------|---------|----------|
| GitOps & VCS (25%) | 84% | 84% | 86% | 88% | 92% |
| Module Library (20%) | 92.5% | 92.5% | 93% | 94% | 95% |
| Policy-as-Code (25%) | 5% | 20% | 45% | 65% | 80% |
| Organization (15%) | 55% | 65% | 72% | 78% | 85% |
| Operations (15%) | 77.5% | 80% | 83% | 86% | 90% |
| **Weighted Total** | **60.6** | **66.1** | **72.6** | **78.9** | **87.5** |

---

## Current State Assessment

### Strengths to Build On

| Strength | Score | Leverage |
|----------|-------|---------|
| Module Library | 92.5% | Use as template for policy development processes |
| VCS Integration | 100% | Foundation for policy-as-code via VCS workflow |
| Run Success Rate | 94.1% | Stable platform for introducing policy checks |
| Speculative Plans | 100% | Ready for PR-based policy review workflow |

### Critical Gaps

| Gap | Current Score | Target (6-month) | Impact on Overall |
|-----|---------------|-------------------|-------------------|
| Policy-as-Code | 5% | 65% | +15 weighted points |
| RBAC / Teams | None | Multi-tier | +3.5 weighted points |
| Variable Sets | 0 attached | All attached | +1.5 weighted points |
| Workspace Lifecycle | No policy | Defined process | +1 weighted point |

---

## Phase 1: Immediate Actions (30 Days)

**Goal**: Quick wins that require minimal effort and demonstrate immediate value.  
**Expected Score Change**: 60.6 → ~66 (+5.4 points)

### Task 1.1: Install AWS CIS Benchmarks

| Attribute | Detail |
|-----------|--------|
| **Priority** | 🔴 Critical |
| **Effort** | 2–4 hours |
| **Owner** | Platform Engineering |
| **Category Impact** | Policy: 5% → 15% |

**Steps:**
1. Navigate to TFC Organization Settings → Policy Sets
2. Click "Connect a new policy set" → "Choose from registry"
3. Select `hashicorp/cis-policy-set-aws`
4. Set enforcement to **advisory** (non-blocking)
5. Apply to all workspaces (global scope)
6. Monitor policy check results for 2 weeks
7. Review any advisory failures and create remediation tickets
8. After 2 weeks, upgrade critical policies to **soft-mandatory**

**Success Criteria:**
- [ ] AWS CIS policy set installed and active
- [ ] Advisory checks running on all workspaces
- [ ] Initial findings documented

### Task 1.2: Install Cloud Foundational Policies

| Attribute | Detail |
|-----------|--------|
| **Priority** | 🔴 High |
| **Effort** | 2–4 hours |
| **Owner** | Platform Engineering |
| **Category Impact** | Policy: 15% → 20% |

**Steps:**
1. Install `hashicorp/foundational-policy-set` from registry
2. Configure in advisory mode
3. Apply globally
4. Review cross-cloud governance patterns

**Success Criteria:**
- [ ] Foundational policy set installed
- [ ] Cross-cloud checks running

### Task 1.3: Attach Variable Sets to Workspaces

| Attribute | Detail |
|-----------|--------|
| **Priority** | 🟡 Medium |
| **Effort** | 1–2 hours |
| **Owner** | Platform Engineering |
| **Category Impact** | Organization: 55% → 62% |

**Steps:**
1. Audit all 5 existing variable sets — identify their purpose
2. For each variable set, determine which workspaces need it
3. Attach variable sets via TFC UI or API:
   ```bash
   # Example API call to attach variable set to workspace
   curl -s \
     --header "Authorization: Bearer $TFC_TOKEN" \
     --header "Content-Type: application/vnd.api+json" \
     --request POST \
     "https://app.terraform.io/api/v2/varsets/{varset-id}/relationships/workspaces" \
     --data '{"data":[{"type":"workspaces","id":"ws-xxx"}]}'
   ```
4. Verify variables are available in workspace runs

**Success Criteria:**
- [ ] All 5 variable sets reviewed
- [ ] Appropriate variable sets attached to workspaces
- [ ] Variable set attachment count > 0

### Task 1.4: Create RBAC Team Structure

| Attribute | Detail |
|-----------|--------|
| **Priority** | 🟡 Medium |
| **Effort** | 4–8 hours |
| **Owner** | Platform Engineering + Security |
| **Category Impact** | Organization: 62% → 68% |

**Steps:**
1. Create three new teams:
   - **platform-admins** — Full admin access, manage workspaces/policies/teams
   - **platform-developers** — Read/write on workspaces, create runs, view state
   - **platform-viewers** — Read-only access to workspaces and runs
2. Assign appropriate workspace permissions per team
3. Configure organization access levels
4. Set team visibility to "organization" (not "secret")
5. Document team roles and responsibilities
6. Migrate key users from `ddr-all-users-team` to appropriate teams

**Success Criteria:**
- [ ] 3+ teams created with distinct access levels
- [ ] Team visibility set to "organization"
- [ ] Organization access configured
- [ ] Key users assigned to appropriate teams

### Task 1.5: Remediate Stale Workspace

| Attribute | Detail |
|-----------|--------|
| **Priority** | 🟡 Medium |
| **Effort** | 1–2 hours |
| **Owner** | Platform Engineering |
| **Category Impact** | Operations: 77.5% → 80% |

**Steps:**
1. Review `packer-out-of-date` workspace — last active July 2025
2. Determine if workspace is still needed:
   - **If needed**: Fix configuration errors, update Terraform version to 1.9.6, enable auto-apply
   - **If not needed**: Archive or delete the workspace
3. Update Terraform version from `~>1.10.0` constraint to exact version

**Success Criteria:**
- [ ] Workspace either fixed or archived
- [ ] No stale workspaces remaining
- [ ] 100% active workspace rate

---

## Phase 2: Short-Term (90 Days)

**Goal**: Develop custom policies for critical governance gaps and establish operational processes.  
**Expected Score Change**: ~66 → ~73 (+7 points)

### Task 2.1: Develop FinOps Cost Control Policies

| Attribute | Detail |
|-----------|--------|
| **Priority** | 🔴 High |
| **Effort** | 1–2 weeks |
| **Owner** | Platform Engineering + FinOps |
| **Category Impact** | Policy: 20% → 30% |

**Policy Examples:**
```hcl
# Restrict EC2 instance types to approved list
policy "restrict-ec2-instance-types" {
  source = "./restrict-ec2-instance-types.sentinel"
  enforcement_level = "soft-mandatory"
}

# Enforce S3 lifecycle policies
policy "require-s3-lifecycle" {
  source = "./require-s3-lifecycle.sentinel"
  enforcement_level = "advisory"
}
```

**Steps:**
1. Define approved instance types per environment (dev/staging/prod)
2. Write Sentinel policies for:
   - EC2 instance type restrictions
   - S3 lifecycle policy requirements
   - Auto-scaling configuration validation
   - RDS instance size limits for non-production
3. Test in advisory mode for 2 weeks
4. Promote to soft-mandatory

**Success Criteria:**
- [ ] 4+ FinOps policies developed and tested
- [ ] Policies in advisory mode on all workspaces
- [ ] Cost impact baseline established

### Task 2.2: Develop Tagging Standard Policies

| Attribute | Detail |
|-----------|--------|
| **Priority** | 🔴 High |
| **Effort** | 1 week |
| **Owner** | Platform Engineering |
| **Category Impact** | Policy: 30% → 35% |

**Required Tags:**
| Tag | Format | Purpose |
|-----|--------|---------|
| `cost-center` | String (e.g., `CC-1234`) | Cost allocation |
| `environment` | Enum: `dev`, `staging`, `prod` | Environment tracking |
| `owner` | Email format | Accountability |
| `project` | String from approved list | Project tracking |

**Steps:**
1. Define mandatory tag schema
2. Write Sentinel policy enforcing required tags on all taggable resources
3. Test with advisory mode
4. Coordinate with teams on tag values
5. Promote to soft-mandatory

**Success Criteria:**
- [ ] Tag policy deployed in advisory mode
- [ ] All existing resources catalogued for tag compliance
- [ ] Remediation plan for non-compliant resources

### Task 2.3: Develop Security Group Hygiene Policies

| Attribute | Detail |
|-----------|--------|
| **Priority** | 🔴 High |
| **Effort** | 1 week |
| **Owner** | Platform Engineering + Security |
| **Category Impact** | Policy: 35% → 40% |

**Policies:**
- Block `0.0.0.0/0` ingress on sensitive ports (22, 3389, 3306, 5432)
- Require specific CIDR ranges for production access
- Enforce egress restrictions
- Validate security group descriptions

**Success Criteria:**
- [ ] Security group policies deployed
- [ ] Zero open-to-world security group rules allowed on sensitive ports

### Task 2.4: Establish Workspace Lifecycle Policy

| Attribute | Detail |
|-----------|--------|
| **Priority** | 🟡 Medium |
| **Effort** | 4–8 hours |
| **Owner** | Platform Engineering |
| **Category Impact** | Operations: 80% → 83% |

**Lifecycle Stages:**

| Stage | Criteria | Action |
|-------|----------|--------|
| Active | Runs within last 30 days | Normal operations |
| Warning | No runs in 60 days | Send notification to owner |
| Stale | No runs in 90 days | Review for archival |
| Archive | Confirmed no longer needed | Lock and document |

**Steps:**
1. Document lifecycle policy
2. Create monitoring script (weekly check for stale workspaces)
3. Set up notification workflow
4. Apply retroactively to current workspaces

**Success Criteria:**
- [ ] Lifecycle policy documented and approved
- [ ] Monitoring script running weekly
- [ ] All current workspaces classified

### Task 2.5: Upgrade CIS Policies to Soft-Mandatory

| Attribute | Detail |
|-----------|--------|
| **Priority** | 🟡 Medium |
| **Effort** | 2–4 hours |
| **Owner** | Platform Engineering + Security |
| **Category Impact** | Policy: 40% → 45% |

**Steps:**
1. Review 2+ weeks of advisory policy check results
2. Identify any legitimate failures that need exceptions
3. Create policy overrides for approved exceptions
4. Upgrade AWS CIS and Foundational policies to soft-mandatory

**Success Criteria:**
- [ ] Policies upgraded to soft-mandatory
- [ ] Exception process documented
- [ ] No false-positive blocks

---

## Phase 3: Medium-Term (6 Months)

**Goal**: Comprehensive governance coverage and advanced operational practices.  
**Expected Score Change**: ~73 → ~79 (+6 points)

### Task 3.1: Develop Data Protection Policies

| Attribute | Detail |
|-----------|--------|
| **Priority** | 🔴 High |
| **Effort** | 1–2 weeks |
| **Owner** | Platform Engineering + Security |
| **Category Impact** | Policy: 45% → 55% |

**Policies:**
- Require encryption-at-rest for all storage (S3, EBS, RDS)
- Enforce KMS key usage (block default AWS encryption keys)
- Validate backup retention periods (minimum 30 days for production)
- Block public access to databases and storage

**Success Criteria:**
- [ ] Data protection policies in soft-mandatory mode
- [ ] All storage resources have encryption-at-rest
- [ ] No publicly accessible databases

### Task 3.2: Develop Demo Showcase Policies

| Attribute | Detail |
|-----------|--------|
| **Priority** | 🟡 Medium |
| **Effort** | 1 week |
| **Owner** | Platform Engineering + Sales Engineering |
| **Category Impact** | Policy: 55% → 60% |

**Purpose**: Showcase TFC policy capabilities in customer demonstrations.

**Demo Policy Set Should Include:**
1. Multi-cloud security policy (show cross-provider governance)
2. Cost control policy (demonstrate FinOps automation)
3. Compliance policy (show audit-ready infrastructure)
4. Custom workflow policy (demonstrate business logic enforcement)

**Success Criteria:**
- [ ] Demo policy set created and tested
- [ ] Demo script documented for SE use
- [ ] Policies demonstrate advisory → soft-mandatory → hard-mandatory workflow

### Task 3.3: Implement Advanced GitOps Patterns

| Attribute | Detail |
|-----------|--------|
| **Priority** | 🟡 Medium |
| **Effort** | 1–2 weeks |
| **Owner** | Platform Engineering |
| **Category Impact** | GitOps: 84% → 88% |

**Steps:**
1. Evaluate enabling VCS-triggered runs alongside API triggers
2. Implement TFC run triggers for workspace dependencies
3. Document the hybrid API + VCS workflow pattern
4. Consider no-code module provisioning for standard deployments

**Success Criteria:**
- [ ] Run trigger dependencies configured where appropriate
- [ ] Workflow pattern documented

### Task 3.4: Module Governance & Lifecycle

| Attribute | Detail |
|-----------|--------|
| **Priority** | 🟢 Low |
| **Effort** | 1 week |
| **Owner** | Platform Engineering |
| **Category Impact** | PMR: 92.5% → 94% |

**Steps:**
1. Fix 2 module ingestion failures (all-boundary-use-cases, invisimart-waypoint-template-nocode-ecs)
2. Document module usage patterns across demo scenarios
3. Identify candidates for public registry publication
4. Establish deprecation process for obsolete modules

**Success Criteria:**
- [ ] Zero module ingestion failures
- [ ] Module documentation published
- [ ] Deprecation process defined

### Task 3.5: Upgrade Critical Policies to Hard-Mandatory

| Attribute | Detail |
|-----------|--------|
| **Priority** | 🟡 Medium |
| **Effort** | 4–8 hours |
| **Owner** | Platform Engineering + Security |
| **Category Impact** | Policy: 60% → 65% |

**Candidates for Hard-Mandatory:**
- Block `0.0.0.0/0` on sensitive ports (security groups)
- Require encryption-at-rest on all production storage
- Enforce mandatory tagging on all resources

**Success Criteria:**
- [ ] Critical policies at hard-mandatory enforcement
- [ ] Zero security group violations in production

---

## Phase 4: Long-Term Vision (12 Months)

**Target Score: 85+ (Standardized)**

### Capabilities to Achieve

| Capability | Description | Category Impact |
|------------|-------------|-----------------|
| **Self-Service Provisioning** | Teams provision workspaces via no-code modules | PMR +2%, Org +5% |
| **Full Policy Coverage** | 80%+ policy coverage with multi-tier enforcement | Policy: 65% → 80% |
| **Compliance Automation** | Industry-specific policies (ISM, APRA, HIPAA as applicable) | Policy +10% |
| **Advanced RBAC** | Project-level permissions, SSO integration | Org: 78% → 85% |
| **FinOps Maturity** | Cost policies, showback/chargeback, budget alerts | Policy +5% |
| **Terraform Version Management** | Automated version upgrades, constraint standardization | Ops: 86% → 90% |

### Industry Compliance Policies (If Applicable)

| Framework | Applicability | Effort | Priority |
|-----------|--------------|--------|----------|
| Australian ISM Essential Eight | Government/Defence customers | 2–4 weeks | Conditional |
| APRA CPS 234 | Financial services customers | 2–4 weeks | Conditional |
| HIPAA | Healthcare customers | 2–4 weeks | Conditional |
| FedRAMP | US government customers | 2–4 weeks | Conditional |
| GDPR | European operations | 2–4 weeks | Conditional |
| PCI-DSS | Payment processing | 2–4 weeks | Conditional |

---

## Quick Wins Register

| # | Action | Effort | Impact | ROI | Timeline |
|---|--------|--------|--------|-----|----------|
| 1 | Install AWS CIS Benchmarks (advisory) | 2–4 hrs | 🔴 High | Immediate security baseline | Week 1 |
| 2 | Install Cloud Foundational Policies (advisory) | 2–4 hrs | 🟡 Medium | Cross-cloud governance | Week 1 |
| 3 | Attach variable sets to workspaces | 1–2 hrs | 🟡 Medium | Configuration management | Week 1 |
| 4 | Archive/fix packer-out-of-date workspace | 1–2 hrs | 🟡 Medium | Operational hygiene | Week 1 |
| 5 | Create Admin/Developer/Viewer teams | 4–8 hrs | 🟡 Medium | RBAC foundation | Week 2 |
| 6 | Change team visibility to "organization" | 30 min | 🟢 Low | Better collaboration | Week 1 |
| 7 | Document API-driven workflow pattern | 2–4 hrs | 🟢 Low | Knowledge transfer | Week 2 |
| 8 | Pin Terraform version (remove constraints) | 1 hr | 🟢 Low | Version stability | Week 1 |

**Total Quick Win Effort**: ~20–30 hours  
**Expected Score Impact**: +5–8 points (60.6 → 66–69)

---

## Success Metrics & KPIs

| Metric | Current | 30-Day Target | 90-Day Target | 6-Month Target |
|--------|---------|---------------|---------------|----------------|
| **Overall Score** | 60.6 | 66+ | 73+ | 79+ |
| **Policy Coverage** | 0% | 100% (advisory) | 100% (soft-mandatory) | 100% (mixed enforcement) |
| **Policy Sets** | 0 | 2+ (registry) | 6+ (registry + custom) | 10+ (comprehensive) |
| **RBAC Teams** | 1 | 3+ | 4+ | 5+ |
| **Variable Sets Attached** | 0 | 5+ | 5+ | 8+ |
| **Active Workspace %** | 75% | 100% | 100% | 100% |
| **Run Success Rate** | 94.1% | 95%+ | 95%+ | 97%+ |
| **Terraform Version** | 1.9.6 | 1.9.6 (consistent) | 1.10.x+ | 1.11.x+ |
| **Stale Workspaces** | 1 | 0 | 0 | 0 |
| **Module Health** | 99.8% | 100% | 100% | 100% |

---

## Resource Requirements

### Team

| Role | Effort (Phase 1) | Effort (Phase 2) | Effort (Phase 3) | Total |
|------|-------------------|-------------------|-------------------|-------|
| Platform Engineer | 20 hours | 80 hours | 60 hours | 160 hours |
| Security Engineer | 4 hours | 40 hours | 40 hours | 84 hours |
| FinOps Analyst | 0 hours | 20 hours | 10 hours | 30 hours |
| Team Lead / Reviewer | 8 hours | 16 hours | 12 hours | 36 hours |
| **Total** | **32 hours** | **156 hours** | **122 hours** | **310 hours** |

### Time

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1 | 30 days | Registry policies, RBAC, variable sets, workspace cleanup |
| Phase 2 | 60 days | Custom FinOps/security/tagging policies, lifecycle process |
| Phase 3 | 90 days | Data protection, demo showcase, advanced GitOps, compliance |
| Phase 4 | 180 days | Self-service, full compliance, advanced automation |

### Budget Estimates

| Item | Estimate | Notes |
|------|----------|-------|
| Registry policies | $0 | Included in TFC subscription |
| Custom policy development | ~$15,000–25,000 | Based on 310 hours at blended rate |
| Terraform version upgrades | $0 | No additional licensing |
| Training & enablement | ~$5,000–10,000 | Team training on Sentinel/OPA |
| **Total Estimated Investment** | **$20,000–35,000** | Over 6 months |

**Expected ROI:**
- 20–40% cloud cost reduction through FinOps policies
- 80% reduction in audit preparation time
- 90% reduction in security misconfiguration incidents
- Improved demo effectiveness leading to higher conversion rates

---

## Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|------------|--------|------------|
| 1 | Policy false positives block legitimate runs | Medium | 🔴 High | Start in advisory mode; 2-week validation before enforcement |
| 2 | RBAC migration disrupts existing users | Low | 🟡 Medium | Gradual rollout; keep ddr-all-users-team active during transition |
| 3 | Custom policy development takes longer than estimated | Medium | 🟡 Medium | Prioritize FinOps and security; defer compliance to Phase 3/4 |
| 4 | Team resistance to new governance | Low | 🟡 Medium | Communicate benefits; involve stakeholders early; start advisory |
| 5 | Terraform version upgrade breaks workspaces | Low | 🔴 High | Test upgrades in dev first; use speculative plans for validation |
| 6 | Registry policy updates cause unexpected failures | Low | 🟡 Medium | Pin policy set versions; review release notes before upgrading |
| 7 | Stale workspace contains active resources | Low | 🔴 High | Review state before archiving; confirm with resource owners |

---

## Appendix A: Enforcement Strategy

**Progressive Enforcement Model:**

```
Week 1-2:     Install policies → Advisory Mode (no blocking)
              └─ Monitor, collect data, identify failures

Week 3-4:     Review findings → Create exceptions for legitimate cases
              └─ Document exception justifications

Month 2:      Upgrade to Soft-Mandatory (team members can override)
              └─ Track override frequency, review monthly

Month 3-4:    Review overrides → Fix root causes
              └─ Reduce override rate to <5%

Month 5-6:    Upgrade critical policies to Hard-Mandatory
              └─ Zero tolerance for security violations
              └─ Soft-mandatory for cost/tagging
```

## Appendix B: Policy Development Workflow

```
1. Identify Gap
   └─ From gap analysis, audit findings, or incidents

2. Define Policy
   └─ Write policy in Sentinel or OPA
   └─ Include test cases (passing and failing)

3. Version Control
   └─ Store in VCS repository (e.g., github.com/org/tfc-policies)
   └─ Use branches for development

4. Test
   └─ Run policy tests locally
   └─ Deploy to test workspace in advisory mode
   └─ Validate against known-good and known-bad configurations

5. Deploy
   └─ Create policy set in TFC
   └─ Link to VCS repository
   └─ Set initial enforcement level (advisory)

6. Monitor
   └─ Track pass/fail rates
   └─ Review advisory failures
   └─ Collect feedback from teams

7. Enforce
   └─ Upgrade to soft-mandatory after validation
   └─ Upgrade to hard-mandatory for critical policies
```

## Appendix C: Key Contacts & References

| Resource | Link |
|----------|------|
| HVD Adoption Guide | https://developer.hashicorp.com/validated-designs/terraform-operating-guides-adoption |
| HVD Standardization Guide | https://developer.hashicorp.com/validated-designs/terraform-operating-guides-standardization |
| HVD Scaling Guide | https://developer.hashicorp.com/validated-designs/terraform-operating-guides-scaling |
| Sentinel Documentation | https://docs.hashicorp.com/sentinel |
| TFC Policy Sets API | https://developer.hashicorp.com/terraform/cloud-docs/api-docs/policy-sets |
| Terraform Registry Policies | https://registry.terraform.io/browse/policies |
| Managing Sensitive Data | https://developer.hashicorp.com/terraform/language/manage-sensitive-data |

---

*Roadmap generated by TFC Practice Evaluator — 7 February 2026*
