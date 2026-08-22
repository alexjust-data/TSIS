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

$heartbeatPath = Join-Path $RunRoot '00_control\heartbeat.json'
$pidPath = Join-Path $RunRoot '00_control\pids.json'
$finalManifestPath = Join-Path $RunRoot '04_closeout\final_manifest.json'

function Read-JsonSafe {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    try {
        return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

function Test-ProcessAlive {
    param([object]$ProcessId)
    if ($null -eq $ProcessId) {
        return $false
    }
    return $null -ne (Get-Process -Id ([int]$ProcessId) -ErrorAction SilentlyContinue)
}

function Format-Value {
    param([object]$Value)
    if ($null -eq $Value) { return 'n/a' }
    return [string]$Value
}

function Get-PropertyValue {
    param(
        [object]$Object,
        [string]$Name
    )
    if ($null -eq $Object) { return $null }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return $property.Value
}

function Write-Snapshot {
    $heartbeat = Read-JsonSafe -Path $heartbeatPath
    $pidManifest = Read-JsonSafe -Path $pidPath
    $finalManifest = Read-JsonSafe -Path $finalManifestPath
    $now = [datetime]::UtcNow

    if ($null -eq $heartbeat) {
        Write-Host "[$($now.ToString('o'))] status=unknown stage=no_heartbeat run_root=$RunRoot"
        return $false
    }

    $observed = [datetime]::Parse([string]$heartbeat.observed_at_utc).ToUniversalTime()
    $age = [math]::Round(($now - $observed).TotalSeconds, 1)
    $parentAlive = Test-ProcessAlive -ProcessId $heartbeat.active_pid
    $childAlive = 0
    foreach ($processId in @($heartbeat.child_pids)) {
        if (Test-ProcessAlive -ProcessId $processId) {
            $childAlive += 1
        }
    }

    $line = @(
        "[$($now.ToString('o'))]"
        "status=$(Format-Value $heartbeat.status)"
        "stage=$(Format-Value $heartbeat.stage)"
        "progress=$(Format-Value $heartbeat.current_index)/$(Format-Value $heartbeat.total_count)"
        "pct=$(Format-Value $heartbeat.progress_pct)"
        "heartbeat_age_sec=$age"
        "parent_alive=$parentAlive"
        "children_alive=$childAlive"
        "files=$(Format-Value $heartbeat.committed_file_count)"
        "dates=$(Format-Value $heartbeat.committed_date_count)"
        "error_files=$(Format-Value $heartbeat.committed_error_file_count)"
        "cpu_pct=$(Format-Value $heartbeat.process_cpu_pct)"
        "rss_bytes=$(Format-Value $heartbeat.process_rss_bytes)"
        "output_free_GB=$(Format-Value $heartbeat.output_free_gb)"
    ) -join ' '
    Write-Host $line

    if ($heartbeat.family_counts) {
        foreach ($property in $heartbeat.family_counts.PSObject.Properties) {
            $counts = $property.Value
            Write-Host (
                '  family={0} pending={1} running={2} committed={3} failed={4}' -f `
                    $property.Name,
                    (Format-Value (Get-PropertyValue $counts 'pending')),
                    (Format-Value (Get-PropertyValue $counts 'running')),
                    (Format-Value (Get-PropertyValue $counts 'committed')),
                    (Format-Value (Get-PropertyValue $counts 'failed'))
            )
        }
    }
    foreach ($task in @($heartbeat.active_tasks)) {
        Write-Host "  active family=$($task.family) ticker=$($task.ticker) pid=$($task.worker_pid)"
    }
    if ($null -ne $finalManifest) {
        Write-Host "  final technical_status=$(Format-Value $finalManifest.technical_status) dataset_verdict=$(Format-Value $finalManifest.dataset_verdict)"
    }
    if ($null -ne $pidManifest -and $age -gt (3 * $IntervalSeconds) -and -not $parentAlive -and $childAlive -eq 0) {
        Write-Warning 'Heartbeat is stale and no recorded process is alive. Resume may be required.'
    }

    return ([string]$heartbeat.status -in @('completed', 'failed', 'interrupted'))
}

do {
    $terminal = Write-Snapshot
    if (-not $Watch -or $terminal) {
        break
    }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)
