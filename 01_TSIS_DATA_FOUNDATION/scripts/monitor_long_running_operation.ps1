param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,

    [string]$RunId = "",

    [int]$IntervalSeconds = 30,

    [switch]$Compact,

    [switch]$Watch
)

$ErrorActionPreference = "Stop"

function Read-JsonFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
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
        $reader = [System.IO.StreamReader]::new($stream)
        return $reader.ReadToEnd() | ConvertFrom-Json
    }
    catch {
        return $null
    }
    finally {
        if ($null -ne $reader) {
            $reader.Dispose()
        }
        elseif ($null -ne $stream) {
            $stream.Dispose()
        }
    }
}

function Get-LatestMatchingFile {
    param(
        [string]$Root,
        [string]$Pattern
    )
    $files = @(Get-ChildItem -LiteralPath $Root -Filter $Pattern -File -ErrorAction SilentlyContinue)
    if ($RunId -ne "" -and $Pattern -ne "_run_summary.json") {
        $files = @($files | Where-Object { $_.Name -like "*$RunId*" })
    }
    return $files | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
}

function Format-Optional {
    param([object]$Value)
    if ($null -eq $Value) {
        return "n/a"
    }
    if ($Value -is [string] -and [string]::IsNullOrWhiteSpace($Value)) {
        return "n/a"
    }
    return [string]$Value
}

function Get-DriveFreeGb {
    param([string]$PathValue)
    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        return $null
    }
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

function Get-ProcessPerfById {
    param([Nullable[int]]$ProcessId)
    if ($null -eq $ProcessId) {
        return $null
    }
    try {
        return Get-CimInstance Win32_PerfFormattedData_PerfProc_Process |
            Where-Object { [int]$_.IDProcess -eq [int]$ProcessId } |
            Select-Object -First 1
    }
    catch {
        return $null
    }
}

function Get-ProcessChildren {
    param([Nullable[int]]$ProcessId)
    if ($null -eq $ProcessId) {
        return @()
    }
    try {
        return @(Get-CimInstance Win32_Process |
            Where-Object { [int]$_.ParentProcessId -eq [int]$ProcessId } |
            Select-Object ProcessId,ParentProcessId,Name,CommandLine)
    }
    catch {
        return @()
    }
}

function Get-AliveProcess {
    param([Nullable[int]]$ProcessId)
    if ($null -eq $ProcessId) {
        return $false
    }
    try {
        $proc = Get-Process -Id ([int]$ProcessId) -ErrorAction Stop
        return (-not $proc.HasExited)
    }
    catch {
        return $false
    }
}

function Get-StatusSnapshot {
    param([string]$Root)

    if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
        throw "RunRoot does not exist: $Root"
    }

    $heartbeatFile = if (Test-Path -LiteralPath (Join-Path $Root "heartbeat_latest.json") -PathType Leaf) {
        Get-Item -LiteralPath (Join-Path $Root "heartbeat_latest.json")
    } else { Get-LatestMatchingFile -Root $Root -Pattern "*.heartbeat.json" }
    $preManifestFile = if (Test-Path -LiteralPath (Join-Path $Root "pre_manifest.json") -PathType Leaf) {
        Get-Item -LiteralPath (Join-Path $Root "pre_manifest.json")
    } else { Get-LatestMatchingFile -Root $Root -Pattern "*.pre_manifest.json" }
    $pidFile = if (Test-Path -LiteralPath (Join-Path $Root "pid_manifest.json") -PathType Leaf) {
        Get-Item -LiteralPath (Join-Path $Root "pid_manifest.json")
    } else { Get-LatestMatchingFile -Root $Root -Pattern "*.pids.json" }
    $finalManifestFile = if (Test-Path -LiteralPath (Join-Path $Root "final_manifest.json") -PathType Leaf) {
        Get-Item -LiteralPath (Join-Path $Root "final_manifest.json")
    } else { Get-LatestMatchingFile -Root $Root -Pattern "*.manifest.json" }
    $runSummaryFile = Get-LatestMatchingFile -Root $Root -Pattern "_run_summary.json"

    $heartbeat = if ($heartbeatFile -ne $null) { Read-JsonFile -Path $heartbeatFile.FullName } else { $null }
    $preManifest = if ($preManifestFile -ne $null) { Read-JsonFile -Path $preManifestFile.FullName } else { $null }
    $pids = if ($pidFile -ne $null) { Read-JsonFile -Path $pidFile.FullName } else { $null }

    $heartbeatAgeSeconds = $null
    if ($heartbeat -ne $null) {
        try {
            $observedUtc = [datetime]::Parse($heartbeat.observed_at_utc).ToUniversalTime()
            $heartbeatAgeSeconds = [Math]::Round(((Get-Date).ToUniversalTime() - $observedUtc).TotalSeconds, 1)
        }
        catch {
            $heartbeatAgeSeconds = $null
        }
    }

    $activePid = $null
    if ($heartbeat -ne $null -and $heartbeat.active_pid -ne $null) {
        $activePid = [int]$heartbeat.active_pid
    }
    $wrapperPid = $null
    if ($heartbeat -ne $null -and $heartbeat.wrapper_pid -ne $null) {
        $wrapperPid = [int]$heartbeat.wrapper_pid
    }
    elseif ($pids -ne $null -and $pids.wrapper_pid -ne $null) {
        $wrapperPid = [int]$pids.wrapper_pid
    }
    $wrapperAlive = Get-AliveProcess -ProcessId $wrapperPid
    $activeAlive = Get-AliveProcess -ProcessId $activePid
    $children = @(Get-ProcessChildren -ProcessId $activePid)
    $workerChildren = @($children | Where-Object { $_.Name -notlike "conhost*" })
    $workerPerf = $null
    $workerPid = $null
    $workerName = $null
    if ($workerChildren.Count -gt 0) {
        $workerPid = [int]$workerChildren[0].ProcessId
        $workerName = [string]$workerChildren[0].Name
        $workerPerf = Get-ProcessPerfById -ProcessId $workerPid
    }

    return [ordered]@{
        heartbeat_file = $heartbeatFile
        pre_manifest_file = $preManifestFile
        pid_file = $pidFile
        final_manifest_file = $finalManifestFile
        run_summary_file = $runSummaryFile
        heartbeat = $heartbeat
        pre_manifest = $preManifest
        pids = $pids
        heartbeat_age_seconds = $heartbeatAgeSeconds
        wrapper_pid = $wrapperPid
        wrapper_alive = $wrapperAlive
        active_pid = $activePid
        active_alive = $activeAlive
        worker_children = $workerChildren
        worker_pid = $workerPid
        worker_name = $workerName
        worker_perf = $workerPerf
    }
}

function Write-CompactStatus {
    param([string]$Root)

    $snapshot = Get-StatusSnapshot -Root $Root
    $heartbeat = $snapshot.heartbeat
    $timestamp = (Get-Date).ToString("s")
    if ($heartbeat -eq $null) {
        Write-Host ("[{0}] status=unknown stage=no_heartbeat processes=0 latest_age_sec=n/a elapsed_sec=n/a progress=unknown reason=no_heartbeat" -f $timestamp)
        return
    }

    $processCount = 0
    if ($snapshot.wrapper_alive) { $processCount += 1 }
    if ($snapshot.active_alive) { $processCount += 1 }
    if ($snapshot.worker_children -ne $null) { $processCount += @($snapshot.worker_children).Count }
    if ($heartbeat.PSObject.Properties.Name -contains "active_worker_count") {
        $processCount = [int]$heartbeat.active_worker_count
        if ($snapshot.wrapper_alive) { $processCount += 1 }
    }

    $displayStatus = Format-Optional $heartbeat.status
    $statusSuffix = ""
    $isTerminalStatus = ($heartbeat.status -eq "completed" -or $heartbeat.status -eq "failed")
    $isStaleRunning = $false
    if (-not $isTerminalStatus -and
        $heartbeat.status -eq "running" -and
        $processCount -eq 0 -and
        $snapshot.heartbeat_age_seconds -ne $null -and
        [double]$snapshot.heartbeat_age_seconds -gt 180) {
        $displayStatus = "stale_no_process"
        $statusSuffix = " raw_status=running"
        $isStaleRunning = $true
    }

    $progress = "unknown"
    $reason = ""
    if ($heartbeat.current_index -ne $null -and $heartbeat.total_count -ne $null -and [int]$heartbeat.total_count -gt 0) {
        $progress = "{0}/{1}" -f $heartbeat.current_index, $heartbeat.total_count
    }
    elseif ($heartbeat.stage -eq "build_manifest") {
        $reason = " reason=total_known_after_manifest"
    }
    else {
        $reason = " reason=total_not_reported"
    }

    $cpu = $heartbeat.process_cpu_pct
    $ioRead = $heartbeat.io_read_bytes_per_sec
    $ioWrite = $heartbeat.io_write_bytes_per_sec
    if ($null -eq $cpu) { $cpu = $heartbeat.system_cpu_percent }
    if ($null -eq $ioRead) { $ioRead = $heartbeat.io_read_Bps }
    if ($null -eq $ioWrite) { $ioWrite = $heartbeat.io_write_Bps }
    $worker = ""
    if ($snapshot.worker_perf -ne $null) {
        $cpu = $snapshot.worker_perf.PercentProcessorTime
        $ioRead = $snapshot.worker_perf.IOReadBytesPersec
        $ioWrite = $snapshot.worker_perf.IOWriteBytesPersec
        $worker = " worker={0}:{1}" -f $snapshot.worker_name, $snapshot.worker_pid
    }

    $domain = ""
    foreach ($name in @(
        "months_done", "months_planned", "repair_rows",
        "chunks_done", "chunk_count", "rows_done", "files_done",
        "bytes_done", "windows_done", "hard_fail_count",
        "epoch", "epochs_total", "train_loss", "val_loss",
        "manifest_rows", "output_files", "smoke_rows",
        "completed_blocks", "active_worker_count", "available_memory_gib",
        "process_tree_rss_gib", "pagefile_used_gib"
    )) {
        if ($heartbeat.PSObject.Properties.Name -contains $name) {
            $domain += " {0}={1}" -f $name, (Format-Optional $heartbeat.$name)
        }
    }

    Write-Host ("[{0}] status={1}{2} stage={3} processes={4} wrapper_alive={5} latest_age_sec={6} elapsed_sec={7} progress={8}{9} item={10}{11} cpu={12} io_read_Bps={13} io_write_Bps={14} output_free_GB={15}{16}" -f `
        $timestamp,
        $displayStatus,
        $statusSuffix,
        (Format-Optional $heartbeat.stage),
        $processCount,
        (Format-Optional $snapshot.wrapper_alive),
        (Format-Optional $snapshot.heartbeat_age_seconds),
        (Format-Optional $heartbeat.elapsed_seconds),
        $progress,
        $reason,
        (Format-Optional $heartbeat.current_item),
        $worker,
        (Format-Optional $cpu),
        (Format-Optional $ioRead),
        (Format-Optional $ioWrite),
        (Format-Optional $(if ($null -ne $heartbeat.output_drive_free_gb) { $heartbeat.output_drive_free_gb } else { $heartbeat.output_free_gib })),
        $domain
    )
}

function Show-Status {
    param([string]$Root)

    $snapshot = Get-StatusSnapshot -Root $Root

    Clear-Host
    Write-Host "TSIS long-running operation monitor"
    Write-Host ("Root: {0}" -f $Root)
    Write-Host ("Observed: {0}" -f (Get-Date).ToString("o"))
    if ($RunId -ne "") {
        Write-Host ("RunId filter: {0}" -f $RunId)
    }
    Write-Host ""

    $heartbeatFile = $snapshot.heartbeat_file
    $preManifestFile = $snapshot.pre_manifest_file
    $pidFile = $snapshot.pid_file
    $finalManifestFile = $snapshot.final_manifest_file
    $runSummaryFile = $snapshot.run_summary_file
    $heartbeat = $snapshot.heartbeat
    $preManifest = $snapshot.pre_manifest
    $pids = $snapshot.pids

    $preManifestDisplay = "n/a"
    $heartbeatDisplay = "n/a"
    $pidDisplay = "n/a"
    $finalDisplay = "n/a"
    $summaryDisplay = "n/a"
    if ($preManifestFile -ne $null) { $preManifestDisplay = $preManifestFile.FullName }
    if ($heartbeatFile -ne $null) { $heartbeatDisplay = $heartbeatFile.FullName }
    if ($pidFile -ne $null) { $pidDisplay = $pidFile.FullName }
    if ($finalManifestFile -ne $null) { $finalDisplay = $finalManifestFile.FullName }
    if ($runSummaryFile -ne $null) { $summaryDisplay = $runSummaryFile.FullName }

    Write-Host "Files:"
    Write-Host ("  pre-manifest: {0}" -f $preManifestDisplay)
    Write-Host ("  heartbeat:    {0}" -f $heartbeatDisplay)
    Write-Host ("  pids:         {0}" -f $pidDisplay)
    Write-Host ("  final:        {0}" -f $finalDisplay)
    Write-Host ("  summary:      {0}" -f $summaryDisplay)
    Write-Host ""

    if ($heartbeat -eq $null) {
        Write-Host "No heartbeat found yet."
        return
    }

    $heartbeatAgeSeconds = $snapshot.heartbeat_age_seconds

    $percent = "n/a"
    if ($null -ne $heartbeat.current_index -and $null -ne $heartbeat.total_count -and [int]$heartbeat.total_count -gt 0) {
        $percent = "{0:n2}%" -f (([double]$heartbeat.current_index / [double]$heartbeat.total_count) * 100.0)
    }

    $activeAlive = $snapshot.active_alive
    $wrapperAlive = $snapshot.wrapper_alive
    $workerChildren = @($snapshot.worker_children)
    $isHeartbeatFresh = $false
    if ($heartbeatAgeSeconds -ne $null -and [double]$heartbeatAgeSeconds -lt 180) {
        $isHeartbeatFresh = $true
    }

    Write-Host "Human readout:"
    if ($heartbeat.status -eq "completed") {
        Write-Host "  Estado: COMPLETADO."
    }
    elseif ($heartbeat.status -eq "failed") {
        Write-Host "  Estado: FALLADO. Revisa stderr/log y final manifest."
    }
    elseif (-not $isHeartbeatFresh -and -not $wrapperAlive -and -not $activeAlive -and $workerChildren.Count -eq 0) {
        Write-Host "  Estado: STALE / SIN PROCESO. El ultimo heartbeat dice running, pero no hay wrapper, worker ni PID activo visible."
    }
    elseif ($wrapperAlive -or $activeAlive -or $workerChildren.Count -gt 0) {
        Write-Host "  Estado: VIVO."
    }
    else {
        Write-Host "  Estado: SIN PID activo visible. Puede haber terminado o estar stale."
    }

    if ($heartbeat.stage -eq "build_manifest") {
        Write-Host "  Fase: construyendo manifest. Todavia no esta materializando parquet."
        Write-Host "  Progreso 0/0 es normal aqui: el total de chunks se conoce despues de crear el manifest."
    }
    elseif ($heartbeat.stage -eq "materialize_chunk") {
        Write-Host "  Fase: materializando chunks. Aqui current/total ya debe indicar avance."
    }
    elseif ($heartbeat.stage -like "*audit*") {
        Write-Host "  Fase: auditando resultados."
    }
    else {
        Write-Host ("  Fase: {0}" -f (Format-Optional $heartbeat.stage))
    }

    if ($isHeartbeatFresh) {
        Write-Host ("  Heartbeat: fresco ({0}s)." -f (Format-Optional $heartbeatAgeSeconds))
    }
    else {
        Write-Host ("  Heartbeat: viejo o desconocido ({0}s). Si supera 180s, revisar procesos." -f (Format-Optional $heartbeatAgeSeconds))
    }

    if ($workerChildren.Count -gt 0) {
        Write-Host "  Worker real detectado bajo el wrapper:"
        foreach ($child in $workerChildren) {
            $childPerf = Get-ProcessPerfById -ProcessId ([int]$child.ProcessId)
            if ($childPerf -ne $null) {
                Write-Host ("    PID {0} {1}: CPU={2} IO_read_Bps={3} IO_write_Bps={4}" -f $child.ProcessId, $child.Name, $childPerf.PercentProcessorTime, $childPerf.IOReadBytesPersec, $childPerf.IOWriteBytesPersec)
            }
            else {
                Write-Host ("    PID {0} {1}: perf n/a" -f $child.ProcessId, $child.Name)
            }
        }
    }
    Write-Host ""

    Write-Host "Latest heartbeat:"
    Write-Host ("  run_id:          {0}" -f (Format-Optional $heartbeat.run_id))
    Write-Host ("  status:          {0}" -f (Format-Optional $heartbeat.status))
    Write-Host ("  stage:           {0}" -f (Format-Optional $heartbeat.stage))
    Write-Host ("  observed:        {0}" -f (Format-Optional $heartbeat.observed_at_utc))
    Write-Host ("  age_seconds:     {0}" -f (Format-Optional $heartbeatAgeSeconds))
    Write-Host ("  elapsed_seconds: {0}" -f (Format-Optional $heartbeat.elapsed_seconds))
    Write-Host ("  current:         {0}/{1} ({2})" -f (Format-Optional $heartbeat.current_index), (Format-Optional $heartbeat.total_count), $percent)
    Write-Host ("  item:            {0}" -f (Format-Optional $heartbeat.current_item))
    Write-Host ("  wrapper_pid:     {0} alive={1}" -f (Format-Optional $snapshot.wrapper_pid), (Format-Optional $snapshot.wrapper_alive))
    Write-Host ("  pid:             {0} alive={1}" -f (Format-Optional $heartbeat.active_pid), (Format-Optional $heartbeat.active_pid_alive))
    Write-Host ("  cpu_pct:         {0}" -f (Format-Optional $heartbeat.process_cpu_pct))
    Write-Host ("  io_read_Bps:     {0}" -f (Format-Optional $heartbeat.io_read_bytes_per_sec))
    Write-Host ("  io_write_Bps:    {0}" -f (Format-Optional $heartbeat.io_write_bytes_per_sec))
    Write-Host ("  io_data_Bps:     {0}" -f (Format-Optional $heartbeat.io_data_bytes_per_sec))
    Write-Host ("  output_free_GB:  {0}" -f (Format-Optional $heartbeat.output_drive_free_gb))
    Write-Host ""

    if ($heartbeat.log_path -ne $null -and -not [string]::IsNullOrWhiteSpace([string]$heartbeat.log_path)) {
        $logPath = [string]$heartbeat.log_path
        Write-Host "Log:"
        Write-Host ("  path:       {0}" -f $logPath)
        if (Test-Path -LiteralPath $logPath -PathType Leaf) {
            $logItem = Get-Item -LiteralPath $logPath
            Write-Host ("  size_bytes: {0}" -f $logItem.Length)
            Write-Host ("  last_write: {0}" -f $logItem.LastWriteTimeUtc.ToString("o"))
        }
        else {
            Write-Host "  missing"
        }
        Write-Host ""
    }

    if ($pids -ne $null) {
        Write-Host "PID manifest:"
        $pids | ConvertTo-Json -Depth 6
        Write-Host ""
    }

    if ($preManifest -ne $null -and $preManifest.monitor_command -ne $null) {
        Write-Host "Monitor command:"
        Write-Host $preManifest.monitor_command
        Write-Host ""
    }

    $targetPath = $null
    if ($heartbeat.target_root -ne $null) {
        $targetPath = [string]$heartbeat.target_root
    }
    elseif ($heartbeat.output_root -ne $null) {
        $targetPath = [string]$heartbeat.output_root
    }
    if ($targetPath -ne $null) {
        $freeGb = Get-DriveFreeGb -PathValue $targetPath
        if ($freeGb -ne $null) {
            Write-Host ("Current output drive free GB: {0}" -f $freeGb)
        }
    }
}

do {
    if ($Compact) {
        Write-CompactStatus -Root $RunRoot
    }
    else {
        Show-Status -Root $RunRoot
    }
    if ($Watch) {
        Start-Sleep -Seconds $IntervalSeconds
    }
} while ($Watch)
