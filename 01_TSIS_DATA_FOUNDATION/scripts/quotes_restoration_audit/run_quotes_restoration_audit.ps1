[CmdletBinding()]
param(
    [ValidateSet('Probe','Full')][string]$Mode = 'Probe',
    [string]$RunId = '',
    [string]$ConfigPath = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\quotes_restoration_audit_v0_1.yaml',
    [string[]]$Tickers = @(),
    [ValidateRange(1,8)][int]$Workers = 0,
    [switch]$Resume,
    [switch]$HumanAuthorizedFull,
    [switch]$Detach
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$runner = Join-Path $PSScriptRoot 'audit_quotes_restoration.py'
$monitor = Join-Path $PSScriptRoot 'monitor_quotes_restoration_audit.ps1'
$stop = Join-Path $PSScriptRoot 'stop_quotes_restoration_audit.ps1'
if ($Mode -eq 'Full' -and -not $HumanAuthorizedFull) { throw 'Full audit requires -HumanAuthorizedFull.' }
if ([string]::IsNullOrWhiteSpace($RunId)) {
    $stamp = [datetime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
    $RunId = "${stamp}_quotes_restoration_$($Mode.ToLowerInvariant())_v0_1"
}
$runRoot = Join-Path 'C:\TSIS_Data\runs\data_ops\quotes_restoration_audit' $RunId
$arguments = @($runner,'--config',$ConfigPath,'--run-id',$RunId,'--mode',$Mode.ToLowerInvariant())
if ($Tickers.Count -gt 0) { $arguments += @('--tickers',($Tickers -join ',')) }
if ($Workers -gt 0) { $arguments += @('--workers',[string]$Workers) }
if ($Resume) { $arguments += '--resume' }
if ($HumanAuthorizedFull) { $arguments += '--human-authorized-full' }
$monitorCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$monitor`" -RunRoot `"$runRoot`" -Watch"
$stopCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$stop`" -RunRoot `"$runRoot`""
Write-Host "Run ID: $RunId"
Write-Host "Mode: $Mode"
Write-Host 'Inputs: historical C pre-merge inventory + G:\TSIS\data\quotes (read-only)'
Write-Host "Output root: $runRoot"
Write-Host "Monitor: $monitorCommand"
Write-Host "Safe stop: $stopCommand"
Write-Host 'Success: all selected historical-C tickers committed; physical findings reported exactly.'
Write-Host 'Resume: repeat this exact command with -Resume.'
if ($Detach) {
    $control = Join-Path $runRoot '00_control'
    New-Item -ItemType Directory -Path $control -Force | Out-Null
    $process = Start-Process -FilePath 'python' -ArgumentList $arguments -PassThru -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $control 'wrapper_stdout.log') `
        -RedirectStandardError (Join-Path $control 'wrapper_stderr.log')
    Write-Host "Launched PID: $($process.Id)"
    exit 0
}
& python @arguments
exit $LASTEXITCODE
