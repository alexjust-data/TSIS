param(
  [string]$PythonExe = "C:\TSIS_Data\02_backtest_SmallCaps\backtest\Scripts\python.exe",
  [string]$ScriptPath = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\build_quotes_lt_1b_missing_only_from_disk.py",
  [string]$TasksCsv = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_tasks\20260322_221029_build_quotes_lt_1b_master_from_ohlcv_windows\tasks_quotes_lt_1b_master.csv",
  [string]$QuotesRoot = "D:\quotes",
  [string]$OutDir = "",
  [int]$LimitRows = 0,
  [int]$BlockSize = 250000,
  [switch]$Resume
)

$ErrorActionPreference = "Stop"

Write-Host "Running build_quotes_lt_1b_missing_only_from_disk..." -ForegroundColor Cyan
Write-Host "python = $PythonExe"
Write-Host "script = $ScriptPath"
Write-Host "tasks = $TasksCsv"
Write-Host "quotes_root = $QuotesRoot"
Write-Host "resume = $Resume"
Write-Host "block_size = $BlockSize"
if ($OutDir -ne "") { Write-Host "outdir = $OutDir" }
if ($LimitRows -gt 0) { Write-Host "limit_rows = $LimitRows" }

$args = @(
  $ScriptPath,
  "--tasks-csv", $TasksCsv,
  "--quotes-root", $QuotesRoot,
  "--block-size", "$BlockSize"
)
if ($OutDir -ne "") {
  $args += @("--outdir", $OutDir)
}
if ($LimitRows -gt 0) {
  $args += @("--limit-rows", "$LimitRows")
}
if ($Resume) {
  $args += "--resume"
}

& $PythonExe @args
