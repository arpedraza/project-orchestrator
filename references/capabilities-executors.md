# Project Orchestrator v2 — Capabilities and Executors

> **Status:** Approved target design — not active runtime behavior.
> **Current runtime authority:** Existing v1 role mapping and primary-skill routing remain active until their migration batch is completed.

## Design provenance

Implements **Detailed Design 2 — Capability, Executor & Authority Model** and the executor-facing portions of Detailed Design 8.

**Runtime activation:** Planned for the scanner/capability-registry and later orchestration-loop migrations.

## Four separate concepts

```text
ROLE        broad professional/organizational function
CAPABILITY  what can actually be done
EXECUTOR    who/what will do the work
AUTHORITY   what that executor is allowed to do in context
```

Roles remain descriptive metadata. Capabilities are the delegation primitive. Executors perform work. Authority determines which actions are permitted.

## Capability-driven routing

Work items specify **required capabilities** and may specify **preferred capabilities**. Required capabilities must be satisfied. Preferred capabilities influence ranking but should not create unnecessary blockers.

Capability records use stable normalized identifiers independent from natural-language labels. Alias/taxonomy mapping may normalize equivalent declarations from different specialists.

A capability may be explicitly declared or inferred. Its provenance is retained. Inferred capabilities may carry confidence such as high/medium/low, and policy may reject low-confidence inference for high-impact work or gates.

## Executor classes

Primary executor classes are:

- human;
- AI/agent;
- automation;
- external system/service.

A skill is normally a capability package made available through an executor/runtime. A skill and executor are not the same concept.

## Executor profile

An executor profile should support, conceptually:

- stable executor identity and type;
- capability set;
- runtime/tool availability;
- authority profile;
- trust/provenance;
- current health/availability;
- project-specific execution history where useful.

## Assignment pipeline

```text
Work becomes eligible
      │
      ▼
Resolve required/preferred capabilities
      │
      ▼
Query current capability registry
      │
      ▼
Compatibility filter
      │
      ▼
Trust + authority filter
      │
      ▼
Availability/resource constraints
      │
      ▼
Rank eligible candidates
      │
      ▼
Assign executor
```

Compatibility may include platform, environment, runtime, tools, inputs, versions, data sensitivity, policy, and connectivity.

A strong capability match never overrides insufficient authority.

## Ranking

Eligible candidate ranking may consider capability coverage, specialization, trust, prior successful execution, availability, cost, expected duration, context continuity, and project preference.

No static `primary skill` is guaranteed assignment. Runtime task suitability controls selection.

Context continuity may be a preference, but it cannot override missing capability, independence requirements, security policy, or separation of duties.

## Separation of duties

Work items and gates may require executor independence. Examples include:

- implementation executor cannot independently approve a security/release gate;
- deployment preparation and production approval may require different identities;
- regulated projects may require independent verification.

## Human takeover

When a user or team member takes over a task, the executor assignment changes but the task contract does not. The human receives the same objective, dependencies, context, acceptance criteria, evidence requirements, and gates. On completion, normal gate and state evaluation resumes.

## Capability gaps and composition

A capability gap exists when no currently eligible executor can satisfy the task under capability, trust, authority, compatibility, availability, or independence constraints.

Resolution may use:

1. deeper inspection of existing specialists;
2. decomposition of the task;
3. composition of multiple specialists;
4. a human executor;
5. an approved external system/service;
6. discovery and policy-controlled installation of a new specialist.

Installation is not the universal first response.

## Execution contract

Every delegated task should provide:

- objective and relevant context;
- required capabilities;
- inputs and dependencies;
- constraints and policies;
- acceptance criteria;
- expected outputs;
- required evidence.

Every executor returns, as applicable:

- status/result;
- outputs;
- evidence;
- issues;
- assumptions;
- new risks;
- decisions needed;
- follow-up recommendations.

## Invariants

1. Roles never substitute for explicit required task capabilities when selecting executors.
2. Declared and inferred capabilities preserve provenance.
3. Capability does not imply authority.
4. Humans, agents, automation, and external systems use the same work/result contracts.
5. The most restrictive applicable authorization rule controls unless an authorized exception exists.
6. Installation and execution are separate decisions.
7. A newly discovered/installed specialist receives no automatic elevated privilege.
8. Executor selection is dynamic rather than permanently primary-skill based.
9. Capability gaps trigger recovery/decomposition/discovery before project-wide escalation.
10. Consequential escalations contain options, impacts, recommendation, and authority required.
11. Separation-of-duties constraints may prohibit the same executor from implementation and independent approval.
12. Health failures may temporarily remove an executor from eligible selection without deleting its capability definition/history.
