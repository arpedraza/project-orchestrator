# Legacy v1 Phase Model

> **LEGACY / MIGRATION REFERENCE ONLY**
>
> This file is **not runtime authority** for Project Orchestrator v2. Do not execute the former numbered 1–9 phases as a program counter.

Project Orchestrator v2 is driven by canonical Work Items, Dependencies, Gates, environment state, capability/authority matching, evidence, and recovery. High-level lifecycle stages remain useful for reporting and stakeholder navigation, but multiple work items and releases may occupy different stages simultaneously.

## Where the useful v1 concepts moved

The former phase content was migrated into the v2 source architecture:

- project lifecycle and cross-cutting participation → `references/operating-model.md` and `references/lifecycle-environments.md`
- dependencies, parallel work, scheduling, milestones and gates → `references/scheduling-gates.md`
- failure/rework/blocking/escalation → `references/recovery-change-control.md`
- requirements, RAID, decisions, evidence, releases and deployment traceability → `references/project-control-traceability.md`
- Markdown handoffs/documentation → `references/documentation-model.md`
- executable orchestration behavior → `SKILL.md` and `scripts/orchestrate_project.py`

## Historical source

The full v1 phase specification remains available in Git history and on the permanent `baseline/orchestrator-v1` branch.

Use it only when maintaining or understanding a legacy v1 project. New and migrated v2 projects must follow the state-driven model described in `SKILL.md` and the v2 references.
