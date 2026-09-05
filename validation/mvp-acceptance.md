# Project Orchestrator v2 — Working MVP Acceptance

> **Status:** CHG-008 working-project acceptance contract.

The MVP is considered working when the cumulative automated suite demonstrates the control architecture end to end rather than only validating isolated schemas.

## E2E-01 — Dependency-driven delivery progression

**Given**
- a Markdown project workspace;
- two discovered local specialists declaring `development` and `code-review` capabilities;
- a PROPOSED build task;
- a PROPOSED independent-review task with a HARD FS dependency on the build task.

**When**
1. canonical Markdown is synchronized;
2. the capability registry is built;
3. one orchestration iteration runs;
4. the accepted build result is recorded back into canonical Markdown;
5. a second iteration runs.

**Expected**
- the build task is recommended `PROPOSED → READY` and becomes dispatchable;
- the review task does not dispatch before its predecessor completes;
- after the build becomes DONE, the dependency is recommended `UNSATISFIED → SATISFIED`;
- the review task is recommended `PROPOSED → READY` and becomes dispatchable;
- executor handoff and project status/index can be regenerated from canonical state.

Automated by `tests/test_mvp_scenarios.py`.

## E2E-02 — Missing capability does not silently continue

**Given** a PROPOSED work item requiring a capability with no eligible registered executor.

**Expected**
- work is not dispatched;
- a capability gap is reported;
- Project Control recommends the work become BLOCKED pending normal gap recovery.

Automated by `tests/test_mvp_scenarios.py`.

## E2E-03 — Production authority remains separate from capability

**Given** a capable executor and a production-scoped work item without required approval under the conservative default policy.

**Expected**
- the work is not dispatched;
- authority is surfaced as a decision condition;
- Project Control recommends `NEEDS_DECISION` rather than treating technical capability as production permission.

Automated by `tests/test_mvp_scenarios.py`.

## Architecture acceptance

The package additionally passes `tests/test_architecture_acceptance.py`, which verifies:

- active `SKILL.md` is state/capability driven rather than a fixed phase runner;
- old numbered phases are explicitly legacy migration material;
- old role/Primary routing is explicitly retired;
- original handoff templates are marked v1 compatibility only;
- all v2 source references named by the skill exist;
- operator quickstart separates the installed skill root from the project root;
- the permanent v1 baseline is documented.

## Working-MVP boundary

A passing CHG-008 does **not** mean every approved long-term enhancement is implemented. It means the v2 core can operate a real project control loop with canonical Markdown state, dynamic capability routing, dependency progression, policy-aware dispatch, recovery/project-control foundations, and regenerable documentation.

Enhancements after this point return to normal change planning/approval rather than the Product Owner's temporary blanket approval to reach a working project.
