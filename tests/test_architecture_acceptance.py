import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class ArchitectureAcceptanceTests(unittest.TestCase):
    def test_skill_is_state_driven_not_fixed_phase_runner(self):
        text=(ROOT/"SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Do **not** execute a fixed sequence of numbered phases",text)
        self.assertIn("Capabilities drive routing",text)
        self.assertIn("Canonical Markdown",text)
        self.assertIn("Default production policy",text)
        self.assertNotIn("PHASE 1  →",text)
        self.assertNotIn("primary: azure-deploy",text)
        self.assertNotIn("primary: github",text)

    def test_phases_are_explicitly_legacy(self):
        text=(ROOT/"phases.md").read_text(encoding="utf-8")
        self.assertIn("LEGACY / MIGRATION REFERENCE ONLY",text)
        self.assertIn("not runtime authority",text.lower())
        self.assertNotIn("PHASE 1 —",text)

    def test_role_mapping_is_explicitly_legacy(self):
        text=(ROOT/"role-mapping.md").read_text(encoding="utf-8")
        self.assertIn("LEGACY / MIGRATION REFERENCE ONLY",text)
        self.assertIn("capabilities drive task matching",text.lower())
        self.assertIn("Do not restore `Primary` skill routing",text)

    def test_legacy_handoff_directory_is_marked(self):
        text=(ROOT/"handoff-templates/README.md").read_text(encoding="utf-8")
        self.assertIn("v1 compatibility",text)
        self.assertIn("does not use numbered phase handoffs",text)

    def test_skill_source_references_exist(self):
        required=[
          "operating-model.md","project-state.md","capabilities-executors.md","scheduling-gates.md",
          "lifecycle-environments.md","recovery-change-control.md","project-control-traceability.md",
          "documentation-model.md","discovery-registry.md","policy-authority.md","validation-rules.md"
        ]
        for name in required:
            self.assertTrue((ROOT/"references"/name).is_file(),name)

    def test_quickstart_separates_skill_and_project_roots(self):
        text=(ROOT/"README.md").read_text(encoding="utf-8")
        self.assertIn("ORCHESTRATOR_HOME",text)
        self.assertIn("PROJECT_ROOT",text)
        self.assertIn("state_recommendations",text)
        self.assertIn("human by default",text)

    def test_permanent_v1_baseline_is_documented(self):
        for path in (ROOT/"README.md",ROOT/"phases.md",ROOT/"role-mapping.md"):
            self.assertIn("baseline/orchestrator-v1",path.read_text(encoding="utf-8"))

if __name__=="__main__": unittest.main()
