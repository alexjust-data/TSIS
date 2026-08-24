[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('ohlcv_daily', 'ohlcv_1m', 'quotes_')]
    [string]$Family,

    [ValidateSet('Probe', 'Full')]
    [string]$Mode = 'Probe',

    [string]$RunId = '',

    [string]$ConfigPath = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\core_market_family_download_audit_v0_1.yaml',

    [string[]]$Tickers = @(),

    [ValidateRange(1, 12)]
    [int]$Workers = 0,

    [switch]$Resume,

    [switch]$HumanAuthorizedFull,

    [switch]$Detach
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$scriptPath = Join-Path $PSScriptRoot 'audit_family_download.py'
$monitorPath = Join-Path $PSScriptRoot 'monitor_family_download_audit.ps1'
$stopPath = Join-Path $PSScriptRoot 'stop_family_download_audit.ps1'
$outputRoot = 'C:\TSIS_Data\runs\data_ops\core_market_family_download_audit'

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
    $kind = if ($Mode -eq 'Probe') { 'probe' } else { 'audit' }
    $RunId = "${stamp}_${Family}_${kind}_v0_1"
}

$runRoot = Join-Path $outputRoot $RunId
$monitorCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$monitorPath`" -RunRoot `"$runRoot`" -Watch"
$stopCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$stopPath`" -RunRoot `"$runRoot`""
$arguments = @(
    $scriptPath,
    '--config', $ConfigPath,
    '--run-id', $RunId,
    '--mode', $Mode.ToLowerInvariant(),
    '--family', $Family
)
if ($Tickers.Count -gt 0) { $arguments += @('--tickers', ($Tickers -join ',')) }
if ($Workers -gt 0) { $arguments += @('--workers', [string]$Workers) }
if ($Resume) { $arguments += '--resume' }
if ($Mode -eq 'Full') { $arguments += '--human-authorized-full' }

Write-Host "Run ID: $RunId"
Write-Host "Family: $Family"
Write-Host "Mode: $Mode"
Write-Host "Input evidence: closed core_market_raw_alignment audit + RAW clock column (read-only)"
Write-Host "Output root: $runRoot"
Write-Host "Monitor: $monitorCommand"
Write-Host "Safe stop: $stopCommand"
Write-Host 'Success: every selected ticker committed, zero failures, final manifest.'
Write-Host 'Resume: repeat this command with the same RunId and -Resume.'

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

