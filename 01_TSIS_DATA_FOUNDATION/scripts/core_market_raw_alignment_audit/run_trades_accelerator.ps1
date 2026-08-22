[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,

    [ValidateRange(2, 8)]
    [int]$Workers = 6,

    [switch]$PreflightOnly,

    [switch]$HumanAuthorized,

    [switch]$Detach
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$scriptPath = Join-Path $PSScriptRoot 'accelerate_trades_workers.py'
$monitorPath = Join-Path $PSScriptRoot 'monitor_trades_accelerator.ps1'
$stopPath = Join-Path $PSScriptRoot 'stop_trades_accelerator.ps1'
if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
    throw "Missing Trades accelerator: $scriptPath"
}
if (-not $HumanAuthorized) {
    throw 'Trades acceleration refused. Pass -HumanAuthorized after explicit human approval.'
}

$arguments = @(
    $scriptPath,
    '--run-root', $RunRoot,
    '--workers', [string]$Workers,
    '--human-authorized'
)
if ($PreflightOnly) { $arguments += '--preflight-only' }

Write-Host "Run root: $RunRoot"
Write-Host "Trades workers: $Workers"
Write-Host 'Monitor command:'
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File `"$monitorPath`" -RunRoot `"$RunRoot`" -Watch"
Write-Host 'Safe stop command:'
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File `"$stopPath`" -RunRoot `"$RunRoot`""

if ($Detach) {
    $controlRoot = Join-Path $RunRoot '00_control\trades_accelerator'
    New-Item -ItemType Directory -Path $controlRoot -Force | Out-Null
    $process = Start-Process -FilePath 'python' -ArgumentList $arguments -PassThru -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $controlRoot 'wrapper_stdout.log') `
        -RedirectStandardError (Join-Path $controlRoot 'wrapper_stderr.log')
    Write-Host "Launched coordinator PID: $($process.Id)"
    exit 0
}

& python @arguments
exit $LASTEXITCODE
