$python = "C:\TSIS_Data\02_backtest_SmallCaps\backtest\Scripts\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\audit_trades_shards_vs_lt1b_cutoff.py"

Write-Host "Running audit_trades_shards_vs_lt1b_cutoff..."
Write-Host "python = $python"
Write-Host "script = $script"
Write-Host ""

& $python $script
