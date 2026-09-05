from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "scripts" / "build_registry.py"
CATALOG = ROOT / "catalog"

spec = importlib.util.spec_from_file_location("build_registry", REGISTRY_PATH)
build_registry = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(build_registry)


def package(name="alpha", roles=None, capabilities=None, description="", body="", runtime_status="NOT_EVALUATED", side_effect_profile=None):
    return {
        "provider": "local-skill",
        "package_path": name,
        "directory_name": name,
        "manifest_path": f"{name}/SKILL.md",
        "declared": {
            "name": name,
            "description": description,
            "roles": roles or [],
            "capabilities": capabilities or [],
            "runtime_requirements": [],
            "supported_platforms": [],
            "supported_environments": [],
            "side_effect_profile": side_effect_profile,
            "publisher": None,
        },
        "instruction_excerpt": body,
        "metadata_status": "valid",
        "runtime_status": runtime_status,
        "warnings": [],
        "errors": [],
    }


def inventory(packages, provider="local-skill"):
    return {"schema_version": "1.0", "provider": provider, "packages": packages}


class RegistryTests(unittest.TestCase):
    def test_declared_capability_has_high_confidence(self):
        registry = build_registry.build_registry([inventory([package(capabilities=["code-review"])])], CATALOG)
        cap = next(c for c in registry["specialists"][0]["capabilities"] if c["id"] == "code-review")
        self.assertEqual(cap["provenance"], "declared")
        self.assertEqual(cap["confidence"], "high")

    def test_known_specialist_is_bootstrap_not_declared(self):
        registry = build_registry.build_registry([inventory([package(name="azure-deploy")])], CATALOG)
        specialist = registry["specialists"][0]
        roles = {r["id"]: r for r in specialist["roles"]}
        self.assertEqual(roles["devops"]["provenance"], "known-specialist")
        self.assertTrue(any(c["provenance"] in {"known-specialist", "role-hint"} for c in specialist["capabilities"]))

    def test_role_inference_fallback(self):
        registry = build_registry.build_registry([inventory([package(name="mystery", description="Performs GDPR compliance review")])], CATALOG)
        specialist = registry["specialists"][0]
        role = next(r for r in specialist["roles"] if r["id"] == "security")
        self.assertEqual(role["provenance"], "inferred")

    def test_r13_runtime_unavailable_does_not_erase_capability(self):
        registry = build_registry.build_registry([inventory([package(capabilities=["testing"], runtime_status="UNAVAILABLE")])], CATALOG)
        specialist = registry["specialists"][0]
        self.assertEqual(specialist["health"], "UNAVAILABLE")
        self.assertIn("testing", {c["id"] for c in specialist["capabilities"]})

    def test_r14_read_only_instruction_conflict_degrades_health(self):
        registry = build_registry.build_registry([inventory([package(side_effect_profile="read-only", body="Deploy resources and update configuration")])], CATALOG)
        specialist = registry["specialists"][0]
        self.assertEqual(specialist["health"], "DEGRADED")
        self.assertTrue(any("read-only" in f["message"] for f in specialist["findings"]))

    def test_trust_is_not_inferred(self):
        registry = build_registry.build_registry([inventory([package()])], CATALOG)
        trust = registry["specialists"][0]["trust"]
        self.assertEqual(trust["classification"], "UNKNOWN")
        self.assertEqual(trust["source"], "not-assessed")

    def test_eligibility_is_not_evaluated(self):
        registry = build_registry.build_registry([inventory([package()])], CATALOG)
        self.assertEqual(registry["specialists"][0]["eligibility"], "NOT_EVALUATED")

    def test_multiple_provider_inventories_are_accepted(self):
        other = package(name="external")
        other["provider"] = "future-provider"
        registry = build_registry.build_registry([inventory([package(name="local")]), inventory([other], "future-provider")], CATALOG)
        self.assertEqual(registry["summary"]["specialists"], 2)
        self.assertEqual(registry["providers"], ["future-provider", "local-skill"])

    def test_schema_documents_are_valid_json(self):
        for name in ("scanner-inventory.schema.json", "capability-registry.schema.json"):
            doc = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            self.assertEqual(doc["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_catalog_documents_are_valid_and_nonempty(self):
        roles = json.loads((CATALOG / "roles.json").read_text(encoding="utf-8"))
        caps = json.loads((CATALOG / "capabilities.json").read_text(encoding="utf-8"))
        known = json.loads((CATALOG / "known-specialists.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(roles["roles"]), 10)
        self.assertGreaterEqual(len(caps["capabilities"]), 20)
        self.assertGreaterEqual(len(known["specialists"]), 50)


if __name__ == "__main__":
    unittest.main()
