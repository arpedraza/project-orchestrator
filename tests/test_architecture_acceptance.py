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
          "documentation-model.md","discovery-registry.md","policy-authority.md","execution-continuity.md",
          "validation-rules.md"
        ]
        for name in required:
            self.assertTrue((ROOT/"references"/name).is_file(),name)

    def test_quickstart_separates_skill_and_project_roots(self):
        text=(ROOT/"README.md").read_text(encoding="utf-8")
        self.assertIn("ORCHESTRATOR_HOME",text)
        self.assertIn("PROJECT_ROOT",text)
        self.assertIn("state_recommendations",text)
        self.assertIn("human by default",text)

    def test_executor_continuity_is_runtime_not_parallel_truth(self):
        skill=(ROOT/"SKILL.md").read_text(encoding="utf-8")
        reference=(ROOT/"references/execution-continuity.md").read_text(encoding="utf-8")
        self.assertIn("Project state is more important than conversation/session state",skill)
        self.assertIn("non-authoritative runtime artifacts",skill)
        self.assertIn("Mutation scope and authority are separate concepts",reference)
        self.assertIn("Canonical project truth remains under `docs/`",reference)
        self.assertTrue((ROOT/"schemas/execution-run.schema.json").is_file())
        self.assertTrue((ROOT/"schemas/executor-checkpoint.schema.json").is_file())

    def test_chatgpt_project_bootstrap_and_windows_harness_exist(self):
        self.assertTrue((ROOT/"orchestrator.ps1").is_file())
        for name in ("PROJECT-INSTRUCTIONS.md","README.md","TEST-PROMPT.md"):
            self.assertTrue((ROOT/"chatgpt"/name).is_file(),name)
        instructions=(ROOT/"chatgpt/PROJECT-INSTRUCTIONS.md").read_text(encoding="utf-8")
        self.assertIn("chat/project memory",instructions.lower())
        self.assertIn("do not claim",instructions.lower())
        readme=(ROOT/"README.md").read_text(encoding="utf-8")
        self.assertIn("Windows PowerShell local harness",readme)
        self.assertIn("Codex installation not required",readme)

    def test_permanent_v1_baseline_is_documented(self):
        for path in (ROOT/"README.md",ROOT/"phases.md",ROOT/"role-mapping.md"):
            self.assertIn("baseline/orchestrator-v1",path.read_text(encoding="utf-8"))

if __name__=="__main__": unittest.main()
