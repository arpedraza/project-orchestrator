#!/usr/bin/env python3
"""CLI for Project Orchestrator v2 CHG-003 state validation."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from state_model import has_errors, validate_state_bundle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a Project Orchestrator v2 state bundle.")
    parser.add_argument("state_file", help="Path to state-bundle JSON.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    path = Path(args.state_file)
    try:
        with path.open("r", encoding="utf-8") as handle:
            bundle = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        if args.format == "json":
            print(json.dumps({"valid": False, "load_error": str(exc), "findings": []}, indent=2))
        else:
            print(f"LOAD ERROR: {exc}", file=sys.stderr)
        return 2

    findings = validate_state_bundle(bundle)
    valid = not has_errors(findings)
    if args.format == "json":
        print(json.dumps({"valid": valid, "findings": [f.to_dict() for f in findings]}, indent=2, sort_keys=True))
    elif valid:
        print("VALID")
    else:
        for finding in findings:
            suffix = f" [{finding.path}]" if finding.path else ""
            print(f"{finding.severity} {finding.code}: {finding.message}{suffix}")
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
