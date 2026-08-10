param(
    [Parameter(Mandatory = $true)][string]$ReplayRoot,
    [switch]$Compact,
    [switch]$Watch,
    [int]$IntervalSeconds = 30
)

$ErrorActionPreference = "Stop"

do {
    $heartbeatPath = Join-Path $ReplayRoot "heartbeat_latest.json"
    $pidPath = Join-Path $ReplayRoot "pid_manifest.json"
    if (-not (Test-Path -LiteralPath $heartbeatPath)) {
        Write-Output "heartbeat unavailable: $heartbeatPath"
    } else {
        $heartbeat = Get-Content -LiteralPath $heartbeatPath -Raw | ConvertFrom-Json
        $pidAlive = $false
        if (Test-Path -LiteralPath $pidPath) {
            $pidState = Get-Content -LiteralPath $pidPath -Raw | ConvertFrom-Json
            $pidAlive = $null -ne (Get-Process -Id $pidState.wrapper_pid -ErrorAction SilentlyContinue)
        }
        if ($Compact) {
            Write-Output ("[{0}] status={1} progress={2}/{3} ticker={4} free_GiB={5} wrapper_alive={6}" -f `
                $heartbeat.observed_at_utc, $heartbeat.status, $heartbeat.current_index, `
                $heartbeat.total_count, $heartbeat.ticker, $heartbeat.free_space_gib, $pidAlive)
        } else {
            $heartbeat | Add-Member -NotePropertyName wrapper_alive -NotePropertyValue $pidAlive -Force
            $heartbeat | ConvertTo-Json -Depth 8
        }
    }
    if ($Watch) { Start-Sleep -Seconds $IntervalSeconds }
} while ($Watch)
