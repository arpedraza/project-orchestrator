# Project Orchestrator v2 — Project State Model

> **Status:** CHG-003 machine state contract and semantic validation are implemented. Main orchestration remains v1 until later migration batches.
> **Current runtime authority:** `SKILL.md` and v1 phase execution still control project flow; CHG-003 provides validated state interfaces only.

## Design provenance

Implements **Detailed Design 1 — Core Project / Work / State Model**.

**Runtime activation:** Project State / Work / Dependency / Gate machine contracts and semantic validation are active in CHG-003. Scheduling, dispatch, environment promotion, policy evaluation, and the new orchestration loop remain pending.

## Foundational objects

The v2 execution model is built on four foundational objects:

1. **Project State** — project-level context, policy references, milestones, environments, releases, and register references.
2. **Work Item** — an executable unit of project work.
3. **Dependency** — an explicit prerequisite or timing relationship.
4. **Gate** — explicit transition control backed by criteria, evidence, evaluators, and authority.

Gantt, Kanban, status, critical-path, sprint, and release dashboards are generated from these records.

## Project State

Project State is the logical project control root. It supports, conceptually:

- stable `project_id` and project identity;
- objective and current project status;
- reporting stage;
- active approved baseline and forecast context;
- project policies and authority references;
- milestones;
- environments and active releases;
- references to requirements, RAID, decisions, work, quality, and releases.

The reporting stage is never the primary runtime program counter.

## Baseline, forecast, actual

Three schedule concepts remain separate:

- **Baseline** — the approved planned commitment.
- **Forecast** — the current expected outcome based on present project state.
- **Actual** — what actually occurred.

Routine execution changes the forecast. A material change to the approved baseline occurs only through controlled replanning according to authority policy. Historical baselines are preserved.

CHG-003 represents these fields distinctly and validates date-time shape where supplied. It does not calculate schedule outcomes.

## Work Item

A Work Item is the canonical executable unit for architecture, design, implementation, infrastructure, QA, security, documentation, human work, AI work, automation, release work, and operational work.

A work item supports, conceptually:

- stable ID and extensible type;
- title and objective;
- parent/hierarchy link;
- reporting stage and execution state;
- priority;
- required and preferred capabilities;
- executor assignment;
- environment/release scope;
- estimates and baseline/forecast/actual dates where applicable;
- dependencies and gates;
- acceptance criteria;
- traceability links to requirements, ADRs, decisions, risks/issues, and changes;
- outputs and evidence references.

CHG-003 defines the machine/runtime JSON projection for this contract. Durable canonical project knowledge remains Markdown-first and is not replaced by the runtime State Bundle.

## Work taxonomy

The taxonomy is configurable and methodology-neutral. Supported concepts may include Initiative, Epic, Feature, Story, Task, Bug, Spike, Change, Review, Decision, Release, and Operational Task.

The core model must not force Scrum, Kanban, SAFe, or another methodology. CHG-003 therefore validates `type` as an extensible non-empty string rather than a fixed enum.

## Work state machine

Primary states:

```text
PROPOSED
READY
IN_PROGRESS
NEEDS_REVIEW
WAITING
NEEDS_REWORK
BLOCKED
NEEDS_DECISION
DONE
PARKED
CANCELLED
SUPERSEDED
```

`WAITING` represents an expected normal wait, such as CI execution or a scheduled window within the expected service level. `BLOCKED` means the work cannot reasonably progress and may need intervention or replanning.

Parking is controlled and records its reason, owner/resolver, date, revisit trigger, priority, target release where known, and related risk. Detailed parking/change/recovery fields are implemented in their later owning batch.

## Executor neutrality

The work contract remains the same whether the executor is a human, agent, automation, or external system. Acceptance criteria, evidence, gates, dependencies, and traceability do not change when the executor changes.

CHG-003 represents executor assignment but does not evaluate executor eligibility or authority.

## Dependency model

Dependencies are first-class objects. The model supports logical prerequisites plus scheduling relationships such as:

- Finish-to-Start (default);
- Start-to-Start;
- Finish-to-Finish;
- Start-to-Finish;
- lead/lag;
- hard versus soft dependency strength.

A dependency may reference work, a gate, a decision, an artifact, an environment, an external dependency, or capability availability.

CHG-003 activates typed references, `FS`/`SS`/`FF`/`SF`, `HARD`/`SOFT`, explicit lag units, dependency status, waiver decision references, local reference validation, and HARD-cycle detection. It does not yet calculate schedule timing.

`AT_RISK` represents a dependency that remains usable but has elevated risk; it does not automatically become unsatisfied. `UNSATISFIED` and `BROKEN` hard dependencies block a `READY` work state. A validly `WAIVED` hard dependency requires a decision reference.

## Gate model

A gate controls a governed transition and supports:

- stable ID/name/category;
- scope and blocking behavior;
- criteria;
- approval policy reference;
- evaluator capability requirements;
- status/result;
- evidence references;
- waiver/decision references.

Statuses:

```text
NOT_READY
READY
EVALUATING
PASSED
FAILED
WAIVED
```

CHG-003 also represents gate validity independently:

```text
VALID
STALE
INVALIDATED
```

`WAIVED` is not `PASSED`. A waiver requires a decision reference. A `PASSED` gate requires non-empty evaluated scope, current `VALID` status, supporting evidence, and all required criteria satisfied. Material-change impact/invalidation is represented but the automatic invalidation engine is implemented later.

## State Bundle and semantic validator

CHG-003 introduces `state-bundle.schema.json` as a machine/runtime projection containing Project State, Work Items, Dependencies, and Gates. It exists to make cross-record validation deterministic and is not a fifth canonical project-control object.

`python3 scripts/validate_state.py <state-bundle.json>` performs semantic validation and returns deterministic finding codes. The validator currently enforces:

- globally unique stable IDs within the bundle;
- local parent/dependency/gate reference integrity;
- HARD dependency cycle rejection;
- `READY` blocking for `UNSATISFIED`/`BROKEN` hard dependencies;
- decision references for dependency/gate waivers;
- required acceptance criteria before `DONE`;
- required gates before `DONE`;
- gate scope/evidence/criterion/validity requirements for `PASSED`;
- executor representation neutrality;
- baseline/forecast/actual field separation and supplied date-time shape.

Authority validity of a decision reference, task dispatch, scheduling, and environment/promotion semantics remain outside CHG-003.

## Canonical versus derived state

Canonical facts include work definitions, dependencies, acceptance criteria, gates, assignments, approved baselines, actual dates/results, decisions, risks/issues, evidence, and policies.

Derived views include Gantt, critical path, Ready Queue, Kanban, health dashboards, forecasts, sprint reports, status summaries, traceability matrices, and release dashboards.

The CHG-003 JSON State Bundle is a deterministic runtime projection/cache. It must not become the sole authoritative copy of durable project facts.

## Core invariants

1. Work cannot enter `READY` while a hard blocking dependency is unsatisfied or broken.
2. Work cannot become `DONE` until required acceptance criteria and mandatory gates are satisfied.
3. A failed blocking gate prevents only its governed transition/dependent path unless its scope is explicitly broader.
4. Material relevant changes invalidate affected prior gate evidence.
5. Human and AI/automation/external executors follow the same acceptance/evidence contract.
6. `WAIVED` never equals `PASSED` and requires proper authority; CHG-003 validates the decision reference while authority validation comes later.
7. Routine schedule changes update forecast, not the approved baseline.
8. Gantt, status, and traceability views are never independent truth.
9. Consequential state changes record who/what made the change and why; event-history implementation comes in a later batch.
10. Capability failure triggers recovery/capability-gap logic before project-wide escalation; recovery integration comes later.
