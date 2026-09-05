# Legacy v1 Role Mapping

> **LEGACY / MIGRATION REFERENCE ONLY**
>
> This file is **not runtime routing authority** for Project Orchestrator v2. The former fixed role-to-primary-skill model has been retired.

## v2 routing rule

Roles remain useful descriptive metadata, but **capabilities drive task matching**. A specialist may expose multiple roles and capabilities, and no specialist is permanently designated the primary executor for a role.

Current v2 sources are:

- capability/executor semantics → `references/capabilities-executors.md`
- discovery, provenance, trust and registry behavior → `references/discovery-registry.md`
- descriptive role/bootstrap catalog → `catalog/roles.json`
- normalized capability taxonomy/aliases → `catalog/capabilities.json`
- known-specialist bootstrap hints → `catalog/known-specialists.json`
- scanner/registry implementation → `scripts/scan_skills.py` and `scripts/build_registry.py`
- task-time matching/authority → `scripts/orchestration_engine.py`

Static catalog entries are hints only. Declared metadata outranks inference; capability never grants authority; health/trust/environment compatibility and project policy are evaluated before assignment.

## Historical source

The full v1 keyword rules, role tables, `Primary` mappings and gap handling remain available in Git history and on `baseline/orchestrator-v1`.

Do not restore `Primary` skill routing for v2 projects.
