param(
    [string]$QuotesCRoot = "C:\TSIS_Data\data\quotes",
    [string]$QuotesDRoot = "D:\quotes",
    [string]$TradesCRoot = "C:\TSIS_Data\data\trades_ticks_prod_2005_2026",
    [string]$TradesDRoot = "D:\trades_ticks_prod_2005_2026",
    [string]$UniverseCsv = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_tasks\20260322_221029_build_quotes_lt_1b_master_from_ohlcv_windows\tasks_quotes_lt_1b_master.csv",
    [string]$OutDir = ""
)

$python = "C:\Users\AlexJ\AppData\Local\Programs\Python\Python313\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\compare_quotes_vs_trades_total_coverage.py"

Write-Host "Running compare_quotes_vs_trades_total_coverage..."
Write-Host "python = $python"
Write-Host "script = $script"
Write-Host "quotes_c_root = $QuotesCRoot"
Write-Host "quotes_d_root = $QuotesDRoot"
Write-Host "trades_c_root = $TradesCRoot"
Write-Host "trades_d_root = $TradesDRoot"
Write-Host "universe_csv = $UniverseCsv"
Write-Host "outdir = $OutDir"

if ([string]::IsNullOrWhiteSpace($OutDir)) {
  & $python $script `
    --quotes-c-root $QuotesCRoot `
    --quotes-d-root $QuotesDRoot `
    --trades-c-root $TradesCRoot `
    --trades-d-root $TradesDRoot `
    --universe-csv $UniverseCsv
} else {
  & $python $script `
    --quotes-c-root $QuotesCRoot `
    --quotes-d-root $QuotesDRoot `
    --trades-c-root $TradesCRoot `
    --trades-d-root $TradesDRoot `
    --universe-csv $UniverseCsv `
    --outdir $OutDir
}

exit $LASTEXITCODE
