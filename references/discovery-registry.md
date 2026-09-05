# Project Orchestrator v2 — Discovery, Capability Registry & Specialist Installation

> **Status:** CHG-002 scanner/capability-registry subsystem implemented; task routing and broader v2 orchestration are not yet active.
> **Current runtime authority:** `scripts/scan-skills.sh` and the v2 catalog/registry interfaces are active for discovery/classification. Existing `SKILL.md` and v1 `role-mapping.md` compatibility routing remain authoritative for orchestration until their later migration.

## Design provenance

Implements **Detailed Design 8 — Discovery, Scanner, Capability Registry & Specialist Installation Protocol**.

**Runtime activation:** Scanner/registry portion activated by CHG-002. Task-time eligibility, autonomous installation, routing, and orchestration integration remain deferred.

## CHG-002 implementation boundary

CHG-002 implements deterministic local skill discovery, machine-readable inventory, normalized capability/role bootstrap catalogs, declared-versus-inferred provenance, static registry validation, health representation, trust non-inference, multi-provider inventory ingestion, schemas, regression tests, and CI.

It deliberately does **not** implement task assignment, executor ranking, policy authorization, GitHub/catalog candidate search, autonomous specialist installation, runtime credential probing, or production eligibility. Registry entries therefore retain `trust: UNKNOWN` and `eligibility: NOT_EVALUATED` unless a future approved subsystem supplies those decisions.

## Specialist lifecycle

The registry distinguishes these stages:

```text
DISCOVERED → INSPECTED → CLASSIFIED → VALIDATED → REGISTERED → task-time ELIGIBLE
```

Alternative conditions include `DEGRADED`, `INELIGIBLE`, `UNAVAILABLE`, and `QUARANTINED`.

Registration does not mean eligibility for every task.

## Registry scope

The capability registry accepts inventory from multiple discovery providers, for example:

- local installed skills;
- plugins/apps;
- agents;
- configured human/team executors;
- automations;
- external systems/services.

`scan-skills.sh` remains one local inventory provider, not the entire registry architecture.

## Scanner contract

The local scanner:

- enumerates candidate local skill packages deterministically;
- reports declared metadata and package/manifest paths;
- validates basic manifest/package structure;
- exposes machine-readable JSON plus a human-readable Markdown view;
- uses consistent direct-child package-boundary/counting rules;
- returns clear failures for missing/invalid roots.

The scanner does not decide best executor, production permission, trustworthiness, final capability eligibility, or task assignment.

The shell compatibility entry point remains while richer parsing/validation is performed by `scripts/scan_skills.py`.

## Manifest evolution

Future-compatible manifests may support explicit metadata such as:

- name/description;
- roles;
- capabilities;
- runtime requirements;
- supported platforms/environments;
- side-effect profile;
- provenance/publisher/trust hints.

Existing manifests remain backward-compatible through inference.

## Declared vs inferred metadata

Explicit declared metadata takes precedence. Inferred roles/capabilities preserve source/provenance and confidence.

CHG-002 inference inspects name, description, declared roles, instruction excerpts, known-specialist bootstrap hints, and deterministic role/capability keyword mappings. It remains intentionally transparent rather than using an opaque scoring model.

Low-confidence inference may be insufficient for critical work/gates according to future task-time policy.

## Validation and health

After classification, validation may check as relevant:

- manifest structural validity;
- provider-reported runtime/tool availability;
- platform/environment compatibility metadata;
- requested/runtime requirements;
- obvious metadata/instruction conflicts.

Capability definition and current health remain separate. Health states are:

```text
AVAILABLE
DEGRADED
UNAVAILABLE
QUARANTINED
```

A specialist may retain a capability definition/history while currently unavailable.

CHG-002 performs static validation. The local scanner reports runtime validation as `NOT_EVALUATED`; future providers or task-time checks may report actual runtime availability. This prevents static parsing success from being misrepresented as credential/service readiness.

## Registry refresh

The target model refreshes at project startup and after material inventory/runtime events such as specialist install/remove/update, connection changes, capability-gap detection, quarantine/recovery, or before high-impact work when freshness matters.

CHG-002 provides the discovery/building blocks but does not yet wire refresh scheduling into the main orchestrator loop.

## Static catalogs

Known-skill catalogs are bootstrap metadata, compatibility hints, and capability-mapping hints. They are never runtime truth.

The v1 known-skill catalog has been migrated to `catalog/known-specialists.json`; descriptive roles and capability taxonomy live in `catalog/roles.json` and `catalog/capabilities.json`.

Current installation, manifest, trust, health, compatibility, and project policy will determine actual eligibility once task-time routing is implemented.

## Capability-gap classification

A gap exists when no eligible executor can satisfy the task. Reasons may include:

- no specialist installed;
- installed specialist unavailable;
- insufficient capability confidence;
- authority missing;
- platform/runtime incompatibility;
- separation-of-duties constraint;
- trust policy exclusion;
- resource/availability constraint.

The gap retains the actual reason.

Capability-gap orchestration is not activated by CHG-002.

## Gap-resolution order

Before installing something new, the approved target model evaluates:

1. deeper inspection of existing specialists;
2. task decomposition;
3. composition of multiple specialists;
4. human executor;
5. approved external service/system;
6. candidate discovery and installation.

## Candidate discovery

Configured discovery sources may include organization/internal catalogs, approved skill/plugin catalogs, local repositories, GitHub, vendor marketplaces, package registries, or user-provided sources.

GitHub is a candidate source, not inherently a trusted marketplace.

Candidate evaluation considers capability coverage, provenance/publisher, license/policy compatibility, manifest validity, requested permissions, required tools/access, instruction/code footprint, runtime compatibility, maintenance/currentness where relevant, side effects, trust status, and project fit.

Candidate search/install is deferred beyond CHG-002.

## Trust and installation

Conceptual trust classes may distinguish built-in/system, organization-approved, trusted catalog, user-approved, unverified, and quarantined sources.

Trust affects auto-install eligibility, allowed action classes, required review/sandboxing, and production eligibility. Trust does not guarantee technical quality.

Discovery/evaluation may be autonomous. Installation is autonomous only when explicit project/trust policy permits it; otherwise it requires the appropriate approval/review.

Installation is a governed operation and remains distinct from validation, registration, task eligibility, assignment, and execution.

CHG-002 intentionally does not infer trust or perform installation.

## Least privilege and updates

A newly installed specialist receives only task-required authority. Installation never grants blanket project privileges.

Material updates that change capabilities, permissions, runtime requirements, behavior, or trust/provenance are re-evaluated proportionally.

Post-install validation must confirm manifest visibility, runtime prerequisites, parsed capabilities, trust record, health, and refreshed registry state before the specialist is eligible.

These installation/update workflows remain future approved work.

## Identity, aliases, conflicts

Specialists use stable provider-plus-package identities, separate from display names. The registry retains directory and declared names so mismatches remain visible.

Capabilities use normalized identifiers and alias/taxonomy mapping through `catalog/capabilities.json`.

Metadata/instruction conflicts are validation findings. The analyzer does not blindly trust frontmatter; CHG-002 includes the first static read-only-versus-write-instruction conflict check.

## Instruction isolation

Specialist-local instructions define how delegated specialist work is performed inside the project task/authority envelope. They cannot silently redefine project scope, policy, gates, production authority, or project-control semantics.

Specialists may propose follow-up work, risks, assumptions, dependencies, or decisions through the result contract. The orchestrator processes those proposals into canonical state in later batches.

## Quarantine

A specialist may be quarantined for unexpected permissions/side effects, manifest/instruction conflicts, package tampering, security review failure, repeated unsafe behavior, or revoked provenance trust.

Quarantine removes new-task eligibility while preserving historical capability/execution records. Re-entry requires remediation/update/review and revalidation according to policy.

The CHG-002 registry can represent provider-supplied quarantine state but does not independently make quarantine policy decisions.

## Execution history

Successful/failed assignments, failure categories, duration where useful, and recent health may influence candidate ranking. Execution history is advisory and never overrides capability, trust, authority, compatibility, or separation-of-duties requirements.

Execution-history ranking is deferred.

## Human/manual paths

A user may install a specialist manually or choose to execute a capability themselves. Manual installation still enters the same discovery/validation/registry path. Human execution uses the same work contract and gates.

Human/executor orchestration integration is deferred beyond CHG-002.

## Invariants

1. Discovery identifies candidates; it does not decide assignment.
2. Discovered/classified/validated/registered/eligible are distinct states.
3. The registry accepts multiple discovery providers.
4. `scan-skills.sh` is a local inventory provider and exposes machine-readable output.
5. Enumeration/count/package-boundary behavior is deterministic.
6. Declared metadata wins; inferred metadata retains provenance/confidence.
7. Declared capability does not imply current usability.
8. Capability definition and executor health are separate.
9. Registry refresh is startup/event driven in the target orchestration model.
10. Static catalogs are bootstrap hints, not authority.
11. Gaps attempt existing/decomposition/composition/human recovery before assuming installation.
12. Discovery does not imply trust.
13. Installation obeys project/trust policy and remains separate from execution.
14. New specialists receive least-required authority only.
15. Material specialist updates are re-evaluated.
16. Specialist/capability identities are stable and normalized.
17. Specialist instructions cannot override project-control policy.
18. Quarantine removes eligibility without erasing history.
19. Execution history may influence ranking but cannot override hard eligibility controls.
20. Manual installation/human execution follows the same validation/workflow model.
