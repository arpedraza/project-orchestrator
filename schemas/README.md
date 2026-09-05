# Project Orchestrator v2 Schemas

CHG-002 activates two machine-readable interface schemas:

- `scanner-inventory.schema.json` — raw local discovery/provider inventory contract.
- `capability-registry.schema.json` — normalized capability-registry contract.

CHG-003 activates five state-engine schemas:

- `project-state.schema.json` — Project State root metadata/reference contract.
- `work-item.schema.json` — executor-neutral Work Item, acceptance, traceability and schedule-field contract.
- `dependency.schema.json` — typed dependency, relationship, strength, lag, status and waiver contract.
- `gate.schema.json` — gate criteria, evaluated scope, validity, evidence and waiver contract.
- `state-bundle.schema.json` — aggregate machine/runtime projection used for deterministic cross-record validation.

The schemas document interfaces and are intentionally independent of third-party validation libraries. Automated tests validate the implemented semantic contract directly with the Python standard library.

The State Bundle is an execution projection/cache interface. It is **not** the durable canonical project knowledge base and does not replace the approved Markdown-first record model.

Future schemas remain deferred until their approved implementation batches:

- Executor/Authority policy details
- Environment / Promotion
- Requirement / ADR / Decision / RAID
- Test / Evidence canonical records
- Release / Deployment
