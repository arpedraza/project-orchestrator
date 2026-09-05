# Project Orchestrator — Phase Reference

## Contents
- Phase 1: Project Kickoff (Project Manager)
- Phase 2: Solution Architecture
- Phase 3: Parallel Assessment Block
- Phase 4: Design
- Phase 5: Development Sprint Planning
- Phase 6: QA and Code Review
- Phase 7: Deployment Planning
- Phase 8: Parallel Post-Deployment Block
- Phase 9: Documentation and Closure

---

## Phase 1 — Project Kickoff (Project Manager)

**Skills to activate:** `iac-project-control`, `artifact-template-project-kickoff`, `artifact-template-project-tracker`

**Inputs:** `.orchestrator/00-intake.md`

**Tasks:**
1. Read intake document
2. Activate `iac-project-control` → define project scope, objectives, deliverables, stakeholders
3. Activate `artifact-template-project-kickoff` → produce a formatted kickoff document
4. Activate `artifact-template-project-tracker` → set up a work-breakdown structure (WBS) with epics and milestones
5. Identify all project phases that apply (skip design if no UI; skip AI block if no ML)
6. Flag any immediate risks or blockers

**Output artifact:** `.orchestrator/01-project-brief.md`
**Template:** `handoff-templates/project-brief.md`

**Checklist before proceeding:**
- [ ] Project name and description confirmed
- [ ] Stakeholders identified
- [ ] Milestones and target dates set
- [ ] Scope boundaries defined (in-scope / out-of-scope)
- [ ] Initial risk register created

---

## Phase 2 — Solution Architecture

**Skills to activate:** `azure-enterprise-infra-planner`, `artifact-template-system-design`

**Inputs:** `.orchestrator/01-project-brief.md`

**Tasks:**
1. Activate `azure-enterprise-infra-planner` → high-level infrastructure design
2. Activate `artifact-template-system-design` → produce system design document covering:
   - Component diagram
   - Data flow diagram
   - Technology stack decisions
   - Integration points (internal + external)
   - Scalability and availability targets
   - Data storage strategy
3. Identify which downstream phases are required based on the architecture:
   - Does it need Figma design? → Phase 4 active
   - Does it use AI/ML services? → Phase 3 AI block active
   - Azure-based? → Phase 3 Security + Cost + Infra blocks active
   - Migration involved? → note for DevOps phase

**Output artifact:** `.orchestrator/02-architecture-plan.md`
**Template:** `handoff-templates/architecture-plan.md`

**Checklist before proceeding:**
- [ ] Architecture diagram or description complete
- [ ] Tech stack confirmed
- [ ] All integration points listed
- [ ] Phases 3–9 tailored to this architecture (irrelevant phases marked N/A)

---

## Phase 3 — Parallel Assessment Block

All four workstreams run **simultaneously**. Each reads `02-architecture-plan.md` as input.

### 3a. Security Assessment ⚡
**Skills:** `azure-compliance`, `azure-rbac`, `entra-app-registration`, `azure-validate`

Tasks:
- Define compliance requirements (SOC2, HIPAA, GDPR, ISO27001 as applicable)
- Design RBAC model — roles, permissions, least-privilege assignments
- Plan Entra ID app registrations and service principals
- Security checklist for the architecture

Output: `.orchestrator/03a-security-plan.md`

### 3b. Cost Estimation ⚡
**Skills:** `azure-cost`, `capacity`, `artifact-template-financial-budget`

Tasks:
- Estimate Azure resource costs (compute, storage, networking, services)
- Capacity planning — right-sizing VMs, K8s nodes, storage tiers
- Produce budget artifact with monthly/annual projections
- Flag cost optimization opportunities

Output: `.orchestrator/03b-cost-estimate.md`

### 3c. Infrastructure Plan ⚡
**Skills:** `azure-prepare`, `azure-enterprise-infra-planner`, `azure-quotas`

Tasks:
- Define subscription and resource group structure
- Check and request Azure quota increases if needed
- Network topology (VNets, subnets, NSGs, private endpoints)
- Environment strategy (dev / staging / prod)
- IaC tool selection (Bicep, Terraform, ARM)

Output: `.orchestrator/03c-infra-plan.md`

### 3d. AI/ML Assessment ⚡ (only if project uses AI)
**Skills:** `azure-ai`, `azure-aigateway`, `openai-docs`, `microsoft-foundry`, `azure-hosted-copilot-sdk`

Tasks:
- Select AI services and models appropriate to use-case
- Design AI gateway / API management layer
- Define model deployment strategy (`deploy-model`)
- Customization and fine-tuning plan (`customize`, `preset`)
- Token budgets, rate limits, fallback strategy

Output: `.orchestrator/03d-ai-plan.md`

**Merge:** After all parallel tasks complete, create `.orchestrator/03-parallel-summary.md` listing all findings and any cross-cutting concerns.

---

## Phase 4 — Design (if applicable)

**Skills:** `figma-generate-design`, `figma-use`, `figma-generate-diagram`, `figma-generate-library`, `figma-use-figjam`

**Skip if:** Project is backend-only / API-only / CLI with no UI.

**Inputs:** `.orchestrator/02-architecture-plan.md`, `.orchestrator/03-parallel-summary.md`

**Tasks:**
1. `figma-use-figjam` → brainstorm UX flows and user journeys
2. `figma-generate-design` → generate wireframes / mockups
3. `figma-generate-library` → establish design token library (colors, fonts, components)
4. `figma-generate-diagram` → architecture and flow diagrams for documentation
5. `figma-implement-motion` → if animations are required
6. Hand design artifacts off to developer phase

**Output artifact:** `.orchestrator/04-design-plan.md`

**Checklist:**
- [ ] User flows documented
- [ ] Wireframes / mockups created
- [ ] Design system / tokens defined
- [ ] Figma files linked in artifact
- [ ] Accessibility requirements noted

---

## Phase 5 — Development Sprint Planning

**Skills:** `github`, `figma-design-to-code`, `figma-code-connect`, `figma-swiftui`, `artifact-template-project-tracker`

**Inputs:** All prior artifacts (02, 03, 04 as applicable)

**Tasks:**
1. Activate `artifact-template-project-tracker` → break architecture into development tasks / stories
2. Group tasks into sprints. Identify task dependencies.
3. Mark independent tasks as ⚡ PARALLEL within each sprint
4. `figma-design-to-code` → convert Figma designs into frontend code stubs
5. `figma-code-connect` → link Figma components to code components
6. `figma-swiftui` → if building iOS / macOS native app
7. `github` → set up repository structure, branch strategy, PR templates, CI workflow
8. Activate `gh-fix-ci` → configure CI pipeline

**Output artifact:** `.orchestrator/05-sprint-plan.md`
**Template:** `handoff-templates/sprint-plan.md`

**Sprint structure:**
- Each sprint entry: `Sprint N | Tasks: [...] | Parallel: [...] | Dependencies: [...]`
- Clearly separate "can start immediately" vs "blocked by X"

---

## Phase 6 — QA and Code Review

**Skills:** `review-agent`, `gh-address-comments`, `yeet`, `azure-validate`

**Inputs:** `.orchestrator/05-sprint-plan.md`, actual code produced

**Tasks:**
1. `review-agent` → perform code review on each PR / code chunk:
   - Security vulnerabilities
   - Performance concerns
   - Code quality and standards
   - Test coverage
2. `gh-address-comments` → process and resolve review comments
3. `azure-validate` → validate Azure resource configurations (ARM/Bicep templates)
4. For each sprint: review → address → re-review cycle until approval
5. Track review findings in `.orchestrator/06-review-report.md`

**Output artifact:** `.orchestrator/06-review-report.md`

**Gate criteria (do not proceed to Phase 7 until):**
- [ ] All critical and high severity findings resolved
- [ ] Azure resource configs validated
- [ ] At least one clean review-agent pass
- [ ] PR comments addressed

---

## Phase 7 — Deployment Planning

**Skills:** `azure-deploy`, `azure-kubernetes`, `azure-compute`, `azure-storage`, `azure-messaging`, `microsoft-foundry`, `deploy-model`, `azure-prepare`

**Inputs:** `.orchestrator/03c-infra-plan.md`, `.orchestrator/06-review-report.md`

**Tasks:**
1. `azure-prepare` → provision environments (dev → staging → prod)
2. `azure-compute` / `azure-kubernetes` → deploy compute resources
3. `azure-storage` / `azure-messaging` → provision data and messaging services
4. `azure-deploy` → deploy application components
5. `deploy-model` + `microsoft-foundry` → deploy AI models (if applicable)
6. `gh-fix-ci` → finalize CD pipeline (staging gates, rollback strategy)
7. Run smoke tests post-deployment

**Output artifact:** `.orchestrator/07-deployment-plan.md`
**Template:** `handoff-templates/deployment-checklist.md`

**Deployment order within this phase:**
```
1. Networking (VNets, NSGs, private endpoints)
2. Storage and databases
3. Messaging / event infrastructure
4. Compute (VMs, AKS clusters)
5. Application workloads
6. AI/ML models
7. Frontend / CDN
8. DNS and traffic routing
```

---

## Phase 8 — Post-Deployment Parallel Block

All workstreams run **simultaneously** after deployment succeeds.

### 8a. Monitoring and Alerting ⚡
**Skills:** `appinsights-instrumentation`, `azure-diagnostics`

Tasks:
- Instrument application with Application Insights SDK
- Set up diagnostic settings for all Azure resources
- Define alert rules (error rate, latency, availability)
- Configure dashboards

Output: `.orchestrator/08a-monitoring.md`

### 8b. Resource Visualization ⚡
**Skills:** `azure-resource-visualizer`, `azure-resource-lookup`

Tasks:
- Generate visual map of all deployed Azure resources
- Verify resource inventory matches architecture plan
- Document resource IDs, connection strings (reference only, no secrets in docs)

Output: `.orchestrator/08b-resource-map.md`

### 8c. Operating Calendar ⚡
**Skills:** `artifact-template-operating-calendar`, `artifact-template-operating-review`

Tasks:
- Define recurring operational tasks (patching, backups, cost reviews, security scans)
- Create operating review cadence
- Set up runbook stubs

Output: `.orchestrator/08c-ops-calendar.md`

---

## Phase 9 — Documentation and Project Closure

**Skills:** `iac-project-control`, `artifact-template-design-report`, `artifact-template-business-review`, `artifact-template-strategy-memorandum`, `artifact-template-team-alignment`

**Inputs:** All prior artifacts

**Tasks:**
1. `iac-project-control` → compile final project control documentation:
   - Decisions log
   - Risk register (outcomes)
   - Lessons learned
2. `artifact-template-design-report` → final architecture and design report
3. `artifact-template-business-review` → executive summary for stakeholders
4. `artifact-template-team-alignment` → team handover document (who owns what)
5. Produce `.orchestrator/INDEX.md` — master index linking all artifacts
6. Ask user: archive project? → zip `.orchestrator/` directory

**Output artifact:** `.orchestrator/09-final-docs.md` + `.orchestrator/INDEX.md`

**Project closure checklist:**
- [ ] All phase artifacts saved and linked in INDEX.md
- [ ] Open questions resolved or documented as known limitations
- [ ] Runbooks written for operational tasks
- [ ] Ownership and contacts documented
- [ ] Repository and CI/CD pipelines healthy
- [ ] Monitoring and alerting confirmed active
