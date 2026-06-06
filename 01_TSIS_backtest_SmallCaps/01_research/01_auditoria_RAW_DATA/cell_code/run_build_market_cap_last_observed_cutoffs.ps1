$python = "C:\TSIS_Data\02_backtest_SmallCaps\backtest\Scripts\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\build_market_cap_last_observed_cutoffs.py"
$population = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\population_target_pti\population_target_pti_run_01\population_target_pti.parquet"
$universe = "C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti\tickers_2005_2026_upper.parquet"
$outdir = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff"
$runId = Split-Path $outdir -Leaf

Write-Host "Running build_market_cap_last_observed_cutoffs..."
Write-Host "python     = $python"
Write-Host "script     = $script"
Write-Host "population = $population"
Write-Host "universe   = $universe"
Write-Host "outdir     = $outdir"
Write-Host ""

& $python $script --population $population --universe $universe --outdir $outdir --run-id $runId
