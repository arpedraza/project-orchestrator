# Scanner and Registry Tests

CHG-002 uses Python's standard-library `unittest` framework. Test cases create isolated temporary skill-package fixtures so malformed/missing/nested layouts can be exercised without polluting the repository with fake installed skills.

- `test_scan_skills.py` maps the scanner behaviors in `validation/scanner-regression-scenarios.md` to executable regression tests.
- `test_registry.py` covers declared/inferred provenance, bootstrap catalog behavior, health/runtime separation, trust non-inference, multi-provider ingestion, and JSON catalog/schema integrity.

Run locally with:

```bash
python3 -m unittest discover -s tests -v
```
