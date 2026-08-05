# Reproduce BT-GATE-015 R2

From the extracted `02_TSIS_BACKTEST_ENGINE` directory, create a clean virtual
environment and run:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -B RUN_FULL_REPOSITORY_TESTS.py
.\.venv\Scripts\python -B RUN_BT_GATE_015_NON_PHYSICAL.py
```

`pyproject.toml` declares `pyarrow>=21`; installation is required because the
full historical regression suite contains Parquet-based market-bar tests.

Expected R2 results:

```text
full repository suite = 235 tests PASS
BT-GATE-015 focused tests = 13 PASS
deterministic_output_hash =
7d58f4b8bc68dc7cbe5abfe30d5d0c7cf981496dc2d288d1db45693ed9cb8596
Event State physical rows read = 0
```

Do not execute or construct any physical Event State consumer authorization.
