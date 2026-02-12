# 6-Month Implementation Roadmap: TFC Maturity Advancement — Adopt to Standardize

## Executive Summary

This roadmap outlines a structured 6-month plan to advance the organization's Terraform Cloud (TFC) maturity from **Adopt** stage to **Standardize** stage across all practice areas. The improvement focuses on implementing GitOps workflows, policy enforcement, governance controls, and operational scaling across the organization.

### Current State Assessment (Stage: Adopt)
- **GitOps Workflows:** Basic VCS integration exists; missing advanced branching strategies and PR automation
- **Policy & Module Reuse:** Strong module registry; inconsistent module usage patterns
- **Policy Engine:** No Sentinel policy enforcement; no cost controls or tagging governance
- **Organization & Governance:** Minimal team structure; limited RBAC implementation
- **Operational Excellence:** Gaps in state management, runbooks, and lifecycle governance

### Target State Assessment (Stage: Standardize)
- **GitOps Workflows:** Full implementation with sophisticated branching and PR automation
- **Policy & Module Reuse:** Standardized, governed module consumption across all teams
- **Policy Engine:** Comprehensive Sentinel policies for cost, compliance, and tagging
- **Organization & Governance:** Mature team structure with delegated permissions and clear ownership
- **Operational Excellence:** Robust lifecycle management, disaster recovery, and team enablement

### Stage Progression Timeline
| Milestone | Timeline | Stage | Focus Area |
|-----------|----------|-------|-----------|
| Current State | Week 0 | Adopt | Baseline |
| Phase 1 Complete | Week 2 | Adopt (strengthened) | Quick Policy Wins |
| Phase 2 Complete | Week 6 | Adopt → Standardize (emerging) | Foundation & Workflows |
| Phase 3 Complete | Month 3 | Standardize (emerging) | Governance & Policies |
| Phase 4 Complete | Month 6 | Standardize | Scaling & Automation |

---

## PHASE 1: Quick Wins (Week 1-2)

### Objective
Establish foundational governance and eliminate low-hanging operational friction. This phase delivers immediate value with minimal implementation complexity.

### Key Initiatives

#### 1.1 Deploy Core Sentinel Policies
**Timeline:** Day 1-2  
**Effort:** 8 hours  
**Owner:** Security & Governance Team

Deploy three foundational Sentinel policies to establish governance framework:

**Policy 1: CIS AWS Foundations Policy**
```hcl
import "tfplan"
import "json"

# Enforce tagging standards from root module variables
policy "require_cis_tagging" {
  enforcement_level = "soft_mandatory"
}

# Verify encrypted state and data sources
policy "enforce_encryption_at_rest" {
  enforcement_level = "hard_mandatory"
}

main = rule {
  all_resources_have_tags and state_encryption_enabled
}

# Helper rules
all_resources_have_tags = rule {
  length(filter(tfplan.resource_changes, "change.after.tags" else null)) 
    == length(tfplan.resource_changes)
}

state_encryption_enabled = rule {
  all tfplan.resources.aws_s3_bucket as bucket {
    bucket.server_side_encryption_configuration is not empty
  }
}
```

**Policy 2: Cost Control - Large Instance Prevention**
```hcl
import "tfplan"

policy "prevent_oversized_instances" {
  enforcement_level = "soft_mandatory"
}

disallowed_instance_types = [
  "db.r6i.16xlarge",
  "db.r6i.24xlarge",
  "r6i.16xlarge",
  "r6i.24xlarge",
  "u-*"
]

main = rule {
  all tfplan.resources.aws_instance as i {
    i.instance_type not in disallowed_instance_types
  } and
  all tfplan.resources.aws_db_instance as db {
    db.instance_class not in disallowed_instance_types
  }
}
```

**Policy 3: Resource Naming Convention**
```hcl
import "tfplan"
import "strings"

policy "enforce_naming_conventions" {
  enforcement_level = "soft_mandatory"
}

valid_resource_pattern = "^[a-z0-9][a-z0-9_]{0,62}[a-z0-9]$"

main = rule {
  all tfplan.resources as resource_type, resources {
    all resources as name, resource {
      valid_name(name)
    }
  }
}

valid_name = func(name) {
  strings.matches(name, valid_resource_pattern)
}
```

**Deliverables:**
- 3 Sentinel policies deployed to org-level policy sets
- Policy Set ID: `ps-cis-aws-foundations` created and attached
- Soft mandatory enforcement for Day 1-2 (allow overrides for testing)

**Success Criteria:**
- Policies appear in TFC UI under "Policies"
- Policy checks run on next plan operations
- Zero blocking on existing workspaces (soft mandatory)

#### 1.2 Attach Variable Sets to Existing Workspaces
**Timeline:** Day 1  
**Effort:** 3 hours  
**Owner:** Platform Engineering Team

Centralize environment and Terraform variables through Variable Sets to enable consistency:

**Variable Set: org-core-env-vars**
- Variables: `TF_LOG=INFO`, `TF_LOG_PATH=/tmp/terraform.log`
- Scope: Global (all workspaces)
- Status: Active

**Variable Set: org-aws-credentials**
- Variables: `AWS_REGION`, `AWS_ASSUME_ROLE_ARN` (sensitive)
- Scope: All AWS-focused workspaces
- Status: Active

**Attachment Strategy:**
1. Create 2 global variable sets
2. Attach to all active workspaces in single operation
3. Verify through workspace variables page

**Expected Workspaces Affected:** 12-15 workspaces  
**Risk:** Zero impact (environment variables only, no state changes)

**Deliverables:**
- Variable Set IDs: `vs-core-env` and `vs-aws-creds`
- Workspace count with attached sets: 12-15
- Documentation of variable purpose and scope

**Success Criteria:**
- All target workspaces show attached variable sets in UI
- Next plan operation logs show TF_LOG output
- No workspace errors or plan failures

#### 1.3 Investigate and Remediate Stale Workspaces
**Timeline:** Day 2-3  
**Effort:** 6 hours  
**Owner:** Platform Engineering Team

Identify and address workspaces with no runs in >90 days:

**Discovery Queries:**
```
List workspaces with last run >90 days ago
- ws-legacy-vpc-* (4 workspaces, last run 6+ months ago)
- ws-staging-experiment-* (2 workspaces, test runs only)
- ws-archive-* (3 workspaces, manually archived)
```

**Remediation Actions:**
1. **Archive stale workspaces:** ws-legacy-vpc-*, ws-staging-experiment-*
   - Action: Set workspace to locked state
   - Impact: No new plans/applies possible
   - Owner: Assigned team

2. **Cleanup test workspaces:** Destroy state for ws-archive-*
   - Action: Discard state through API
   - Reason: Never reached production
   - Verification: State cleared in TFC UI

3. **Documentation:**
   - Create workspace archive checklist
   - Document cleanup procedure
   - Record decisions in change log

**Deliverables:**
- Stale workspace inventory (spreadsheet)
- Remediation actions log
- Archive/cleanup verification report

**Success Criteria:**
- All identified stale workspaces processed
- No orphaned state remaining
- Documentation complete for future reference

### Phase 1 Maturity Impact
- **Policy-as-Code:** Moves from zero governance to foundational policy framework — first step within Adopt stage
- **Organization & Teams:** Workspace cleanup reduces operational debt
- **Operations & Health:** Variable set standardization improves consistency

### Phase 1 Effort Summary
- **Total Effort:** 17 hours
- **Team Capacity:** 2 FTE weeks
- **Risk Level:** Low
- **Dependencies:** None
- **Rollback Complexity:** Simple (deactivate policies, remove varsets)

---

## PHASE 2: Foundation & Workflows (Week 3-6)

### Objective
Establish mature team structures, implement advanced GitOps workflows, and standardize module ingestion patterns. This phase builds the operational foundation for scaling.

### Key Initiatives

#### 2.1 Implement Team-Based RBAC
**Timeline:** Week 3-4  
**Effort:** 12 hours  
**Owner:** Platform Engineering & Security

Establish role-based access control with team segregation:

**Team Structure:**
```
Org: org-terraform-prod
├── Team: platform-admins (Admins)
│   ├── Manage: org settings, SSO, billing
│   ├── Members: 3 senior engineers
│   └── Permissions: Manage workspaces, state, policies
│
├── Team: platform-engineers (Developers)
│   ├── Manage: VCS, modules, workspaces
│   ├── Members: 5 infrastructure engineers
│   └── Permissions: Create/edit workspaces, apply runs
│
├── Team: app-team-a (Developers)
│   ├── Manage: app-team-a-* workspaces only
│   ├── Members: 2 application engineers
│   └── Permissions: Plan and apply only on assigned workspaces
│
└── Team: app-team-b (Developers)
    ├── Manage: app-team-b-* workspaces only
    ├── Members: 2 application engineers
    └── Permissions: Plan and apply only on assigned workspaces
```

**Implementation Steps:**
1. Create 4 teams in TFC organization
2. Assign users using SSO group mapping
3. Configure workspace-level team access
4. Document access policy and approval workflows

**Variable Set Scope:**
- Platform varsets (org-wide): Visible to platform-admins only initially, promote to all teams
- Team-specific varsets: Scoped to individual teams only

**Deliverables:**
- 4 teams created with documented members
- RBAC matrix (who can do what on which resources)
- SSO group mapping configuration
- Team access verification report

**Success Criteria:**
- RBAC enforced in TFC (users can't access unauthorized workspaces)
- Team members can self-serve on assigned workspaces
- Platform admins maintain org-wide control

#### 2.2 Advanced GitOps Workflow Implementation
**Timeline:** Week 4-5  
**Effort:** 14 hours  
**Owner:** Platform Engineering Team

Implement sophisticated VCS integration with branch protection and PR automation:

**Workflow Architecture:**
```
GitHub Repository: terraform-infrastructure

main branch (production)
├── Branch Protection Rules:
│   ├── Require pull request reviews: 2 approvals
│   ├── Require code owner review: true
│   ├── Require status checks: TFC plan passed
│   ├── Dismiss stale reviews: true
│   └── Restrict who can push: platform-admins only
│
develop branch (staging)
├── Branch Protection Rules:
│   ├── Require pull request reviews: 1 approval
│   ├── Require status checks: TFC plan passed
│   └── Allow self-review: false
│
feature/* branches (development)
└── Working branches for feature development

TFC Workspace Workflow:
- Workspace: ws-prod-* (linked to main branch)
  ├── VCS Trigger: Automatic on tag push (v*.*.*)
  ├── Auto-apply: Enabled (after approvals)
  ├── Notifications: Slack on plan completion
  └── Cost estimation: Enabled

- Workspace: ws-staging-* (linked to develop branch)
  ├── VCS Trigger: Automatic on push
  ├── Auto-apply: Disabled (manual review)
  ├── Notifications: Slack on plan completion
  └── Cost estimation: Enabled

- Workspace: ws-feature-* (linked to feature/* branches)
  ├── VCS Trigger: Manual plans only
  ├── Auto-apply: Disabled
  ├── Notifications: Email on completion
  └── Cost estimation: Enabled
```

**GitHub Actions Integration:**
```yaml
# .github/workflows/terraform-plan.yml
name: Terraform Plan
on:
  pull_request:
    paths:
      - 'terraform/**'
jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.6.0
      - run: terraform plan
      - uses: actions/github-script@v6
        with:
          script: |
            github.rest.pulls.createReview({
              pull_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: 'Terraform plan completed. See TFC for details.',
              event: 'COMMENT'
            })
```

**Workspace Tagging for Workflow Identification:**
```
Production workspaces: tags=prod,auto-apply,critical
Staging workspaces: tags=staging,manual-apply,non-critical
Feature workspaces: tags=feature,dev,experimental
```

**VCS Webhook Configuration:**
- Event: Push to branches
- Trigger TFC plans automatically
- Status checks: Require TFC plan success before merge
- Cost notifications: Slack integration

**Deliverables:**
- VCS repository with branch protection rules
- TFC workspace VCS connections (12-15 workspaces)
- GitHub Actions workflow definitions
- Slack integration for notifications
- Documentation: PR workflow guide for developers

**Success Criteria:**
- Developers can merge PRs only with TFC plan approval
- Automatic plans trigger on push to develop/main
- Cost estimates appear in PR comments
- Notification chain verified (Slack, GitHub)

#### 2.3 Promote Policy Sets and Establish Governance
**Timeline:** Week 5-6  
**Effort:** 10 hours  
**Owner:** Security & Governance Team

Transition policies from soft to hard mandatory enforcement:

**Policy Set Promotion Strategy:**

| Policy | Current | Week 5 | Week 6 | Target |
|--------|---------|--------|--------|--------|
| CIS AWS Foundations | Soft | Hard | Hard | Hard Mandatory |
| Cost Control | Soft | Soft | Hard | Hard Mandatory |
| Naming Conventions | Soft | Hard | Hard | Hard Mandatory |

**Promotion Process:**
1. Week 5: Monitor policy override rates
2. Monitor plan failures on policy violations
3. Adjust policies based on false positives
4. Week 6: Transition to hard mandatory
5. Document exceptions and approval workflows

**Exception Handling:**
- Policy Override Form: Required for hard mandatory violations
- Override Approvers: platform-admins, security-team
- Override Expiration: 30 days (requires renewal)
- Audit Log: All overrides tracked in change management system

**Deliverables:**
- Policy enforcement level changes in TFC
- Override approval workflow documentation
- Monitoring dashboard for policy violations
- Exceptions log with justification

**Success Criteria:**
- All policies at hard mandatory enforcement
- Override rate <5% of total plans
- Zero unapproved policy violations
- Audit trail complete for compliance

### Phase 2 Maturity Impact
- **GitOps & VCS:** VCS workflows, branch protection, and auto-apply strengthen Standardize-level practices
- **Module Library:** Module standardization progress continues
- **Policy-as-Code:** Hard mandatory policies and exception handling advance governance maturity
- **Organization & Teams:** Team RBAC structure establishes clear ownership boundaries
- **Operations & Health:** No change this phase — focus on governance foundation

### Phase 2 Effort Summary
- **Total Effort:** 36 hours
- **Team Capacity:** 2 FTE weeks
- **Risk Level:** Medium (RBAC requires careful testing)
- **Dependencies:** Phase 1 completion
- **Rollback Complexity:** Medium (can revert policy levels, RBAC changes reversible)

---

## PHASE 3: Governance & Policy Scaling (Month 2-3, Weeks 7-13)

### Objective
Implement comprehensive governance policies including custom tagging rules, cost controls, and module ingestion standards. Establish the compliance and cost management foundation.

### Key Initiatives

#### 3.1 Custom Tagging Policy and Enforcement
**Timeline:** Week 7-8  
**Effort:** 10 hours  
**Owner:** Security & Compliance Team

Deploy organization-wide tagging governance with Sentinel enforcement:

**Tagging Standard:**
```
Required Tags (all resources):
- environment: [dev, staging, prod]
- owner: [team-name]
- cost-center: [cc-xxxx]
- project: [project-name]
- compliance: [yes/no] (if applicable)
- backup-required: [yes/no]

Optional Tags:
- data-classification: [public, internal, confidential]
- dr-tier: [tier1, tier2, tier3]
- maintenance-window: [mon-fri-2am, 24/7, none]
```

**Sentinel Policy: Custom Tagging Enforcement**
```hcl
import "tfplan"

policy "enforce_required_tags" {
  enforcement_level = "hard_mandatory"
}

required_tags = {
  "environment": ["dev", "staging", "prod"],
  "owner": null,           # Must exist, any value acceptable
  "cost-center": null,
  "project": null,
  "compliance": ["yes", "no"],
  "backup-required": ["yes", "no"]
}

optional_tags = {
  "data-classification": ["public", "internal", "confidential"],
  "dr-tier": ["tier1", "tier2", "tier3"],
  "maintenance-window": ["mon-fri-2am", "24/7", "none"]
}

main = rule {
  all tfplan.resources as resource_type, resources {
    all resources as name, resource {
      check_required_tags(resource) and
      check_optional_tags(resource)
    }
  }
}

check_required_tags = func(resource) {
  tags = resource.change.after.tags else {}
  
  all required_tags as tag_key, allowed_values {
    # Tag must exist
    (tag_key in keys(tags)) and
    # If values specified, tag must match one of them (or null = any value)
    (allowed_values is null or tags[tag_key] in allowed_values)
  }
}

check_optional_tags = func(resource) {
  tags = resource.change.after.tags else {}
  
  all optional_tags as tag_key, allowed_values {
    # If tag exists, must be valid value
    (tag_key not in keys(tags)) or
    (tags[tag_key] in allowed_values)
  }
}
```

**Tag Validation Workflow:**
```
Developer creates resource with tags
    ↓
Terraform plan runs
    ↓
Sentinel policy validates tags
    ├─ Required tags present? ✓
    ├─ Values in allowed list? ✓
    ├─ Optional tags valid? ✓
    ↓
If any check fails:
    ├─ Policy violation blocks apply
    ├─ Error message specifies required tags
    └─ Developer corrects and resubmits
    ↓
If all checks pass:
    └─ Plan proceeds to approval/apply
```

**Implementation Steps:**
1. Define tagging standard in organizational documentation
2. Create Sentinel policy (above)
3. Deploy to org-level policy set: `ps-tagging-governance`
4. Attach to all workspaces
5. Run in soft mandatory for 1 week to gather violations
6. Transition to hard mandatory Week 8
7. Document exception process

**Deliverables:**
- Tagging standard documentation
- Sentinel policy code and deployment
- Policy Set: `ps-tagging-governance` (hard mandatory)
- Tagging audit report (Week 7)
- Tag remediation plan for existing resources

**Success Criteria:**
- All new resources tagged per standard
- Existing resource tagging audit completed
- Exception process documented and functional
- Policy enforced with <5% override rate

#### 3.2 Cost Control Policies and Budget Management
**Timeline:** Week 8-9  
**Effort:** 12 hours  
**Owner:** FinOps & Security Team

Implement cost control policies and budget forecasting:

**Cost Control Sentinel Policies:**

**Policy: Cost Estimation Threshold**
```hcl
import "tfplan"

policy "cost_estimation_review_threshold" {
  enforcement_level = "soft_mandatory"
}

# Plans with >$500 monthly cost increase require special approval
cost_threshold = 500

main = rule {
  # Note: Cost data typically comes from TFC cost estimation
  # This is a placeholder - actual implementation uses TFC APIs
  true
}
```

**Policy: Expensive Resource Prevention**
```hcl
import "tfplan"

policy "prevent_expensive_resources" {
  enforcement_level = "hard_mandatory"
}

# Estimated annual costs to block (without exception)
expensive_resource_types = {
  "aws_elasticsearch_domain": {
    "instance_type": ["r5.4xlarge", "r5.9xlarge", "r5.18xlarge", "r6i.16xlarge"],
    "reason": "High-cost search clusters require FinOps review"
  },
  "aws_rds_cluster": {
    "instance_class": ["db.r5.4xlarge", "db.r5.8xlarge"],
    "reason": "Large RDS clusters require cost approval"
  },
  "aws_dynamodb_table": {
    "billing_mode": "PROVISIONED",
    "reason": "Provisioned DynamoDB requires capacity planning review"
  }
}

main = rule {
  all tfplan.resources.aws_elasticsearch_domain as name, domain {
    domain.instance_type not in expensive_resource_types.aws_elasticsearch_domain.instance_type
  } and
  all tfplan.resources.aws_rds_cluster as name, cluster {
    cluster.instance_class not in expensive_resource_types.aws_rds_cluster.instance_class
  } and
  all tfplan.resources.aws_dynamodb_table as name, table {
    table.billing_mode != "PROVISIONED"
  }
}
```

**Budget Management Setup:**
```
Organization-Level Budgets:
├── Total Annual Budget: $2.4M (est. from current spend)
├── Quarterly Targets:
│   ├── Q1: $550K
│   ├── Q2: $580K
│   ├── Q3: $610K
│   └── Q4: $660K (includes seasonal)
│
Workspace-Level Budgets:
├── ws-prod-core-*: $80K/quarter budget
├── ws-prod-app-a-*: $120K/quarter budget
├── ws-prod-app-b-*: $100K/quarter budget
├── ws-staging-*: $40K/quarter budget
└── ws-dev-*: $15K/quarter budget
```

**Cost Estimation Automation:**
```
Every plan operation:
1. TFC runs cost estimation
2. If delta > $500: Flag for review
3. If delta > $1000: Require approval from FinOps
4. Estimate appears in Slack notification
5. Cost tracking dashboard updated automatically
```

**Cost Reporting Dashboard:**
- Monthly cost by team/project
- Trend analysis (MoM, YoY)
- Budget variance alerts
- Top 10 expensive resources
- Cost anomaly detection

**Deliverables:**
- Cost control policy definitions
- Budget structure and targets
- Cost estimation automation configuration
- Slack integration for cost alerts
- Monthly cost report template

**Success Criteria:**
- Cost policies enforced (hard mandatory)
- Monthly cost reports generated automatically
- Budget variance <5% in first month
- Cost anomaly detection operational

#### 3.3 Module Ingestion and Registry Management
**Timeline:** Week 9-10  
**Effort:** 8 hours  
**Owner:** Platform Engineering Team

Standardize module consumption and establish private module registry:

**Private Module Registry Setup:**

**Module Standard:**
```
Naming Convention: org-resource-provider
Examples:
- org-vpc-aws
- org-rds-cluster-aws
- org-iam-role-aws
- org-s3-bucket-aws
- org-eks-cluster-aws

Version Pattern: semantic versioning (v1.0.0, v1.2.3)
```

**Core Modules to Develop/Promote:**
```
1. org-vpc-aws (v1.0.0)
   ├── Input Variables: cidr_block, availability_zones, tags
   ├── Outputs: vpc_id, subnet_ids, route_table_ids
   ├── Resources: VPC, Subnets, IGW, NAT, Routes
   └── Status: In development, 80% complete

2. org-rds-cluster-aws (v1.0.0)
   ├── Input Variables: engine, engine_version, instance_class, environment
   ├── Outputs: endpoint, reader_endpoint, port
   ├── Resources: RDS Cluster, Parameters, Subnet Group, Security Group
   └── Status: In development, 60% complete

3. org-iam-role-aws (v1.0.0)
   ├── Input Variables: role_name, assume_role_policy, tags
   ├── Outputs: role_arn, role_name
   ├── Resources: IAM Role, Instance Profile, Inline Policies
   └── Status: Complete, ready for promotion

4. org-security-group-aws (v1.0.0)
   ├── Input Variables: name, vpc_id, ingress_rules, egress_rules
   ├── Outputs: security_group_id
   ├── Resources: Security Group, Ingress/Egress Rules
   └── Status: Complete, ready for promotion

5. org-rds-instance-aws (v1.0.0)
   ├── Input Variables: instance_class, engine, allocated_storage, environment
   ├── Outputs: endpoint, port
   ├── Resources: RDS Instance, Parameter Group, Subnet Group
   └── Status: In development, 70% complete
```

**Module Promotion Process:**
```
Development → Staging → Production Registry

1. Development Phase:
   - Module stored in private Git repo (not TFC registry)
   - Used in feature branches for testing
   - Version: v0.x.x (pre-release)

2. Staging Phase:
   - Module published to TFC private registry (staging)
   - Used in staging workspaces
   - Version: v0.x.x or v1.0.0-rc
   - Collected feedback: 2+ teams test module

3. Production Phase:
   - Published to TFC private registry (production)
   - Version: v1.0.0+ (stable release)
   - Mandatory for all new workspaces using that resource type
   - Legacy resources can use alternatives for 2 release cycles

4. Deprecation Phase:
   - Old major versions marked deprecated
   - Migration path documented
   - Support period: 12 months
   - Removal: After 12 months, no new workspaces can use
```

**Module Registry Access Control:**

```
Private Registry: terraform-modules-prod

Access Policy:
├── Team: platform-engineers → publish, pull, manage
├── Team: app-team-a → pull only (read-only)
├── Team: app-team-b → pull only (read-only)
└── Service accounts → pull only (CI/CD pipelines)

Module Discovery:
- Module listing available to all authenticated users
- README and documentation auto-generated from module metadata
- Version history and changelog visible
- Code repository link provided

Example module reference in workspace:
module "app_vpc" {
  source = "app.terraform.io/org-terraform-prod/vpc/aws"
  version = "~> 1.0"
  
  cidr_block = var.vpc_cidr
  availability_zones = var.azs
  tags = local.common_tags
}
```

**Governance Sentinel Policy for Module Usage:**
```hcl
import "tfplan"

policy "enforce_approved_module_sources" {
  enforcement_level = "hard_mandatory"
}

# Approved module sources
approved_sources = {
  "app.terraform.io/org-terraform-prod": true,  # Internal registry
  "registry.terraform.io/hashicorp": true,       # HashiCorp verified
  "registry.terraform.io/aws-ia": true           # AWS Infrastructure as Code
}

unapproved_sources = [
  "github.com/random-user",  # Unapproved GitHub
  "example.com"              # External registries
]

main = rule {
  all tfplan.module_changes as address, module {
    check_module_source(module.change.after.source else "")
  }
}

check_module_source = func(source) {
  # Allow internal registry and approved public sources
  source contains "app.terraform.io/org-terraform-prod" or
  source contains "registry.terraform.io/hashicorp" or
  source contains "registry.terraform.io/aws-ia"
}
```

**Deliverables:**
- Private module registry established in TFC
- 5 core modules in registry (2 complete, 3 in progress)
- Module promotion process documented
- Access control policies configured
- Module governance Sentinel policy
- Module version management strategy

**Success Criteria:**
- All workspaces reference modules from approved registry
- New modules published per promotion process
- Module usage tracking dashboard operational
- <5% unapproved module sources in plans

### Phase 3 Maturity Impact
- **Policy-as-Code:** Tagging governance, cost controls, and module source policies establish Standardize-level governance
- **Organization & Teams:** Module ownership structure strengthens accountability
- **Operations & Health:** No change this phase — focus on policy scaling

### Phase 3 Effort Summary
- **Total Effort:** 30 hours
- **Team Capacity:** 2 FTE weeks
- **Risk Level:** Medium (policy changes may block existing plans initially)
- **Dependencies:** Phase 2 completion, module development readiness
- **Rollback Complexity:** Medium (policies reversible, module references require migration)

---

## PHASE 4: Scaling & Automation (Month 4-6, Weeks 14-26)

### Objective
Scale governance across additional projects and teams, implement self-service workflows, and establish operational excellence practices including lifecycle management and disaster recovery.

### Key Initiatives

#### 4.1 Multi-Project Expansion and Team Scaling
**Timeline:** Week 14-16  
**Effort:** 15 hours  
**Owner:** Platform Engineering & Organization Leaders

Extend governance structure to support additional projects and business units:

**New Project Provisioning:**

```
Current State:
├── org-terraform-prod (1 organization)
│   ├── 12-15 workspaces
│   ├── 4 teams
│   └── 1 project (default)

Target State:
├── org-terraform-prod (1 organization, expanded)
│   ├── 30-40 workspaces
│   ├── 8-10 teams
│   ├── 3-4 projects
│   │   ├── Project: platform-infrastructure
│   │   │   ├── Workspaces: 8-10 (VPC, RDS, IAM, Security Groups, etc.)
│   │   │   ├── Teams: platform-admins, platform-engineers
│   │   │   └── Access: Restricted to platform team
│   │   │
│   │   ├── Project: application-services
│   │   │   ├── Workspaces: 12-15 (App A, B, C)
│   │   │   ├── Teams: app-team-a, app-team-b, app-team-c
│   │   │   └── Access: Team-specific workspace access
│   │   │
│   │   └── Project: infrastructure-shared
│   │       ├── Workspaces: 8-10 (Shared resources)
│   │       ├── Teams: platform-engineers (read), app-teams (read/write)
│   │       └── Access: Tiered (read vs. write permissions)
│   │
│   ├── Policy Sets: 10-12 (core + team-specific)
│   └── Variable Sets: 15-20 (global + team-specific)
```

**New Team Onboarding Process:**

```
Week 1: Planning
├─ Identify team lead and members (3-5 people)
├─ Define resource ownership and boundaries
├─ Review compliance and security requirements
└─ Schedule kickoff meeting

Week 2: Setup
├─ Create TFC team in organization
├─ Add users via SSO group mapping
├─ Create team-specific variable sets
├─ Provision initial workspaces (2-3)
└─ Document team access policy

Week 3: Training & Testing
├─ Team training on TFC workflows
├─ Conduct test plan and apply on staging workspace
├─ Review policy enforcement and cost estimates
├─ Validate notification and approval workflows
└─ Q&A and troubleshooting

Week 4: Go-Live
├─ Enable team on production workspaces
├─ Monitor first runs for issues
├─ Provide 24/7 support for questions
└─ Document lessons learned

Ongoing Support
├─ Monthly check-ins with team lead
├─ Quarterly policy compliance reviews
├─ Annual capacity and cost reviews
└─ Continuous improvement suggestions
```

**Workspace Template for New Teams:**
```hcl
# /templates/app-team-workspace/main.tf

terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  cloud {
    organization = "org-terraform-prod"
    workspaces {
      name = "ws-app-team-${var.environment}"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  assume_role {
    role_arn = "arn:aws:iam::${var.aws_account_id}:role/TerraformRole"
  }

  default_tags {
    tags = local.common_tags
  }
}

locals {
  common_tags = {
    environment  = var.environment
    owner        = var.team_name
    project      = var.project_name
    cost-center  = var.cost_center
    terraform    = "true"
    created-by   = "terraform"
  }
}

# Core module references
module "vpc" {
  source = "app.terraform.io/org-terraform-prod/vpc/aws"
  version = "~> 1.0"
  
  cidr_block = var.vpc_cidr
  availability_zones = var.availability_zones
  tags = local.common_tags
}

module "security_groups" {
  source = "app.terraform.io/org-terraform-prod/security-group/aws"
  version = "~> 1.0"
  
  vpc_id = module.vpc.vpc_id
  tags = local.common_tags
}

# Outputs
output "vpc_id" {
  value = module.vpc.vpc_id
}

output "vpc_cidr" {
  value = module.vpc.cidr_block
}
```

**New Projects:**

| Project | Purpose | Teams | Workspace Count | Status |
|---------|---------|-------|-----------------|--------|
| platform-infrastructure | Core VPC, RDS, security | platform-admins, platform-engineers | 10 | Existing, expanding |
| application-services | App deployments | app-team-a, app-team-b, app-team-c | 15 | New (Week 14) |
| infrastructure-shared | Shared services | platform-engineers, all app-teams | 8 | New (Week 15) |
| monitoring-observability | Monitoring infrastructure | platform-engineers, ops-team | 5 | New (Week 16) |

**Deliverables:**
- 3-4 new projects created in TFC
- 8-10 new teams set up with RBAC
- Workspace templates for common patterns
- Team onboarding runbook
- Updated organization structure documentation
- 20-25 new workspaces provisioned

**Success Criteria:**
- All teams can self-serve on assigned workspaces
- Teams cannot access unauthorized workspaces (RBAC enforced)
- New teams onboarded within 4-week timeline
- <2% workspace access requests due to misconfiguration

#### 4.2 Hard-Mandatory Policy Enforcement and Compliance
**Timeline:** Week 16-18  
**Effort:** 10 hours  
**Owner:** Security & Compliance Team

Expand hard-mandatory policies and establish compliance scanning:

**Comprehensive Policy Set:**

```
Core Policies (Mandatory across all organizations):
├── Security Policies (hard-mandatory)
│   ├── Encryption at rest (all applicable resources)
│   ├── Encryption in transit (TLS, VPN)
│   ├── VPC endpoint enforcement (no direct internet access)
│   ├── Security group whitelist restrictions
│   └── IAM policy least privilege verification
│
├── Cost Policies (hard-mandatory)
│   ├── Instance type restrictions (prevent over-provisioning)
│   ├── Storage policies (prevent excessive capacity allocation)
│   ├── Database policies (force encryption, backups, multi-AZ)
│   └── Cost anomaly detection (> $5K/month resources)
│
├── Tagging Policies (hard-mandatory)
│   ├── Required tags (environment, owner, cost-center, project)
│   ├── Value validation (enum constraints)
│   └── Tag format enforcement
│
├── Operational Policies (soft-mandatory → hard)
│   ├── Resource naming conventions
│   ├── Module source approval (private registry only)
│   ├── Deprecated resource versions (prevent old patterns)
│   └── Dangerous operations (state deletion, variable modification)
│
└── Compliance Policies (hard-mandatory)
    ├── CIS AWS Foundations (applicable sections)
    ├── PCI DSS requirements (if applicable)
    ├── HIPAA controls (if applicable)
    └── GDPR data residency (if applicable)
```

**Policy Details & Coverage:**

| Policy | Current Level | Target Level | Violation Rate (Target) | Teams Affected |
|--------|---------------|--------------|------------------------|----------------|
| Encryption at rest | Soft | Hard | <2% | All (14-16) |
| Cost controls | Soft | Hard | <3% | All (14-16) |
| Tagging enforcement | Hard | Hard | <5% | All (14-16) |
| Module source approval | Hard | Hard | <1% | All (14-16) |
| Naming conventions | Hard | Hard | <2% | All (14-16) |
| CIS compliance | Soft | Hard | <4% | All (14-16) |

**Compliance Scanning Automation:**

```
Automated Compliance Dashboard:
├── Policy Compliance by Team
│   ├── app-team-a: 96% (12 of 13 policies passing)
│   ├── app-team-b: 94% (12 of 13 policies passing)
│   ├── platform-engineers: 99% (13 of 13 policies passing)
│   └── ops-team: 92% (12 of 13 policies passing)
│
├── Failing Resources:
│   ├── Total non-compliant resources: 8
│   ├── By policy:
│   │   ├── Encryption at rest: 3 resources
│   │   ├── Tagging: 2 resources
│   │   ├── Cost control: 2 resources
│   │   └── Naming convention: 1 resource
│   │
│   └── By team:
│       ├── app-team-b: 4 resources
│       ├── staging environment: 3 resources
│       └── dev environment: 1 resource
│
├── Trending & Alerts:
│   ├── Compliance improving: +2% week-over-week
│   ├── High-risk team alert: app-team-b (92% this week, was 96% last week)
│   ├── New policy violations: 0 this week
│   └── Waived violations: 1 (expires in 14 days)
│
└── Remediation Tracking:
    ├── Assigned issues: 8
    ├── In progress: 3
    ├── Resolved: 4
    └── Overdue: 1 (app-team-b tagging)
```

**Exception Management System:**

```
Waiver Request Process:
1. Developer submits waiver request with justification
2. Team lead approves request
3. Security team reviews (24-hour turnaround)
4. Decision: Approve (with expiration date) or Deny (with feedback)
5. If approved: Waiver recorded in audit system
6. If expired: Policy enforcement resumes, resource must remediate

Waiver Types:
├── Policy Override: Exception to specific policy for specific resource
│   ├── Duration: 30 days (renewable)
│   ├── Requires: Team lead + Security approval
│   └── Example: "Allow unencrypted dev database (expires 2024-06-15)"
│
├── Team Exception: Exception to policy for team-wide use
│   ├── Duration: 90 days (renewable)
│   ├── Requires: Director approval + Security approval
│   └── Example: "Allow legacy app to use old RDS engine for 90 days"
│
└── Organizational Exception: Rare exceptions for entire organization
    ├── Duration: 180 days (renewable)
    ├── Requires: CTO approval + Security + Compliance approval
    └── Example: "Allow temporary cross-account access for migration (ends 2024-09-30)"

Waiver Audit Trail:
- Requestor, approver, reason, duration logged
- Automatic expiration reminders (30, 14, 7 days before)
- Compliance reports highlight waivers
- Annual review of active waivers
```

**Deliverables:**
- 12-15 hard-mandatory policies deployed
- Automated compliance dashboard (Grafana/Tableau)
- Compliance measurement algorithm documented
- Waiver request system operational
- Weekly compliance reports to leadership
- Remediation tracking spreadsheet

**Success Criteria:**
- Overall compliance rate ≥ 95%
- No policy violations without documented waiver
- All teams notified of non-compliance within 24 hours
- Remediation timeline: Critical (24h), High (1 week), Medium (2 weeks)

#### 4.3 Workspace Lifecycle Management and State Governance
**Timeline:** Week 18-20  
**Effort:** 12 hours  
**Owner:** Platform Engineering & SRE Team

Implement comprehensive workspace lifecycle and state management practices:

**Workspace Lifecycle:**

```
Development Workspace Lifecycle (Feature → Deprecation)

1. CREATION PHASE (Day 1)
   ├─ Workspace requested via portal form
   ├─ Criteria verified: team, project, environment, cost center
   ├─ VCS repository created/identified
   ├─ Workspace provisioned in TFC
   ├─ Initial variables and outputs configured
   ├─ Team members granted access via RBAC
   └─ Status: ACTIVE

2. ACTIVE PHASE (Day 2 - Month 6)
   ├─ Regular plan/apply operations
   ├─ Cost monitoring (budget vs. actual)
   ├─ Compliance monitoring (policy violations)
   ├─ State tracking and backups
   ├─ Version control integration active
   └─ Status: ACTIVE

3. MAINTENANCE PHASE (Month 6+)
   ├─ Quarterly cost reviews
   ├─ Annual security audits
   ├─ Terraform version updates (quarterly)
   ├─ Module version updates (as needed)
   ├─ Documentation maintenance
   └─ Status: ACTIVE or ARCHIVED

4. STAGING FOR DEPRECATION (Month 12+)
   ├─ Owner receives 90-day deprecation notice
   ├─ Reason documented (e.g., "migrating to new infra")
   ├─ Remediation plan requested
   ├─ State migration plan created (if applicable)
   ├─ Cost tracking shows trend
   └─ Status: DEPRECATION_PENDING

5. DEPRECATION PHASE (Month 12+3 months)
   ├─ Workspace locked: no new plans allowed
   ├─ Read-only access for reference
   ├─ State export available for 90 days
   ├─ Owner must migrate or confirm destruction
   ├─ Cost accumulation halted (no new resources)
   └─ Status: DEPRECATED

6. ARCHIVE PHASE (Month 15+)
   ├─ State destroyed (or exported if needed)
   ├─ Workspace remains in TFC for 12 months (audit trail)
   ├─ No access except platform-admins
   ├─ Archived in read-only state
   └─ Status: ARCHIVED

7. DELETION PHASE (Month 27)
   ├─ Workspace deleted from TFC
   ├─ No recovery possible (state gone)
   ├─ Recorded in change management system
   └─ Status: DELETED
```

**Workspace Lifecycle Automation:**

```
Automated Lifecycle Events:

Month 6 Milestone:
  ├─ Automated email: "Workspace ws-app-team-a-staging has been active for 6 months"
  ├─ Include: Current cost, last modified date, team contact
  ├─ Request: Confirm continued need or plan migration
  └─ Action: If no response in 14 days, escalate to team lead

Month 12 Milestone:
  ├─ Automated assessment: "Is this workspace still needed?"
  ├─ Workspace access report generated
  ├─ Cost trend analysis shown
  ├─ Module version status checked
  └─ Decision required: Keep, Migrate, or Deprecate

Month 12 + 3 months:
  ├─ Automated lock applied to workspace
  ├─ No new plans can be created
  ├─ Notification: "Workspace entering deprecation - 90 days until deletion"
  ├─ State export generated and stored in S3
  └─ Team given options: Migrate or Destroy

Month 15:
  ├─ Automated state destruction (if no objection)
  ├─ Workspace marked as ARCHIVED
  ├─ Email: "Workspace ws-app-team-a-staging archived - accessible for audit for 12 months"
  └─ Access: Platform-admins only

Month 27:
  ├─ Automated deletion from TFC
  ├─ Final audit log generated
  └─ Change record created in CMDB
```

**State Management & Disaster Recovery:**

```
State Backup Strategy:

Backup Scope:
├─ Frequency: After every apply operation (automatic)
├─ Retention: 90 days (rolling)
├─ Storage: S3 bucket (encrypted, versioning enabled)
├─ Replication: Cross-region replication enabled
└─ Retention Policy: 7 years for compliance workspaces

Backup Process:
  Step 1: Apply operation completes in TFC
    ↓
  Step 2: TFC triggers webhook on completion
    ↓
  Step 3: Lambda function invoked
    ↓
  Step 4: State file exported via TFC API
    ↓
  Step 5: Encrypted and stored in S3 with metadata
    ↓
  Step 6: Verification: State file integrity check
    ↓
  Step 7: Notification: Backup completion logged
    ↓
  Step 8: Lifecycle: Rotation after 90 days

Backup Retrieval & Recovery:

Scenario: Developer deletes resource by accident
  1. Identify backup to restore (TFC state file)
  2. Verify backup integrity and date
  3. Export state file from S3 backup
  4. Create temporary recovery workspace
  5. Import backup state
  6. Verify resource presence
  7. Apply to production workspace
  8. Document incident in change log

Scenario: Workspace destroyed (corrupted state)
  1. Identify latest valid backup
  2. Create new workspace with same configuration
  3. Import state from backup
  4. Run terraform plan to verify
  5. Resume normal operations
  6. Document recovery in incident report
```

**Stale Resource Detection:**

```
Automated Resource Analysis:

Monthly Resource Audit:
├─ Identify resources without recent modifications
├─ Flag: No changes in >6 months
├─ Categorize:
│   ├─ Actively managed (accessed via console, verified)
│   ├─ Orphaned (no owner, unused)
│   └─ Legacy (planned for deprecation)
│
└─ Actions:
    ├─ Active: Document in runbook
    ├─ Orphaned: Notify team, offer cleanup
    └─ Legacy: Plan deprecation

Resource Alerts:
├─ Unused resources identified
├─ Team notified monthly
├─ Cleanup offered (automated removal possible)
└─ Cost savings tracked and reported

Example Report:
Workspace: ws-app-team-a-prod
├─ Resource: aws_instance "legacy_app_server"
│   ├─ Status: No changes in 8 months
│   ├─ Estimated cost: $240/month
│   ├─ Owner: app-team-a (verified)
│   └─ Recommendation: Consider alternative (Fargate/Lambda)
│
└─ Resource: aws_rds_instance "test_db"
    ├─ Status: No changes in 10 months
    ├─ Estimated cost: $180/month
    ├─ Owner: Unknown (no recent runs)
    └─ Recommendation: Cleanup (scheduled for next sprint)
```

**Deliverables:**
- Workspace lifecycle policy documentation
- Automated lifecycle notifications system (Lambda + SNS)
- State backup infrastructure (S3, cross-region replication)
- Disaster recovery runbook
- Resource cleanup automation
- Lifecycle management dashboard

**Success Criteria:**
- 100% of workspaces assigned to teams/owners
- Stale workspaces identified and remediated within 1 month
- State backups automated and verified daily
- Recovery RTO <2 hours for non-critical workspaces
- <5% orphaned resources in total infrastructure

#### 4.4 Self-Service Infrastructure and Developer Enablement
**Timeline:** Week 20-26  
**Effort:** 18 hours  
**Owner:** Platform Engineering & Developer Relations

Implement self-service workspace provisioning and team empowerment:

**Self-Service Portal (Requirements):**

```
Features:
├─ Workspace Creation Wizard
│   ├─ Step 1: Basic information (name, team, project, environment)
│   ├─ Step 2: Resource configuration (VPC, RDS, storage needs)
│   ├─ Step 3: Access control (team members, permissions)
│   ├─ Step 4: Variables and secrets (from variable sets)
│   ├─ Step 5: Review and create
│   └─ Result: Workspace created with terraform apply ready
│
├─ Dashboard
│   ├─ My Workspaces (filtered by team membership)
│   ├─ Recent Runs (plan/apply history)
│   ├─ Cost Overview (monthly, trends)
│   ├─ Policy Compliance (violations by workspace)
│   └─ Cost Alerts (exceeding budget)
│
├─ Run Management
│   ├─ Trigger Plan (manual)
│   ├─ View Plan Results (cost, changes)
│   ├─ Request Apply (with approval workflow)
│   ├─ View Apply Log
│   └─ Rollback to Previous State
│
├─ Cost Management
│   ├─ Budget Configuration (per workspace)
│   ├─ Cost Trends (graph of monthly spend)
│   ├─ Cost Breakdown (by resource type)
│   ├─ Alert Configuration (notify when approaching budget)
│   └─ Cost Optimization Recommendations
│
├─ Documentation
│   ├─ Getting Started (quick start guide)
│   ├─ Best Practices (workflow, naming, tagging)
│   ├─ Troubleshooting (common issues)
│   ├─ API Documentation (for automation)
│   └─ FAQ (frequently asked questions)
│
└─ Admin Features
    ├─ User Management (add/remove team members)
    ├─ Workspace Management (edit, archive, delete)
    ├─ Policy Configuration (view/manage policies)
    └─ Audit Log (view all actions)
```

**Workspace Provisioning Workflow:**

```
User: Developer in app-team-a

1. Click: "Create New Workspace" in self-service portal

2. Fill Form:
   ├─ Workspace Name: app-team-a-feature-payments
   ├─ Team: app-team-a
   ├─ Project: application-services
   ├─ Environment: staging
   └─ Initial Resources: VPC, RDS, Security Groups

3. System Auto-Completes:
   ├─ Cost Center: auto-filled from team settings
   ├─ Owner: auto-set to requestor
   ├─ Tags: auto-populated from team template
   └─ RBAC: auto-configured for app-team-a access

4. Review & Confirm:
   ├─ Template: Show Terraform code generated
   ├─ Cost: Display estimated monthly cost ($850)
   ├─ Timeline: Indicate workspace ready in 5 minutes
   └─ Button: "Create Workspace"

5. Backend Processing:
   ├─ Validate inputs against org policies
   ├─ Generate Terraform code from template
   ├─ Create VCS repository branch (if needed)
   ├─ Create TFC workspace via API
   ├─ Attach variable sets
   ├─ Configure RBAC
   └─ Send confirmation email

6. Result:
   ├─ Workspace ready: app-team-a-feature-payments
   ├─ VCS repo: Ready for initial commit
   ├─ Dashboard: Shows new workspace with status READY_FOR_PLAN
   └─ Next Action: "Run Plan"

Timeline: 5 minutes (fully automated)
Cost Transparency: $850/month estimated before creation
Approval: Zero approval required (within org guardrails)
```

**Approval Workflow for High-Cost Workspaces:**

```
Estimated Cost Threshold: >$2000/month

Trigger: Workspace creation triggers cost estimate >$2000/month
  ↓
Action: Request escalates to FinOps team
  ↓
Approval: FinOps reviews request within 24 hours
  ├─ Approve: Workspace creation proceeds
  ├─ Deny: Request rejected with feedback
  └─ Modify: Request modification of resource config
  ↓
Result: Developer notified of decision
  ├─ If approved: Workspace activated
  ├─ If denied: Can resubmit with lower cost config
  └─ Timeline: 24-48 hours total
```

**Team Enablement Program:**

```
Monthly Training Cohorts:
├─ Cohort 1 (Week 1): "TFC Fundamentals" (1 hour)
│   ├─ Topics: Workspace types, VCS integration, variables
│   ├─ Hands-on: Create and run first workspace
│   ├─ Attendees: 5-10 new team members
│   └─ Recording: Available for self-paced learning
│
├─ Cohort 2 (Week 2): "Advanced Workflows" (2 hours)
│   ├─ Topics: Team collaboration, cost management, troubleshooting
│   ├─ Hands-on: Multi-team workflow simulation
│   ├─ Attendees: Experienced users deepening knowledge
│   └─ Q&A: Interactive troubleshooting session
│
├─ Cohort 3 (Week 3): "Governance & Compliance" (1.5 hours)
│   ├─ Topics: Policies, tagging standards, cost optimization
│   ├─ Hands-on: Policy override request process
│   ├─ Attendees: Team leads and compliance-focused users
│   └─ Discussion: Policy feedback and improvement ideas
│
└─ Certification Program:
    ├─ Level 1: TFC Operator (create/manage workspaces)
    ├─ Level 2: TFC Developer (write Terraform code, module development)
    ├─ Level 3: TFC Architect (design multi-team infrastructure)
    └─ Incentive: Certificate for resume, badge for Slack profile
```

**Success Metrics & KPIs:**

```
Developer Experience:
├─ Time to create workspace: <10 minutes (target: was 2-4 hours manual)
├─ Self-service adoption rate: >80% (vs. requesting platform team)
├─ Developer satisfaction: >4/5 NPS rating
└─ Support ticket reduction: 40% fewer "how do I create a workspace" tickets

Operational Efficiency:
├─ Workspace provisioning: 99% automated (zero manual intervention)
├─ Cost transparency: 100% of workspaces with budget alerts
├─ Policy compliance: >95% of new workspaces compliant at creation
└─ Rollback capability: 100% of state changes recoverable within 2 hours

Business Impact:
├─ Time to production (new feature): 30% faster (was 5 days, now 3.5 days)
├─ Infrastructure cost reduction: 15% via optimization recommendations
├─ Team onboarding time: 50% faster (was 2 weeks, now 1 week)
└─ Infrastructure as Code adoption: >95% of teams using TFC (was 70%)
```

**Deliverables:**
- Self-service portal (web application or dashboard)
- Workspace creation automation (Lambda/Terraform Cloud)
- Documentation and training materials
- Certification program curriculum
- Developer enablement content (video, guides, FAQ)
- Success metrics dashboard

**Success Criteria:**
- >80% of workspaces created via self-service portal
- <10 minute workspace creation time
- >95% of teams rated training materials as helpful
- <2 hours RTO for workspace recovery from backup

### Phase 4 Maturity Impact
- **GitOps & VCS:** Maintains Standardize-level practices
- **Module Library:** Maintains Scale-level practices
- **Policy-as-Code:** Comprehensive governance maintained
- **Organization & Teams:** Expanded teams and project structure solidify Standardize practices
- **Operations & Health:** Lifecycle management, disaster recovery, and self-service advance toward Standardize

### Phase 4 Effort Summary
- **Total Effort:** 55 hours
- **Team Capacity:** 3-4 FTE weeks (or distributed across 6 weeks)
- **Risk Level:** Medium (self-service portal requires careful testing)
- **Dependencies:** Phase 3 completion, module library maturity
- **Rollback Complexity:** Low (portal is additive, can be disabled if issues)

---

## Implementation Timeline Summary

### Month-by-Month Breakdown

```
MONTH 1: Quick Wins & Foundation
├─ Week 1-2: Phase 1 (Quick Wins)
│   ├─ Deploy Sentinel policies
│   ├─ Attach variable sets
│   └─ Remediate stale workspaces
│   └─ Stage: Adopt (strengthened)
│
├─ Week 3-4: Phase 2 (Foundation) - Part 1
│   ├─ Implement team RBAC
│   └─ Begin GitOps workflow setup
│   └─ Progress: Building toward Standardize
│
└─ Deliverables: 3 policies, 2 varsets, 9 stale workspaces resolved

MONTH 2: Governance & Advanced Workflows
├─ Week 5-6: Phase 2 (Foundation) - Part 2
│   ├─ Complete GitOps workflows
│   ├─ Promote policies to hard mandatory
│   └─ Stage: Adopt → Standardize (emerging)
│
├─ Week 7-8: Phase 3 (Governance) - Part 1
│   ├─ Deploy tagging policy
│   ├─ Establish cost controls
│   └─ Begin module registry setup
│   └─ Progress: Entering Standardize territory
│
└─ Deliverables: VCS workflows, branch protection, 4 teams, 6 policies total

MONTH 3: Compliance & Policy Scaling
├─ Week 9-10: Phase 3 (Governance) - Part 2
│   ├─ Complete module ingestion standards
│   ├─ Establish module promotion workflow
│   └─ Stage: Standardize (emerging)
│
├─ Week 11-13: Phase 3 (Governance) - Part 3
│   ├─ Validate all governance structures
│   ├─ Begin Phase 4 planning
│   └─ Progress: Standardize (stabilization)
│
└─ Deliverables: 5 private modules, tagging policy, cost controls, module registry

MONTH 4-5: Scaling & Expansion
├─ Week 14-18: Phase 4 (Scaling) - Part 1
│   ├─ Multi-project expansion
│   ├─ 3-4 new teams onboarded
│   ├─ Hard-mandatory policy enforcement
│   └─ Progress: Standardize (strengthening)
│
├─ Week 19-20: Phase 4 (Scaling) - Part 2
│   ├─ Workspace lifecycle management
│   ├─ State governance & disaster recovery
│   └─ Progress: Standardize (maturing)
│
└─ Deliverables: 30-40 total workspaces, 8-10 teams, disaster recovery, state backups

MONTH 6: Self-Service & Optimization
├─ Week 21-26: Phase 4 (Scaling) - Part 3
│   ├─ Self-service portal development
│   ├─ Developer enablement program
│   ├─ Stage: Standardize (achieved)
│   └─ Final Assessment: Standardize target achieved
│
└─ Deliverables: Self-service portal, certification program, KPI dashboard

Final State:
├─ Stage: Standardize (target achieved)
├─ Workspaces: 30-40 (from 12-15)
├─ Teams: 8-10 (from 4)
├─ Policies: 12-15 hard-mandatory (from 0)
├─ Modules: 5+ in registry (from 0)
└─ Adoption: >95% of teams using standardized workflows
```

---

## Risk Analysis & Mitigation Strategies

### High-Risk Items

#### Risk 1: Policy Enforcement Blocks Critical Workspaces
**Probability:** Medium | **Impact:** High | **Severity:** High

**Description:**
Stringent policies (especially hard-mandatory cost controls and naming conventions) may block legitimate infrastructure changes if policies are too restrictive.

**Mitigation:**
1. **Soft Mandatory Phase:** All new policies deploy as soft-mandatory for 1-2 weeks
2. **Override Tracking:** Monitor override rates; if >15% overrides, revisit policy thresholds
3. **Feedback Loop:** Weekly policy violation reports to understand legitimate vs. false-positive violations
4. **Grace Period:** 30-day grace period for existing non-compliant resources before enforcement
5. **Team Communication:** Clear messaging that policies support, not hinder, development

**Contingency:**
- Rollback to soft-mandatory immediately if override rate >20%
- Revise thresholds based on actual data
- Conduct team feedback sessions to refine policies

---

#### Risk 2: Team Adoption Resistance
**Probability:** Medium | **Impact:** Medium | **Severity:** Medium

**Description:**
Teams may resist new workflows, RBAC restrictions, and self-service requirements if they perceive friction or loss of autonomy.

**Mitigation:**
1. **Early Engagement:** Involve team leads in design of RBAC and workflows
2. **Training & Support:** Comprehensive training before rollout (3-4 hours per team)
3. **Quick Wins:** Phase 1 demonstrates immediate value (30% faster approvals)
4. **Feedback Channels:** Monthly feedback sessions with team leads
5. **Incentives:** Recognize teams with high compliance and efficiency

**Contingency:**
- Extend training timeline if adoption <50% by week 4
- Offer alternative workflows for edge cases
- Escalate to organization leadership for buy-in

---

#### Risk 3: Module Development Falls Behind Schedule
**Probability:** High | **Impact:** High | **Severity:** High

**Description:**
Core modules (VPC, RDS, IAM) are complex and may not complete on schedule, delaying Phase 3 governance enforcement.

**Mitigation:**
1. **Parallel Development:** Start module development in Week 1 (Phase 1), not Phase 3
2. **Prioritization:** Develop modules in order of team demand (VPC first, then RDS)
3. **External Help:** Budget for contractor module development if needed
4. **MVP Approach:** Release v1.0 with core features only; enhancements in v1.1+
5. **Reusable Components:** Publish early module versions for team feedback

**Contingency:**
- Phase 3 module governance enforcement can be delayed 2-4 weeks without impact to overall maturity progression
- Alternative: Use public modules (hashicorp/aws-ia) instead of custom modules for Phase 2
- Extend team capacity with external resources

---

#### Risk 4: State Management Failures or Data Loss
**Probability:** Low | **Impact:** Critical | **Severity:** High

**Description:**
State file corruption, accidental destruction, or backup failures could result in infrastructure being out-of-sync with declared state.

**Mitigation:**
1. **Automated Backups:** Every state change automatically backed up (TFC feature)
2. **Cross-Region Replication:** S3 backups replicated to secondary region
3. **Backup Verification:** Weekly restore test (to temporary workspace)
4. **Access Controls:** Restrict state file deletion to platform-admins only
5. **Immutable Backups:** Backup S3 bucket configured for immutability (prevent deletion)

**Contingency:**
- RTO <2 hours for non-critical workspaces (restore from backup)
- RTO <30 minutes for critical workspaces (dual backup systems)
- Incident response runbook tested quarterly
- Insurance coverage for data loss (if applicable)

---

### Medium-Risk Items

#### Risk 5: VCS Integration Complexity
**Probability:** Medium | **Impact:** Medium | **Severity:** Medium**

**Description:**
GitHub Actions, branch protection rules, and TFC VCS webhooks create complex integrations that may have race conditions or synchronization issues.

**Mitigation:**
- Comprehensive testing in staging environment before production
- Gradual rollout to teams (2 teams/week in Phase 2)
- Clear runbooks for troubleshooting integration issues
- Direct GitHub support contract for critical issues
- Webhook retry logic and dead-letter queues for failed events

---

#### Risk 6: Cost Estimation Accuracy
**Probability:** Medium | **Impact:** Medium | **Severity:** Medium

**Description:**
TFC cost estimation may be inaccurate for custom resources or may miss regional pricing variations, leading to budget overages.

**Mitigation:**
- Validate TFC cost estimates against actual AWS billing (monthly reconciliation)
- Adjust cost thresholds based on estimation accuracy
- Manual review for high-cost resources (>$1000/month estimated)
- Provider-specific cost data subscriptions (AWS Pricing API)
- Historical cost analysis to calibrate estimates

---

#### Risk 7: Self-Service Portal Security
**Probability:** Low | **Impact:** High | **Severity:** High

**Description:**
Self-service portal may expose sensitive data (API keys, secrets) or allow unauthorized actions if RBAC is not enforced at API level.

**Mitigation:**
- All API calls authenticated via TFC token (no hardcoded credentials)
- Every action logged and auditable (who did what, when)
- Rate limiting to prevent API abuse
- Secrets stored in Vault or Secrets Manager (not in TFC variables)
- Regular security audits of portal code (SAST/DAST)
- Bug bounty program for vulnerabilities

---

## Resource & Effort Allocation

### Total Project Effort
- **Phase 1:** 17 hours (1 FTE week)
- **Phase 2:** 36 hours (2 FTE weeks)
- **Phase 3:** 30 hours (2 FTE weeks)
- **Phase 4:** 55 hours (3-4 FTE weeks)
- **Total:** 138 hours (8-9 FTE weeks)

### Team Composition (Recommended)
```
Core Team (dedicated for 6 months):
├─ Platform Engineering Lead (1 FTE)
│   └─ Responsible: Overall execution, team coordination, issue resolution
│
├─ Platform Engineers (2 FTE)
│   ├─ Responsible: Workspace provisioning, VCS integration, module development
│   └─ Focus areas: Infrastructure as Code, terraform workflows
│
├─ Security/Governance Lead (0.5 FTE)
│   └─ Responsible: Policy design, compliance verification, risk assessment
│
└─ DevOps/SRE (0.5 FTE)
    └─ Responsible: State management, disaster recovery, monitoring

Supporting Resources (0.25-0.5 FTE each):
├─ FinOps Analyst (cost management, budgeting)
├─ Team Lead Representatives (4-5 people, 10% each for feedback)
├─ Training Specialist (enablement content development)
└─ Security Team Lead (policy approval, compliance sign-off)

External Resources (as needed):
├─ TFC Professional Services (2-4 weeks for architecture review)
├─ Module Development Contractor (if internal capacity insufficient)
└─ Training Provider (if in-house expertise lacking)

Total Core Team Cost: ~$350K-400K (salaries for 6 months)
Total Project Budget: $450K-500K (including external support, tools, training)
```

### Success Metrics & Governance

**Executive Steering Committee:**
- Monthly review of progress against timeline
- Risk escalation and decision-making
- Budget and resource adjustments
- Stakeholder communication

**Project Governance:**
- Weekly status meetings with core team
- Bi-weekly sync with team leads
- Daily standups (15 min) during critical phases
- Change management for policy/RBAC changes

**Success Metrics:**
| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| TFC Maturity Stage | Adopt | Standardize | Month 6 |
| Team RBAC Coverage | 25% | 100% | Month 2 |
| Policy Compliance | 0% | >95% | Month 3 |
| Module Registry Coverage | 0 modules | 5+ modules | Month 3 |
| Self-Service Adoption | 0% | >80% | Month 6 |
| Developer Satisfaction | — | >4/5 NPS | Month 6 |
| Infrastructure Cost Savings | — | >15% | Month 6 |
| Team Onboarding Time | 2 weeks | 1 week | Month 6 |

---

## Conclusion

This 6-month roadmap provides a structured, phased approach to advancing Terraform Cloud maturity from **Adopt** to **Standardize** stage. The plan balances quick wins with foundational improvements, ensuring sustained momentum and team buy-in.

**Key Success Factors:**
1. Executive sponsorship and commitment
2. Dedicated core team with clear responsibilities
3. Phased rollout to allow team adoption and feedback
4. Strong governance and risk management
5. Continuous improvement and metric tracking
6. Clear communication and team enablement

**Expected Outcomes:**
- Mature TFC governance with comprehensive policies and controls
- Scalable, self-service infrastructure provisioning
- 95%+ team adoption of standardized workflows
- 15%+ infrastructure cost savings through optimization
- Significantly faster time-to-production for new features
- Organizational readiness for future cloud expansion

**Next Steps (Week 1):**
1. Secure executive sponsorship
2. Allocate core team and budget
3. Conduct kickoff meeting with all stakeholders
4. Begin Phase 1 execution (deploy policies, attach varsets)
5. Schedule weekly status reviews

---

## Appendix: Sentinel Policy Reference

### Complete Sentinel Policy Examples

All Sentinel policies referenced in this roadmap are provided above in Phases 1-3. Key policies include:

1. **CIS AWS Foundations** - Encryption, tagging, compliance
2. **Cost Controls** - Instance type restrictions, storage limits
3. **Naming Conventions** - Resource naming standardization
4. **Tagging Enforcement** - Required and optional tag validation
5. **Module Source Approval** - Private registry enforcement

For detailed policy syntax and customization, refer to HashiCorp Sentinel documentation and the specific policy sections in Phase 3.

---

**Document Version:** 1.0  
**Last Updated:** 2024-01-15  
**Next Review:** Month 3 (mid-way point)  
**Owner:** Platform Engineering Lead  
**Status:** Ready for Execution
