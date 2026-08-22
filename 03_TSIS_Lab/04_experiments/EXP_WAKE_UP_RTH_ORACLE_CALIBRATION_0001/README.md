# EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001

Status: `full_candidate_complete_repair_probe_pass_full_panel_rebuild_pending_human_launch`

## Question

How can TSIS identify and retrospectively adjudicate, without Binding A/B
circularity, the first observable transition from within-RTH dormancy to
material anomalous realized participation?

## Scope

```text
development only = 2011-01-03 .. 2022-12-30
targets = frozen TA-3 2,400 instrument-sessions
source = official G legacy RTH trades
observation = open-exclusive / close-exclusive symbol-seconds
```

## Authority

The master execution plan is:

```text
C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/04_EVENTS/WAKE_UP/
03_LABELS/WAKE_UP_RTH_ORACLE_CALIBRATION_END_TO_END_v0_1.md
```

## Outputs

Heavy outputs are written only below:

```text
G:/TSIS/data/research_experiments/
EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001/runs/<run_id>/
```

The full run is human-launched under `LONG_RUNNING_OPERATIONS_CONTRACT.md`.
Agents may execute unit tests and bounded smoke/probe runs.

## Current certified state

```text
unit tests                    = 6 passed
probe shards                  = D1, D2, D3, D4
probe targets                 = 4/4
probe failures                = 0
repair probe validation       = 25/25 PASS
full preflight targets        = 2,400
full candidate run            = COMPLETE 2,400/2,400
full candidates               = 4,447
initial full blind panel      = INVALID, 240/240 CLOSE_240M_PLUS
full repaired panel           = PENDING HUMAN LAUNCH
```

Governed readout:

```text
C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/04_EVENTS/WAKE_UP/
03_LABELS/
WAKE_UP_RTH_ORACLE_CALIBRATION_IMPLEMENTATION_AND_PROBE_READOUT_v0_1.md
```

## Human full panel repair

```powershell
& "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\scripts\rebuild_wake_up_rth_blind_panel.ps1" -RunRoot "G:\TSIS\data\research_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\runs\wake_up_rth_full_v0_1_20260817" -RepairId "blind_panel_rth_stratification_v0_2"
```

Monitor:

```powershell
& "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\scripts\monitor_wake_up_rth_blind_panel_repair.ps1" -RunRoot "G:\TSIS\data\research_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\runs\wake_up_rth_full_v0_1_20260817" -RepairId "blind_panel_rth_stratification_v0_2" -IntervalSeconds 10 -Compact -Watch
```

Resume reuses the same `RepairId` and adds `-Resume`. The 2,400-session
candidate search is not repeated.
