from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_PATH = ROOT / "scripts" / "scan_skills.py"
WRAPPER = ROOT / "scripts" / "scan-skills.sh"

spec = importlib.util.spec_from_file_location("scan_skills", SCAN_PATH)
scan_skills = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(scan_skills)


def write_skill(root: Path, directory: str, frontmatter: str, body: str = "") -> Path:
    skill = root / directory
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n{body}\n", encoding="utf-8")
    return skill


class ScannerRegressionTests(unittest.TestCase):
    def test_r01_simple_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "alpha", "name: alpha\ndescription: Simple scanner fixture\nrole: developer")
            inv = scan_skills.scan(root)
            self.assertEqual(inv["summary"]["skills_found"], 1)
            record = inv["packages"][0]
            self.assertEqual(record["declared"]["name"], "alpha")
            self.assertEqual(record["declared"]["roles"], ["developer"])
            self.assertEqual(record["metadata_status"], "valid")

    def test_r02_multiline_description(self):
        for marker in ("|", ">"):
            with self.subTest(marker=marker), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_skill(root, "alpha", f"name: alpha\ndescription: {marker}\n  First line\n  second line\nrole: developer")
                record = scan_skills.scan(root)["packages"][0]
                self.assertIn("First line", record["declared"]["description"])
                self.assertIn("second line", record["declared"]["description"])

    def test_r03_multiple_roles_inline_and_multiline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "inline", "name: inline\ndescription: x\nrole: [project-manager, scriber]")
            write_skill(root, "multi", "name: multi\ndescription: x\nroles:\n  - project-manager\n  - scriber")
            records = {p["directory_name"]: p for p in scan_skills.scan(root)["packages"]}
            self.assertEqual(records["inline"]["declared"]["roles"], ["project-manager", "scriber"])
            self.assertEqual(records["multi"]["declared"]["roles"], ["project-manager", "scriber"])

    def test_r04_explicit_capabilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "alpha", "name: alpha\ndescription: x\ncapabilities: [code-review, testing]")
            record = scan_skills.scan(root)["packages"][0]
            self.assertEqual(record["declared"]["capabilities"], ["code-review", "testing"])

    def test_r05_missing_manifest_not_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "not-a-skill").mkdir()
            inv = scan_skills.scan(root)
            self.assertEqual(inv["summary"]["skills_found"], 0)
            self.assertEqual(inv["summary"]["skipped_directories"], ["not-a-skill"])

    def test_r06_missing_root_returns_nonzero(self):
        missing = ROOT / "tests" / "definitely-not-present"
        proc = subprocess.run([sys.executable, str(SCAN_PATH), str(missing), "--format", "json"], capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("does not exist", proc.stderr)

    def test_r07_directory_manifest_name_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "directory-name", "name: manifest-name\ndescription: x")
            record = scan_skills.scan(root)["packages"][0]
            self.assertEqual(record["directory_name"], "directory-name")
            self.assertEqual(record["declared"]["name"], "manifest-name")
            self.assertEqual(record["metadata_status"], "warning")
            self.assertTrue(any("differs" in w for w in record["warnings"]))

    def test_r08_nested_packages_are_not_enumerated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent = write_skill(root, "parent", "name: parent\ndescription: x")
            nested = parent / "nested"
            nested.mkdir()
            (nested / "SKILL.md").write_text("---\nname: nested\ndescription: nested\n---\n", encoding="utf-8")
            inv = scan_skills.scan(root)
            self.assertEqual([p["directory_name"] for p in inv["packages"]], ["parent"])

    def test_r09_count_uses_same_boundary_as_listing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent = write_skill(root, "a", "name: a\ndescription: x")
            (parent / "nested").mkdir()
            (parent / "nested" / "SKILL.md").write_text("---\nname: nested\ndescription: y\n---\n", encoding="utf-8")
            write_skill(root, "b", "name: b\ndescription: x")
            (root / "c").mkdir()
            inv = scan_skills.scan(root)
            self.assertEqual(inv["summary"]["skills_found"], len(inv["packages"]))
            self.assertEqual(inv["summary"]["skills_found"], 2)

    def test_r10_json_output_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "alpha", "name: alpha\ndescription: x")
            proc = subprocess.run([sys.executable, str(SCAN_PATH), str(root), "--format", "json"], check=True, capture_output=True, text=True)
            data = json.loads(proc.stdout)
            self.assertEqual(data["schema_version"], "1.0")
            self.assertEqual(data["summary"]["skills_found"], 1)

    def test_r11_markdown_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "alpha", "name: alpha\ndescription: readable\nrole: developer")
            proc = subprocess.run([sys.executable, str(SCAN_PATH), str(root)], check=True, capture_output=True, text=True)
            self.assertIn("# Skill Registry Scan", proc.stdout)
            self.assertIn("`alpha`", proc.stdout)
            self.assertIn("developer", proc.stdout)

    def test_r12_shell_wrapper_compatibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "alpha", "name: alpha\ndescription: wrapper")
            proc = subprocess.run(["bash", str(WRAPPER), str(root), "--format", "json"], check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(proc.stdout)["summary"]["skills_found"], 1)

    def test_invalid_frontmatter_is_recorded_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "broken"
            skill.mkdir()
            (skill / "SKILL.md").write_text("name: broken\n", encoding="utf-8")
            record = scan_skills.scan(root)["packages"][0]
            self.assertEqual(record["metadata_status"], "invalid")
            self.assertTrue(record["errors"])


if __name__ == "__main__":
    unittest.main()
