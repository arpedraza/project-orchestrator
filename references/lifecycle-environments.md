# Project Orchestrator v2 — Lifecycle, Environments & Cross-Cutting Disciplines

> **Status:** Approved target design — not active runtime behavior.
> **Current runtime authority:** Existing v1 phase sequencing and Azure-oriented deployment guidance remain active until migration.

## Design provenance

Implements **Detailed Design 4 — Lifecycle, Environments & Cross-Cutting Engineering Disciplines**.

**Runtime activation:** Planned for the lifecycle/environment migration after the scheduling foundation exists.

## Separate dimensions

Three concepts remain independent:

- **Project stage** — human reporting/milestone context.
- **Work state** — state of an individual work item.
- **Environment state** — readiness/runtime state of an environment or deployed artifact.

A project may simultaneously have one release operating in production, another validating in QA, and a future release in planning.

## Human-readable lifecycle

The default reporting lifecycle is conceptually:

```text
INITIATE → PLAN/ARCHITECT → PREPARE → BUILD → VALIDATE → RELEASE → OPERATE → IMPROVE/CLOSE
```

Stages support reporting and governance; they do not force all work to move in lockstep.

## Environment topology

Environments are first-class configurable objects arranged as a promotion graph rather than a hard-coded list.

Examples may include:

- DEV → PROD;
- DEV → QA → STAGING → PROD;
- DEV → INTEGRATION → QA → UAT → PREPROD → PROD;
- regional or parallel topologies;
- ephemeral PR/test environments.

Environment records should support identity, class/purpose, readiness state, promotion relationships, deployment authority, required gates, data restrictions, and capability requirements.

Conceptual environment states include `PROPOSED`, `PROVISIONING`, `READY`, `DEGRADED`, `UNAVAILABLE`, and `RETIRED`.

## Promotion

Promotion between environments is auditable work with:

- release/artifact identity;
- source and target environment;
- executor;
- configuration identity;
- required gates;
- deployment evidence;
- validation evidence;
- rollback path and result.

The preferred model preserves artifact identity across environments. A material rebuild/change creates a new artifact identity and triggers appropriate revalidation.

## Provider-neutral deployment

The orchestrator understands promotion, gates, environment readiness, artifact identity, and policy. It does not implement provider-specific mechanics such as Azure deployment slots, AWS blue/green, Kubernetes rolling updates, or mobile-store release behavior.

Those mechanics belong to selected specialists.

## Cross-cutting invocation model

Security, Infrastructure, Cost, AI, and Observability are involved through four modes as relevant:

1. **Baseline** — initial design assessment.
2. **Event-triggered** — a material relevant change occurs.
3. **Mandatory gate** — project/release/environment policy requires evidence.
4. **Operational** — production evidence, drift, incidents, or trends trigger work.

The model is event/materiality driven rather than "call discipline X because Phase N started."

## Security

Security may be triggered by architecture baseline work, identity/authentication/authorization changes, new sensitive data, new public/external integrations, permission or secret changes, significant infrastructure changes, release gates, vulnerabilities, incidents, and compliance needs.

Security validation may occur during design, build, test, release, and operations according to project risk/policy.

## Infrastructure

Infrastructure involvement covers topology/runtime/resilience/environment planning, IaC/configuration implementation, environment readiness, material topology/capacity/network/storage changes, release validation, drift, capacity, availability, and operational lifecycle.

Provider-specific implementation remains delegated.

## Cost

Cost uses an initial architecture baseline plus material-change and threshold triggers, such as new paid services, capacity growth, regions, environment count, storage/network changes, AI traffic/model changes, or forecast/budget variance.

Operations compares actuals to forecasts and generates optimization work when appropriate.

## AI

AI disciplines are activated only when applicable but remain lifecycle-wide once present. Triggers may include model/provider changes, prompt/agent/tool-access changes, retrieval/training data changes, evaluation requirements, safety constraints, latency/cost changes, and runtime quality drift.

AI release gates may evaluate quality, safety, latency, cost/token limits, fallback behavior, and project-specific acceptance criteria.

## Observability

Observability begins during architecture with critical flows, signals, metrics, logs, traces, audit events, health indicators, SLO/SLA signals, and diagnostic requirements.

Instrumentation is implemented during build, verified during test, validated for dashboards/alerts/rollback signals before release, and continuously used in production.

Observability is not a post-deployment-only activity.

## Trigger relevance and materiality

Changes undergo impact classification before specialists are invoked. A trivial documentation edit should not trigger a full security/cost/infrastructure/AI review. A material topology, data, authentication, model, or availability change may trigger several disciplines.

Reusable project profiles may provide defaults, but project policy remains authoritative.

## Convergence

Material cross-disciplinary changes may require convergence work/gates. Specialists reconcile technical conflicts where possible. Consequential business, cost, risk, scope, or policy trade-offs become structured decisions for the appropriate authority.

## Release readiness

Required release gates are project-specific. A prototype may require only tests and health checks, while a regulated AI service may require QA, security/compliance, AI evaluation, observability, release documentation, business acceptance, and production approval.

## Data and alternate paths

Environment policy may restrict data classifications and access. Alternate paths such as hotfix/emergency promotions are allowed only when explicitly defined by policy; urgency does not create undocumented bypasses.

## Operational feedback

Production evidence can create new work, risks, issues, incidents, decisions, and improvement items. Delivery completion and project closure are distinct: products may continue operating long after an individual release or project delivery milestone.

## Invariants

1. Project stage, work state, and environment state are separate dimensions.
2. Multiple releases/workstreams may occupy different lifecycle stages simultaneously.
3. Environment topology is configurable and may be a graph.
4. Promotion is controlled auditable work.
5. Artifact identity is preserved through promotion unless material change creates a new artifact requiring revalidation.
6. Provider-specific deployment mechanics belong to specialists.
7. Security, Infrastructure, Cost, AI, and Observability use baseline/event/gate/operations involvement as relevant.
8. Cross-cutting invocation is impact/materiality based.
9. Material cross-disciplinary changes require convergence.
10. Required release gates come from project policy/risk rather than universal hard-coding.
11. Environment policy may govern data classification/access.
12. Promotion requires target-environment readiness.
13. Hotfix/alternate paths require explicit policy.
14. Operational evidence may create new project work/control records.
15. Delivery completion and project closure are separate concepts.
