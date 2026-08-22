[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,

    [switch]$Watch,

    [ValidateRange(2, 300)]
    [int]$IntervalSeconds = 10
)

$ErrorActionPreference = 'Stop'
$controlRoot = Join-Path $RunRoot '00_control\trades_accelerator'
$heartbeatPath = Join-Path $controlRoot 'heartbeat.json'
$finalPath = Join-Path $controlRoot 'final_manifest.json'

function Read-JsonSafe {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try { return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json }
    catch { return $null }
}

function Value-OrNa {
    param([object]$Object, [string]$Name)
    if ($null -eq $Object) { return 'n/a' }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property -or $null -eq $property.Value) { return 'n/a' }
    return [string]$property.Value
}

function Write-Snapshot {
    $heartbeat = Read-JsonSafe -Path $heartbeatPath
    $final = Read-JsonSafe -Path $finalPath
    $now = [datetime]::UtcNow
    if ($null -eq $heartbeat) {
        Write-Host "[$($now.ToString('o'))] status=waiting_for_trades_accelerator_heartbeat"
        return $false
    }
    $observed = [datetime]::Parse([string]$heartbeat.observed_at_utc).ToUniversalTime()
    $age = [math]::Round(($now - $observed).TotalSeconds, 1)
    $counts = $heartbeat.trades_counts
    Write-Host (
        '[{0}] status={1} stage={2} heartbeat_age_sec={3} workers={4}/{5} pending={6} running={7} committed={8}/{9} failed={10} original_pid={11} original_status={12} parent_alive={13}' -f `
            $now.ToString('o'),
            (Value-OrNa $heartbeat 'status'),
            (Value-OrNa $heartbeat 'stage'),
            $age,
            (Value-OrNa $heartbeat 'added_trades_workers_alive'),
            (Value-OrNa $heartbeat 'desired_trades_workers'),
            (Value-OrNa $counts 'pending'),
            (Value-OrNa $counts 'running'),
            (Value-OrNa $counts 'committed'),
            (Value-OrNa $counts 'total'),
            (Value-OrNa $counts 'failed'),
            (Value-OrNa $heartbeat 'original_worker_pid'),
            (Value-OrNa $heartbeat 'original_worker_status'),
            (Value-OrNa $heartbeat 'parent_alive')
    )
    foreach ($worker in @($heartbeat.added_trades_workers)) {
        Write-Host "  trades_worker pid=$($worker.pid) alive=$($worker.alive) exitcode=$(Value-OrNa $worker 'exitcode')"
    }
    foreach ($task in @($heartbeat.active_trades)) {
        Write-Host "  active ticker=$($task.ticker) pid=$($task.worker_pid) attempt=$($task.attempt)"
    }
    if ($null -ne $final) {
        Write-Host "  final status=$(Value-OrNa $final 'status') stage=$(Value-OrNa $final 'stage')"
    }
    return ([string]$heartbeat.status -in @('completed', 'failed', 'interrupted'))
}

do {
    $terminal = Write-Snapshot
    if (-not $Watch -or $terminal) { break }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)
