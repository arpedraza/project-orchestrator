#!/usr/bin/env python3
"""Environment, promotion, and cross-cutting trigger primitives for CHG-004."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

ENVIRONMENT_STATES={"PROPOSED","PROVISIONING","READY","DEGRADED","UNAVAILABLE","RETIRED"}
PROMOTION_STATUSES={"PROPOSED","READY","IN_PROGRESS","SUCCEEDED","FAILED","ROLLED_BACK","CANCELLED"}
PATH_TYPES={"NORMAL","HOTFIX","EMERGENCY"}
MATERIALITY_RANK={"LOW":0,"MEDIUM":1,"HIGH":2,"CRITICAL":3}
TRIGGER_MODES={"BASELINE","EVENT_TRIGGERED","MANDATORY_GATE","OPERATIONAL"}

@dataclass(frozen=True)
class LifecycleFinding:
    severity: str
    code: str
    message: str
    path: str=""
    def to_dict(self): return asdict(self)

def _f(code,msg,path="",severity="ERROR"):
    return LifecycleFinding(severity,code,msg,path)

def validate_lifecycle(bundle: dict[str,Any]) -> list[LifecycleFinding]:
    findings=[]
    envs=bundle.get("environments",[])
    promotions=bundle.get("promotions",[])
    env_map={}
    for i,e in enumerate(envs):
        p=f"environments[{i}]"
        if not isinstance(e,dict):
            findings.append(_f("LIFE-ENV-001","Environment must be an object.",p)); continue
        eid=e.get("id")
        if not isinstance(eid,str) or not eid.strip():
            findings.append(_f("LIFE-ENV-002","Environment id must be non-empty.",p+".id")); continue
        if eid in env_map:
            findings.append(_f("LIFE-ENV-003",f"Duplicate environment id {eid}.",p+".id"))
        env_map[eid]=e
        if e.get("state") not in ENVIRONMENT_STATES:
            findings.append(_f("LIFE-ENV-004",f"Invalid environment state {e.get('state')}.",p+".state"))
        for field in ("promotion_to","required_gates","required_capabilities","allowed_data_classifications"):
            if field in e and (not isinstance(e[field],list) or not all(isinstance(x,str) and x for x in e[field])):
                findings.append(_f("LIFE-ENV-005",f"{field} must be a list of non-empty strings.",p+"."+field))
    for eid,e in env_map.items():
        for target in e.get("promotion_to",[]) or []:
            if target not in env_map:
                findings.append(_f("LIFE-ENV-006",f"Environment {eid} promotes to undefined environment {target}.",f"environment:{eid}.promotion_to"))
    for i,pr in enumerate(promotions):
        p=f"promotions[{i}]"
        if not isinstance(pr,dict):
            findings.append(_f("LIFE-PROMO-001","Promotion must be an object.",p)); continue
        for key in ("id","artifact_id","source_environment","target_environment","status","path_type"):
            if not isinstance(pr.get(key),str) or not pr.get(key):
                findings.append(_f("LIFE-PROMO-002",f"{key} must be non-empty.",p+"."+key))
        source,target=pr.get("source_environment"),pr.get("target_environment")
        if source not in env_map:
            findings.append(_f("LIFE-PROMO-003",f"Unknown source environment {source}.",p+".source_environment"))
        if target not in env_map:
            findings.append(_f("LIFE-PROMO-004",f"Unknown target environment {target}.",p+".target_environment"))
        if pr.get("status") not in PROMOTION_STATUSES:
            findings.append(_f("LIFE-PROMO-005","Invalid promotion status.",p+".status"))
        if pr.get("path_type") not in PATH_TYPES:
            findings.append(_f("LIFE-PROMO-006","Invalid path_type.",p+".path_type"))
        if pr.get("path_type") in {"HOTFIX","EMERGENCY"} and not pr.get("policy_ref"):
            findings.append(_f("LIFE-PROMO-007","HOTFIX/EMERGENCY promotion requires policy_ref.",p+".policy_ref"))
        if target in env_map and pr.get("status") in {"READY","IN_PROGRESS","SUCCEEDED"} and env_map[target].get("state") not in {"READY","DEGRADED"}:
            findings.append(_f("LIFE-PROMO-008",f"Target environment {target} is not ready.",p+".target_environment"))
        if source in env_map and target in env_map:
            allowed=env_map[source].get("promotion_to",[]) or []
            if target not in allowed and pr.get("path_type")=="NORMAL":
                findings.append(_f("LIFE-PROMO-009",f"Normal promotion route {source}->{target} is not declared.",p))
        if pr.get("status")=="SUCCEEDED":
            if not pr.get("deployment_evidence_refs"):
                findings.append(_f("LIFE-PROMO-010","Succeeded promotion requires deployment evidence.",p+".deployment_evidence_refs"))
            if not pr.get("validation_evidence_refs"):
                findings.append(_f("LIFE-PROMO-011","Succeeded promotion requires validation evidence.",p+".validation_evidence_refs"))
    return findings

def evaluate_cross_cutting(event: dict[str,Any], profile: dict[str,Any], project_flags: dict[str,bool] | None=None) -> list[dict[str,Any]]:
    """Return applicable discipline triggers from a configurable profile."""
    project_flags=project_flags or {}
    materiality=event.get("materiality","LOW")
    mode=event.get("mode","EVENT_TRIGGERED")
    tags=set(event.get("tags",[]) or [])
    kind=event.get("kind")
    results=[]
    for discipline,rule in (profile.get("disciplines") or {}).items():
        if rule.get("enabled",True) is False:
            continue
        required_flag=rule.get("requires_project_flag")
        if required_flag and not project_flags.get(required_flag,False):
            continue
        modes=set(rule.get("modes",TRIGGER_MODES))
        if mode not in modes:
            continue
        min_mat=rule.get("minimum_materiality","LOW")
        if MATERIALITY_RANK.get(materiality,-1) < MATERIALITY_RANK.get(min_mat,0):
            continue
        kinds=set(rule.get("event_kinds",[]) or [])
        trigger_tags=set(rule.get("tags",[]) or [])
        if kinds and kind not in kinds and not (tags & trigger_tags):
            continue
        if not kinds and trigger_tags and not (tags & trigger_tags):
            continue
        results.append({
            "discipline": discipline,
            "mode": mode,
            "event_id": event.get("id"),
            "reason": "profile-rule-match",
        })
    return sorted(results,key=lambda x:x["discipline"])
