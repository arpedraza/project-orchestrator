# Project Orchestrator v2 — Dependency, Scheduling, Gate & Rework Engine

> **Status:** Approved target design — not active runtime behavior.
> **Current runtime authority:** Existing phase sequencing and phase-level parallel blocks remain active until the scheduling/gate migration is completed.

## Design provenance

Implements **Detailed Design 3 — Dependency, Scheduling, Gate & Rework Engine**.

**Runtime activation:** Planned for the Project State / Scheduling / Lifecycle implementation batches.

## Engine responsibilities

The execution-control engine has five logical responsibilities:

1. **Dependency engine** — what may proceed?
2. **Scheduling engine** — when should it occur?
3. **Dispatch engine** — what starts now within capacity/policy?
4. **Gate engine** — may a transition advance?
5. **Recovery engine** — what happens when execution or validation fails?

## Dependency graph

The dependency graph is the execution backbone. Fixed phase order is not the runtime program counter.

Independent nodes become eligible for concurrent execution when their hard prerequisites are satisfied. Actual dispatch also considers executor capacity, resource conflicts, priority, risk, milestones, and policy.

Hard dependency graphs must remain cycle-free. A proposed hard dependency that creates a cycle is rejected or requires restructuring/decision review.

## Logical and schedule relationships

Logical dependencies answer **what must be true**. Schedule relationships answer **how timings relate**.

Supported schedule relationships are:

- Finish-to-Start (default);
- Start-to-Start;
- Finish-to-Finish;
- Start-to-Finish;
- lead/lag.

Default is hard Finish-to-Start with zero lag when no richer relation is required.

Dependencies may be hard or soft. Hard prerequisites prevent governed progress. Soft relationships express planning preference and may be overridden through controlled reasoning/policy.

## Ready calculation

A work item enters `READY` only when all mandatory start conditions are satisfied, including as applicable:

- hard dependencies;
- required inputs/artifacts;
- environment readiness;
- required prior gates;
- no unresolved blocking decision;
- required capabilities resolvable;
- policy permits start.

`READY` means eligible, not automatically dispatched.

## Dispatch and parallelism

Dispatch selects from ready work based on priority, critical-path/milestone impact, executor availability, resource contention, risk, and policy.

Parallel execution requires both dependency independence and absence of incompatible shared-resource conflicts. Resource locking may serialize tasks that are logically independent but contend for an exclusive resource or environment.

Agent concurrency is not assumed to be unlimited.

## Schedule model

Where useful, scheduled work may carry estimates, baseline dates, forecast dates, actual dates, remaining estimates, constraints, resource/calendar information, float, and critical-path status.

The scheduler updates **forecast**, not the approved baseline, during routine execution.

## Gantt and critical path

The Gantt is a generated planning and decision-support view derived from canonical work, dependencies, baseline, forecast, actuals, resources, and milestones. It is never project truth by itself.

Critical-path analysis is used only when schedule inputs are sufficient. The orchestrator must not manufacture false precision when durations/calendars are unknown.

Material schedule variance is evaluated through project policy and may create/update risks, issues, mitigation work, replanning, or decision requests.

## Milestones

Milestones are first-class zero-duration control objects representing meaningful project/release events. Milestone completion and forecast should be derived from their required tasks, gates, decisions, artifacts, and external dependencies where possible.

Baseline milestone date, forecast milestone date, and variance remain distinct.

## Gates

A gate governs a transition and is distinct from task execution. Gates may contain criteria evaluated by automation, specialists, humans, or combinations of them.

Composite gates may aggregate independent subordinate gates or criteria such as QA, Security, Observability, Infrastructure readiness, rollback readiness, business acceptance, and production approval.

Gate results require evidence and must state the evaluated scope: artifact/build/version, environment/configuration, release, model version, or other relevant identity.

## Gate invalidation

A material relevant change triggers impact analysis. Only affected gate results/evidence are invalidated. Irrelevant changes must not cause indiscriminate revalidation.

Traceability links are used to determine which requirements, components, tests, evidence, and gates are affected by a change.

## Rework and defects

Failed acceptance or gates result in explicit recovery paths such as retry, rework, linked defect creation, alternate executor, replanning, parking, blocking, or decision escalation.

Significant defects should normally be separate linked work records when that improves historical traceability. A minor direct failure of a work contract may instead reopen the original work item.

Defect blocking is severity-, gate-, and policy-driven. Not every bug blocks a release.

Autonomous retry/rework loops are bounded by policy.

## Environment promotion and rollback

Environment promotions are controlled work operations with executor, artifact identity, source/target environment, required gates, evidence, result, and rollback path.

Rollback is an executable recovery path, not merely a checklist statement. Post-deployment operational validation may still invalidate release success and trigger rollback/incident/rework.

## Invariants

1. Only dependency-satisfied work can enter `READY`.
2. `READY` means eligible, not necessarily dispatched.
3. Dispatch respects executor/resource capacity and policy.
4. Hard dependency cycles are invalid.
5. Forecast changes do not silently rewrite approved baseline.
6. Material forecast variance triggers project-control evaluation.
7. Parallel work requires dependency independence and compatible resource use.
8. A blocking gate controls only its governed transition/dependent scope unless explicitly broader.
9. Gate results reference evaluated scope and evidence.
10. Material relevant changes invalidate affected gate results.
11. Failure produces an explicit recovery path.
12. Autonomous retries/rework are bounded.
13. Defect blocking follows severity/gate/policy rather than existence alone.
14. Environment promotion is controlled work with evidence/gates.
15. Rollback is executable controlled recovery.
16. Material task, gate, schedule, assignment, and release state changes are auditable.
