import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"scripts"))
from orchestration_engine import eligible_candidates, orchestration_snapshot


def registry():
    return {"specialists":[
      {"specialist_id":"local:dev","health":"AVAILABLE","trust":{"classification":"UNKNOWN"},"capabilities":[{"id":"development","provenance":"declared"},{"id":"code-review","provenance":"role-hint"}],"supported_environments":[]},
      {"specialist_id":"local:review","health":"AVAILABLE","trust":{"classification":"TRUSTED_CATALOG"},"capabilities":[{"id":"code-review","provenance":"declared"}],"supported_environments":[]},
      {"specialist_id":"local:bad","health":"QUARANTINED","trust":{"classification":"QUARANTINED"},"capabilities":[{"id":"development","provenance":"declared"}],"supported_environments":[]}
    ]}

def policy():
    return {"allowed_health":["AVAILABLE","DEGRADED"],"unknown_trust_max_action_class":"A1","production_approval":"HUMAN"}

def bundle():
    return {"schema_version":"1.0","project":{"project_id":"P","name":"Demo","objective":"Demo","status":"ACTIVE","reporting_stage":"BUILD"},"work_items":[
      {"id":"T1","type":"Task","title":"Build","objective":"Build","reporting_stage":"BUILD","state":"READY","priority":"HIGH","required_capabilities":["development"],"action_class":"A1","schedule":{"estimate":{"value":1,"unit":"hours"}}},
      {"id":"T2","type":"Task","title":"Review","objective":"Review","reporting_stage":"VALIDATE","state":"READY","priority":"MEDIUM","required_capabilities":["code-review"],"action_class":"A1","schedule":{"estimate":{"value":1,"unit":"hours"}}}
    ],"dependencies":[],"gates":[]}

class OrchestrationEngineTests(unittest.TestCase):
    def test_candidate_matching(self):
        b=bundle(); c,reasons=eligible_candidates(b["work_items"][0],registry(),policy(),b)
        self.assertEqual(c[0]["specialist_id"],"local:dev"); self.assertEqual(reasons,[])
    def test_declared_preferred_ranking(self):
        b=bundle(); c,_=eligible_candidates(b["work_items"][1],registry(),policy(),b)
        self.assertEqual(c[0]["specialist_id"],"local:review")
    def test_missing_capability_gap(self):
        b=bundle(); b["work_items"][0]["required_capabilities"]=["nonexistent"]
        s=orchestration_snapshot(b,registry(),policy())
        self.assertEqual(s["capability_gaps"][0]["work_id"],"T1")
        self.assertNotIn("T1",s["dispatch"]["selected"])
    def test_unknown_trust_blocked_high_impact(self):
        b=bundle(); b["work_items"][0]["action_class"]="A3"
        s=orchestration_snapshot(b,registry(),policy())
        self.assertEqual(s["capability_gaps"][0]["work_id"],"T1")
        self.assertTrue(any("UNKNOWN trust" in r for r in s["capability_gaps"][0]["reasons"]))
    def test_production_requires_approval(self):
        b=bundle(); b["environments"]=[{"id":"PROD","name":"Prod","class":"production","purpose":"prod","state":"READY","promotion_to":[]}]; b["work_items"][0]["environment_refs"]=["PROD"]
        s=orchestration_snapshot(b,registry(),policy())
        self.assertTrue(any(x["work_id"]=="T1" for x in s["capability_gaps"]))
    def test_production_with_approval_can_match(self):
        b=bundle(); b["environments"]=[{"id":"PROD","name":"Prod","class":"production","purpose":"prod","state":"READY","promotion_to":[]}]; b["work_items"][0]["environment_refs"]=["PROD"]; b["work_items"][0]["approval_ref"]="DEC-PROD"
        # UNKNOWN trust still supports only A1, so this local reversible task can be planned after explicit approval.
        s=orchestration_snapshot(b,registry(),policy())
        self.assertIn("T1",s["assignments"])
    def test_valid_snapshot_dispatches_matches(self):
        s=orchestration_snapshot(bundle(),registry(),policy())
        self.assertTrue(s["valid"]); self.assertEqual(set(s["assignments"]),{"T1","T2"}); self.assertEqual(set(s["dispatch"]["selected"]),{"T1","T2"})
    def test_invalid_state_stops_dispatch(self):
        b=bundle(); b["work_items"][0]["state"]="NOPE"
        s=orchestration_snapshot(b,registry(),policy())
        self.assertFalse(s["valid"]); self.assertEqual(s["dispatch"]["selected"],[])

if __name__=="__main__": unittest.main()
