#!/usr/bin/env python3
"""Canonical project-control and traceability validation for v2."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

REQ_STATES={"PROPOSED","ANALYZED","APPROVED","IMPLEMENTED","VERIFIED","ACCEPTED","DEFERRED","REJECTED","SUPERSEDED","CANCELLED"}
DEC_STATES={"OPEN","DEFERRED","DECIDED","SUPERSEDED","CANCELLED"}
RISK_STATES={"OPEN","MITIGATING","MONITORING","ACCEPTED","CLOSED"}
ASSUMPTION_STATES={"UNVALIDATED","VALIDATED","INVALIDATED","EXPIRED"}
ISSUE_STATES={"OPEN","IN_PROGRESS","RESOLVED","CLOSED"}
CHANGE_STATES={"PROPOSED","ASSESSING","APPROVED","REJECTED","IMPLEMENTED","CLOSED"}
RELEASE_STATES={"PLANNED","ASSEMBLING","CANDIDATE","VALIDATING","APPROVED","RELEASED","REJECTED","ROLLED_BACK","SUPERSEDED","CANCELLED"}
DEPLOYMENT_STATES={"PLANNED","READY","IN_PROGRESS","SUCCEEDED","FAILED","ROLLED_BACK","CANCELLED"}
RELATIONSHIPS={"implements","implemented_by","verifies","verified_by","evidences","depends_on","blocks","mitigates","caused_by","addresses","supersedes","derived_from","affects","introduced_by","released_in","deployed_as","accepted_by","waived_by"}

@dataclass(frozen=True)
class ControlFinding:
    severity:str; code:str; message:str; path:str=""
    def to_dict(self): return asdict(self)
def _f(code,msg,path="",severity="ERROR"): return ControlFinding(severity,code,msg,path)

def _records(bundle:dict[str,Any])->dict[str,dict[str,Any]]:
    result={}
    for family in ("requirements","decisions","raid","changes","evidence","releases","deployments"):
        for r in bundle.get(family,[]) or []:
            if isinstance(r,dict) and isinstance(r.get("id"),str): result[r["id"]]=r
    for w in bundle.get("work_items",[]) or []:
        if isinstance(w,dict) and isinstance(w.get("id"),str): result[w["id"]]=w
    for g in bundle.get("gates",[]) or []:
        if isinstance(g,dict) and isinstance(g.get("id"),str): result[g["id"]]=g
    return result

def validate_project_control(bundle:dict[str,Any])->list[ControlFinding]:
    findings=[]; seen=set()
    families={"requirements":"requirement","decisions":"decision","raid":"raid","changes":"change","evidence":"evidence","releases":"release","deployments":"deployment"}
    for family,label in families.items():
        vals=bundle.get(family,[]) or []
        if not isinstance(vals,list): findings.append(_f("CTRL-FAMILY-001",f"{family} must be an array.",family)); continue
        for i,r in enumerate(vals):
            p=f"{family}[{i}]"
            if not isinstance(r,dict): findings.append(_f("CTRL-REC-001",f"{label} record must be an object.",p)); continue
            rid=r.get("id")
            if not isinstance(rid,str) or not rid: findings.append(_f("CTRL-ID-001","Record id must be non-empty.",p+".id"))
            elif rid in seen: findings.append(_f("CTRL-ID-002",f"Duplicate project-control id {rid}.",p+".id"))
            else: seen.add(rid)
    for i,r in enumerate(bundle.get("requirements",[]) or []):
        p=f"requirements[{i}]"; st=r.get("status")
        if st not in REQ_STATES: findings.append(_f("CTRL-REQ-001","Invalid requirement status.",p+".status"))
    for i,r in enumerate(bundle.get("decisions",[]) or []):
        p=f"decisions[{i}]"
        if r.get("status") not in DEC_STATES: findings.append(_f("CTRL-DEC-001","Invalid decision status.",p+".status"))
        if r.get("status")=="DECIDED" and not r.get("authority_ref"): findings.append(_f("CTRL-DEC-002","DECIDED decision requires authority_ref.",p+".authority_ref"))
    for i,r in enumerate(bundle.get("raid",[]) or []):
        p=f"raid[{i}]"; kind=r.get("kind")
        if kind=="risk":
            if r.get("status") not in RISK_STATES: findings.append(_f("CTRL-RAID-001","Invalid risk status.",p+".status"))
            if not r.get("owner"): findings.append(_f("CTRL-RAID-002","Risk requires owner.",p+".owner"))
            if r.get("status")=="ACCEPTED" and not r.get("acceptance_decision_ref"): findings.append(_f("CTRL-RAID-003","Accepted risk requires acceptance decision.",p))
        elif kind=="assumption":
            if r.get("status") not in ASSUMPTION_STATES: findings.append(_f("CTRL-RAID-004","Invalid assumption status.",p+".status"))
            if not r.get("owner") or not r.get("validation_condition"): findings.append(_f("CTRL-RAID-005","Assumption requires owner and validation_condition.",p))
        elif kind=="issue":
            if r.get("status") not in ISSUE_STATES: findings.append(_f("CTRL-RAID-006","Invalid issue status.",p+".status"))
            if not r.get("owner"): findings.append(_f("CTRL-RAID-007","Issue requires owner.",p+".owner"))
        else: findings.append(_f("CTRL-RAID-008","RAID kind must be risk, assumption, or issue.",p+".kind"))
    for i,r in enumerate(bundle.get("changes",[]) or []):
        p=f"changes[{i}]"
        if r.get("status") not in CHANGE_STATES: findings.append(_f("CTRL-CHG-001","Invalid change status.",p+".status"))
        if r.get("material",False) and r.get("status") in {"APPROVED","IMPLEMENTED","CLOSED"} and not r.get("decision_ref"): findings.append(_f("CTRL-CHG-002","Material approved/implemented change requires decision_ref.",p+".decision_ref"))
    for i,r in enumerate(bundle.get("releases",[]) or []):
        p=f"releases[{i}]"
        if r.get("status") not in RELEASE_STATES: findings.append(_f("CTRL-REL-001","Invalid release status.",p+".status"))
        if r.get("status") in {"APPROVED","RELEASED"} and not r.get("evidence_refs"): findings.append(_f("CTRL-REL-002","Approved/released release requires evidence_refs.",p+".evidence_refs"))
    for i,r in enumerate(bundle.get("deployments",[]) or []):
        p=f"deployments[{i}]"
        if r.get("status") not in DEPLOYMENT_STATES: findings.append(_f("CTRL-DEPLOY-001","Invalid deployment status.",p+".status"))
        if r.get("status")=="SUCCEEDED":
            for key in ("release_ref","environment_ref","validation_evidence_refs"):
                if not r.get(key): findings.append(_f("CTRL-DEPLOY-002",f"Successful deployment requires {key}.",p+"."+key))
    all_records=_records(bundle); links=bundle.get("trace_links",[]) or []; by_source={}
    for i,l in enumerate(links):
        p=f"trace_links[{i}]"
        if not isinstance(l,dict): findings.append(_f("CTRL-LINK-001","Trace link must be an object.",p)); continue
        s,t,rel=l.get("source_ref"),l.get("target_ref"),l.get("relationship")
        if rel not in RELATIONSHIPS: findings.append(_f("CTRL-LINK-002","Unknown relationship.",p+".relationship"))
        if s not in all_records: findings.append(_f("CTRL-LINK-003",f"Unknown source_ref {s}.",p+".source_ref"))
        if t not in all_records: findings.append(_f("CTRL-LINK-004",f"Unknown target_ref {t}.",p+".target_ref"))
        by_source.setdefault(s,[]).append(l)
    for i,r in enumerate(bundle.get("requirements",[]) or []):
        rid=r.get("id"); st=r.get("status"); rels=by_source.get(rid,[])
        if st in {"APPROVED","IMPLEMENTED","VERIFIED","ACCEPTED"} and not any(x.get("relationship") in {"implemented_by","implements"} for x in rels): findings.append(_f("CTRL-TRACE-REQ-001",f"{rid} has no implementation/work trace.",f"requirements[{i}]"))
        if st in {"VERIFIED","ACCEPTED"} and not any(x.get("relationship") in {"verified_by","verifies","evidences"} for x in rels): findings.append(_f("CTRL-TRACE-REQ-002",f"{rid} has no verification/evidence trace.",f"requirements[{i}]"))
    return findings

def traceability_summary(bundle:dict[str,Any])->dict[str,Any]:
    reqs=bundle.get("requirements",[]) or []; links=bundle.get("trace_links",[]) or []
    implementation={l.get("source_ref") for l in links if l.get("relationship") in {"implemented_by","implements"}}
    verified={l.get("source_ref") for l in links if l.get("relationship") in {"verified_by","verifies","evidences"}}
    approved=[r.get("id") for r in reqs if r.get("status") in {"APPROVED","IMPLEMENTED","VERIFIED","ACCEPTED"}]
    return {"approved_requirements":len(approved),"with_implementation":sum(1 for x in approved if x in implementation),"with_verification":sum(1 for x in approved if x in verified),"implementation_coverage":(sum(1 for x in approved if x in implementation)/len(approved) if approved else 1.0),"verification_coverage":(sum(1 for x in approved if x in verified)/len(approved) if approved else 1.0)}
