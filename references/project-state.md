# Project Orchestrator v2 — Project State Model

> **Status:** Approved target design — not active runtime behavior.
> **Current runtime authority:** Existing v1 orchestration files remain authoritative until the state-engine migration is approved and completed.

## Design provenance

Implements **Detailed Design 1 — Core Project / Work / State Model**.

**Runtime activation:** Planned for the Project State / Work / Dependency / Gate implementation batch.

## Foundational objects

The v2 execution model is built on four foundational objects:

1. **Project State** — project-level context, policy references, milestones, environments, releases, and register references.
2. **Work Item** — an executable unit of project work.
3. **Dependency** — an explicit prerequisite or timing relationship.
4. **Gate** — explicit transition control backed by criteria, evidence, evaluators, and authority.

Gantt, Kanban, status, critical-path, sprint, and release dashboards are generated from these records.

## Project State

Project State is the logical project control root. It should support, conceptually:

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

## Work Item

A Work Item is the canonical executable unit for architecture, design, implementation, infrastructure, QA, security, documentation, human work, AI work, automation, release work, and operational work.

A work item should support, conceptually:

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

Exact serialization is intentionally deferred.

## Work taxonomy

The taxonomy is configurable and methodology-neutral. Supported concepts may include Initiative, Epic, Feature, Story, Task, Bug, Spike, Change, Review, Decision, Release, and Operational Task.

The core model must not force Scrum, Kanban, SAFe, or another methodology.

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

Parking is controlled and records its reason, owner/resolver, date, revisit trigger, priority, target release where known, and related risk.

## Executor neutrality

The work contract remains the same whether the executor is a human, agent, automation, or external system. Acceptance criteria, evidence, gates, dependencies, and traceability do not change when the executor changes.

## Dependency model

Dependencies are first-class objects. The model supports logical prerequisites plus scheduling relationships such as:

- Finish-to-Start (default);
- Start-to-Start;
- Finish-to-Finish;
- Start-to-Finish;
- lead/lag;
- hard versus soft dependency strength.

A dependency may reference work, a gate, a decision, an artifact, an environment, an external dependency, or capability availability.

## Gate model

A gate controls a governed transition and should support:

- stable ID/name/category;
- scope and blocking behavior;
- criteria;
- approval policy;
- evaluator capability requirements;
- status/result;
- evidence references;
- waiver/decision references.

Conceptual statuses:

```text
NOT_READY
READY
EVALUATING
PASSED
FAILED
WAIVED
```

`WAIVED` is not `PASSED`. A waiver requires authorized evidence/decision. Gate results are valid only for the evaluated scope/version/evidence. Material relevant changes invalidate affected gate results and require re-evaluation.

## Canonical versus derived state

Canonical facts include work definitions, dependencies, acceptance criteria, gates, assignments, approved baselines, actual dates/results, decisions, risks/issues, evidence, and policies.

Derived views include Gantt, critical path, Ready Queue, Kanban, health dashboards, forecasts, sprint reports, status summaries, traceability matrices, and release dashboards.

## Core invariants

1. Work cannot enter `READY` while a hard blocking dependency is unsatisfied.
2. Work cannot become `DONE` until required acceptance criteria and mandatory gates are satisfied.
3. A failed blocking gate prevents only its governed transition/dependent path unless its scope is explicitly broader.
4. Material relevant changes invalidate affected prior gate evidence.
5. Human and AI/automation executors follow the same acceptance/evidence contract.
6. `WAIVED` never equals `PASSED` and requires proper authority.
7. Routine schedule changes update forecast, not the approved baseline.
8. Gantt, status, and traceability views are never independent truth.
9. Consequential state changes record who/what made the change and why.
10. Capability failure triggers recovery/capability-gap logic before project-wide escalation.
