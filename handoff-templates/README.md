# Legacy v1 Handoff Templates

The four templates in this directory are preserved for **v1 compatibility and migration history only**:

- `project-brief.md`
- `architecture-plan.md`
- `sprint-plan.md`
- `deployment-checklist.md`

Project Orchestrator v2 does not use numbered phase handoffs as its primary project memory. Durable project truth is stored as canonical Markdown records under `docs/`, while regenerable executor context is produced under `.orchestrator/handoffs/`.

For v2 use:

- canonical record template → `../templates/canonical/record.md`
- runtime handoff template → `../templates/runtime/work-handoff.md`
- workspace/sync/render/handoff CLI → `../scripts/project_docs.py`
- documentation semantics → `../references/documentation-model.md`

The original full v1 behavior remains available on `baseline/orchestrator-v1` and in Git history.
