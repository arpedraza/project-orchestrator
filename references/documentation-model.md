# Project Orchestrator v2 — Documentation, Scriber & Knowledge-Base Architecture

> **Status:** Approved target design — not active runtime behavior.
> **Current runtime authority:** Existing v1 `.orchestrator/NN-phase-name.md` handoffs remain the active documentation mechanism until migration.

## Design provenance

Implements **Detailed Design 7 — Documentation, Scriber & Knowledge-Base Architecture**.

**Runtime activation:** Planned for the Documentation/Scriber migration after canonical records and project-control state exist.

## Three artifact classes

Every project artifact belongs explicitly to one class:

1. **Canonical record** — authoritative project knowledge/state.
2. **Generated view** — regenerable presentation/reporting derived from canonical state.
3. **Working state** — execution/runtime material, scratch analysis, handoffs, checkpoints, raw transient outputs.

Material project facts must never exist only in working state.

## Two-root project layout

Default project layout:

```text
project-root/
├── docs/             durable canonical knowledge + generated human views
└── .orchestrator/    execution/runtime workspace
```

A default `docs/` structure may organize durable knowledge by information domain, for example project control, requirements, architecture, decisions, delivery, quality/evidence, releases, operations, and reviews.

`.orchestrator/` may contain state/cache, registry, runs, handoffs, checkpoints, and temporary evidence/context.

The runtime workspace must never hold the only authoritative requirement, decision, accepted risk, release approval, or other material project fact.

## User/PM and executor views

Human project-control views and executor context packages are generated from the same canonical project state.

A Product Owner may receive milestone status, blockers, decisions, risks, and next actions. A task executor receives relevant requirements, ADRs, dependencies, environment, constraints, acceptance criteria, and evidence expectations.

These are different views, not different truths.

## Markdown-first portability

Canonical project records are portable Markdown with stable IDs, structured metadata (likely YAML frontmatter), and human-readable narrative.

The repository must remain usable from GitHub, VS Code, terminal tooling, Obsidian, and AI agents.

Obsidian is supported as an optional interface but is never a dependency. Canonical records should not require proprietary plugins or hidden Obsidian-only state.

## Filenames and history

Canonical filenames normally include the stable record ID, such as `REQ-014-centralized-authentication.md` or `ADR-007-authentication-strategy.md`.

Avoid filename version proliferation such as `final-v7-final2.md`. History comes from stable IDs, record lifecycle/supersession, baseline versions, repository history, and project event history.

## Common record structure

Canonical Markdown should support structured metadata for at least identity/type/title/status/ownership/time and relationship fields as appropriate, followed by human-readable Markdown.

Exact schema/property names are intentionally deferred.

## Project-control documentation

User/PM views should answer:

- what are we building and why;
- where are we now;
- what changed;
- what is done/next;
- what is blocked;
- what decisions are needed;
- are milestones/releases on track;
- what material risks/issues/exceptions exist.

These views derive from canonical project state.

## Scriber responsibilities

Project Control owns semantic truth, IDs, states, relationships, authority, and project-control meaning.

The Scriber/documentation capability owns presentation and hygiene, including:

- Markdown organization/formatting;
- summaries and stakeholder views;
- indexes/navigation;
- meeting minutes;
- cross-link maintenance;
- generated report updates;
- diagram documentation;
- documentation consistency/freshness checks.

A Scriber may automatically repair formatting/link defects. It may not silently resolve semantic contradictions or declare work/release/risk success. Semantic contradictions become attention/issues for Project Control.

## Generated views

Examples include project status, Gantt/timeline, Kanban/work status, RAID dashboard, traceability matrix, requirement coverage, ADR index, release dashboard, environment status, evidence coverage, and master `INDEX.md`.

Generated files must indicate they derive from canonical state and are not authoritative editable truth.

If a human edits a generated view intending to change the project, the intent must be converted into a canonical project update rather than leaving two conflicting sources.

## Handoffs

Handoffs become regenerable execution context packages containing task objective, relevant requirements/decisions/risks/issues, dependencies, inputs, policies, acceptance criteria, environment, expected outputs/evidence, and prior relevant results.

Deleting a handoff should not destroy project memory; it should be regenerable from canonical state.

Existing v1 handoff concepts map forward as follows:

- Context → generated task context;
- Decisions Made → ADR/DEC references;
- Open Questions → decision/risk/assumption/issue/work records where material;
- Inputs for Next Phase → dependency/task input context;
- Skills Used → executor/capability execution history.

## Runtime runs and evidence

Executor run records may store input snapshot, executor, timings, raw outputs, tool actions, warnings, and temporary files under `.orchestrator/`.

Material evidence is promoted to canonical `EVID-*` records with provenance and references to raw external/runtime evidence. Large logs/reports need not be duplicated into Markdown if provenance/retrieval is preserved.

## Diagrams

Prefer portable textual diagrams (for example Mermaid) where practical for architecture/workflow documentation. Use C4-style views as useful for architecture. UI/product design may remain authoritative in Figma or another appropriate specialist tool.

External authoritative diagrams/assets are explicitly referenced by Markdown records with purpose, scope, ownership, status/revision, and related records.

Markdown is the project knowledge/control layer; not every binary/visual artifact must physically live inside Markdown.

## Meetings/reviews

Meetings produce both human-readable minutes and canonical state changes. Decisions, actions, risks, assumptions, issues, and changes are extracted into their formal record types rather than buried only in meeting notes.

Meeting folders must not become a shadow backlog or decision register.

## Synchronization and freshness

Canonical state changes trigger documentation updates. Generated views may record generation time, project-state revision, and active baseline.

If canonical state changes while a generated view is not refreshed, the view is stale and should be regenerated automatically when possible.

Documentation is continuous, not a Phase-9 cleanup activity. Closure performs completeness/handover/archive review.

## Human edits and validation

Humans may edit canonical Markdown directly. Edits enter the same validation/state-update flow as agent-produced changes. The system validates duplicate IDs, missing references, invalid supersession chains, broken internal links, missing evidence references, and generated-view freshness.

Formatting/link problems may be auto-repaired. Semantic integrity problems are surfaced to Project Control.

## Archive/closure

The durable archive is the canonical knowledge base: approved brief/baselines, requirements, decisions/ADRs, RAID outcomes, acceptance/evidence, releases/deployments, operations/handover, indexes, and lessons learned.

Runtime material may be retained, summarized, archived separately, or cleaned according to policy; it is secondary.

## Invariants

1. Every artifact is canonical, generated, or working-state.
2. Durable project truth lives outside the runtime workspace.
3. `.orchestrator/` is execution/work context, not the sole project record.
4. Human/PM and executor views derive from the same canonical state.
5. Canonical records are portable Markdown with structured metadata/stable IDs.
6. Obsidian is compatible but never required.
7. Stable IDs/lifecycle/baselines/repository history replace filename-version proliferation.
8. Project Control owns semantics; Scriber owns presentation/hygiene.
9. Status/Gantt/indexes/RAID/traceability reports are derived views.
10. Handoffs are regenerable context packages, not primary project memory.
11. Material runtime evidence is promoted into canonical evidence records with provenance.
12. Portable textual diagrams are preferred where practical; external authoritative visual assets are explicitly governed/referenced.
13. Meeting minutes preserve context while decisions/actions/risks are promoted to canonical records.
14. Project-state changes drive continuous documentation updates.
15. IDs/links/references/view freshness are validated.
16. Human canonical edits use the same validation/state workflow.
17. Scratch analysis is not accepted project truth until promoted.
18. The durable archive is the canonical knowledge base; runtime artifacts are secondary.
