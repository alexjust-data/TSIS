[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,

    [switch]$Watch,

    [ValidateRange(2, 300)]
    [int]$IntervalSeconds = 10
)

$ErrorActionPreference = 'Stop'
$monitor = Join-Path $PSScriptRoot 'monitor_family_download_audit.py'
$arguments = @($monitor, '--run-root', $RunRoot, '--interval-seconds', [string]$IntervalSeconds)
if ($Watch) { $arguments += '--watch' }
& python @arguments
exit $LASTEXITCODE

