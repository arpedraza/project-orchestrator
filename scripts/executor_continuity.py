#!/usr/bin/env python3
"""Executor/session continuity for Project Orchestrator v2.

Run records and checkpoints are runtime continuity artifacts. They are not
canonical project truth; material facts must still be promoted to Markdown
records under docs/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from markdown_records import RecordError, sync_state

SCHEMA_VERSION = "1.0"
EXECUTOR_TYPES = {"human", "agent", "automation", "external"}
RUN_CLASSIFICATIONS = {
    "PASS",
    "FAIL_PRE_EXECUTION",
    "FAIL_PRE_WRITE",
    "FAIL_POST_WRITE",
    "FAIL_ROLLBACK_PASS",
    "RECOVERED_VALIDATED",
    "CANCELLED",
}
TERMINAL_CLASSIFICATIONS = RUN_CLASSIFICATIONS


class ContinuityError(ValueError):
    """Raised when runtime continuity state is invalid or unsafe to resume."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ContinuityError(f"expected JSON object in {path}")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _bundle(root: Path) -> dict[str, Any]:
    if (root / "docs").exists():
        return sync_state(root)
    state = root / ".orchestrator" / "state" / "state.json"
    if not state.exists():
        raise ContinuityError("project state not found; initialize/sync the project first")
    return _read_json(state)


def bundle_digest(bundle: dict[str, Any]) -> str:
    """Return a deterministic SHA256 used for drift detection, not trust."""
    encoded = json.dumps(bundle, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def git_snapshot(root: Path) -> dict[str, Any]:
    git = shutil.which("git")
    if not git:
        return {"available": False, "reason": "git executable not found"}

    def run(*args: str) -> tuple[int, str]:
        proc = subprocess.run(
            [git, "-C", str(root), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        return proc.returncode, proc.stdout.strip()

    code, top = run("rev-parse", "--show-toplevel")
    if code != 0:
        return {"available": True, "repository": False, "reason": top or "not a Git repository"}
    _, head = run("rev-parse", "HEAD")
    branch_code, branch = run("branch", "--show-current")
    if branch_code != 0 or not branch:
        _, branch = run("rev-parse", "--abbrev-ref", "HEAD")
    _, status = run("status", "--porcelain=v1")
    changed = [line for line in status.splitlines() if line.strip()]
    return {
        "available": True,
        "repository": True,
        "root": top,
        "head": head,
        "branch": branch,
        "working_tree_clean": not changed,
        "changed_paths": changed,
    }


def _project_summary(bundle: dict[str, Any]) -> dict[str, Any]:
    project = bundle.get("project", {}) or {}
    return {
        "project_id": project.get("project_id") or project.get("id"),
        "name": project.get("name"),
        "status": project.get("status"),
        "reporting_stage": project.get("reporting_stage"),
        "active_baseline_ref": project.get("active_baseline_ref"),
        "active_release_refs": project.get("active_release_refs", []) or [],
    }


def _work_by_state(bundle: dict[str, Any]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for work in bundle.get("work_items", []) or []:
        state = str(work.get("state") or "UNKNOWN")
        out.setdefault(state, []).append(str(work.get("id")))
    return {state: sorted(ids) for state, ids in sorted(out.items())}


def _open_records(bundle: dict[str, Any], family: str, terminal: set[str]) -> list[str]:
    result: list[str] = []
    for record in bundle.get(family, []) or []:
        if str(record.get("status") or "") not in terminal:
            rid = record.get("id")
            if rid:
                result.append(str(rid))
    return sorted(result)


def _load_orchestration(root: Path) -> dict[str, Any]:
    path = root / ".orchestrator" / "state" / "orchestration.json"
    return _read_json(path) if path.exists() else {}


def _latest_run(root: Path) -> dict[str, Any] | None:
    runs = root / ".orchestrator" / "runs"
    if not runs.exists():
        return None
    candidates = sorted((p for p in runs.iterdir() if p.is_dir() and (p / "run.json").exists()), key=lambda p: p.name)
    return _read_json(candidates[-1] / "run.json") if candidates else None


def _next_actions(bundle: dict[str, Any], orchestration: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    if orchestration and not orchestration.get("valid", True):
        actions.append("Repair project validation findings before dispatch.")
    decisions = orchestration.get("decisions", []) or []
    authority = orchestration.get("authority_blocks", []) or []
    gaps = orchestration.get("capability_gaps", []) or []
    selected = (orchestration.get("dispatch", {}) or {}).get("selected", []) or []
    if authority or decisions:
        ids = sorted({str(x.get("work_id") or x.get("id")) for x in [*authority, *decisions] if x.get("work_id") or x.get("id")})
        actions.append("Resolve authority/decision conditions" + (f" for: {', '.join(ids)}." if ids else "."))
    if selected:
        actions.append(f"Generate handoffs and delegate: {', '.join(map(str, selected))}.")
    if gaps:
        ids = sorted({str(x.get("work_id")) for x in gaps if x.get("work_id")})
        actions.append("Run capability-gap recovery" + (f" for: {', '.join(ids)}." if ids else "."))
    blocked = [str(w.get("id")) for w in bundle.get("work_items", []) or [] if w.get("state") == "BLOCKED"]
    if blocked:
        actions.append(f"Review active blockers: {', '.join(sorted(blocked))}.")
    if not actions:
        actions.append("Re-sync canonical state and continue with the next eligible work.")
    return actions


def _checkpoint_markdown(checkpoint: dict[str, Any]) -> str:
    project = checkpoint["project"]
    work = checkpoint["work"]
    orchestration = checkpoint["orchestration"]
    latest = checkpoint.get("latest_run") or {}
    lines = [
        "<!-- GENERATED: Project Orchestrator executor checkpoint; non-authoritative -->",
        "# Project Orchestrator — Executor Checkpoint",
        "",
        "> Runtime resume context only. Canonical project truth remains in `docs/`.",
        "",
        f"Checkpoint: `{checkpoint['checkpoint_id']}`",
        f"Generated: `{checkpoint['generated_at']}`",
        f"Project: **{project.get('name') or ''}** (`{project.get('project_id') or ''}`)",
        f"Project status: `{project.get('status') or ''}`",
        f"Reporting stage: `{project.get('reporting_stage') or ''}`",
        f"Canonical state digest: `{checkpoint['canonical_state_digest']}`",
        "",
        "## Current executor/session",
        "",
        f"- Executor: `{checkpoint['executor']['type']}:{checkpoint['executor']['id']}`",
        f"- Objective: {checkpoint.get('objective') or 'Resume project control from canonical state.'}",
        f"- Latest run: `{latest.get('run_id') or 'None'}`",
        f"- Latest run classification: `{latest.get('classification') or latest.get('status') or 'None'}`",
        "",
        "## Work state",
        "",
    ]
    if work:
        for state, ids in work.items():
            lines.append(f"- `{state}`: {', '.join(f'`{x}`' for x in ids) if ids else 'None'}")
    else:
        lines.append("- No work items recorded.")
    lines += ["", "## Dispatch / control-plane snapshot", ""]
    selected = orchestration.get("dispatch_selected", [])
    lines.append(f"- Dispatch selected: {', '.join(f'`{x}`' for x in selected) if selected else 'None'}")
    lines.append(f"- Capability gaps: {', '.join(f'`{x}`' for x in orchestration.get('capability_gap_work_ids', [])) or 'None'}")
    lines.append(f"- Authority/decision work: {', '.join(f'`{x}`' for x in orchestration.get('authority_work_ids', [])) or 'None'}")
    lines += ["", "## Project-control attention", ""]
    lines.append(f"- Open decisions: {', '.join(f'`{x}`' for x in checkpoint.get('open_decisions', [])) or 'None'}")
    lines.append(f"- Open RAID: {', '.join(f'`{x}`' for x in checkpoint.get('open_raid', [])) or 'None'}")
    lines += ["", "## Git read-only snapshot", ""]
    git = checkpoint.get("git", {})
    if not git.get("available"):
        lines.append(f"- Git unavailable: {git.get('reason', 'unknown')}")
    elif not git.get("repository"):
        lines.append(f"- Not a Git repository: {git.get('reason', '')}")
    else:
        lines.append(f"- Branch: `{git.get('branch')}`")
        lines.append(f"- HEAD: `{git.get('head')}`")
        lines.append(f"- Working tree clean: `{git.get('working_tree_clean')}`")
        for changed in git.get("changed_paths", []) or []:
            lines.append(f"  - `{changed}`")
    lines += ["", "## Next actions", ""]
    for action in checkpoint.get("next_actions", []):
        lines.append(f"- {action}")
    lines += ["", "## Resume rule", "", "Validate project identity and canonical state before acting. If the digest changed, re-sync/recalculate rather than trusting this checkpoint as current truth.", ""]
    return "\n".join(lines)


def write_checkpoint(
    root: Path,
    executor_id: str,
    executor_type: str,
    objective: str | None = None,
) -> tuple[Path, Path, dict[str, Any]]:
    if executor_type not in EXECUTOR_TYPES:
        raise ContinuityError(f"unsupported executor type: {executor_type}")
    bundle = _bundle(root)
    project = _project_summary(bundle)
    if not project.get("project_id"):
        raise ContinuityError("project identity is missing from canonical state")
    orchestration = _load_orchestration(root)
    latest_run = _latest_run(root)
    selected = (orchestration.get("dispatch", {}) or {}).get("selected", []) or []
    gaps = orchestration.get("capability_gaps", []) or []
    authority = [*(orchestration.get("authority_blocks", []) or []), *(orchestration.get("decisions", []) or [])]
    checkpoint_id = f"CHK-{_stamp()}-{uuid.uuid4().hex[:8]}"
    checkpoint = {
        "schema_version": SCHEMA_VERSION,
        "kind": "executor-checkpoint",
        "checkpoint_id": checkpoint_id,
        "generated_at": _now(),
        "project": project,
        "canonical_state_digest": bundle_digest(bundle),
        "executor": {"id": executor_id, "type": executor_type},
        "objective": objective,
        "work": _work_by_state(bundle),
        "open_decisions": _open_records(bundle, "decisions", {"DECIDED", "SUPERSEDED", "CANCELLED"}),
        "open_raid": _open_records(bundle, "raid", {"CLOSED", "RESOLVED", "VALIDATED"}),
        "orchestration": {
            "valid": orchestration.get("valid") if orchestration else None,
            "dispatch_selected": list(map(str, selected)),
            "state_recommendations": orchestration.get("state_recommendations", []) or [],
            "capability_gap_work_ids": sorted({str(x.get("work_id")) for x in gaps if x.get("work_id")}),
            "authority_work_ids": sorted({str(x.get("work_id") or x.get("id")) for x in authority if x.get("work_id") or x.get("id")}),
        },
        "latest_run": {
            "run_id": latest_run.get("run_id"),
            "status": latest_run.get("status"),
            "classification": latest_run.get("classification"),
            "ended_at": latest_run.get("ended_at"),
            "summary": latest_run.get("summary"),
        } if latest_run else None,
        "git": git_snapshot(root),
        "next_actions": _next_actions(bundle, orchestration),
    }
    checkpoint_dir = root / ".orchestrator" / "checkpoints"
    archive_json = checkpoint_dir / f"{checkpoint_id}.json"
    archive_md = checkpoint_dir / f"{checkpoint_id}.md"
    _write_json(archive_json, checkpoint)
    archive_md.write_text(_checkpoint_markdown(checkpoint), encoding="utf-8")
    _write_json(checkpoint_dir / "latest.json", checkpoint)
    (checkpoint_dir / "latest.md").write_text(_checkpoint_markdown(checkpoint), encoding="utf-8")
    return archive_json, archive_md, checkpoint


def resume_status(root: Path) -> dict[str, Any]:
    latest = root / ".orchestrator" / "checkpoints" / "latest.json"
    if not latest.exists():
        raise ContinuityError("no executor checkpoint exists")
    checkpoint = _read_json(latest)
    bundle = _bundle(root)
    current = _project_summary(bundle)
    checkpoint_project = checkpoint.get("project", {}) or {}
    if current.get("project_id") != checkpoint_project.get("project_id"):
        raise ContinuityError(
            f"project identity mismatch: checkpoint={checkpoint_project.get('project_id')} current={current.get('project_id')}"
        )
    current_digest = bundle_digest(bundle)
    return {
        "project_id": current.get("project_id"),
        "checkpoint_id": checkpoint.get("checkpoint_id"),
        "checkpoint_generated_at": checkpoint.get("generated_at"),
        "checkpoint_digest": checkpoint.get("canonical_state_digest"),
        "current_digest": current_digest,
        "state_changed_since_checkpoint": current_digest != checkpoint.get("canonical_state_digest"),
        "latest_checkpoint_markdown": str(root / ".orchestrator" / "checkpoints" / "latest.md"),
        "next_actions": checkpoint.get("next_actions", []),
    }


def start_run(
    root: Path,
    executor_id: str,
    executor_type: str,
    objective: str,
    work_item_refs: list[str] | None = None,
    authority_refs: list[str] | None = None,
    modify: list[str] | None = None,
    new: list[str] | None = None,
    delete: list[str] | None = None,
    protected: list[str] | None = None,
) -> tuple[Path, dict[str, Any]]:
    if executor_type not in EXECUTOR_TYPES:
        raise ContinuityError(f"unsupported executor type: {executor_type}")
    bundle = _bundle(root)
    project = _project_summary(bundle)
    if not project.get("project_id"):
        raise ContinuityError("project identity is missing from canonical state")
    run_id = f"RUN-{_stamp()}-{uuid.uuid4().hex[:8]}"
    record = {
        "schema_version": SCHEMA_VERSION,
        "kind": "execution-run",
        "run_id": run_id,
        "project_id": project["project_id"],
        "executor": {"id": executor_id, "type": executor_type},
        "objective": objective,
        "work_item_refs": sorted(set(work_item_refs or [])),
        "authority_refs": sorted(set(authority_refs or [])),
        "mutation_boundary": {
            "modify": sorted(set(modify or [])),
            "new": sorted(set(new or [])),
            "delete": sorted(set(delete or [])),
            "protected": sorted(set(protected or [])),
        },
        "status": "IN_PROGRESS",
        "classification": None,
        "cause": None,
        "started_at": _now(),
        "ended_at": None,
        "starting_state": {
            "canonical_state_digest": bundle_digest(bundle),
            "project": project,
            "git": git_snapshot(root),
        },
        "events": [],
        "outputs": [],
        "files_affected": [],
        "evidence_refs": [],
        "issue_refs": [],
        "decision_refs": [],
        "summary": None,
    }
    path = root / ".orchestrator" / "runs" / run_id / "run.json"
    _write_json(path, record)
    return path, record


def add_run_event(root: Path, run_id: str, kind: str, message: str, refs: list[str] | None = None) -> dict[str, Any]:
    path = root / ".orchestrator" / "runs" / run_id / "run.json"
    if not path.exists():
        raise ContinuityError(f"unknown run: {run_id}")
    record = _read_json(path)
    if record.get("status") != "IN_PROGRESS":
        raise ContinuityError(f"run {run_id} is already terminal")
    record.setdefault("events", []).append({"at": _now(), "kind": kind, "message": message, "refs": refs or []})
    _write_json(path, record)
    return record


def end_run(
    root: Path,
    run_id: str,
    classification: str,
    summary: str,
    cause: str | None = None,
    files_affected: list[str] | None = None,
    outputs: list[str] | None = None,
    evidence_refs: list[str] | None = None,
    issue_refs: list[str] | None = None,
    decision_refs: list[str] | None = None,
) -> dict[str, Any]:
    if classification not in TERMINAL_CLASSIFICATIONS:
        raise ContinuityError(f"unsupported run classification: {classification}")
    path = root / ".orchestrator" / "runs" / run_id / "run.json"
    if not path.exists():
        raise ContinuityError(f"unknown run: {run_id}")
    record = _read_json(path)
    if record.get("status") != "IN_PROGRESS":
        raise ContinuityError(f"run {run_id} is already terminal")
    record.update({
        "status": "COMPLETED" if classification in {"PASS", "RECOVERED_VALIDATED"} else "FAILED" if classification.startswith("FAIL_") else "CANCELLED",
        "classification": classification,
        "cause": cause,
        "ended_at": _now(),
        "summary": summary,
        "files_affected": sorted(set(files_affected or [])),
        "outputs": sorted(set(outputs or [])),
        "evidence_refs": sorted(set(evidence_refs or [])),
        "issue_refs": sorted(set(issue_refs or [])),
        "decision_refs": sorted(set(decision_refs or [])),
        "ending_state": {
            "canonical_state_digest": bundle_digest(_bundle(root)),
            "git": git_snapshot(root),
        },
    })
    _write_json(path, record)
    return record


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Project Orchestrator executor/session continuity")
    p.add_argument("--root", default=".")
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("checkpoint")
    c.add_argument("--executor-id", required=True)
    c.add_argument("--executor-type", choices=sorted(EXECUTOR_TYPES), required=True)
    c.add_argument("--objective")

    sub.add_parser("resume")

    s = sub.add_parser("run-start")
    s.add_argument("--executor-id", required=True)
    s.add_argument("--executor-type", choices=sorted(EXECUTOR_TYPES), required=True)
    s.add_argument("--objective", required=True)
    s.add_argument("--work", action="append", default=[])
    s.add_argument("--authority-ref", action="append", default=[])
    s.add_argument("--modify", action="append", default=[])
    s.add_argument("--new", action="append", default=[])
    s.add_argument("--delete", action="append", default=[])
    s.add_argument("--protected", action="append", default=[])

    e = sub.add_parser("run-event")
    e.add_argument("--run-id", required=True)
    e.add_argument("--kind", required=True)
    e.add_argument("--message", required=True)
    e.add_argument("--ref", action="append", default=[])

    f = sub.add_parser("run-end")
    f.add_argument("--run-id", required=True)
    f.add_argument("--classification", choices=sorted(RUN_CLASSIFICATIONS), required=True)
    f.add_argument("--summary", required=True)
    f.add_argument("--cause")
    f.add_argument("--file", action="append", default=[])
    f.add_argument("--output", action="append", default=[])
    f.add_argument("--evidence-ref", action="append", default=[])
    f.add_argument("--issue-ref", action="append", default=[])
    f.add_argument("--decision-ref", action="append", default=[])
    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.command == "checkpoint":
            archive_json, archive_md, _ = write_checkpoint(root, args.executor_id, args.executor_type, args.objective)
            print(json.dumps({"checkpoint_json": str(archive_json), "checkpoint_markdown": str(archive_md), "latest": str(root / '.orchestrator/checkpoints/latest.md')}, indent=2))
            return 0
        if args.command == "resume":
            print(json.dumps(resume_status(root), indent=2, sort_keys=True))
            return 0
        if args.command == "run-start":
            path, record = start_run(root, args.executor_id, args.executor_type, args.objective, args.work, args.authority_ref, args.modify, args.new, args.delete, args.protected)
            print(json.dumps({"run_id": record["run_id"], "path": str(path)}, indent=2))
            return 0
        if args.command == "run-event":
            record = add_run_event(root, args.run_id, args.kind, args.message, args.ref)
            print(json.dumps({"run_id": record["run_id"], "events": len(record.get("events", []))}, indent=2))
            return 0
        if args.command == "run-end":
            record = end_run(root, args.run_id, args.classification, args.summary, args.cause, args.file, args.output, args.evidence_ref, args.issue_ref, args.decision_ref)
            print(json.dumps({"run_id": record["run_id"], "classification": record["classification"], "status": record["status"]}, indent=2))
            return 0
    except (ContinuityError, RecordError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"executor-continuity: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
