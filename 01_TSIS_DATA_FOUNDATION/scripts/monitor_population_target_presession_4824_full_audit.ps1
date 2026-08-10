param(
    [Parameter(Mandatory = $true)]
    [string]$RuntimeRoot,
    [switch]$Compact,
    [int]$IntervalSeconds = 5
)

$heartbeatPath = Join-Path $RuntimeRoot 'heartbeat_latest.json'
$pidManifestPath = Join-Path $RuntimeRoot 'pid_manifest.json'
$finalManifestPath = Join-Path $RuntimeRoot 'final_manifest.json'

while ($true) {
    $now = [datetime]::UtcNow
    $heartbeat = if (Test-Path -LiteralPath $heartbeatPath) {
        Get-Content -LiteralPath $heartbeatPath -Raw | ConvertFrom-Json
    } else { $null }
    $pidManifest = if (Test-Path -LiteralPath $pidManifestPath) {
        Get-Content -LiteralPath $pidManifestPath -Raw | ConvertFrom-Json
    } else { $null }
    $finalManifest = if (Test-Path -LiteralPath $finalManifestPath) {
        Get-Content -LiteralPath $finalManifestPath -Raw | ConvertFrom-Json
    } else { $null }

    $childAlive = $false
    if ($pidManifest -and $pidManifest.child_pid) {
        $childAlive = [bool](Get-Process -Id $pidManifest.child_pid -ErrorAction SilentlyContinue)
    }
    $wrapperAlive = $false
    if ($pidManifest -and $pidManifest.wrapper_pid) {
        $wrapperAlive = [bool](Get-Process -Id $pidManifest.wrapper_pid -ErrorAction SilentlyContinue)
    }
    $latestAge = if ($heartbeat) {
        [math]::Round(($now - [datetime]::Parse($heartbeat.observed_at_utc).ToUniversalTime()).TotalSeconds, 1)
    } else { $null }
    $status = if ($finalManifest) {
        $finalManifest.final_status
    } elseif (-not $heartbeat) {
        'WAITING_FOR_HEARTBEAT'
    } elseif ($heartbeat.status -eq 'running' -and $latestAge -gt (3 * $IntervalSeconds) -and -not $childAlive -and -not $wrapperAlive) {
        'STALE_NO_PROCESS'
    } else {
        $heartbeat.status.ToUpperInvariant()
    }

    if ($Compact) {
        $timestamp = $now.ToString('o')
        $stage = if ($heartbeat) { $heartbeat.stage } else { 'UNKNOWN' }
        $elapsed = if ($heartbeat) { $heartbeat.elapsed_seconds } else { 0 }
        $free = if ($heartbeat) { $heartbeat.output_free_gb } else { 'unknown' }
        Write-Output "[$timestamp] status=$status stage=$stage wrapper_alive=$($wrapperAlive.ToString().ToLowerInvariant()) child_alive=$($childAlive.ToString().ToLowerInvariant()) latest_age_sec=$latestAge elapsed_sec=$elapsed progress=unknown reason=single_read_only_audit output_free_GB=$free"
    } else {
        [PSCustomObject]@{
            status = $status
            heartbeat = $heartbeat
            wrapper_alive = $wrapperAlive
            child_alive = $childAlive
            latest_age_seconds = $latestAge
            final_manifest = $finalManifest
        } | Format-List
    }

    if ($finalManifest) { break }
    Start-Sleep -Seconds $IntervalSeconds
}
