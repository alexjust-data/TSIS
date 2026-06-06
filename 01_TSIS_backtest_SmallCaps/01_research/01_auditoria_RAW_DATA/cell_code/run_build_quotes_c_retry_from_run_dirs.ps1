param(
    [string]$RunBaseDir = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_download_c",
    [string]$Pattern = "20260327_quotes_lt_1b_c_shard_*_of_08",
    [string]$OutDir = ""
)

$python = "C:\Users\AlexJ\AppData\Local\Programs\Python\Python313\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\build_quotes_c_retry_from_run_dirs.py"

Write-Host "Running build_quotes_c_retry_from_run_dirs..."
Write-Host "python = $python"
Write-Host "script = $script"
Write-Host "run_base_dir = $RunBaseDir"
Write-Host "pattern = $Pattern"
Write-Host "outdir = $OutDir"

if ([string]::IsNullOrWhiteSpace($OutDir)) {
  & $python $script `
    --run-base-dir $RunBaseDir `
    --pattern $Pattern
} else {
  & $python $script `
    --run-base-dir $RunBaseDir `
    --pattern $Pattern `
    --outdir $OutDir
}

exit $LASTEXITCODE
