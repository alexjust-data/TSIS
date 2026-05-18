[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\TSIS_Data\02_backtest_SmallCaps",
    [string]$SourceRunId = "20260319_quotes_clean_v2_draft",
    [string]$QuotesRoot = "D:\quotes",
    [string]$Agent02RunId = "20260313_quotes_prod_full_12133_clean",
    [switch]$ForceHardFailRedownload = $true,
    [int]$ProgressEvery = 25000,
    [switch]$ResumeCheckpoint = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRootPath = [System.IO.Path]::GetFullPath($ProjectRoot)
$sourceRunDir = Join-Path $projectRootPath ("runs\polygon_realtime_audit\" + $SourceRunId)
$inputsDir = Join-Path $sourceRunDir "inputs"

$requiredPaths = @{
    tasks_clean = Join-Path $inputsDir "tasks_quotes_prod_v2_clean.csv"
    meta_clean = Join-Path $inputsDir "tasks_quotes_prod_v2_clean.meta.json"
}

$agent02Path = Join-Path $projectRootPath ("runs\polygon_realtime_audit\" + $Agent02RunId + "\quotes_agent_strict_events_current.csv")
if (Test-Path $agent02Path) {
    $requiredPaths["agent02_current"] = $agent02Path
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
    missing_csv = Join-Path $inputsDir "tasks_quotes_prod_v2_clean_missing_only.csv"
    keep_csv = Join-Path $inputsDir "tasks_quotes_prod_v2_clean_existing_ok.csv"
    audit_csv = Join-Path $inputsDir "tasks_quotes_prod_v2_clean_disk_audit.csv"
    meta_json = Join-Path $inputsDir "tasks_quotes_prod_v2_clean_missing_only.meta.json"
    partial_csv = Join-Path $inputsDir "tasks_quotes_prod_v2_clean_disk_audit.partial.csv"
    progress_json = Join-Path $inputsDir "tasks_quotes_prod_v2_clean_disk_audit.progress.json"
}

$pythonScript = @'
from __future__ import annotations

import json
import math
import time
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


project_root = Path(r"__PROJECT_ROOT__")
source_run_id = "__SOURCE_RUN_ID__"
source_run_dir = Path(r"__SOURCE_RUN_DIR__")
quotes_root = Path(r"__QUOTES_ROOT__")
tasks_path = Path(r"__REQ_tasks_clean__")
meta_path = Path(r"__REQ_meta_clean__")
agent02_path = Path(r"__REQ_agent02_current__") if "__HAS_AGENT02__" == "1" else None

missing_csv = Path(r"__OUT_missing_csv__")
keep_csv = Path(r"__OUT_keep_csv__")
audit_csv = Path(r"__OUT_audit_csv__")
meta_json = Path(r"__OUT_meta_json__")
partial_csv = Path(r"__OUT_partial_csv__")
progress_json = Path(r"__OUT_progress_json__")

force_hard_fail_redownload = "__FORCE_HARD_FAIL__" == "1"
progress_every = int("__PROGRESS_EVERY__")
resume_checkpoint = "__RESUME_CHECKPOINT__" == "1"


def expected_file(output_root: Path, ticker: str, date: str) -> Path:
    y, m, d = date.split("-")
    return output_root / ticker / f"year={y}" / f"month={m}" / f"day={d}" / "quotes.parquet"


def inspect_existing_good_file(path: Path) -> tuple[bool, int | None, str]:
    if not path.exists():
        return False, None, "missing_on_disk"
    try:
        pf = pq.ParquetFile(path)
        rows = int(pf.metadata.num_rows) if pf.metadata is not None else 0
        if rows > 0:
            return True, rows, "existing_ok"
        return False, rows, "existing_zero_rows"
    except Exception as exc:
        return False, None, f"existing_unreadable:{type(exc).__name__}"


tasks = pd.read_csv(tasks_path, usecols=["ticker", "date"])
tasks["ticker"] = tasks["ticker"].astype(str).str.upper().str.strip()
tasks["date"] = tasks["date"].astype(str).str.strip()
tasks = tasks.drop_duplicates(["ticker", "date"]).sort_values(["ticker", "date"]).reset_index(drop=True)
tasks["task_key"] = tasks["ticker"] + "|" + tasks["date"]

hard_fail_files: set[str] = set()
if agent02_path is not None and agent02_path.exists():
    agent02 = pd.read_csv(agent02_path, usecols=["file", "severity"])
    agent02["file"] = agent02["file"].astype(str)
    if force_hard_fail_redownload:
        hard_fail_files = set(agent02.loc[agent02["severity"] == "HARD_FAIL", "file"])

resume_from = 0
started_at = time.time()
if resume_checkpoint and progress_json.exists() and partial_csv.exists():
    try:
        progress_state = json.loads(progress_json.read_text(encoding="utf-8"))
        if int(progress_state.get("tasks_total", -1)) == int(len(tasks)):
            resume_from = int(progress_state.get("processed_tasks", 0))
            if resume_from < 0 or resume_from > len(tasks):
                resume_from = 0
    except Exception:
        resume_from = 0

if resume_from == 0:
    for p in [partial_csv, progress_json, missing_csv, keep_csv, audit_csv, meta_json]:
        if p.exists():
            p.unlink()

if resume_from > 0:
    print(
        json.dumps(
            {
                "stage": "resume_checkpoint",
                "processed_tasks": resume_from,
                "tasks_total": int(len(tasks)),
                "pct": round(100.0 * resume_from / len(tasks), 2),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

rows = []
total = len(tasks)
for idx, row in enumerate(tasks.iloc[resume_from:].itertuples(index=False), start=resume_from + 1):
    fpath = expected_file(quotes_root, row.ticker, row.date)
    ok_existing, existing_rows, disk_status = inspect_existing_good_file(fpath)
    force_redownload = str(fpath) in hard_fail_files
    final_keep = bool(ok_existing and not force_redownload)
    reason = "agent02_hard_fail_redownload" if force_redownload else disk_status

    rows.append(
        {
            "ticker": row.ticker,
            "date": row.date,
            "task_key": row.task_key,
            "file": str(fpath),
            "file_exists": bool(fpath.exists()),
            "existing_rows": existing_rows,
            "disk_status": disk_status,
            "agent02_hard_fail": bool(force_redownload),
            "keep_existing": final_keep,
            "decision": "existing_ok_skip" if final_keep else "missing_only_download",
            "decision_reason": reason,
        }
    )

    if progress_every > 0 and (idx % progress_every == 0 or idx == total):
        chunk_df = pd.DataFrame(rows)
        if len(chunk_df):
            write_header = not partial_csv.exists()
            chunk_df.to_csv(partial_csv, mode="a", header=write_header, index=False, encoding="utf-8")
            rows = []
        elapsed = max(0.001, time.time() - started_at)
        processed_since_start = idx - resume_from
        rate = processed_since_start / elapsed
        remaining = total - idx
        eta_seconds = int(remaining / rate) if rate > 0 else None
        eta_minutes = round(eta_seconds / 60.0, 2) if eta_seconds is not None else None
        eta_hours = round(eta_seconds / 3600.0, 2) if eta_seconds is not None else None
        progress_payload = {
            "source_run_id": source_run_id,
            "tasks_total": int(total),
            "processed_tasks": int(idx),
            "resume_from": int(resume_from),
            "last_task_key": row.task_key,
            "elapsed_seconds_since_resume": round(elapsed, 2),
            "rate_tasks_per_sec": round(rate, 2),
            "eta_seconds": eta_seconds,
        }
        progress_json.write_text(json.dumps(progress_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(
            json.dumps(
                {
                    "stage": "build_missing_only_from_disk",
                    "processed_tasks": idx,
                    "tasks_total": total,
                    "pct": round(100.0 * idx / total, 2),
                    "last_task_key": row.task_key,
                    "rate_tasks_per_sec": round(rate, 2),
                    "eta_minutes": eta_minutes,
                    "eta_hours": eta_hours,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

if rows:
    chunk_df = pd.DataFrame(rows)
    write_header = not partial_csv.exists()
    chunk_df.to_csv(partial_csv, mode="a", header=write_header, index=False, encoding="utf-8")
    rows = []

audit = pd.read_csv(partial_csv) if partial_csv.exists() else pd.DataFrame(
    columns=[
        "ticker",
        "date",
        "task_key",
        "file",
        "file_exists",
        "existing_rows",
        "disk_status",
        "agent02_hard_fail",
        "keep_existing",
        "decision",
        "decision_reason",
    ]
)
missing_df = audit.loc[~audit["keep_existing"], ["ticker", "date"]].copy()
keep_df = audit.loc[audit["keep_existing"], ["ticker", "date"]].copy()

missing_df.to_csv(missing_csv, index=False, encoding="utf-8")
keep_df.to_csv(keep_csv, index=False, encoding="utf-8")
audit.to_csv(audit_csv, index=False, encoding="utf-8")

base_meta = {}
if meta_path.exists():
    base_meta = json.loads(meta_path.read_text(encoding="utf-8"))

summary = {
    "source_run_id": source_run_id,
    "source_tasks_csv": str(tasks_path),
    "quotes_root": str(quotes_root),
    "agent02_reference_csv": str(agent02_path) if agent02_path is not None else None,
    "force_hard_fail_redownload": force_hard_fail_redownload,
    "tasks_total": int(len(tasks)),
    "existing_ok_skip": int(audit["keep_existing"].sum()),
    "missing_only_download": int((~audit["keep_existing"]).sum()),
    "missing_on_disk": int((audit["disk_status"] == "missing_on_disk").sum()),
    "existing_zero_rows": int((audit["disk_status"] == "existing_zero_rows").sum()),
    "existing_unreadable": int(audit["disk_status"].astype(str).str.startswith("existing_unreadable:").sum()),
    "agent02_hard_fail_redownload": int(audit["agent02_hard_fail"].sum()),
    "outputs": {
        "missing_csv": str(missing_csv),
        "keep_csv": str(keep_csv),
        "audit_csv": str(audit_csv),
    },
    "base_meta": base_meta,
}
meta_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
if progress_json.exists():
    progress_json.unlink()
print(json.dumps(summary, indent=2, ensure_ascii=False))
'@

foreach ($key in $requiredPaths.Keys) {
    $token = "__REQ_${key}__"
    $pythonScript = $pythonScript.Replace($token, ($requiredPaths[$key] -replace "\\", "\\"))
}
foreach ($key in $outputs.Keys) {
    $token = "__OUT_${key}__"
    $pythonScript = $pythonScript.Replace($token, ($outputs[$key] -replace "\\", "\\"))
}

$pythonScript = $pythonScript.Replace("__PROJECT_ROOT__", ($projectRootPath -replace "\\", "\\"))
$pythonScript = $pythonScript.Replace("__SOURCE_RUN_ID__", $SourceRunId)
$pythonScript = $pythonScript.Replace("__SOURCE_RUN_DIR__", ($sourceRunDir -replace "\\", "\\"))
$pythonScript = $pythonScript.Replace("__QUOTES_ROOT__", ($QuotesRoot -replace "\\", "\\"))
$pythonScript = $pythonScript.Replace("__HAS_AGENT02__", ($(if (Test-Path $agent02Path) { "1" } else { "0" })))
$pythonScript = $pythonScript.Replace("__REQ_agent02_current__", (($agent02Path) -replace "\\", "\\"))
$pythonScript = $pythonScript.Replace("__FORCE_HARD_FAIL__", ($(if ($ForceHardFailRedownload) { "1" } else { "0" })))
$pythonScript = $pythonScript.Replace("__PROGRESS_EVERY__", [string]$ProgressEvery)
$pythonScript = $pythonScript.Replace("__RESUME_CHECKPOINT__", ($(if ($ResumeCheckpoint) { "1" } else { "0" })))

Write-Host "Construyendo tasks missing_only para quotes..." -ForegroundColor Cyan
Write-Host "  source_run_id : $SourceRunId"
Write-Host "  source_run_dir: $sourceRunDir"
Write-Host "  quotes_root   : $QuotesRoot"
Write-Host "  agent02_run   : $Agent02RunId"
Write-Host "  hard_fail     : $ForceHardFailRedownload"
Write-Host "  progress      : cada $ProgressEvery tareas"

$pythonScript | python -

Write-Host ""
Write-Host "Artifacts:" -ForegroundColor Green
Write-Host "  $($outputs.missing_csv)"
Write-Host "  $($outputs.keep_csv)"
Write-Host "  $($outputs.audit_csv)"
Write-Host "  $($outputs.meta_json)"

$agent01Cmd = 'python "{0}" --csv "{1}" --output "{2}" --concurrent 32 --run-id "{3}" --run-dir "{4}" --resume --task-batch-size 1000' -f `
    (Join-Path $projectRootPath "scripts\download_quotes.py"), `
    $outputs.missing_csv, `
    $QuotesRoot, `
    $SourceRunId, `
    $sourceRunDir

Write-Host ""
Write-Host "Agent01 command over missing_only:" -ForegroundColor Green
Write-Host $agent01Cmd
