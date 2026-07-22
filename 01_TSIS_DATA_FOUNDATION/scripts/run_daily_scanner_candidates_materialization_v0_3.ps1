param(
    [string]$StartDate = "2005-01-03",
    [string]$EndDate = "2025-12-31",
    [string]$ProjectRoot = "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION",
    [string]$OutputBaseRoot = "E:\TSIS\data\data_foundation_outputs\daily_scanner_candidates_table\candidate_replays",
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
    $replaceId = [guid]::NewGuid().ToString("N")
    $tmp = "$Path.$PID.$replaceId.tmp"
    $backup = "$Path.$PID.$replaceId.bak"
    $Payload | ConvertTo-Json -Depth $Depth | Set-Content -LiteralPath $tmp -Encoding UTF8
    try {
        if (Test-Path -LiteralPath $Path -PathType Leaf) {
            [System.IO.File]::Replace($tmp, $Path, $backup, $true)
        }
        else {
            [System.IO.File]::Move($tmp, $Path)
        }
    }
    catch {
        if (Test-Path -LiteralPath $Path -PathType Leaf) {
            Remove-Item -LiteralPath $Path -Force
        }
        [System.IO.File]::Move($tmp, $Path)
    }
    finally {
        Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $backup -Force -ErrorAction SilentlyContinue
    }
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
        if ([string]::IsNullOrWhiteSpace($root)) {
            return $null
        }
        $drive = Get-PSDrive -Name $root.Substring(0, 1) -ErrorAction Stop
        return [Math]::Round($drive.Free / 1GB, 2)
    }
    catch {
        return $null
    }
}

function ConvertTo-Arg {
    param([string]$Value)
    if ($null -eq $Value) {
        return '""'
    }
    return '"' + ([string]$Value).Replace('"', '\"') + '"'
}

function Get-YearWindows {
    param(
        [datetime]$Start,
        [datetime]$End
    )
    $windows = @()
    for ($year = $Start.Year; $year -le $End.Year; $year++) {
        $windowStart = Get-Date -Year $year -Month 1 -Day 1
        $windowEnd = Get-Date -Year $year -Month 12 -Day 31
        if ($windowStart -lt $Start) { $windowStart = $Start }
        if ($windowEnd -gt $End) { $windowEnd = $End }
        $windows += [PSCustomObject]@{
            year = $year
            start_date = $windowStart.ToString("yyyy-MM-dd")
            end_date = $windowEnd.ToString("yyyy-MM-dd")
        }
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
    $logInfo = [ordered]@{
        log_path = $LogPath
        log_size_bytes = $null
        log_last_write_utc = $null
    }
    if (-not [string]::IsNullOrWhiteSpace($LogPath) -and (Test-Path -LiteralPath $LogPath -PathType Leaf)) {
        $logItem = Get-Item -LiteralPath $LogPath
        $logInfo.log_size_bytes = $logItem.Length
        $logInfo.log_last_write_utc = $logItem.LastWriteTimeUtc.ToString("o")
    }
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
        project_root = $ProjectRoot
        output_root = $script:RunRoot
        output_drive_free_gb = Get-DriveFreeGbForPath -PathValue $script:RunRoot
        physical_counting_policy = "progress is year-window based; no recursive million-file scans in heartbeat"
    }
    foreach ($key in $perf.Keys) { $payload[$key] = $perf[$key] }
    foreach ($key in $logInfo.Keys) { $payload[$key] = $logInfo[$key] }
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
    $builder = Join-Path $ProjectRoot "scripts\materialize_daily_scanner_candidates_table_v0_3.py"
    if (-not (Test-Path -LiteralPath $builder -PathType Leaf)) {
        throw "Missing builder: $builder"
    }
    $yearRunId = "$script:RunId`_year_$($Window.year)"
    $yearRoot = Join-Path $script:RunRoot ("parts\year={0}" -f $Window.year)
    New-Item -ItemType Directory -Force -Path $yearRoot | Out-Null
    $logPath = Join-Path $script:RunRoot ("logs\year={0}.stdout.log" -f $Window.year)
    $errPath = Join-Path $script:RunRoot ("logs\year={0}.stderr.log" -f $Window.year)
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $logPath) | Out-Null

    $args = @(
        $builder,
        "--start-date", $Window.start_date,
        "--end-date", $Window.end_date,
        "--run-id", $yearRunId,
        "--output-root", $yearRoot
    )
    if ($Overwrite) {
        $args += "--overwrite"
    }

    Write-OperationHeartbeat -Status "running" -Stage "year_window_start" -CurrentItem $Window.year -CurrentIndex $Index -TotalCount $Total -LogPath $logPath -Extra @{
        window_start_date = $Window.start_date
        window_end_date = $Window.end_date
        year_output_root = $yearRoot
    }

    $argText = (($args | ForEach-Object { ConvertTo-Arg -Value ([string]$_) }) -join " ")
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $PythonExe
    $psi.Arguments = $argText
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi
    [void]$proc.Start()
    $pids = [ordered]@{
        run_id = $script:RunId
        observed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        wrapper_pid = $PID
        active_pid = $proc.Id
        active_stage = "year_window"
        current_item = $Window.year
        command = $PythonExe
        args = $args
        command_text = (ConvertTo-Arg -Value $PythonExe) + " " + $argText
        log_path = $logPath
        stderr_log_path = $errPath
    }
    Write-JsonAtomic -Path $script:PidPath -Payload $pids

    while (-not $proc.HasExited) {
        Write-OperationHeartbeat -Status "running" -Stage "year_window" -CurrentItem $Window.year -CurrentIndex $Index -TotalCount $Total -ActivePid $proc.Id -LogPath $logPath -Extra @{
            window_start_date = $Window.start_date
            window_end_date = $Window.end_date
            year_output_root = $yearRoot
        }
        Start-Sleep -Seconds $HeartbeatSeconds
        $proc.Refresh()
    }

    $stdout = $proc.StandardOutput.ReadToEnd()
    $stderr = $proc.StandardError.ReadToEnd()
    $proc.WaitForExit()
    $proc.Refresh()
    Set-Content -LiteralPath $logPath -Encoding UTF8 -Value $stdout
    Set-Content -LiteralPath $errPath -Encoding UTF8 -Value $stderr
    $exitCode = $proc.ExitCode
    if ($null -eq $exitCode) {
        $exitCode = -9999
    }

    if ($exitCode -ne 0) {
        Write-OperationHeartbeat -Status "failed" -Stage "year_window_failed" -CurrentItem $Window.year -CurrentIndex $Index -TotalCount $Total -ActivePid $proc.Id -LogPath $logPath -Extra @{
            exit_code = $exitCode
            stderr_log_path = $errPath
        }
        throw "Builder failed for year $($Window.year) with exit code $exitCode. See $errPath"
    }

    $manifest = Join-Path $yearRoot "_daily_scanner_candidates_table_manifest_v0_3_candidate_replay.json"
    $summary = Join-Path $yearRoot "_daily_scanner_candidates_table_summary_v0_3_candidate_replay.csv"
    Write-OperationHeartbeat -Status "running" -Stage "year_window_finished" -CurrentItem $Window.year -CurrentIndex $Index -TotalCount $Total -LogPath $logPath -Extra @{
        year_output_root = $yearRoot
        year_manifest = $manifest
        year_summary = $summary
    }
    return [ordered]@{
        year = $Window.year
        start_date = $Window.start_date
        end_date = $Window.end_date
        output_root = $yearRoot
        manifest = $manifest
        summary = $summary
    }
}

$start = [datetime]::ParseExact($StartDate, "yyyy-MM-dd", $null)
$end = [datetime]::ParseExact($EndDate, "yyyy-MM-dd", $null)
if ($start -gt $end) {
    throw "StartDate must be <= EndDate"
}

if ([string]::IsNullOrWhiteSpace($RunId)) {
    $RunId = "daily_scanner_candidates_v0_3_" + (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
}
if ([string]::IsNullOrWhiteSpace($RunRoot)) {
    $RunRoot = Join-Path $OutputBaseRoot $RunId
}

$script:RunId = $RunId
$script:RunRoot = $RunRoot
$script:PreManifestPath = Join-Path $RunRoot "$RunId.pre_manifest.json"
$script:HeartbeatPath = Join-Path $RunRoot "$RunId.heartbeat.json"
$script:HeartbeatLogPath = Join-Path $RunRoot "$RunId.heartbeat.jsonl"
$script:PidPath = Join-Path $RunRoot "$RunId.pids.json"
$script:SummaryPath = Join-Path $RunRoot "_run_summary.json"

$windows = @(Get-YearWindows -Start $start -End $end)
$git = Get-GitSnapshot -Root (Split-Path -Parent $ProjectRoot)
$preManifest = [ordered]@{
    run_id = $RunId
    status = if ($Run) { "prepared_to_run" } else { "dry_run_only" }
    created_at_utc = $ScriptStartedAtUtc.ToString("o")
    script_path = $ScriptPath
    project_root = $ProjectRoot
    builder = Join-Path $ProjectRoot "scripts\materialize_daily_scanner_candidates_table_v0_3.py"
    start_date = $StartDate
    end_date = $EndDate
    output_root = $RunRoot
    output_base_root = $OutputBaseRoot
    year_window_count = $windows.Count
    year_windows = $windows
    overwrite = [bool]$Overwrite
    python_exe = $PythonExe
    git = $git
    materialization_scope = "candidate_replay_year_windowed_not_official"
    full_universe_claim = $false
    telemetry_contract = "pre_manifest + heartbeat + pid_manifest + logs + monitor command"
}

New-Item -ItemType Directory -Force -Path $RunRoot | Out-Null
Write-JsonAtomic -Path $script:PreManifestPath -Payload $preManifest
Write-OperationHeartbeat -Status "prepared" -Stage "pre_manifest" -CurrentItem $StartDate -CurrentIndex 0 -TotalCount $windows.Count -Extra @{
    run_mode = if ($Run) { "run" } else { "dry_run" }
}

Write-Host "TSIS daily scanner candidates v0.3 runner"
Write-Host "Run ID: $RunId"
Write-Host "Mode: $(if ($Run) { 'run' } else { 'dry_run' })"
Write-Host "Date range: $StartDate -> $EndDate"
Write-Host "Year windows: $($windows.Count)"
Write-Host "Run root: $RunRoot"
Write-Host "Pre-manifest: $script:PreManifestPath"
Write-Host "Heartbeat: $script:HeartbeatPath"
Write-Host "PID manifest: $script:PidPath"
Write-Host "Monitor command:"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File `"$(Join-Path $ProjectRoot 'scripts\monitor_long_running_operation.ps1')`" -RunRoot `"$RunRoot`" -RunId `"$RunId`" -Compact -Watch"

if (-not $Run) {
    Write-Host "Dry run only. Add -Run to materialize yearly candidate parts."
    exit 0
}

$results = @()
$i = 0
foreach ($window in $windows) {
    $i += 1
    $results += Invoke-BuilderForWindow -Window $window -Index $i -Total $windows.Count
}

$summary = [ordered]@{
    run_id = $RunId
    status = "completed"
    completed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    elapsed_seconds = [Math]::Round(((Get-Date).ToUniversalTime() - $ScriptStartedAtUtc).TotalSeconds, 1)
    start_date = $StartDate
    end_date = $EndDate
    output_root = $RunRoot
    year_window_count = $windows.Count
    parts = $results
    promotion_level = "candidate_replay_not_official"
    full_universe_claim = $false
}
Write-JsonAtomic -Path $script:SummaryPath -Payload $summary
Write-OperationHeartbeat -Status "completed" -Stage "completed" -CurrentItem $script:SummaryPath -CurrentIndex $windows.Count -TotalCount $windows.Count -Extra @{
    summary_path = $script:SummaryPath
}

Write-Host "Completed."
Write-Host "Run root: $RunRoot"
Write-Host "Summary: $script:SummaryPath"
