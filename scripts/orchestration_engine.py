#!/usr/bin/env python3
"""Deterministic orchestration control-plane snapshot for Project Orchestrator v2.

This module decides what is eligible/recommended. It never invokes specialists or
changes canonical project state by itself.
"""
from __future__ import annotations
from copy import deepcopy
from typing import Any

from state_model import validate_state_bundle
from lifecycle_engine import validate_lifecycle
from project_control import validate_project_control
from scheduling import ready_queue, dispatch_plan, critical_path

ACTION_RANK={"A0":0,"A1":1,"A2":2,"A3":3,"A4":4}
PRODUCTION_CLASSES={"production","prod"}

def _cap_ids(specialist:dict[str,Any])->set[str]:
    return {str(c.get("id")) for c in specialist.get("capabilities",[]) or [] if isinstance(c,dict) and c.get("id")}

def _provenance_score(specialist:dict[str,Any], required:set[str], preferred:set[str])->tuple[int,int,int,str]:
    provenance={"declared":4,"known-specialist":3,"role-hint":2,"inferred":1}
    caps={c.get("id"):c for c in specialist.get("capabilities",[]) or [] if isinstance(c,dict)}
    required_score=sum(provenance.get((caps.get(c) or {}).get("provenance"),0) for c in required)
    preferred_hits=sum(1 for c in preferred if c in caps)
    health_score={"AVAILABLE":2,"DEGRADED":1}.get(specialist.get("health"),0)
    return (-required_score,-preferred_hits,-health_score,str(specialist.get("specialist_id","")))

def _is_production_work(work:dict[str,Any],bundle:dict[str,Any])->bool:
    env_map={e.get("id"):e for e in bundle.get("environments",[]) or [] if isinstance(e,dict)}
    for ref in work.get("environment_refs",[]) or []:
        env=env_map.get(ref) or {}
        if str(env.get("class","")).lower() in PRODUCTION_CLASSES: return True
    return str(work.get("action_class","A1"))=="A4"

def authority_check(work:dict[str,Any],specialist:dict[str,Any]|None,policy:dict[str,Any],bundle:dict[str,Any])->tuple[bool,str|None]:
    action=str(work.get("action_class","A1"))
    if action not in ACTION_RANK: return False,f"unknown action class {action}"
    if _is_production_work(work,bundle) and str(policy.get("production_approval","HUMAN")).upper()=="HUMAN" and not work.get("approval_ref"):
        return False,"production/high-impact work requires human approval_ref"
    if specialist is None: return True,None
    trust=((specialist.get("trust") or {}).get("classification") or "UNKNOWN").upper()
    if trust=="QUARANTINED": return False,"specialist is quarantined"
    if trust=="UNKNOWN":
        maximum=str(policy.get("unknown_trust_max_action_class","A0"))
        if ACTION_RANK[action] > ACTION_RANK.get(maximum,0):
            return False,f"UNKNOWN trust is permitted only through {maximum}"
    return True,None

def eligible_candidates(work:dict[str,Any],registry:dict[str,Any],policy:dict[str,Any],bundle:dict[str,Any])->tuple[list[dict[str,Any]],list[str]]:
    required=set(map(str,work.get("required_capabilities",[]) or [])); preferred=set(map(str,work.get("preferred_capabilities",[]) or []))
    allowed_health=set(policy.get("allowed_health",["AVAILABLE"]))
    reasons=[]; candidates=[]
    for specialist in registry.get("specialists",[]) or []:
        sid=specialist.get("specialist_id")
        if specialist.get("health") not in allowed_health: continue
        caps=_cap_ids(specialist)
        if not required.issubset(caps): continue
        supported_env=set(map(str,specialist.get("supported_environments",[]) or []))
        if supported_env and any(e not in supported_env for e in work.get("environment_refs",[]) or []): continue
        ok,reason=authority_check(work,specialist,policy,bundle)
        if not ok:
            reasons.append(f"{sid}: {reason}"); continue
        candidates.append(specialist)
    candidates.sort(key=lambda s:_provenance_score(s,required,preferred))
    return candidates,reasons

def orchestration_snapshot(bundle:dict[str,Any],registry:dict[str,Any],policy:dict[str,Any])->dict[str,Any]:
    findings=[]
    for f in validate_state_bundle(bundle): findings.append(f.to_dict())
    for f in validate_lifecycle(bundle): findings.append(f.to_dict())
    for f in validate_project_control(bundle): findings.append(f.to_dict())
    errors=[f for f in findings if f.get("severity")=="ERROR"]
    ready=ready_queue(bundle) if not errors else []
    works={w.get("id"):w for w in bundle.get("work_items",[]) or [] if isinstance(w,dict)}
    assignments={}; gaps=[]; authority_blocks=[]
    planned=deepcopy(bundle); planned_works={w.get("id"):w for w in planned.get("work_items",[]) or [] if isinstance(w,dict)}
    for wid in ready:
        work=works[wid]
        assigned=work.get("executor")
        if assigned:
            ok,reason=authority_check(work,None,policy,bundle)
            if ok: assignments[wid]={"executor":assigned,"source":"existing-assignment"}
            else: authority_blocks.append({"work_id":wid,"reason":reason}); continue
        else:
            candidates,reasons=eligible_candidates(work,registry,policy,bundle)
            if candidates:
                top=candidates[0]
                executor={"type":"agent","id":top["specialist_id"]}
                assignments[wid]={"executor":executor,"source":"capability-match","alternatives":[x["specialist_id"] for x in candidates[1:4]]}
                planned_works[wid]["executor"]=executor
            else:
                required=work.get("required_capabilities",[]) or []
                gaps.append({"work_id":wid,"required_capabilities":required,"reasons":reasons or ["no eligible specialist covers all required capabilities"],"recovery":"capability-gap"})
    dispatchable=set(assignments)
    for w in planned.get("work_items",[]) or []:
        if w.get("state")=="READY" and w.get("id") not in dispatchable:
            w["state"]="PROPOSED"  # planning-copy only: exclude non-dispatchable work
    dispatch=dispatch_plan(planned).to_dict() if not errors else {"selected":[],"deferred":{}}
    decisions=[]
    for item in authority_blocks:
        decisions.append({"type":"DECISION_REQUIRED","work_id":item["work_id"],"reason":item["reason"],"recommendation":"Obtain required approval or reassign/re-scope within policy."})
    for gap in gaps:
        decisions.append({"type":"CAPABILITY_GAP","work_id":gap["work_id"],"reason":gap["reasons"],"recommendation":"Inspect/decompose/compose/human-execute/discover candidate specialist according to policy."})
    return {
      "valid":not errors,
      "findings":findings,
      "ready_queue":ready,
      "assignments":assignments,
      "dispatch":dispatch,
      "capability_gaps":gaps,
      "authority_blocks":authority_blocks,
      "decisions":decisions,
      "critical_path":critical_path(bundle) if not errors else {"available":False,"reason":"state validation errors"},
    }
