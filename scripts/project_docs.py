#!/usr/bin/env python3
"""Markdown-first workspace and Scriber utilities for Project Orchestrator v2."""
from __future__ import annotations
import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from markdown_records import GENERATED_MARKER, RecordError, sync_state, write_record
from state_model import validate_state_bundle
from lifecycle_engine import validate_lifecycle
from project_control import validate_project_control, traceability_summary
from scheduling import ready_queue, critical_path

DOC_DIRS=[
  "00-project-control","10-requirements","20-architecture","30-decisions","40-delivery",
  "50-quality","60-releases","70-operations","80-reviews"
]
RUNTIME_DIRS=["state","registry","runs","handoffs","checkpoints","cache","temporary"]
LINK_RE=re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")

def _now()->str: return datetime.now(timezone.utc).isoformat()

def init_workspace(root:Path, project_id:str, name:str, objective:str)->Path:
    docs=root/"docs"; runtime=root/".orchestrator"
    for d in DOC_DIRS: (docs/d).mkdir(parents=True,exist_ok=True)
    for d in RUNTIME_DIRS: (runtime/d).mkdir(parents=True,exist_ok=True)
    project_file=docs/"00-project-control"/f"{project_id}-project.md"
    if not project_file.exists():
        record={
          "id":project_id,"project_id":project_id,"name":name,"objective":objective,
          "status":"ACTIVE","reporting_stage":"INITIATE","policy_refs":[],"environment_refs":[],
          "active_release_refs":[],"register_refs":{}
        }
        write_record(project_file,"project",record,
          f"# {name}\n\n## Objective\n\n{objective}\n\nThis is the canonical project control root.\n")
    return project_file

def validate_bundle(bundle:dict[str,Any])->list[dict[str,Any]]:
    findings=[]
    for f in validate_state_bundle(bundle): findings.append(f.to_dict())
    for f in validate_lifecycle(bundle): findings.append(f.to_dict())
    for f in validate_project_control(bundle): findings.append(f.to_dict())
    return sorted(findings,key=lambda x:(x.get("severity",""),x.get("code",""),x.get("path","")))

def sync_and_validate(root:Path)->tuple[dict[str,Any],list[dict[str,Any]]]:
    bundle=sync_state(root)
    findings=validate_bundle(bundle)
    result_path=root/".orchestrator"/"state"/"validation.json"
    result_path.write_text(json.dumps({"generated_at":_now(),"findings":findings},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return bundle,findings

def _status_counts(bundle:dict[str,Any])->dict[str,int]:
    out={}
    for w in bundle.get("work_items",[]) or []:
        state=w.get("state","UNKNOWN"); out[state]=out.get(state,0)+1
    return dict(sorted(out.items()))

def _open_decisions(bundle): return [x for x in bundle.get("decisions",[]) or [] if x.get("status") in {"OPEN","DEFERRED"}]
def _open_raid(bundle): return [x for x in bundle.get("raid",[]) or [] if x.get("status") not in {"CLOSED","RESOLVED","VALIDATED"}]

def render_views(root:Path,bundle:dict[str,Any],findings:list[dict[str,Any]]|None=None)->list[Path]:
    docs=root/"docs"; findings=findings or []
    project=bundle.get("project",{}); generated=_now(); counts=_status_counts(bundle)
    rq=ready_queue(bundle); cp=critical_path(bundle); trace=traceability_summary(bundle)
    errors=[f for f in findings if f.get("severity")=="ERROR"]
    idx=[GENERATED_MARKER,"# Project Index","","> Generated view. Do not edit as authoritative project truth.","",f"Generated: `{generated}`",f"Project: **{project.get('name','')}** (`{project.get('project_id','')}`)","","## Navigation",""]
    for d in DOC_DIRS: idx.append(f"- [{d}]({d}/)")
    idx += ["","## Current control snapshot","",f"- Reporting stage: `{project.get('reporting_stage','')}`",f"- Ready work: {len(rq)}",f"- Open decisions: {len(_open_decisions(bundle))}",f"- Open RAID records: {len(_open_raid(bundle))}",f"- Validation errors: {len(errors)}",f"- Requirement implementation coverage: {trace['implementation_coverage']:.0%}",f"- Requirement verification coverage: {trace['verification_coverage']:.0%}",""]
    index_path=docs/"INDEX.md"; index_path.write_text("\n".join(idx),encoding="utf-8")
    status=[GENERATED_MARKER,"# Project Status","","> Generated from canonical Markdown records. Do not edit as source of truth.","",f"Generated: `{generated}`",f"Project: **{project.get('name','')}**",f"Reporting stage: `{project.get('reporting_stage','')}`","","## Work state",""]
    if counts:
        for state,count in counts.items(): status.append(f"- `{state}`: {count}")
    else: status.append("- No work items recorded.")
    status += ["","## Ready queue",""] + ([f"- `{x}`" for x in rq] or ["- None"])
    status += ["","## Schedule",""]
    if cp.get("available"): status.append(f"- Critical path: {' → '.join(cp.get('work_ids',[])) or 'None'} ({cp.get('duration_hours',0):g}h)")
    else: status.append(f"- Critical path unavailable: {cp.get('reason','insufficient data')}")
    status += ["","## Decisions requiring attention",""] + ([f"- `{x.get('id')}` — {x.get('title') or x.get('question') or x.get('status')}" for x in _open_decisions(bundle)] or ["- None"])
    status += ["","## RAID",""] + ([f"- `{x.get('id')}` ({x.get('kind')}) — {x.get('status')}" for x in _open_raid(bundle)] or ["- None"])
    status += ["","## Validation",""] + ([f"- **{f.get('severity')}** `{f.get('code')}` — {f.get('message')}" for f in findings] or ["- No findings."])
    status += ["","## Traceability coverage","",f"- Implementation: {trace['implementation_coverage']:.0%}",f"- Verification: {trace['verification_coverage']:.0%}",""]
    status_path=docs/"00-project-control"/"status.md"; status_path.write_text("\n".join(status),encoding="utf-8")
    return [index_path,status_path]

def generate_handoff(root:Path,bundle:dict[str,Any],work_id:str)->Path:
    works={w.get("id"):w for w in bundle.get("work_items",[]) or []}; work=works.get(work_id)
    if not work: raise RecordError(f"unknown work item {work_id}")
    dep_ids=set(work.get("dependencies",[]) or [])
    deps=[d for d in bundle.get("dependencies",[]) or [] if d.get("id") in dep_ids or (isinstance(d.get("successor"),dict) and d["successor"].get("kind")=="work" and d["successor"].get("id")==work_id)]
    gate_map={g.get("id"):g for g in bundle.get("gates",[]) or []}
    gates=[gate_map[g] for g in work.get("required_gates",[]) or [] if g in gate_map]
    related=set()
    for link in bundle.get("trace_links",[]) or []:
        if link.get("source_ref")==work_id: related.add(link.get("target_ref"))
        if link.get("target_ref")==work_id: related.add(link.get("source_ref"))
    record_map={}
    for family in ("requirements","decisions","raid","changes"):
        for r in bundle.get(family,[]) or []: record_map[r.get("id")]=r
    context=[record_map[x] for x in sorted(related) if x in record_map]
    lines=[GENERATED_MARKER,f"# Work Handoff — {work_id}","","> Regenerable executor context. Canonical truth remains in `docs/` records.","",f"Generated: `{_now()}`","",f"## Objective\n\n{work.get('objective','')}","","## Assignment",f"- State: `{work.get('state')}`",f"- Priority: `{work.get('priority')}`",f"- Executor: `{json.dumps(work.get('executor'),sort_keys=True)}`",f"- Required capabilities: {', '.join(work.get('required_capabilities',[]) or []) or 'None'}",f"- Environments: {', '.join(work.get('environment_refs',[]) or []) or 'None'}","","## Acceptance criteria",""]
    criteria=work.get("acceptance_criteria",[]) or []
    lines += ([f"- `{c.get('id')}` [{c.get('status')}] {c.get('description')}" for c in criteria] or ["- None"])
    lines += ["","## Dependencies",""] + ([f"- `{d.get('id')}` {d.get('strength','HARD')} {d.get('relationship','FS')} — {d.get('status')}" for d in deps] or ["- None"])
    lines += ["","## Required gates",""] + ([f"- `{g.get('id')}` — {g.get('status')} / {g.get('validity')}" for g in gates] or ["- None"])
    lines += ["","## Related canonical context",""] + ([f"- `{r.get('id')}` — {r.get('title') or r.get('status') or r.get('kind','record')}" for r in context] or ["- None"])
    lines += ["","## Evidence expectation",f"- Work evidence refs currently recorded: {', '.join(work.get('evidence_refs',[]) or []) or 'None'}","- Return outputs, evidence, issues, assumptions, risks, decision recommendations, and follow-up work to Project Control.",""]
    target=root/".orchestrator"/"handoffs"/f"{work_id}.md"; target.parent.mkdir(parents=True,exist_ok=True); target.write_text("\n".join(lines),encoding="utf-8"); return target

def validate_links(root:Path)->list[dict[str,str]]:
    findings=[]; docs=root/"docs"
    for path in sorted(docs.rglob("*.md")) if docs.exists() else []:
        text=path.read_text(encoding="utf-8")
        for raw in LINK_RE.findall(text):
            link=raw.split("#",1)[0].strip()
            if not link or link.startswith(("http://","https://","mailto:")) or link.endswith("/"): continue
            target=(path.parent/link).resolve()
            try: target.relative_to(root.resolve())
            except ValueError:
                findings.append({"severity":"ERROR","code":"DOC-LINK-001","message":f"Link escapes project root: {raw}","path":str(path)}); continue
            if not target.exists(): findings.append({"severity":"ERROR","code":"DOC-LINK-002","message":f"Broken local link: {raw}","path":str(path)})
    return findings

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--root",default=".")
    sub=p.add_subparsers(dest="command",required=True)
    i=sub.add_parser("init"); i.add_argument("--project-id",required=True); i.add_argument("--name",required=True); i.add_argument("--objective",required=True)
    sub.add_parser("sync"); sub.add_parser("render"); sub.add_parser("validate-docs")
    h=sub.add_parser("handoff"); h.add_argument("work_id")
    args=p.parse_args(); root=Path(args.root).resolve()
    try:
        if args.command=="init":
            print(init_workspace(root,args.project_id,args.name,args.objective)); return 0
        bundle,findings=sync_and_validate(root)
        if args.command=="sync": print(json.dumps({"findings":findings},indent=2)); return 1 if any(f.get("severity")=="ERROR" for f in findings) else 0
        if args.command=="render":
            paths=render_views(root,bundle,findings); print("\n".join(map(str,paths))); return 1 if any(f.get("severity")=="ERROR" for f in findings) else 0
        if args.command=="handoff": print(generate_handoff(root,bundle,args.work_id)); return 0
        if args.command=="validate-docs":
            docs_findings=validate_links(root); print(json.dumps(docs_findings,indent=2)); return 1 if docs_findings else 0
    except (RecordError,OSError,ValueError,json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}"); return 2
    return 0
if __name__=="__main__": raise SystemExit(main())
