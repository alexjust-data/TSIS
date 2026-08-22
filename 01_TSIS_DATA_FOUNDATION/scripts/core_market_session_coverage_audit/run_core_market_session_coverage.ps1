[CmdletBinding()]
param(
    [ValidateSet('Probe', 'Full')]
    [string]$Mode = 'Probe',

    [string]$RunId = '',

    [string]$ConfigPath = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\core_market_session_coverage_audit_v0_1.yaml',

    [string[]]$Tickers = @(),

    [switch]$Resume,

    [switch]$HumanAuthorizedFull,

    [switch]$Detach
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$scriptPath = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_session_coverage_audit\audit_core_market_session_coverage.py'
$outputRoot = 'C:\TSIS_Data\runs\data_ops\core_market_session_coverage_audit'
$monitorPath = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_session_coverage_audit\monitor_core_market_session_coverage.ps1'

if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) { throw "Missing runner: $scriptPath" }
if (-not (Test-Path -LiteralPath $ConfigPath -PathType Leaf)) { throw "Missing config: $ConfigPath" }
if ($Mode -eq 'Full' -and -not $HumanAuthorizedFull) {
    throw 'Full audit refused. Pass -HumanAuthorizedFull only after explicit human authorization.'
}
if ($Mode -eq 'Full' -and $Tickers.Count -gt 0) {
    throw 'Full mode must use the exact governed 4,824-member universe.'
}
if ([string]::IsNullOrWhiteSpace($RunId)) {
    $stamp = [datetime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
    $RunId = if ($Mode -eq 'Probe') {
        "${stamp}_core_market_session_coverage_probe_v0_1"
    } else {
        "${stamp}_core_market_session_coverage_audit_v0_1"
    }
}

$runRoot = Join-Path $outputRoot $RunId
$monitorCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$monitorPath`" -RunRoot `"$runRoot`" -Watch"
$arguments = @($scriptPath, '--config', $ConfigPath, '--run-id', $RunId, '--mode', $Mode.ToLowerInvariant())
if ($Tickers.Count -gt 0) { $arguments += @('--tickers', ($Tickers -join ',')) }
if ($Resume) { $arguments += '--resume' }
if ($Mode -eq 'Full') { $arguments += '--human-authorized-full' }

Write-Host "Run ID: $RunId"
Write-Host "Run root: $runRoot"
Write-Host 'Monitor command:'
Write-Host "  $monitorCommand"
Write-Host 'Safe stop command:'
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\stop_core_market_session_coverage.ps1`" -RunRoot `"$runRoot`""

if ($Detach) {
    $controlRoot = Join-Path $runRoot '00_control'
    New-Item -ItemType Directory -Path $controlRoot -Force | Out-Null
    $process = Start-Process -FilePath 'python' -ArgumentList $arguments -PassThru -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $controlRoot 'wrapper_stdout.log') `
        -RedirectStandardError (Join-Path $controlRoot 'wrapper_stderr.log')
    Write-Host "Launched PID: $($process.Id)"
    exit 0
}

& python @arguments
exit $LASTEXITCODE
