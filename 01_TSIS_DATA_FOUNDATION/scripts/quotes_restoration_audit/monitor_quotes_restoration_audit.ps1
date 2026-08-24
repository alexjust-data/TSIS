[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RunRoot,
    [switch]$Watch
)
$argsList = @((Join-Path $PSScriptRoot 'monitor_quotes_restoration_audit.py'), '--run-root', $RunRoot)
if ($Watch) { $argsList += '--watch' }
& python @argsList
exit $LASTEXITCODE
