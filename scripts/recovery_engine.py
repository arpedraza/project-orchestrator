#!/usr/bin/env python3
"""Recovery/change-control primitives for Project Orchestrator v2."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

FAILURE_CLASSES={"transient","defect","environmental","capability","assumption","authority","incident","nonblocking"}
RECOVERY_ACTIONS={"retry","rework","infrastructure","capability-gap","replan","escalate","incident-response","park","recovery-review"}

@dataclass(frozen=True)
class RecoveryPlan:
    failure_class: str
    action: str
    autonomous: bool
    reason: str
    next_state: str | None = None
    escalation: dict[str,Any] | None = None
    def to_dict(self): return asdict(self)

def classify_failure(event: dict[str,Any]) -> str:
    explicit=event.get("failure_class")
    if explicit in FAILURE_CLASSES: return explicit
    tags={str(x).lower() for x in event.get("tags",[]) or []}
    kind=str(event.get("kind","")).lower()
    if "timeout" in tags or "rate-limit" in tags or "transient" in tags: return "transient"
    if "test-failure" in tags or "defect" in tags or kind=="qa-failure": return "defect"
    if "environment" in tags or "infra" in tags or "credential" in tags: return "environmental"
    if "capability" in tags or "missing-skill" in tags: return "capability"
    if "assumption" in tags or kind=="assumption-invalidated": return "assumption"
    if "approval" in tags or "authority" in tags or kind=="decision-required": return "authority"
    if "incident" in tags or kind=="incident": return "incident"
    if event.get("blocking") is False: return "nonblocking"
    return "defect"

def decision_package(work_ref:str, reason:str, options:list[dict[str,Any]], recommendation:str, authority:str, blocked_scope:list[str]|None=None, unaffected:list[str]|None=None)->dict[str,Any]:
    return {
      "work_ref":work_ref,"reason":reason,"options":options,"recommendation":recommendation,
      "required_authority":authority,"blocked_scope":blocked_scope or [work_ref],"unaffected_work":unaffected or []
    }

def plan_recovery(event:dict[str,Any], *, attempts:int=0, max_attempts:int=2, within_authority:bool=True)->RecoveryPlan:
    cls=classify_failure(event)
    if attempts>=max_attempts and cls in {"transient","defect","environmental"}:
        return RecoveryPlan(cls,"recovery-review",False,"Recovery budget exhausted.","NEEDS_DECISION",
            decision_package(event.get("work_ref","unknown"),"Recovery budget exhausted.",
                [{"option":"alternate-executor"},{"option":"replan"},{"option":"accept/park if policy permits"}],
                "Review alternate executor or replan.","project-owner"))
    if cls=="transient":
        return RecoveryPlan(cls,"retry",within_authority,"Transient failure within recovery budget.","WAITING" if within_authority else "NEEDS_DECISION")
    if cls=="defect":
        return RecoveryPlan(cls,"rework",within_authority,"Output failed acceptance/quality.","NEEDS_REWORK" if within_authority else "NEEDS_DECISION")
    if cls=="environmental":
        return RecoveryPlan(cls,"infrastructure",within_authority,"Environment/runtime prerequisite failed.","BLOCKED")
    if cls=="capability":
        return RecoveryPlan(cls,"capability-gap",within_authority,"No eligible capability/executor available.","BLOCKED")
    if cls=="assumption":
        return RecoveryPlan(cls,"replan",within_authority,"An approved planning assumption is invalid.","NEEDS_REWORK" if within_authority else "NEEDS_DECISION")
    if cls=="incident":
        return RecoveryPlan(cls,"incident-response",within_authority,"Operational incident requires containment/recovery.","BLOCKED")
    if cls=="nonblocking":
        return RecoveryPlan(cls,"park",within_authority,"Failure is nonblocking and may be deferred by policy.","PARKED")
    pkg=decision_package(event.get("work_ref","unknown"),event.get("message","Authority/decision required."),
        event.get("options") or [{"option":"approve"},{"option":"reject/defer"}],
        event.get("recommendation","Review and decide."),event.get("required_authority","project-owner"))
    return RecoveryPlan(cls,"escalate",False,"Resolution exceeds delegated authority.","NEEDS_DECISION",pkg)
