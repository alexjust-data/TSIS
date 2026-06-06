param(
  [string]$PythonExe = "C:\TSIS_Data\02_backtest_SmallCaps\backtest\Scripts\python.exe",
  [string]$ScriptPath = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\build_ping_range_master_resume.py",
  [string]$UniverseParquet = "C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti\hybrid_enriched\universe_hybrid_enriched_with_financial_ranges.parquet",
  [string]$OutDir = "C:\TSIS_Data\02_backtest_SmallCaps\data\reference",
  [string]$PingStart = "2004-01-01",
  [string]$PingEnd = "2026-12-31",
  [int]$BlockSize = 100,
  [double]$SleepPerTickerSec = 0.12,
  [int]$TimeoutSec = 30,
  [int]$MaxRetries = 5,
  [double]$RetryBackoffSec = 1.5,
  [int]$LimitTickers = 0,
  [switch]$Resume
)

$ErrorActionPreference = "Stop"

Write-Host "Running build_ping_range_master_resume..." -ForegroundColor Cyan
Write-Host "python = $PythonExe"
Write-Host "script = $ScriptPath"
Write-Host "universe = $UniverseParquet"
Write-Host "outdir = $OutDir"
Write-Host "resume = $Resume"
Write-Host "block_size = $BlockSize"
Write-Host "sleep_per_ticker_sec = $SleepPerTickerSec"
if ($LimitTickers -gt 0) { Write-Host "limit_tickers = $LimitTickers" }

$args = @(
  $ScriptPath,
  "--universe-parquet", $UniverseParquet,
  "--outdir", $OutDir,
  "--ping-start", $PingStart,
  "--ping-end", $PingEnd,
  "--block-size", "$BlockSize",
  "--sleep-per-ticker-sec", "$SleepPerTickerSec",
  "--timeout-sec", "$TimeoutSec",
  "--max-retries", "$MaxRetries",
  "--retry-backoff-sec", "$RetryBackoffSec"
)
if ($LimitTickers -gt 0) {
  $args += @("--limit-tickers", "$LimitTickers")
}
if ($Resume) {
  $args += "--resume"
}

& $PythonExe @args
