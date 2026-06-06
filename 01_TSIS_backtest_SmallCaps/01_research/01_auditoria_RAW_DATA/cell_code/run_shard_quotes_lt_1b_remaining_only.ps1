param(
    [string]$RemainingCsv = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_remaining_only\20260325_184118_build_quotes_lt_1b_remaining_only_from_run_state\tasks_quotes_lt_1b_remaining_only.csv",
    [int]$NumShards = 10,
    [string]$OutDir = ""
)

$python = "C:\Users\AlexJ\AppData\Local\Programs\Python\Python313\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\shard_quotes_lt_1b_remaining_only.py"

Write-Host "Running shard_quotes_lt_1b_remaining_only..."
Write-Host "python = $python"
Write-Host "script = $script"
Write-Host "remaining = $RemainingCsv"
Write-Host "num_shards = $NumShards"
Write-Host "outdir = $OutDir"

if ([string]::IsNullOrWhiteSpace($OutDir)) {
  & $python $script `
    --remaining-csv $RemainingCsv `
    --num-shards $NumShards
} else {
  & $python $script `
    --remaining-csv $RemainingCsv `
    --num-shards $NumShards `
    --outdir $OutDir
}

exit $LASTEXITCODE
