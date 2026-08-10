[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RuntimeRoot,

    [switch]$Compact,
    [switch]$Once,
    [switch]$RequestStop,
    [int]$IntervalSeconds = 30,
    [int]$StaleAfterSeconds = 180
)

$ErrorActionPreference = "Stop"
$runtime = [System.IO.Path]::GetFullPath($RuntimeRoot)
if (-not (Test-Path -LiteralPath $runtime)) {
    throw "Runtime root does not exist: $runtime"
}

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

function Test-ProcessAlive {
    param($PidValue)
    if ($null -eq $PidValue) {
        return $false
    }
    try {
        $null = Get-Process -Id ([int]$PidValue) -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

function Get-FreeGiB {
    param($PreManifest)
    if ($null -eq $PreManifest -or [string]::IsNullOrWhiteSpace($PreManifest.output_run_root)) {
        return $null
    }
    try {
        $root = [System.IO.Path]::GetPathRoot([string]$PreManifest.output_run_root)
        $drive = Get-PSDrive -Name $root.Substring(0, 1) -ErrorAction Stop
        return [math]::Round($drive.Free / 1GB, 2)
    }
    catch {
        return $null
    }
}

if ($RequestStop) {
    $requestPath = Join-Path $runtime "stop_requested.json"
    $temporary = Join-Path $runtime (".stop_requested.{0}.{1}.tmp" -f $PID, [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())
    $payload = [ordered]@{
        requested_at_utc = [DateTime]::UtcNow.ToString("o")
        requested_by_pid = $PID
        request = "COOPERATIVE_STOP"
    } | ConvertTo-Json
    [System.IO.File]::WriteAllText($temporary, $payload + [Environment]::NewLine)
    [System.IO.File]::Move($temporary, $requestPath, $true)
    Write-Output "Cooperative stop requested: $requestPath"
    exit 0
}

do {
    $heartbeat = Read-JsonFile (Join-Path $runtime "heartbeat_latest.json")
    $pidManifest = Read-JsonFile (Join-Path $runtime "pid_manifest.json")
    $final = Read-JsonFile (Join-Path $runtime "final_manifest.json")
    $preManifest = Read-JsonFile (Join-Path $runtime "pre_manifest.json")
    $alive = Test-ProcessAlive $pidManifest.pid
    $now = [DateTime]::UtcNow
    $heartbeatTime = $null
    if ($null -ne $heartbeat -and $null -ne $heartbeat.timestamp_utc) {
        try {
            $heartbeatTime = [DateTimeOffset]::Parse([string]$heartbeat.timestamp_utc).UtcDateTime
        }
        catch {
            $heartbeatTime = $null
        }
    }
    $age = if ($null -ne $heartbeatTime) { ($now - $heartbeatTime).TotalSeconds } else { [double]::PositiveInfinity }
    $derivedStatus = if ($null -ne $final) {
        [string]$final.status
    }
    elseif (($age -gt $StaleAfterSeconds) -and (-not $alive)) {
        "STALE_NO_PROCESS"
    }
    elseif ($null -ne $heartbeat) {
        [string]$heartbeat.status
    }
    else {
        "NO_HEARTBEAT"
    }

    $counters = if ($null -ne $heartbeat) { $heartbeat.counters } else { $null }
    $sessionsDone = if ($null -ne $counters.current_state_sessions) { [int64]$counters.current_state_sessions } elseif ($null -ne $counters.sessions_audited) { [int64]$counters.sessions_audited } else { 0 }
    $sessionsTotal = if ($null -ne $counters.sessions_total) { [int64]$counters.sessions_total } else { 0 }
    $rows = 0
    foreach ($name in @("current_state_rows", "multiscale_rows", "baseline_rows")) {
        if ($null -ne $counters.$name) {
            $rows += [int64]$counters.$name
        }
    }
    $partitions = if ($null -ne $counters.partitions_written) { [int64]$counters.partitions_written } else { 0 }
    $timestamp = $now.ToString("o")
    $stage = if ($null -ne $heartbeat) { [string]$heartbeat.stage } else { "UNKNOWN" }
    $session = if ($null -ne $heartbeat -and $null -ne $heartbeat.current_session) { [string]$heartbeat.current_session } else { "-" }
    $freeGiB = Get-FreeGiB $preManifest

    if ($Compact) {
        Write-Output ("[{0}] status={1} stage={2} wrapper_alive={3} progress={4}/{5} session={6} rows={7} partitions={8} output_free_GB={9}" -f $timestamp, $derivedStatus, $stage, $alive.ToString().ToLowerInvariant(), $sessionsDone, $sessionsTotal, $session, $rows, $partitions, $freeGiB)
    }
    else {
        [pscustomobject]@{
            timestamp_utc = $timestamp
            status = $derivedStatus
            stage = $stage
            wrapper_alive = $alive
            heartbeat_age_seconds = if ([double]::IsInfinity($age)) { $null } else { [math]::Round($age, 1) }
            current_session = $session
            sessions_done = $sessionsDone
            sessions_total = $sessionsTotal
            rows = $rows
            partitions = $partitions
            output_free_GB = $freeGiB
            runtime_root = $runtime
        } | Format-List
    }

    if ($Once -or $null -ne $final -or $derivedStatus -eq "STALE_NO_PROCESS") {
        break
    }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)

if ($derivedStatus -eq "STALE_NO_PROCESS") {
    exit 3
}
if ($null -ne $final -and $final.status -eq "FAILED") {
    exit 1
}
exit 0
