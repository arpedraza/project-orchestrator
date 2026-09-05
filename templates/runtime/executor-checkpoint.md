<!-- GENERATED: Project Orchestrator executor checkpoint; non-authoritative -->
# Project Orchestrator — Executor Checkpoint

> Runtime resume context only. Canonical project truth remains in `docs/`.

Checkpoint: `<CHK-ID>`  
Generated: `<timestamp>`  
Project: `<name>` (`<project-id>`)  
Canonical state digest: `<sha256>`

## Current executor/session

- Executor: `<type>:<id>`
- Objective: `<current objective>`
- Latest run: `<RUN-ID or None>`
- Latest run classification: `<classification or status>`

## Work state

- `READY`: `<ids>`
- `IN_PROGRESS`: `<ids>`
- `BLOCKED`: `<ids>`
- `NEEDS_DECISION`: `<ids>`

## Dispatch / control-plane snapshot

- Dispatch selected: `<ids>`
- Capability gaps: `<work ids>`
- Authority/decision work: `<work ids>`

## Project-control attention

- Open decisions: `<ids>`
- Open RAID: `<ids>`

## Git read-only snapshot

- Branch: `<branch if available>`
- HEAD: `<sha if available>`
- Working tree clean: `<true/false>`
- Unrelated changes: `<paths; do not touch unless in authorized scope>`

## Next actions

- `<next exact action>`

## Resume rule

Validate project identity and canonical state before acting. If the digest changed, re-sync/recalculate rather than trusting this checkpoint as current truth.
