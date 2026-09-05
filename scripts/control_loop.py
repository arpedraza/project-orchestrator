#!/usr/bin/env python3
"""One full v2 control iteration including derived state-progression recommendations."""
from __future__ import annotations
from copy import deepcopy
from typing import Any

from orchestration_engine import orchestration_snapshot
from lifecycle_engine import environment_ready_for if False else None


def _work_index(bundle): return {w.get("id"):w for w in bundle.get("work_items",[]) or [] if isinstance(w,dict)}
def _gate_index(bundle): return {g.get("id"):g for g in bundle.get("gates",[]) or [] if isinstance(g,dict)}
def _decision_index(bundle): return {d.get("id"):d for d in bundle.get("decisions",[]) or [] if isinstance(d,dict)}
def _env_index(bundle): return {e.get("id"):e for e in bundle.get("environments",[]) or [] if isinstance(e,dict)}

def _derived_dependency_status(dep:dict[str,Any],bundle:dict[str,Any])->str|None:
    if dep.get("status")=="WAIVED": return "WAIVED"
    pred=dep.get("predecessor") or {}; kind=pred.get("kind"); rid=pred.get("id")
    if not kind or not rid: return None
    if kind=="work":
        work=_work_index(bundle).get(rid)
        if not work: return None
        relation=dep.get("relationship","FS")
        state=work.get("state")
        if state in {"CANCELLED","SUPERSEDED"}: return "BROKEN"
        if relation in {"FS","FF"}: return "SATISFIED" if state=="DONE" else "UNSATISFIED"
        if relation in {"SS","SF"}: return "SATISFIED" if state in {"IN_PROGRESS","NEEDS_REVIEW","DONE"} else "UNSATISFIED"
    if kind=="gate":
        gate=_gate_index(bundle).get(rid)
        if not gate: return None
        return "SATISFIED" if gate.get("validity")=="VALID" and gate.get("status") in {"PASSED","WAIVED"} else "UNSATISFIED"
    if kind=="decision":
        decision=_decision_index(bundle).get(rid)
        if not decision: return None
        return "SATISFIED" if decision.get("status")=="DECIDED" else "UNSATISFIED"
    if kind=="environment":
        env=_env_index(bundle).get(rid)
        if not env: return None
        return "SATISFIED" if env.get("state") in {"READY","DEGRADED"} else "UNSATISFIED"
    return None

def prepare_iteration(bundle:dict[str,Any])->tuple[dict[str,Any],list[dict[str,Any]],set[str]]:
    """Create a planning copy with safe derived dependency statuses and provisional READY states."""
    planned=deepcopy(bundle); recommendations=[]; originally_proposed=set()
    for dep in planned.get("dependencies",[]) or []:
        if not isinstance(dep,dict): continue
        derived=_derived_dependency_status(dep,planned)
        if derived and derived!=dep.get("status"):
            recommendations.append({"record_type":"dependency","id":dep.get("id"),"field":"status","from":dep.get("status"),"to":derived,"reason":"derived-from-predecessor-state"})
            dep["status"]=derived
    incoming={w.get("id"):[] for w in planned.get("work_items",[]) or [] if isinstance(w,dict)}
    for dep in planned.get("dependencies",[]) or []:
        if not isinstance(dep,dict) or dep.get("strength","HARD")!="HARD": continue
        succ=dep.get("successor") or {}
        if succ.get("kind")=="work" and succ.get("id") in incoming: incoming[succ["id"]].append(dep)
    envs=_env_index(planned); gates=_gate_index(planned)
    for work in planned.get("work_items",[]) or []:
        if not isinstance(work,dict) or work.get("state")!="PROPOSED": continue
        wid=work.get("id"); originally_proposed.add(wid)
        hard_ok=all(d.get("status") in {"SATISFIED","WAIVED","AT_RISK"} for d in incoming.get(wid,[]))
        env_ok=all((envs.get(e) or {}).get("state") in {"READY","DEGRADED"} for e in work.get("environment_refs",[]) or [])
        start_gates=work.get("start_gate_refs",[]) or []
        gates_ok=all((gates.get(g) or {}).get("validity")=="VALID" and (gates.get(g) or {}).get("status") in {"PASSED","WAIVED"} for g in start_gates)
        if hard_ok and env_ok and gates_ok:
            work["state"]="READY"
    return planned,recommendations,originally_proposed

def run_iteration(bundle:dict[str,Any],registry:dict[str,Any],policy:dict[str,Any])->dict[str,Any]:
    planned,recommendations,originally_proposed=prepare_iteration(bundle)
    result=orchestration_snapshot(planned,registry,policy)
    gap_ids={g.get("work_id") for g in result.get("capability_gaps",[])}
    decision_ids={d.get("work_id") for d in result.get("decisions",[]) if d.get("type")=="DECISION_REQUIRED"}
    for wid in sorted(originally_proposed):
        work=next((w for w in planned.get("work_items",[]) or [] if w.get("id")==wid),None)
        if not work or work.get("state")!="READY": continue
        if wid in decision_ids:
            target="NEEDS_DECISION"; reason="authority-required"
        elif wid in gap_ids:
            reasons=next((g.get("reasons",[]) for g in result.get("capability_gaps",[]) if g.get("work_id")==wid),[])
            target="NEEDS_DECISION" if any("approval" in str(r).lower() or "authority" in str(r).lower() for r in reasons) else "BLOCKED"
            reason="capability-or-authority-gap"
        else:
            target="READY"; reason="start-conditions-satisfied"
        recommendations.append({"record_type":"work","id":wid,"field":"state","from":"PROPOSED","to":target,"reason":reason})
    result["state_recommendations"]=recommendations
    return result
