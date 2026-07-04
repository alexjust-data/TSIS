param(
    [string]$ProjectRoot = "C:\TSIS_Data\01_TSIS_backtest_SmallCaps",
    [string[]]$RunRoots = @(),
    [string]$UniverseParquet = "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet",
    [string]$OutputRoot = "E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded",
    [string]$ConsolidationRunRoot = "",
    [string]$ManifestOutput = "",
    [int]$ExpectedTickers = 4824,
    [int]$ProgressEvery = 500,
    [int]$SampleRows = 1000,
    [string]$PythonExe = "python",
    [switch]$SkipManifest,
    [switch]$NoRequireComplete,
    [switch]$Overwrite,
    [switch]$Promote
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONUNBUFFERED = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"

function Assert-PathExists {
    param(
        [string]$Path,
        [string]$Label
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Missing ${Label}: $Path"
    }
}

Assert-PathExists -Path $ProjectRoot -Label "ProjectRoot"
Assert-PathExists -Path $UniverseParquet -Label "UniverseParquet"

$ScriptPath = Join-Path $ProjectRoot "scripts\inspection\minute\consolidate_ohlcv_1m_quote_guarded_lt1b_v0_1.py"
Assert-PathExists -Path $ScriptPath -Label "LT1B consolidator script"

if ($RunRoots.Count -eq 0) {
    $RunsRoot = Join-Path $ProjectRoot "runs\data_foundation\ohlcv_1m_quote_guarded"
    $BroadRun = Join-Path $RunsRoot "quote_guarded_v0_2_20260627_091838"
    $Supplement = Get-ChildItem -LiteralPath $RunsRoot -Directory |
        Where-Object { $_.Name -like "quote_guarded_v0_2_lt1b_missing180_*" } |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
    if ($null -eq $Supplement) {
        throw "Could not find latest quote_guarded_v0_2_lt1b_missing180_* supplement run."
    }
    $RunRoots = @($BroadRun, $Supplement.FullName)
}

$NormalizedRunRoots = @()
foreach ($Root in $RunRoots) {
    foreach ($Token in ([string]$Root -split '[,;]')) {
        $Trimmed = $Token.Trim().Trim('"')
        if (-not [string]::IsNullOrWhiteSpace($Trimmed)) {
            $NormalizedRunRoots += $Trimmed
        }
    }
}
$RunRoots = $NormalizedRunRoots

foreach ($Root in $RunRoots) {
    Assert-PathExists -Path $Root -Label "RunRoot"
}

if ([string]::IsNullOrWhiteSpace($ConsolidationRunRoot)) {
    $RunId = "quote_guarded_lt1b_consolidation_{0}" -f (Get-Date -Format "yyyyMMdd_HHmmss")
    $ConsolidationRunRoot = Join-Path $ProjectRoot "runs\data_foundation\ohlcv_1m_quote_guarded\$RunId"
}
New-Item -ItemType Directory -Force -Path $ConsolidationRunRoot | Out-Null

$LogPath = Join-Path $ConsolidationRunRoot "consolidation.log"

Write-Host "TSIS quote-guarded LT1B consolidator v0_1"
Write-Host ("Consolidation run root: {0}" -f $ConsolidationRunRoot)
Write-Host ("Universe parquet: {0}" -f $UniverseParquet)
Write-Host ("Expected tickers: {0}" -f $ExpectedTickers)
Write-Host "Run roots:"
foreach ($Root in $RunRoots) {
    Write-Host ("  {0}" -f $Root)
}
Write-Host ""

$Args = @(
    $ScriptPath,
    "--universe-parquet", $UniverseParquet,
    "--expected-tickers", [string]$ExpectedTickers,
    "--consolidation-run-root", $ConsolidationRunRoot,
    "--output-root", $OutputRoot,
    "--progress-every", [string]$ProgressEvery,
    "--sample-rows", [string]$SampleRows,
    "--run-roots"
)
$Args += $RunRoots

if (-not [string]::IsNullOrWhiteSpace($ManifestOutput)) {
    $Args += @("--manifest-output", $ManifestOutput)
}
if ($SkipManifest) {
    $Args += "--skip-manifest"
}
if ($NoRequireComplete) {
    $Args += "--no-require-complete"
}
if ($Overwrite) {
    $Args += "--overwrite"
}
if ($Promote) {
    $Args += "--promote"
}

& $PythonExe @Args 2>&1 | Tee-Object -FilePath $LogPath
if ($LASTEXITCODE -ne 0) {
    throw "LT1B consolidation failed with exit code $LASTEXITCODE. Log: $LogPath"
}

Write-Host ""
Write-Host "Completed."
Write-Host ("Log: {0}" -f $LogPath)
Write-Host ("Summary: {0}" -f (Join-Path $ConsolidationRunRoot "consolidation_summary.json"))
