#!/usr/bin/env python3
"""Human-friendly disposable smoke test for the working Project Orchestrator MVP."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from build_registry import build_registry
from control_loop import run_iteration
from executor_continuity import end_run, start_run, write_checkpoint
from markdown_records import write_record
from project_docs import generate_handoff, init_workspace, render_views, sync_and_validate
from scan_skills import scan

ROOT = Path(__file__).resolve().parent.parent
POLICY = json.loads((ROOT / "profiles" / "default-policy.json").read_text(encoding="utf-8"))


def _pass(message: str) -> None:
    print(f"[PASS] {message}")


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    _pass(message)


def _registry(root: Path) -> dict:
    skills = root / "skills"
    skills.mkdir(parents=True, exist_ok=True)
    dev = skills / "developer"
    dev.mkdir()
    (dev / "SKILL.md").write_text(
        """---
name: smoke-developer
description: Implements delegated code work.
role: developer
capabilities: [development]
---
Implement delegated work only inside the provided contract.
""",
        encoding="utf-8",
    )
    review = skills / "reviewer"
    review.mkdir()
    (review / "SKILL.md").write_text(
        """---
name: smoke-reviewer
description: Independently reviews delegated code work.
role: qa-reviewer
capabilities: [code-review]
---
Review delegated work independently.
""",
        encoding="utf-8",
    )
    inventory = scan(skills)
    registry = build_registry([inventory], ROOT / "catalog")
    registry_dir = root / ".orchestrator" / "registry"
    registry_dir.mkdir(parents=True, exist_ok=True)
    (registry_dir / "capability-registry.json").write_text(json.dumps(registry, indent=2), encoding="utf-8")
    return registry


def run_smoke_test(verbose: bool = True) -> int:
    if verbose:
        print("Project Orchestrator MVP Smoke Test")
        print("Mode: DISPOSABLE / TEMPORARY")
        print("Canonical writes: temporary test root only")
        print("Git/cloud/pipeline writes: 0")
        print("")
    try:
        with tempfile.TemporaryDirectory(prefix="project-orchestrator-smoke-") as td:
            root = Path(td)
            registry = _registry(root)
            _pass("Local skill discovery and capability registry")

            init_workspace(root, "PRJ-SMOKE-001", "Orchestrator Smoke", "Validate the local orchestrator control loop")
            _pass("Markdown-first workspace initialization")

            build = {
                "id": "TASK-BUILD",
                "type": "Task",
                "title": "Build",
                "objective": "Implement the disposable smoke-test feature",
                "reporting_stage": "BUILD",
                "state": "PROPOSED",
                "priority": "HIGH",
                "required_capabilities": ["development"],
                "action_class": "A1",
                "acceptance_criteria": [
                    {"id": "AC-BUILD", "description": "Disposable feature completed", "required": True, "status": "PENDING"}
                ],
            }
            review = {
                "id": "TASK-REVIEW",
                "type": "Review",
                "title": "Review",
                "objective": "Independently review the disposable feature",
                "reporting_stage": "VALIDATE",
                "state": "PROPOSED",
                "priority": "HIGH",
                "required_capabilities": ["code-review"],
                "action_class": "A1",
            }
            dep = {
                "id": "DEP-BUILD-REVIEW",
                "predecessor": {"kind": "work", "id": "TASK-BUILD"},
                "successor": {"kind": "work", "id": "TASK-REVIEW"},
                "relationship": "FS",
                "strength": "HARD",
                "status": "UNSATISFIED",
            }
            write_record(root / "docs/40-delivery/TASK-BUILD.md", "work", build)
            write_record(root / "docs/40-delivery/TASK-REVIEW.md", "work", review)
            write_record(root / "docs/40-delivery/DEP-BUILD-REVIEW.md", "dependency", dep)

            run_path, run = start_run(
                root,
                "powershell-smoke-test",
                "automation",
                "Exercise local end-to-end orchestration",
                ["TASK-BUILD", "TASK-REVIEW"],
                modify=["TEMP/docs/**", "TEMP/.orchestrator/**"],
                protected=["real projects", "cloud", "pipelines"],
            )
            _expect(run_path.exists(), "Executor run record created")

            bundle, findings = sync_and_validate(root)
            _expect(not findings, "Canonical project state validates")
            first = run_iteration(bundle, registry, POLICY)
            _expect("TASK-BUILD" in first["dispatch"]["selected"], "Build becomes dispatchable")
            _expect("TASK-REVIEW" not in first["dispatch"]["selected"], "Review remains behind hard dependency")

            build["state"] = "DONE"
            build["acceptance_criteria"][0]["status"] = "SATISFIED"
            build["evidence_refs"] = ["EVID-SMOKE-BUILD"]
            write_record(root / "docs/40-delivery/TASK-BUILD.md", "work", build)
            bundle, findings = sync_and_validate(root)
            _expect(not findings, "Accepted build result revalidates")
            second = run_iteration(bundle, registry, POLICY)
            _expect(
                any(r["id"] == "DEP-BUILD-REVIEW" and r["to"] == "SATISFIED" for r in second["state_recommendations"]),
                "Completed predecessor satisfies dependency",
            )
            _expect(
                any(r["id"] == "TASK-REVIEW" and r["to"] == "READY" for r in second["state_recommendations"]),
                "Dependent review becomes READY",
            )
            _expect("TASK-REVIEW" in second["dispatch"]["selected"], "Dependent review becomes dispatchable")

            dep["status"] = "SATISFIED"
            review["state"] = "READY"
            write_record(root / "docs/40-delivery/DEP-BUILD-REVIEW.md", "dependency", dep)
            write_record(root / "docs/40-delivery/TASK-REVIEW.md", "work", review)
            bundle, findings = sync_and_validate(root)
            _expect(not findings, "Derived progression can be persisted canonically")

            state_dir = root / ".orchestrator" / "state"
            (state_dir / "orchestration.json").write_text(json.dumps(second, indent=2), encoding="utf-8")
            handoff = generate_handoff(root, bundle, "TASK-REVIEW")
            _expect(handoff.exists(), "Executor handoff generated")
            views = render_views(root, bundle, findings)
            _expect(all(path.exists() for path in views), "Project status/index regenerated")

            end_run(root, run["run_id"], "PASS", "Disposable end-to-end smoke test passed.")
            checkpoint_json, checkpoint_md, checkpoint = write_checkpoint(
                root, "powershell-smoke-test", "automation", "Resume after completed smoke test"
            )
            _expect(checkpoint_json.exists() and checkpoint_md.exists(), "Executor checkpoint generated")
            _expect(checkpoint["project"]["project_id"] == "PRJ-SMOKE-001", "Checkpoint preserves project identity")

            gap = {
                "id": "TASK-GAP",
                "type": "Task",
                "title": "Missing capability",
                "objective": "Require a deliberately unavailable capability",
                "reporting_stage": "BUILD",
                "state": "PROPOSED",
                "priority": "HIGH",
                "required_capabilities": ["quantum-potato-deployment"],
                "action_class": "A1",
            }
            write_record(root / "docs/40-delivery/TASK-GAP.md", "work", gap)
            bundle, _ = sync_and_validate(root)
            gap_result = run_iteration(bundle, registry, POLICY)
            _expect(
                any(r["id"] == "TASK-GAP" and r["to"] == "BLOCKED" for r in gap_result["state_recommendations"]),
                "Missing capability recommends BLOCKED instead of silent continuation",
            )

            prod = {
                "id": "PROD",
                "name": "Production",
                "class": "production",
                "purpose": "Serve users",
                "state": "READY",
                "promotion_to": [],
            }
            prod_work = {
                "id": "TASK-PROD",
                "type": "Task",
                "title": "Production change",
                "objective": "Validate production authority separation",
                "reporting_stage": "RELEASE",
                "state": "PROPOSED",
                "priority": "CRITICAL",
                "required_capabilities": ["development"],
                "environment_refs": ["PROD"],
                "action_class": "A1",
            }
            write_record(root / "docs/70-operations/PROD.md", "environment", prod)
            write_record(root / "docs/40-delivery/TASK-PROD.md", "work", prod_work)
            bundle, _ = sync_and_validate(root)
            prod_result = run_iteration(bundle, registry, POLICY)
            _expect(
                any(r["id"] == "TASK-PROD" and r["to"] == "NEEDS_DECISION" for r in prod_result["state_recommendations"]),
                "Production capability does not bypass approval authority",
            )

        print("")
        print("RESULT: PASS")
        return 0
    except Exception as exc:  # smoke harness should present one compact terminal result
        print("")
        print(f"[FAIL] {exc}")
        print("RESULT: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(run_smoke_test())
