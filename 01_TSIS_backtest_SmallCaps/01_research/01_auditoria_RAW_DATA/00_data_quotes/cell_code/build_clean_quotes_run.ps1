[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\TSIS_Data\02_backtest_SmallCaps",
    [string]$RunId = "20260319_quotes_clean_v2_draft",
    [string]$QuotesRoot = "D:\quotes_clean_v2",
    [string]$RunDateFrom = "2005-01-01",
    [string]$RunDateTo = "2025-12-31",
    [int]$Concurrent = 24,
    [int]$TaskBatchSize = 500
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRootPath = [System.IO.Path]::GetFullPath($ProjectRoot)
$runDir = Join-Path $projectRootPath ("runs\polygon_realtime_audit\" + $RunId)
$inputsDir = Join-Path $runDir "inputs"
New-Item -ItemType Directory -Force -Path $inputsDir | Out-Null

$requiredPaths = @{
    universe_refined = Join-Path $projectRootPath "data\reference\universe_pti\tickers_2005_2026_upper_excluding_ohlcv_1m_missing_vs_daily_ge_2B_or_null.parquet"
    official_lifecycle = Join-Path $projectRootPath "data\reference\official_lifecycle_compiled.csv"
}

$missing = @()
foreach ($entry in $requiredPaths.GetEnumerator()) {
    if (-not (Test-Path $entry.Value)) {
        $missing += "$($entry.Key): $($entry.Value)"
    }
}
if ($missing.Count -gt 0) {
    Write-Error ("Faltan artefactos requeridos:`n - " + ($missing -join "`n - "))
}

$outputs = @{
    tickers = Join-Path $inputsDir "tickers_quotes_prod_v2_clean.csv"
    tasks = Join-Path $inputsDir "tasks_quotes_prod_v2_clean.csv"
    meta = Join-Path $inputsDir "tasks_quotes_prod_v2_clean.meta.json"
}

$pythonScript = @'
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


project_root = Path(r"__PROJECT_ROOT__")
run_id = "__RUN_ID__"
run_dir = Path(r"__RUN_DIR__")
quotes_root = Path(r"__QUOTES_ROOT__")
run_date_from = pd.Timestamp("__RUN_DATE_FROM__")
run_date_to = pd.Timestamp("__RUN_DATE_TO__")

universe_refined = Path(r"__REQ_universe_refined__")
official_lifecycle = Path(r"__REQ_official_lifecycle__")

tickers_out = Path(r"__OUT_tickers__")
tasks_out = Path(r"__OUT_tasks__")
meta_out = Path(r"__OUT_meta__")

u = pd.read_parquet(universe_refined)
lc = pd.read_csv(official_lifecycle)

u["ticker"] = u["ticker"].astype(str).str.upper().str.strip()
lc["ticker"] = lc["ticker"].astype(str).str.upper().str.strip()
lc["list_date"] = pd.to_datetime(lc["list_date"], errors="coerce")
lc["delist_date"] = pd.to_datetime(lc["delist_date"], errors="coerce")

base = lc[lc["ticker"].isin(set(u["ticker"]))].copy()
base["run_start"] = base["list_date"].clip(lower=run_date_from)
base["run_end"] = base["delist_date"].fillna(run_date_to).clip(upper=run_date_to)
base = base.dropna(subset=["ticker", "run_start", "run_end"]).copy()
base = base[base["run_end"] >= base["run_start"]].copy()
base = (
    base.sort_values(["ticker", "run_start", "run_end"])
    .drop_duplicates(subset=["ticker"], keep="first")
    .reset_index(drop=True)
)

tickers_df = base.copy()
tickers_df["run_start"] = tickers_df["run_start"].dt.strftime("%Y-%m-%d")
tickers_df["run_end"] = tickers_df["run_end"].dt.strftime("%Y-%m-%d")
tickers_df.to_csv(tickers_out, index=False, encoding="utf-8")

task_rows = []
for row in base.itertuples(index=False):
    days = pd.bdate_range(row.run_start.date(), row.run_end.date())
    if len(days) == 0:
        continue
    task_rows.extend(
        {
            "ticker": row.ticker,
            "date": d.strftime("%Y-%m-%d"),
        }
        for d in days
    )

tasks_df = pd.DataFrame(task_rows)
if tasks_df.empty:
    tasks_df = pd.DataFrame(columns=["ticker", "date"])
tasks_df = tasks_df.drop_duplicates(["ticker", "date"]).sort_values(["ticker", "date"]).reset_index(drop=True)
tasks_df.to_csv(tasks_out, index=False, encoding="utf-8")

meta = {
    "run_id": run_id,
    "quotes_root": str(quotes_root),
    "universe_path": str(universe_refined),
    "lifecycle_path": str(official_lifecycle),
    "tickers_csv": str(tickers_out),
    "tasks_csv": str(tasks_out),
    "calendar_policy": "business_day_intersection_with_run_window",
    "run_date_from": str(run_date_from.date()),
    "run_date_to": str(run_date_to.date()),
    "tickers_count": int(tickers_df["ticker"].nunique()) if "ticker" in tickers_df.columns else 0,
    "tasks_total": int(len(tasks_df)),
    "date_min": str(tasks_df["date"].min()) if len(tasks_df) else None,
    "date_max": str(tasks_df["date"].max()) if len(tasks_df) else None,
}
meta_out.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(meta, indent=2, ensure_ascii=False))
'@

foreach ($key in $requiredPaths.Keys) {
    $pythonScript = $pythonScript.Replace(("__REQ_${key}__"), ($requiredPaths[$key] -replace "\\", "\\"))
}
foreach ($key in $outputs.Keys) {
    $pythonScript = $pythonScript.Replace(("__OUT_${key}__"), ($outputs[$key] -replace "\\", "\\"))
}
$pythonScript = $pythonScript.Replace("__PROJECT_ROOT__", ($projectRootPath -replace "\\", "\\"))
$pythonScript = $pythonScript.Replace("__RUN_ID__", $RunId)
$pythonScript = $pythonScript.Replace("__RUN_DIR__", ($runDir -replace "\\", "\\"))
$pythonScript = $pythonScript.Replace("__QUOTES_ROOT__", ($QuotesRoot -replace "\\", "\\"))
$pythonScript = $pythonScript.Replace("__RUN_DATE_FROM__", $RunDateFrom)
$pythonScript = $pythonScript.Replace("__RUN_DATE_TO__", $RunDateTo)

Write-Host "Materializando run limpio quotes..." -ForegroundColor Cyan
Write-Host "  run_id       : $RunId"
Write-Host "  run_dir      : $runDir"
Write-Host "  quotes_root  : $QuotesRoot"
Write-Host "  run_date_from: $RunDateFrom"
Write-Host "  run_date_to  : $RunDateTo"

$pythonScript | python -

$agent01Cmd = 'python "{0}" --csv "{1}" --output "{2}" --concurrent {3} --run-id "{4}" --run-dir "{5}" --resume --task-batch-size {6}' -f `
    (Join-Path $projectRootPath "scripts\download_quotes.py"), `
    $outputs.tasks, `
    $QuotesRoot, `
    $Concurrent, `
    $RunId, `
    $runDir, `
    $TaskBatchSize

Write-Host ""
Write-Host "Artifacts:" -ForegroundColor Green
Write-Host "  $($outputs.tickers)"
Write-Host "  $($outputs.tasks)"
Write-Host "  $($outputs.meta)"
Write-Host ""
Write-Host "Agent01 command:" -ForegroundColor Green
Write-Host $agent01Cmd
