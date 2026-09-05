# Project Orchestrator v2 — Executor Continuity

> **Status:** Active continuity model introduced by CHG-009.

## Purpose

Project Orchestrator must remain resumable when the executor changes: ChatGPT chat, ChatGPT Project chat, Codex session, human operator, automation, or another approved agent.

The governing principle is:

> Project state is more important than conversation state.

Continuity therefore records enough runtime context to resume safely without making chat memory or hidden agent state authoritative.

## Authority layers

Continuity does **not** create a second project record.

```text
docs/**                         canonical durable project truth
.orchestrator/state/**          deterministic runtime projection/cache
.orchestrator/runs/**           executor/session history
.orchestrator/checkpoints/**    portable resume snapshots
.orchestrator/handoffs/**       work-specific executor context
```

Material facts discovered during a run must be promoted into canonical Markdown when they become project truth. Run logs and checkpoints may reference those records; they do not replace them.

## Execution run

A run is one bounded period of work by one executor. It records:

- project identity;
- executor identity/type;
- objective and related work items;
- applicable authority references;
- declared mutation boundary (`modify`, `new`, `delete`, `protected`);
- starting state digest and optional Git read-only snapshot;
- events during execution;
- terminal result classification;
- affected files, raw outputs, evidence/issue/decision references;
- ending state digest.

The mutation boundary describes intended scope. It does **not** itself grant authority. Project policy decides whether execution may proceed autonomously or requires approval.

## Run classifications

Execution-stage classification is separate from root-cause classification.

Supported terminal classifications:

- `PASS`
- `FAIL_PRE_EXECUTION`
- `FAIL_PRE_WRITE`
- `FAIL_POST_WRITE`
- `FAIL_ROLLBACK_PASS`
- `RECOVERED_VALIDATED`
- `CANCELLED`

Examples:

```text
Cause: ENVIRONMENT
Classification: FAIL_POST_WRITE
Rollback: not completed
```

```text
Cause: IMPLEMENTATION_DEFECT
Classification: FAIL_ROLLBACK_PASS
Authoritative state restored
```

The existing recovery/change-control model still owns root-cause handling. Continuity adds *where in the execution boundary the run ended*.

## Checkpoint

A checkpoint is a generated runtime snapshot designed for executor replacement or conversation/session change.

It includes:

- project identity/status/reporting stage;
- deterministic canonical-state digest;
- current executor/session objective;
- work grouped by state;
- current dispatch selection;
- capability gaps and authority/decision blocks;
- open decisions and RAID records;
- latest execution run;
- optional Git read-only snapshot;
- next recommended actions.

`latest.md` is optimized for humans and AI executors. `latest.json` is the machine-readable equivalent. Historical checkpoint files are retained beside them.

## Resume contract

A new executor should:

1. establish the selected project root;
2. read canonical project identity/state;
3. read `.orchestrator/checkpoints/latest.md` or `latest.json` when present;
4. verify the checkpoint `project_id` matches the current project;
5. compare the checkpoint state digest with current canonical state;
6. if state changed, re-sync/recalculate rather than treating the checkpoint as current truth;
7. continue eligible work inside policy;
8. escalate only material decisions outside delegated authority.

Project identity mismatch is a hard stop. State-digest mismatch is a **drift signal**, not necessarily an error: another executor may have legitimately advanced the project.

## Raw output versus evidence

Raw run output is runtime material. Evidence is an accepted project-control object.

```text
raw output / tool result
        ↓
evaluation / validation
        ↓
accepted evidence record (EVID-*)
```

A run may reference raw output paths and accepted evidence IDs separately. Do not promote every log into canonical evidence.

## Hashes and digests

SHA256 is used here for deterministic drift/integrity comparison. A matching hash does **not** prove that content is safe, trusted, or correct. Trust and authority remain separate policy concerns.

## ChatGPT Project usage

When Project Orchestrator is used in a ChatGPT Project:

- project instructions should bootstrap `SKILL.md` plus this continuity model;
- uploaded/project-source canonical files remain the source of durable facts available to that environment;
- project/chat memory is useful context but not correctness-critical state;
- before handing work to Codex/human/another chat, produce or refresh a checkpoint;
- when direct filesystem access is unavailable, emit the checkpoint content for the user/executor to persist rather than pretending it was written locally.

## Codex / terminal usage

A terminal-capable executor should prefer the deterministic helper:

```bash
python3 scripts/executor_continuity.py --root <project-root> checkpoint \
  --executor-id codex \
  --executor-type agent
```

Runs may be recorded with `run-start`, optional `run-event`, and `run-end` commands. These operations affect only `.orchestrator/runs/` and `.orchestrator/checkpoints/` unless material results are separately promoted to canonical Markdown.

## Invariants

1. Canonical project truth remains under `docs/`.
2. Runs/checkpoints are runtime history/context, never parallel canonical truth.
3. Project identity mismatch prevents resume.
4. State digest mismatch forces revalidation/recalculation, not blind continuation.
5. Mutation scope and authority are separate concepts.
6. Routine authorized work does not require a universal human approval gate.
7. Failed attempts remain in run history.
8. Root cause and execution-stage classification remain separate.
9. Raw output and accepted evidence remain separate.
10. Hashes support drift/integrity checks; they do not establish trust.
11. Checkpoints are refreshed at meaningful stopping points/context switches.
12. Material run outcomes are promoted into canonical records before being treated as project truth.
