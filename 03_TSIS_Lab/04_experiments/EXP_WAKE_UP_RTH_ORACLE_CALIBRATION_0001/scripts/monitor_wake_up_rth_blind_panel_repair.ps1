param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,
    [Parameter(Mandatory = $true)]
    [string]$RepairId,
    [int]$IntervalSeconds = 10,
    [switch]$Compact,
    [switch]$Watch
)

$ErrorActionPreference = "Stop"
$RunRoot = (Resolve-Path -LiteralPath $RunRoot).Path
$repairRoot = Join-Path (Join-Path $RunRoot "repairs") $RepairId
$heartbeatPath = Join-Path $repairRoot "heartbeat_latest.json"
$pidPath = Join-Path $repairRoot "wrapper_pid.txt"
$finalPath = Join-Path $repairRoot "final_manifest.json"
$logPath = Join-Path $repairRoot "repair.log"

function Get-OutputFreeGiB {
    $root = [System.IO.Path]::GetPathRoot($RunRoot)
    if (-not $root) { return $null }
    $driveName = $root.TrimEnd('\').TrimEnd(':')
    $drive = Get-PSDrive -Name $driveName -ErrorAction SilentlyContinue
    if (-not $drive) { return $null }
    return [math]::Round($drive.Free / 1GB, 2)
}

do {
    $now = Get-Date
    $heartbeat = $null
    $final = $null
    if (Test-Path -LiteralPath $heartbeatPath) {
        try { $heartbeat = Get-Content -LiteralPath $heartbeatPath -Raw | ConvertFrom-Json } catch { }
    }
    if (Test-Path -LiteralPath $finalPath) {
        try { $final = Get-Content -LiteralPath $finalPath -Raw | ConvertFrom-Json } catch { }
    }
    $wrapperPid = $null
    if (Test-Path -LiteralPath $pidPath) {
        try { $wrapperPid = [int](Get-Content -LiteralPath $pidPath -Raw) } catch { }
    }
    $wrapperAlive = $false
    if ($wrapperPid) {
        $wrapperAlive = $null -ne (Get-Process -Id $wrapperPid -ErrorAction SilentlyContinue)
    }

    $status = "WAITING"
    $stage = "NO_HEARTBEAT"
    $progress = "unknown"
    $latestAgeSec = $null
    if ($heartbeat) {
        $status = [string]$heartbeat.status
        $stage = [string]$heartbeat.stage
        $progress = [string]$heartbeat.target_progress
        try {
            $updated = [datetimeoffset]::Parse([string]$heartbeat.updated_at_utc)
            $latestAgeSec = [math]::Round(([datetimeoffset]::Now - $updated).TotalSeconds, 2)
        } catch { }
    }
    if ($final) {
        if ([string]$final.status -eq "COMPLETE_PASS") {
            $status = "COMPLETE_PASS"
            $stage = "HUMAN_GATE"
        }
        elseif ([string]$final.status -eq "FAILED") {
            $status = "FAILED"
            $stage = "FINAL"
        }
    }
    if (-not $final -and -not $wrapperAlive -and $heartbeat -and $status -eq "RUNNING") {
        $status = "STALE_NO_PROCESS"
    }

    $logMiB = 0.0
    if (Test-Path -LiteralPath $logPath) {
        $logMiB = [math]::Round((Get-Item -LiteralPath $logPath).Length / 1MB, 2)
    }
    $ageText = if ($null -eq $latestAgeSec) { "n/a" } else { [string]$latestAgeSec }
    $freeText = [string](Get-OutputFreeGiB)
    $line = "[{0}] status={1} stage={2} wrapper_alive={3} latest_age_sec={4} progress={5} repair={6} log_MiB={7} output_free_GiB={8}" -f $now.ToString("yyyy-MM-ddTHH:mm:ss"), $status, $stage, $wrapperAlive, $ageText, $progress, $RepairId, $logMiB, $freeText
    Write-Host $line

    $terminal = $status -in @("COMPLETE_PASS", "FAILED", "STALE_NO_PROCESS")
    if (-not $Watch -or $terminal) { break }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)

if ($status -eq "FAILED" -or $status -eq "STALE_NO_PROCESS") { exit 1 }
exit 0
