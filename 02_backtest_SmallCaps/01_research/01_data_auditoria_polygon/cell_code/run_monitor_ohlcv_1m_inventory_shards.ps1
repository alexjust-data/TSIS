param(
    [string]$BaseDir = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory",
    [string]$Pattern = "ohlcv_1m_inventory_shard_*_of_*",
    [double]$IntervalSec = 5.0
)

function Read-JsonFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }
    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

while ($true) {
    Clear-Host

    $dirs = Get-ChildItem -Path $BaseDir -Directory -Filter $Pattern -ErrorAction SilentlyContinue | Sort-Object Name
    $rows = @()

    foreach ($d in $dirs) {
        $checkpointPath = Join-Path $d.FullName "inventory_checkpoint.json"
        $manifestPath = Join-Path $d.FullName "inventory_run_manifest.json"
        $summaryPath = Join-Path $d.FullName "ohlcv_1m_inventory_summary.json"

        $checkpoint = Read-JsonFile -Path $checkpointPath
        $manifest = Read-JsonFile -Path $manifestPath
        $summary = Read-JsonFile -Path $summaryPath

        $status = "missing"
        if ($summary) {
            $status = "finalized"
        }
        elseif ($checkpoint -and $checkpoint.active_root) {
            $status = "running"
        }
        elseif ($checkpoint) {
            $status = "idle"
        }

        $rows += [pscustomobject]@{
            run_dir             = $d.Name
            updated_utc         = if ($checkpoint) { $checkpoint.updated_utc } else { $null }
            persisted_rows_total= if ($checkpoint) { [int64]$checkpoint.persisted_rows_total } else { $null }
            batches_written     = if ($checkpoint) { [int64]$checkpoint.batches_written } else { $null }
            next_batch_index    = if ($checkpoint) { [int64]$checkpoint.next_batch_index } else { $null }
            active_root         = if ($checkpoint) { $checkpoint.active_root } else { $null }
            last_relpath        = if ($checkpoint) { $checkpoint.last_relpath_persisted } else { $null }
            finalized           = if ($manifest) { [bool]$manifest.finalized } else { $null }
            final_rows          = if ($summary) { [int64]$summary.all_rows } else { $null }
            final_tickers       = if ($summary) { [int64]$summary.all_tickers } else { $null }
            status              = $status
        }
    }

    if ($rows.Count -eq 0) {
        Write-Host "No shard run_dirs found."
        Write-Host "base_dir=$BaseDir"
        Write-Host "pattern=$Pattern"
        Start-Sleep -Seconds $IntervalSec
        continue
    }

    Write-Host "base_dir=$BaseDir"
    Write-Host "pattern=$Pattern"
    Write-Host "run_dirs=$($rows.Count)"
    Write-Host "interval_sec=$IntervalSec"
    Write-Host ""

    $rows | Format-Table -AutoSize

    $persistedTotal = ($rows | Measure-Object -Property persisted_rows_total -Sum).Sum
    $finalRowsTotal = ($rows | Measure-Object -Property final_rows -Sum).Sum
    $finalizedCount = ($rows | Where-Object { $_.status -eq "finalized" }).Count
    $runningCount = ($rows | Where-Object { $_.status -eq "running" }).Count

    Write-Host ""
    Write-Host "TOTAL"
    Write-Host ("persisted_rows_total={0} | final_rows={1} | finalized={2}/{3} | running={4}" -f $persistedTotal, $finalRowsTotal, $finalizedCount, $rows.Count, $runningCount)

    Start-Sleep -Seconds $IntervalSec
}
