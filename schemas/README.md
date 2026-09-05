# Project Orchestrator v2 Schemas

CHG-002 activates two machine-readable interface schemas:

- `scanner-inventory.schema.json` — raw local discovery/provider inventory contract.
- `capability-registry.schema.json` — normalized capability-registry contract.

The schemas document interfaces and are intentionally independent of third-party validation libraries. Automated tests validate the implemented contract directly with the Python standard library.

Future schemas remain deferred until their approved implementation batches:

- Project State
- Work Item
- Dependency
- Gate
- Executor/Authority
- Environment
- Requirement / ADR / Decision / RAID
- Test / Evidence
- Release / Deployment
