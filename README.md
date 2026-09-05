# Project Orchestrator v2

Project Orchestrator is a Markdown-first, capability-driven project-delivery control plane for coordinating human, AI-agent, automation, and external-system executors through dependency-aware work, gates, evidence, recovery, environment promotion, and project control.

The repository contains the **skill source**. Projects being orchestrated may live somewhere else.

## Working MVP

The v2 MVP supports:

- local specialist discovery and normalized capability registry;
- canonical Markdown project records under `docs/`;
- machine state projection under `.orchestrator/state/`;
- Project / Work Item / Dependency / Gate validation;
- dependency-derived readiness and state-progression recommendations;
- capability/trust/authority-aware assignment planning;
- capacity, executor, and exclusive-resource-aware dispatch planning;
- simple critical-path/forecast support with graceful degradation;
- configurable environments and promotion validation;
- baseline/event/gate/operational cross-cutting triggers;
- bounded failure recovery and structured escalation packages;
- live Requirements / Decisions / RAID / Changes / Evidence / Release / Deployment traceability;
- generated project index/status and regenerable executor handoffs;
- human-default production approval under the conservative default policy.

The control plane **plans and coordinates**. Domain implementation and provider-specific mechanics remain delegated to specialists/executors.

## Installation / paths

Keep the skill installation path separate from the project being orchestrated:

```bash
export ORCHESTRATOR_HOME=/absolute/path/to/project-orchestrator
export PROJECT_ROOT=/absolute/path/to/the-project
export SKILLS_ROOT=/absolute/path/to/installed-skills
```

`ORCHESTRATOR_HOME` is this repository/installed skill package. `PROJECT_ROOT` is the project whose canonical records and runtime state are being managed.

No third-party Python runtime packages are required by the MVP utilities.

## 1. Initialize a project workspace

```bash
python3 "$ORCHESTRATOR_HOME/scripts/project_docs.py" \
  --root "$PROJECT_ROOT" init \
  --project-id PRJ-001 \
  --name "My Project" \
  --objective "Deliver the approved project outcome"
```

This creates the default Markdown-first layout:

```text
PROJECT_ROOT/
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
│   └── INDEX.md                 # generated when rendered
└── .orchestrator/
    ├── state/
    ├── registry/
    ├── runs/
    ├── handoffs/
    ├── checkpoints/
    ├── cache/
    └── temporary/
```

Canonical durable truth lives in Markdown records under `docs/`. `.orchestrator/` is runtime state/context and must not contain the only authoritative copy of material project facts.

## 2. Discover local skills and build a capability registry

```bash
bash "$ORCHESTRATOR_HOME/scripts/scan-skills.sh" \
  "$SKILLS_ROOT" --format json \
  > "$PROJECT_ROOT/.orchestrator/registry/local-inventory.json"

python3 "$ORCHESTRATOR_HOME/scripts/build_registry.py" \
  --inventory "$PROJECT_ROOT/.orchestrator/registry/local-inventory.json" \
  --catalog-dir "$ORCHESTRATOR_HOME/catalog" \
  --format json \
  > "$PROJECT_ROOT/.orchestrator/registry/capability-registry.json"
```

Declared metadata outranks inference. The registry records capability provenance, current health, trust state, and validation status. Discovery does not itself grant execution authority.

## 3. Add canonical work/project-control records

Use `templates/canonical/record.md` as a portable example. A canonical record is ordinary Markdown with structured frontmatter and a human-readable narrative.

Typical record types include:

```text
project, requirement, decision, raid, change,
work, dependency, gate, environment, promotion,
evidence, release, deployment, trace_link
```

Work can be performed by a human, agent, automation, or external executor without changing the acceptance/evidence/gate contract.

## 4. Sync and validate

```bash
python3 "$ORCHESTRATOR_HOME/scripts/project_docs.py" \
  --root "$PROJECT_ROOT" sync
```

This compiles canonical Markdown into `.orchestrator/state/state.json` and validates the Project/Work/Dependency/Gate model, lifecycle/environment rules, and project-control/traceability rules.

Do not dispatch from an invalid state.

## 5. Run one orchestration iteration

```bash
python3 "$ORCHESTRATOR_HOME/scripts/orchestrate_project.py" \
  --root "$PROJECT_ROOT"
```

The result is written to:

```text
PROJECT_ROOT/.orchestrator/state/orchestration.json
```

Key fields include:

- `state_recommendations` — safe derived changes such as dependency satisfaction and `PROPOSED → READY/BLOCKED/NEEDS_DECISION`;
- `assignments` — capability/policy-compatible executor recommendations;
- `dispatch.selected` — conflict-free work that may be delegated now;
- `capability_gaps` — unresolved capability coverage;
- `authority_blocks` / `decisions` — actions outside current authority;
- `critical_path` — calculated only when schedule inputs are sufficient.

The file is a planning snapshot. Project Control applies accepted recommendations back to the canonical Markdown records and records executor results/evidence there.

## 6. Generate executor context

```bash
python3 "$ORCHESTRATOR_HOME/scripts/project_docs.py" \
  --root "$PROJECT_ROOT" handoff TASK-001
```

Generated handoffs live under `.orchestrator/handoffs/`. They can be deleted and regenerated; they are not canonical project memory.

## 7. Refresh human/project-control views

```bash
python3 "$ORCHESTRATOR_HOME/scripts/project_docs.py" --root "$PROJECT_ROOT" render
python3 "$ORCHESTRATOR_HOME/scripts/project_docs.py" --root "$PROJECT_ROOT" validate-docs
```

Generated views include `docs/INDEX.md` and `docs/00-project-control/status.md`.

## Control-loop pattern

```text
edit canonical Markdown
→ sync/validate
→ refresh registry when needed
→ orchestrate one iteration
→ apply safe state recommendations
→ generate handoff(s)
→ execute delegated work
→ record result/evidence/RAID/decisions
→ re-sync/recalculate
→ render status
→ repeat
```

The `SKILL.md` conductor performs this logic autonomously within project policy. It should escalate only consequential decisions or unresolved blockers outside delegated authority.

## Production and high-impact work

The included `profiles/default-policy.json` is intentionally conservative:

- unknown-trust specialists are limited to low-impact local/reversible work;
- production/high-impact work requires an approval reference;
- production approval is human by default.

A project can define a stricter or explicitly delegated policy, but technical gate success never silently creates production authority.

## Testing

Run the cumulative suite from the skill source checkout:

```bash
cd "$ORCHESTRATOR_HOME"
python3 -m unittest discover -s tests -v
```

GitHub Actions runs the same cumulative suite on pushes and pull requests.

The MVP end-to-end tests cover:

1. canonical Markdown project → local skills → registry → build task dispatch;
2. accepted build result → hard dependency becomes satisfied → dependent review becomes READY and dispatchable;
3. generated review handoff and project status views;
4. missing capability → BLOCKED recommendation rather than silent continuation;
5. production work without approval → NEEDS_DECISION and no dispatch.

## Windows PowerShell local harness

`orchestrator.ps1` provides a Windows-first façade over the same tested Python engine. It installs no PowerShell modules, Node packages, Docker images, or other tooling.

The current engine **does require an existing Python 3.10+ runtime**. The harness will detect `py -3`, `python`, or `python3` and will fail clearly if none is already available; it does not install Python automatically.

Start with:

```powershell
.\orchestrator.ps1 doctor
.\orchestrator.ps1 smoke-test
```

`smoke-test` runs entirely in a unique temporary directory. It performs no Git, cloud, pipeline, or real-project writes.

Common commands:

```powershell
.\orchestrator.ps1 init -ProjectRoot C:\Projects\MyPilot -ProjectId PRJ-001 -Name "My Pilot" -Objective "Validate Orchestrator"
.\orchestrator.ps1 scan -ProjectRoot C:\Projects\MyPilot -SkillsRoot C:\Path\To\Skills
.\orchestrator.ps1 sync -ProjectRoot C:\Projects\MyPilot
.\orchestrator.ps1 plan -ProjectRoot C:\Projects\MyPilot
.\orchestrator.ps1 status -ProjectRoot C:\Projects\MyPilot
.\orchestrator.ps1 checkpoint -ProjectRoot C:\Projects\MyPilot -ExecutorId chatgpt -ExecutorType agent
.\orchestrator.ps1 resume -ProjectRoot C:\Projects\MyPilot
```

The wrapper also exposes `run-start`, `run-event`, and `run-end` for executor/session history and mutation-boundary tracking.

## Executor continuity across ChatGPT, Codex, humans, and automation

Project state is more important than conversation state.

CHG-009 continuity artifacts live only under the runtime workspace:

```text
.orchestrator/runs/<RUN-ID>/run.json
.orchestrator/checkpoints/<CHK-ID>.json
.orchestrator/checkpoints/<CHK-ID>.md
.orchestrator/checkpoints/latest.json
.orchestrator/checkpoints/latest.md
```

Run records capture executor identity, objective, mutation/protected scope, events, execution-stage result classification, raw outputs, evidence/issue/decision references, and state digests. Checkpoints provide a compact resume snapshot for the next executor.

They are **not** a parallel project record. Material decisions, requirements, accepted risks, completed work, and evidence remain canonical under `docs/`.

See `references/execution-continuity.md`.

## ChatGPT Project mode — Codex installation not required

Project Orchestrator can be tested as a governing operating model inside a ChatGPT Project without first installing it as a Codex skill.

Use:

- `chatgpt/PROJECT-INSTRUCTIONS.md` as the ChatGPT Project-specific bootstrap instructions;
- `chatgpt/README.md` for setup and cross-chat/Codex handoff guidance;
- `chatgpt/TEST-PROMPT.md` for a disposable first pilot.

In this mode, ChatGPT should use canonical project files/checkpoints as project state, not rely on hidden chat memory. If the environment does not actually expose a local repository or terminal, it must hand exact execution work to a human/Codex/other executor rather than pretending it executed it.

Codex is therefore one possible executor/integration, not a prerequisite for the Project Orchestrator control model.

## Source map

- `SKILL.md` — active v2 conductor/runtime instructions
- `orchestrator.ps1` — Windows-first local façade and smoke-test entry point
- `chatgpt/` — ChatGPT Project bootstrap/test material
- `references/` — detailed approved operating semantics
- `scripts/` — executable deterministic helpers/control plane
- `schemas/` — machine interface contracts
- `catalog/` — descriptive roles, capability taxonomy, known-specialist bootstrap hints
- `profiles/` — configurable default policy/trigger profiles
- `templates/` — v2 canonical/runtime templates
- `validation/` — scenario/acceptance manifests
- `tests/` — cumulative regression and end-to-end tests

`phases.md`, `role-mapping.md`, and `handoff-templates/` are legacy v1 migration/compatibility material only. The full original v1 source is permanently preserved on `baseline/orchestrator-v1`.

## MVP boundaries / post-MVP opportunities

The working MVP intentionally does not attempt to be an enterprise PM suite. Future batches can add, under separate approval:

- automated application of safe state recommendations to canonical records;
- richer policy/authority engine and separation-of-duties profiles;
- dynamic plugin/GitHub marketplace candidate discovery and installation workflows;
- richer schedule calendars/resource optimization and generated Gantt views;
- first-class ADR/test/incident schemas and richer traceability matrices;
- additional provider inventory adapters;
- packaging/install automation and release versioning.

The core v2 architecture is provider-neutral and does not require Obsidian or a particular cloud platform.
