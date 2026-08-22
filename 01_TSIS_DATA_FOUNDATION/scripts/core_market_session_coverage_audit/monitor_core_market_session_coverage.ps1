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

function Read-JsonSafe([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try { return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json }
    catch { return $null }
}

function ValueOrNa([object]$Value) { if ($null -eq $Value) { 'n/a' } else { [string]$Value } }
function PropertyOrNull([object]$Object, [string]$Name) {
    if ($null -eq $Object) { return $null }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return $property.Value
}

$heartbeatPath = Join-Path $RunRoot '00_control\heartbeat.json'
$finalPath = Join-Path $RunRoot '05_closeout\final_manifest.json'
do {
    $now = [datetime]::UtcNow
    $heartbeat = Read-JsonSafe $heartbeatPath
    if ($null -eq $heartbeat) {
        Write-Host "[$($now.ToString('o'))] status=unknown stage=no_heartbeat run_root=$RunRoot"
        $terminal = $false
    } else {
        $observed = [datetime]::Parse([string]$heartbeat.observed_at_utc).ToUniversalTime()
        $age = [math]::Round(($now - $observed).TotalSeconds, 1)
        $processAlive = $null -ne (Get-Process -Id ([int]$heartbeat.active_pid) -ErrorAction SilentlyContinue)
        $counts = $heartbeat.task_counts
        Write-Host ((@(
            "[$($now.ToString('o'))]"
            "status=$(ValueOrNa $heartbeat.status)"
            "stage=$(ValueOrNa $heartbeat.stage)"
            "heartbeat_age_sec=$age"
            "process_alive=$processAlive"
            "pending=$(ValueOrNa (PropertyOrNull $counts 'pending'))"
            "running=$(ValueOrNa (PropertyOrNull $counts 'running'))"
            "committed=$(ValueOrNa (PropertyOrNull $counts 'committed'))"
            "failed=$(ValueOrNa (PropertyOrNull $counts 'failed'))"
            "files_read=$(ValueOrNa $heartbeat.files_read)"
            "minute_rows=$(ValueOrNa $heartbeat.minute_rows_read)"
            "presence_rows=$(ValueOrNa $heartbeat.presence_rows)"
            "gap_rows=$(ValueOrNa $heartbeat.gap_rows)"
            "active_ticker=$(ValueOrNa (PropertyOrNull $heartbeat 'active_ticker'))"
        )) -join ' ')
        $terminal = [string]$heartbeat.status -in @('completed', 'failed', 'interrupted')
        if (-not $processAlive -and $age -gt (3 * $IntervalSeconds) -and -not $terminal) {
            Write-Warning 'Stale heartbeat and no live process; resume is required.'
        }
    }
    $final = Read-JsonSafe $finalPath
    if ($null -ne $final) {
        Write-Host "  final technical_status=$($final.technical_status) comparison_state=$($final.comparison_state)"
    }
    if (-not $Watch -or $terminal) { break }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)
