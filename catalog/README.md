# Project Orchestrator v2 Catalogs

> **Status:** CHG-002 active bootstrap data for the scanner/capability-registry subsystem.

The catalog is descriptive bootstrap knowledge, never runtime task-routing authority.

- `roles.json` preserves the v1 role definitions and keyword hints for compatibility/classification.
- `capabilities.json` defines normalized capability identifiers, aliases, role hints, and deterministic inference terms.
- `known-specialists.json` preserves the v1 known-skill catalog as bootstrap role/capability hints.

Declared specialist metadata takes precedence over catalog hints. Catalog-derived roles/capabilities are marked as inferred/bootstrap provenance in registry output. Task-time eligibility, trust, authority, health validation, and executor ranking remain outside CHG-002.
