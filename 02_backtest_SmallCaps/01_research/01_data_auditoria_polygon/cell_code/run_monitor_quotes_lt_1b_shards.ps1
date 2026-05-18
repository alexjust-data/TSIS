param(
    [string]$BaseDir = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_download",
    [string]$Pattern = "20260325_quotes_lt_1b_shard_*_of_10",
    [double]$IntervalSec = 10,
    [int]$Iterations = 0
)

$python = "C:\Users\AlexJ\AppData\Local\Programs\Python\Python313\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\monitor_quotes_lt_1b_shards.py"

Write-Host "Running monitor_quotes_lt_1b_shards..."
Write-Host "python = $python"
Write-Host "script = $script"
Write-Host "base_dir = $BaseDir"
Write-Host "pattern = $Pattern"
Write-Host "interval_sec = $IntervalSec"
Write-Host "iterations = $Iterations"

& $python $script `
  --base-dir $BaseDir `
  --pattern $Pattern `
  --interval-sec $IntervalSec `
  --iterations $Iterations

exit $LASTEXITCODE
