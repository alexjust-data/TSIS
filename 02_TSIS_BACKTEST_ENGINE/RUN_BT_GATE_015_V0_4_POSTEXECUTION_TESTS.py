"""Focused tests for the consumed BT-GATE-015 V0.4 physical result."""
from __future__ import annotations

import unittest

from tests.unit.test_bt_gate_015_single_use_physical_v0_4 import (
    PhysicalEventStateV04CanonicalTests,
    PhysicalEventStateV04Tests,
)

suite = unittest.TestSuite()
loader = unittest.defaultTestLoader
suite.addTests(loader.loadTestsFromTestCase(PhysicalEventStateV04Tests))
suite.addTests(loader.loadTestsFromTestCase(PhysicalEventStateV04CanonicalTests))
count = suite.countTestCases()
if count != 25:
    raise SystemExit(f"UNEXPECTED_BT_GATE_015_V0_4_POSTEXECUTION_TEST_COUNT={count}")
result = unittest.TextTestRunner(verbosity=2).run(suite)
print(f"BT_GATE_015_V0_4_POSTEXECUTION_TEST_COUNT={count}")
raise SystemExit(0 if result.wasSuccessful() else 1)
