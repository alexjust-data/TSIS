param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,
    [switch]$Watch,
    [int]$IntervalSeconds = 10
)

$ErrorActionPreference = 'Stop'
$heartbeatPath = Join-Path $RunRoot '00_control\quotes_scaleout_6_workers\heartbeat.json'

do {
    if (-not (Test-Path -LiteralPath $heartbeatPath)) {
        Write-Host "[$([DateTime]::UtcNow.ToString('o'))] status=waiting_for_quotes_scaleout_heartbeat"
    }
    else {
        $heartbeat = Get-Content -LiteralPath $heartbeatPath -Raw | ConvertFrom-Json
        $age = ([DateTime]::UtcNow - [DateTime]::Parse($heartbeat.observed_at_utc).ToUniversalTime()).TotalSeconds
        $counts = $heartbeat.quotes_counts
        Write-Host ('[{0}] status={1} heartbeat_age_sec={2:N1} quote_workers={3}+{4}/{5} pending={6} running={7} committed={8} failed={9} duplicates={10} trades_alive={11}' -f `
            [DateTime]::UtcNow.ToString('o'),
            $heartbeat.status,
            $age,
            $heartbeat.original_quote_workers_alive,
            $heartbeat.added_quote_workers_alive,
            $heartbeat.target_total_quote_workers,
            $counts.pending,
            $counts.running,
            $counts.committed,
            $counts.failed,
            $heartbeat.duplicate_active_tasks,
            $heartbeat.trades_worker_alive)
        foreach ($task in @($heartbeat.active_quotes)) {
            Write-Host "  active family=quotes_ ticker=$($task.ticker) pid=$($task.worker_pid) attempt=$($task.attempt)"
        }
    }
    if ($Watch) { Start-Sleep -Seconds $IntervalSeconds }
} while ($Watch)
