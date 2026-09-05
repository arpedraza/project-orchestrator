import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from executor_continuity import (
    ContinuityError,
    add_run_event,
    end_run,
    resume_status,
    start_run,
    write_checkpoint,
)
from markdown_records import write_record
from project_docs import init_workspace, sync_and_validate


class ExecutorContinuityTests(unittest.TestCase):
    def test_run_history_preserves_boundary_events_and_failure_classification(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root, "PRJ-1", "Continuity", "Test executor continuity")
            sync_and_validate(root)
            path, run = start_run(
                root,
                executor_id="codex-session-1",
                executor_type="agent",
                objective="Validate a proposed source mutation",
                work_item_refs=["TASK-1"],
                authority_refs=["POLICY-LOCAL"],
                modify=["src/app.py"],
                new=["tests/test_app.py"],
                protected=["production", "unrelated.txt"],
            )
            self.assertTrue(path.exists())
            self.assertEqual(run["mutation_boundary"]["modify"], ["src/app.py"])
            add_run_event(root, run["run_id"], "PREFLIGHT", "Read-only validation found stale input", ["TASK-1"])
            ended = end_run(
                root,
                run["run_id"],
                "FAIL_PRE_WRITE",
                "Stopped before mutation because the pre-write state was stale.",
                cause="STATE_DRIFT",
            )
            self.assertEqual(ended["status"], "FAILED")
            self.assertEqual(ended["classification"], "FAIL_PRE_WRITE")
            self.assertEqual(ended["cause"], "STATE_DRIFT")
            self.assertEqual(len(ended["events"]), 1)
            persisted = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(persisted["mutation_boundary"]["protected"], ["production", "unrelated.txt"])
            self.assertIsNotNone(persisted["ended_at"])

    def test_checkpoint_is_noncanonical_and_resume_detects_state_drift(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root, "PRJ-1", "Continuity", "Resume safely")
            work = {
                "id": "TASK-1",
                "type": "Task",
                "title": "Implement",
                "objective": "Implement the change",
                "reporting_stage": "BUILD",
                "state": "READY",
                "priority": "HIGH",
                "required_capabilities": ["development"],
                "action_class": "A1",
            }
            write_record(root / "docs/40-delivery/TASK-1.md", "work", work)
            sync_and_validate(root)
            orchestration = {
                "valid": True,
                "dispatch": {"selected": ["TASK-1"]},
                "state_recommendations": [],
                "capability_gaps": [],
                "authority_blocks": [],
                "decisions": [],
            }
            state_dir = root / ".orchestrator/state"
            state_dir.mkdir(parents=True, exist_ok=True)
            (state_dir / "orchestration.json").write_text(json.dumps(orchestration), encoding="utf-8")
            archive_json, archive_md, checkpoint = write_checkpoint(root, "chatgpt-project", "agent", "Continue delivery")
            self.assertTrue(archive_json.exists())
            self.assertTrue(archive_md.exists())
            self.assertTrue((root / ".orchestrator/checkpoints/latest.json").exists())
            latest_md = (root / ".orchestrator/checkpoints/latest.md").read_text(encoding="utf-8")
            self.assertIn("non-authoritative", latest_md)
            self.assertIn("TASK-1", latest_md)
            self.assertEqual(checkpoint["orchestration"]["dispatch_selected"], ["TASK-1"])
            first_resume = resume_status(root)
            self.assertFalse(first_resume["state_changed_since_checkpoint"])

            work["state"] = "IN_PROGRESS"
            write_record(root / "docs/40-delivery/TASK-1.md", "work", work)
            sync_and_validate(root)
            second_resume = resume_status(root)
            self.assertTrue(second_resume["state_changed_since_checkpoint"])

    def test_project_identity_mismatch_is_hard_stop(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root, "PRJ-1", "Identity", "Identity test")
            sync_and_validate(root)
            write_checkpoint(root, "human-1", "human")
            latest = root / ".orchestrator/checkpoints/latest.json"
            value = json.loads(latest.read_text(encoding="utf-8"))
            value["project"]["project_id"] = "PRJ-WRONG"
            latest.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(ContinuityError):
                resume_status(root)

    def test_completed_run_cannot_be_modified(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root, "PRJ-1", "Run", "Terminal run test")
            sync_and_validate(root)
            _, run = start_run(root, "automation", "automation", "Execute a disposable validation")
            end_run(root, run["run_id"], "PASS", "Validation passed.")
            with self.assertRaises(ContinuityError):
                add_run_event(root, run["run_id"], "INFO", "Too late")
            with self.assertRaises(ContinuityError):
                end_run(root, run["run_id"], "PASS", "Second terminal update")


if __name__ == "__main__":
    unittest.main()
