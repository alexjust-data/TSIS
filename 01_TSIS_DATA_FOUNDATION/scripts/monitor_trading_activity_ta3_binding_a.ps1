param(
    [Parameter(Mandatory = $true)]
    [string]$RuntimeRoot,
    [int]$IntervalSeconds = 30,
    [switch]$Watch
)

$ErrorActionPreference = "Stop"

function Show-Status {
    $heartbeatPath = Join-Path $RuntimeRoot "heartbeat_latest.json"
    if (-not (Test-Path -LiteralPath $heartbeatPath -PathType Leaf)) {
        Write-Host "[$((Get-Date).ToString('s'))] status=UNKNOWN stage=NO_HEARTBEAT"
        return $false
    }
    $heartbeat = Get-Content -LiteralPath $heartbeatPath -Raw | ConvertFrom-Json
    $wrapperAlive = $false
    if ($null -ne $heartbeat.wrapper_pid) {
        $wrapperAlive = $null -ne (Get-Process -Id ([int]$heartbeat.wrapper_pid) -ErrorAction SilentlyContinue)
    }
    $activeAlive = $false
    if ($null -ne $heartbeat.active_pid) {
        $activeAlive = $null -ne (Get-Process -Id ([int]$heartbeat.active_pid) -ErrorAction SilentlyContinue)
    }

    $detail = $null
    $blocksRoot = Join-Path $RuntimeRoot "blocks"
    if (Test-Path -LiteralPath $blocksRoot -PathType Container) {
        $detailPath = Get-ChildItem -LiteralPath $blocksRoot -Recurse -Filter "heartbeat_latest.json" -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTimeUtc -Descending |
            Select-Object -First 1
        if ($null -ne $detailPath) {
            $detail = Get-Content -LiteralPath $detailPath.FullName -Raw | ConvertFrom-Json
        }
    }

    if ($null -ne $detail) {
        $ageSeconds = [math]::Round(([datetimeoffset]::UtcNow - [datetimeoffset]::Parse($detail.timestamp_utc)).TotalSeconds, 1)
        Write-Host (
            "[{0}] status={1} blocks={2}/{3} failed={5} stage={6} session={7} rows={8} partitions={9} elapsed_s={13} cpu_s={14} heartbeat_age_s={10} message={15} wrapper={11} worker={12}" -f
            (Get-Date).ToString("s"),
            $heartbeat.status,
            $heartbeat.current_index,
            $heartbeat.total_count,
            $heartbeat.completed_blocks,
            $heartbeat.failed_blocks,
            $detail.stage,
            $detail.current_session,
            $detail.counters.current_state_rows,
            $detail.counters.partitions_written,
            $ageSeconds,
            $wrapperAlive,
            $activeAlive,
            [math]::Round([double]$detail.elapsed_seconds, 1),
            $(if ($activeAlive) { [math]::Round((Get-Process -Id ([int]$heartbeat.active_pid)).CPU, 1) } else { "-" }),
            $detail.message
        )
    } else {
        Write-Host (
            "[{0}] status={1} stage={2} progress={3}/{4} block={5} completed={6} failed={7} wrapper_alive={8} active_pid={9} active_alive={10}" -f
            (Get-Date).ToString("s"),
            $heartbeat.status,
            $heartbeat.stage,
            $heartbeat.current_index,
            $heartbeat.total_count,
            $heartbeat.item,
            $heartbeat.completed_blocks,
            $heartbeat.failed_blocks,
            $wrapperAlive,
            $heartbeat.active_pid,
            $activeAlive
        )
    }
    return $heartbeat.status -in @("COMPLETE", "FAILED", "PREFLIGHT_PASS")
}

do {
    $terminal = Show-Status
    if (-not $Watch -or $terminal) {
        break
    }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)
