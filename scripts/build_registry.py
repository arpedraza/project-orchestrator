#!/usr/bin/env python3
"""Build a normalized Project Orchestrator capability registry from provider inventories."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
PROVENANCE_PRIORITY = {"declared": 4, "known-specialist": 3, "role-hint": 2, "inferred": 1}
CONFIDENCE_BY_SOURCE = {"declared": "high", "known-specialist": "medium", "role-hint": "medium", "inferred": "low"}
WRITE_TERMS = re.compile(r"\b(write|modify|edit|create|delete|deploy|provision|install|merge|push|update)\b", re.I)


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "unclassified"


def text_contains(text: str, needle: str) -> bool:
    needle = needle.strip().lower()
    if not needle:
        return False
    haystack = text.lower()
    if " " in needle or "-" in needle:
        return needle in haystack
    return re.search(rf"\b{re.escape(needle)}\b", haystack, re.I) is not None


def build_alias_map(capabilities: dict[str, Any]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for cid, record in capabilities.items():
        aliases[cid.lower()] = cid
        for alias in record.get("aliases", []):
            aliases[str(alias).lower()] = cid
    return aliases


def normalize_capability(value: str, alias_map: dict[str, str]) -> str:
    raw = value.strip().lower()
    return alias_map.get(raw, slugify(value))


def add_capability(store: dict[str, dict[str, str]], capability_id: str, source: str) -> None:
    candidate = {"id": capability_id, "provenance": source, "confidence": CONFIDENCE_BY_SOURCE[source]}
    existing = store.get(capability_id)
    if existing is None or PROVENANCE_PRIORITY[source] > PROVENANCE_PRIORITY[existing["provenance"]]:
        store[capability_id] = candidate


def add_role(store: dict[str, dict[str, str]], role_id: str, source: str) -> None:
    candidate = {"id": role_id, "provenance": source, "confidence": CONFIDENCE_BY_SOURCE[source]}
    existing = store.get(role_id)
    if existing is None or PROVENANCE_PRIORITY[source] > PROVENANCE_PRIORITY[existing["provenance"]]:
        store[role_id] = candidate


def classify_package(
    package: dict[str, Any],
    roles_catalog: dict[str, Any],
    capabilities_catalog: dict[str, Any],
    known_catalog: dict[str, Any],
    alias_map: dict[str, str],
) -> dict[str, Any]:
    declared = package.get("declared") or {}
    directory_name = str(package.get("directory_name") or "unknown")
    declared_name = declared.get("name") or None
    display_name = declared_name or directory_name
    known = known_catalog.get(display_name) or known_catalog.get(directory_name) or {}

    roles: dict[str, dict[str, str]] = {}
    for role in declared.get("roles") or []:
        add_role(roles, str(role), "declared")
    if not roles:
        for role in known.get("roles", []):
            add_role(roles, str(role), "known-specialist")

    searchable = "\n".join(str(value or "") for value in (display_name, declared.get("description"), package.get("instruction_excerpt")))
    if not roles:
        for role_id, role_record in roles_catalog.items():
            if any(text_contains(searchable, str(keyword)) for keyword in role_record.get("keywords", [])):
                add_role(roles, role_id, "inferred")

    capabilities: dict[str, dict[str, str]] = {}
    for capability in declared.get("capabilities") or []:
        add_capability(capabilities, normalize_capability(str(capability), alias_map), "declared")
    for capability in known.get("capability_hints", []):
        add_capability(capabilities, normalize_capability(str(capability), alias_map), "known-specialist")
    for role in roles.values():
        role_id = role["id"]
        for cid, cap_record in capabilities_catalog.items():
            if role_id in cap_record.get("role_hints", []):
                add_capability(capabilities, cid, "role-hint")
    for cid, cap_record in capabilities_catalog.items():
        if any(text_contains(searchable, str(alias)) for alias in [cid, *cap_record.get("aliases", [])]):
            add_capability(capabilities, cid, "inferred")

    findings = [
        {"severity": "warning", "source": "scanner", "message": message}
        for message in package.get("warnings", [])
    ] + [
        {"severity": "error", "source": "scanner", "message": message}
        for message in package.get("errors", [])
    ]

    side_effect = declared.get("side_effect_profile")
    side_effect_values = side_effect if isinstance(side_effect, list) else ([side_effect] if side_effect else [])
    if any(str(v).strip().lower() in {"read-only", "readonly", "read_only"} for v in side_effect_values) and WRITE_TERMS.search(str(package.get("instruction_excerpt") or "")):
        findings.append({
            "severity": "warning",
            "source": "registry-validation",
            "message": "declared read-only side-effect profile conflicts with write/change instructions",
        })

    metadata_status = package.get("metadata_status", "invalid")
    runtime_status = str(package.get("runtime_status") or "NOT_EVALUATED").upper()
    provider_health = str(package.get("provider_health") or "").upper()
    if provider_health == "QUARANTINED":
        health = "QUARANTINED"
    elif metadata_status == "invalid" or any(f["severity"] == "error" for f in findings) or runtime_status == "UNAVAILABLE":
        health = "UNAVAILABLE"
    elif findings or runtime_status == "DEGRADED":
        health = "DEGRADED"
    else:
        health = "AVAILABLE"

    provider = str(package.get("provider") or "unknown-provider")
    package_path = str(package.get("package_path") or directory_name)
    specialist_id = f"{provider}:{package_path}"
    return {
        "specialist_id": specialist_id,
        "provider": provider,
        "package_path": package_path,
        "identity": {
            "directory_name": directory_name,
            "declared_name": declared_name,
            "display_name": display_name,
        },
        "roles": sorted(roles.values(), key=lambda r: r["id"]),
        "capabilities": sorted(capabilities.values(), key=lambda c: c["id"]),
        "runtime_requirements": declared.get("runtime_requirements") or [],
        "supported_platforms": declared.get("supported_platforms") or [],
        "supported_environments": declared.get("supported_environments") or [],
        "side_effect_profile": side_effect,
        "trust": {"classification": "UNKNOWN", "source": "not-assessed"},
        "health": health,
        "validation_level": "STATIC",
        "runtime_status": runtime_status,
        "eligibility": "NOT_EVALUATED",
        "findings": findings,
    }


def build_registry(inventories: list[dict[str, Any]], catalog_dir: Path) -> dict[str, Any]:
    roles_doc = load_json(catalog_dir / "roles.json")
    capabilities_doc = load_json(catalog_dir / "capabilities.json")
    known_doc = load_json(catalog_dir / "known-specialists.json")
    roles_catalog = roles_doc.get("roles", {})
    capabilities_catalog = capabilities_doc.get("capabilities", {})
    known_catalog = known_doc.get("specialists", {})
    alias_map = build_alias_map(capabilities_catalog)

    specialists: dict[str, dict[str, Any]] = {}
    providers: set[str] = set()
    for inventory in inventories:
        provider = str(inventory.get("provider") or "unknown-provider")
        providers.add(provider)
        for package in inventory.get("packages", []):
            record = classify_package(package, roles_catalog, capabilities_catalog, known_catalog, alias_map)
            specialists[record["specialist_id"]] = record

    ordered = [specialists[key] for key in sorted(specialists)]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "providers": sorted(providers),
        "specialists": ordered,
        "summary": {
            "specialists": len(ordered),
            "available": sum(s["health"] == "AVAILABLE" for s in ordered),
            "degraded": sum(s["health"] == "DEGRADED" for s in ordered),
            "unavailable": sum(s["health"] == "UNAVAILABLE" for s in ordered),
            "quarantined": sum(s["health"] == "QUARANTINED" for s in ordered),
        },
    }


def render_markdown(registry: dict[str, Any]) -> str:
    lines = [
        "# Capability Registry",
        "",
        "| Specialist | Health | Roles | Capabilities | Trust |",
        "|------------|--------|-------|--------------|-------|",
    ]
    for specialist in registry["specialists"]:
        name = specialist["identity"]["display_name"]
        roles = ", ".join(r["id"] for r in specialist["roles"]) or "unclassified"
        capabilities = ", ".join(c["id"] for c in specialist["capabilities"]) or "unclassified"
        trust = specialist["trust"]["classification"]
        lines.append(f"| `{name}` | {specialist['health']} | {roles} | {capabilities} | {trust} |")
    lines.append("")
    lines.append(f"Total specialists: {registry['summary']['specialists']}")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a Project Orchestrator capability registry")
    parser.add_argument("--inventory", action="append", required=True, help="Provider inventory JSON file; repeatable")
    default_catalog = Path(__file__).resolve().parent.parent / "catalog"
    parser.add_argument("--catalog-dir", default=str(default_catalog))
    parser.add_argument("--format", choices=("json", "markdown"), default="json", dest="output_format")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        inventories = [load_json(Path(path)) for path in args.inventory]
        registry = build_registry(inventories, Path(args.catalog_dir))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"build-registry: {exc}", file=sys.stderr)
        return 2

    if args.output_format == "json":
        json.dump(registry, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_markdown(registry))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
