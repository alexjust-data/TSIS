param(
    [Parameter(Mandatory=$true)]
    [string]$ConsolidationRunRoot,
    [string]$OutputRoot = "E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded",
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
        return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Format-Size {
    param([Nullable[Int64]]$Bytes)
    if ($null -eq $Bytes) {
        return ""
    }
    if ($Bytes -ge 1TB) {
        return ("{0:N2} TB" -f ($Bytes / 1TB))
    }
    if ($Bytes -ge 1GB) {
        return ("{0:N2} GB" -f ($Bytes / 1GB))
    }
    if ($Bytes -ge 1MB) {
        return ("{0:N2} MB" -f ($Bytes / 1MB))
    }
    return ("{0} B" -f $Bytes)
}

function Show-Status {
    param([string]$Root)

    Clear-Host
    $now = Get-Date
    Write-Host "TSIS quote-guarded LT1B consolidation monitor"
    Write-Host ("Run root: {0}" -f $Root)
    Write-Host ("Observed: {0}" -f $now.ToString("o"))
    Write-Host ""

    $statusPath = Join-Path $Root "consolidation_status.json"
    $summaryPath = Join-Path $Root "consolidation_summary.json"
    $completionCsv = Join-Path $Root "lt1b_ticker_completion.csv"
    $shardIndexCsv = Join-Path $Root "lt1b_repair_shard_index.csv"
    $logPath = Join-Path $Root "consolidation.log"

    $summary = Read-JsonFile -Path $summaryPath
    $status = Read-JsonFile -Path $statusPath

    if ($summary -ne $null) {
        Write-Host ("Final status: {0}" -f $summary.status)
        Write-Host ("Universe tickers: {0}" -f $summary.universe_tickers)
        Write-Host ("Completed tickers: {0}" -f $summary.completed_tickers)
        Write-Host ("Missing tickers: {0}" -f $summary.missing_tickers)
        Write-Host ("Selected shards: {0}" -f $summary.selected_repair_shards)
        Write-Host ("Out-of-scope shards skipped: {0}" -f $summary.skipped_out_scope_shards)
        Write-Host ("Malformed shard names: {0}" -f $summary.malformed_shard_names)
        Write-Host ("Manifest rows: {0}" -f $summary.manifest_rows)
        Write-Host ("Manifest: {0}" -f $summary.manifest_path)
        Write-Host ("Promoted manifest: {0}" -f $summary.promoted_manifest)
        Write-Host ""
    } elseif ($status -ne $null) {
        $pct = 0
        if ([double]$status.shards_total -gt 0) {
            $pct = [math]::Round(([double]$status.shards_done / [double]$status.shards_total) * 100, 2)
        }
        Write-Host ("Stage: {0}" -f $status.stage)
        Write-Host ("Shards: {0}/{1} ({2}%)" -f $status.shards_done, $status.shards_total, $pct)
        Write-Host ("Rows written: {0}" -f $status.rows_written)
        Write-Host ("Rows/sec: {0}" -f $status.rows_per_sec)
        Write-Host ("Current shard: {0}" -f $status.current_shard)
        Write-Host ("Manifest: {0}" -f $status.manifest_path)
        Write-Host ""
    } else {
        Write-Host "No consolidation_status.json or consolidation_summary.json yet."
        Write-Host "If the consolidator has just started, wait for the first progress checkpoint."
        Write-Host ""
    }

    foreach ($path in @($completionCsv, $shardIndexCsv, $logPath)) {
        if (Test-Path -LiteralPath $path) {
            $item = Get-Item -LiteralPath $path
            Write-Host ("{0}: {1} | {2}" -f $item.Name, (Format-Size $item.Length), $item.LastWriteTime.ToString("s"))
        }
    }

    $promoted = Join-Path $OutputRoot "repair_manifest_lt1b_v0_1.parquet"
    if (Test-Path -LiteralPath $promoted) {
        $item = Get-Item -LiteralPath $promoted
        Write-Host ("promoted repair_manifest_lt1b_v0_1.parquet: {0} | {1}" -f (Format-Size $item.Length), $item.LastWriteTime.ToString("s"))
    }

    try {
        $drive = Get-PSDrive -Name E -ErrorAction Stop
        Write-Host ("E: free: {0}" -f (Format-Size $drive.Free))
    } catch {
        Write-Host "E: free: unavailable"
    }

    Write-Host ""
    if ($summary -ne $null) {
        Write-Host "Consolidation summary exists. Monitor can be stopped."
    } else {
        Write-Host ("Next refresh in {0}s. Ctrl+C to stop." -f $IntervalSeconds)
    }
}

if (-not (Test-Path -LiteralPath $ConsolidationRunRoot)) {
    New-Item -ItemType Directory -Force -Path $ConsolidationRunRoot | Out-Null
}

do {
    Show-Status -Root $ConsolidationRunRoot
    if (-not $Watch) {
        break
    }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)
