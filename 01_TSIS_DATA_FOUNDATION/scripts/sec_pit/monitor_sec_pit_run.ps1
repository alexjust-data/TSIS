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
        $age = [math]::Round(((Get-Date).ToUniversalTime() - [datetime]$heartbeat.observed_at_utc).TotalSeconds, 1)
        if ($status -eq 'RUNNING' -and -not $alive -and $age -gt ($IntervalSeconds * 3) -and -not (Test-Path -LiteralPath $finalPath)) {
            $status = 'STALE_NO_PROCESS'
        }
        $line = "[{0}] status={1} stage={2} wrapper_alive={3} heartbeat_age_s={4}" -f (Get-Date).ToUniversalTime().ToString('s'), $status, $heartbeat.stage, $alive.ToString().ToLower(), $age
        if ($heartbeat.completed -ne $null) { $line += " progress=$($heartbeat.completed)/$($heartbeat.total)" }
        if ($heartbeat.filing_count -ne $null) { $line += " filings=$($heartbeat.filing_count)" }
        if ($heartbeat.observation_count -ne $null) { $line += " observations=$($heartbeat.observation_count)" }
        Write-Output $line
        if ($status -in @('COMPLETE','FAILED','STALE_NO_PROCESS')) { break }
    } else {
        Write-Output "[$((Get-Date).ToUniversalTime().ToString('s'))] status=WAITING_FOR_HEARTBEAT"
    }
    Start-Sleep -Seconds $IntervalSeconds
}

