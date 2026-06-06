param(
    [string]$InputParquet = "C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_2005_2026_upper.parquet",
    [string]$DailyRoot = "D:\ohlcv_daily",
    [string]$MinuteRoot = "D:\ohlcv_1m",
    [int]$TopN = 50
)

$python = "C:\Users\AlexJ\AppData\Local\Programs\Python\Python313\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\audit_ohlcv_input_vs_daily_vs_1m_cli.py"

Write-Host "Running audit_ohlcv_input_vs_daily_vs_1m..."
Write-Host "python = $python"
Write-Host "script = $script"
Write-Host "input_parquet = $InputParquet"
Write-Host "daily_root = $DailyRoot"
Write-Host "minute_root = $MinuteRoot"
Write-Host "top_n = $TopN"

& $python $script `
  --input-parquet $InputParquet `
  --daily-root $DailyRoot `
  --minute-root $MinuteRoot `
  --top-n $TopN

exit $LASTEXITCODE
