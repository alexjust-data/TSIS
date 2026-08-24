[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot
)

$ErrorActionPreference = 'Stop'
$resolved = (Resolve-Path -LiteralPath $RunRoot).Path
$governedRoot = 'C:\TSIS_Data\runs\data_ops\core_market_family_download_audit'
if (-not $resolved.StartsWith($governedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing stop request outside governed root: $resolved"
}
$control = Join-Path $resolved '00_control'
if (-not (Test-Path -LiteralPath $control -PathType Container)) {
    throw "Run control directory does not exist: $control"
}
$request = Join-Path $control 'stop.requested'
[System.IO.File]::WriteAllText($request, [datetime]::UtcNow.ToString('o'))
Write-Host "Controlled stop requested: $request"
Write-Host 'Active ticker tasks may finish before stop. Resume with the same run ID and -Resume.'

