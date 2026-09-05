# Project Orchestrator v2 — Schemas

> **Status:** Structural placeholder approved by CHG-001. No runtime schema is active yet.

## Purpose

This directory will contain machine-validation schemas for Project Orchestrator v2 canonical/runtime objects.

CHG-001 intentionally does **not** select or implement the final serialization format. JSON Schema, YAML-backed validation, typed code models, or another implementation approach will be decided in the batch that introduces state validation.

## Planned schema domains

- Project State
- Work Item
- Dependency
- Gate
- Milestone
- Baseline / Forecast / Actual scheduling data
- Capability
- Executor
- Environment
- Requirement
- ADR / Decision
- RAID records
- Change
- Test / Evidence
- Release / Deployment
- Incident

## Constraints already approved

Future schemas must preserve the semantics in `../references/` including stable IDs, explicit relationships, executor neutrality, gate/evidence scope, authority separation, baseline history, configurable environments, and canonical-vs-derived state.

Exact property names, required/optional fields, serialization technology, and storage implementation remain deferred.

**Runtime activation:** Pending the Project State / validation implementation batch.
