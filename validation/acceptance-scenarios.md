# Project Orchestrator v2 — Acceptance Scenario Manifest

> **Status:** Approved CHG-001 validation contract — scenarios are documented, not executable yet.
> **Purpose:** Define representative behaviors the redesigned runtime must eventually satisfy before v1 execution logic is retired.

Each scenario records **Given / When / Expected orchestration result**, including scope, authority, and project-control effects.

## S01 — Simple software project

**Given:** A project has no AI workload, no special compliance requirement, a simple DEV → QA → PROD topology, and sufficient installed development/deployment capabilities.

**When:** The project moves from planning through build, QA, and release.

**Expected:** Only relevant specialists/gates are invoked; unnecessary AI/compliance work is not created. Work progresses through dependency/gate state rather than fixed numbered phases. Production follows configured approval policy.

## S02 — Parallel development

**Given:** API, UI, and test-automation work have no mutual hard dependencies, but later integration work depends on all three.

**When:** The three items become ready.

**Expected:** They are parallel-eligible and dispatched within executor/resource capacity. Integration remains not ready until its hard prerequisites are satisfied. Shared-resource conflicts may still serialize work.

## S03 — QA defect and rework

**Given:** A release candidate reaches QA and a blocking defect is found.

**When:** QA fails its governed criteria.

**Expected:** A defect/rework path is created or the failed item is reopened as appropriate; the affected release path is blocked; unrelated work continues; changed implementation is re-reviewed/retested and affected gates are reevaluated before promotion.

## S04 — Non-blocking parked bug

**Given:** QA finds a low-severity defect that policy permits deferring.

**When:** The defect is assessed against acceptance/release gates.

**Expected:** The bug is parked with reason, owner, residual risk/impact, target/revisit trigger, and traceability. The current release may continue if all mandatory gates remain satisfied.

## S05 — Missing capability with autonomous resolution

**Given:** A ready task requires a capability with no eligible executor; a matching specialist exists in an approved trusted catalog and project policy allows autonomous installation for its permission profile.

**When:** The capability gap is processed.

**Expected:** Candidate discovery/evaluation occurs, installation is governed but autonomous, post-install validation and registry refresh complete, the specialist becomes task-eligible, and work resumes without Product Owner interruption.

## S06 — Missing capability requiring approval

**Given:** A required capability is missing; the best candidate is an unverified GitHub repository requesting elevated terminal/cloud access.

**When:** The capability gap is processed.

**Expected:** Discovery does not imply trust or installation. The affected path remains blocked while independent work continues. A structured decision package presents candidate, permissions/trust concerns, alternatives, schedule impact, recommendation, and required authority.

## S07 — Human takes over execution

**Given:** An AI/agent executor owns a ready/in-progress task.

**When:** The user chooses to perform the task personally.

**Expected:** Executor assignment changes to the human. Objective, dependencies, acceptance criteria, evidence requirements, gates, and traceability remain unchanged. Other project work continues autonomously.

## S08 — Human-default production approval

**Given:** All technical release gates pass and project policy uses the default human approval for production.

**When:** Production promotion becomes otherwise ready.

**Expected:** Production remains gated pending authorized human approval. Preparation/execution and approval remain distinct roles. Non-production/future work may continue where independent.

## S09 — Critical-path schedule slip

**Given:** A work item on a calculable release critical path slips beyond a configured material-variance threshold.

**When:** Actual/progress information updates the schedule.

**Expected:** Forecast dates and Gantt/critical path are recalculated; the approved baseline remains unchanged; relevant risk/issue/project-attention records are created or updated; mitigation/replanning is attempted; consequential baseline/scope choices escalate only if authority is required.

## S10 — Material architecture change invalidates affected gates

**Given:** Authentication architecture was previously validated and linked QA/security evidence exists.

**When:** Authentication implementation/architecture changes materially.

**Expected:** Impact analysis identifies affected requirements/tests/evidence/gates. Relevant security/QA gate results become stale/invalid and require reevaluation. Unrelated evidence/gates remain valid.

## S11 — Infrastructure agnosticism

**Given:** Equivalent projects target Azure, AWS, GCP, or generic/on-prem infrastructure.

**When:** Infrastructure architecture/deployment work is required.

**Expected:** The core orchestrator requests capabilities and enforces project policy consistently. Provider-specific specialist selection/mechanics vary, while the core project-control workflow does not contain provider-specific mandatory rules.

## S12 — AI-enabled lifecycle

**Given:** A project includes an AI model/provider and explicit quality/safety/cost/latency requirements.

**When:** Architecture, build, validation, release, and operation occur, including a later material model or prompt/agent change.

**Expected:** AI specialist work is lifecycle-wide and trigger-driven; evaluation/evidence/gates reflect project requirements; cost/observability/security are invoked when materially affected. Equivalent non-AI projects do not receive unnecessary AI work.

## S13 — Production incident

**Given:** A production deployment is operating and monitoring detects a critical availability incident.

**When:** Incident policy triggers.

**Expected:** Incident record/response work is created; production promotions may freeze according to scope; operations/application specialists are engaged; rollback/recovery is evaluated/executed under authority policy; service recovery is validated; RCA/follow-up risks/bugs/architecture/observability work is created as appropriate; unaffected DEV/QA planning may continue.

## S14 — Authorized hotfix path

**Given:** Project policy defines a hotfix route with a reduced but explicit gate set and authority rules.

**When:** A qualifying urgent defect requires release.

**Expected:** The orchestrator uses the configured hotfix promotion path, preserves artifact/evidence/deployment traceability, applies the required shortened controls, and does not invent an undocumented bypass.

## S15 — Specialist quarantine

**Given:** A registered specialist exhibits unexpected permission behavior or another material trust/integrity concern.

**When:** The concern is classified as quarantine-worthy.

**Expected:** The specialist becomes ineligible for new tasks; historical capability/execution records remain; affected work is paused/reassigned/recovered; clearing quarantine requires remediation/revalidation and proper authority.

## S16 — Human edits canonical Markdown

**Given:** Canonical project records are stored as portable Markdown with structured metadata.

**When:** A human directly edits a canonical record.

**Expected:** Referential/state validation processes the edit; valid changes update project state and affected derived views; invalid semantic/reference changes are flagged rather than silently accepted. Human edits follow the same project-control rules as agent changes.

## S17 — Broken release traceability/evidence

**Given:** A release claims completion of a requirement but required verification evidence is missing or points to the wrong artifact/version.

**When:** Release readiness is evaluated.

**Expected:** Traceability validation identifies the evidence gap. A mandatory release gate cannot pass unless policy explicitly permits an authorized waiver. Generated release/status views expose the exception.

## S18 — Cross-specialist convergence conflict

**Given:** Security, Cost, and Infrastructure specialists produce materially conflicting recommendations for the same architecture decision.

**When:** Their parallel work completes.

**Expected:** A convergence review attempts technical reconciliation. If no technically dominant solution exists within approved constraints, the orchestrator produces a decision package containing specialist positions, options, trade-offs, recommendation, required authority, blocked scope, and unaffected work.

## Scenario execution status

CHG-001 establishes this manifest only. These scenarios become executable/manual acceptance tests incrementally as their owning runtime subsystems are implemented.
