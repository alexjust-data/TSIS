param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,
    [int]$IntervalSeconds = 10,
    [switch]$Compact,
    [switch]$Watch
)

$ErrorActionPreference = 'Stop'
$heartbeat = Join-Path $RunRoot 'heartbeat_latest.json'

do {
    if (-not (Test-Path -LiteralPath $heartbeat)) {
        Write-Output "[$(Get-Date -Format s)] status=WAITING heartbeat_missing=True"
    }
    else {
        $state = Get-Content -LiteralPath $heartbeat -Raw | ConvertFrom-Json
        $observed = [DateTimeOffset]::Parse($state.observed_at_utc)
        $age = ([DateTimeOffset]::UtcNow - $observed).TotalSeconds
        $alive = $false
        if ($state.wrapper_pid) {
            $alive = $null -ne (Get-Process -Id ([int]$state.wrapper_pid) -ErrorAction SilentlyContinue)
        }
        if ($Compact) {
            Write-Output (
                '[{0}] status={1} stage={2} wrapper_alive={3} latest_age_sec={4:N2} os={5}/{6} ownership={7}/{6} ticker={8} failed={9} cpu={10:N1} rss_GiB={11:N2} ram_free_GiB={12:N2}' -f
                (Get-Date -Format s), $state.status, $state.stage, $alive, $age,
                $state.os_completed, $state.total_cases, $state.owner_completed,
                $state.current_ticker, $state.failed, $state.system_cpu_percent,
                $state.process_rss_gib, $state.available_memory_gib
            )
        }
        else {
            $state | Add-Member -NotePropertyName latest_age_seconds -NotePropertyValue $age -Force
            $state | Add-Member -NotePropertyName wrapper_process_alive -NotePropertyValue $alive -Force
            $state | ConvertTo-Json -Depth 5
        }
    }
    if (-not $Watch) { break }
    if ($state -and $state.status -in @('COMPLETE', 'FAILED')) { break }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)
