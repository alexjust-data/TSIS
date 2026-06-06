$python = "C:\TSIS_Data\02_backtest_SmallCaps\backtest\Scripts\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\cross_lt_1b_universe_vs_quotes_trades_c_and_d.py"
$target = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_2b_active_inactive.parquet"
$runId = Get-Date -Format "yyyyMMdd_HHmmss_lt_2b_quotes_trades_cross_cd"
$outdir = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\universe_coverage_lt_2b\$runId"

Write-Host "Running lt_2b universe coverage cross (C + D inventories)..."
Write-Host "python = $python"
Write-Host "script = $script"
Write-Host "target = $target"
Write-Host "runId  = $runId"
Write-Host "outdir = $outdir"
Write-Host ""

& $python $script --target $target --run-id $runId --outdir $outdir

Write-Host ""
Write-Host "Outputs:"
Write-Host "  $outdir"
