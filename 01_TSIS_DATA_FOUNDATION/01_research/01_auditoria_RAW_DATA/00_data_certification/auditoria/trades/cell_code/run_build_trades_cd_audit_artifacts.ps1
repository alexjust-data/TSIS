param(
    [int]$BatchSize = 10000,
    [int]$DiagSampleSize = 100000,
    [int]$IssueSampleSize = 20000,
    [int]$ExampleReservoirSize = 5000,
    [int]$ExampleHead = 30,
    [Nullable[int]]$MaxBatches = $null,
    [string]$PythonExe = "C:\TSIS_Data\02_backtest_SmallCaps\backtest\Scripts\python.exe"
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false

$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\cell_code\build_trades_cd_audit_artifacts.py"
$outDir = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\notebook_cd_cache"
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$log = Join-Path $outDir "build_trades_cd_audit_artifacts_$ts.log"

New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$argsList = @(
    "-u",
    $script,
    "--batch-size", $BatchSize,
    "--diag-sample-size", $DiagSampleSize,
    "--issue-sample-size", $IssueSampleSize,
    "--example-reservoir-size", $ExampleReservoirSize,
    "--example-head", $ExampleHead
)

if ($null -ne $MaxBatches) {
    $argsList += @("--max-batches", $MaxBatches)
}

$startLine = "[{0}] START trades C+D audit builder" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
$configLine = "python={0} script={1} batch_size={2} diag_sample_size={3} issue_sample_size={4} example_reservoir_size={5} example_head={6} max_batches={7} log={8}" -f $PythonExe, $script, $BatchSize, $DiagSampleSize, $IssueSampleSize, $ExampleReservoirSize, $ExampleHead, $MaxBatches, $log

$startLine | Tee-Object -FilePath $log
$configLine | Tee-Object -FilePath $log -Append
"Command: `"$PythonExe`" $($argsList -join ' ')" | Tee-Object -FilePath $log -Append

& $PythonExe @argsList 2>&1 | Tee-Object -FilePath $log -Append
$exitCode = $LASTEXITCODE

$endLine = "[{0}] END exit_code={1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $exitCode
$endLine | Tee-Object -FilePath $log -Append

if ($exitCode -ne 0) {
    throw "Builder failed with exit code $exitCode. Revisa el log: $log"
}

Write-Host ""
Write-Host "Log:" $log
