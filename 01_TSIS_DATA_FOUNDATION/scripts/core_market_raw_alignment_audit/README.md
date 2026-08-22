# Core Market RAW Alignment Audit

Read-only auditor for the governed LT1B target across:

```text
ohlcv_daily
ohlcv_1m
quotes_
trades_ticks_prod_2005_2026
```

The auditor checks only physical Parquet integrity, minimum required schema and
exact `(ticker, observed_date)` alignment. It does not inspect economic market
values or modify the source roots.

Institutional design handoff:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\core_market_raw_alignment_audit\core_market_raw_alignment_audit_handoff_v0_2.md
```

## Probe

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\run_core_market_raw_alignment.ps1" `
  -Mode Probe `
  -RunId "20260821_core_market_raw_alignment_probe_v0_3"
```

The configured probe uses `AACT`, literal ticker `NA`, and `MMMW` so the same
runner exercises a common ticker plus known missing-directory cases.

## Resume

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\run_core_market_raw_alignment.ps1" `
  -Mode Probe `
  -RunId "20260821_core_market_raw_alignment_probe_v0_3" `
  -Resume
```

Committed `family × ticker` tasks are reused only when their manifests,
artifact hashes and run-contract hash still match.

## Monitor

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\monitor_core_market_raw_alignment.ps1" `
  -RunRoot "C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\20260821_core_market_raw_alignment_probe_v0_3" `
  -Watch
```

## Full run gate

The full command is deliberately rejected unless the human passes
`-HumanAuthorizedFull`. Do not provide that flag until the production-equivalent
probe, its resume replay and its output audit are closed.

Ticker directories outside the governed 4,824-member universe are reported as
context and are non-blocking. Missing governed ticker directories are blocking.

The authoritative production-equivalent probe is v0.3: 12/12 tasks committed,
2,259 Parquets inspected, zero physical/schema errors, zero remaining
`.partial` files and an exact resume replay with `adopted=12`, `reset=0`.
Its dataset verdict is `PROBE_COMPLETED_WITH_DIFFERENCES`; this certifies the
runner, not equality of the four RAW families.

## Human-authorized full run

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\run_core_market_raw_alignment.ps1" `
  -Mode Full `
  -RunId "20260821_core_market_raw_alignment_audit_v0_1" `
  -HumanAuthorizedFull
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\monitor_core_market_raw_alignment.ps1" `
  -RunRoot "C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\20260821_core_market_raw_alignment_audit_v0_1" `
  -Watch
```

After interruption, repeat the full command with `-Resume`. Never mutate the
four source roots.
