from __future__ import annotations
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent; sys.path.insert(0,str(ROOT/'src'))
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py',top_level_dir=str(ROOT)); count=suite.countTestCases(); result=unittest.TextTestRunner(verbosity=1).run(suite)
if count!=235: print(f'UNEXPECTED_FULL_TEST_COUNT={count}'); raise SystemExit(2)
raise SystemExit(0 if result.wasSuccessful() else 1)

