# Project Orchestrator v2 — Project Profiles

> **Status:** Structural placeholder approved by CHG-001. No behavioral profile is active yet.

## Purpose

Profiles will provide reusable defaults for project-control strictness without hard-coding one methodology or environment topology into the core orchestrator.

Potential future profiles include examples such as:

- lightweight/internal tool;
- standard production service;
- regulated enterprise;
- AI-enabled product;
- high-availability/critical system.

A profile may eventually supply defaults for environment topology, gates, security checkpoints, cost thresholds, observability requirements, separation of duties, release controls, production approval, documentation rigor, and traceability requirements.

## Governing rule

Profiles provide **defaults**. Explicit project policy remains authoritative and may tighten or adapt profile defaults within applicable organization/runtime constraints.

CHG-001 deliberately creates no behavioral profile to avoid changing v1 runtime or prematurely locking policy constants.
