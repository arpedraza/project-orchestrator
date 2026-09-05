from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from state_model import validate_state_bundle  # noqa: E402


def minimal_bundle():
    return {
        "schema_version": "1.0",
        "project": {
            "project_id": "PRJ-001",
            "name": "Example",
            "objective": "Validate state semantics",
            "status": "ACTIVE",
            "reporting_stage": "Build/Iterate",
            "active_baseline_ref": "BL-001",
            "policy_refs": [],
            "environment_refs": [],
            "active_release_refs": [],
            "register_refs": {},
        },
        "work_items": [
            {
                "id": "TASK-001",
                "type": "Task",
                "title": "Implement component",
                "objective": "Produce accepted component",
                "parent_ref": None,
                "reporting_stage": "Build/Iterate",
                "state": "PROPOSED",
                "priority": "HIGH",
                "required_capabilities": ["delivery.code-implementation"],
                "preferred_capabilities": [],
                "executor": None,
                "environment_refs": [],
                "release_refs": [],
                "dependencies": [],
                "required_gates": [],
                "acceptance_criteria": [
                    {"id": "AC-001", "description": "Component exists", "required": True, "status": "PENDING", "evidence_refs": []}
                ],
                "traceability_refs": [],
                "output_refs": [],
                "evidence_refs": [],
                "schedule": {
                    "estimate": {"value": 4, "unit": "hours"},
                    "baseline": {"start": "2026-09-06T09:00:00+02:00", "finish": "2026-09-06T13:00:00+02:00"},
                    "forecast": {"start": "2026-09-06T10:00:00+02:00", "finish": "2026-09-06T14:00:00+02:00"},
                    "actual": {}
                }
            }
        ],
        "dependencies": [],
        "gates": [],
    }


def codes(bundle):
    return {finding.code for finding in validate_state_bundle(bundle)}


class StateModelTests(unittest.TestCase):
    def test_valid_minimal_project_state(self):
        self.assertEqual(validate_state_bundle(minimal_bundle()), [])

    def test_duplicate_stable_ids_rejected(self):
        bundle = minimal_bundle()
        bundle["gates"].append({
            "id": "TASK-001", "name": "Duplicate", "category": "qa", "scope": {"artifact": "A"},
            "blocking": True, "criteria": [], "status": "READY", "validity": "VALID", "evidence_refs": []
        })
        self.assertIn("STATE-ID-001", codes(bundle))

    def test_missing_local_reference_rejected(self):
        bundle = minimal_bundle()
        bundle["work_items"][0]["parent_ref"] = "TASK-MISSING"
        self.assertIn("STATE-REF-WORK-001", codes(bundle))

    def test_hard_dependency_cycle_rejected(self):
        bundle = minimal_bundle()
        second = copy.deepcopy(bundle["work_items"][0])
        second["id"] = "TASK-002"
        second["acceptance_criteria"][0]["id"] = "AC-002"
        bundle["work_items"].append(second)
        bundle["dependencies"] = [
            {"id": "DEP-001", "predecessor": {"kind": "work", "id": "TASK-001"}, "successor": {"kind": "work", "id": "TASK-002"}, "relationship": "FS", "strength": "HARD", "status": "SATISFIED"},
            {"id": "DEP-002", "predecessor": {"kind": "work", "id": "TASK-002"}, "successor": {"kind": "work", "id": "TASK-001"}, "relationship": "FS", "strength": "HARD", "status": "SATISFIED"},
        ]
        self.assertIn("STATE-DEP-CYCLE-001", codes(bundle))

    def test_soft_cycle_allowed(self):
        bundle = minimal_bundle()
        second = copy.deepcopy(bundle["work_items"][0])
        second["id"] = "TASK-002"
        second["acceptance_criteria"][0]["id"] = "AC-002"
        bundle["work_items"].append(second)
        bundle["dependencies"] = [
            {"id": "DEP-001", "predecessor": {"kind": "work", "id": "TASK-001"}, "successor": {"kind": "work", "id": "TASK-002"}, "strength": "SOFT", "status": "UNSATISFIED"},
            {"id": "DEP-002", "predecessor": {"kind": "work", "id": "TASK-002"}, "successor": {"kind": "work", "id": "TASK-001"}, "strength": "SOFT", "status": "UNSATISFIED"},
        ]
        self.assertNotIn("STATE-DEP-CYCLE-001", codes(bundle))

    def test_ready_with_unsatisfied_hard_dependency_rejected(self):
        bundle = minimal_bundle()
        bundle["work_items"][0]["state"] = "READY"
        bundle["dependencies"] = [{
            "id": "DEP-001", "predecessor": {"kind": "external", "id": "EXT-001"},
            "successor": {"kind": "work", "id": "TASK-001"}, "strength": "HARD", "status": "UNSATISFIED"
        }]
        self.assertIn("STATE-READY-001", codes(bundle))

    def test_ready_with_unsatisfied_soft_dependency_allowed(self):
        bundle = minimal_bundle()
        bundle["work_items"][0]["state"] = "READY"
        bundle["dependencies"] = [{
            "id": "DEP-001", "predecessor": {"kind": "external", "id": "EXT-001"},
            "successor": {"kind": "work", "id": "TASK-001"}, "strength": "SOFT", "status": "UNSATISFIED"
        }]
        self.assertNotIn("STATE-READY-001", codes(bundle))

    def test_ready_with_at_risk_hard_dependency_allowed(self):
        bundle = minimal_bundle()
        bundle["work_items"][0]["state"] = "READY"
        bundle["dependencies"] = [{
            "id": "DEP-001", "predecessor": {"kind": "external", "id": "EXT-001"},
            "successor": {"kind": "work", "id": "TASK-001"}, "strength": "HARD", "status": "AT_RISK"
        }]
        self.assertNotIn("STATE-READY-001", codes(bundle))

    def test_ready_with_waived_hard_dependency_and_decision_allowed(self):
        bundle = minimal_bundle()
        bundle["work_items"][0]["state"] = "READY"
        bundle["dependencies"] = [{
            "id": "DEP-001", "predecessor": {"kind": "external", "id": "EXT-001"},
            "successor": {"kind": "work", "id": "TASK-001"}, "strength": "HARD", "status": "WAIVED", "decision_ref": "DEC-001"
        }]
        result = codes(bundle)
        self.assertNotIn("STATE-READY-001", result)
        self.assertNotIn("STATE-DEP-WAIVER-001", result)

    def test_done_with_pending_required_acceptance_rejected(self):
        bundle = minimal_bundle()
        bundle["work_items"][0]["state"] = "DONE"
        self.assertIn("STATE-DONE-AC-001", codes(bundle))

    def test_done_with_failed_required_acceptance_rejected(self):
        bundle = minimal_bundle()
        bundle["work_items"][0]["state"] = "DONE"
        bundle["work_items"][0]["acceptance_criteria"][0]["status"] = "FAILED"
        self.assertIn("STATE-DONE-AC-001", codes(bundle))

    def test_done_with_missing_required_gate_rejected(self):
        bundle = minimal_bundle()
        work = bundle["work_items"][0]
        work["state"] = "DONE"
        work["acceptance_criteria"][0]["status"] = "SATISFIED"
        work["required_gates"] = ["GATE-001"]
        result = codes(bundle)
        self.assertIn("STATE-REF-GATE-001", result)
        self.assertIn("STATE-DONE-GATE-001", result)

    def test_done_with_failed_gate_rejected(self):
        bundle = minimal_bundle()
        work = bundle["work_items"][0]
        work["state"] = "DONE"
        work["acceptance_criteria"][0]["status"] = "SATISFIED"
        work["required_gates"] = ["GATE-001"]
        bundle["gates"] = [{
            "id": "GATE-001", "name": "QA", "category": "qa", "scope": {"artifact": "BUILD-1"},
            "blocking": True, "criteria": [], "status": "FAILED", "validity": "VALID", "evidence_refs": ["EVID-001"]
        }]
        self.assertIn("STATE-DONE-GATE-002", codes(bundle))

    def test_passed_gate_without_evidence_rejected(self):
        bundle = minimal_bundle()
        bundle["gates"] = [{
            "id": "GATE-001", "name": "QA", "category": "qa", "scope": {"artifact": "BUILD-1"},
            "blocking": True, "criteria": [], "status": "PASSED", "validity": "VALID", "evidence_refs": []
        }]
        self.assertIn("STATE-GATE-PASS-003", codes(bundle))

    def test_passed_gate_without_scope_rejected(self):
        bundle = minimal_bundle()
        bundle["gates"] = [{
            "id": "GATE-001", "name": "QA", "category": "qa", "scope": {},
            "blocking": True, "criteria": [], "status": "PASSED", "validity": "VALID", "evidence_refs": ["EVID-001"]
        }]
        self.assertIn("STATE-GATE-PASS-002", codes(bundle))

    def test_passed_gate_with_unsatisfied_required_criterion_rejected(self):
        bundle = minimal_bundle()
        bundle["gates"] = [{
            "id": "GATE-001", "name": "QA", "category": "qa", "scope": {"artifact": "BUILD-1"},
            "blocking": True,
            "criteria": [{"id": "GC-001", "description": "Tests pass", "required": True, "status": "FAILED", "evidence_refs": ["EVID-001"]}],
            "status": "PASSED", "validity": "VALID", "evidence_refs": ["EVID-001"]
        }]
        self.assertIn("STATE-GATE-PASS-001", codes(bundle))

    def test_waived_gate_without_decision_rejected(self):
        bundle = minimal_bundle()
        bundle["gates"] = [{
            "id": "GATE-001", "name": "QA", "category": "qa", "scope": {"artifact": "BUILD-1"},
            "blocking": True, "criteria": [], "status": "WAIVED", "validity": "VALID", "evidence_refs": []
        }]
        self.assertIn("STATE-GATE-WAIVER-001", codes(bundle))

    def test_waived_dependency_without_decision_rejected(self):
        bundle = minimal_bundle()
        bundle["dependencies"] = [{
            "id": "DEP-001", "predecessor": {"kind": "external", "id": "EXT-1"},
            "successor": {"kind": "work", "id": "TASK-001"}, "status": "WAIVED"
        }]
        self.assertIn("STATE-DEP-WAIVER-001", codes(bundle))

    def test_valid_waived_gate_is_not_passed_but_can_close_required_gate(self):
        bundle = minimal_bundle()
        work = bundle["work_items"][0]
        work["state"] = "DONE"
        work["acceptance_criteria"][0]["status"] = "SATISFIED"
        work["required_gates"] = ["GATE-001"]
        bundle["gates"] = [{
            "id": "GATE-001", "name": "Business waiver", "category": "acceptance", "scope": {"release": "REL-1"},
            "blocking": True, "criteria": [], "status": "WAIVED", "validity": "VALID",
            "evidence_refs": [], "decision_ref": "DEC-001"
        }]
        self.assertEqual(validate_state_bundle(bundle), [])
        self.assertEqual(bundle["gates"][0]["status"], "WAIVED")

    def test_executor_types_share_same_contract(self):
        for executor_type in ("human", "agent", "automation", "external"):
            with self.subTest(executor_type=executor_type):
                bundle = minimal_bundle()
                bundle["work_items"][0]["executor"] = {"type": executor_type, "id": f"EXE-{executor_type}"}
                self.assertEqual(validate_state_bundle(bundle), [])

    def test_baseline_forecast_actual_are_separate(self):
        bundle = minimal_bundle()
        schedule = bundle["work_items"][0]["schedule"]
        self.assertNotEqual(schedule["baseline"]["start"], schedule["forecast"]["start"])
        self.assertEqual(validate_state_bundle(bundle), [])

    def test_extensible_work_item_type_accepted(self):
        bundle = minimal_bundle()
        bundle["work_items"][0]["type"] = "OrganizationSpecificReview"
        self.assertEqual(validate_state_bundle(bundle), [])

    def test_configurable_reporting_stage_accepted(self):
        bundle = minimal_bundle()
        bundle["project"]["reporting_stage"] = "Custom Steering Window"
        bundle["work_items"][0]["reporting_stage"] = "Custom Steering Window"
        self.assertEqual(validate_state_bundle(bundle), [])

    def test_invalid_schedule_datetime_rejected(self):
        bundle = minimal_bundle()
        bundle["work_items"][0]["schedule"]["forecast"]["start"] = "tomorrow morning"
        self.assertIn("STATE-SCHEDULE-002", codes(bundle))

    def test_required_gate_passed_and_valid_allows_done(self):
        bundle = minimal_bundle()
        work = bundle["work_items"][0]
        work["state"] = "DONE"
        work["acceptance_criteria"][0]["status"] = "SATISFIED"
        work["required_gates"] = ["GATE-001"]
        bundle["gates"] = [{
            "id": "GATE-001", "name": "QA", "category": "qa", "scope": {"artifact": "BUILD-1", "environment": "QA"},
            "blocking": True,
            "criteria": [{"id": "GC-001", "description": "Tests pass", "required": True, "status": "SATISFIED", "evidence_refs": ["EVID-001"]}],
            "status": "PASSED", "validity": "VALID", "evidence_refs": ["EVID-001"]
        }]
        self.assertEqual(validate_state_bundle(bundle), [])

    def test_cli_valid_and_invalid_exit_codes(self):
        bundle = minimal_bundle()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "state.json"
            path.write_text(json.dumps(bundle), encoding="utf-8")
            good = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_state.py"), str(path)], capture_output=True, text=True)
            self.assertEqual(good.returncode, 0)
            self.assertEqual(good.stdout.strip(), "VALID")
            bundle["work_items"][0]["state"] = "DONE"
            path.write_text(json.dumps(bundle), encoding="utf-8")
            bad = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_state.py"), str(path), "--format", "json"], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)
            payload = json.loads(bad.stdout)
            self.assertFalse(payload["valid"])
            self.assertIn("STATE-DONE-AC-001", {f["code"] for f in payload["findings"]})


if __name__ == "__main__":
    unittest.main()
