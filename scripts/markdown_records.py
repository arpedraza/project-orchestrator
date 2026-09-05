#!/usr/bin/env python3
"""Portable Markdown canonical-record I/O for Project Orchestrator v2.

Canonical project records are Markdown files with simple YAML frontmatter and a
JSON object carried in the `data` block. The format is readable in any Markdown
editor, works in Obsidian without plugins, and remains deterministic for agents.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from scan_skills import parse_frontmatter, FrontmatterError

TYPE_TO_FAMILY={
  "work":"work_items","dependency":"dependencies","gate":"gates","environment":"environments",
  "promotion":"promotions","milestone":"milestones","event":"events","requirement":"requirements",
  "decision":"decisions","raid":"raid","change":"changes","evidence":"evidence","release":"releases",
  "deployment":"deployments","trace_link":"trace_links"
}
GENERATED_MARKER="<!-- generated-by: project-orchestrator -->"

class RecordError(ValueError): pass

def _clean_runtime_record(record:dict[str,Any], record_type:str)->dict[str,Any]:
    out={k:v for k,v in record.items() if not k.startswith("_") and k!="record_type"}
    if record_type=="trace_link":
        out.pop("id",None)
    return out

def parse_record(path:Path)->dict[str,Any]|None:
    text=path.read_text(encoding="utf-8")
    if GENERATED_MARKER in text:
        return None
    try:
        meta,body,warnings=parse_frontmatter(text)
    except FrontmatterError:
        return None
    record_type=str(meta.get("record_type") or "").strip()
    rid=str(meta.get("id") or "").strip()
    if not record_type:
        return None
    if not rid:
        raise RecordError(f"{path}: canonical record requires id")
    raw=meta.get("data") or "{}"
    if not isinstance(raw,str):
        raise RecordError(f"{path}: data must be a JSON object encoded as a string/block")
    try:
        data=json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RecordError(f"{path}: invalid data JSON: {exc}") from exc
    if not isinstance(data,dict):
        raise RecordError(f"{path}: data JSON must be an object")
    data["id"]=rid
    status=meta.get("status")
    if status and "status" not in data and "state" not in data:
        data["status"]=status
    data["record_type"]=record_type
    data["_file"]=str(path)
    data["_narrative"]=body
    if warnings: data["_warnings"]=warnings
    return data

def write_record(path:Path, record_type:str, record:dict[str,Any], narrative:str="") -> None:
    rid=str(record.get("id") or "").strip()
    if not rid: raise RecordError("record requires id")
    payload=_clean_runtime_record(dict(record),record_type)
    compact=json.dumps(payload,separators=(",",":"),ensure_ascii=False,sort_keys=True)
    status=record.get("status") or record.get("state") or ""
    lines=["---",f"id: {rid}",f"record_type: {record_type}"]
    if status: lines.append(f"status: {status}")
    lines.extend(["data: >",f"  {compact}","---",""])
    title=record.get("title") or record.get("name") or rid
    body=narrative.strip() or f"# {rid} — {title}\n"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text("\n".join(lines)+body.rstrip()+"\n",encoding="utf-8")

def scan_records(docs_root:Path)->list[dict[str,Any]]:
    records=[]; ids=set()
    if not docs_root.exists(): return records
    for path in sorted(docs_root.rglob("*.md")):
        record=parse_record(path)
        if record is None: continue
        rid=record["id"]
        if rid in ids: raise RecordError(f"duplicate canonical id {rid}")
        ids.add(rid); records.append(record)
    return records

def build_state_bundle(records:list[dict[str,Any]])->dict[str,Any]:
    projects=[r for r in records if r.get("record_type")=="project"]
    if len(projects)!=1: raise RecordError(f"expected exactly one project record, found {len(projects)}")
    project=_clean_runtime_record(projects[0],"project")
    project.pop("id",None)
    bundle={"schema_version":"1.0","project":project,"work_items":[],"dependencies":[],"gates":[]}
    for r in records:
        rt=r.get("record_type")
        if rt=="project": continue
        family=TYPE_TO_FAMILY.get(rt)
        if not family: continue
        bundle.setdefault(family,[]).append(_clean_runtime_record(r,rt))
    return bundle

def sync_state(project_root:Path)->dict[str,Any]:
    records=scan_records(project_root/"docs")
    bundle=build_state_bundle(records)
    target=project_root/".orchestrator"/"state"/"state.json"
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(bundle,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return bundle
