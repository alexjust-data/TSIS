param(
    [string]$ShardsDir = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_shards\20260325_185507_shard_quotes_lt_1b_remaining_only",
    [string]$RunBaseDir = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_download",
    [int]$NumShards = 10,
    [string]$CompletedShards = "1,2,3,4",
    [string]$PartialShards = "5,6,7,8",
    [string]$NotStartedShards = "9,10",
    [string]$OutDir = ""
)

$python = "C:\Users\AlexJ\AppData\Local\Programs\Python\Python313\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\build_quotes_lt_1b_remaining_after_d_stop.py"

Write-Host "Running build_quotes_lt_1b_remaining_after_d_stop..."
Write-Host "python = $python"
Write-Host "script = $script"
Write-Host "shards_dir = $ShardsDir"
Write-Host "run_base_dir = $RunBaseDir"
Write-Host "num_shards = $NumShards"
Write-Host "completed_shards = $CompletedShards"
Write-Host "partial_shards = $PartialShards"
Write-Host "not_started_shards = $NotStartedShards"
Write-Host "outdir = $OutDir"

if ([string]::IsNullOrWhiteSpace($OutDir)) {
  & $python $script `
    --shards-dir $ShardsDir `
    --run-base-dir $RunBaseDir `
    --num-shards $NumShards `
    --completed-shards $CompletedShards `
    --partial-shards $PartialShards `
    --not-started-shards $NotStartedShards
} else {
  & $python $script `
    --shards-dir $ShardsDir `
    --run-base-dir $RunBaseDir `
    --num-shards $NumShards `
    --completed-shards $CompletedShards `
    --partial-shards $PartialShards `
    --not-started-shards $NotStartedShards `
    --outdir $OutDir
}

exit $LASTEXITCODE
