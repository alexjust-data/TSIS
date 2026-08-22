param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,
    [int]$IntervalSeconds = 10,
    [switch]$Compact,
    [switch]$Watch
)

$ErrorActionPreference = "SilentlyContinue"
function Read-JsonSafe([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    try { return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json }
    catch { return $null }
}
function Show-Status {
    $now = (Get-Date).ToUniversalTime()
    $heartbeat = Read-JsonSafe (Join-Path $RunRoot "heartbeat_latest.json")
    $final = Read-JsonSafe (Join-Path $RunRoot "final_manifest.json")
    $handoff = Read-JsonSafe (Join-Path $RunRoot "human_gate_handoff.json")
    $panel = Read-JsonSafe (Join-Path $RunRoot "blind_panel\panel_manifest.json")
    $gallery = Read-JsonSafe (Join-Path $RunRoot "blind_panel\gallery_manifest.json")
    $wrapperAlive = $false
    $cpu = "n/a"
    $rssGiB = "n/a"
    $pidPath = Join-Path $RunRoot "wrapper_pid.txt"
    if (Test-Path -LiteralPath $pidPath) {
        $wrapperPid = [int](Get-Content -LiteralPath $pidPath -Raw)
        $process = Get-Process -Id $wrapperPid
        if ($process) {
            $wrapperAlive = $true
            $cpu = [math]::Round($process.CPU, 1)
            $rssGiB = [math]::Round($process.WorkingSet64 / 1GB, 3)
        }
    }
    $status = "WAITING"
    $stage = "PRE_START"
    $progress = "0/2400"
    $ticker = ""
    $age = "n/a"
    if ($heartbeat) {
        $status = [string]$heartbeat.status
        $stage = [string]$heartbeat.stage
        $progress = [string]$heartbeat.target_progress
        $ticker = [string]$heartbeat.ticker
        $updated = [datetimeoffset]::Parse([string]$heartbeat.updated_at_utc)
        $age = [math]::Round(($now - $updated.UtcDateTime).TotalSeconds, 2)
    }
    if ($final -and $final.status -eq "FAILED") { $status = "FAILED"; $stage = "FINAL" }
    if ($panel -and -not $gallery) { $status = [string]$panel.status; $stage = "BLIND_PANEL" }
    if ($gallery) { $status = [string]$gallery.status; $stage = "BLIND_GALLERY" }
    if ($handoff) { $status = [string]$handoff.status; $stage = [string]$handoff.stage }
    $freeGiB = "n/a"
    try {
        $letter = [System.IO.Path]::GetPathRoot($RunRoot).Substring(0,1)
        $drive = Get-PSDrive -Name $letter
        $freeGiB = [math]::Round($drive.Free / 1GB, 2)
    } catch {}
    $stamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    Write-Host "[$stamp] status=$status stage=$stage wrapper_alive=$wrapperAlive latest_age_sec=$age targets=$progress ticker=$ticker cpu_s=$cpu rss_GiB=$rssGiB output_free_GiB=$freeGiB"
    return $status
}
do {
    $current = Show-Status
    if (-not $Watch) { break }
    if ($current -in @("FAILED", "WAITING_HUMAN_BLIND_REVIEW")) { break }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)
