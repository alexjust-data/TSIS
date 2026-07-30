from __future__ import annotations
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent; sys.path.insert(0,str(ROOT/'src'))
suite=unittest.TestSuite()
loader=unittest.TestLoader()
for name in ('tests.unit.test_market_state_consumer','tests.unit.test_market_state_acceptance_matrix','tests.unit.test_market_state_external_review_regressions'): suite.addTests(loader.loadTestsFromName(name))
count=suite.countTestCases(); result=unittest.TextTestRunner(verbosity=2).run(suite)
if count!=36: print(f'UNEXPECTED_INCLUDED_TEST_COUNT={count}'); raise SystemExit(2)
raise SystemExit(0 if result.wasSuccessful() else 1)
