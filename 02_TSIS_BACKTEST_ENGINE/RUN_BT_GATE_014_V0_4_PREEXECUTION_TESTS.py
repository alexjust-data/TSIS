from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

suite = unittest.defaultTestLoader.loadTestsFromName(
    "tests.unit.test_bt_gate_014_single_use_physical_v0_4"
)
count = suite.countTestCases()
result = unittest.TextTestRunner(verbosity=2).run(suite)
if count != 18:
    print(f"UNEXPECTED_V0_4_PREEXECUTION_TEST_COUNT={count}")
    raise SystemExit(2)
raise SystemExit(0 if result.wasSuccessful() else 1)
