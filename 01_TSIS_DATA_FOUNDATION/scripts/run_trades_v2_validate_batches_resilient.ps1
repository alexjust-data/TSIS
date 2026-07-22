param(
    [Parameter(Mandatory = $true)][string]$InventoryParquet,
    [Parameter(Mandatory = $true)][string]$Outdir,
    [Parameter(Mandatory = $true)][string]$RunId,
    [int]$Workers = 4,
    [int]$ChunkSize = 500,
    [string]$Root = "",
    [string]$Ticker = "",
    [string]$DateFrom = "",
    [string]$DateTo = "",
    [int]$Limit = 0,
    [string]$ScanReason = "rescan_all",
    [string]$ValidationKind = "normal_validation",
    [string]$OhlcvDailyRoot = "D:\ohlcv_daily",
    [string]$Ohlcv1mRoot = "D:\ohlcv_1m",
    [double]$DuplicateExcessWarnPct = 3.0,
    [double]$DuplicateExcessHardPct = 10.0,
    [double]$DailyRangeTolerancePct = 1.0,
    [double]$MinExpectedPrice = 0.0,
    [int]$RestartDelaySec = 20,
    [int]$MaxRestarts = 0,
    [switch]$Resume = $true
)

$ErrorActionPreference = "Stop"

$RepoRoot = "C:\TSIS_Data\02_backtest_SmallCaps"
$ScriptPath = Join-Path $RepoRoot "data_auditoria_polygon\cell_code\00_data_certification\052_trades_v2_validate_batches.py"
$CheckpointPath = Join-Path $Outdir "validation_checkpoint.json"
$SummaryPath = Join-Path $Outdir "validation_run_summary.json"
$SupervisorLog = Join-Path $Outdir "resilient_supervisor_log.csv"

function Read-JsonFile([string]$Path) {
    if (!(Test-Path $Path)) { return $null }
    try {
        return Get-Content -Raw -Path $Path | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Test-ValidationCompleted {
    $checkpoint = Read-JsonFile $CheckpointPath
    if ($null -ne $checkpoint -and [string]$checkpoint.status -eq "completed") {
        return $true
    }
    $summary = Read-JsonFile $SummaryPath
    if ($null -ne $summary) {
        return $true
    }
    return $false
}

function Write-SupervisorEvent([string]$Level, [string]$Message, [int]$Attempt, [int]$ExitCode) {
    $row = [pscustomobject]@{
        observed_at_local = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        observed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        run_id = $RunId
        outdir = $Outdir
        attempt = $Attempt
        exit_code = $ExitCode
        level = $Level
        message = $Message
    }
    $exists = Test-Path $SupervisorLog
    $row | Export-Csv -Path $SupervisorLog -Append -NoTypeInformation -Encoding UTF8
    if (-not $exists) {
        $tmp = Import-Csv $SupervisorLog
        $tmp | Export-Csv -Path $SupervisorLog -NoTypeInformation -Encoding UTF8
    }
}

function Build-PythonArgs {
    $args = @(
        $ScriptPath,
        "--inventory-parquet", $InventoryParquet,
        "--outdir", $Outdir,
        "--run-id", $RunId,
        "--workers", "$Workers",
        "--chunk-size", "$ChunkSize",
        "--scan-reason", $ScanReason,
        "--validation-kind", $ValidationKind,
        "--ohlcv-daily-root", $OhlcvDailyRoot,
        "--ohlcv-1m-root", $Ohlcv1mRoot,
        "--duplicate-excess-warn-pct", "$DuplicateExcessWarnPct",
        "--duplicate-excess-hard-pct", "$DuplicateExcessHardPct",
        "--daily-range-tolerance-pct", "$DailyRangeTolerancePct",
        "--min-expected-price", "$MinExpectedPrice"
    )
    if ($Resume) {
        $args += "--resume"
    }
    if ($Root.Trim()) {
        $args += @("--root", $Root)
    }
    if ($Ticker.Trim()) {
        $args += @("--ticker", $Ticker)
    }
    if ($DateFrom.Trim()) {
        $args += @("--date-from", $DateFrom)
    }
    if ($DateTo.Trim()) {
        $args += @("--date-to", $DateTo)
    }
    if ($Limit -gt 0) {
        $args += @("--limit", "$Limit")
    }
    return ,$args
}

New-Item -ItemType Directory -Force -Path $Outdir | Out-Null

if (Test-ValidationCompleted) {
    Write-Host "Validation already completed: $Outdir" -ForegroundColor Green
    exit 0
}

$attempt = 0
while ($true) {
    if (Test-ValidationCompleted) {
        Write-SupervisorEvent -Level "RUN_STATE" -Message "Validation already completed before launch" -Attempt $attempt -ExitCode 0
        Write-Host "Validation completed: $Outdir" -ForegroundColor Green
        break
    }

    $attempt += 1
    if ($MaxRestarts -gt 0 -and $attempt -gt $MaxRestarts) {
        Write-SupervisorEvent -Level "ALERT" -Message "Reached MaxRestarts=$MaxRestarts" -Attempt $attempt -ExitCode -1
        throw "Reached MaxRestarts=$MaxRestarts for $RunId"
    }

    $pyArgs = Build-PythonArgs
    Write-SupervisorEvent -Level "RUN_STATE" -Message "Launching validator" -Attempt $attempt -ExitCode 0
    Write-Host ""
    Write-Host "[$attempt] Launching $RunId" -ForegroundColor Cyan
    Write-Host ("python " + ($pyArgs -join " ")) -ForegroundColor DarkCyan

    & python @pyArgs
    $exitCode = $LASTEXITCODE

    if (Test-ValidationCompleted) {
        Write-SupervisorEvent -Level "RUN_STATE" -Message "Validation completed" -Attempt $attempt -ExitCode $exitCode
        Write-Host "Validation completed: $Outdir" -ForegroundColor Green
        break
    }

    if ($exitCode -eq 0) {
        Write-SupervisorEvent -Level "WARNING" -Message "Process exited 0 but validation is not marked completed; relaunching" -Attempt $attempt -ExitCode $exitCode
    } else {
        Write-SupervisorEvent -Level "WARNING" -Message "Process exited non-zero; relaunching after delay" -Attempt $attempt -ExitCode $exitCode
    }

    Write-Host "[$attempt] ExitCode=$exitCode. Sleeping $RestartDelaySec s before relaunch..." -ForegroundColor Yellow
    Start-Sleep -Seconds $RestartDelaySec
}
