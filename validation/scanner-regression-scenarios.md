# Project Orchestrator v2 — Scanner Regression Scenario Manifest

> **Status:** CHG-002 executable regression contract.
> **Current scanner:** `scripts/scan-skills.sh` is the compatibility entry point for the Python scanner implementation.

## Purpose

Define the scanner/discovery behaviors covered while the existing Bash scanner is hardened and the capability registry is introduced.

## R01 — Simple frontmatter

**Given:** A direct child skill package has `SKILL.md` with scalar `name`, one-line `description`, and scalar `role`.

**Expected:** The package is discovered once; declared values are preserved; metadata status is valid.

## R02 — Multiline YAML description

**Given:** `description` uses valid YAML block/folded multiline syntax.

**Expected:** The parser reads the complete logical value rather than returning blank/truncated metadata because it assumes one physical line.

## R03 — Multiple roles

**Given:** `role` is a YAML list such as `[project-manager, scriber]` or equivalent multiline list.

**Expected:** All declared roles are preserved as declared metadata. The scanner does not collapse the field into an invalid scalar representation.

## R04 — Explicit capabilities

**Given:** A future-compatible manifest declares multiple capabilities.

**Expected:** The scanner reports the declarations without deciding task suitability. Capability classification/normalization happens in the registry/analyzer layer.

## R05 — Missing `SKILL.md`

**Given:** A direct child directory exists but does not contain a skill manifest.

**Expected:** It is not counted as a discovered skill package. The scanner behavior is deterministic and may report an informational validation finding without creating a false skill record.

## R06 — Missing scan root

**Given:** The configured skill root does not exist or cannot be read.

**Expected:** The scanner returns a clear failure/non-success result rather than a misleading successful empty registry.

## R07 — Directory/manifest identity mismatch

**Given:** The directory name and declared manifest `name` differ.

**Expected:** Both identities are retained and a validation warning/finding is produced. The scanner does not silently overwrite one with the other.

## R08 — Nested package behavior

**Given:** Nested directories contain additional `SKILL.md` files beneath a direct child package.

**Expected:** Discovery follows the explicitly chosen package-boundary rule: only direct child skill packages are enumerated unless a future provider explicitly supports namespaced/recursive packages.

## R09 — Accurate result count

**Given:** The skill root contains valid direct child packages plus nested/non-skill directories.

**Expected:** The reported total uses exactly the same enumeration/package-boundary semantics as the listed records. Listed count and total cannot disagree because one is recursive and the other is not.

## R10 — Machine-readable output validity

**Given:** The scanner is invoked in machine-readable mode.

**Expected:** Output is syntactically valid, deterministic enough for registry ingestion, and contains raw inventory/metadata status without requiring the registry to parse a Markdown table.

## R11 — Human-readable output

**Given:** The scanner is invoked in human-readable mode or a registry summary is rendered from machine data.

**Expected:** The output remains easy to inspect while clearly distinguishing declared metadata from inferred/registry-level conclusions.

## R12 — Executable wrapper compatibility

**Given:** Existing callers execute `bash scripts/scan-skills.sh`.

**Expected:** The shell entry point remains usable while richer parsing/validation is delegated to the Python implementation utility.

## R13 — Health/runtime separation

**Given:** A skill declares a valid capability but a required runtime/tool/connection is absent.

**Expected:** The capability remains part of the specialist profile while current health becomes unavailable/degraded. Discovery does not erase capability because runtime is temporarily missing. Task-time eligibility is still not evaluated in CHG-002.

## R14 — Metadata/instruction conflict

**Given:** Manifest metadata says the specialist is read-only while its instructions clearly require write/deploy side effects.

**Expected:** Validation produces a conflict finding; frontmatter is not blindly trusted as the final capability/side-effect profile.

## Automation mapping

| Scenario | Automated coverage |
|---|---|
| R01–R12 | `tests/test_scan_skills.py` |
| R13–R14 | `tests/test_registry.py` |

The suite uses standard-library `unittest` and temporary filesystem fixtures. CI runs the suite on every push and pull request. Task routing, trust decisions, autonomous installation, and task-time runtime checks remain outside CHG-002.
