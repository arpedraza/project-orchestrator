#!/usr/bin/env python3
"""Project Orchestrator v2 state model and semantic validation.

CHG-003 implements the machine/runtime projection for Project State, Work Items,
Dependencies, and Gates. It intentionally does not implement scheduling,
dispatch, authority evaluation, or environment promotion.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Iterable

WORK_STATES = {
    "PROPOSED", "READY", "IN_PROGRESS", "NEEDS_REVIEW", "WAITING",
    "NEEDS_REWORK", "BLOCKED", "NEEDS_DECISION", "DONE", "PARKED",
    "CANCELLED", "SUPERSEDED",
}
DEPENDENCY_RELATIONSHIPS = {"FS", "SS", "FF", "SF"}
DEPENDENCY_STRENGTHS = {"HARD", "SOFT"}
DEPENDENCY_STATUSES = {"SATISFIED", "UNSATISFIED", "AT_RISK", "BROKEN", "WAIVED"}
DEPENDENCY_KINDS = {"work", "gate", "decision", "artifact", "environment", "external", "capability"}
GATE_STATUSES = {"NOT_READY", "READY", "EVALUATING", "PASSED", "FAILED", "WAIVED"}
GATE_VALIDITIES = {"VALID", "STALE", "INVALIDATED"}
ACCEPTANCE_STATUSES = {"PENDING", "SATISFIED", "FAILED"}
GATE_CRITERION_STATUSES = {"NOT_EVALUATED", "SATISFIED", "FAILED", "WAIVED"}
EXECUTOR_TYPES = {"human", "agent", "automation", "external"}
DURATION_UNITS = {"minutes", "hours", "days"}
LOCAL_REFERENCE_KINDS = {"work", "gate"}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    path: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _finding(code: str, message: str, path: str = "", severity: str = "ERROR") -> Finding:
    return Finding(severity=severity, code=code, message=message, path=path)


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(_is_nonempty_string(v) for v in value)


def _is_nonempty_string_list(value: Any) -> bool:
    return _is_string_list(value) and len(value) > 0


def _valid_iso_datetime(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        datetime.fromisoformat(candidate)
        return True
    except ValueError:
        return False


def _check_datetime_map(value: Any, path: str, findings: list[Finding]) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        findings.append(_finding("STATE-SCHEDULE-001", "Schedule phase must be an object.", path))
        return
    for key in ("start", "finish"):
        if key in value and value[key] is not None and not _valid_iso_datetime(value[key]):
            findings.append(_finding("STATE-SCHEDULE-002", f"{key} must be an ISO-8601 date-time string.", f"{path}.{key}"))


def _check_duration(value: Any, path: str, findings: list[Finding]) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        findings.append(_finding("STATE-DURATION-001", "Duration must be an object.", path))
        return
    amount = value.get("value")
    if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount < 0:
        findings.append(_finding("STATE-DURATION-002", "Duration value must be a non-negative number.", f"{path}.value"))
    if value.get("unit") not in DURATION_UNITS:
        findings.append(_finding("STATE-DURATION-003", f"Duration unit must be one of {sorted(DURATION_UNITS)}.", f"{path}.unit"))


def _typed_ref(ref: Any, path: str, findings: list[Finding]) -> tuple[str, str] | None:
    if not isinstance(ref, dict):
        findings.append(_finding("STATE-REF-001", "Reference must be an object with kind and id.", path))
        return None
    kind, ref_id = ref.get("kind"), ref.get("id")
    if kind not in DEPENDENCY_KINDS:
        findings.append(_finding("STATE-REF-002", f"Reference kind must be one of {sorted(DEPENDENCY_KINDS)}.", f"{path}.kind"))
        return None
    if not _is_nonempty_string(ref_id):
        findings.append(_finding("STATE-REF-003", "Reference id must be a non-empty string.", f"{path}.id"))
        return None
    return kind, ref_id


def _validate_project(project: Any, findings: list[Finding]) -> None:
    if not isinstance(project, dict):
        findings.append(_finding("STATE-PROJECT-001", "project must be an object.", "project"))
        return
    for key in ("project_id", "name", "objective", "status", "reporting_stage"):
        if not _is_nonempty_string(project.get(key)):
            findings.append(_finding("STATE-PROJECT-002", f"{key} must be a non-empty string.", f"project.{key}"))
    for key in ("policy_refs", "environment_refs", "active_release_refs"):
        if key in project and not _is_string_list(project[key]):
            findings.append(_finding("STATE-PROJECT-003", f"{key} must be an array of non-empty strings.", f"project.{key}"))
    if "register_refs" in project:
        refs = project["register_refs"]
        if not isinstance(refs, dict) or not all(_is_nonempty_string(k) and _is_nonempty_string(v) for k, v in refs.items()):
            findings.append(_finding("STATE-PROJECT-004", "register_refs must map non-empty names to non-empty reference strings.", "project.register_refs"))
    if project.get("active_baseline_ref") is not None and not _is_nonempty_string(project.get("active_baseline_ref")):
        findings.append(_finding("STATE-PROJECT-005", "active_baseline_ref must be null or a non-empty string.", "project.active_baseline_ref"))


def _validate_work_item(work: Any, index: int, findings: list[Finding]) -> None:
    path = f"work_items[{index}]"
    if not isinstance(work, dict):
        findings.append(_finding("STATE-WORK-001", "Work item must be an object.", path))
        return
    for key in ("id", "type", "title", "objective", "reporting_stage", "priority"):
        if not _is_nonempty_string(work.get(key)):
            findings.append(_finding("STATE-WORK-002", f"{key} must be a non-empty string.", f"{path}.{key}"))
    if work.get("state") not in WORK_STATES:
        findings.append(_finding("STATE-WORK-003", f"state must be one of {sorted(WORK_STATES)}.", f"{path}.state"))
    if work.get("parent_ref") is not None and not _is_nonempty_string(work.get("parent_ref")):
        findings.append(_finding("STATE-WORK-004", "parent_ref must be null or a non-empty string.", f"{path}.parent_ref"))
    for key in ("required_capabilities", "preferred_capabilities", "environment_refs", "release_refs", "dependencies", "required_gates", "traceability_refs", "output_refs", "evidence_refs"):
        if key in work and not _is_string_list(work[key]):
            findings.append(_finding("STATE-WORK-005", f"{key} must be an array of non-empty strings.", f"{path}.{key}"))
    executor = work.get("executor")
    if executor is not None:
        if not isinstance(executor, dict):
            findings.append(_finding("STATE-EXECUTOR-001", "executor must be null or an object.", f"{path}.executor"))
        else:
            if executor.get("type") not in EXECUTOR_TYPES:
                findings.append(_finding("STATE-EXECUTOR-002", f"executor.type must be one of {sorted(EXECUTOR_TYPES)}.", f"{path}.executor.type"))
            if not _is_nonempty_string(executor.get("id")):
                findings.append(_finding("STATE-EXECUTOR-003", "executor.id must be a non-empty string.", f"{path}.executor.id"))
    criteria = work.get("acceptance_criteria", [])
    if not isinstance(criteria, list):
        findings.append(_finding("STATE-AC-001", "acceptance_criteria must be an array.", f"{path}.acceptance_criteria"))
    else:
        for cidx, criterion in enumerate(criteria):
            cpath = f"{path}.acceptance_criteria[{cidx}]"
            if not isinstance(criterion, dict):
                findings.append(_finding("STATE-AC-002", "Acceptance criterion must be an object.", cpath))
                continue
            for key in ("id", "description"):
                if not _is_nonempty_string(criterion.get(key)):
                    findings.append(_finding("STATE-AC-003", f"{key} must be a non-empty string.", f"{cpath}.{key}"))
            if not isinstance(criterion.get("required"), bool):
                findings.append(_finding("STATE-AC-004", "required must be boolean.", f"{cpath}.required"))
            if criterion.get("status") not in ACCEPTANCE_STATUSES:
                findings.append(_finding("STATE-AC-005", f"status must be one of {sorted(ACCEPTANCE_STATUSES)}.", f"{cpath}.status"))
            if "evidence_refs" in criterion and not _is_string_list(criterion["evidence_refs"]):
                findings.append(_finding("STATE-AC-006", "evidence_refs must be an array of non-empty strings.", f"{cpath}.evidence_refs"))
    schedule = work.get("schedule")
    if schedule is not None:
        if not isinstance(schedule, dict):
            findings.append(_finding("STATE-SCHEDULE-003", "schedule must be null or an object.", f"{path}.schedule"))
        else:
            _check_duration(schedule.get("estimate"), f"{path}.schedule.estimate", findings)
            for phase in ("baseline", "forecast", "actual"):
                _check_datetime_map(schedule.get(phase), f"{path}.schedule.{phase}", findings)


def _validate_dependency(dep: Any, index: int, findings: list[Finding]) -> None:
    path = f"dependencies[{index}]"
    if not isinstance(dep, dict):
        findings.append(_finding("STATE-DEP-001", "Dependency must be an object.", path))
        return
    if not _is_nonempty_string(dep.get("id")):
        findings.append(_finding("STATE-DEP-002", "id must be a non-empty string.", f"{path}.id"))
    _typed_ref(dep.get("predecessor"), f"{path}.predecessor", findings)
    _typed_ref(dep.get("successor"), f"{path}.successor", findings)
    relationship = dep.get("relationship", "FS")
    if relationship not in DEPENDENCY_RELATIONSHIPS:
        findings.append(_finding("STATE-DEP-003", f"relationship must be one of {sorted(DEPENDENCY_RELATIONSHIPS)}.", f"{path}.relationship"))
    strength = dep.get("strength", "HARD")
    if strength not in DEPENDENCY_STRENGTHS:
        findings.append(_finding("STATE-DEP-004", f"strength must be one of {sorted(DEPENDENCY_STRENGTHS)}.", f"{path}.strength"))
    if dep.get("status") not in DEPENDENCY_STATUSES:
        findings.append(_finding("STATE-DEP-005", f"status must be one of {sorted(DEPENDENCY_STATUSES)}.", f"{path}.status"))
    _check_duration(dep.get("lag"), f"{path}.lag", findings)
    if dep.get("status") == "WAIVED" and not _is_nonempty_string(dep.get("decision_ref")):
        findings.append(_finding("STATE-DEP-WAIVER-001", "A WAIVED dependency requires decision_ref.", f"{path}.decision_ref"))
    if dep.get("decision_ref") is not None and not _is_nonempty_string(dep.get("decision_ref")):
        findings.append(_finding("STATE-DEP-006", "decision_ref must be null or a non-empty string.", f"{path}.decision_ref"))


def _validate_gate(gate: Any, index: int, findings: list[Finding]) -> None:
    path = f"gates[{index}]"
    if not isinstance(gate, dict):
        findings.append(_finding("STATE-GATE-001", "Gate must be an object.", path))
        return
    for key in ("id", "name", "category"):
        if not _is_nonempty_string(gate.get(key)):
            findings.append(_finding("STATE-GATE-002", f"{key} must be a non-empty string.", f"{path}.{key}"))
    if not isinstance(gate.get("blocking"), bool):
        findings.append(_finding("STATE-GATE-003", "blocking must be boolean.", f"{path}.blocking"))
    if gate.get("status") not in GATE_STATUSES:
        findings.append(_finding("STATE-GATE-004", f"status must be one of {sorted(GATE_STATUSES)}.", f"{path}.status"))
    if gate.get("validity") not in GATE_VALIDITIES:
        findings.append(_finding("STATE-GATE-005", f"validity must be one of {sorted(GATE_VALIDITIES)}.", f"{path}.validity"))
    if not isinstance(gate.get("scope"), dict):
        findings.append(_finding("STATE-GATE-006", "scope must be an object.", f"{path}.scope"))
    if "required_evaluator_capabilities" in gate and not _is_string_list(gate["required_evaluator_capabilities"]):
        findings.append(_finding("STATE-GATE-007", "required_evaluator_capabilities must be an array of non-empty strings.", f"{path}.required_evaluator_capabilities"))
    if gate.get("approval_policy_ref") is not None and not _is_nonempty_string(gate.get("approval_policy_ref")):
        findings.append(_finding("STATE-GATE-008", "approval_policy_ref must be null or a non-empty string.", f"{path}.approval_policy_ref"))
    if "evidence_refs" in gate and not _is_string_list(gate["evidence_refs"]):
        findings.append(_finding("STATE-GATE-009", "evidence_refs must be an array of non-empty strings.", f"{path}.evidence_refs"))
    if gate.get("decision_ref") is not None and not _is_nonempty_string(gate.get("decision_ref")):
        findings.append(_finding("STATE-GATE-010", "decision_ref must be null or a non-empty string.", f"{path}.decision_ref"))
    criteria = gate.get("criteria", [])
    if not isinstance(criteria, list):
        findings.append(_finding("STATE-GC-001", "criteria must be an array.", f"{path}.criteria"))
        criteria = []
    for cidx, criterion in enumerate(criteria):
        cpath = f"{path}.criteria[{cidx}]"
        if not isinstance(criterion, dict):
            findings.append(_finding("STATE-GC-002", "Gate criterion must be an object.", cpath))
            continue
        for key in ("id", "description"):
            if not _is_nonempty_string(criterion.get(key)):
                findings.append(_finding("STATE-GC-003", f"{key} must be a non-empty string.", f"{cpath}.{key}"))
        if not isinstance(criterion.get("required"), bool):
            findings.append(_finding("STATE-GC-004", "required must be boolean.", f"{cpath}.required"))
        if criterion.get("status") not in GATE_CRITERION_STATUSES:
            findings.append(_finding("STATE-GC-005", f"status must be one of {sorted(GATE_CRITERION_STATUSES)}.", f"{cpath}.status"))
        if "evidence_refs" in criterion and not _is_string_list(criterion["evidence_refs"]):
            findings.append(_finding("STATE-GC-006", "evidence_refs must be an array of non-empty strings.", f"{cpath}.evidence_refs"))
        if criterion.get("status") == "WAIVED" and not _is_nonempty_string(criterion.get("decision_ref")):
            findings.append(_finding("STATE-GC-WAIVER-001", "A WAIVED gate criterion requires decision_ref.", f"{cpath}.decision_ref"))
    status = gate.get("status")
    if status == "PASSED":
        for cidx, criterion in enumerate(criteria):
            if isinstance(criterion, dict) and criterion.get("required") is True and criterion.get("status") != "SATISFIED":
                findings.append(_finding("STATE-GATE-PASS-001", "A PASSED gate requires every required criterion to be SATISFIED.", f"{path}.criteria[{cidx}]"))
        if not isinstance(gate.get("scope"), dict) or not gate.get("scope"):
            findings.append(_finding("STATE-GATE-PASS-002", "A PASSED gate requires non-empty evaluated scope.", f"{path}.scope"))
        if not _is_nonempty_string_list(gate.get("evidence_refs")):
            findings.append(_finding("STATE-GATE-PASS-003", "A PASSED gate requires at least one supporting evidence reference.", f"{path}.evidence_refs"))
        if gate.get("validity") != "VALID":
            findings.append(_finding("STATE-GATE-PASS-004", "A PASSED gate must have validity VALID.", f"{path}.validity"))
    if status == "WAIVED":
        if not _is_nonempty_string(gate.get("decision_ref")):
            findings.append(_finding("STATE-GATE-WAIVER-001", "A WAIVED gate requires decision_ref.", f"{path}.decision_ref"))
        if gate.get("validity") != "VALID":
            findings.append(_finding("STATE-GATE-WAIVER-002", "A current WAIVED gate must have validity VALID.", f"{path}.validity"))


def _collect_ids(bundle: dict[str, Any], findings: list[Finding]) -> dict[str, str]:
    seen: dict[str, str] = {}

    def register(identifier: Any, path: str) -> None:
        if not _is_nonempty_string(identifier):
            return
        identifier = identifier.strip()
        if identifier in seen:
            findings.append(_finding("STATE-ID-001", f"Duplicate stable id {identifier!r}; first seen at {seen[identifier]}.", path))
        else:
            seen[identifier] = path

    project = bundle.get("project")
    if isinstance(project, dict):
        register(project.get("project_id"), "project.project_id")
    for i, work in enumerate(bundle.get("work_items", []) if isinstance(bundle.get("work_items"), list) else []):
        if isinstance(work, dict):
            register(work.get("id"), f"work_items[{i}].id")
            for j, criterion in enumerate(work.get("acceptance_criteria", []) if isinstance(work.get("acceptance_criteria"), list) else []):
                if isinstance(criterion, dict):
                    register(criterion.get("id"), f"work_items[{i}].acceptance_criteria[{j}].id")
    for i, dep in enumerate(bundle.get("dependencies", []) if isinstance(bundle.get("dependencies"), list) else []):
        if isinstance(dep, dict):
            register(dep.get("id"), f"dependencies[{i}].id")
    for i, gate in enumerate(bundle.get("gates", []) if isinstance(bundle.get("gates"), list) else []):
        if isinstance(gate, dict):
            register(gate.get("id"), f"gates[{i}].id")
            for j, criterion in enumerate(gate.get("criteria", []) if isinstance(gate.get("criteria"), list) else []):
                if isinstance(criterion, dict):
                    register(criterion.get("id"), f"gates[{i}].criteria[{j}].id")
    return seen


def _local_indexes(bundle: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    work = {item.get("id"): item for item in bundle.get("work_items", []) if isinstance(item, dict) and _is_nonempty_string(item.get("id"))}
    deps = {item.get("id"): item for item in bundle.get("dependencies", []) if isinstance(item, dict) and _is_nonempty_string(item.get("id"))}
    gates = {item.get("id"): item for item in bundle.get("gates", []) if isinstance(item, dict) and _is_nonempty_string(item.get("id"))}
    return work, deps, gates


def _validate_references(bundle: dict[str, Any], findings: list[Finding]) -> None:
    work_index, dep_index, gate_index = _local_indexes(bundle)
    for i, work in enumerate(bundle.get("work_items", [])):
        if not isinstance(work, dict):
            continue
        parent = work.get("parent_ref")
        if _is_nonempty_string(parent) and parent not in work_index:
            findings.append(_finding("STATE-REF-WORK-001", f"parent_ref {parent!r} does not reference a local work item.", f"work_items[{i}].parent_ref"))
        for j, dep_id in enumerate(work.get("dependencies", []) if isinstance(work.get("dependencies"), list) else []):
            if _is_nonempty_string(dep_id) and dep_id not in dep_index:
                findings.append(_finding("STATE-REF-DEP-001", f"Dependency {dep_id!r} does not exist.", f"work_items[{i}].dependencies[{j}]"))
        for j, gate_id in enumerate(work.get("required_gates", []) if isinstance(work.get("required_gates"), list) else []):
            if _is_nonempty_string(gate_id) and gate_id not in gate_index:
                findings.append(_finding("STATE-REF-GATE-001", f"Gate {gate_id!r} does not exist.", f"work_items[{i}].required_gates[{j}]"))
    for i, dep in enumerate(bundle.get("dependencies", [])):
        if not isinstance(dep, dict):
            continue
        for side in ("predecessor", "successor"):
            ref = dep.get(side)
            if not isinstance(ref, dict):
                continue
            kind, ref_id = ref.get("kind"), ref.get("id")
            if kind == "work" and _is_nonempty_string(ref_id) and ref_id not in work_index:
                findings.append(_finding("STATE-REF-LOCAL-001", f"{side} references missing local work item {ref_id!r}.", f"dependencies[{i}].{side}"))
            elif kind == "gate" and _is_nonempty_string(ref_id) and ref_id not in gate_index:
                findings.append(_finding("STATE-REF-LOCAL-002", f"{side} references missing local gate {ref_id!r}.", f"dependencies[{i}].{side}"))


def _node_key(ref: dict[str, Any]) -> str | None:
    kind, ref_id = ref.get("kind"), ref.get("id")
    if kind in DEPENDENCY_KINDS and _is_nonempty_string(ref_id):
        return f"{kind}:{ref_id}"
    return None


def _hard_cycle(findings: list[Finding], dependencies: Iterable[Any]) -> None:
    graph: dict[str, set[str]] = {}
    for dep in dependencies:
        if not isinstance(dep, dict) or dep.get("strength", "HARD") != "HARD":
            continue
        pred = dep.get("predecessor")
        succ = dep.get("successor")
        if not isinstance(pred, dict) or not isinstance(succ, dict):
            continue
        pkey, skey = _node_key(pred), _node_key(succ)
        if pkey and skey:
            graph.setdefault(pkey, set()).add(skey)
            graph.setdefault(skey, set())

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}
    stack: list[str] = []

    def visit(node: str) -> bool:
        color[node] = GRAY
        stack.append(node)
        for nxt in graph[node]:
            if color[nxt] == GRAY:
                start = stack.index(nxt)
                cycle = stack[start:] + [nxt]
                findings.append(_finding("STATE-DEP-CYCLE-001", "Hard dependency cycle detected: " + " -> ".join(cycle), "dependencies"))
                return True
            if color[nxt] == WHITE and visit(nxt):
                return True
        stack.pop()
        color[node] = BLACK
        return False

    for node in sorted(graph):
        if color[node] == WHITE and visit(node):
            return


def _validate_ready_done(bundle: dict[str, Any], findings: list[Finding]) -> None:
    work_index, _, gate_index = _local_indexes(bundle)
    incoming_hard: dict[str, list[dict[str, Any]]] = {wid: [] for wid in work_index}
    for dep in bundle.get("dependencies", []):
        if not isinstance(dep, dict) or dep.get("strength", "HARD") != "HARD":
            continue
        successor = dep.get("successor")
        if isinstance(successor, dict) and successor.get("kind") == "work" and successor.get("id") in incoming_hard:
            incoming_hard[successor["id"]].append(dep)

    for i, work in enumerate(bundle.get("work_items", [])):
        if not isinstance(work, dict) or not _is_nonempty_string(work.get("id")):
            continue
        work_id = work["id"]
        if work.get("state") == "READY":
            for dep in incoming_hard.get(work_id, []):
                if dep.get("status") in {"UNSATISFIED", "BROKEN"}:
                    findings.append(_finding("STATE-READY-001", f"{work_id} is READY but hard dependency {dep.get('id')!r} is {dep.get('status')!r}.", f"work_items[{i}].state"))
        if work.get("state") == "DONE":
            for cidx, criterion in enumerate(work.get("acceptance_criteria", []) if isinstance(work.get("acceptance_criteria"), list) else []):
                if isinstance(criterion, dict) and criterion.get("required") is True and criterion.get("status") != "SATISFIED":
                    findings.append(_finding("STATE-DONE-AC-001", f"{work_id} is DONE but required acceptance criterion {criterion.get('id')!r} is not SATISFIED.", f"work_items[{i}].acceptance_criteria[{cidx}]"))
            for gidx, gate_id in enumerate(work.get("required_gates", []) if isinstance(work.get("required_gates"), list) else []):
                gate = gate_index.get(gate_id)
                if gate is None:
                    findings.append(_finding("STATE-DONE-GATE-001", f"{work_id} is DONE but required gate {gate_id!r} is missing.", f"work_items[{i}].required_gates[{gidx}]"))
                    continue
                passed = gate.get("status") == "PASSED" and gate.get("validity") == "VALID"
                waived = gate.get("status") == "WAIVED" and gate.get("validity") == "VALID" and _is_nonempty_string(gate.get("decision_ref"))
                if not (passed or waived):
                    findings.append(_finding("STATE-DONE-GATE-002", f"{work_id} is DONE but required gate {gate_id!r} is not currently PASSED or validly WAIVED.", f"work_items[{i}].required_gates[{gidx}]"))


def validate_state_bundle(bundle: Any) -> list[Finding]:
    """Return deterministic semantic findings for a state bundle."""
    findings: list[Finding] = []
    if not isinstance(bundle, dict):
        return [_finding("STATE-BUNDLE-001", "State bundle must be a JSON object.", "$")]
    if not _is_nonempty_string(bundle.get("schema_version")):
        findings.append(_finding("STATE-BUNDLE-002", "schema_version must be a non-empty string.", "schema_version"))
    _validate_project(bundle.get("project"), findings)
    for key in ("work_items", "dependencies", "gates"):
        if not isinstance(bundle.get(key), list):
            findings.append(_finding("STATE-BUNDLE-003", f"{key} must be an array.", key))
    for i, work in enumerate(bundle.get("work_items", []) if isinstance(bundle.get("work_items"), list) else []):
        _validate_work_item(work, i, findings)
    for i, dep in enumerate(bundle.get("dependencies", []) if isinstance(bundle.get("dependencies"), list) else []):
        _validate_dependency(dep, i, findings)
    for i, gate in enumerate(bundle.get("gates", []) if isinstance(bundle.get("gates"), list) else []):
        _validate_gate(gate, i, findings)
    _collect_ids(bundle, findings)
    _validate_references(bundle, findings)
    _hard_cycle(findings, bundle.get("dependencies", []) if isinstance(bundle.get("dependencies"), list) else [])
    _validate_ready_done(bundle, findings)
    return findings


def has_errors(findings: Iterable[Finding]) -> bool:
    return any(f.severity == "ERROR" for f in findings)
