# Project Orchestrator v2 — Discovery, Capability Registry & Specialist Installation

> **Status:** Approved target design — not active runtime behavior.
> **Current runtime authority:** Existing `scan-skills.sh`, `role-mapping.md`, and v1 primary-role routing remain active until the scanner/registry migration is completed.

## Design provenance

Implements **Detailed Design 8 — Discovery, Scanner, Capability Registry & Specialist Installation Protocol**.

**Runtime activation:** Planned for CHG-002 / the scanner and capability-registry migration.

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

The local scanner should eventually:

- enumerate candidate local skill packages deterministically;
- report declared metadata and package/manifest paths;
- validate basic manifest/package structure;
- expose machine-readable output plus a human-readable view;
- use consistent package-boundary/counting rules;
- return clear failures for missing/invalid roots.

The scanner should not decide best executor, production permission, trustworthiness, final capability profile, or task assignment.

A shell compatibility entry point may remain while richer parsing/validation moves behind it.

## Manifest evolution

Future manifests should support explicit metadata such as:

- name/description;
- roles;
- capabilities;
- runtime requirements;
- supported platforms/environments;
- side-effect profile;
- provenance/publisher/trust hints.

Existing manifests remain backward-compatible through inference.

## Declared vs inferred metadata

Explicit declared metadata takes precedence. Inferred roles/capabilities preserve source/provenance and may carry confidence.

Capability inference may inspect name, description, declared roles, skill instructions/content, required tools, actions, inputs/outputs, runtime prerequisites, and side effects rather than relying only on keyword matching.

Low-confidence inference may be insufficient for critical work/gates according to policy.

## Validation and health

After classification, validation checks as relevant:

- manifest structural validity;
- runtime/tool availability;
- connection/authentication availability;
- platform/environment compatibility;
- required permissions;
- data/policy restrictions;
- obvious metadata/instruction conflicts.

Capability definition and current health remain separate. Conceptual health states:

```text
AVAILABLE
DEGRADED
UNAVAILABLE
QUARANTINED
```

A specialist may retain a capability definition/history while currently unavailable.

Health checking is proportional: static validation, runtime prerequisites, lightweight checks, execution history, and task-time validation are used as appropriate rather than blindly executing every specialist at startup.

## Registry refresh

Refresh occurs at project startup and after material inventory/runtime events such as specialist install/remove/update, connection changes, capability-gap detection, quarantine/recovery, or before high-impact work when freshness matters.

The registry is dynamic but does not require a full rescan before every small task.

## Static catalogs

Known-skill catalogs become bootstrap metadata, compatibility hints, and capability-mapping hints. They are never runtime truth.

Current installation, manifest, trust, health, compatibility, and project policy determine actual eligibility.

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

## Gap-resolution order

Before installing something new, evaluate:

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

## Trust and installation

Conceptual trust classes may distinguish built-in/system, organization-approved, trusted catalog, user-approved, unverified, and quarantined sources.

Trust affects auto-install eligibility, allowed action classes, required review/sandboxing, and production eligibility. Trust does not guarantee technical quality.

Discovery/evaluation may be autonomous. Installation is autonomous only when explicit project/trust policy permits it; otherwise it requires the appropriate approval/review.

Installation is a governed operation and remains distinct from validation, registration, task eligibility, assignment, and execution.

## Least privilege and updates

A newly installed specialist receives only task-required authority. Installation never grants blanket project privileges.

Material updates that change capabilities, permissions, runtime requirements, behavior, or trust/provenance are re-evaluated proportionally.

Post-install validation must confirm manifest visibility, runtime prerequisites, parsed capabilities, trust record, health, and refreshed registry state before the specialist is eligible.

## Identity, aliases, conflicts

Specialists need stable identities including source/package/repository and version/revision information, separate from display names.

Capabilities need stable normalized identifiers. Alias/taxonomy mapping may normalize different declared terms.

Metadata/instruction conflicts are validation findings. The analyzer must not blindly trust frontmatter.

## Instruction isolation

Specialist-local instructions define how delegated specialist work is performed inside the project task/authority envelope. They cannot silently redefine project scope, policy, gates, production authority, or project-control semantics.

Specialists may propose follow-up work, risks, assumptions, dependencies, or decisions through the result contract. The orchestrator processes those proposals into canonical state.

## Quarantine

A specialist may be quarantined for unexpected permissions/side effects, manifest/instruction conflicts, package tampering, security review failure, repeated unsafe behavior, or revoked provenance trust.

Quarantine removes new-task eligibility while preserving historical capability/execution records. Re-entry requires remediation/update/review and revalidation according to policy.

## Execution history

Successful/failed assignments, failure categories, duration where useful, and recent health may influence candidate ranking. Execution history is advisory and never overrides capability, trust, authority, compatibility, or separation-of-duties requirements.

## Human/manual paths

A user may install a specialist manually or choose to execute a capability themselves. Manual installation still enters the same discovery/validation/registry path. Human execution uses the same work contract and gates.

## Invariants

1. Discovery identifies candidates; it does not decide assignment.
2. Discovered/classified/validated/registered/eligible are distinct states.
3. The registry accepts multiple discovery providers.
4. `scan-skills.sh` is a local inventory provider and should expose machine-readable output.
5. Enumeration/count/package-boundary behavior is deterministic.
6. Declared metadata wins; inferred metadata retains provenance/confidence.
7. Declared capability does not imply current usability.
8. Capability definition and executor health are separate.
9. Registry refresh is startup/event driven.
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
