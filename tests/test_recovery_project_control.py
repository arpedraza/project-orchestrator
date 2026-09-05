import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"scripts"))
import recovery_engine, project_control

class RecoveryTests(unittest.TestCase):
  def test_transient_retry(self):
    p=recovery_engine.plan_recovery({"work_ref":"T1","tags":["timeout"]},attempts=0,max_attempts=2)
    self.assertEqual(p.action,"retry"); self.assertTrue(p.autonomous)
  def test_defect_rework(self): self.assertEqual(recovery_engine.plan_recovery({"tags":["test-failure"]}).action,"rework")
  def test_capability_gap(self): self.assertEqual(recovery_engine.plan_recovery({"tags":["missing-skill"]}).action,"capability-gap")
  def test_authority_escalates(self):
    p=recovery_engine.plan_recovery({"kind":"decision-required","work_ref":"T1"}); self.assertEqual(p.action,"escalate"); self.assertIsNotNone(p.escalation)
  def test_recovery_budget(self):
    p=recovery_engine.plan_recovery({"tags":["timeout"],"work_ref":"T1"},attempts=2,max_attempts=2); self.assertEqual(p.action,"recovery-review"); self.assertEqual(p.next_state,"NEEDS_DECISION")
  def test_nonblocking_parks(self): self.assertEqual(recovery_engine.plan_recovery({"blocking":False}).action,"park")

class ControlTests(unittest.TestCase):
  def bundle(self):
    return {"work_items":[{"id":"T1"}],"gates":[],"requirements":[{"id":"REQ-1","status":"VERIFIED","owner":"po"}],"decisions":[{"id":"DEC-1","status":"DECIDED","authority_ref":"PO"}],"raid":[{"id":"RISK-1","kind":"risk","status":"OPEN","owner":"pm"}],"changes":[],"evidence":[{"id":"EVID-1","type":"test-result","artifact_ref":"A1"}],"releases":[{"id":"REL-1","status":"RELEASED","evidence_refs":["EVID-1"]}],"deployments":[{"id":"DEPLOY-1","status":"SUCCEEDED","release_ref":"REL-1","environment_ref":"PROD","validation_evidence_refs":["EVID-1"]}],"trace_links":[{"source_ref":"REQ-1","target_ref":"T1","relationship":"implemented_by"},{"source_ref":"REQ-1","target_ref":"EVID-1","relationship":"verified_by"},{"source_ref":"REL-1","target_ref":"DEPLOY-1","relationship":"deployed_as"}]}
  def test_valid_control(self): self.assertEqual(project_control.validate_project_control(self.bundle()),[])
  def test_requirement_orphan(self):
    b=self.bundle(); b["trace_links"]=[]; codes={x.code for x in project_control.validate_project_control(b)}; self.assertIn("CTRL-TRACE-REQ-001",codes); self.assertIn("CTRL-TRACE-REQ-002",codes)
  def test_decided_requires_authority(self):
    b=self.bundle(); del b["decisions"][0]["authority_ref"]; self.assertTrue(any(x.code=="CTRL-DEC-002" for x in project_control.validate_project_control(b)))
  def test_accepted_risk_requires_decision(self):
    b=self.bundle(); b["raid"][0]["status"]="ACCEPTED"; self.assertTrue(any(x.code=="CTRL-RAID-003" for x in project_control.validate_project_control(b)))
  def test_material_change_requires_decision(self):
    b=self.bundle(); b["changes"]=[{"id":"CHG-1","status":"APPROVED","material":True}]; self.assertTrue(any(x.code=="CTRL-CHG-002" for x in project_control.validate_project_control(b)))
  def test_release_requires_evidence(self):
    b=self.bundle(); b["releases"][0]["evidence_refs"]=[]; self.assertTrue(any(x.code=="CTRL-REL-002" for x in project_control.validate_project_control(b)))
  def test_deployment_requires_validation(self):
    b=self.bundle(); b["deployments"][0]["validation_evidence_refs"]=[]; self.assertTrue(any(x.code=="CTRL-DEPLOY-002" for x in project_control.validate_project_control(b)))
  def test_traceability_summary(self):
    s=project_control.traceability_summary(self.bundle()); self.assertEqual(s["implementation_coverage"],1.0); self.assertEqual(s["verification_coverage"],1.0)
