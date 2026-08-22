[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot
)

$ErrorActionPreference = 'Stop'
$controlRoot = Join-Path $RunRoot '00_control\trades_accelerator'
$request = Join-Path $controlRoot 'stop.requested'
$ack = Join-Path $controlRoot 'stop.acknowledged'
if (-not (Test-Path -LiteralPath $controlRoot -PathType Container)) {
    throw "Trades accelerator control root does not exist: $controlRoot"
}
if (Test-Path -LiteralPath $ack -PathType Leaf) {
    Write-Host "Stop already acknowledged: $ack"
    exit 0
}
New-Item -ItemType File -Path $request -Force | Out-Null
Write-Host "Controlled stop requested: $request"
