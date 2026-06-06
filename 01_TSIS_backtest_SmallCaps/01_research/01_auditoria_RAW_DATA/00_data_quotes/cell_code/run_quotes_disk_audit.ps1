[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\TSIS_Data\02_backtest_SmallCaps",
    [string]$RunId = "20260313_quotes_prod_full_12133_clean",
    [string]$QuotesRoot = "D:\quotes",
    [string]$OutputPrefix = "live_audit",
    [int]$MaxFiles = 0,
    [int]$ProgressEvery = 10000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRootPath = [System.IO.Path]::GetFullPath($ProjectRoot)
$runDir = Join-Path $projectRootPath ("runs\polygon_realtime_audit\" + $RunId)
$inputsDir = Join-Path $runDir "inputs"

$requiredPaths = @{
    universe_refined = Join-Path $projectRootPath "data\reference\universe_pti\tickers_2005_2026_upper_excluding_ohlcv_1m_missing_vs_daily_ge_2B_or_null.parquet"
    official_lifecycle = Join-Path $projectRootPath "data\reference\official_lifecycle_compiled.csv"
    tickers_prod = Join-Path $inputsDir "tickers_quotes_prod.csv"
    tasks_master = Join-Path $inputsDir "tasks_quotes_prod.csv"
    tasks_meta = Join-Path $inputsDir "tasks_quotes_prod_meta.json"
    tasks_recovery = Join-Path $inputsDir "tasks_quotes_prod_missing_only_final_v2.csv"
    download_events_current = Join-Path $runDir "download_events_current.csv"
    quotes_agent_strict_current = Join-Path $runDir "quotes_agent_strict_events_current.csv"
}

$optionalPaths = @{
    download_events_history = Join-Path $runDir "download_events_history.csv"
    download_state = Join-Path $runDir "download_state.json"
    download_live_status = Join-Path $runDir "download_live_status.json"
}

$missing = @()
foreach ($entry in $requiredPaths.GetEnumerator()) {
    if (-not (Test-Path $entry.Value)) {
        $missing += "$($entry.Key): $($entry.Value)"
    }
}

if (-not (Test-Path $QuotesRoot)) {
    $missing += "quotes_root: $QuotesRoot"
}

if ($missing.Count -gt 0) {
    Write-Error ("Faltan artefactos requeridos:`n - " + ($missing -join "`n - "))
}

$outputPaths = @{
    disk_inventory = Join-Path $runDir ("disk_quotes_inventory_taskkey_" + $OutputPrefix + ".csv")
    compare_master = Join-Path $runDir ("audit_disk_vs_master_" + $OutputPrefix + ".csv")
    master_missing = Join-Path $runDir ("audit_master_missing_on_disk_" + $OutputPrefix + ".csv")
    disk_not_in_master = Join-Path $runDir ("audit_disk_not_in_master_" + $OutputPrefix + ".csv")
    compare_recovery = Join-Path $runDir ("audit_disk_vs_recovery_" + $OutputPrefix + ".csv")
    recovery_missing = Join-Path $runDir ("audit_recovery_missing_on_disk_" + $OutputPrefix + ".csv")
    current_closed_not_on_disk = Join-Path $runDir ("audit_current_closed_not_on_disk_" + $OutputPrefix + ".csv")
    disk_not_in_current = Join-Path $runDir ("audit_disk_not_in_current_" + $OutputPrefix + ".csv")
    compare_agent02 = Join-Path $runDir ("audit_disk_vs_agent02_" + $OutputPrefix + ".csv")
    summary = Join-Path $runDir ("audit_disk_summary_" + $OutputPrefix + ".json")
}

$pythonScript = @'
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def normalize_task_frame(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["task_key", "ticker", "date"])
    out = df.copy()
    if "ticker" in out.columns:
        out["ticker"] = out["ticker"].astype(str).str.upper().str.strip()
    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    if "task_key" not in out.columns:
        if {"ticker", "date"}.issubset(out.columns):
            out["task_key"] = out["ticker"].astype(str) + "|" + out["date"].astype(str)
        else:
            raise ValueError("No se pudo construir task_key: faltan columnas ticker/date")
    out["task_key"] = out["task_key"].astype(str)
    keep = [c for c in ["task_key", "ticker", "date"] if c in out.columns]
    return out[keep].dropna(subset=["task_key"]).drop_duplicates("task_key").reset_index(drop=True)


def inventory_quotes_root(quotes_root: Path, max_files: int = 0, progress_every: int = 10000) -> pd.DataFrame:
    rows = []
    count = 0
    for path in quotes_root.rglob("quotes.parquet"):
        if max_files > 0 and count >= max_files:
            break
        try:
            rel = path.relative_to(quotes_root)
        except ValueError:
            continue
        parts = rel.parts
        if len(parts) != 5:
            continue
        ticker, year_part, month_part, day_part, file_name = parts
        if file_name != "quotes.parquet":
            continue
        if not (year_part.startswith("year=") and month_part.startswith("month=") and day_part.startswith("day=")):
            continue
        year = year_part.replace("year=", "")
        month = month_part.replace("month=", "")
        day = day_part.replace("day=", "")
        date = f"{year}-{month}-{day}"
        stat = path.stat()
        rows.append(
            {
                "task_key": f"{ticker}|{date}",
                "ticker": ticker,
                "date": date,
                "file": str(path),
                "size_bytes": stat.st_size,
                "mtime_utc": pd.Timestamp(stat.st_mtime, unit="s", tz="UTC").isoformat(),
            }
        )
        count += 1
        if progress_every > 0 and count % progress_every == 0:
            print(json.dumps({
                "stage": "inventory_quotes_root",
                "files_seen": count,
                "last_file": str(path),
            }, ensure_ascii=False), flush=True)
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["task_key", "ticker", "date", "file", "size_bytes", "mtime_utc"])
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["task_key"] = df["ticker"] + "|" + df["date"]
    return df.drop_duplicates("task_key").sort_values(["ticker", "date"]).reset_index(drop=True)


def classify_merge(left: pd.DataFrame, right: pd.DataFrame, label: str) -> pd.DataFrame:
    merged = left.merge(right, on="task_key", how="outer", suffixes=("_left", "_right"), indicator=True)
    merged[label] = merged["_merge"].map({
        "both": "both",
        "left_only": "left_only",
        "right_only": "right_only",
    })
    return merged.drop(columns=["_merge"])


project_root = Path(r"__PROJECT_ROOT__")
run_dir = Path(r"__RUN_DIR__")
quotes_root = Path(r"__QUOTES_ROOT__")
max_files = int("__MAX_FILES__")
progress_every = int("__PROGRESS_EVERY__")

required = {
    "universe_refined": Path(r"__REQ_universe_refined__"),
    "official_lifecycle": Path(r"__REQ_official_lifecycle__"),
    "tickers_prod": Path(r"__REQ_tickers_prod__"),
    "tasks_master": Path(r"__REQ_tasks_master__"),
    "tasks_meta": Path(r"__REQ_tasks_meta__"),
    "tasks_recovery": Path(r"__REQ_tasks_recovery__"),
    "download_events_current": Path(r"__REQ_download_events_current__"),
    "quotes_agent_strict_current": Path(r"__REQ_quotes_agent_strict_current__"),
}

optional = {
    "download_events_history": Path(r"__OPT_download_events_history__"),
    "download_state": Path(r"__OPT_download_state__"),
    "download_live_status": Path(r"__OPT_download_live_status__"),
}

outputs = {
    "disk_inventory": Path(r"__OUT_disk_inventory__"),
    "compare_master": Path(r"__OUT_compare_master__"),
    "master_missing": Path(r"__OUT_master_missing__"),
    "disk_not_in_master": Path(r"__OUT_disk_not_in_master__"),
    "compare_recovery": Path(r"__OUT_compare_recovery__"),
    "recovery_missing": Path(r"__OUT_recovery_missing__"),
    "current_closed_not_on_disk": Path(r"__OUT_current_closed_not_on_disk__"),
    "disk_not_in_current": Path(r"__OUT_disk_not_in_current__"),
    "compare_agent02": Path(r"__OUT_compare_agent02__"),
    "summary": Path(r"__OUT_summary__"),
}

tasks_master = normalize_task_frame(pd.read_csv(required["tasks_master"], usecols=["ticker", "date"]))
tasks_recovery = normalize_task_frame(pd.read_csv(required["tasks_recovery"], usecols=["ticker", "date"]))
current = pd.read_csv(
    required["download_events_current"],
    usecols=["task_key", "ticker", "date", "status", "rows", "error", "file"],
)
current = normalize_task_frame(current).merge(
    pd.read_csv(
        required["download_events_current"],
        usecols=["task_key", "status", "rows", "error", "file"],
    ).drop_duplicates("task_key"),
    on="task_key",
    how="left",
)
strict = pd.read_csv(
    required["quotes_agent_strict_current"],
    usecols=["file", "rows", "severity", "action", "processed_at_utc", "run_id"],
)

disk = inventory_quotes_root(quotes_root, max_files=max_files, progress_every=progress_every)
disk.to_csv(outputs["disk_inventory"], index=False, encoding="utf-8")

master_cmp = classify_merge(tasks_master, disk[["task_key", "file", "size_bytes", "mtime_utc"]], "vs_disk")
master_cmp.to_csv(outputs["compare_master"], index=False, encoding="utf-8")
master_cmp[master_cmp["vs_disk"] == "left_only"].to_csv(outputs["master_missing"], index=False, encoding="utf-8")
master_cmp[master_cmp["vs_disk"] == "right_only"].to_csv(outputs["disk_not_in_master"], index=False, encoding="utf-8")

recovery_cmp = classify_merge(tasks_recovery, disk[["task_key", "file", "size_bytes", "mtime_utc"]], "vs_disk")
recovery_cmp.to_csv(outputs["compare_recovery"], index=False, encoding="utf-8")
recovery_cmp[recovery_cmp["vs_disk"] == "left_only"].to_csv(outputs["recovery_missing"], index=False, encoding="utf-8")

closed_statuses = {"DOWNLOADED_OK", "DOWNLOADED_EMPTY", "EMPTY_CONFIRMED"}
current_closed = current[current["status"].isin(closed_statuses)].copy()
current_closed_cmp = classify_merge(
    current_closed[["task_key", "status", "rows", "error", "file"]],
    disk[["task_key", "file", "size_bytes", "mtime_utc"]],
    "vs_disk",
)
current_closed_cmp[current_closed_cmp["vs_disk"] == "left_only"].to_csv(
    outputs["current_closed_not_on_disk"], index=False, encoding="utf-8"
)

disk_vs_current = classify_merge(
    disk[["task_key", "file", "size_bytes", "mtime_utc"]],
    current[["task_key", "status", "rows", "error", "file"]],
    "vs_current",
)
disk_vs_current[disk_vs_current["vs_current"] == "left_only"].to_csv(
    outputs["disk_not_in_current"], index=False, encoding="utf-8"
)

strict_norm = strict.copy()
strict_norm["task_key"] = strict_norm["file"].str.replace("\\\\", "/", regex=False)
strict_norm["task_key"] = strict_norm["task_key"].str.replace(str(quotes_root).replace("\\", "/") + "/", "", regex=False)
strict_norm["task_key"] = strict_norm["task_key"].str.split("/")
strict_norm = strict_norm[strict_norm["task_key"].map(lambda x: isinstance(x, list) and len(x) == 5 and x[4] == "quotes.parquet")].copy()
strict_norm["ticker"] = strict_norm["task_key"].str[0].str.upper().str.strip()
strict_norm["date"] = (
    strict_norm["task_key"].str[1].str.replace("year=", "", regex=False)
    + "-"
    + strict_norm["task_key"].str[2].str.replace("month=", "", regex=False)
    + "-"
    + strict_norm["task_key"].str[3].str.replace("day=", "", regex=False)
)
strict_norm["task_key"] = strict_norm["ticker"] + "|" + strict_norm["date"]
strict_norm = strict_norm.drop_duplicates("task_key")

disk_vs_agent02 = classify_merge(
    disk[["task_key", "file", "size_bytes", "mtime_utc"]],
    strict_norm[["task_key", "severity", "action", "rows", "processed_at_utc", "run_id"]],
    "vs_agent02",
)
disk_vs_agent02.to_csv(outputs["compare_agent02"], index=False, encoding="utf-8")

summary = {
    "run_dir": str(run_dir),
    "quotes_root": str(quotes_root),
    "required_inputs": {k: str(v) for k, v in required.items()},
    "optional_inputs_present": {k: v.exists() for k, v in optional.items()},
    "counts": {
        "max_files_limit": int(max_files),
        "progress_every": int(progress_every),
        "disk_files": int(len(disk)),
        "tasks_master": int(len(tasks_master)),
        "tasks_recovery": int(len(tasks_recovery)),
        "current_rows": int(len(current)),
        "current_closed_rows": int(len(current_closed)),
        "agent02_rows": int(len(strict_norm)),
        "master_missing_on_disk": int((master_cmp["vs_disk"] == "left_only").sum()),
        "disk_not_in_master": int((master_cmp["vs_disk"] == "right_only").sum()),
        "recovery_missing_on_disk": int((recovery_cmp["vs_disk"] == "left_only").sum()),
        "current_closed_not_on_disk": int((current_closed_cmp["vs_disk"] == "left_only").sum()),
        "disk_not_in_current": int((disk_vs_current["vs_current"] == "left_only").sum()),
        "disk_without_agent02_record": int((disk_vs_agent02["vs_agent02"] == "left_only").sum()),
    },
    "severity_counts": strict_norm["severity"].value_counts(dropna=False).to_dict(),
    "output_files": {k: str(v) for k, v in outputs.items()},
}

outputs["summary"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(summary, indent=2, ensure_ascii=False))
'@

foreach ($key in $requiredPaths.Keys) {
    $pythonScript = $pythonScript.Replace(("__REQ_${key}__"), ($requiredPaths[$key] -replace "\\", "\\"))
}
foreach ($key in $optionalPaths.Keys) {
    $pythonScript = $pythonScript.Replace(("__OPT_${key}__"), ($optionalPaths[$key] -replace "\\", "\\"))
}
foreach ($key in $outputPaths.Keys) {
    $pythonScript = $pythonScript.Replace(("__OUT_${key}__"), ($outputPaths[$key] -replace "\\", "\\"))
}
$pythonScript = $pythonScript.Replace("__PROJECT_ROOT__", ($projectRootPath -replace "\\", "\\"))
$pythonScript = $pythonScript.Replace("__RUN_DIR__", ($runDir -replace "\\", "\\"))
$pythonScript = $pythonScript.Replace("__QUOTES_ROOT__", ($QuotesRoot -replace "\\", "\\"))
$pythonScript = $pythonScript.Replace("__MAX_FILES__", [string]$MaxFiles)
$pythonScript = $pythonScript.Replace("__PROGRESS_EVERY__", [string]$ProgressEvery)

Write-Host "Auditando disco quotes..." -ForegroundColor Cyan
Write-Host "  run_id     : $RunId"
Write-Host "  run_dir    : $runDir"
Write-Host "  quotes_root: $QuotesRoot"
Write-Host "  output     : $OutputPrefix"
Write-Host "  max_files  : $MaxFiles"
Write-Host "  progress   : cada $ProgressEvery files"

$pythonScript | python -

Write-Host ""
Write-Host "Auditoría completada. Resumen:" -ForegroundColor Green
Write-Host "  $($outputPaths.summary)"
