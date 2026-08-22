param(
    [Parameter(Mandatory=$true)][string]$RunRoot,
    [switch]$Compact,
    [int]$IntervalSeconds = 30
)

while ($true) {
    $heartbeatPath = Join-Path $RunRoot 'heartbeat_latest.json'
    $finalPath = Join-Path $RunRoot 'final_manifest.json'
    if (Test-Path -LiteralPath $heartbeatPath) {
        $heartbeat = Get-Content -LiteralPath $heartbeatPath -Raw | ConvertFrom-Json
        $alive = $false
        if ($heartbeat.wrapper_pid) {
            $alive = $null -ne (Get-Process -Id $heartbeat.wrapper_pid -ErrorAction SilentlyContinue)
        }
        $status = [string]$heartbeat.status
        $observedUtc = [DateTimeOffset]::Parse(
            [string]$heartbeat.observed_at_utc,
            [System.Globalization.CultureInfo]::InvariantCulture
        ).UtcDateTime
        $age = [math]::Round(((Get-Date).ToUniversalTime() - $observedUtc).TotalSeconds, 1)
        if ($status -eq 'RUNNING' -and -not $alive -and $age -gt ($IntervalSeconds * 3) -and -not (Test-Path -LiteralPath $finalPath)) {
            $status = 'STALE_NO_PROCESS'
        }
        $line = "[{0}] status={1} stage={2} processes={3} wrapper_alive={4} latest_age_sec={5} elapsed_sec={6}" -f `
            (Get-Date).ToUniversalTime().ToString('s'), $status, $heartbeat.stage, `
            $heartbeat.process_tree_count, $alive.ToString().ToLower(), $age, `
            ([math]::Round([double]$heartbeat.elapsed_seconds, 1))
        if ($heartbeat.completed -ne $null) { $line += " progress=$($heartbeat.completed)/$($heartbeat.total)" }
        elseif ($heartbeat.current_index -ne $null) { $line += " progress=$($heartbeat.current_index)/$($heartbeat.total_count)" }
        else { $line += " progress=unknown reason=total_not_reported" }
        if ($heartbeat.current_item -ne $null) { $line += " item=$($heartbeat.current_item)" }
        if ($heartbeat.filing_count -ne $null) { $line += " filings=$($heartbeat.filing_count)" }
        if ($heartbeat.observation_count -ne $null) { $line += " observations=$($heartbeat.observation_count)" }
        if ($heartbeat.process_cpu_core_percent -ne $null) { $line += " cpu=$([math]::Round([double]$heartbeat.process_cpu_core_percent, 1))" }
        if ($heartbeat.io_read_Bps -ne $null) { $line += " io_read_Bps=$([math]::Round([double]$heartbeat.io_read_Bps, 0))" }
        if ($heartbeat.io_write_Bps -ne $null) { $line += " io_write_Bps=$([math]::Round([double]$heartbeat.io_write_Bps, 0))" }
        if ($heartbeat.output_free_gib -ne $null) { $line += " output_free_GB=$([math]::Round([double]$heartbeat.output_free_gib, 1))" }
        Write-Output $line
        if ($status -in @('COMPLETE','FAILED','INTERRUPTED','STALE_NO_PROCESS')) { break }
    } else {
        Write-Output "[$((Get-Date).ToUniversalTime().ToString('s'))] status=WAITING_FOR_HEARTBEAT"
    }
    Start-Sleep -Seconds $IntervalSeconds
}
