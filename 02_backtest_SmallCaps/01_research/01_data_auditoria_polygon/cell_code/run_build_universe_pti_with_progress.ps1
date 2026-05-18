$python = "C:\TSIS_Data\02_backtest_SmallCaps\backtest\Scripts\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\scripts\build_universe_pti.py"
$outdir = "C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare"
$progress = Join-Path $outdir "build_universe_pti.progress.json"

$args = @(
    $script,
    "--start", "2005-01-01",
    "--end", "2026-12-31",
    "--outdir", $outdir,
    "--frequency", "daily",
    "--active-filter", "all",
    "--checkpoint-mode", "on",
    "--resume"
)

Write-Host "Launching build_universe_pti..."
Write-Host "python = $python"
Write-Host "script = $script"
Write-Host "outdir = $outdir"
Write-Host ""

$p = Start-Process -FilePath $python -ArgumentList $args -PassThru -WindowStyle Hidden

while (-not $p.HasExited) {
    Clear-Host
    Write-Host "build_universe_pti progress"
    Write-Host "PID=$($p.Id)"
    Write-Host "OUTDIR=$outdir"
    Write-Host ""

    if (Test-Path $progress) {
        try {
            $j = Get-Content $progress -Raw | ConvertFrom-Json

            Write-Host ("status={0}" -f $j.status)
            Write-Host ("snapshot_index={0}" -f $j.snapshot_index)
            Write-Host ("snapshot_total={0}" -f $j.snapshot_total)
            Write-Host ("progress_pct={0}" -f $j.progress_pct)
            Write-Host ("snapshot_date={0}" -f $j.snapshot_date)
            Write-Host ("successful_cuts={0}" -f $j.successful_cuts)
            Write-Host ("elapsed_sec={0}" -f $j.elapsed_sec)
            Write-Host ("eta_sec={0}" -f $j.eta_sec)
            Write-Host ("updated_at_utc={0}" -f $j.updated_at_utc)
            Write-Host ("error={0}" -f $j.error)

            $ckptDir = Join-Path $outdir "tickers_panel_pti_checkpoints"
            if (Test-Path $ckptDir) {
                $n = (Get-ChildItem $ckptDir -Recurse -Filter *.parquet -File -ErrorAction SilentlyContinue | Measure-Object).Count
                Write-Host ("checkpoint_parquets={0}" -f $n)
            }

            $partialQa = Join-Path $outdir "qa_coverage_by_cut.partial.csv"
            if (Test-Path $partialQa) {
                $lineCount = (Get-Content $partialQa | Measure-Object -Line).Lines
                Write-Host ("qa_partial_lines={0}" -f $lineCount)
            }
        }
        catch {
            Write-Host "progress file existe pero aun no parsea bien"
        }
    }
    else {
        Write-Host "progress file aun no existe"
    }

    Start-Sleep 5
    $p.Refresh()
}

Write-Host ""
Write-Host ("PROCESS EXITED WITH CODE {0}" -f $p.ExitCode)

if (Test-Path $progress) {
    Write-Host ""
    Write-Host "Final progress:"
    Get-Content $progress -Raw
}
