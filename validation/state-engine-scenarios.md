# Project Orchestrator v2 — State Engine Validation Scenarios

> **Status:** CHG-003 executable validation contract.
> **Scope:** Project State, Work Item, Dependency, Gate, State Bundle and semantic validation only. Scheduling, dispatch, environments and production policy remain deferred.

## Scenario coverage

The CHG-003 test suite implements these approved behaviors:

| ID | Scenario | Expected result |
|---|---|---|
| S01 | Valid minimal project state | Valid |
| S02 | Duplicate stable IDs | Rejected |
| S03 | Missing local work/gate/dependency reference | Rejected |
| S04 | HARD dependency cycle | Rejected |
| S05 | SOFT dependency cycle | Does not fail hard-cycle validation |
| S06 | `READY` with `UNSATISFIED` HARD dependency | Rejected |
| S07 | `READY` with unsatisfied SOFT dependency | Allowed |
| S08 | `READY` with `AT_RISK` HARD dependency | Allowed; risk state is not automatically unsatisfied |
| S09 | `READY` with properly `WAIVED` HARD dependency | Allowed |
| S10 | `DONE` with pending required acceptance criterion | Rejected |
| S11 | `DONE` with failed required acceptance criterion | Rejected |
| S12 | `DONE` with missing required gate | Rejected |
| S13 | `DONE` with failed/non-current required gate | Rejected |
| S14 | `PASSED` gate without evidence | Rejected |
| S15 | `PASSED` gate without evaluated scope | Rejected |
| S16 | `PASSED` gate with unsatisfied required criterion | Rejected |
| S17 | `WAIVED` gate without decision reference | Rejected |
| S18 | `WAIVED` dependency without decision reference | Rejected |
| S19 | Valid waived gate remains `WAIVED` and may satisfy a required gate | Valid |
| S20 | Human/agent/automation/external executor assignments | Same Work Item contract; valid representation |
| S21 | Baseline / forecast / actual schedule fields | Remain separate and independently represented |
| S22 | Organization-specific Work Item type | Accepted; taxonomy remains extensible |
| S23 | Project-specific reporting stage | Accepted; reporting stage is not an execution enum |

Additional regression checks cover invalid schedule date-time shapes, a fully valid `DONE` item with a current passed gate, CLI exit codes/JSON findings, and schema-file JSON parsing.

## Finding contract

Semantic validation returns deterministic findings with:

- `severity`;
- stable `code`;
- human-readable `message`;
- object `path` where applicable.

Examples include `STATE-DEP-CYCLE-001`, `STATE-READY-001`, `STATE-DONE-AC-001`, and `STATE-GATE-PASS-003`.

## Boundary

The State Bundle is a machine/runtime projection used for deterministic validation. It does **not** replace the approved Markdown-first canonical project knowledge model. CHG-003 does not calculate a Ready Queue, dispatch work, compute critical path, manage resource capacity, promote environments, or make authority decisions.
