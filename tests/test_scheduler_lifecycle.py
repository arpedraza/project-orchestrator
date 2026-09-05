import unittest, copy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import scheduling
import lifecycle_engine

def base_bundle():
    return {
      "project":{"project_id":"P1","name":"x","objective":"o","status":"active","reporting_stage":"BUILD"},
      "work_items":[
        {"id":"A","type":"Task","title":"A","objective":"a","reporting_stage":"BUILD","state":"READY","priority":"HIGH",
         "schedule":{"estimate":{"value":2,"unit":"hours"}}, "executor":{"type":"agent","id":"e1"}, "environment_refs":["DEV"]},
        {"id":"B","type":"Task","title":"B","objective":"b","reporting_stage":"BUILD","state":"READY","priority":"CRITICAL",
         "schedule":{"estimate":{"value":2,"unit":"hours"}}, "executor":{"type":"agent","id":"e2"}, "environment_refs":["DEV"]},
        {"id":"C","type":"Task","title":"C","objective":"c","reporting_stage":"BUILD","state":"PROPOSED","priority":"LOW",
         "schedule":{"estimate":{"value":1,"unit":"hours"}}, "environment_refs":["DEV"]},
      ],
      "dependencies":[
        {"id":"D1","predecessor":{"kind":"work","id":"A"},"successor":{"kind":"work","id":"C"},"relationship":"FS","strength":"HARD","status":"UNSATISFIED"}
      ],
      "gates":[],
      "environments":[
        {"id":"DEV","name":"Dev","class":"development","purpose":"dev","state":"READY","promotion_to":["PROD"]},
        {"id":"PROD","name":"Prod","class":"production","purpose":"prod","state":"READY","promotion_to":[]},
      ]
    }

class SchedulingTests(unittest.TestCase):
    def test_ready_queue_priority(self):
        self.assertEqual(scheduling.ready_queue(base_bundle()),["B","A"])
    def test_non_ready_environment_excludes(self):
        b=base_bundle(); b["environments"][0]["state"]="UNAVAILABLE"
        self.assertEqual(scheduling.ready_queue(b),[])
    def test_dispatch_capacity(self):
        d=scheduling.dispatch_plan(base_bundle(),1)
        self.assertEqual(d.selected,["B"]); self.assertEqual(d.deferred["A"],"capacity")
    def test_executor_conflict(self):
        b=base_bundle(); b["work_items"][1]["executor"]={"type":"agent","id":"e1"}
        d=scheduling.dispatch_plan(b,2)
        self.assertEqual(len(d.selected),1); self.assertIn("executor-conflict",d.deferred.values())
    def test_resource_conflict(self):
        b=base_bundle(); b["work_items"][0]["exclusive_resource_refs"]=["db"]; b["work_items"][1]["exclusive_resource_refs"]=["db"]
        d=scheduling.dispatch_plan(b,2)
        self.assertEqual(len(d.selected),1); self.assertIn("resource-conflict",d.deferred.values())
    def test_critical_path(self):
        b=base_bundle(); b["work_items"][2]["state"]="READY"; b["dependencies"][0]["status"]="SATISFIED"
        cp=scheduling.critical_path(b)
        self.assertTrue(cp["available"]); self.assertEqual(cp["work_ids"],["A","C"]); self.assertEqual(cp["duration_hours"],3)
    def test_critical_path_missing_estimate_degrades(self):
        b=base_bundle(); del b["work_items"][0]["schedule"]
        self.assertFalse(scheduling.critical_path(b)["available"])
    def test_non_fs_degrades(self):
        b=base_bundle(); b["dependencies"][0]["relationship"]="SS"
        self.assertFalse(scheduling.critical_path(b)["available"])
    def test_forecast_does_not_mutate(self):
        b=base_bundle(); before=copy.deepcopy(b)
        out=scheduling.forecast_schedule(b,"2026-09-05T10:00:00+00:00")
        self.assertEqual(b,before); self.assertIn("A",out)

class LifecycleTests(unittest.TestCase):
    def test_valid_env(self):
        self.assertEqual(lifecycle_engine.validate_lifecycle(base_bundle()),[])
    def test_undefined_route(self):
        b=base_bundle(); b["environments"][0]["promotion_to"]=["NOPE"]
        self.assertTrue(any(f.code=="LIFE-ENV-006" for f in lifecycle_engine.validate_lifecycle(b)))
    def test_target_not_ready(self):
        b=base_bundle(); b["environments"][1]["state"]="UNAVAILABLE"
        b["promotions"]=[{"id":"P","artifact_id":"A1","source_environment":"DEV","target_environment":"PROD","status":"READY","path_type":"NORMAL"}]
        self.assertTrue(any(f.code=="LIFE-PROMO-008" for f in lifecycle_engine.validate_lifecycle(b)))
    def test_success_requires_evidence(self):
        b=base_bundle(); b["promotions"]=[{"id":"P","artifact_id":"A1","source_environment":"DEV","target_environment":"PROD","status":"SUCCEEDED","path_type":"NORMAL"}]
        codes={f.code for f in lifecycle_engine.validate_lifecycle(b)}
        self.assertIn("LIFE-PROMO-010",codes); self.assertIn("LIFE-PROMO-011",codes)
    def test_hotfix_policy(self):
        b=base_bundle(); b["promotions"]=[{"id":"P","artifact_id":"A1","source_environment":"DEV","target_environment":"PROD","status":"PROPOSED","path_type":"HOTFIX"}]
        self.assertTrue(any(f.code=="LIFE-PROMO-007" for f in lifecycle_engine.validate_lifecycle(b)))
    def test_trigger_security(self):
        profile={"disciplines":{"security":{"minimum_materiality":"MEDIUM","tags":["identity"],"modes":["EVENT_TRIGGERED"]}}}
        event={"id":"E","kind":"change","materiality":"HIGH","mode":"EVENT_TRIGGERED","tags":["identity"]}
        self.assertEqual(lifecycle_engine.evaluate_cross_cutting(event,profile)[0]["discipline"],"security")
    def test_trigger_materiality_filters(self):
        profile={"disciplines":{"security":{"minimum_materiality":"HIGH","tags":["identity"]}}}
        event={"id":"E","kind":"change","materiality":"LOW","mode":"EVENT_TRIGGERED","tags":["identity"]}
        self.assertEqual(lifecycle_engine.evaluate_cross_cutting(event,profile),[])
    def test_ai_flag(self):
        profile={"disciplines":{"ai":{"requires_project_flag":"ai","tags":["model"]}}}
        event={"id":"E","kind":"change","materiality":"HIGH","mode":"EVENT_TRIGGERED","tags":["model"]}
        self.assertEqual(lifecycle_engine.evaluate_cross_cutting(event,profile,{"ai":False}),[])
        self.assertTrue(lifecycle_engine.evaluate_cross_cutting(event,profile,{"ai":True}))
