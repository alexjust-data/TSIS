param(
    [ValidateSet("split-affected", "all-existing")]
    [string]$Mode = "split-affected",

    [string]$ProjectRoot = "C:\TSIS_Data\01_TSIS_backtest_SmallCaps",
    [string]$MinuteRoot = "E:\TSIS\data\ohlcv_1m",
    [string]$SplitsRoot = "E:\TSIS\data\additional\corporate_actions\splits",
    [string]$RunRoot = "",
    [string]$OutputRoot = "",
    [int]$ChunkSize = 5000,
    [Nullable[int]]$MinYear = $null,
    [Nullable[int]]$MaxYear = $null,
    [Nullable[int]]$Limit = $null,
    [int]$SmokeLimit = 100,
    [string]$PythonExe = "python",
    [switch]$SmokeOnly,
    [switch]$RunAudit,
    [switch]$Overwrite
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

function Invoke-NativeLogged {
    param(
        [string]$LogPath,
        [string[]]$CommandArgs
    )

    & $PythonExe @CommandArgs 2>&1 | Tee-Object -FilePath $LogPath
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE. Log: $LogPath"
    }
}

Assert-PathExists -Path $ProjectRoot -Label "ProjectRoot"
Assert-PathExists -Path $MinuteRoot -Label "MinuteRoot"
Assert-PathExists -Path $SplitsRoot -Label "SplitsRoot"

$ManifestBuilder = Join-Path $ProjectRoot "scripts\build_1m_split_normalized_materialization_manifest.py"
$Materializer = Join-Path $ProjectRoot "scripts\materialize_1m_split_normalized.py"
$AuditScript = Join-Path $ProjectRoot "scripts\inspection\minute\audit_1m_split_full_universe.py"

Assert-PathExists -Path $ManifestBuilder -Label "manifest builder"
Assert-PathExists -Path $Materializer -Label "materializer"
if ($RunAudit) {
    Assert-PathExists -Path $AuditScript -Label "audit script"
}

if ([string]::IsNullOrWhiteSpace($RunRoot)) {
    $RunId = "{0}_{1}" -f ($Mode -replace "-", "_"), (Get-Date -Format "yyyyMMdd_HHmmss")
    $RunRoot = Join-Path $ProjectRoot "runs\data_foundation\1m_split_normalized_full_universe_candidate\$RunId"
}

if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    if ($Mode -eq "all-existing") {
        $OutputRoot = "E:\TSIS\data\ohlcv_1m_split_normalized_physical_full_candidate"
    } else {
        $OutputRoot = "E:\TSIS\data\ohlcv_1m_split_normalized_full_universe_candidate"
    }
}

New-Item -ItemType Directory -Force -Path $RunRoot | Out-Null

$Manifest = Join-Path $RunRoot ("manifest_{0}.csv" -f ($Mode -replace "-", "_"))
$ChunksDir = Join-Path $RunRoot "chunks"
$RunSummaryPath = Join-Path $RunRoot "_run_summary.json"
$BuildManifestLog = Join-Path $RunRoot "build_manifest.log"

$Config = [ordered]@{
    created_at = (Get-Date).ToString("o")
    mode = $Mode
    project_root = $ProjectRoot
    minute_root = $MinuteRoot
    splits_root = $SplitsRoot
    run_root = $RunRoot
    output_root = $OutputRoot
    manifest = $Manifest
    chunks_dir = $ChunksDir
    chunk_size = $ChunkSize
    min_year = $MinYear
    max_year = $MaxYear
    limit = $Limit
    smoke_only = [bool]$SmokeOnly
    smoke_limit = $SmokeLimit
    run_audit = [bool]$RunAudit
    overwrite = [bool]$Overwrite
}
$Config | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $RunSummaryPath -Encoding UTF8

Write-Host "TSIS 1m split-normalized materialization runner"
Write-Host "Mode: $Mode"
Write-Host "Run root: $RunRoot"
Write-Host "Output root: $OutputRoot"
Write-Host ""

if ($SmokeOnly) {
    $SmokeManifest = Join-Path $RunRoot "manifest_smoke.csv"
    $SmokeArgs = @(
        $ManifestBuilder,
        "--minute-root", $MinuteRoot,
        "--splits-root", $SplitsRoot,
        "--output", $SmokeManifest,
        "--mode", $Mode,
        "--limit", [string]$SmokeLimit
    )
    if ($null -ne $MinYear) {
        $SmokeArgs += @("--min-year", [string]$MinYear)
    }
    if ($null -ne $MaxYear) {
        $SmokeArgs += @("--max-year", [string]$MaxYear)
    }

    Invoke-NativeLogged -LogPath (Join-Path $RunRoot "build_manifest_smoke.log") -CommandArgs $SmokeArgs
    Write-Host ""
    Write-Host "Smoke manifest written:"
    Write-Host $SmokeManifest
    exit 0
}

$BuildArgs = @(
    $ManifestBuilder,
    "--minute-root", $MinuteRoot,
    "--splits-root", $SplitsRoot,
    "--output", $Manifest,
    "--mode", $Mode,
    "--chunk-size", [string]$ChunkSize,
    "--chunks-dir", $ChunksDir
)
if ($null -ne $MinYear) {
    $BuildArgs += @("--min-year", [string]$MinYear)
}
if ($null -ne $MaxYear) {
    $BuildArgs += @("--max-year", [string]$MaxYear)
}
if ($null -ne $Limit) {
    $BuildArgs += @("--limit", [string]$Limit)
}

Invoke-NativeLogged -LogPath $BuildManifestLog -CommandArgs $BuildArgs

$ManifestRows = (Import-Csv -LiteralPath $Manifest).Count
if ($ManifestRows -eq 0) {
    throw "Manifest has zero rows: $Manifest"
}

$Chunks = @(Get-ChildItem -LiteralPath $ChunksDir -Filter "*.csv" -File | Sort-Object Name)
if ($Chunks.Count -eq 0) {
    throw "No chunk files were produced under: $ChunksDir"
}

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

$ChunkIndex = 0
foreach ($Chunk in $Chunks) {
    $ChunkIndex += 1
    $ChunkLog = Join-Path $RunRoot ("materialize_{0}.log" -f $Chunk.BaseName)
    Write-Host ("[{0}/{1}] Materializing {2}" -f $ChunkIndex, $Chunks.Count, $Chunk.Name)

    $MaterializeArgs = @(
        $Materializer,
        "--minute-root", $MinuteRoot,
        "--splits-root", $SplitsRoot,
        "--output-root", $OutputRoot,
        "--manifest", $Chunk.FullName
    )
    if ($Overwrite) {
        $MaterializeArgs += "--overwrite"
    }

    Invoke-NativeLogged -LogPath $ChunkLog -CommandArgs $MaterializeArgs
}

$OutputFiles = (Get-ChildItem -LiteralPath $OutputRoot -Recurse -Filter "*_split_normalized.parquet" -File).Count

$FinalSummary = [ordered]@{
    finished_at = (Get-Date).ToString("o")
    mode = $Mode
    run_root = $RunRoot
    manifest = $Manifest
    manifest_rows = $ManifestRows
    chunk_count = $Chunks.Count
    output_root = $OutputRoot
    output_files = $OutputFiles
    audit_run = $false
}

if ($RunAudit) {
    $AuditRoot = Join-Path $RunRoot "full_universe_split_event_audit"
    New-Item -ItemType Directory -Force -Path $AuditRoot | Out-Null
    $AuditLog = Join-Path $RunRoot "audit_full_universe_split.log"
    $AuditArgs = @(
        $AuditScript,
        "--minute-root", $MinuteRoot,
        "--splits-root", $SplitsRoot,
        "--output-root", $AuditRoot
    )

    Invoke-NativeLogged -LogPath $AuditLog -CommandArgs $AuditArgs
    $FinalSummary["audit_run"] = $true
    $FinalSummary["audit_root"] = $AuditRoot
}

$FinalSummary | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $RunSummaryPath -Encoding UTF8

Write-Host ""
Write-Host "Completed."
Write-Host ("Run root: {0}" -f $RunRoot)
Write-Host ("Manifest rows: {0}" -f $ManifestRows)
Write-Host ("Chunks: {0}" -f $Chunks.Count)
Write-Host ("Output root: {0}" -f $OutputRoot)
Write-Host ("Output files now present: {0}" -f $OutputFiles)
Write-Host ("Summary: {0}" -f $RunSummaryPath)
