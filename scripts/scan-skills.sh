#!/usr/bin/env bash
# Compatibility entry point for Project Orchestrator local skill discovery.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/scan_skills.py" "$@"
