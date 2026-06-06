param(
    [string]$Input = "C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_2005_2026.parquet",
    [string]$Out = "C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_2005_2026_upper.parquet"
)

$python = "C:\Users\AlexJ\AppData\Local\Programs\Python\Python313\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\build_tickers_2005_2026_upper_from_rebuild_compare.py"
$defaultInput = "C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_2005_2026.parquet"
$effectiveInput = if ([string]::IsNullOrWhiteSpace($Input)) { $defaultInput } else { $Input }

Write-Host "Running build_tickers_2005_2026_upper_from_rebuild_compare..."
Write-Host "python = $python"
Write-Host "script = $script"
Write-Host "input = $effectiveInput"
Write-Host "out = $Out"

if ([string]::IsNullOrWhiteSpace($Input)) {
  & $python $script `
    --out $Out
} else {
  & $python $script `
    --input $Input `
    --out $Out
}

exit $LASTEXITCODE
