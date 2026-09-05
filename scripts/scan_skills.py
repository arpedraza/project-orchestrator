#!/usr/bin/env python3
"""Deterministic local skill discovery for Project Orchestrator v2.

This scanner is intentionally limited to discovery and manifest parsing. It does not
make task-routing, trust, authorization, or final capability-eligibility decisions.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
SUPPORTED_LIST_FIELDS = {"role", "roles", "capability", "capabilities", "runtime_requirements", "supported_platforms", "supported_environments", "side_effect_profile"}


class FrontmatterError(ValueError):
    pass


def _strip_comment(value: str) -> str:
    """Strip a simple unquoted YAML comment from a scalar."""
    in_single = False
    in_double = False
    escaped = False
    for i, ch in enumerate(value):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and in_double:
            escaped = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            if i == 0 or value[i - 1].isspace():
                return value[:i].rstrip()
    return value.rstrip()


def _parse_quoted(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise FrontmatterError(f"invalid double-quoted scalar: {exc}") from exc
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def _split_inline_list(inner: str) -> list[str]:
    items: list[str] = []
    buf: list[str] = []
    in_single = False
    in_double = False
    escaped = False
    for ch in inner:
        if escaped:
            buf.append(ch)
            escaped = False
            continue
        if ch == "\\" and in_double:
            buf.append(ch)
            escaped = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            buf.append(ch)
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            buf.append(ch)
            continue
        if ch == "," and not in_single and not in_double:
            item = "".join(buf).strip()
            if item:
                items.append(_parse_quoted(_strip_comment(item)))
            buf = []
        else:
            buf.append(ch)
    if in_single or in_double:
        raise FrontmatterError("unterminated quoted value in inline list")
    item = "".join(buf).strip()
    if item:
        items.append(_parse_quoted(_strip_comment(item)))
    return items


def _parse_scalar(value: str) -> Any:
    value = _strip_comment(value.strip())
    if value.startswith("["):
        if not value.endswith("]"):
            raise FrontmatterError("unterminated inline list")
        return _split_inline_list(value[1:-1])
    return _parse_quoted(value)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str, list[str]]:
    """Parse the supported YAML-frontmatter subset and return metadata/body/warnings."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("missing opening YAML frontmatter delimiter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise FrontmatterError("missing closing YAML frontmatter delimiter") from exc

    fm_lines = lines[1:end]
    body = "\n".join(lines[end + 1 :]).strip()
    metadata: dict[str, Any] = {}
    warnings: list[str] = []
    i = 0
    while i < len(fm_lines):
        raw = fm_lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        if raw[:1].isspace():
            raise FrontmatterError(f"unexpected indentation at frontmatter line {i + 2}")
        match = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", raw)
        if not match:
            raise FrontmatterError(f"unsupported frontmatter syntax at line {i + 2}: {raw!r}")
        key, value = match.group(1), match.group(2)
        if key in metadata:
            warnings.append(f"duplicate key '{key}' encountered; last value wins")

        if value in {"|", ">"}:
            style = value
            block: list[str] = []
            i += 1
            while i < len(fm_lines):
                candidate = fm_lines[i]
                if candidate and not candidate[:1].isspace():
                    break
                if not candidate.strip():
                    block.append("")
                else:
                    block.append(candidate.lstrip())
                i += 1
            if style == "|":
                metadata[key] = "\n".join(block).rstrip()
            else:
                paragraphs: list[str] = []
                current: list[str] = []
                for item in block:
                    if item == "":
                        if current:
                            paragraphs.append(" ".join(current))
                            current = []
                        paragraphs.append("")
                    else:
                        current.append(item)
                if current:
                    paragraphs.append(" ".join(current))
                metadata[key] = "\n".join(paragraphs).rstrip()
            continue

        if value == "":
            seq: list[str] = []
            j = i + 1
            while j < len(fm_lines):
                candidate = fm_lines[j]
                m_item = re.match(r"^\s+-\s+(.*)$", candidate)
                if not m_item:
                    break
                seq.append(_parse_quoted(_strip_comment(m_item.group(1).strip())))
                j += 1
            if seq:
                metadata[key] = seq
                i = j
                continue
            metadata[key] = ""
            i += 1
            continue

        metadata[key] = _parse_scalar(value)
        i += 1

    for key in SUPPORTED_LIST_FIELDS:
        if key in metadata and isinstance(metadata[key], str) and key in {"roles", "capabilities", "runtime_requirements", "supported_platforms", "supported_environments"}:
            warnings.append(f"'{key}' is expected to be a list; scalar preserved")
    return metadata, body, warnings


def _as_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [str(value).strip()] if str(value).strip() else []


def discover_skill(skill_dir: Path, root: Path) -> dict[str, Any] | None:
    manifest = skill_dir / "SKILL.md"
    if not manifest.is_file():
        return None

    warnings: list[str] = []
    errors: list[str] = []
    metadata: dict[str, Any] = {}
    body = ""
    try:
        text = manifest.read_text(encoding="utf-8")
        metadata, body, parse_warnings = parse_frontmatter(text)
        warnings.extend(parse_warnings)
    except (OSError, UnicodeError, FrontmatterError) as exc:
        errors.append(str(exc))

    directory_name = skill_dir.name
    declared_name = str(metadata.get("name") or "").strip() or None
    if declared_name and declared_name != directory_name:
        warnings.append(f"directory name '{directory_name}' differs from declared name '{declared_name}'")
    if not declared_name:
        warnings.append("manifest does not declare a non-empty name")

    roles = _as_list(metadata.get("roles")) or _as_list(metadata.get("role"))
    capabilities = _as_list(metadata.get("capabilities")) or _as_list(metadata.get("capability"))
    description = str(metadata.get("description") or "").strip()
    if not description:
        warnings.append("manifest does not declare a non-empty description")

    status = "invalid" if errors else ("warning" if warnings else "valid")
    rel_path = skill_dir.relative_to(root).as_posix()
    return {
        "provider": "local-skill",
        "package_path": rel_path,
        "directory_name": directory_name,
        "manifest_path": f"{rel_path}/SKILL.md",
        "declared": {
            "name": declared_name,
            "description": description,
            "roles": roles,
            "capabilities": capabilities,
            "runtime_requirements": _as_list(metadata.get("runtime_requirements")),
            "supported_platforms": _as_list(metadata.get("supported_platforms")),
            "supported_environments": _as_list(metadata.get("supported_environments")),
            "side_effect_profile": metadata.get("side_effect_profile"),
            "publisher": metadata.get("publisher"),
        },
        "instruction_excerpt": body[:4000],
        "metadata_status": status,
        "runtime_status": "NOT_EVALUATED",
        "warnings": warnings,
        "errors": errors,
    }


def scan(root: Path) -> dict[str, Any]:
    if not root.exists():
        raise FileNotFoundError(f"skill root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"skill root is not a directory: {root}")
    if not os.access(root, os.R_OK | os.X_OK):
        raise PermissionError(f"skill root is not readable: {root}")

    packages: list[dict[str, Any]] = []
    skipped_directories: list[str] = []
    for child in sorted((p for p in root.iterdir() if p.is_dir()), key=lambda p: p.name.casefold()):
        record = discover_skill(child, root)
        if record is None:
            skipped_directories.append(child.name)
        else:
            packages.append(record)

    return {
        "schema_version": SCHEMA_VERSION,
        "provider": "local-skill",
        "scanned_root": str(root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "package_boundary": "direct-child-directory-with-SKILL.md",
        "packages": packages,
        "summary": {
            "skills_found": len(packages),
            "valid": sum(p["metadata_status"] == "valid" for p in packages),
            "warnings": sum(p["metadata_status"] == "warning" for p in packages),
            "invalid": sum(p["metadata_status"] == "invalid" for p in packages),
            "skipped_directories": skipped_directories,
        },
    }


def render_markdown(inventory: dict[str, Any]) -> str:
    lines = [
        "# Skill Registry Scan",
        f"Scanned: {inventory['generated_at']}",
        "",
        "| Skill | Description (first 120 chars) | Role(s) (declared) | Status |",
        "|-------|-------------------------------|--------------------|--------|",
    ]
    for package in inventory["packages"]:
        name = package["declared"]["name"] or package["directory_name"]
        description = package["declared"]["description"].replace("\n", " ")[:120] or "(no description)"
        roles = ", ".join(package["declared"]["roles"]) or "auto-infer"
        lines.append(f"| `{name}` | {description} | {roles} | {package['metadata_status']} |")
    lines.extend([
        "",
        "---",
        f"Total skills found: {inventory['summary']['skills_found']}",
        "",
        "Run 'cat skills/<name>/SKILL.md' to read full skill details.",
    ])
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan local Project Orchestrator skills")
    parser.add_argument("skills_dir", nargs="?", default="skills", help="Root containing direct child skill packages")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", dest="output_format")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        inventory = scan(Path(args.skills_dir))
    except (OSError, ValueError) as exc:
        print(f"scan-skills: {exc}", file=sys.stderr)
        return 2

    if args.output_format == "json":
        json.dump(inventory, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_markdown(inventory))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
