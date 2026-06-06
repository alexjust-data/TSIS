param(
    [string]$InAll = "C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_all.parquet",
    [string]$Out = "C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_2005_2026.parquet",
    [string]$Start = "2005-01-01",
    [string]$End = "2026-12-31"
)

$python = "C:\Users\AlexJ\AppData\Local\Programs\Python\Python313\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\build_tickers_2005_2026_from_rebuild_compare.py"

Write-Host "Running build_tickers_2005_2026_from_rebuild_compare..."
Write-Host "python = $python"
Write-Host "script = $script"
Write-Host "in_all = $InAll"
Write-Host "out = $Out"
Write-Host "start = $Start"
Write-Host "end = $End"

& $python $script `
  --in-all $InAll `
  --out $Out `
  --start $Start `
  --end $End

exit $LASTEXITCODE
