<# 
Clone D:\quotes into E:\TSIS\data\quotes_ as a safe staging root.

Default mode is dry-run. Use -Run for the real copy.

Examples:
  powershell -ExecutionPolicy Bypass -File .\scripts\data_ops\clone_quotes_to_staging.ps1

  powershell -ExecutionPolicy Bypass -File .\scripts\data_ops\clone_quotes_to_staging.ps1 -Run

  powershell -ExecutionPolicy Bypass -File .\scripts\data_ops\clone_quotes_to_staging.ps1 -Run -AllowNonEmptyTarget

  powershell -ExecutionPolicy Bypass -File .\scripts\data_ops\clone_quotes_to_staging.ps1 -Run -AllowNonEmptyTarget -ChunkByTicker -ThreadCount 64 -Retries 2 -WaitSeconds 2 -HeartbeatSeconds 30

  powershell -ExecutionPolicy Bypass -File .\scripts\data_ops\clone_quotes_to_staging.ps1 -Run -AllowNonEmptyTarget -ChunkByTicker -StartAtTicker APEX -ThreadCount 64 -Retries 2 -WaitSeconds 2 -HeartbeatSeconds 30

  powershell -ExecutionPolicy Bypass -File .\scripts\data_ops\clone_quotes_to_staging.ps1 -Run -SubPath "SGC\year=2013\month=11\day=04"

  powershell -ExecutionPolicy Bypass -File .\scripts\monitor_long_running_operation.ps1 -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_clone" -Watch
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$SourceRoot = "D:\quotes",

    [Parameter()]
    [string]$TargetRoot = "E:\TSIS\data\quotes_",

    [Parameter()]
    [string]$LogRoot = "E:\TSIS\data\data_ops_manifests\quotes_clone",

    [Parameter()]
    [string[]]$SubPath = @(),

    [Parameter()]
    [switch]$Run,

    [Parameter()]
    [switch]$AllowNonEmptyTarget,

    [Parameter()]
    [switch]$ChunkByTicker,

    [Parameter()]
    [ValidateRange(0, 100000)]
    [int]$MaxTickerChunks = 0,

    [Parameter()]
    [string]$StartAtTicker = "",

    [Parameter()]
    [switch]$VerboseFileList,

    [Parameter()]
    [switch]$Unbuffered,

    [Parameter()]
    [ValidateRange(1, 128)]
    [int]$ThreadCount = 32,

    [Parameter()]
    [ValidateRange(0, 100000)]
    [int]$Retries = 3,

    [Parameter()]
    [ValidateRange(0, 3600)]
    [int]$WaitSeconds = 5,

    [Parameter()]
    [ValidateRange(10, 3600)]
    [int]$HeartbeatSeconds = 60
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$scriptStartedAtUtc = (Get-Date).ToUniversalTime()
$scriptPath = $MyInvocation.MyCommand.Path

function Get-NormalizedPath {
    param([Parameter(Mandatory = $true)][string]$PathValue)
    return [System.IO.Path]::GetFullPath($PathValue).TrimEnd("\")
}

function Assert-SourceRoot {
    param([Parameter(Mandatory = $true)][string]$PathValue)

    $normalized = Get-NormalizedPath -PathValue $PathValue
    if (-not (Test-Path -LiteralPath $normalized -PathType Container)) {
        throw "Source root does not exist: $normalized"
    }
    return (Get-Item -LiteralPath $normalized).FullName.TrimEnd("\")
}

function Assert-SafeTargetRoot {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$PathValue
    )

    $normalized = Get-NormalizedPath -PathValue $PathValue
    $forbiddenLiveQuotesRoot = Get-NormalizedPath -PathValue "E:\TSIS\data\quotes"

    if ($normalized -ieq $forbiddenLiveQuotesRoot) {
        throw "Refusing to use live quotes root as target: $normalized"
    }
    if ((Split-Path -Leaf $normalized) -ne "quotes_") {
        throw "Target root must end in quotes_ for this staging operation: $normalized"
    }
    if ($normalized -ieq $Source) {
        throw "Source and target resolve to the same path: $normalized"
    }

    $targetParent = Split-Path -Parent $normalized
    if (-not (Test-Path -LiteralPath $targetParent -PathType Container)) {
        throw "Target parent does not exist: $targetParent"
    }

    New-Item -ItemType Directory -Force -Path $normalized | Out-Null
    return (Get-Item -LiteralPath $normalized).FullName.TrimEnd("\")
}

function Test-DirectoryHasAnyEntry {
    param([Parameter(Mandatory = $true)][string]$PathValue)

    $firstEntry = Get-ChildItem -LiteralPath $PathValue -Force -ErrorAction Stop | Select-Object -First 1
    return $null -ne $firstEntry
}

function Quote-Argument {
    param([Parameter(Mandatory = $true)][string]$Value)

    if ($Value -match "\s") {
        return '"' + $Value.Replace('"', '\"') + '"'
    }
    return $Value
}

function Resolve-SafeRelativeSubPath {
    param([Parameter(Mandatory = $true)][string]$PathValue)

    $clean = $PathValue.Trim().Trim("\", "/")
    if ([string]::IsNullOrWhiteSpace($clean)) {
        throw "SubPath cannot be empty."
    }
    if ([System.IO.Path]::IsPathRooted($clean)) {
        throw "SubPath must be relative, not rooted: $PathValue"
    }
    $parts = $clean -split "[\\/]+"
    foreach ($part in $parts) {
        if ($part -eq "." -or $part -eq ".." -or [string]::IsNullOrWhiteSpace($part)) {
            throw "SubPath contains an unsafe segment: $PathValue"
        }
    }
    return ($parts -join "\")
}

function Write-JsonAtomic {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object]$Payload,
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
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object]$Payload,
        [int]$Depth = 8
    )
    $dir = Split-Path -Parent $Path
    if (-not [string]::IsNullOrWhiteSpace($dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    Add-Content -LiteralPath $Path -Encoding UTF8 -Value ($Payload | ConvertTo-Json -Compress -Depth $Depth)
}

function Get-GitSnapshot {
    $repoRoot = "C:\TSIS_Data"
    $snapshot = [ordered]@{
        branch = $null
        commit = $null
        dirty_state = "unknown"
    }
    try {
        $snapshot.branch = (& git -C $repoRoot rev-parse --abbrev-ref HEAD 2>$null)
        $snapshot.commit = (& git -C $repoRoot rev-parse HEAD 2>$null)
        $dirty = (& git -C $repoRoot status --porcelain 2>$null)
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

function Write-CloneHeartbeat {
    param(
        [string]$Status,
        [string]$Stage,
        [string]$CurrentItem = "",
        [int]$CurrentIndex = 0,
        [int]$TotalCount = 0,
        [Nullable[int]]$ActivePid = $null,
        [string]$ActiveSource = "",
        [string]$ActiveTarget = "",
        [hashtable]$Extra = @{}
    )
    if ([string]::IsNullOrWhiteSpace($script:heartbeatPath)) {
        return
    }
    $nowUtc = (Get-Date).ToUniversalTime()
    $perf = Get-ProcessPerfSnapshot -ProcessId $ActivePid
    $logInfo = [ordered]@{
        log_path = $script:robocopyLog
        log_size_bytes = $null
        log_last_write_utc = $null
    }
    if (Test-Path -LiteralPath $script:robocopyLog -PathType Leaf) {
        $logItem = Get-Item -LiteralPath $script:robocopyLog
        $logInfo.log_size_bytes = $logItem.Length
        $logInfo.log_last_write_utc = $logItem.LastWriteTimeUtc.ToString("o")
    }
    $payload = [ordered]@{
        run_id = $script:runId
        observed_at_utc = $nowUtc.ToString("o")
        status = $Status
        stage = $Stage
        elapsed_seconds = [Math]::Round(($nowUtc - $scriptStartedAtUtc).TotalSeconds, 1)
        wrapper_pid = $PID
        active_pid = $ActivePid
        current_item = $CurrentItem
        current_index = $CurrentIndex
        total_count = $TotalCount
        source_root = $script:source
        target_root = $script:target
        active_source = $ActiveSource
        active_target = $ActiveTarget
        output_drive_free_gb = Get-DriveFreeGbForPath -PathValue $script:target
        physical_counting_policy = "no recursive target counting during million-file clone; use process IO, robocopy log and final summary"
    }
    foreach ($key in $perf.Keys) { $payload[$key] = $perf[$key] }
    foreach ($key in $logInfo.Keys) { $payload[$key] = $logInfo[$key] }
    foreach ($key in $Extra.Keys) { $payload[$key] = $Extra[$key] }
    Write-JsonAtomic -Path $script:heartbeatPath -Payload $payload
    Add-JsonLine -Path $script:heartbeatLogPath -Payload $payload
}

$script:source = Assert-SourceRoot -PathValue $SourceRoot
$script:target = Assert-SafeTargetRoot -Source $script:source -PathValue $TargetRoot
$targetWasNonEmpty = Test-DirectoryHasAnyEntry -PathValue $script:target

if ($Run -and $targetWasNonEmpty -and -not $AllowNonEmptyTarget) {
    throw "Target already has content: $script:target. Re-run with -AllowNonEmptyTarget if this is an intentional resume/update."
}

New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
$logRootItem = Get-Item -LiteralPath $LogRoot
$script:runId = "quotes_clone_to_staging_{0}" -f (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$script:robocopyLog = Join-Path $logRootItem.FullName ("{0}.robocopy.log" -f $script:runId)
$manifestPath = Join-Path $logRootItem.FullName ("{0}.manifest.json" -f $script:runId)
$preManifestPath = Join-Path $logRootItem.FullName ("{0}.pre_manifest.json" -f $script:runId)
$script:heartbeatPath = Join-Path $logRootItem.FullName ("{0}.heartbeat.json" -f $script:runId)
$script:heartbeatLogPath = Join-Path $logRootItem.FullName ("{0}.heartbeat.jsonl" -f $script:runId)
$pidManifestPath = Join-Path $logRootItem.FullName ("{0}.pids.json" -f $script:runId)
$monitorScript = "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\monitor_long_running_operation.ps1"
$monitorCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$monitorScript`" -RunRoot `"$($logRootItem.FullName)`" -RunId `"$($script:runId)`" -Compact -Watch"

$copyPairs = @()
if ($SubPath.Count -gt 0) {
    if ($ChunkByTicker) {
        throw "-ChunkByTicker cannot be combined with -SubPath. Use one scope mode."
    }
    if (-not [string]::IsNullOrWhiteSpace($StartAtTicker)) {
        throw "-StartAtTicker cannot be combined with -SubPath. Use -ChunkByTicker."
    }
    foreach ($item in $SubPath) {
        $relative = Resolve-SafeRelativeSubPath -PathValue $item
        $pairSource = Join-Path $script:source $relative
        if (-not (Test-Path -LiteralPath $pairSource -PathType Container)) {
            throw "SubPath does not exist under source root: $pairSource"
        }
        $copyPairs += [ordered]@{
            relative_subpath = $relative
            source = (Get-Item -LiteralPath $pairSource).FullName.TrimEnd("\")
            target = (Join-Path $script:target $relative)
        }
    }
}
elseif ($ChunkByTicker) {
    $tickerDirs = @(Get-ChildItem -LiteralPath $script:source -Directory -Force |
        Sort-Object Name)
    if (-not [string]::IsNullOrWhiteSpace($StartAtTicker)) {
        $startTicker = $StartAtTicker.Trim().ToUpperInvariant()
        $exactStart = @($tickerDirs | Where-Object { $_.Name -ieq $startTicker })
        if ($exactStart.Count -eq 0) {
            throw "StartAtTicker was not found under source root: $startTicker"
        }
        $tickerDirs = @($tickerDirs | Where-Object { [StringComparer]::OrdinalIgnoreCase.Compare($_.Name, $startTicker) -ge 0 })
    }
    if ($MaxTickerChunks -gt 0) {
        $tickerDirs = @($tickerDirs | Select-Object -First $MaxTickerChunks)
    }
    if ($tickerDirs.Count -eq 0) {
        throw "No ticker directories found under source root: $script:source"
    }
    foreach ($tickerDir in $tickerDirs) {
        $relative = $tickerDir.Name
        $copyPairs += [ordered]@{
            relative_subpath = $relative
            source = $tickerDir.FullName.TrimEnd("\")
            target = (Join-Path $script:target $relative)
        }
    }
}
else {
    $copyPairs += [ordered]@{
        relative_subpath = $null
        source = $script:source
        target = $script:target
    }
}

$baseRobocopyOptions = @(
    "/E",
    "/MT:$ThreadCount",
    "/R:$Retries",
    "/W:$WaitSeconds",
    "/FFT",
    "/XJ",
    "/COPY:DAT",
    "/DCOPY:DAT",
    "/IT",
    "/BYTES",
    "/NP",
    "/TEE"
)

if (-not $VerboseFileList) {
    $baseRobocopyOptions += "/NFL"
    $baseRobocopyOptions += "/NDL"
}

if ($Unbuffered) {
    $baseRobocopyOptions += "/J"
}

if (-not $Run) {
    $baseRobocopyOptions += "/L"
}

$mode = if ($Run) { "copy" } else { "dry_run" }
if ($SubPath.Count -gt 0) {
    $mode = "${mode}_scoped"
}
elseif ($ChunkByTicker) {
    $mode = "${mode}_ticker_chunks"
}
$startedAtUtc = (Get-Date).ToUniversalTime().ToString("o")

$preManifest = [ordered]@{
    run_id = $script:runId
    status = "starting"
    created_at_utc = $startedAtUtc
    script_path = $scriptPath
    command_line = [Environment]::CommandLine
    cwd = (Get-Location).Path
    host = $env:COMPUTERNAME
    user = [Environment]::UserName
    wrapper_pid = $PID
    git = Get-GitSnapshot
    mode = $mode
    dry_run = -not [bool]$Run
    source_root = $script:source
    target_root = $script:target
    scoped_subpaths = @($SubPath)
    chunk_by_ticker = [bool]$ChunkByTicker
    max_ticker_chunks = $MaxTickerChunks
    start_at_ticker = if ([string]::IsNullOrWhiteSpace($StartAtTicker)) { $null } else { $StartAtTicker.Trim().ToUpperInvariant() }
    copy_pairs = @($copyPairs)
    log_root = $logRootItem.FullName
    robocopy_log = $script:robocopyLog
    manifest_path = $manifestPath
    pre_manifest_path = $preManifestPath
    heartbeat_path = $script:heartbeatPath
    heartbeat_log_path = $script:heartbeatLogPath
    pid_manifest_path = $pidManifestPath
    heartbeat_seconds = $HeartbeatSeconds
    target_was_non_empty = [bool]$targetWasNonEmpty
    allow_non_empty_target = [bool]$AllowNonEmptyTarget
    thread_count = $ThreadCount
    retries = $Retries
    wait_seconds = $WaitSeconds
    verbose_file_list = [bool]$VerboseFileList
    unbuffered = [bool]$Unbuffered
    expected_scope = if ($SubPath.Count -gt 0) { "scoped subpaths only" } elseif ($ChunkByTicker) { "top-level ticker chunks under source root" } else { "full source tree clone/update into staging target" }
    resume_policy = "rerun with -Run -AllowNonEmptyTarget against the same target; robocopy skips unchanged files under copy semantics"
    overwrite_policy = "changed files inside target may be overwritten; no /MIRROR or /PURGE is used"
    success_rule = "robocopy exit codes 0-7 are success; >=8 is failure"
    monitor_command = $monitorCommand
}
Write-JsonAtomic -Path $preManifestPath -Payload $preManifest
Write-JsonAtomic -Path $pidManifestPath -Payload ([ordered]@{
    run_id = $script:runId
    observed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    wrapper_pid = $PID
    active_pid = $null
    active_stage = "startup"
})
Write-CloneHeartbeat -Status "running" -Stage "startup" -Extra @{
    monitor_command = $monitorCommand
}

Write-Host "TSIS quotes staging clone"
Write-Host "Run ID: $script:runId"
Write-Host "Mode: $mode"
Write-Host "Source: $script:source"
Write-Host "Target: $script:target"
if ($SubPath.Count -gt 0) {
    Write-Host "Scoped subpaths:"
    foreach ($pair in $copyPairs) {
        Write-Host "  - $($pair.relative_subpath)"
    }
}
elseif ($ChunkByTicker) {
    Write-Host "Ticker chunks: $($copyPairs.Count)"
    if (-not [string]::IsNullOrWhiteSpace($StartAtTicker)) {
        Write-Host "Start at ticker: $($StartAtTicker.Trim().ToUpperInvariant())"
    }
}
Write-Host "Log: $script:robocopyLog"
Write-Host "Manifest: $manifestPath"
Write-Host "Pre-manifest: $preManifestPath"
Write-Host "Heartbeat: $script:heartbeatPath"
Write-Host "PID manifest: $pidManifestPath"
Write-Host "Monitor command:"
Write-Host "  $monitorCommand"
Write-Host "Robocopy success convention: exit codes 0-7 are success; >=8 is failure."

$pairResults = @()
$robocopyExitCode = 0
$commandText = @()
for ($i = 0; $i -lt $copyPairs.Count; $i++) {
    $pair = $copyPairs[$i]
    $logOption = if ($i -eq 0) { "/LOG:$script:robocopyLog" } else { "/LOG+:$script:robocopyLog" }
    $robocopyArgs = @($pair.source, $pair.target) + $baseRobocopyOptions + @($logOption)
    $commandText += "robocopy " + (($robocopyArgs | ForEach-Object { Quote-Argument -Value ([string]$_) }) -join " ")

    Write-Host ""
    if ($null -ne $pair.relative_subpath) {
        Write-Host "Running scoped copy: $($pair.relative_subpath)"
    }

    Write-CloneHeartbeat -Status "running" -Stage "robocopy_pair_start" -CurrentItem ([string]$pair.relative_subpath) -CurrentIndex ($i + 1) -TotalCount $copyPairs.Count -ActiveSource $pair.source -ActiveTarget $pair.target -Extra @{
        robocopy_args = @($robocopyArgs)
    }
    $proc = Start-Process -FilePath "robocopy.exe" -ArgumentList $robocopyArgs -PassThru -NoNewWindow
    Write-JsonAtomic -Path $pidManifestPath -Payload ([ordered]@{
        run_id = $script:runId
        observed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        wrapper_pid = $PID
        active_pid = $proc.Id
        active_stage = "robocopy"
        source = $pair.source
        target = $pair.target
        robocopy_log = $script:robocopyLog
    })
    while (-not $proc.HasExited) {
        Write-CloneHeartbeat -Status "running" -Stage "robocopy" -CurrentItem ([string]$pair.relative_subpath) -CurrentIndex ($i + 1) -TotalCount $copyPairs.Count -ActivePid $proc.Id -ActiveSource $pair.source -ActiveTarget $pair.target
        Start-Sleep -Seconds $HeartbeatSeconds
        $proc.Refresh()
    }
    $proc.WaitForExit()
    $proc.Refresh()
    $pairExitCode = [int]$proc.ExitCode
    Write-CloneHeartbeat -Status "running" -Stage "robocopy_pair_finished" -CurrentItem ([string]$pair.relative_subpath) -CurrentIndex ($i + 1) -TotalCount $copyPairs.Count -ActivePid $proc.Id -ActiveSource $pair.source -ActiveTarget $pair.target -Extra @{
        robocopy_exit_code = $pairExitCode
    }
    if ($pairExitCode -gt $robocopyExitCode) {
        $robocopyExitCode = $pairExitCode
    }
    $pairResults += [ordered]@{
        relative_subpath = $pair.relative_subpath
        source = $pair.source
        target = $pair.target
        robocopy_pid = $proc.Id
        robocopy_exit_code = $pairExitCode
        robocopy_success = [bool]($pairExitCode -le 7)
    }
}
$endedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
$robocopySucceeded = $robocopyExitCode -le 7

$manifest = [ordered]@{
    run_id = $script:runId
    mode = $mode
    source_root = $script:source
    target_root = $script:target
    scoped_subpaths = @($SubPath)
    chunk_by_ticker = [bool]$ChunkByTicker
    max_ticker_chunks = $MaxTickerChunks
    start_at_ticker = if ([string]::IsNullOrWhiteSpace($StartAtTicker)) { $null } else { $StartAtTicker.Trim().ToUpperInvariant() }
    target_was_non_empty = [bool]$targetWasNonEmpty
    allow_non_empty_target = [bool]$AllowNonEmptyTarget
    thread_count = $ThreadCount
    retries = $Retries
    wait_seconds = $WaitSeconds
    verbose_file_list = [bool]$VerboseFileList
    unbuffered = [bool]$Unbuffered
    started_at_utc = $startedAtUtc
    ended_at_utc = $endedAtUtc
    robocopy_exit_code = $robocopyExitCode
    robocopy_success = [bool]$robocopySucceeded
    robocopy_pair_results = @($pairResults)
    robocopy_success_rule = "0-7 success, >=8 failure"
    copy_policy = [ordered]@{
        deletes_target_extra_files = $false
        uses_mirror = $false
        uses_purge = $false
        overwrites_changed_files_inside_target = [bool]$Run
        preserves_existing_live_quotes_root = $true
        live_quotes_root = "E:\TSIS\data\quotes"
    }
    robocopy_command = @($commandText)
    robocopy_log = $script:robocopyLog
    pre_manifest_path = $preManifestPath
    heartbeat_path = $script:heartbeatPath
    heartbeat_log_path = $script:heartbeatLogPath
    pid_manifest_path = $pidManifestPath
    monitor_command = $monitorCommand
    manifest_path = $manifestPath
}

$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
Write-CloneHeartbeat -Status $(if ($robocopySucceeded) { "completed" } else { "failed" }) -Stage "final_manifest_written" -Extra @{
    robocopy_exit_code = $robocopyExitCode
    manifest_path = $manifestPath
}

if (-not $robocopySucceeded) {
    Write-Error "Robocopy failed with exit code $robocopyExitCode. See log: $script:robocopyLog"
    exit $robocopyExitCode
}

if ($Run) {
    Write-Host "Copy completed or resumed successfully under robocopy success semantics."
} else {
    Write-Host "Dry-run completed. No files were copied. Review the robocopy summary before running with -Run."
}

exit 0
