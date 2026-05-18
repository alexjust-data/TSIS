[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\TSIS_Data\02_backtest_SmallCaps",
    [string]$SourceRunId = "20260319_quotes_clean_v2_draft",
    [string]$QuotesRoot = "D:\quotes",
    [string]$Agent02RunId = "20260313_quotes_prod_full_12133_clean",
    [switch]$ForceHardFailRedownload = $true,
    [int]$ProgressEvery = 50000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRootPath = [System.IO.Path]::GetFullPath($ProjectRoot)
$sourceRunDir = Join-Path $projectRootPath ("runs\polygon_realtime_audit\" + $SourceRunId)
$inputsDir = Join-Path $sourceRunDir "inputs"

$requiredPaths = @{
    tasks_clean = Join-Path $inputsDir "tasks_quotes_prod_v2_clean.csv"
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
    inventory_csv = Join-Path $inputsDir "disk_quotes_inventory_by_path.fast.csv"
    missing_csv = Join-Path $inputsDir "tasks_quotes_prod_v2_clean_missing_only.fast.csv"
    keep_csv = Join-Path $inputsDir "tasks_quotes_prod_v2_clean_existing_ok.fast.csv"
    audit_csv = Join-Path $inputsDir "tasks_quotes_prod_v2_clean_path_audit.fast.csv"
    meta_json = Join-Path $inputsDir "tasks_quotes_prod_v2_clean_missing_only.fast.meta.json"
}

$pythonScript = @'
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


source_run_id = "__SOURCE_RUN_ID__"
source_run_dir = Path(r"__SOURCE_RUN_DIR__")
quotes_root = Path(r"__QUOTES_ROOT__")
tasks_path = Path(r"__REQ_tasks_clean__")
agent02_path = Path(r"__REQ_agent02_current__") if "__HAS_AGENT02__" == "1" else None

inventory_csv = Path(r"__OUT_inventory_csv__")
missing_csv = Path(r"__OUT_missing_csv__")
keep_csv = Path(r"__OUT_keep_csv__")
audit_csv = Path(r"__OUT_audit_csv__")
meta_json = Path(r"__OUT_meta_json__")

force_hard_fail_redownload = "__FORCE_HARD_FAIL__" == "1"

tasks = pd.read_csv(tasks_path, usecols=["ticker", "date"])
tasks["ticker"] = tasks["ticker"].astype(str).str.upper().str.strip()
tasks["date"] = tasks["date"].astype(str).str.strip()
tasks = tasks.drop_duplicates(["ticker", "date"]).sort_values(["ticker", "date"]).reset_index(drop=True)
tasks["task_key"] = tasks["ticker"] + "|" + tasks["date"]

inv = pd.read_csv(inventory_csv)
inv["ticker"] = inv["ticker"].astype(str).str.upper().str.strip()
inv["date"] = inv["date"].astype(str).str.strip()
inv["task_key"] = inv["ticker"] + "|" + inv["date"]
inv = inv.drop_duplicates(["task_key"], keep="first")
existing_task_keys = set(inv.loc[inv["size_bytes"] > 0, "task_key"])
existing_by_key = inv.set_index("task_key", drop=False)

hard_fail_files: set[str] = set()
if agent02_path is not None and agent02_path.exists():
    agent02 = pd.read_csv(agent02_path, usecols=["file", "severity"])
    agent02["file"] = agent02["file"].astype(str)
    if force_hard_fail_redownload:
        hard_fail_files = set(agent02.loc[agent02["severity"] == "HARD_FAIL", "file"])

audit = tasks.copy()
audit["file"] = audit["task_key"].map(existing_by_key["file"]) if len(existing_by_key) else pd.NA
audit["size_bytes"] = audit["task_key"].map(existing_by_key["size_bytes"]) if len(existing_by_key) else pd.NA
audit["file_exists_by_path"] = audit["task_key"].isin(existing_task_keys)
audit["agent02_hard_fail"] = audit["file"].astype(str).isin(hard_fail_files)
audit["keep_existing"] = audit["file_exists_by_path"] & (~audit["agent02_hard_fail"])
audit["decision"] = audit["keep_existing"].map({True: "existing_ok_skip", False: "missing_only_download"})
audit["decision_reason"] = "missing_on_disk_or_forced_redownload"
audit.loc[audit["file_exists_by_path"] & (~audit["agent02_hard_fail"]), "decision_reason"] = "path_exists_nonzero_skip"
audit.loc[audit["agent02_hard_fail"], "decision_reason"] = "agent02_hard_fail_redownload"

missing_df = audit.loc[~audit["keep_existing"], ["ticker", "date"]].copy()
keep_df = audit.loc[audit["keep_existing"], ["ticker", "date"]].copy()

missing_df.to_csv(missing_csv, index=False, encoding="utf-8")
keep_df.to_csv(keep_csv, index=False, encoding="utf-8")
audit.to_csv(audit_csv, index=False, encoding="utf-8")

summary = {
    "source_run_id": source_run_id,
    "source_tasks_csv": str(tasks_path),
    "quotes_root": str(quotes_root),
    "agent02_reference_csv": str(agent02_path) if agent02_path is not None else None,
    "force_hard_fail_redownload": force_hard_fail_redownload,
    "tasks_total": int(len(tasks)),
    "disk_inventory_rows": int(len(inv)),
    "existing_ok_skip": int(audit["keep_existing"].sum()),
    "missing_only_download": int((~audit["keep_existing"]).sum()),
    "path_exists_nonzero": int(audit["file_exists_by_path"].sum()),
    "agent02_hard_fail_redownload": int(audit["agent02_hard_fail"].sum()),
    "outputs": {
        "inventory_csv": str(inventory_csv),
        "missing_csv": str(missing_csv),
        "keep_csv": str(keep_csv),
        "audit_csv": str(audit_csv),
    },
}
meta_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
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

$pythonScript = $pythonScript.Replace("__SOURCE_RUN_ID__", $SourceRunId)
$pythonScript = $pythonScript.Replace("__SOURCE_RUN_DIR__", ($sourceRunDir -replace "\\", "\\"))
$pythonScript = $pythonScript.Replace("__QUOTES_ROOT__", ($QuotesRoot -replace "\\", "\\"))
$pythonScript = $pythonScript.Replace("__HAS_AGENT02__", ($(if (Test-Path $agent02Path) { "1" } else { "0" })))
$pythonScript = $pythonScript.Replace("__REQ_agent02_current__", (($agent02Path) -replace "\\", "\\"))
$pythonScript = $pythonScript.Replace("__FORCE_HARD_FAIL__", ($(if ($ForceHardFailRedownload) { "1" } else { "0" })))

Write-Host "Inventariando D:\\quotes por path..." -ForegroundColor Cyan
Write-Host "  source_run_id : $SourceRunId"
Write-Host "  source_run_dir: $sourceRunDir"
Write-Host "  quotes_root   : $QuotesRoot"
Write-Host "  agent02_run   : $Agent02RunId"
Write-Host "  hard_fail     : $ForceHardFailRedownload"
Write-Host "  progress      : cada $ProgressEvery files"

$inventoryRows = New-Object System.Collections.Generic.List[object]
$count = 0
Get-ChildItem -Path $QuotesRoot -Recurse -Filter quotes.parquet -File | ForEach-Object {
    $count += 1
    $full = $_.FullName
    $rel = $full.Substring($QuotesRoot.Length).TrimStart('\')
    $parts = $rel -split '\\'
    if ($parts.Length -ge 5) {
        $ticker = $parts[0]
        $year = $parts[1] -replace '^year=', ''
        $month = $parts[2] -replace '^month=', ''
        $day = $parts[3] -replace '^day=', ''
        if ($year -match '^\d{4}$' -and $month -match '^\d{2}$' -and $day -match '^\d{2}$') {
            $inventoryRows.Add([PSCustomObject]@{
                ticker = $ticker
                date = "$year-$month-$day"
                file = $full
                size_bytes = [int64]$_.Length
            }) | Out-Null
        }
    }

    if ($ProgressEvery -gt 0 -and (($count % $ProgressEvery) -eq 0)) {
        Write-Host (@{
            stage = "inventory_quotes_root"
            files_seen = $count
            last_file = $full
        } | ConvertTo-Json -Compress)
    }
}

$inventoryRows | Export-Csv -Path $outputs.inventory_csv -NoTypeInformation -Encoding UTF8

Write-Host "Construyendo missing_only desde inventario..." -ForegroundColor Cyan
$pythonScript | python -

Write-Host ""
Write-Host "Artifacts:" -ForegroundColor Green
Write-Host "  $($outputs.inventory_csv)"
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
Write-Host "Agent01 command over fast missing_only:" -ForegroundColor Green
Write-Host $agent01Cmd
