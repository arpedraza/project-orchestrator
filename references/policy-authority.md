# Project Orchestrator v2 — Policy & Authority Model

> **Status:** Approved target design — not active runtime behavior.
> **Current runtime authority:** Existing v1 behavior remains active until policy/authority support is implemented and referenced by the runtime orchestrator.

## Design provenance

Consolidates approved authority/policy decisions from **Detailed Designs 2, 4, 5, and 8**.

**Runtime activation:** Introduced incrementally with capability/executor, environment, recovery/change-control, and final orchestration-loop migrations.

## Principle

**Capability is not authority.** Knowing how to perform an action does not grant permission to perform it.

Authority is action-, scope-, environment-, data-, and project-context specific.

## Policy hierarchy

Conceptually, applicable constraints are evaluated from broadest safety/trust boundaries to project/task execution rules:

```text
External/runtime safety constraints
        ↓
Organization/trust policy
        ↓
Project authority policy
        ↓
Environment/release policy
        ↓
Gate/work-item policy
        ↓
Executor permissions
```

The most restrictive applicable rule controls unless an explicitly authorized exception/waiver exists.

## Action impact

The implementation may classify actions by impact. Exact labels are deferred, but the concept must distinguish at least:

- observation/read/analyze operations;
- project-local reversible changes;
- external but reversible changes;
- trust/security-boundary changes such as installing specialists or changing permissions;
- high-impact/production/destructive/irreversible actions.

Policy determines which classes are autonomous, conditional, or approval-gated.

## Default production policy

Human approval is the default for production promotion/deployment.

Projects may explicitly authorize automatic production promotion after required gates, but that authorization must be visible and policy-controlled. Production approval and production execution are separate responsibilities and may have different executors.

## Environment policy

Environments may define deployment authority, approval requirements, permissible data classifications/access, required gates, maintenance/change windows, and alternate promotion paths.

Non-production environments may permit autonomous deployment within policy while production remains human-gated.

## Specialist installation policy

Discovery/evaluation may proceed autonomously. Installation may proceed autonomously only when trust/project policy explicitly permits the candidate/action. Unknown or elevated-permission specialists may require security review and/or human approval.

Installation never implies activation or elevated privileges.

## Least privilege

Executors receive only the authority needed for the assigned work. A specialist installed for read-only review does not gain unrelated write/deploy permissions.

Authority is recalculated in task context and remains bounded by broader project/environment policy.

## Separation of duties

Policies may require different identities/executors for implementation, independent review, release approval, production execution, or risk acceptance.

Context continuity and convenience cannot override mandatory independence.

## Risk acceptance and waivers

Risk mitigation and residual-risk acceptance are different outcomes. Only authorized roles may accept risk above delegated tolerance.

Gate waiver is an explicit controlled outcome, not a technical pass. Waivers normally reference the governing decision and related risk/issue and preserve residual exposure.

## Change authority

Minor implementation/operational adjustments inside approved scope, architecture, acceptance, and thresholds may be autonomous.

Material changes affecting scope, requirements, architecture, provider, production topology, security model, budget, release commitments, or regulated obligations require impact analysis and the authority defined by project policy.

## Baseline authority

Forecast changes do not rewrite the approved baseline. Material rebaselining follows controlled change/replanning policy and preserves baseline history.

## Emergency authority

Emergency paths may shorten normal controls only when explicitly predefined by policy. They retain required evidence, authority, rollback/recovery controls, and post-change review where required.

Urgency does not create an undocumented bypass.

## Autonomy boundary

General decision rule:

```text
Can the action/problem be resolved within approved
scope + policy + risk tolerance + budget/schedule thresholds + delegated authority?
        │
      yes → continue autonomously
       no → structured escalation
```

Routine task assignment, expected QA failures, bounded retries/rework, specialist handoffs, documentation refresh, forecast recalculation, and low-impact implementation choices should not generate unnecessary Product Owner approval requests when already authorized.

## Escalation authority

Escalation is required for actions/choices such as:

- approval outside delegated authority;
- consequential scope/cost/time/risk trade-offs without a technically dominant authorized option;
- policy exceptions;
- unresolved blockers after feasible recovery is exhausted;
- residual-risk acceptance above tolerance;
- production approval when required;
- critical incidents when incident policy demands human involvement.

Escalations identify the exact authority required.

## User roles

The same person may act as Product Owner/decision authority and as work executor. Audit history distinguishes decision authority from task execution.

A user taking over one task does not suspend autonomous progress on unrelated work.

## Invariants

1. Capability never implies authority.
2. The most restrictive applicable authorization rule controls unless an authorized exception exists.
3. Production approval is human-default unless explicitly delegated by policy.
4. Installation, registration, task assignment, and execution are separate authorization points.
5. Least privilege applies to every executor type.
6. Separation-of-duties policy can override continuity/convenience preferences.
7. Risk acceptance and gate waiver require explicit authorized outcomes.
8. Forecast changes do not silently alter approved baselines.
9. Emergency paths remain policy-defined and auditable.
10. The orchestrator escalates only when resolution exceeds its approved authority/scope/thresholds/risk tolerance.
