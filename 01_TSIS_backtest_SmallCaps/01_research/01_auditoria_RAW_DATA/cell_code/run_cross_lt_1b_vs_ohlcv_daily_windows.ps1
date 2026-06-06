param(
  [string]$PythonExe = "C:\TSIS_Data\02_backtest_SmallCaps\backtest\Scripts\python.exe",
  [string]$ScriptPath = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\cross_lt_1b_vs_ohlcv_daily_windows.py",
  [string]$TargetParquet = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet",
  [string]$OhlcvRoot = "D:\ohlcv_daily",
  [string]$OutDir = "",
  [int]$LimitTickers = 0
)

$ErrorActionPreference = "Stop"

Write-Host "Running cross_lt_1b_vs_ohlcv_daily_windows..." -ForegroundColor Cyan
Write-Host "python = $PythonExe"
Write-Host "script = $ScriptPath"
Write-Host "target = $TargetParquet"
Write-Host "ohlcv_root = $OhlcvRoot"
if ($OutDir -ne "") { Write-Host "outdir = $OutDir" }
if ($LimitTickers -gt 0) { Write-Host "limit_tickers = $LimitTickers" }

$args = @(
  $ScriptPath,
  "--target-parquet", $TargetParquet,
  "--ohlcv-root", $OhlcvRoot
)
if ($OutDir -ne "") {
  $args += @("--outdir", $OutDir)
}
if ($LimitTickers -gt 0) {
  $args += @("--limit-tickers", "$LimitTickers")
}

& $PythonExe @args
