param(
    [string]$StartDate = "2005-01-03",
    [string]$EndDate = "2025-12-31",
    [string]$ProjectRoot = "C:\TSIS_Data\01_TSIS_backtest_SmallCaps",
    [string]$OutputBaseRoot = "E:\TSIS\data\data_foundation_outputs\intraday_scanner_candidates_table\candidate_replays",
    [string]$RunRoot = "",
    [string]$RunId = "",
    [string]$PythonExe = "python",
    [int]$HeartbeatSeconds = 30,
    [switch]$Run,
    [switch]$Overwrite
)

$ErrorActionPreference = "Stop"
$ScriptStartedAtUtc = (Get-Date).ToUniversalTime()
$ScriptPath = $MyInvocation.MyCommand.Path

$env:PYTHONUTF8 = "1"
$env:PYTHONUNBUFFERED = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"

function Write-JsonAtomic {
    param(
        [string]$Path,
        [object]$Payload,
        [int]$Depth = 10
    )
    $dir = Split-Path -Parent $Path
    if (-not [string]::IsNullOrWhiteSpace($dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    $tmp = "$Path.$PID.$([guid]::NewGuid().ToString('N')).tmp"
    $Payload | ConvertTo-Json -Depth $Depth | Set-Content -LiteralPath $tmp -Encoding UTF8
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        Remove-Item -LiteralPath $Path -Force
    }
    [System.IO.File]::Move($tmp, $Path)
}

function Add-JsonLine {
    param(
        [string]$Path,
        [object]$Payload,
        [int]$Depth = 10
    )
    $dir = Split-Path -Parent $Path
    if (-not [string]::IsNullOrWhiteSpace($dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    Add-Content -LiteralPath $Path -Encoding UTF8 -Value ($Payload | ConvertTo-Json -Compress -Depth $Depth)
}

function Get-GitSnapshot {
    param([string]$Root)
    $snapshot = [ordered]@{
        branch = $null
        commit = $null
        dirty_state = "unknown"
    }
    try {
        $snapshot.branch = (& git -C $Root rev-parse --abbrev-ref HEAD 2>$null)
        $snapshot.commit = (& git -C $Root rev-parse HEAD 2>$null)
        $dirty = (& git -C $Root status --porcelain 2>$null)
        $snapshot.dirty_state = if ([string]::IsNullOrWhiteSpace(($dirty -join ""))) { "clean" } else { "dirty" }
    }
    catch {
        $snapshot.dirty_state = "unavailable"
    }
    return $snapshot
}

function Get-ProcessPerfSnapshot {
    param([Nullable[int]]$ProcessId)
    if ($null -eq $ProcessId) {
        return [ordered]@{
            active_pid_alive = $null
            process_cpu_pct = $null
            io_read_bytes_per_sec = $null
            io_write_bytes_per_sec = $null
            io_data_bytes_per_sec = $null
        }
    }
    $alive = $false
    try {
        $proc = Get-Process -Id ([int]$ProcessId) -ErrorAction Stop
        $alive = -not $proc.HasExited
    }
    catch {
        $alive = $false
    }
    $perf = $null
    try {
        $perf = Get-CimInstance Win32_PerfFormattedData_PerfProc_Process |
            Where-Object { [int]$_.IDProcess -eq [int]$ProcessId } |
            Select-Object -First 1
    }
    catch {
        $perf = $null
    }
    return [ordered]@{
        active_pid_alive = [bool]$alive
        process_cpu_pct = if ($perf -ne $null) { $perf.PercentProcessorTime } else { $null }
        io_read_bytes_per_sec = if ($perf -ne $null) { $perf.IOReadBytesPersec } else { $null }
        io_write_bytes_per_sec = if ($perf -ne $null) { $perf.IOWriteBytesPersec } else { $null }
        io_data_bytes_per_sec = if ($perf -ne $null) { $perf.IODataBytesPersec } else { $null }
    }
}

function Get-DriveFreeGbForPath {
    param([string]$PathValue)
    try {
        $root = [System.IO.Path]::GetPathRoot($PathValue)
        if ([string]::IsNullOrWhiteSpace($root)) { return $null }
        $drive = Get-PSDrive -Name $root.Substring(0, 1) -ErrorAction Stop
        return [Math]::Round($drive.Free / 1GB, 2)
    }
    catch {
        return $null
    }
}

function ConvertTo-Arg {
    param([string]$Value)
    if ($null -eq $Value) { return '""' }
    return '"' + ([string]$Value).Replace('"', '\"') + '"'
}

function Get-MonthWindows {
    param(
        [datetime]$Start,
        [datetime]$End
    )
    $windows = @()
    $cursor = Get-Date -Year $Start.Year -Month $Start.Month -Day 1
    while ($cursor -le $End) {
        $monthStart = $cursor
        $monthEnd = $cursor.AddMonths(1).AddDays(-1)
        if ($monthStart -lt $Start) { $monthStart = $Start }
        if ($monthEnd -gt $End) { $monthEnd = $End }
        $windows += [PSCustomObject]@{
            year = $cursor.Year
            month = $cursor.Month
            key = $cursor.ToString("yyyy-MM")
            start_date = $monthStart.ToString("yyyy-MM-dd")
            end_date = $monthEnd.ToString("yyyy-MM-dd")
        }
        $cursor = $cursor.AddMonths(1)
    }
    return $windows
}

function Write-OperationHeartbeat {
    param(
        [string]$Status,
        [string]$Stage,
        [string]$CurrentItem = "",
        [int]$CurrentIndex = 0,
        [int]$TotalCount = 0,
        [Nullable[int]]$ActivePid = $null,
        [string]$LogPath = "",
        [hashtable]$Extra = @{}
    )
    $nowUtc = (Get-Date).ToUniversalTime()
    $perf = Get-ProcessPerfSnapshot -ProcessId $ActivePid
    $payload = [ordered]@{
        run_id = $script:RunId
        observed_at_utc = $nowUtc.ToString("o")
        status = $Status
        stage = $Stage
        elapsed_seconds = [Math]::Round(($nowUtc - $ScriptStartedAtUtc).TotalSeconds, 1)
        wrapper_pid = $PID
        active_pid = $ActivePid
        current_item = $CurrentItem
        current_index = $CurrentIndex
        total_count = $TotalCount
        progress_unit = "calendar_month_window"
        project_root = $ProjectRoot
        output_root = $script:RunRoot
        output_drive_free_gb = Get-DriveFreeGbForPath -PathValue $script:RunRoot
        physical_counting_policy = "progress is month-window based; no recursive million-file scans in heartbeat"
    }
    foreach ($key in $perf.Keys) { $payload[$key] = $perf[$key] }
    if (-not [string]::IsNullOrWhiteSpace($LogPath) -and (Test-Path -LiteralPath $LogPath -PathType Leaf)) {
        $logItem = Get-Item -LiteralPath $LogPath
        $payload["log_path"] = $LogPath
        $payload["log_size_bytes"] = $logItem.Length
        $payload["log_last_write_utc"] = $logItem.LastWriteTimeUtc.ToString("o")
    }
    foreach ($key in $Extra.Keys) { $payload[$key] = $Extra[$key] }
    Write-JsonAtomic -Path $script:HeartbeatPath -Payload $payload
    Add-JsonLine -Path $script:HeartbeatLogPath -Payload $payload
}

function Invoke-BuilderForWindow {
    param(
        [object]$Window,
        [int]$Index,
        [int]$Total
    )
    $builder = Join-Path $ProjectRoot "scripts\materialize_intraday_scanner_candidates_table_v0_1.py"
    if (-not (Test-Path -LiteralPath $builder -PathType Leaf)) {
        throw "Missing builder: $builder"
    }
    $partRunId = "$script:RunId`_month_$($Window.key.Replace('-', '_'))"
    $partRoot = Join-Path $script:RunRoot ("parts\year={0}\month={1:00}" -f $Window.year, $Window.month)
    New-Item -ItemType Directory -Force -Path $partRoot | Out-Null
    $logPath = Join-Path $script:RunRoot ("logs\{0}.stdout.log" -f $Window.key)
    $errPath = Join-Path $script:RunRoot ("logs\{0}.stderr.log" -f $Window.key)
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $logPath) | Out-Null

    $args = @(
        $builder,
        "--start-date", $Window.start_date,
        "--end-date", $Window.end_date,
        "--run-id", $partRunId,
        "--output-root", $partRoot
    )
    if ($Overwrite) { $args += "--overwrite" }

    Write-OperationHeartbeat -Status "running" -Stage "month_window_start" -CurrentItem $Window.key -CurrentIndex $Index -TotalCount $Total -LogPath $logPath -Extra @{
        window_start_date = $Window.start_date
        window_end_date = $Window.end_date
        part_output_root = $partRoot
    }

    $argText = (($args | ForEach-Object { ConvertTo-Arg -Value ([string]$_) }) -join " ")
    if (Test-Path -LiteralPath $logPath -PathType Leaf) {
        Remove-Item -LiteralPath $logPath -Force
    }
    if (Test-Path -LiteralPath $errPath -PathType Leaf) {
        Remove-Item -LiteralPath $errPath -Force
    }
    $proc = Start-Process `
        -FilePath $PythonExe `
        -ArgumentList $argText `
        -RedirectStandardOutput $logPath `
        -RedirectStandardError $errPath `
        -WindowStyle Hidden `
        -PassThru

    Write-JsonAtomic -Path $script:PidPath -Payload ([ordered]@{
        run_id = $script:RunId
        observed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        wrapper_pid = $PID
        active_pid = $proc.Id
        active_stage = "month_window"
        current_item = $Window.key
        command = $PythonExe
        args = $args
        stdout_log_path = $logPath
        stderr_log_path = $errPath
    })

    while (-not $proc.HasExited) {
        Start-Sleep -Seconds $HeartbeatSeconds
        Write-OperationHeartbeat -Status "running" -Stage "month_window" -CurrentItem $Window.key -CurrentIndex $Index -TotalCount $Total -ActivePid $proc.Id -LogPath $logPath -Extra @{
            window_start_date = $Window.start_date
            window_end_date = $Window.end_date
            part_output_root = $partRoot
        }
    }
    if ($proc.ExitCode -ne 0) {
        Write-OperationHeartbeat -Status "failed" -Stage "month_window_failed" -CurrentItem $Window.key -CurrentIndex $Index -TotalCount $Total -LogPath $logPath -Extra @{
            exit_code = $proc.ExitCode
            stderr_log_path = $errPath
        }
        throw "Builder failed for $($Window.key) with exit code $($proc.ExitCode). See $errPath"
    }
    Write-OperationHeartbeat -Status "running" -Stage "month_window_finished" -CurrentItem $Window.key -CurrentIndex $Index -TotalCount $Total -LogPath $logPath -Extra @{
        part_output_root = $partRoot
    }
}

$start = [datetime]::ParseExact($StartDate, "yyyy-MM-dd", $null)
$end = [datetime]::ParseExact($EndDate, "yyyy-MM-dd", $null)
if ($start -gt $end) { throw "StartDate must be <= EndDate" }
if ([string]::IsNullOrWhiteSpace($RunId)) {
    $RunId = "intraday_scanner_candidates_v0_1_" + (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
}
if ([string]::IsNullOrWhiteSpace($RunRoot)) {
    $RunRoot = Join-Path $OutputBaseRoot $RunId
}

$PreManifestPath = Join-Path $RunRoot "$RunId.pre_manifest.json"
$HeartbeatPath = Join-Path $RunRoot "$RunId.heartbeat.json"
$HeartbeatLogPath = Join-Path $RunRoot "$RunId.heartbeat.jsonl"
$PidPath = Join-Path $RunRoot "$RunId.pids.json"
$FinalSummaryPath = Join-Path $RunRoot "_run_summary.json"
$MonitorScript = Join-Path $ProjectRoot "scripts\monitor_long_running_operation.ps1"
$windows = @(Get-MonthWindows -Start $start -End $end)

New-Item -ItemType Directory -Force -Path $RunRoot | Out-Null

$preManifest = [ordered]@{
    run_id = $RunId
    created_at_utc = $ScriptStartedAtUtc.ToString("o")
    status = if ($Run) { "pre_manifest_created" } else { "dry_run" }
    script_path = $ScriptPath
    project_root = $ProjectRoot
    output_root = $RunRoot
    start_date = $StartDate
    end_date = $EndDate
    window_count = $windows.Count
    window_unit = "calendar_month"
    windows = $windows
    builder = Join-Path $ProjectRoot "scripts\materialize_intraday_scanner_candidates_table_v0_1.py"
    git = Get-GitSnapshot -Root (Split-Path -Parent $ProjectRoot)
    telemetry_contract = "pre_manifest + heartbeat + pid manifest + compact monitor command required"
}
Write-JsonAtomic -Path $PreManifestPath -Payload $preManifest -Depth 20
Write-JsonAtomic -Path $PidPath -Payload ([ordered]@{
    run_id = $RunId
    wrapper_pid = $PID
    active_pid = $null
    active_stage = "pre_manifest"
})

Write-Host "TSIS intraday scanner candidates materialization runner"
Write-Host "Run ID: $RunId"
Write-Host "Mode: $(if ($Run) { 'run' } else { 'dry_run' })"
Write-Host "Run root: $RunRoot"
Write-Host "Window count: $($windows.Count)"
Write-Host "Pre-manifest: $PreManifestPath"
Write-Host "Heartbeat: $HeartbeatPath"
Write-Host "PID manifest: $PidPath"
Write-Host "Monitor command:"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File `"$MonitorScript`" -RunRoot `"$RunRoot`" -RunId `"$RunId`" -Compact -Watch"

if (-not $Run) {
    Write-OperationHeartbeat -Status "dry_run" -Stage "pre_manifest_only" -CurrentItem "" -CurrentIndex 0 -TotalCount $windows.Count
    return
}

$index = 0
try {
    foreach ($window in $windows) {
        $index += 1
        Invoke-BuilderForWindow -Window $window -Index $index -Total $windows.Count
    }
    $summary = [ordered]@{
        run_id = $RunId
        status = "completed"
        completed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        run_root = $RunRoot
        start_date = $StartDate
        end_date = $EndDate
        window_count = $windows.Count
        parts_root = Join-Path $RunRoot "parts"
        full_universe_claim = $false
        materialization_scope = "candidate_replay_month_parts"
        note = "Monthly parts are authoritative for this runner output; promote/compact separately before official E-root dataset use."
    }
    Write-JsonAtomic -Path $FinalSummaryPath -Payload $summary -Depth 20
    Write-OperationHeartbeat -Status "completed" -Stage "completed" -CurrentItem $FinalSummaryPath -CurrentIndex $windows.Count -TotalCount $windows.Count
    Write-Host "Completed."
    Write-Host "Run root: $RunRoot"
    Write-Host "Summary: $FinalSummaryPath"
}
catch {
    Write-JsonAtomic -Path $FinalSummaryPath -Payload ([ordered]@{
        run_id = $RunId
        status = "failed"
        failed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        run_root = $RunRoot
        error = $_.Exception.Message
    }) -Depth 20
    Write-OperationHeartbeat -Status "failed" -Stage "failed" -CurrentItem $RunRoot -CurrentIndex $index -TotalCount $windows.Count
    throw
}
