"""Focused non-physical tests for the exact BT-GATE-015 V0.3 path."""
from __future__ import annotations

import unittest

from tests.unit.test_bt_gate_015_single_use_physical_v0_3 import (
    PhysicalEventStateV03CanonicalTests,
    PhysicalEventStateV03Tests,
)

suite = unittest.TestSuite()
loader = unittest.defaultTestLoader
suite.addTests(loader.loadTestsFromTestCase(PhysicalEventStateV03Tests))
suite.addTests(loader.loadTestsFromTestCase(PhysicalEventStateV03CanonicalTests))
count = suite.countTestCases()
if count != 21:
    raise SystemExit(f"UNEXPECTED_BT_GATE_015_V0_3_TEST_COUNT={count}")
result = unittest.TextTestRunner(verbosity=2).run(suite)
print(f"BT_GATE_015_V0_3_PREEXECUTION_TEST_COUNT={count}")
raise SystemExit(0 if result.wasSuccessful() else 1)
