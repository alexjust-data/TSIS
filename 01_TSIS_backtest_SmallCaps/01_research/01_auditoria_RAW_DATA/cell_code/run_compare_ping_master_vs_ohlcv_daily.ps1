param(
  [string]$PythonExe = "C:\TSIS_Data\02_backtest_SmallCaps\backtest\Scripts\python.exe",
  [string]$ScriptPath = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\compare_ping_master_vs_ohlcv_daily.py",
  [string]$PingMaster = "C:\TSIS_Data\02_backtest_SmallCaps\data\reference\ping_range_master.parquet",
  [string]$OhlcvRoot = "D:\ohlcv_daily",
  [string]$OutDir = "",
  [int]$LimitTickers = 0
)

$ErrorActionPreference = "Stop"

Write-Host "Running compare_ping_master_vs_ohlcv_daily..." -ForegroundColor Cyan
Write-Host "python = $PythonExe"
Write-Host "script = $ScriptPath"
Write-Host "ping_master = $PingMaster"
Write-Host "ohlcv_root = $OhlcvRoot"
if ($OutDir -ne "") { Write-Host "outdir = $OutDir" }
if ($LimitTickers -gt 0) { Write-Host "limit_tickers = $LimitTickers" }

$args = @(
  $ScriptPath,
  "--ping-master", $PingMaster,
  "--ohlcv-root", $OhlcvRoot
)

if ($OutDir -ne "") {
  $args += @("--outdir", $OutDir)
}
if ($LimitTickers -gt 0) {
  $args += @("--limit-tickers", "$LimitTickers")
}

& $PythonExe @args
