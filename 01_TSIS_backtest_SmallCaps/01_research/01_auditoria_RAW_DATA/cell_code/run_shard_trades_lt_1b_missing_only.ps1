param(
  [string]$PythonExe = "C:\TSIS_Data\02_backtest_SmallCaps\backtest\Scripts\python.exe",
  [string]$ScriptPath = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\shard_trades_lt_1b_missing_only.py",
  [string]$MissingCsv,
  [string]$OutDir = "",
  [int]$NumShards = 4
)

$ErrorActionPreference = "Stop"

if ($MissingCsv -eq "") {
  throw "Debes pasar -MissingCsv con el tasks_trades_lt_1b_missing_only.csv"
}

Write-Host "Running shard_trades_lt_1b_missing_only..." -ForegroundColor Cyan
Write-Host "python = $PythonExe"
Write-Host "script = $ScriptPath"
Write-Host "missing = $MissingCsv"
Write-Host "num_shards = $NumShards"
if ($OutDir -ne "") { Write-Host "outdir = $OutDir" }

$args = @(
  $ScriptPath,
  "--missing-csv", $MissingCsv,
  "--num-shards", "$NumShards"
)
if ($OutDir -ne "") {
  $args += @("--outdir", $OutDir)
}

& $PythonExe @args
