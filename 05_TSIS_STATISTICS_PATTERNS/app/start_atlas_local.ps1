param(
    [string]$RunsRoot = "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAILY_PATTERN_ATLAS_0001\runs",
    [switch]$ResolveOnly
)

$ErrorActionPreference = "Stop"

function Resolve-AtlasFinalRoot {
    param([Parameter(Mandatory = $true)][string]$Root)

    if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
        throw "Atlas runs root unavailable: $Root"
    }

    $candidates = foreach ($runRoot in Get-ChildItem -LiteralPath $Root -Directory) {
        $finalRoot = Join-Path $runRoot.FullName "final"
        $certificationPath = Join-Path $finalRoot "terminal_certification.json"
        $preManifestPath = Join-Path $runRoot.FullName "pre_manifest.json"
        $operationFinalPath = Join-Path $runRoot.FullName "operation_final_manifest.json"
        if (-not (Test-Path -LiteralPath $certificationPath -PathType Leaf) -or
            -not (Test-Path -LiteralPath $preManifestPath -PathType Leaf) -or
            -not (Test-Path -LiteralPath $operationFinalPath -PathType Leaf)) {
            continue
        }
        try {
            $certification = Get-Content -Raw -LiteralPath $certificationPath | ConvertFrom-Json
            $preManifest = Get-Content -Raw -LiteralPath $preManifestPath | ConvertFrom-Json
            $operationFinal = Get-Content -Raw -LiteralPath $operationFinalPath | ConvertFrom-Json
        } catch {
            continue
        }
        # Fail closed: exclude every run that consumed the defective adjusted root.
        if (([string]$operationFinal.status).ToLowerInvariant() -ne "pass" -or
            [string]$preManifest.input_roots.raw -ne "G:/TSIS/data/ohlcv_daily" -or
            $null -ne $preManifest.input_roots.adjusted) {
            continue
        }
        $mode = ([string]$certification.mode).ToLowerInvariant()
        if (([string]$certification.status).ToLowerInvariant() -ne "pass" -or
            $mode -notin @("full", "probe")) {
            continue
        }
        try {
            $certifiedAt = [DateTimeOffset]::Parse([string]$certification.certified_at)
        } catch {
            $certifiedAt = [DateTimeOffset]::MinValue
        }
        [PSCustomObject]@{
            FinalRoot = $finalRoot
            ModePriority = if ($mode -eq "full") { 1 } else { 0 }
            CertifiedAt = $certifiedAt
            RunName = $runRoot.Name
        }
    }

    $selected = $candidates | Sort-Object -Property @(
        @{ Expression = { $_.ModePriority }; Descending = $true },
        @{ Expression = { $_.CertifiedAt }; Descending = $true },
        @{ Expression = { $_.RunName }; Descending = $true }
    ) | Select-Object -First 1
    if ($null -eq $selected) {
        throw "No terminal PASS Atlas run is available under: $Root"
    }
    return $selected.FinalRoot
}

$appRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:ATLAS_FINAL_ROOT = Resolve-AtlasFinalRoot -Root $RunsRoot

if ($ResolveOnly) {
    Write-Output $env:ATLAS_FINAL_ROOT
    return
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
