$ErrorActionPreference = "Stop"

$appRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$fullFinal = "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAILY_PATTERN_ATLAS_0001\runs\20260825_full_v0_1\final"
$probeFinal = "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAILY_PATTERN_ATLAS_0001\runs\20260825_probe_v0_2\final"

$env:ATLAS_FINAL_ROOT = if (Test-Path -LiteralPath (Join-Path $fullFinal "terminal_certification.json")) {
    $fullFinal
} else {
    $probeFinal
}

Write-Host "Atlas data: $env:ATLAS_FINAL_ROOT"
Write-Host "API: http://127.0.0.1:8765"
Write-Host "UI:  http://localhost:3000"

$api = Start-Process -FilePath "python" -ArgumentList @(
    "-m", "uvicorn", "api.server_v2:app", "--host", "127.0.0.1", "--port", "8765"
) -WorkingDirectory $appRoot -PassThru -WindowStyle Hidden

try {
    npm.cmd run dev
} finally {
    if (-not $api.HasExited) {
        Stop-Process -Id $api.Id
    }
}
