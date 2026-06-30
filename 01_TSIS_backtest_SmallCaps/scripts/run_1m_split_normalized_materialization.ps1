param(
    [ValidateSet("split-affected", "all-existing")]
    [string]$Mode = "split-affected",

    [string]$ProjectRoot = "C:\TSIS_Data\01_TSIS_backtest_SmallCaps",
    [string]$MinuteRoot = "E:\TSIS\data\ohlcv_1m",
    [string]$SplitsRoot = "E:\TSIS\data\additional\corporate_actions\splits",
    [string]$RunRoot = "",
    [string]$OutputRoot = "",
    [int]$ChunkSize = 5000,
    [Nullable[int]]$MinYear = $null,
    [Nullable[int]]$MaxYear = $null,
    [Nullable[int]]$Limit = $null,
    [int]$SmokeLimit = 100,
    [int]$HeartbeatSeconds = 60,
    [string]$PythonExe = "python",
    [switch]$SmokeOnly,
    [switch]$RunAudit,
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

function Assert-PathExists {
    param(
        [string]$Path,
        [string]$Label
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Missing ${Label}: $Path"
    }
}

function Write-JsonAtomic {
    param(
        [string]$Path,
        [object]$Payload,
        [int]$Depth = 8
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
        if (Test-Path -LiteralPath $tmp -PathType Leaf) {
            Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
        }
        if (Test-Path -LiteralPath $backup -PathType Leaf) {
            Remove-Item -LiteralPath $backup -Force -ErrorAction SilentlyContinue
        }
    }
}

function Add-JsonLine {
    param(
        [string]$Path,
        [object]$Payload,
        [int]$Depth = 8
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
    } catch {
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
    } catch {
        $alive = $false
    }
    $perf = $null
    try {
        $perf = Get-CimInstance Win32_PerfFormattedData_PerfProc_Process |
            Where-Object { [int]$_.IDProcess -eq [int]$ProcessId } |
            Select-Object -First 1
    } catch {
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
    } catch {
        return $null
    }
}

function ConvertTo-CmdArgument {
    param([string]$Value)
    if ($null -eq $Value) {
        return '""'
    }
    $text = [string]$Value
    if ($text.Length -eq 0) {
        return '""'
    }
    return '"' + $text.Replace('"', '\"') + '"'
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
    if ([string]::IsNullOrWhiteSpace($script:HeartbeatPath)) {
        return
    }
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
        minute_root = $MinuteRoot
        splits_root = $SplitsRoot
        output_root = $OutputRoot
        output_drive_free_gb = Get-DriveFreeGbForPath -PathValue $OutputRoot
        physical_counting_policy = "recursive output counting is stage-boundary only; heartbeat avoids million-file scans"
    }
    foreach ($key in $perf.Keys) { $payload[$key] = $perf[$key] }
    foreach ($key in $logInfo.Keys) { $payload[$key] = $logInfo[$key] }
    foreach ($key in $Extra.Keys) { $payload[$key] = $Extra[$key] }
    Write-JsonAtomic -Path $script:HeartbeatPath -Payload $payload
    Add-JsonLine -Path $script:HeartbeatLogPath -Payload $payload
}

function Invoke-NativeLogged {
    param(
        [string]$LogPath,
        [string[]]$CommandArgs,
        [string]$Stage,
        [string]$CurrentItem = "",
        [int]$CurrentIndex = 0,
        [int]$TotalCount = 0
    )

    $stderrLogPath = "$LogPath.stderr.log"
    Write-OperationHeartbeat -Status "running" -Stage "${Stage}:start" -CurrentItem $CurrentItem -CurrentIndex $CurrentIndex -TotalCount $TotalCount -LogPath $LogPath -Extra @{
        native_exe = $PythonExe
        native_args = @($CommandArgs)
        stderr_log_path = $stderrLogPath
    }
    $cmdText = (ConvertTo-CmdArgument -Value $PythonExe) + " " +
        (($CommandArgs | ForEach-Object { ConvertTo-CmdArgument -Value ([string]$_) }) -join " ") +
        " > " + (ConvertTo-CmdArgument -Value $LogPath) +
        " 2> " + (ConvertTo-CmdArgument -Value $stderrLogPath)
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = "cmd.exe"
    $startInfo.Arguments = "/d /s /c `"$cmdText`""
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $startInfo
    [void]$proc.Start()
    $pidPayload = [ordered]@{
        run_id = $script:RunId
        observed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        wrapper_pid = $PID
        active_pid = $proc.Id
        active_stage = $Stage
        command = "cmd.exe"
        args = @($CommandArgs)
        command_text = $cmdText
        log_path = $LogPath
        stderr_log_path = $stderrLogPath
    }
    Write-JsonAtomic -Path $script:PidManifestPath -Payload $pidPayload

    while (-not $proc.HasExited) {
        Write-OperationHeartbeat -Status "running" -Stage $Stage -CurrentItem $CurrentItem -CurrentIndex $CurrentIndex -TotalCount $TotalCount -ActivePid $proc.Id -LogPath $LogPath -Extra @{
            stderr_log_path = $stderrLogPath
        }
        Start-Sleep -Seconds $HeartbeatSeconds
        $proc.Refresh()
    }
    $proc.WaitForExit()
    $proc.Refresh()
    Write-OperationHeartbeat -Status "running" -Stage "${Stage}:finished" -CurrentItem $CurrentItem -CurrentIndex $CurrentIndex -TotalCount $TotalCount -ActivePid $proc.Id -LogPath $LogPath -Extra @{
        native_exit_code = $proc.ExitCode
        stderr_log_path = $stderrLogPath
    }
    if ($proc.ExitCode -ne 0) {
        throw "Command failed with exit code $($proc.ExitCode). Log: $LogPath Stderr: $stderrLogPath"
    }
}

Assert-PathExists -Path $ProjectRoot -Label "ProjectRoot"
Assert-PathExists -Path $MinuteRoot -Label "MinuteRoot"
Assert-PathExists -Path $SplitsRoot -Label "SplitsRoot"

$ManifestBuilder = Join-Path $ProjectRoot "scripts\build_1m_split_normalized_materialization_manifest.py"
$Materializer = Join-Path $ProjectRoot "scripts\materialize_1m_split_normalized.py"
$AuditScript = Join-Path $ProjectRoot "scripts\inspection\minute\audit_1m_split_full_universe.py"

Assert-PathExists -Path $ManifestBuilder -Label "manifest builder"
Assert-PathExists -Path $Materializer -Label "materializer"
if ($RunAudit) {
    Assert-PathExists -Path $AuditScript -Label "audit script"
}

if ([string]::IsNullOrWhiteSpace($RunRoot)) {
    $script:RunId = "{0}_{1}" -f ($Mode -replace "-", "_"), (Get-Date -Format "yyyyMMdd_HHmmss")
    $RunRoot = Join-Path $ProjectRoot ("runs\data_foundation\1m_split_normalized_full_universe_candidate\{0}" -f $script:RunId)
} else {
    $script:RunId = Split-Path -Leaf $RunRoot
}

if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    if ($Mode -eq "all-existing") {
        $OutputRoot = "E:\TSIS\data\ohlcv_1m_split_normalized_physical_full_candidate"
    } else {
        $OutputRoot = "E:\TSIS\data\ohlcv_1m_split_normalized_full_universe_candidate"
    }
}

New-Item -ItemType Directory -Force -Path $RunRoot | Out-Null

$Manifest = Join-Path $RunRoot ("manifest_{0}.csv" -f ($Mode -replace "-", "_"))
$ChunksDir = Join-Path $RunRoot "chunks"
$RunSummaryPath = Join-Path $RunRoot "_run_summary.json"
$BuildManifestLog = Join-Path $RunRoot "build_manifest.log"
$script:PreManifestPath = Join-Path $RunRoot ("{0}.pre_manifest.json" -f $script:RunId)
$script:HeartbeatPath = Join-Path $RunRoot ("{0}.heartbeat.json" -f $script:RunId)
$script:HeartbeatLogPath = Join-Path $RunRoot ("{0}.heartbeat.jsonl" -f $script:RunId)
$script:PidManifestPath = Join-Path $RunRoot ("{0}.pids.json" -f $script:RunId)
$MonitorScript = Join-Path $ProjectRoot "scripts\monitor_long_running_operation.ps1"
$MonitorCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$MonitorScript`" -RunRoot `"$RunRoot`" -RunId `"$($script:RunId)`" -Compact -Watch"

$Config = [ordered]@{
    created_at = (Get-Date).ToString("o")
    mode = $Mode
    project_root = $ProjectRoot
    minute_root = $MinuteRoot
    splits_root = $SplitsRoot
    run_root = $RunRoot
    output_root = $OutputRoot
    manifest = $Manifest
    chunks_dir = $ChunksDir
    chunk_size = $ChunkSize
    min_year = $MinYear
    max_year = $MaxYear
    limit = $Limit
    smoke_only = [bool]$SmokeOnly
    smoke_limit = $SmokeLimit
    heartbeat_seconds = $HeartbeatSeconds
    run_audit = [bool]$RunAudit
    overwrite = [bool]$Overwrite
}
$Config | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $RunSummaryPath -Encoding UTF8

$PreManifest = [ordered]@{
    run_id = $script:RunId
    status = "starting"
    created_at_utc = $ScriptStartedAtUtc.ToString("o")
    script_path = $ScriptPath
    command_line = [Environment]::CommandLine
    cwd = (Get-Location).Path
    host = $env:COMPUTERNAME
    user = [Environment]::UserName
    wrapper_pid = $PID
    git = Get-GitSnapshot -Root $ProjectRoot
    mode = $Mode
    dry_run = $false
    project_root = $ProjectRoot
    minute_root = $MinuteRoot
    splits_root = $SplitsRoot
    run_root = $RunRoot
    output_root = $OutputRoot
    manifest = $Manifest
    chunks_dir = $ChunksDir
    run_summary_path = $RunSummaryPath
    pre_manifest_path = $script:PreManifestPath
    heartbeat_path = $script:HeartbeatPath
    heartbeat_log_path = $script:HeartbeatLogPath
    pid_manifest_path = $script:PidManifestPath
    build_manifest_log = $BuildManifestLog
    heartbeat_seconds = $HeartbeatSeconds
    expected_scope = if ($Mode -eq "split-affected") { "all split-affected ticker-month files identified by splits root" } else { "all existing minute files under minute root" }
    resume_policy = "rerun with same RunRoot/OutputRoot; materializer should skip or overwrite according to -Overwrite"
    overwrite = [bool]$Overwrite
    success_rule = "all native commands exit 0; final summary written; optional audit exits 0"
    monitor_command = $MonitorCommand
}
Write-JsonAtomic -Path $script:PreManifestPath -Payload $PreManifest
Write-JsonAtomic -Path $script:PidManifestPath -Payload ([ordered]@{
    run_id = $script:RunId
    observed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    wrapper_pid = $PID
    active_pid = $null
    active_stage = "startup"
})
Write-OperationHeartbeat -Status "running" -Stage "startup" -Extra @{
    monitor_command = $MonitorCommand
}

Write-Host "TSIS 1m split-normalized materialization runner"
Write-Host "Run ID: $script:RunId"
Write-Host "Mode: $Mode"
Write-Host "Run root: $RunRoot"
Write-Host "Output root: $OutputRoot"
Write-Host "Pre-manifest: $script:PreManifestPath"
Write-Host "Heartbeat: $script:HeartbeatPath"
Write-Host "PID manifest: $script:PidManifestPath"
Write-Host "Monitor command:"
Write-Host "  $MonitorCommand"
Write-Host ""

if ($SmokeOnly) {
    $SmokeManifest = Join-Path $RunRoot "manifest_smoke.csv"
    $SmokeArgs = @(
        $ManifestBuilder,
        "--minute-root", $MinuteRoot,
        "--splits-root", $SplitsRoot,
        "--output", $SmokeManifest,
        "--mode", $Mode,
        "--limit", [string]$SmokeLimit
    )
    if ($null -ne $MinYear) {
        $SmokeArgs += @("--min-year", [string]$MinYear)
    }
    if ($null -ne $MaxYear) {
        $SmokeArgs += @("--max-year", [string]$MaxYear)
    }

    Invoke-NativeLogged -LogPath (Join-Path $RunRoot "build_manifest_smoke.log") -CommandArgs $SmokeArgs -Stage "build_smoke_manifest" -CurrentItem "smoke_manifest"
    $SmokeRows = 0
    if (Test-Path -LiteralPath $SmokeManifest -PathType Leaf) {
        $SmokeRows = (Import-Csv -LiteralPath $SmokeManifest).Count
    }
    $SmokeSummary = [ordered]@{
        finished_at = (Get-Date).ToString("o")
        mode = $Mode
        smoke_only = $true
        run_root = $RunRoot
        smoke_manifest = $SmokeManifest
        smoke_rows = $SmokeRows
        output_root = $OutputRoot
        audit_run = $false
        pre_manifest_path = $script:PreManifestPath
        heartbeat_path = $script:HeartbeatPath
        heartbeat_log_path = $script:HeartbeatLogPath
        pid_manifest_path = $script:PidManifestPath
    }
    $SmokeSummary | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $RunSummaryPath -Encoding UTF8
    Write-OperationHeartbeat -Status "completed" -Stage "smoke_only_completed" -CurrentItem $SmokeManifest -Extra @{
        smoke_rows = $SmokeRows
        run_summary_path = $RunSummaryPath
    }
    Write-Host ""
    Write-Host "Smoke manifest written:"
    Write-Host $SmokeManifest
    exit 0
}

$BuildArgs = @(
    $ManifestBuilder,
    "--minute-root", $MinuteRoot,
    "--splits-root", $SplitsRoot,
    "--output", $Manifest,
    "--mode", $Mode,
    "--chunk-size", [string]$ChunkSize,
    "--chunks-dir", $ChunksDir
)
if ($null -ne $MinYear) {
    $BuildArgs += @("--min-year", [string]$MinYear)
}
if ($null -ne $MaxYear) {
    $BuildArgs += @("--max-year", [string]$MaxYear)
}
if ($null -ne $Limit) {
    $BuildArgs += @("--limit", [string]$Limit)
}

Invoke-NativeLogged -LogPath $BuildManifestLog -CommandArgs $BuildArgs -Stage "build_manifest" -CurrentItem $Manifest

$ManifestRows = (Import-Csv -LiteralPath $Manifest).Count
if ($ManifestRows -eq 0) {
    throw "Manifest has zero rows: $Manifest"
}

$Chunks = @(Get-ChildItem -LiteralPath $ChunksDir -Filter "*.csv" -File | Sort-Object Name)
if ($Chunks.Count -eq 0) {
    throw "No chunk files were produced under: $ChunksDir"
}

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

$ChunkIndex = 0
foreach ($Chunk in $Chunks) {
    $ChunkIndex += 1
    $ChunkLog = Join-Path $RunRoot ("materialize_{0}.log" -f $Chunk.BaseName)
    Write-Host ("[{0}/{1}] Materializing {2}" -f $ChunkIndex, $Chunks.Count, $Chunk.Name)
    Write-OperationHeartbeat -Status "running" -Stage "materialize_chunk" -CurrentItem $Chunk.Name -CurrentIndex $ChunkIndex -TotalCount $Chunks.Count -LogPath $ChunkLog -Extra @{
        manifest_rows = $ManifestRows
    }

    $MaterializeArgs = @(
        $Materializer,
        "--minute-root", $MinuteRoot,
        "--splits-root", $SplitsRoot,
        "--output-root", $OutputRoot,
        "--manifest", $Chunk.FullName
    )
    if ($Overwrite) {
        $MaterializeArgs += "--overwrite"
    }

    Invoke-NativeLogged -LogPath $ChunkLog -CommandArgs $MaterializeArgs -Stage "materialize_chunk" -CurrentItem $Chunk.Name -CurrentIndex $ChunkIndex -TotalCount $Chunks.Count
}

$OutputFiles = (Get-ChildItem -LiteralPath $OutputRoot -Recurse -Filter "*_split_normalized.parquet" -File).Count

$FinalSummary = [ordered]@{
    finished_at = (Get-Date).ToString("o")
    mode = $Mode
    run_root = $RunRoot
    manifest = $Manifest
    manifest_rows = $ManifestRows
    chunk_count = $Chunks.Count
    output_root = $OutputRoot
    output_files = $OutputFiles
    audit_run = $false
}

if ($RunAudit) {
    $AuditRoot = Join-Path $RunRoot "full_universe_split_event_audit"
    New-Item -ItemType Directory -Force -Path $AuditRoot | Out-Null
    $AuditLog = Join-Path $RunRoot "audit_full_universe_split.log"
    $AuditArgs = @(
        $AuditScript,
        "--minute-root", $MinuteRoot,
        "--splits-root", $SplitsRoot,
        "--output-root", $AuditRoot
    )

    Invoke-NativeLogged -LogPath $AuditLog -CommandArgs $AuditArgs -Stage "audit_full_universe_split" -CurrentItem $AuditRoot
    $FinalSummary["audit_run"] = $true
    $FinalSummary["audit_root"] = $AuditRoot
}

$FinalSummary | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $RunSummaryPath -Encoding UTF8
Write-OperationHeartbeat -Status "completed" -Stage "completed" -CurrentItem $RunSummaryPath -Extra @{
    manifest_rows = $ManifestRows
    chunk_count = $Chunks.Count
    output_files = $OutputFiles
    run_summary_path = $RunSummaryPath
}

Write-Host ""
Write-Host "Completed."
Write-Host ("Run root: {0}" -f $RunRoot)
Write-Host ("Manifest rows: {0}" -f $ManifestRows)
Write-Host ("Chunks: {0}" -f $Chunks.Count)
Write-Host ("Output root: {0}" -f $OutputRoot)
Write-Host ("Output files now present: {0}" -f $OutputFiles)
Write-Host ("Summary: {0}" -f $RunSummaryPath)
