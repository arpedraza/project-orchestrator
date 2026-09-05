#!/usr/bin/env python3
"""Run one deterministic Project Orchestrator v2 control-plane iteration."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from markdown_records import sync_state, RecordError
from control_loop import run_iteration


def _load(path:Path)->dict:
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise ValueError(f"expected JSON object in {path}")
    return value

def main()->int:
    p=argparse.ArgumentParser(description="Run one Project Orchestrator v2 control-plane iteration")
    p.add_argument("--root",default=".")
    p.add_argument("--state",default=None)
    p.add_argument("--registry",default=None)
    p.add_argument("--policy",default=None)
    p.add_argument("--output",default=None)
    args=p.parse_args(); root=Path(args.root).resolve()
    source_root=Path(__file__).resolve().parent.parent
    try:
        if args.state:
            bundle=_load(Path(args.state))
        elif (root/"docs").exists():
            bundle=sync_state(root)
        else:
            bundle=_load(root/".orchestrator/state/state.json")
        registry_path=Path(args.registry) if args.registry else root/".orchestrator/registry/capability-registry.json"
        registry=_load(registry_path)
        policy_path=Path(args.policy) if args.policy else source_root/"profiles/default-policy.json"
        policy=_load(policy_path)
        result=run_iteration(bundle,registry,policy)
        target=Path(args.output) if args.output else root/".orchestrator/state/orchestration.json"
        target.parent.mkdir(parents=True,exist_ok=True); target.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps(result,indent=2,sort_keys=True))
        return 1 if not result["valid"] else 0
    except (OSError,ValueError,json.JSONDecodeError,RecordError) as exc:
        print(f"orchestrate-project: {exc}")
        return 2
if __name__=="__main__": raise SystemExit(main())
