param(
  [string]$PythonExe = "C:\TSIS_Data\02_backtest_SmallCaps\backtest\Scripts\python.exe",
  [string]$ScriptPath = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\build_trades_lt_1b_missing_only_from_inventory.py",
  [string]$TasksCsv = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_lt_1b_tasks\20260324_200919_build_trades_lt_1b_master_from_ohlcv_windows\tasks_trades_lt_1b_master.csv",
  [string]$InventoryTxt = "C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit\trades_ticks_prod_2005_2026\inputs\trades_ticks_final_file_paths.txt",
  [string]$OutDir = "",
  [int]$LimitRows = 0
)

$ErrorActionPreference = "Stop"

Write-Host "Running build_trades_lt_1b_missing_only_from_inventory..." -ForegroundColor Cyan
Write-Host "python = $PythonExe"
Write-Host "script = $ScriptPath"
Write-Host "tasks = $TasksCsv"
Write-Host "inventory = $InventoryTxt"
if ($OutDir -ne "") { Write-Host "outdir = $OutDir" }
if ($LimitRows -gt 0) { Write-Host "limit_rows = $LimitRows" }

$args = @(
  $ScriptPath,
  "--tasks-csv", $TasksCsv,
  "--inventory-txt", $InventoryTxt
)
if ($OutDir -ne "") {
  $args += @("--outdir", $OutDir)
}
if ($LimitRows -gt 0) {
  $args += @("--limit-rows", "$LimitRows")
}

& $PythonExe @args
