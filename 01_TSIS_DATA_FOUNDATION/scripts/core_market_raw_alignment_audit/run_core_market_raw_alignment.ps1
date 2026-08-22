[CmdletBinding()]
param(
    [ValidateSet('Probe', 'Full')]
    [string]$Mode = 'Probe',

    [string]$RunId = '',

    [string]$ConfigPath = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\core_market_raw_alignment_audit_v0_1.yaml',

    [string[]]$Tickers = @(),

    [switch]$Resume,

    [switch]$HumanAuthorizedFull,

    [switch]$Detach
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$scriptPath = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\audit_core_market_raw_alignment.py'
$outputRoot = 'C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit'

if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
    throw "Auditor script does not exist: $scriptPath"
}
if (-not (Test-Path -LiteralPath $ConfigPath -PathType Leaf)) {
    throw "Config does not exist: $ConfigPath"
}
if ($Mode -eq 'Full' -and -not $HumanAuthorizedFull) {
    throw 'Full audit refused. Pass -HumanAuthorizedFull only after explicit human authorization.'
}
if ($Mode -eq 'Full' -and $Tickers.Count -gt 0) {
    throw 'Full mode must use the exact governed universe; do not pass -Tickers.'
}
if ([string]::IsNullOrWhiteSpace($RunId)) {
    $stamp = [datetime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
    $RunId = if ($Mode -eq 'Probe') {
        "${stamp}_core_market_raw_alignment_probe_v0_1"
    }
    else {
        "${stamp}_core_market_raw_alignment_audit_v0_1"
    }
}

$runRoot = Join-Path $outputRoot $RunId
$monitorPath = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\monitor_core_market_raw_alignment.ps1'
$monitorCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$monitorPath`" -RunRoot `"$runRoot`" -Watch"

$arguments = @(
    $scriptPath,
    '--config', $ConfigPath,
    '--run-id', $RunId,
    '--mode', $Mode.ToLowerInvariant()
)
if ($Tickers.Count -gt 0) {
    $arguments += @('--tickers', ($Tickers -join ','))
}
if ($Resume) {
    $arguments += '--resume'
}
if ($Mode -eq 'Full') {
    $arguments += '--human-authorized-full'
}

Write-Host "Run ID: $RunId"
Write-Host "Mode: $Mode"
Write-Host "Run root: $runRoot"
Write-Host 'Monitor command:'
Write-Host "  $monitorCommand"

if ($Detach) {
    $controlRoot = Join-Path $runRoot '00_control'
    New-Item -ItemType Directory -Path $controlRoot -Force | Out-Null
    $stdoutPath = Join-Path $controlRoot 'wrapper_stdout.log'
    $stderrPath = Join-Path $controlRoot 'wrapper_stderr.log'
    $process = Start-Process `
        -FilePath 'python' `
        -ArgumentList $arguments `
        -PassThru `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath
    Write-Host "Launched PID: $($process.Id)"
    Write-Host "Stdout: $stdoutPath"
    Write-Host "Stderr: $stderrPath"
    exit 0
}

& python @arguments
exit $LASTEXITCODE
