[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,

    [switch]$Watch,

    [ValidateRange(2, 300)]
    [int]$IntervalSeconds = 10
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$controlRoot = Join-Path $RunRoot '00_control\quotes_accelerator'
$heartbeatPath = Join-Path $controlRoot 'heartbeat.json'
$finalPath = Join-Path $controlRoot 'final_manifest.json'

function Read-JsonSafe {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try { return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json }
    catch { return $null }
}

function Get-Value {
    param([object]$Object, [string]$Name)
    if ($null -eq $Object) { return $null }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return $property.Value
}

function Format-Value {
    param([object]$Value)
    if ($null -eq $Value) { return 'n/a' }
    return [string]$Value
}

function Write-Snapshot {
    $heartbeat = Read-JsonSafe -Path $heartbeatPath
    $final = Read-JsonSafe -Path $finalPath
    $now = [datetime]::UtcNow
    if ($null -eq $heartbeat) {
        Write-Host "[$($now.ToString('o'))] status=waiting_for_quotes_accelerator_heartbeat"
        return $false
    }
    $observed = [datetime]::Parse([string]$heartbeat.observed_at_utc).ToUniversalTime()
    $age = [math]::Round(($now - $observed).TotalSeconds, 1)
    $quotes = $heartbeat.quotes_counts
    $minute = $heartbeat.ohlcv_1m_counts
    Write-Host (
        '[{0}] status={1} stage={2} heartbeat_age_sec={3} quote_workers={4}/{5} quotes_pending={6} quotes_running={7} quotes_committed={8} quotes_failed={9} 1m_committed={10}/{11}' -f `
            $now.ToString('o'),
            (Format-Value $heartbeat.status),
            (Format-Value $heartbeat.stage),
            $age,
            (Format-Value $heartbeat.alive_quote_workers),
            (Format-Value $heartbeat.desired_quote_workers),
            (Format-Value (Get-Value $quotes 'pending')),
            (Format-Value (Get-Value $quotes 'running')),
            (Format-Value (Get-Value $quotes 'committed')),
            (Format-Value (Get-Value $quotes 'failed')),
            (Format-Value (Get-Value $minute 'committed')),
            (Format-Value (Get-Value $minute 'total'))
    )
    foreach ($worker in @($heartbeat.quote_workers)) {
        Write-Host "  quote_worker pid=$($worker.pid) alive=$($worker.alive) exitcode=$(Format-Value $worker.exitcode)"
    }
    foreach ($worker in @($heartbeat.protected_workers)) {
        $alive = $null -ne (Get-Process -Id ([int]$worker.worker_pid) -ErrorAction SilentlyContinue)
        Write-Host "  protected family=$($worker.family) ticker=$($worker.ticker) pid=$($worker.worker_pid) alive=$alive"
    }
    if ($null -ne $final) {
        Write-Host "  final status=$(Format-Value $final.status) stage=$(Format-Value $final.stage)"
    }
    return ([string]$heartbeat.status -in @('completed', 'failed'))
}

do {
    $terminal = Write-Snapshot
    if (-not $Watch -or $terminal) { break }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)
