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
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    $stream = $null
    $reader = $null
    try {
        $share = [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete
        $stream = [System.IO.FileStream]::new(
            $Path,
            [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::Read,
            $share
        )
        $reader = [System.IO.StreamReader]::new($stream)
        return $reader.ReadToEnd() | ConvertFrom-Json
    }
    catch {
        return $null
    }
    finally {
        if ($null -ne $reader) { $reader.Dispose() }
        elseif ($null -ne $stream) { $stream.Dispose() }
    }
}

function Is-Alive {
    param([object]$ProcessId)
    if ($null -eq $ProcessId) { return $false }
    try {
        $process = Get-Process -Id ([int]$ProcessId) -ErrorAction Stop
        return (-not $process.HasExited)
    }
    catch { return $false }
}

function Optional {
    param([object]$Value)
    if ($null -eq $Value -or [string]::IsNullOrWhiteSpace([string]$Value)) {
        return "n/a"
    }
    return [string]$Value
}

function Snapshot {
    $heartbeatPath = Join-Path $RunRoot "heartbeat_latest.json"
    $pidPath = Join-Path $RunRoot "pid_manifest.json"
    $finalPath = Join-Path $RunRoot "final_manifest.json"
    $heartbeat = Read-SharedJson -Path $heartbeatPath
    $pidManifest = Read-SharedJson -Path $pidPath
    $final = Read-SharedJson -Path $finalPath
    $wrapperPid = $null
    if ($null -ne $heartbeat -and $null -ne $heartbeat.wrapper_pid) {
        $wrapperPid = [int]$heartbeat.wrapper_pid
    }
    elseif ($null -ne $pidManifest -and $null -ne $pidManifest.wrapper_pid) {
        $wrapperPid = [int]$pidManifest.wrapper_pid
    }
    $age = $null
    if ($null -ne $heartbeat -and $null -ne $heartbeat.observed_at_utc) {
        try {
            $observed = [datetime]::Parse([string]$heartbeat.observed_at_utc).ToUniversalTime()
            $age = [Math]::Round(((Get-Date).ToUniversalTime() - $observed).TotalSeconds, 2)
        }
        catch { $age = $null }
    }
    return [ordered]@{
        heartbeat = $heartbeat
        final = $final
        wrapper_pid = $wrapperPid
        wrapper_alive = Is-Alive -ProcessId $wrapperPid
        heartbeat_age = $age
    }
}

function Write-Compact {
    param([object]$State)
    $now = (Get-Date).ToString("s")
    $h = $State.heartbeat
    if ($null -eq $h) {
        Write-Host ("[{0}] status=WAITING stage=NO_HEARTBEAT wrapper_alive={1} progress=unknown" -f $now, $State.wrapper_alive)
        return
    }
    $status = [string]$h.status
    if ($status -eq "running" -and -not $State.wrapper_alive -and $null -ne $State.heartbeat_age -and [double]$State.heartbeat_age -gt 180) {
        $status = "stale_no_process"
    }
    Write-Host ("[{0}] status={1} stage={2} wrapper_alive={3} latest_age_sec={4} elapsed_sec={5} progress={6}/{7} item={8} verified_partitions={9} failed_partitions={10} cpu={11} io_read_Bps={12} io_write_Bps={13} output_free_GB={14}" -f `
        $now,
        $status.ToUpperInvariant(),
        (Optional $h.stage),
        $State.wrapper_alive,
        (Optional $State.heartbeat_age),
        (Optional $h.elapsed_seconds),
        (Optional $h.current_index),
        (Optional $h.total_count),
        (Optional $h.current_item),
        (Optional $h.verified_partitions),
        (Optional $h.failed_partitions),
        (Optional $h.process_cpu_pct),
        (Optional $h.io_read_bytes_per_sec),
        (Optional $h.io_write_bytes_per_sec),
        (Optional $h.output_drive_free_gb)
    )
}

function Write-Full {
    param([object]$State)
    Clear-Host
    Write-Host "TSIS Trading Activity Stage-8 target-only recovery monitor"
    Write-Host ("RunRoot: {0}" -f $RunRoot)
    Write-Host ("Observed: {0}" -f (Get-Date).ToString("o"))
    Write-Host ("Wrapper PID: {0} alive={1}" -f (Optional $State.wrapper_pid), $State.wrapper_alive)
    Write-Host ("Heartbeat age seconds: {0}" -f (Optional $State.heartbeat_age))
    Write-Host ""
    if ($null -eq $State.heartbeat) {
        Write-Host "No heartbeat yet."
    }
    else {
        $State.heartbeat | ConvertTo-Json -Depth 8
    }
    if ($null -ne $State.final) {
        Write-Host ""
        Write-Host "Final manifest:"
        $State.final | ConvertTo-Json -Depth 10
    }
}

$terminal = @("completed", "failed", "interrupted", "stopped_low_disk", "stopped")
do {
    if (-not (Test-Path -LiteralPath $RunRoot -PathType Container)) {
        Write-Host ("[{0}] status=WAITING run_root_missing=True run_root={1}" -f (Get-Date).ToString("s"), $RunRoot)
        $state = $null
    }
    else {
        $state = Snapshot
        if ($Compact) { Write-Compact -State $state }
        else { Write-Full -State $state }
    }
    $done = $false
    if ($null -ne $state -and $null -ne $state.heartbeat) {
        $done = $terminal -contains ([string]$state.heartbeat.status).ToLowerInvariant()
    }
    if ($Watch -and -not $done) {
        Start-Sleep -Seconds $IntervalSeconds
    }
} while ($Watch -and -not $done)
