param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,
    [int]$IntervalSeconds = 10,
    [int]$StaleAfterSeconds = 120,
    [switch]$Compact,
    [switch]$Watch
)

$ErrorActionPreference = "Stop"
$TerminalStatuses = @("COMPLETE", "FAILED", "INTERRUPTED", "STOPPED_LOW_DISK")

function Read-SharedJson {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try {
        $stream = [System.IO.FileStream]::new(
            $Path,
            [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::Read,
            [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete
        )
        try {
            $reader = [System.IO.StreamReader]::new($stream)
            try { return ($reader.ReadToEnd() | ConvertFrom-Json) }
            finally { $reader.Dispose() }
        }
        finally { $stream.Dispose() }
    }
    catch { return $null }
}

function Fmt {
    param($Value, [int]$Digits = 2)
    if ($null -eq $Value -or [string]::IsNullOrWhiteSpace([string]$Value)) { return "n/a" }
    if ($Value -is [double] -or $Value -is [single] -or $Value -is [decimal]) {
        return ([Math]::Round([double]$Value, $Digits)).ToString(
            [System.Globalization.CultureInfo]::InvariantCulture
        )
    }
    return [string]$Value
}

function Write-Status {
    $heartbeatPath = Join-Path $RunRoot "heartbeat_latest.json"
    $finalPath = Join-Path $RunRoot "final_manifest.json"
    $heartbeat = Read-SharedJson -Path $heartbeatPath
    $final = Read-SharedJson -Path $finalPath
    if ($null -eq $heartbeat) {
        $status = if ($null -ne $final) { [string]$final.status } else { "UNKNOWN" }
        Write-Host ("[{0}] status={1} stage=NO_HEARTBEAT progress=unknown reason=heartbeat_not_created" -f (Get-Date -Format "yyyy-MM-ddTHH:mm:ss"), $status)
        return ($status -in $TerminalStatuses)
    }

    $age = $null
    try {
        $age = ((Get-Date).ToUniversalTime() - [datetime]::Parse($heartbeat.observed_at_utc).ToUniversalTime()).TotalSeconds
    } catch { $age = $null }
    $wrapperAlive = $false
    if ($heartbeat.wrapper_pid -ne $null) {
        $wrapperAlive = $null -ne (Get-Process -Id ([int]$heartbeat.wrapper_pid) -ErrorAction SilentlyContinue)
    }
    $rawStatus = [string]$heartbeat.status
    $status = $rawStatus
    if ($null -ne $final -and ([string]$final.status) -in $TerminalStatuses) {
        $status = [string]$final.status
    }
    elseif ($rawStatus -eq "RUNNING" -and $null -ne $age -and $age -gt $StaleAfterSeconds -and -not $wrapperAlive) {
        $status = "stale_no_process"
    }
    $current = $heartbeat.current_index
    $total = $heartbeat.total_count
    $progress = if ($null -eq $total -or [int]$total -le 0) {
        "unknown reason=total_not_available"
    } else {
        "{0}/{1}" -f (Fmt $current 0), (Fmt $total 0)
    }
    $line = "[{0}] status={1} raw_status={2} stage={3} processes={4} wrapper_alive={5} latest_age_sec={6} elapsed_sec={7} progress={8} item={9} chains={10}/{11} pages_committed={12} pages_resumed={13} rows={14} retries={15} http_429={16} rate_rps={17} cpu={18} io_read_Bps={19} io_write_Bps={20} output_free_GiB={21}" -f `
        (Get-Date -Format "yyyy-MM-ddTHH:mm:ss"), $status, $rawStatus, (Fmt $heartbeat.stage), `
        (Fmt $heartbeat.process_tree_count 0), $wrapperAlive, (Fmt $age), `
        (Fmt $heartbeat.elapsed_seconds), $progress, (Fmt $heartbeat.current_item), `
        (Fmt $heartbeat.chains_completed 0), (Fmt $heartbeat.total_count 0), `
        (Fmt $heartbeat.pages_committed 0), (Fmt $heartbeat.pages_resumed 0), `
        (Fmt $heartbeat.rows_committed 0), (Fmt $heartbeat.retry_count 0), `
        (Fmt $heartbeat.http_429_count 0), (Fmt $heartbeat.current_requests_per_second), `
        (Fmt $heartbeat.process_cpu_core_percent), (Fmt $heartbeat.io_read_Bps), `
        (Fmt $heartbeat.io_write_Bps), (Fmt $heartbeat.output_free_gib)
    Write-Host $line
    return (($status -in $TerminalStatuses) -or $status -eq "stale_no_process")
}

$resolved = (Resolve-Path -LiteralPath $RunRoot).Path
do {
    $terminal = Write-Status
    if (-not $Watch -or $terminal) { break }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)
