param(
    [Parameter(Mandatory = $true)]
    [string]$RuntimeRoot,
    [int]$IntervalSeconds = 30,
    [switch]$Compact
)

$ErrorActionPreference = 'Stop'
$heartbeat = Join-Path $RuntimeRoot 'heartbeat_latest.json'
$final = Join-Path $RuntimeRoot 'final_manifest.json'

while ($true) {
    if (Test-Path -LiteralPath $heartbeat) {
        try {
            $h = Get-Content -LiteralPath $heartbeat -Raw | ConvertFrom-Json
            if ($Compact) {
                $gb = [math]::Round([double]$h.output_bytes / 1GB, 3)
                Write-Host "[$($h.observed_at_utc)] status=$($h.status) stage=$($h.stage) child_pid=$($h.child_pid) files=$($h.output_files) output_GB=$gb free_GB=$($h.output_free_gb) last=$($h.last_builder_line)"
            } else {
                $h | ConvertTo-Json -Depth 20
            }
            if ($h.status -in @('COMPLETE', 'FAILED')) { break }
        } catch {
            Write-Warning "Heartbeat is transiently unreadable: $($_.Exception.Message)"
        }
    } else {
        Write-Host "Waiting for heartbeat: $heartbeat"
    }
    Start-Sleep -Seconds $IntervalSeconds
}

if (Test-Path -LiteralPath $final) {
    Get-Content -LiteralPath $final -Raw
}
