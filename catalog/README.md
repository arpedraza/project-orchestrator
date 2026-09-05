# Project Orchestrator v2 — Catalog

> **Status:** Structural placeholder approved by CHG-001. Existing `role-mapping.md` remains the active v1 routing source.

## Purpose

This directory will hold bootstrap/reference metadata used by the v2 capability registry. Catalog data is never runtime truth by itself.

## Planned separation

Future catalog content is expected to distinguish:

- **roles** — broad descriptive organizational functions;
- **capability taxonomy** — stable normalized capability identifiers and aliases;
- **known specialist mappings** — bootstrap hints about commonly known skills/specialists and likely capabilities.

## Rules

- Roles remain descriptive; capabilities drive task matching.
- Static known-specialist entries are hints and must be validated against the current installation/runtime.
- Capability declarations/inference retain provenance and confidence where applicable.
- Catalog metadata cannot grant authority, production permission, trust, or task eligibility.
- A missing catalog entry never prevents dynamic discovery/classification of a newly installed specialist.

Migration of the useful role definitions and known-skill knowledge from `../role-mapping.md` is deferred to CHG-002.
