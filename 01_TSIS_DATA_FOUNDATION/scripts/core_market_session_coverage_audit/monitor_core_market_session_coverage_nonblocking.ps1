[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,

    [switch]$Watch,

    [ValidateRange(2, 300)]
    [int]$IntervalSeconds = 10
)

$ErrorActionPreference = 'Stop'
$heartbeatPath = Join-Path $RunRoot '00_control\heartbeat.json'
$finalPath = Join-Path $RunRoot '05_closeout\final_manifest.json'

function Read-JsonNonBlocking {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    $stream = $null
    $reader = $null
    try {
        $share = [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete
        $stream = [System.IO.FileStream]::new(
            $Path,
            [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::Read,
            $share
        )
        $reader = [System.IO.StreamReader]::new($stream, [System.Text.Encoding]::UTF8)
        return ($reader.ReadToEnd() | ConvertFrom-Json)
    } catch {
        return $null
    } finally {
        if ($null -ne $reader) { $reader.Dispose() }
        elseif ($null -ne $stream) { $stream.Dispose() }
    }
}

function Value-OrNa {
    param([object]$Object, [string]$Name)
    if ($null -eq $Object) { return 'n/a' }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property -or $null -eq $property.Value) { return 'n/a' }
    return [string]$property.Value
}

function Write-Snapshot {
    $heartbeat = Read-JsonNonBlocking -Path $heartbeatPath
    $final = Read-JsonNonBlocking -Path $finalPath
    $now = [datetime]::UtcNow
    if ($null -eq $heartbeat) {
        Write-Host "[$($now.ToString('o'))] status=waiting_for_nonblocking_heartbeat"
        return $false
    }
    $observed = [datetime]::Parse([string]$heartbeat.observed_at_utc).ToUniversalTime()
    $age = [math]::Round(($now - $observed).TotalSeconds, 1)
    $counts = $heartbeat.task_counts
    $processId = [int]$heartbeat.active_pid
    $alive = $null -ne (Get-Process -Id $processId -ErrorAction SilentlyContinue)
    Write-Host (
        '[{0}] status={1} stage={2} progress={3}/{4} heartbeat_age_sec={5} pid={6} alive={7} active={8} files={9} rows={10} gaps={11}' -f `
            $now.ToString('o'),
            (Value-OrNa $heartbeat 'status'),
            (Value-OrNa $heartbeat 'stage'),
            (Value-OrNa $counts 'committed'),
            (Value-OrNa $heartbeat 'total_count'),
            $age,
            $processId,
            $alive,
            (Value-OrNa $heartbeat 'active_ticker'),
            (Value-OrNa $heartbeat 'files_read'),
            (Value-OrNa $heartbeat 'minute_rows_read'),
            (Value-OrNa $heartbeat 'gap_rows')
    )
    if ($null -ne $final) {
        Write-Host "  final technical_status=$(Value-OrNa $final 'technical_status') comparison_state=$(Value-OrNa $final 'comparison_state')"
    }
    return ([string]$heartbeat.status -in @('completed', 'failed', 'interrupted'))
}

do {
    $terminal = Write-Snapshot
    if (-not $Watch -or $terminal) { break }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)
