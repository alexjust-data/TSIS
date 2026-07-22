param(
    [Parameter(Mandatory=$true)]
    [string]$RunRoot,
    [int]$Top = 20,
    [int]$IntervalSeconds = 30,
    [switch]$Watch
)

$ErrorActionPreference = "Stop"

function Read-JsonFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }
    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Show-Status {
    param([string]$Root)

    Clear-Host
    Write-Host "TSIS quote-guarded v0_2 monitor"
    Write-Host ("Run root: {0}" -f $Root)
    Write-Host ("Observed: {0}" -f (Get-Date).ToString("o"))
    Write-Host ""

    $runConfig = Read-JsonFile -Path (Join-Path $Root "run_config.json")
    $runnerConfig = Read-JsonFile -Path (Join-Path $Root "runner_config.json")
    if ($runConfig -ne $null) {
        Write-Host ("Planned tickers: {0} | workers: {1} | years: {2}-{3}" -f $runConfig.tickers_planned, $runConfig.workers, $runConfig.min_year, $runConfig.max_year)
    } elseif ($runnerConfig -ne $null) {
        Write-Host ("Runner created: {0} | workers: {1}" -f $runnerConfig.created_at, $runnerConfig.workers)
    } else {
        Write-Host "No run_config.json yet."
    }

    $statusDir = Join-Path $Root "ticker_status"
    $monthDir = Join-Path $Root "month_summaries"
    $shardDir = Join-Path $Root "repair_shards"
    $statuses = @()
    if (Test-Path -LiteralPath $statusDir) {
        $statuses = @(Get-ChildItem -LiteralPath $statusDir -Filter *.json -File | ForEach-Object {
            $obj = Read-JsonFile -Path $_.FullName
            if ($obj -ne $null) { $obj }
        })
    }

    $statusGroups = $statuses | Group-Object status | Sort-Object Name
    Write-Host ""
    Write-Host "Ticker status:"
    if ($statusGroups.Count -eq 0) {
        Write-Host "  none"
    } else {
        $statusGroups | ForEach-Object { Write-Host ("  {0}: {1}" -f $_.Name, $_.Count) }
    }

    $monthsDone = ($statuses | Measure-Object -Property months_done -Sum).Sum
    $monthsPlanned = ($statuses | Measure-Object -Property months_planned -Sum).Sum
    $repairRows = ($statuses | Measure-Object -Property repair_rows -Sum).Sum
    $ohlcRows = ($statuses | Measure-Object -Property ohlc_repair_rows -Sum).Sum
    $vwRows = ($statuses | Measure-Object -Property vw_invalid_rows -Sum).Sum
    $monthSummaryCount = @(Get-ChildItem -LiteralPath $monthDir -Filter *.json -File -ErrorAction SilentlyContinue).Count
    $shardCount = @(Get-ChildItem -LiteralPath $shardDir -Filter *.parquet -File -ErrorAction SilentlyContinue).Count

    Write-Host ""
    Write-Host ("Months done/planned in started tickers: {0}/{1}" -f $monthsDone, $monthsPlanned)
    Write-Host ("Month summaries: {0}" -f $monthSummaryCount)
    Write-Host ("Repair shards: {0}" -f $shardCount)
    Write-Host ("Repair rows: {0} | OHLC rows: {1} | VW invalid rows: {2}" -f $repairRows, $ohlcRows, $vwRows)

    Write-Host ""
    Write-Host "Active / latest tickers:"
    $statuses |
        Sort-Object last_heartbeat_utc -Descending |
        Select-Object -First $Top ticker,status,months_done,months_planned,current_year,current_month,repair_rows,ohlc_repair_rows,vw_invalid_rows,last_heartbeat_utc |
        Format-Table -AutoSize

    $summaryPath = Join-Path $Root "repair_summary.json"
    if (Test-Path -LiteralPath $summaryPath) {
        Write-Host ""
        Write-Host "Final summary exists:"
        Write-Host $summaryPath
    }
}

do {
    Show-Status -Root $RunRoot
    if ($Watch) {
        Start-Sleep -Seconds $IntervalSeconds
    }
} while ($Watch)
