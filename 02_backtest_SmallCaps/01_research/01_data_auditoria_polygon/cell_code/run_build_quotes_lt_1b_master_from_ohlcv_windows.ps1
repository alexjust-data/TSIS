param(
  [string]$PythonExe = "C:\TSIS_Data\02_backtest_SmallCaps\backtest\Scripts\python.exe",
  [string]$ScriptPath = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\build_quotes_lt_1b_master_from_ohlcv_windows.py",
  [string]$WindowsParquet = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\lt_1b_vs_ohlcv_daily_windows\20260322_202042_cross_lt_1b_vs_ohlcv_daily_windows\lt_1b_vs_ohlcv_daily_windows.parquet",
  [string]$OutDir = "",
  [int]$LimitTickers = 0
)

$ErrorActionPreference = "Stop"

Write-Host "Running build_quotes_lt_1b_master_from_ohlcv_windows..." -ForegroundColor Cyan
Write-Host "python = $PythonExe"
Write-Host "script = $ScriptPath"
Write-Host "windows = $WindowsParquet"
if ($OutDir -ne "") { Write-Host "outdir = $OutDir" }
if ($LimitTickers -gt 0) { Write-Host "limit_tickers = $LimitTickers" }

$args = @(
  $ScriptPath,
  "--windows-parquet", $WindowsParquet
)
if ($OutDir -ne "") {
  $args += @("--outdir", $OutDir)
}
if ($LimitTickers -gt 0) {
  $args += @("--limit-tickers", "$LimitTickers")
}

& $PythonExe @args
