# Project Orchestrator v2 — Source Architecture & Migration Plan

> **Status:** Approved target design — CHG-001 documentation only; not active runtime behavior.
> **Current runtime authority:** Existing v1 source files remain authoritative until each migration batch is approved and completed.

## Design provenance

Implements **Detailed Design 9 — Source Architecture & File Migration Plan** and records the approved CHG-001 boundary.

## Layered package architecture

The target source package separates four responsibilities:

```text
1. ENTRY / ORCHESTRATION
   SKILL.md

2. REFERENCE / POLICY
   operating model, state, capabilities, scheduling, lifecycle,
   recovery, project control, documentation, authority, validation

3. SCHEMAS / TEMPLATES / CATALOGS / PROFILES
   machine definitions, canonical/runtime templates,
   role/capability bootstrap metadata, policy profiles

4. EXECUTABLE UTILITIES
   discovery, validation, state/view generation
```

The main `SKILL.md` remains the conductor and should not grow into a monolithic repository of every methodology detail.

## Target source layout

Conceptually:

```text
project-orchestrator/
├── SKILL.md
├── references/
├── schemas/
├── templates/ or migrated handoff/template structure
├── catalog/
├── profiles/
├── scripts/
└── validation/
```

Exact serialization formats for schemas/catalogs/profiles remain deferred until their implementation batches.

## `SKILL.md` target responsibility

The future `SKILL.md` owns:

- Project Orchestrator identity/conductor principle;
- startup/loading/validation/registry refresh;
- the top-level event/state orchestration loop;
- when to consult dedicated references;
- authority boundary and escalation behavior.

It should not inline provider-specific deployment sequences, fixed phase-to-skill maps, exhaustive RAID schemas, scheduling details, capability keyword catalogs, or all templates.

## Target orchestration loop

```text
BOOTSTRAP
├─ detect runtime/project
├─ load/create project control structure
├─ validate canonical records/state
├─ refresh capability registry
└─ evaluate policies
      │
      ▼
LOOP
├─ process events/changes
├─ update dependency/gate state
├─ calculate READY work
├─ resolve capabilities/executors
├─ dispatch within capacity/policy
├─ collect outcomes/evidence
├─ evaluate gates
├─ recover/rework/replan/escalate as needed
├─ update RAID/decisions/changes
├─ recalculate schedule/milestones
└─ refresh generated documentation/views
```

When no work is ready, the controller distinguishes completed projects, normal waiting, recoverable blockers, decision requirements, and capability gaps.

## Existing-file migration

| Current file | Approved target disposition |
|---|---|
| `SKILL.md` | Major rewrite only after supporting models exist |
| `phases.md` | Retire as execution controller; migrate useful lifecycle/domain content |
| `role-mapping.md` | Retire as routing authority; migrate roles/catalog hints to capability architecture |
| `scripts/scan-skills.sh` | Keep compatibility entry point; harden/refactor implementation |
| `handoff-templates/project-brief.md` | Keep concept; split intake vs approved brief semantics later |
| `handoff-templates/architecture-plan.md` | Keep concept; make provider-neutral and traceability/gate aware later |
| `handoff-templates/sprint-plan.md` | Retain as generated planning view, not canonical work state |
| `handoff-templates/deployment-checklist.md` | Retain release concepts; remove generic Azure assumptions and make promotion/gate driven |

No existing file is discarded without migrating useful knowledge.

## Reference ownership

- `operating-model.md` — concise architectural overview.
- `project-state.md` — Project State, Work, Dependency, Gate semantics.
- `capabilities-executors.md` — capability/executor/routing contract.
- `scheduling-gates.md` — dependency/scheduling/dispatch/gate model.
- `lifecycle-environments.md` — lifecycle, environment topology, cross-cutting triggers.
- `recovery-change-control.md` — failure, recovery, change, escalation.
- `project-control-traceability.md` — requirements, ADRs, RAID, evidence, releases, traceability.
- `documentation-model.md` — canonical/generated/working knowledge architecture and Scriber.
- `discovery-registry.md` — scanner, registry, trust, installation.
- `policy-authority.md` — cross-cutting authorization policy.
- `validation-rules.md` — consolidated invariants and architecture acceptance rules.

## Planned implementation batches

0. Preserve existing source baseline.
1. Add package skeleton and approved design references/validation manifests. **CHG-001**.
2. Scanner and capability registry.
3. Project State / Work / Dependencies / Gates.
4. Scheduler / lifecycle / environments / cross-cutting triggers.
5. Recovery / change control / project control / traceability.
6. Documentation/Scriber/runtime handoff model.
7. Rewrite main `SKILL.md` after underlying models exist.
8. Compatibility and scenario validation; retire/deprecate superseded v1 execution references.

Each functional batch requires its own plan/review/approval before source behavior changes.

## CHG-001 boundary

CHG-001 may:

- preserve the exact v1 baseline in source control;
- establish a v2 feature branch;
- add `references/` design specifications;
- add structural `schemas/`, `catalog/`, and `profiles/` README placeholders;
- add validation scenario manifests.

CHG-001 must not modify the text or runtime behavior of:

- `SKILL.md`;
- `phases.md`;
- `role-mapping.md`;
- `scripts/scan-skills.sh`;
- the four existing handoff templates.

The new v2 files are intentionally unreferenced by the active runtime during CHG-001.

## Default future project runtime layout

The approved default project workspace is:

```text
project/
├── docs/
│   ├── 00-project-control/
│   ├── 10-requirements/
│   ├── 20-architecture/
│   ├── 30-decisions/
│   ├── 40-delivery/
│   ├── 50-quality/
│   ├── 60-releases/
│   ├── 70-operations/
│   ├── 80-reviews/
│   └── INDEX.md
└── .orchestrator/
    ├── state/
    ├── registry/
    ├── runs/
    ├── handoffs/
    ├── checkpoints/
    ├── cache/
    └── temporary/
```

The layout is a default profile and may be adapted when project requirements justify it.

## MVP boundary

The first redesigned runtime should prove the control architecture: specialist discovery/registry, canonical project state, dependencies/gates, ready work, executor delegation, parallelism with constraints, QA/rework/blocking/parking, configurable environments, production policy, RAID/decisions, traceability/evidence, Markdown status/index generation, capability gaps, structured escalation, and resumption.

Deferred concerns include full graphical UI, custom database, advanced probabilistic/resource optimization, proprietary Gantt engines, mandatory Obsidian plugins, opaque ML trust scoring, exhaustive provider integrations, and marketplace crawling.
