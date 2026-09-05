# Project Orchestrator v2 — Validation Rules & System Invariants

> **Status:** Approved target design — not active runtime behavior.
> **Current runtime authority:** These invariants are specifications only until corresponding validators/runtime subsystems are implemented.

## Design provenance

Consolidates the approved invariants and architecture acceptance criteria from **Detailed Designs 1–9**.

**Runtime activation:** Incremental. Individual rules become enforceable as their owning subsystems are implemented.

## Project/work/state invariants

1. High-level stages are reporting/milestone constructs, not the runtime execution controller.
2. A work item cannot enter `READY` while a hard blocking dependency/start condition is unsatisfied.
3. `READY` means eligible; dispatch remains capacity/policy constrained.
4. A work item cannot become `DONE` until required acceptance criteria and mandatory gates are satisfied.
5. Routine schedule changes update forecast, not approved baseline.
6. Consequential state changes preserve actor/source, reason, and history.
7. Human, agent, automation, and external executors follow the same task acceptance/evidence contract.

## Dependency/scheduling invariants

8. Hard dependency graphs must be cycle-free.
9. Dependency relationships and schedule relationships are explicit; default scheduling relation is hard Finish-to-Start with zero lag when not otherwise specified.
10. Parallel execution requires dependency independence and absence of incompatible resource conflicts.
11. Dispatch respects executor/resource capacity, project policy, and environment constraints.
12. Gantt, critical path, sprint plan, Kanban, and status views are derived from canonical state and are never independent truth.
13. Critical-path calculations are used only when available schedule inputs justify them; false precision must not be invented.
14. Material forecast/milestone variance triggers project-control evaluation according to configured thresholds.

## Gate/evidence invariants

15. A blocking gate controls only its governed transition/dependency scope unless explicitly broader.
16. Gate results identify evaluated scope/version/artifact/environment/configuration and reference supporting evidence.
17. `WAIVED` is not `PASSED`; waiver requires authorized decision/evidence and preserves the exception.
18. Material relevant changes invalidate affected gate evidence/results; unrelated gates remain valid.
19. Evidence is historically preserved and scoped to the actual tested artifact/environment/version.
20. Release/deployment success cannot be asserted solely from unsupported status text.

## Capability/executor invariants

21. Roles are descriptive; required capabilities drive task matching.
22. Declared/inferred capabilities preserve provenance; inferred metadata may carry confidence.
23. Capability never implies authority.
24. Executor selection is dynamic; no static `primary skill` is guaranteed assignment.
25. Compatibility, trust, authority, availability, and independence constraints are applied before ranking.
26. Separation-of-duties rules may prohibit implementer self-approval.
27. Human takeover is executor reassignment, not a separate project workflow.
28. Execution history may influence ranking but cannot override hard eligibility controls.

## Discovery/registry invariants

29. Discovery identifies candidates; assignment happens later.
30. Discovered, classified, validated, registered, and task-eligible are distinct states.
31. The capability registry may use multiple discovery providers; local scanner output is only one source.
32. Discovery enumeration/count/package-boundary semantics are deterministic and consistent.
33. Explicit declared metadata wins over inference while provenance is retained.
34. Declared capability does not guarantee current runtime usability.
35. Capability definition and health (`AVAILABLE`/`DEGRADED`/`UNAVAILABLE`/`QUARANTINED`) remain separate.
36. Static known-skill catalogs are bootstrap hints, not runtime truth.
37. Capability gaps attempt existing-specialist analysis, decomposition/composition, human/external options, and policy-controlled discovery before project-wide escalation.
38. Candidate discovery does not imply trust.
39. Installation, validation, registration, assignment, and execution are separate transitions.
40. Newly installed specialists receive least-required authority only.
41. Specialist-local instructions operate inside the delegated project authority/policy envelope and cannot override it.
42. Quarantine removes new-task eligibility without erasing historical records.

## Lifecycle/environment/cross-cutting invariants

43. Project stage, work state, and environment state are separate dimensions.
44. Multiple releases/workstreams may occupy different stages simultaneously.
45. Environment topology is configurable and may be a graph.
46. Promotion is controlled auditable work and requires target-environment readiness.
47. Artifact identity is preserved through promotion unless material change creates a new artifact requiring revalidation.
48. Provider-specific deployment mechanics belong to specialists rather than the generic core.
49. Security, Infrastructure, Cost, AI, and Observability use baseline/event/gate/operational participation as relevant.
50. Cross-cutting invocation is impact/materiality based rather than unconditional.
51. Material cross-disciplinary changes require convergence.
52. Required release gates come from project policy/risk rather than hard-coded universal rules.
53. Environment policy may restrict data classification/access.
54. Hotfix/emergency promotion paths require explicit policy.
55. Operational evidence may create work, risks, issues, incidents, or decisions.
56. Delivery completion and project closure are distinct.

## Failure/recovery/change invariants

57. Failures are classified before selecting recovery.
58. Retry, rework, alternate executor, replan, parking, blocking, and escalation are distinct paths.
59. Automatic retry/rework loops are policy-bounded.
60. Blockers propagate only through affected scopes/dependency paths unless explicitly broader.
61. Parked work retains reason, owner, residual impact, and revisit criteria.
62. Risks, assumptions, issues, and dependencies are live canonical project controls.
63. Material assumptions identify validation conditions and trigger impact/replanning if invalidated.
64. Operational incidents use dedicated response/recovery workflows.
65. Material changes require impact analysis before approved-baseline modification.
66. Baseline history is preserved through explicit versions.
67. Unaffected work continues while localized blockers/decisions wait.
68. Risk mitigation and risk acceptance are separate; acceptance requires authorized authority.
69. Emergency workflows may shorten controls only through predefined auditable policy.
70. Information, attention, decision-required, and urgent-action notifications are distinct.

## Project-control/traceability invariants

71. Significant project-control records use stable IDs.
72. Requirement implementation, verification, and acceptance are separate states.
73. Significant architecture decisions use durable ADRs; business/project decisions use explicit decision records.
74. Accepted historical records are superseded rather than destructively rewritten.
75. Record accountability/ownership is independent from work executor assignment.
76. Requirements, decisions, work, tests, evidence, releases, and deployments form an explicit relationship graph.
77. Important links use defined relationship semantics rather than generic prose only.
78. Forward and backward traceability are supported.
79. Traceability may be transitive through hierarchy to avoid pointless duplicate links.
80. Release identity and deployment identity are distinct.
81. Material change records link decisions, affected records, and baseline impacts.
82. Canonical record references are validated.
83. Material historical records are lifecycle-retained rather than silently deleted.

## Documentation invariants

84. Every artifact is classified as canonical, generated view, or working state.
85. Durable project truth lives outside the runtime workspace.
86. `.orchestrator/` is execution/work context and must not contain the only authoritative copy of material project facts.
87. Human/PM and executor views derive from the same canonical state.
88. Canonical records are portable Markdown with stable IDs and structured metadata.
89. Obsidian compatibility must not become an Obsidian dependency.
90. Project Control owns semantic truth; Scriber/documentation capabilities own presentation, organization, and hygiene.
91. Handoffs are regenerable context packages rather than primary project memory.
92. Material runtime evidence is promoted into canonical evidence records with provenance.
93. Meeting/review notes preserve context while decisions/actions/risks/changes are promoted into canonical records.
94. Project-state changes drive continuous documentation/view updates.
95. Human edits to canonical Markdown use the same validation/state-update rules as agent edits.
96. Scratch analysis does not become accepted project truth without explicit promotion.

## Authority invariants

97. The most restrictive applicable authorization rule controls unless an authorized exception exists.
98. Human approval is the default for production unless project policy explicitly delegates automated promotion after gates.
99. Installation does not automatically grant activation or elevated privileges.
100. Separation-of-duties requirements override convenience/context continuity.
101. Waivers and residual-risk acceptance require appropriate authority and remain visible.
102. The orchestrator escalates only when resolution exceeds delegated authority, approved scope, thresholds, policy, or risk tolerance.
103. Escalations include context, feasible options, impacts, recommendation, required authority, blocked scope, and unaffected work.

## Architecture acceptance checks

The redesigned generic core is not complete if any of these remain true without project-specific configuration:

- a generic rule requires Azure/AWS/GCP rather than requesting provider-neutral capabilities;
- a generic rule says a numbered phase automatically invokes Security/Cost/Infrastructure/AI;
- a generic failure rule simply logs an error and continues regardless of dependency impact;
- task routing permanently assigns a `primary skill` instead of task-time matching;
- a Gantt/sprint/status document acts as an authoritative project database;
- production deployment can bypass applicable production authority policy;
- workflow semantics assume the executor must be an AI agent;
- a completed material requirement cannot be traced through decision/work/test/evidence/release/deployment history.

## CHG-001 validation boundary

For CHG-001 itself, validation is documentary/structural only. No v2 runtime rule above is expected to execute yet. The key checks are:

1. the v1 baseline is recoverable;
2. existing runtime files are unchanged;
3. approved v2 design areas have clear source ownership;
4. v1 and v2 authority status is unmistakable;
5. schema/catalog/profile implementation remains deferred;
6. acceptance/scanner regression manifests exist;
7. new documentation links/references are internally coherent.
