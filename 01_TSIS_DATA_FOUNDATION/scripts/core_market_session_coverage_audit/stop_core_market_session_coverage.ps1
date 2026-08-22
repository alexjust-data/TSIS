[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot
)

$ErrorActionPreference = 'Stop'
$control = Join-Path $RunRoot '00_control'
if (-not (Test-Path -LiteralPath $control -PathType Container)) {
    throw "Run control directory does not exist: $control"
}
$request = Join-Path $control 'stop.requested'
Set-Content -LiteralPath $request -Value ([datetime]::UtcNow.ToString('o')) -Encoding UTF8
Write-Host "Controlled stop requested: $request"
Write-Host 'The active ticker may finish before the runner stops. Resume with the same run ID and -Resume.'
