[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,

    [switch]$Watch,

    [ValidateRange(2, 300)]
    [int]$IntervalSeconds = 10
)

$ErrorActionPreference = 'Stop'
$ledgerMonitor = Join-Path $PSScriptRoot 'monitor_core_market_session_coverage_ledger.py'
if (-not (Test-Path -LiteralPath $ledgerMonitor -PathType Leaf)) {
    throw "Missing ledger monitor: $ledgerMonitor"
}

$arguments = @(
    $ledgerMonitor,
    '--run-root', $RunRoot,
    '--interval-seconds', [string]$IntervalSeconds
)
if ($Watch) { $arguments += '--watch' }

& python @arguments
exit $LASTEXITCODE
