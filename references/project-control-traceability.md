# Project Orchestrator v2 — Project Control & End-to-End Traceability

> **Status:** Approved target design — not active runtime behavior.
> **Current runtime authority:** Existing v1 briefs, handoffs, decisions sections, and risk tables remain active until canonical project-control records are introduced.

## Design provenance

Implements **Detailed Design 6 — Project Control, RAID, ADRs, Requirements & End-to-End Traceability**.

**Runtime activation:** Planned for the Project Control / RAID / ADR / Traceability implementation batch.

## Canonical record families

The v2 project-control model supports these primary record families as applicable:

```text
PROJECT
REQ        Requirements
ADR        Significant architecture/engineering decisions
DEC        Business/project/governance decisions
RISK       Risks
ASM        Assumptions
ISSUE      Issues
DEP        Significant dependencies / canonical dependency references
WORK       Initiative/Epic/Feature/Story/Task/Bug/Review/etc.
GATE       Transition controls
TEST       Defined verification methods
EVID       Evidence/results
CHANGE     Material changes
MILESTONE  Milestones
RELEASE    Release identity/scope
DEPLOYMENT Deployment instances
INCIDENT   Operational incidents
```

Project profiles determine which records are required; the model does not force maximum bureaucracy on every project.

## Stable IDs

Significant project-control records use stable unique IDs that survive title/status/document changes. IDs are used for links, relationships, traceability, handoffs, generated views, and audit history.

Material records are normally cancelled, rejected, superseded, deprecated, retired, or otherwise lifecycle-managed rather than silently deleted.

## Objectives, requirements, acceptance, tests, evidence

These concepts remain separate:

- **Objective** — intended outcome.
- **Requirement** — specific need/constraint the solution must satisfy.
- **Acceptance criterion** — measurable condition for completion.
- **Test** — defined verification method.
- **Evidence** — result showing what actually happened.

A requirement lifecycle may include `PROPOSED`, `ANALYZED`, `APPROVED`, `IMPLEMENTED`, `VERIFIED`, `ACCEPTED`, plus deferred/rejected/superseded/cancelled outcomes.

`IMPLEMENTED` is not `VERIFIED`; `VERIFIED` is not automatically business `ACCEPTED`.

Requirements may be functional, business, non-functional, security, compliance, operational, performance, availability, data, AI/ML, UX/accessibility, or constraint records.

## Decisions and ADRs

Significant durable technical/architectural decisions use ADRs. Project/business/governance choices use explicit decision records.

Accepted ADRs are not rewritten to erase historical decisions. A later ADR supersedes an earlier ADR and links the relationship.

Decision records preserve question/context, options, specialist assessments as relevant, selected decision, authority, date, consequences, and related records.

## RAID

RAID is canonical and active:

- **Risk** — uncertain possible event and impact, owner, likelihood/impact/exposure, trigger/proximity, response, actions, residual risk, status, evidence.
- **Assumption** — statement, owner, validation method/trigger, status, and impact if false.
- **Issue** — realized problem, impact, owner, corrective actions, severity, lifecycle.
- **Dependency** — project-significant dependency referencing the canonical dependency relationship where applicable.

The PM RAID view and the execution dependency graph should not become separate conflicting sources of truth.

## Traceability graph

Canonical records form an explicit relationship graph. Typical chain:

```text
Business need / Objective
          ↓
      Requirement
          ↓
  ADR / Decision
          ↓
      Work item
          ↓
 Implementation/artifact
          ↓
        Test
          ↓
       Evidence
          ↓
       Release
          ↓
     Deployment
          ↓
 Production validation
```

Forward and backward traceability are both required.

## Relationship semantics

Important links should use defined semantics rather than only generic "related to". Examples include:

```text
implements
verifies
evidences
depends_on
blocks
mitigates
caused_by
addresses
supersedes
derived_from
affects
introduced_by
released_in
deployed_as
accepted_by
waived_by
```

Exact serialization is deferred, but relationship meaning must remain explicit.

## Hierarchy and transitive traceability

Not every low-level task must duplicate a direct business-requirement link if traceability is unambiguous through parent/work relationships. The graph may traverse hierarchy.

Direct links are added where required for clarity, governance, testing, or release evidence.

## Gap/orphan detection

The system should be able to identify anomalies such as:

- approved requirement without implementing work;
- implemented requirement without verification;
- unjustified/orphan work with no approved parent/requirement/issue/change/decision;
- release scope missing required evidence;
- obsolete tests pointing only to superseded requirements;
- risks/issues without owners/actions as required;
- accepted ADRs without downstream implementation where expected.

Policy determines whether a gap is informational, attention-worthy, or gate-blocking.

## Tests and evidence

A test is a reusable verification definition; evidence is a scoped execution/result record.

Evidence identifies the tested artifact/version, environment/configuration/model version as relevant, result, time, executor/source, and provenance/reference to raw evidence.

Evidence history is preserved. A new test execution creates new evidence rather than silently rewriting earlier evidence for another build/version.

## Releases and deployments

Release and deployment identities are separate. One release may have multiple deployments across QA, staging, regions, or production instances.

A release records scope, artifacts, known issues, waivers, required gates, and lifecycle. A deployment records release/artifact/configuration, environment, executor, time/result, validation evidence, and rollback when applicable.

## Changes and baselines

Material change records link origin/reason, affected requirements/ADRs/work/risks/cost/schedule, impact analysis, authority decision, and baseline changes.

This allows project control to explain why schedule, scope, architecture, or release plans changed.

## Milestones and status

Milestones are canonical control objects whose forecast/status is derived from dependencies and gates where possible.

Project status, Gantt, RAID summaries, release views, traceability matrices, and coverage reports are generated management views over canonical records.

## Ownership

Record accountability and work execution are separate. A Product Owner may own a requirement while an agent implements it; a PM may own a risk while a security specialist executes mitigation work.

## Handoffs

Specialist handoffs are generated from the relevant traceability neighborhood: objective, requirements, decisions, risks/issues, dependencies, inputs, policies, acceptance criteria, environment, expected evidence, and related work.

Specialist outputs return through controlled project-state processing rather than silently redefining project truth.

## Invariants

1. Significant project-control objects have stable IDs.
2. Requirement implementation, verification, and acceptance are separate states.
3. Significant technical decisions use durable ADRs; business/project choices use decision records.
4. Accepted historical records are superseded rather than rewritten out of history.
5. RAID records are canonical live controls.
6. Record accountability is distinct from task executor assignment.
7. Requirements, decisions, work, tests, evidence, releases, and deployments form an explicit relationship graph.
8. Important relationships use defined semantics.
9. Forward and backward traceability are supported.
10. Traceability may be transitive through hierarchy without pointless duplicate links.
11. Evidence is scoped to the tested artifact/environment/version and historically preserved.
12. Release and deployment identities are distinct.
13. Material change records link decisions, affected records, and baseline impacts.
14. Status/Gantt/RAID/traceability views are derived, not independent truth.
15. Project Control owns record semantics/state; documentation specialists do not independently redefine them.
16. Handoffs are generated from relevant canonical context and feed controlled updates.
17. Canonical references are validated.
18. Material historical records are lifecycle-retained rather than silently deleted.
