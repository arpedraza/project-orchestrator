#!/usr/bin/env python3
"""Produce a deterministic planning snapshot from a v2 State Bundle."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from scheduling import ready_queue, dispatch_plan, critical_path, forecast_schedule
from lifecycle_engine import validate_lifecycle, evaluate_cross_cutting


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("state_bundle")
    p.add_argument("--capacity",type=int,default=None)
    p.add_argument("--forecast-start",default=None)
    p.add_argument("--cross-cutting-profile",default=None)
    args=p.parse_args()
    bundle=json.loads(Path(args.state_bundle).read_text(encoding="utf-8"))
    result={
      "ready_queue":ready_queue(bundle),
      "dispatch":dispatch_plan(bundle,args.capacity).to_dict(),
      "critical_path":critical_path(bundle),
      "forecast":forecast_schedule(bundle,args.forecast_start),
      "lifecycle_findings":[f.to_dict() for f in validate_lifecycle(bundle)],
      "cross_cutting":[],
    }
    if args.cross_cutting_profile:
        profile=json.loads(Path(args.cross_cutting_profile).read_text(encoding="utf-8"))
        flags=(bundle.get("project") or {}).get("feature_flags",{})
        for event in bundle.get("events",[]):
            result["cross_cutting"].extend(evaluate_cross_cutting(event,profile,flags))
    print(json.dumps(result,indent=2,sort_keys=True))
    return 1 if any(x["severity"]=="ERROR" for x in result["lifecycle_findings"]) else 0

if __name__=="__main__":
    raise SystemExit(main())
