import json
import tempfile
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from markdown_records import GENERATED_MARKER, RecordError, parse_record, scan_records, sync_state, write_record
from project_docs import init_workspace, render_views, generate_handoff, sync_and_validate, validate_links

class MarkdownRecordTests(unittest.TestCase):
    def test_write_parse_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"REQ-1.md"
            rec={"id":"REQ-1","status":"PROPOSED","title":"Need thing","owner":"po"}
            write_record(p,"requirement",rec,"# Requirement\n\nNarrative.")
            parsed=parse_record(p)
            self.assertEqual(parsed["id"],"REQ-1")
            self.assertEqual(parsed["record_type"],"requirement")
            self.assertEqual(parsed["owner"],"po")
            self.assertIn("Narrative",parsed["_narrative"])

    def test_generated_file_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"status.md"; p.write_text(GENERATED_MARKER+"\n# Status\n",encoding="utf-8")
            self.assertIsNone(parse_record(p))

    def test_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); write_record(root/"a.md","requirement",{"id":"X","status":"PROPOSED"}); write_record(root/"b.md","decision",{"id":"X","status":"OPEN"})
            with self.assertRaises(RecordError): scan_records(root)

class WorkspaceTests(unittest.TestCase):
    def make_root(self):
        td=tempfile.TemporaryDirectory(); root=Path(td.name)
        init_workspace(root,"PRJ-1","Demo","Deliver demo")
        return td,root

    def test_init_creates_project_and_runtime_dirs(self):
        td,root=self.make_root()
        try:
            self.assertTrue((root/"docs/00-project-control/PRJ-1-project.md").exists())
            self.assertTrue((root/".orchestrator/state").is_dir())
            self.assertTrue((root/"docs/70-operations").is_dir())
        finally: td.cleanup()

    def test_second_init_does_not_overwrite_project(self):
        td,root=self.make_root()
        try:
            p=root/"docs/00-project-control/PRJ-1-project.md"; before=p.read_text()
            init_workspace(root,"PRJ-1","Changed","Different objective")
            self.assertEqual(before,p.read_text())
        finally: td.cleanup()

    def test_sync_writes_state(self):
        td,root=self.make_root()
        try:
            bundle,findings=sync_and_validate(root)
            self.assertEqual(findings,[])
            state=root/".orchestrator/state/state.json"; self.assertTrue(state.exists())
            self.assertEqual(json.loads(state.read_text())["project"]["project_id"],"PRJ-1")
        finally: td.cleanup()

    def test_render_views_are_generated_not_canonical(self):
        td,root=self.make_root()
        try:
            bundle,findings=sync_and_validate(root); paths=render_views(root,bundle,findings)
            self.assertTrue(all(GENERATED_MARKER in p.read_text() for p in paths))
            ids=[r["id"] for r in scan_records(root/"docs")]
            self.assertEqual(ids,["PRJ-1"])
        finally: td.cleanup()

    def test_handoff_is_regenerable_context(self):
        td,root=self.make_root()
        try:
            work={"id":"TASK-1","type":"Task","title":"Build","objective":"Build it","reporting_stage":"BUILD","state":"READY","priority":"HIGH","required_capabilities":["development"],"acceptance_criteria":[{"id":"AC-1","description":"Works","required":True,"status":"PENDING"}]}
            write_record(root/"docs/40-delivery/TASK-1.md","work",work)
            bundle,findings=sync_and_validate(root); self.assertEqual(findings,[])
            p=generate_handoff(root,bundle,"TASK-1")
            self.assertIn(GENERATED_MARKER,p.read_text())
            self.assertIn("Build it",p.read_text())
            p.unlink(); p2=generate_handoff(root,bundle,"TASK-1"); self.assertTrue(p2.exists())
        finally: td.cleanup()

    def test_broken_link_detected(self):
        td,root=self.make_root()
        try:
            p=root/"docs/80-reviews/note.md"; p.write_text("# Review\n\n[missing](missing.md)\n",encoding="utf-8")
            findings=validate_links(root)
            self.assertEqual(findings[0]["code"],"DOC-LINK-002")
        finally: td.cleanup()

    def test_valid_link_passes(self):
        td,root=self.make_root()
        try:
            target=root/"docs/80-reviews/target.md"; target.write_text("# Target\n",encoding="utf-8")
            note=root/"docs/80-reviews/note.md"; note.write_text("[target](target.md)\n",encoding="utf-8")
            self.assertEqual(validate_links(root),[])
        finally: td.cleanup()

if __name__=="__main__": unittest.main()
