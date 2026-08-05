# Reproduce BT-GATE-015 V0.3

From the extracted package root:

```powershell
cd 02_TSIS_BACKTEST_ENGINE
python -B RUN_BT_GATE_015_NON_PHYSICAL.py
python -B -m unittest tests.unit.test_event_state_consumer tests.unit.test_event_state_runner
python -B RUN_FULL_REPOSITORY_TESTS.py
cd ..\00_CTO\14_BACKTEST_ENGINE
python -B 10_VALIDATION\validate_governance.py
```

Expected boundaries:

```text
Event State physical files opened = 0
Event State physical rows read = 0
single-use physical authorization = NOT_AUTHORIZED
BT-GATE-015 acceptance = PENDING_EXTERNAL_REVIEW
```
