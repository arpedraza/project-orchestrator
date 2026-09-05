# Project Orchestrator v2 — Operating Model

> **Status:** Approved target design — not active runtime behavior.
> **Current runtime authority:** `SKILL.md`, `phases.md`, `role-mapping.md`, and the existing handoff templates remain authoritative until their migration batches are approved and completed.

## Design provenance

Implements the approved operating principles established across Detailed Designs 1–9.

**Runtime activation:** Pending later migration batches, especially the final `SKILL.md` rewrite.

## Purpose

Project Orchestrator v2 is an autonomous project-delivery controller. It coordinates specialist skills, agents, humans, automation, and external systems; maintains project state; manages dependencies, gates, schedules, risks, decisions, environments, and evidence; and escalates only when a decision or action exceeds delegated authority.

The orchestrator is the conductor. It does not replace domain specialists and must not perform specialist work merely because it can describe that work.

## Core operating model

```text
Project intent / approved baseline
            │
            ▼
     Canonical project state
            │
     ┌──────┼─────────────┐
     ▼      ▼             ▼
 dependencies gates    policies
     │      │             │
     └──────┼─────────────┘
            ▼
       READY work
            │
            ▼
 capability + executor resolution
            │
            ▼
          execute
            │
            ▼
   outcome + evidence + events
            │
            ▼
 update state / gates / RAID / schedule
            │
            ▼
 recover, continue, or escalate
            │
            ▼
 update generated documentation/views
```

## Stages are not the execution engine

High-level stages such as Initiate, Plan/Architect, Prepare, Build, Validate, Release, Operate, and Improve/Close exist for human reporting, milestones, and governance context.

Execution is controlled by a dependency-aware work/state graph. Multiple work items and releases may occupy different stages and states simultaneously.

## Autonomy boundary

The orchestrator continues autonomously when a problem or action can be resolved within approved scope, policy, risk tolerance, schedule/cost thresholds, and delegated authority.

It escalates when a consequential choice, policy exception, unresolved blocker, risk acceptance, production approval, or other action requires higher authority.

Escalation packages must include context, feasible options, impacts, a recommendation, the authority required, the affected scope, and work that can continue independently.

## Executor independence

Workflows, quality gates, documentation, and traceability are executor-independent. An executor may be a human, AI/agent, automation, or external system if it satisfies the required capability, authority, acceptance criteria, and evidence contract.

A human taking over a task is executor reassignment, not a separate workflow.

## Provider and methodology neutrality

The core orchestrator requests capabilities and enforces project policy. It does not hard-code Azure, AWS, GCP, Kubernetes, Scrum, Kanban, SAFe, or another provider/methodology as universal behavior.

Provider-specific implementation belongs to selected specialists. Work-item taxonomy, environment topology, gates, profiles, and planning sophistication are configurable.

## Canonical state and derived views

Canonical facts include work definitions, dependencies, gates, approved baselines, actual results, decisions, risks/issues, evidence, releases, policies, and authority decisions.

Gantt charts, Kanban boards, sprint plans, status summaries, RAID dashboards, release dashboards, and traceability matrices are derived views. They never become an independent source of truth.

## Continuous cross-cutting engineering

Security, Infrastructure, Cost, AI, and Observability are involved through baseline assessment, relevant event triggers, mandatory gates where applicable, and operational feedback. They are not one-time phases.

## Recovery principle

Failure affects the relevant dependency path, not automatically the whole project. Recovery prefers transient retry, rework, alternate executors, decomposition, capability-gap resolution, parking of permitted non-blocking work, and replanning before project-wide escalation.

## Knowledge principle

Durable project knowledge is Markdown-first and portable. Canonical project records live outside runtime scratch state. Generated views and executor handoffs derive from the same canonical project state. Obsidian is supported as an optional interface but is never required.

## Related references

- `project-state.md`
- `capabilities-executors.md`
- `scheduling-gates.md`
- `lifecycle-environments.md`
- `recovery-change-control.md`
- `project-control-traceability.md`
- `documentation-model.md`
- `discovery-registry.md`
- `policy-authority.md`
- `validation-rules.md`
