from __future__ import annotations
import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
suite=unittest.TestSuite([
    unittest.defaultTestLoader.loadTestsFromName('tests.unit.test_bt_gate_014_single_use_physical_v0_5'),
    unittest.defaultTestLoader.loadTestsFromName('tests.unit.test_market_state_restriction_domains'),
])
count=suite.countTestCases()
result=unittest.TextTestRunner(verbosity=2).run(suite)
print(f'V0_5_PREEXECUTION_TEST_COUNT={count}')
raise SystemExit(0 if result.wasSuccessful() else 1)

