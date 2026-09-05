import json
import tempfile
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from scan_skills import scan
from build_registry import build_registry
from markdown_records import write_record
from project_docs import init_workspace, sync_and_validate, render_views, generate_handoff
from control_loop import run_iteration

POLICY=json.loads((ROOT/"profiles/default-policy.json").read_text())

class MVPScenarioTests(unittest.TestCase):
    def make_registry(self, root:Path):
        skills=root/"skills"; skills.mkdir()
        dev=skills/"dev"; dev.mkdir(); (dev/"SKILL.md").write_text("""---
name: dev
description: Implements project code.
role: developer
capabilities: [development]
---
Implement delegated code work.
""",encoding="utf-8")
        review=skills/"review"; review.mkdir(); (review/"SKILL.md").write_text("""---
name: review
description: Independently reviews code.
role: qa-reviewer
capabilities: [code-review]
---
Review delegated code work.
""",encoding="utf-8")
        inventory=scan(skills)
        return build_registry([inventory],ROOT/"catalog")

    def test_end_to_end_dependency_progression(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); registry=self.make_registry(root)
            init_workspace(root,"PRJ-1","MVP","Build then review")
            t1={"id":"TASK-1","type":"Task","title":"Build","objective":"Implement feature","reporting_stage":"BUILD","state":"PROPOSED","priority":"HIGH","required_capabilities":["development"],"action_class":"A1","schedule":{"estimate":{"value":1,"unit":"hours"}},"acceptance_criteria":[{"id":"AC-1","description":"Feature implemented","required":True,"status":"PENDING"}]}
            t2={"id":"TASK-2","type":"Review","title":"Review","objective":"Review implementation","reporting_stage":"VALIDATE","state":"PROPOSED","priority":"HIGH","required_capabilities":["code-review"],"action_class":"A1","schedule":{"estimate":{"value":1,"unit":"hours"}}}
            dep={"id":"DEP-1","predecessor":{"kind":"work","id":"TASK-1"},"successor":{"kind":"work","id":"TASK-2"},"relationship":"FS","strength":"HARD","status":"UNSATISFIED"}
            write_record(root/"docs/40-delivery/TASK-1.md","work",t1)
            write_record(root/"docs/40-delivery/TASK-2.md","work",t2)
            write_record(root/"docs/40-delivery/DEP-1.md","dependency",dep)
            bundle,findings=sync_and_validate(root); self.assertEqual(findings,[])
            first=run_iteration(bundle,registry,POLICY)
            self.assertIn("TASK-1",first["dispatch"]["selected"])
            self.assertNotIn("TASK-2",first["dispatch"]["selected"])
            self.assertTrue(any(r["id"]=="TASK-1" and r["to"]=="READY" for r in first["state_recommendations"]))

            # Simulate accepted executor result written back to canonical Markdown.
            t1["state"]="DONE"; t1["acceptance_criteria"][0]["status"]="SATISFIED"; t1["evidence_refs"]=["run:TASK-1"]
            write_record(root/"docs/40-delivery/TASK-1.md","work",t1,"# TASK-1 — Build\n\nImplementation completed and accepted.\n")
            bundle,findings=sync_and_validate(root); self.assertEqual(findings,[])
            second=run_iteration(bundle,registry,POLICY)
            self.assertTrue(any(r["id"]=="DEP-1" and r["to"]=="SATISFIED" for r in second["state_recommendations"]))
            self.assertTrue(any(r["id"]=="TASK-2" and r["to"]=="READY" for r in second["state_recommendations"]))
            self.assertIn("TASK-2",second["dispatch"]["selected"])

            # Apply recommendations as Project Control would, then generate execution/user views.
            dep["status"]="SATISFIED"; t2["state"]="READY"
            write_record(root/"docs/40-delivery/DEP-1.md","dependency",dep)
            write_record(root/"docs/40-delivery/TASK-2.md","work",t2)
            bundle,findings=sync_and_validate(root); self.assertEqual(findings,[])
            handoff=generate_handoff(root,bundle,"TASK-2"); self.assertIn("Review implementation",handoff.read_text())
            views=render_views(root,bundle,findings); self.assertTrue(all(p.exists() for p in views))

    def test_capability_gap_recommends_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); registry=self.make_registry(root)
            init_workspace(root,"PRJ-1","Gap","Gap test")
            work={"id":"TASK-X","type":"Task","title":"Special","objective":"Need rare capability","reporting_stage":"BUILD","state":"PROPOSED","priority":"HIGH","required_capabilities":["rare-capability"],"action_class":"A1"}
            write_record(root/"docs/40-delivery/TASK-X.md","work",work)
            bundle,_=sync_and_validate(root); result=run_iteration(bundle,registry,POLICY)
            self.assertTrue(any(r["id"]=="TASK-X" and r["to"]=="BLOCKED" for r in result["state_recommendations"]))
            self.assertEqual(result["capability_gaps"][0]["work_id"],"TASK-X")

    def test_production_without_approval_recommends_decision(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); registry=self.make_registry(root)
            init_workspace(root,"PRJ-1","Release","Production gate")
            env={"id":"PROD","name":"Production","class":"production","purpose":"serve users","state":"READY","promotion_to":[]}
            work={"id":"TASK-P","type":"Task","title":"Prod change","objective":"Change production","reporting_stage":"RELEASE","state":"PROPOSED","priority":"CRITICAL","required_capabilities":["development"],"environment_refs":["PROD"],"action_class":"A1"}
            write_record(root/"docs/70-operations/PROD.md","environment",env)
            write_record(root/"docs/40-delivery/TASK-P.md","work",work)
            bundle,_=sync_and_validate(root); result=run_iteration(bundle,registry,POLICY)
            self.assertTrue(any(r["id"]=="TASK-P" and r["to"]=="NEEDS_DECISION" for r in result["state_recommendations"]))
            self.assertNotIn("TASK-P",result["dispatch"]["selected"])

if __name__=="__main__": unittest.main()
