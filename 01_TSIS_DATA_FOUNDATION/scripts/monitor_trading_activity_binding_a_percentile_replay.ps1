param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,
    [int]$IntervalSeconds = 10,
    [switch]$Compact,
    [switch]$Watch
)

$ErrorActionPreference = "Stop"

function Read-SharedJson {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    $stream = $null; $reader = $null
    try {
        $share = [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete
        $stream = [System.IO.FileStream]::new($Path,[System.IO.FileMode]::Open,[System.IO.FileAccess]::Read,$share)
        $reader = [System.IO.StreamReader]::new($stream)
        return $reader.ReadToEnd() | ConvertFrom-Json
    }
    catch { return $null }
    finally {
        if ($null -ne $reader) { $reader.Dispose() }
        elseif ($null -ne $stream) { $stream.Dispose() }
    }
}

function Is-Alive {
    param([object]$ProcessId)
    if ($null -eq $ProcessId) { return $false }
    try { $p = Get-Process -Id ([int]$ProcessId) -ErrorAction Stop; return (-not $p.HasExited) }
    catch { return $false }
}

function Optional {
    param([object]$Value)
    if ($null -eq $Value -or [string]::IsNullOrWhiteSpace([string]$Value)) { return "n/a" }
    return [string]$Value
}

function Snapshot {
    $heartbeat = Read-SharedJson -Path (Join-Path $RunRoot "heartbeat_latest.json")
    $pidManifest = Read-SharedJson -Path (Join-Path $RunRoot "pid_manifest.json")
    $final = Read-SharedJson -Path (Join-Path $RunRoot "final_manifest.json")
    $wrapperPid = if ($null -ne $heartbeat -and $null -ne $heartbeat.wrapper_pid) { [int]$heartbeat.wrapper_pid } elseif ($null -ne $pidManifest) { [int]$pidManifest.wrapper_pid } else { $null }
    $age = $null
    if ($null -ne $heartbeat -and $null -ne $heartbeat.observed_at_utc) {
        try { $age = [Math]::Round(((Get-Date).ToUniversalTime() - [datetime]::Parse([string]$heartbeat.observed_at_utc).ToUniversalTime()).TotalSeconds, 2) } catch { $age = $null }
    }
    return [ordered]@{ heartbeat=$heartbeat; final=$final; wrapper_pid=$wrapperPid; wrapper_alive=(Is-Alive $wrapperPid); heartbeat_age=$age }
}

function Write-Compact {
    param([object]$State)
    $now = (Get-Date).ToString("s"); $h = $State.heartbeat
    if ($null -eq $h) { Write-Host ("[{0}] status=WAITING stage=NO_HEARTBEAT wrapper_alive={1} progress=unknown" -f $now,$State.wrapper_alive); return }
    $status = [string]$h.status
    if ($status -eq "running" -and -not $State.wrapper_alive -and $null -ne $State.heartbeat_age -and [double]$State.heartbeat_age -gt 180) { $status = "stale_no_process" }
    Write-Host ("[{0}] status={1} stage={2} wrapper_alive={3} latest_age_sec={4} elapsed_sec={5} blocks={6}/{7} sessions={8}/{9} shard={10} session={11} item={12} rows={13} percentile_cells={14} mismatches={15} cpu={16} rss_GiB={17} ram_free_GiB={18} io_read_Bps={19} io_write_Bps={20} output_free_GB={21}" -f `
        $now,$status.ToUpperInvariant(),(Optional $h.stage),$State.wrapper_alive,(Optional $State.heartbeat_age),(Optional $h.elapsed_seconds),
        (Optional $h.blocks_completed),(Optional $h.blocks_total),(Optional $h.sessions_completed),(Optional $h.sessions_total),
        (Optional $h.current_shard),(Optional $h.current_session),(Optional $h.current_item),(Optional $h.rows_checked),
        (Optional $h.percentile_cells_checked),(Optional $h.mismatch_count),(Optional $h.process_cpu_pct),
        (Optional $h.process_tree_rss_gib),(Optional $h.available_memory_gib),(Optional $h.io_read_bytes_per_sec),
        (Optional $h.io_write_bytes_per_sec),(Optional $h.output_drive_free_gb))
}

function Write-Full {
    param([object]$State)
    Clear-Host
    Write-Host "TSIS Trading Activity independent percentile replay monitor"
    Write-Host ("RunRoot: {0}" -f $RunRoot)
    Write-Host ("Observed: {0}" -f (Get-Date).ToString("o"))
    Write-Host ("Wrapper PID: {0} alive={1}" -f (Optional $State.wrapper_pid),$State.wrapper_alive)
    Write-Host ("Heartbeat age seconds: {0}" -f (Optional $State.heartbeat_age))
    if ($null -eq $State.heartbeat) { Write-Host "No heartbeat yet." } else { $State.heartbeat | ConvertTo-Json -Depth 8 }
    if ($null -ne $State.final) { Write-Host "Final manifest:"; $State.final | ConvertTo-Json -Depth 10 }
}

$terminal = @("completed","failed","interrupted","stopped")
do {
    if (-not (Test-Path -LiteralPath $RunRoot -PathType Container)) {
        Write-Host ("[{0}] status=WAITING run_root_missing=True run_root={1}" -f (Get-Date).ToString("s"),$RunRoot); $state=$null
    }
    else { $state=Snapshot; if ($Compact) { Write-Compact $state } else { Write-Full $state } }
    $done=$false
    if ($null -ne $state -and $null -ne $state.heartbeat) { $done=$terminal -contains ([string]$state.heartbeat.status).ToLowerInvariant() }
    if ($Watch -and -not $done) { Start-Sleep -Seconds $IntervalSeconds }
} while ($Watch -and -not $done)

