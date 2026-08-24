[CmdletBinding()]
param([Parameter(Mandatory = $true)][string]$RunRoot)
$control = Join-Path $RunRoot '00_control'
if (-not (Test-Path -LiteralPath $control -PathType Container)) { throw "Missing control root: $control" }
$request = Join-Path $control 'stop.requested'
Set-Content -LiteralPath $request -Value ([datetime]::UtcNow.ToString('o')) -Encoding UTF8
Write-Host "Controlled stop requested: $request"
