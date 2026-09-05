import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from smoke_test import run_smoke_test


class SmokeHarnessTests(unittest.TestCase):
    def test_disposable_smoke_harness_passes(self):
        self.assertEqual(run_smoke_test(verbose=False), 0)


if __name__ == "__main__":
    unittest.main()
