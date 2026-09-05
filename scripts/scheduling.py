#!/usr/bin/env python3
"""Scheduling and dispatch helpers for Project Orchestrator v2.

CHG-004 provides deterministic planning primitives. It does not execute work.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import Any

PRIORITY_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
READY_ENV_STATES = {"READY", "DEGRADED"}
TERMINAL_WORK_STATES = {"DONE", "CANCELLED", "SUPERSEDED"}

@dataclass(frozen=True)
class DispatchDecision:
    selected: list[str]
    deferred: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def _duration_hours(duration: Any) -> float | None:
    if not isinstance(duration, dict):
        return None
    value = duration.get("value")
    unit = duration.get("unit")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        return None
    return float(value) * {"minutes": 1/60, "hours": 1, "days": 24}.get(unit, 0) if unit in {"minutes","hours","days"} else None

def _work_map(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {w["id"]: w for w in bundle.get("work_items", []) if isinstance(w, dict) and isinstance(w.get("id"), str)}

def _env_map(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {e["id"]: e for e in bundle.get("environments", []) if isinstance(e, dict) and isinstance(e.get("id"), str)}

def _hard_work_edges(bundle: dict[str, Any]) -> list[tuple[str, str, str]]:
    edges=[]
    for dep in bundle.get("dependencies", []):
        if not isinstance(dep, dict) or dep.get("strength", "HARD") != "HARD":
            continue
        pred, succ = dep.get("predecessor"), dep.get("successor")
        if isinstance(pred, dict) and isinstance(succ, dict) and pred.get("kind")=="work" and succ.get("kind")=="work":
            edges.append((pred.get("id"), succ.get("id"), dep.get("relationship","FS")))
    return [(a,b,r) for a,b,r in edges if isinstance(a,str) and isinstance(b,str)]

def environment_ready_for(work: dict[str, Any], bundle: dict[str, Any]) -> tuple[bool, str | None]:
    refs = work.get("environment_refs", [])
    if not refs:
        return True, None
    envs = _env_map(bundle)
    for ref in refs:
        env = envs.get(ref)
        if env is None:
            return False, f"environment {ref} is not defined"
        if env.get("state") not in READY_ENV_STATES:
            return False, f"environment {ref} is {env.get('state')}"
    return True, None

def ready_queue(bundle: dict[str, Any]) -> list[str]:
    """Return READY work in deterministic planning order.

    READY is eligibility, not execution. Environment readiness is applied here
    because CHG-003 intentionally did not own environment semantics.
    """
    candidates=[]
    for work in bundle.get("work_items", []):
        if not isinstance(work, dict) or work.get("state") != "READY":
            continue
        ok, _ = environment_ready_for(work, bundle)
        if not ok:
            continue
        priority = str(work.get("priority","")).upper()
        forecast = (work.get("schedule") or {}).get("forecast") or {}
        finish = forecast.get("finish") or "9999-12-31T23:59:59+00:00"
        candidates.append((PRIORITY_RANK.get(priority, 50), finish, work.get("id","")))
    candidates.sort()
    return [x[2] for x in candidates]

def dispatch_plan(bundle: dict[str, Any], capacity: int | None = None) -> DispatchDecision:
    """Select a conflict-free subset from the Ready Queue.

    This planner respects a simple executor single-flight rule and exclusive
    resource refs. It does not start work or claim authority.
    """
    queue = ready_queue(bundle)
    if capacity is None:
        project = bundle.get("project", {})
        capacity = int(project.get("dispatch_capacity", len(queue) or 1))
    capacity = max(0, capacity)
    works = _work_map(bundle)
    selected=[]
    deferred={}
    busy_executors=set()
    busy_resources=set()
    for wid in queue:
        if len(selected) >= capacity:
            deferred[wid] = "capacity"
            continue
        work=works[wid]
        executor = work.get("executor") or {}
        executor_key = None
        if executor.get("id") and not work.get("allow_executor_parallel", False):
            executor_key=(executor.get("type"), executor.get("id"))
        resources=set(work.get("exclusive_resource_refs", []) or [])
        if executor_key and executor_key in busy_executors:
            deferred[wid]="executor-conflict"
            continue
        if resources & busy_resources:
            deferred[wid]="resource-conflict"
            continue
        selected.append(wid)
        if executor_key:
            busy_executors.add(executor_key)
        busy_resources |= resources
    return DispatchDecision(selected=selected, deferred=deferred)

def _topological_work_order(bundle: dict[str, Any]) -> tuple[list[str] | None, str | None]:
    works=_work_map(bundle)
    indegree={wid:0 for wid in works}
    succ={wid:[] for wid in works}
    for a,b,_ in _hard_work_edges(bundle):
        if a in works and b in works:
            indegree[b]+=1
            succ[a].append(b)
    q=sorted([wid for wid,d in indegree.items() if d==0])
    order=[]
    while q:
        n=q.pop(0)
        order.append(n)
        for s in sorted(succ[n]):
            indegree[s]-=1
            if indegree[s]==0:
                q.append(s); q.sort()
    if len(order)!=len(works):
        return None, "hard dependency graph contains a cycle"
    return order, None

def critical_path(bundle: dict[str, Any]) -> dict[str, Any]:
    """Compute a simple longest path when estimates and HARD FS edges suffice."""
    works=_work_map(bundle)
    non_fs=[r for _,_,r in _hard_work_edges(bundle) if r!="FS"]
    if non_fs:
        return {"available": False, "reason": "critical-path MVP supports HARD FS dependencies only"}
    durations={}
    for wid,w in works.items():
        h=_duration_hours((w.get("schedule") or {}).get("estimate"))
        if h is None:
            return {"available": False, "reason": f"missing/invalid estimate for {wid}"}
        durations[wid]=h
    order, reason=_topological_work_order(bundle)
    if order is None:
        return {"available": False, "reason": reason}
    preds={wid:[] for wid in works}
    for a,b,_ in _hard_work_edges(bundle):
        if a in works and b in works:
            preds[b].append(a)
    finish={}
    parent={}
    for wid in order:
        if preds[wid]:
            p=max(preds[wid], key=lambda x: finish[x])
            start=finish[p]
            parent[wid]=p
        else:
            start=0.0
        finish[wid]=start+durations[wid]
    if not finish:
        return {"available": True, "duration_hours":0.0, "work_ids":[]}
    end=max(finish, key=finish.get)
    path=[]
    cur=end
    while True:
        path.append(cur)
        if cur not in parent: break
        cur=parent[cur]
    path.reverse()
    return {"available": True, "duration_hours":finish[end], "work_ids":path}

def forecast_schedule(bundle: dict[str, Any], start: str | None = None) -> dict[str, dict[str, str]] | dict[str, Any]:
    """Derive simple forecast dates without mutating baseline or source bundle."""
    cp=critical_path(bundle)
    if not cp.get("available"):
        return {"available": False, "reason": cp.get("reason")}
    works=_work_map(bundle)
    order,_=_topological_work_order(bundle)
    if start:
        dt=datetime.fromisoformat(start.replace("Z","+00:00"))
    else:
        dt=datetime.now(timezone.utc)
    preds={wid:[] for wid in works}
    for a,b,r in _hard_work_edges(bundle):
        if r=="FS" and a in works and b in works:
            preds[b].append(a)
    finish_dt={}
    out={}
    for wid in order or []:
        begin=max((finish_dt[p] for p in preds[wid]), default=dt)
        hours=_duration_hours((works[wid].get("schedule") or {}).get("estimate")) or 0
        end=begin+timedelta(hours=hours)
        finish_dt[wid]=end
        out[wid]={"start":begin.isoformat(), "finish":end.isoformat()}
    return out
