param(
    [string]$ProjectRoot = "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION",
    [string]$MinuteRoot = "E:\TSIS\data\ohlcv_1m",
    [string]$QuotesRoot = "D:\quotes",
    [string]$OutputRoot = "E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded",
    [string]$RunRoot = "",
    [int]$Workers = 0,
    [Nullable[int]]$MinYear = $null,
    [Nullable[int]]$MaxYear = $null,
    [string]$Tickers = "",
    [Nullable[int]]$MaxFiles = $null,
    [double]$BidQuantile = 0.01,
    [double]$AskQuantile = 0.99,
    [double]$TolerancePct = 0.003,
    [double]$AbsTolerance = 0.0001,
    [int]$MinQuoteCount = 3,
    [string]$SessionStart = "04:00",
    [string]$SessionEnd = "20:00",
    [Nullable[double]]$MaxSpreadPct = $null,
    [string]$PythonExe = "python",
    [switch]$SmokeOnly,
    [switch]$Overwrite,
    [switch]$NoPromoteManifest
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
Assert-PathExists -Path $QuotesRoot -Label "QuotesRoot"

$RepairScript = Join-Path $ProjectRoot "scripts\inspection\minute\build_ohlcv_1m_quote_guarded_repairs.py"
Assert-PathExists -Path $RepairScript -Label "quote-guarded repair script"

if ($Workers -le 0) {
    $Workers = [Math]::Max(1, [Environment]::ProcessorCount - 2)
}

if ([string]::IsNullOrWhiteSpace($RunRoot)) {
    $RunId = "quote_guarded_{0}" -f (Get-Date -Format "yyyyMMdd_HHmmss")
    $RunRoot = Join-Path $ProjectRoot "runs\data_foundation\ohlcv_1m_quote_guarded\$RunId"
}

if ($SmokeOnly -and $null -eq $MaxFiles) {
    $MaxFiles = 12
}

New-Item -ItemType Directory -Force -Path $RunRoot | Out-Null
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

$RunLog = Join-Path $RunRoot "quote_guarded_repair.log"

$Config = [ordered]@{
    created_at = (Get-Date).ToString("o")
    project_root = $ProjectRoot
    minute_root = $MinuteRoot
    quotes_root = $QuotesRoot
    output_root = $OutputRoot
    run_root = $RunRoot
    workers = $Workers
    min_year = $MinYear
    max_year = $MaxYear
    tickers = $Tickers
    max_files = $MaxFiles
    bid_quantile = $BidQuantile
    ask_quantile = $AskQuantile
    tolerance_pct = $TolerancePct
    abs_tolerance = $AbsTolerance
    min_quote_count = $MinQuoteCount
    session_start = $SessionStart
    session_end = $SessionEnd
    max_spread_pct = $MaxSpreadPct
    smoke_only = [bool]$SmokeOnly
    overwrite = [bool]$Overwrite
    promote_manifest = -not [bool]$NoPromoteManifest
}
$Config | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $RunRoot "runner_config.json") -Encoding UTF8

Write-Host "TSIS OHLCV 1m quote-guarded repair runner"
Write-Host "Minute root: $MinuteRoot"
Write-Host "Quotes root: $QuotesRoot"
Write-Host "Run root: $RunRoot"
Write-Host "Output root: $OutputRoot"
Write-Host "Workers: $Workers"
Write-Host ""

$Args = @(
    $RepairScript,
    "--minute-root", $MinuteRoot,
    "--quotes-root", $QuotesRoot,
    "--run-root", $RunRoot,
    "--output-root", $OutputRoot,
    "--workers", [string]$Workers,
    "--bid-quantile", [string]$BidQuantile,
    "--ask-quantile", [string]$AskQuantile,
    "--tolerance-pct", [string]$TolerancePct,
    "--abs-tolerance", [string]$AbsTolerance,
    "--min-quote-count", [string]$MinQuoteCount,
    "--session-start", $SessionStart,
    "--session-end", $SessionEnd
)

if ($null -ne $MinYear) {
    $Args += @("--min-year", [string]$MinYear)
}
if ($null -ne $MaxYear) {
    $Args += @("--max-year", [string]$MaxYear)
}
if (-not [string]::IsNullOrWhiteSpace($Tickers)) {
    $Args += @("--tickers", $Tickers)
}
if ($null -ne $MaxFiles) {
    $Args += @("--max-files", [string]$MaxFiles)
}
if ($null -ne $MaxSpreadPct) {
    $Args += @("--max-spread-pct", [string]$MaxSpreadPct)
}
if ($Overwrite) {
    $Args += "--overwrite"
}
if (-not $NoPromoteManifest) {
    $Args += "--promote-manifest"
}

Invoke-NativeLogged -LogPath $RunLog -CommandArgs $Args

$Summary = Join-Path $RunRoot "repair_summary.json"
Write-Host ""
Write-Host "Completed."
Write-Host ("Run root: {0}" -f $RunRoot)
Write-Host ("Log: {0}" -f $RunLog)
Write-Host ("Summary: {0}" -f $Summary)
if (-not $NoPromoteManifest) {
    Write-Host ("Promoted manifest: {0}" -f (Join-Path $OutputRoot "repair_manifest_v0_1.parquet"))
}
