param(
    [string]$MissingCsv = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_missing_only\20260322_221951_build_quotes_lt_1b_missing_only_from_disk\tasks_quotes_lt_1b_missing_only.csv",
    [string]$EventsHistoryCsv = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_missing_only\20260322_quotes_lt_1b_full_py313\download_events_history.csv",
    [string]$OutDir = ""
)

$python = "C:\Users\AlexJ\AppData\Local\Programs\Python\Python313\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\build_quotes_lt_1b_remaining_only_from_run_state.py"

Write-Host "Running build_quotes_lt_1b_remaining_only_from_run_state..."
Write-Host "python = $python"
Write-Host "script = $script"
Write-Host "missing = $MissingCsv"
Write-Host "events_history = $EventsHistoryCsv"
Write-Host "outdir = $OutDir"

if ([string]::IsNullOrWhiteSpace($OutDir)) {
  & $python $script `
    --missing-csv $MissingCsv `
    --events-history-csv $EventsHistoryCsv
} else {
  & $python $script `
    --missing-csv $MissingCsv `
    --events-history-csv $EventsHistoryCsv `
    --outdir $OutDir
}

exit $LASTEXITCODE
