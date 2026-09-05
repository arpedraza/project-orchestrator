# Project Orchestrator v2 — Failure, Recovery, Escalation & Change Control

> **Status:** Approved target design — not active runtime behavior.
> **Current runtime authority:** The existing v1 error-handling rules remain active until this subsystem is migrated.

## Design provenance

Implements **Detailed Design 5 — Failure, Recovery, Escalation & Change Control**.

**Runtime activation:** Planned for the recovery/change-control implementation after state, dependency, gate, and lifecycle foundations exist.

## Distinct project-control concepts

The orchestrator must distinguish:

- execution failure;
- work defect;
- blocker;
- risk;
- issue;
- incident;
- change;
- decision.

These concepts have different lifecycles and recovery behavior.

## Failure classification

A failure is classified before selecting recovery. Typical classes include:

- transient runtime/network/service failure → retry;
- implementation/result defect → rework;
- environment/infrastructure failure → infrastructure/operations work;
- missing capability → capability-gap workflow;
- invalid assumption/approach → replan;
- authority or consequential trade-off → escalation.

## Retry and rework

A retry repeats substantially the same action because the failure is believed transient. Rework changes/fixes the produced result while the underlying plan remains valid.

Automatic retry/rework is bounded by configurable recovery policy. Exhausting the recovery budget triggers a recovery review that may choose an alternate executor, decomposition, a different technical approach, replanning, parking, or escalation.

## Blocking

`BLOCKED` means required progress cannot currently continue. A blocker records its identity, cause, affected work/scope, owner/resolver, detected date, impact, next action, and expected resolution when known.

Blocking propagates only through affected dependency paths unless the blocker is explicitly scoped more broadly, such as workstream, release, environment, or project level.

Global/release blockers may include legal stop orders, catastrophic security compromise, invalid foundational architecture, production freezes, or an explicit Product Owner stop.

## Parking

Parking is a deliberate controlled choice to defer work while permitted surrounding work/release activity continues. Parked records retain reason, authority/policy basis, residual impact/risk, owner, target milestone/release where known, and a revisit trigger.

Revisit triggers may automatically return parked work to proposed/ready state.

## RAID behavior

Risks describe uncertain future harm. Issues describe problems that have occurred. A risk may realize into an issue while retaining historical linkage.

Assumptions are explicit and testable. Material assumptions identify validation method/trigger and impact if false. Invalidation creates impact analysis/replanning.

RAID records are active project-control mechanisms, not reporting-only tables.

## Incidents

Operational incidents use a dedicated flow: contain, diagnose, communicate as required, recover/rollback, validate recovery, and create corrective follow-up work. Severity/policy may freeze production promotions while allowing unaffected DEV/QA/planning work to continue.

The orchestrator coordinates incident specialists; it does not replace domain incident responders.

## Change classification

Minor operational changes inside approved scope/policy may be applied autonomously. Material changes require impact analysis before changing approved project baselines or governed records.

Material change examples include scope/requirement changes, architecture/provider/security-model changes, significant cost/schedule changes, production topology changes, and regulated/compliance impacts.

## Impact analysis

Material changes are evaluated against, as applicable:

- requirements and scope;
- architecture;
- work/dependencies;
- schedule/milestones;
- cost;
- security/compliance;
- infrastructure;
- AI;
- observability;
- quality/test scope;
- environments;
- RAID;
- documentation;
- releases/deployments.

Cross-cutting specialists are invoked by relevance/materiality.

## Replanning and baselines

Rework keeps the approved plan valid while fixing execution. Replanning changes the plan because assumptions, constraints, architecture, scope, or priorities no longer fit.

Baseline changes create new baseline versions rather than overwriting history. Each baseline revision records predecessor, reason, authority, effective date, and major changes.

## Escalation

Before escalation, specialists should attempt technical convergence where a clear technical resolution exists.

The orchestrator escalates when resolution exceeds approved authority, scope, risk tolerance, budget/schedule thresholds, or policy.

Escalation categories include authority approval, business decision, unresolved blocker, policy exception, priority/scope conflict, and critical incident.

A decision package includes:

- decision required and why now;
- relevant context/evidence;
- feasible options;
- impacts/trade-offs;
- specialist positions where relevant;
- recommended option;
- authority required;
- decision deadline/trigger;
- blocked scope;
- unaffected work that can continue.

## User roles

A user may simultaneously act as Product Owner/decision authority and as a task executor. These are distinct audit roles. Taking over a task does not put the entire project into manual mode.

Pauses, cancellations, and freezes are scoped to task/workstream/release/environment/project as appropriate. Cancellation/supersession preserves history rather than deleting material records.

## Risk acceptance and waiver

Mitigation and acceptance are distinct. Residual risk may be accepted only by authorized authority.

A waived gate remains `WAIVED`, not `PASSED`, and normally links to the relevant decision and risk/issue. Known exceptions remain visible in status/release summaries.

## Emergency path

Emergency workflows may use a shortened control path only when pre-authorized by policy. Emergency work remains auditable and may require mandatory post-change review.

Urgency does not erase governance.

## Communication levels

Project events may produce:

- information;
- attention;
- decision required;
- urgent action required.

Not every material event requires a Product Owner decision.

## Invariants

1. Failures are classified before recovery.
2. Retry, rework, alternate executor, replan, parking, and escalation are distinct paths.
3. Automatic recovery loops are policy-bounded.
4. Blockers propagate only through affected scopes unless explicitly broader.
5. Parked work retains reason/owner/revisit criteria.
6. RAID records are live canonical controls.
7. Material assumptions are explicit and validate/replan when false.
8. Operational incidents use dedicated recovery workflows.
9. Material changes require impact analysis before approved-baseline changes.
10. Baseline history is preserved through versions.
11. Escalations contain context, options, impacts, recommendation, and authority.
12. Unaffected work continues while localized blockers/decisions wait.
13. Escalation occurs only when resolution exceeds delegated authority/scope/thresholds/risk tolerance.
14. Risk mitigation and acceptance remain distinct; acceptance requires authority.
15. Waivers remain linked to risk/decision and never masquerade as passes.
16. Emergency paths require explicit policy and auditability.
17. Material state transitions preserve actor, reason, and history.
18. Information/attention/decision/urgent-action notifications are distinct.
