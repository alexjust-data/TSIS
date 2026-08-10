param(
    [Parameter(Mandatory = $true)]
    [string]$RuntimeRoot,
    [int]$HeartbeatSeconds = 5,
    [int]$Threads = 4,
    [string]$MemoryLimit = '8GB'
)

$ErrorActionPreference = 'Stop'
$runId = Split-Path -Leaf $RuntimeRoot
$scriptPath = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\audit_population_target_presession_4824_gates.py'
$monitorPath = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\monitor_population_target_presession_4824_full_audit.ps1'
$configPath = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\population_target_presession_4824_audit_v0_1.json'
$masterRoot = 'G:\TSIS\data\data_foundation_outputs\master_daily_table\master_daily_table_v0_1'
$instrumentMaster = 'G:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet'
$fundamentalsRoot = 'G:\TSIS\data\data_foundation_outputs\fundamentals_asof_table\fundamentals_asof_table_v0_1'
$legacyParquet = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\runs\backtest\population_target_pti\population_target_pti_run_01\population_target_pti.parquet'
$masterManifest = 'G:\TSIS\data\data_foundation_outputs\master_daily_table\_master_daily_table_manifest_v0_1.json'
$fundamentalsManifest = 'G:\TSIS\data\data_foundation_outputs\fundamentals_asof_table\_fundamentals_asof_table_manifest_v0_1.json'

$preManifestPath = Join-Path $RuntimeRoot 'pre_manifest.json'
$pidManifestPath = Join-Path $RuntimeRoot 'pid_manifest.json'
$heartbeatPath = Join-Path $RuntimeRoot 'heartbeat_latest.json'
$heartbeatJsonlPath = Join-Path $RuntimeRoot 'heartbeat.jsonl'
$stdoutPath = Join-Path $RuntimeRoot 'stdout.log'
$stderrPath = Join-Path $RuntimeRoot 'stderr.log'
$outputJson = Join-Path $RuntimeRoot 'population_target_presession_4824_g0_g3_full_history_v0_1.json'
$finalManifestPath = Join-Path $RuntimeRoot 'final_manifest.json'
$spillPath = Join-Path $RuntimeRoot 'duckdb_spill'
$monitorCommand = "powershell -NoProfile -File `"$monitorPath`" -RuntimeRoot `"$RuntimeRoot`" -Compact -IntervalSeconds 5"

function Write-AtomicJson {
    param([string]$Path, [object]$Payload)
    $json = $Payload | ConvertTo-Json -Depth 30
    $temporary = "$Path.$PID.$([guid]::NewGuid().ToString('N')).tmp"
    [System.IO.File]::WriteAllText($temporary, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    if (Test-Path -LiteralPath $Path) {
        $backup = "$Path.$PID.bak"
        [System.IO.File]::Replace($temporary, $Path, $backup, $true)
        if (Test-Path -LiteralPath $backup) {
            Remove-Item -LiteralPath $backup -Force
        }
    } else {
        [System.IO.File]::Move($temporary, $Path)
    }
}

function Get-FileSha256 {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-LogBytes {
    $bytes = 0L
    foreach ($path in @($stdoutPath, $stderrPath)) {
        if (Test-Path -LiteralPath $path) {
            $bytes += (Get-Item -LiteralPath $path).Length
        }
    }
    return $bytes
}

function Write-Heartbeat {
    param(
        [string]$Status,
        [string]$Stage,
        [datetime]$StartedAt,
        [int]$ChildPid,
        [bool]$ChildAlive,
        [string]$LastError = $null
    )
    $now = [datetime]::UtcNow
    $drive = Get-PSDrive -Name 'G'
    $payload = [ordered]@{
        run_id = $runId
        observed_at_utc = $now.ToString('o')
        status = $Status
        stage = $Stage
        elapsed_seconds = [math]::Round(($now - $StartedAt).TotalSeconds, 3)
        wrapper_pid = $PID
        wrapper_alive = $true
        child_pid = $ChildPid
        child_alive = $ChildAlive
        progress = 'unknown'
        progress_reason = 'single_read_only_full_history_audit_query'
        source_root = $masterRoot
        target_root = $RuntimeRoot
        output_json = $outputJson
        log_path = $stdoutPath
        log_size_bytes = Get-LogBytes
        output_free_gb = [math]::Round($drive.Free / 1GB, 3)
        last_error = $LastError
    }
    try {
        Write-AtomicJson -Path $heartbeatPath -Payload $payload
    } catch {
        Add-Content -LiteralPath (Join-Path $RuntimeRoot 'heartbeat_write_errors.log') -Value ("$([datetime]::UtcNow.ToString('o')) $($_.Exception.Message)") -Encoding utf8 -ErrorAction SilentlyContinue
    }
    try {
        Add-Content -LiteralPath $heartbeatJsonlPath -Value ($payload | ConvertTo-Json -Compress -Depth 10) -Encoding utf8
    } catch {
        Add-Content -LiteralPath (Join-Path $RuntimeRoot 'heartbeat_write_errors.log') -Value ("$([datetime]::UtcNow.ToString('o')) JSONL $($_.Exception.Message)") -Encoding utf8 -ErrorAction SilentlyContinue
    }
}

New-Item -ItemType Directory -Path $RuntimeRoot -Force | Out-Null
New-Item -ItemType Directory -Path $spillPath -Force | Out-Null

if (Test-Path -LiteralPath $pidManifestPath) {
    $oldPid = Get-Content -LiteralPath $pidManifestPath -Raw | ConvertFrom-Json
    if ($oldPid.child_pid -and (Get-Process -Id $oldPid.child_pid -ErrorAction SilentlyContinue)) {
        throw "An active child process already exists for this runtime root: $($oldPid.child_pid)"
    }
}

$startedAt = [datetime]::UtcNow
$gitBranch = (& git -C 'C:\TSIS_Data' branch --show-current 2>$null)
$gitCommit = (& git -C 'C:\TSIS_Data' rev-parse HEAD 2>$null)
$gitDirty = [bool]((& git -C 'C:\TSIS_Data' status --porcelain 2>$null))
$arguments = @(
    $scriptPath,
    '--config', $configPath,
    '--master-daily-root', $masterRoot,
    '--instrument-master', $instrumentMaster,
    '--fundamentals-root', $fundamentalsRoot,
    '--legacy-parquet', $legacyParquet,
    '--master-manifest', $masterManifest,
    '--fundamentals-manifest', $fundamentalsManifest,
    '--threads', [string]$Threads,
    '--memory-limit', $MemoryLimit,
    '--temp-directory', $spillPath,
    '--output-json', $outputJson
)
$commandLine = 'python ' + (($arguments | ForEach-Object { '"' + $_ + '"' }) -join ' ')
$preManifest = [ordered]@{
    run_id = $runId
    status = 'starting'
    created_at_utc = $startedAt.ToString('o')
    script_path = $scriptPath
    script_sha256 = Get-FileSha256 $scriptPath
    config_path = $configPath
    config_sha256 = Get-FileSha256 $configPath
    command_line = $commandLine
    cwd = 'C:\TSIS_Data'
    host = $env:COMPUTERNAME
    user = $env:USERNAME
    parent_pid = $PID
    wrapper_pid = $PID
    git_branch = $gitBranch
    git_commit = $gitCommit
    git_dirty_state = $gitDirty
    mode = 'full_history_read_only_audit'
    dry_run = $false
    input_roots = @($masterRoot, $instrumentMaster, $fundamentalsRoot, $legacyParquet)
    output_root = $RuntimeRoot
    output_json = $outputJson
    log_roots = @($stdoutPath, $stderrPath)
    manifest_paths = @($preManifestPath, $pidManifestPath, $heartbeatPath, $finalManifestPath)
    expected_scope = 'all daily_raw parent-universe instrument-ticker-sessions available in master_daily_table_v0_1'
    resume_policy = 'new_run_id_no_in_place_resume'
    overwrite_policy = 'refuse_duplicate_live_child; runtime root should be unique'
    success_criteria = 'exit_code=0 and G0=PASS and G1/G2/G3=PASS_WITH_RESTRICTIONS'
    monitor_command = $monitorCommand
}
Write-AtomicJson -Path $preManifestPath -Payload $preManifest
Write-Heartbeat -Status 'starting' -Stage 'LAUNCH' -StartedAt $startedAt -ChildPid 0 -ChildAlive $false

Write-Output "run_id=$runId"
Write-Output 'mode=full_history_read_only_audit'
Write-Output "input_root=$masterRoot"
Write-Output "output_root=$RuntimeRoot"
Write-Output "pre_manifest=$preManifestPath"
Write-Output "heartbeat=$heartbeatPath"
Write-Output "log=$stdoutPath"
Write-Output "pid_manifest=$pidManifestPath"
Write-Output "monitor_command=$monitorCommand"
Write-Output 'success_rule=exit_code_0_and_g0_pass_and_g1_g2_g3_pass_with_restrictions'
Write-Output 'resume_policy=new_run_id_no_in_place_resume'

$process = $null
$exitCode = 1
$status = 'FAILED'
$failure = $null
try {
    $process = Start-Process -FilePath 'python' -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
    $pidManifest = [ordered]@{
        run_id = $runId
        wrapper_pid = $PID
        child_pid = $process.Id
        child_process_name = 'python'
        child_command_summary = $commandLine
        started_at_utc = $startedAt.ToString('o')
        current_stage = 'G0_G3_FULL_HISTORY_AUDIT'
        wrapper_expected_alive = $true
        child_expected_alive = $true
    }
    Write-AtomicJson -Path $pidManifestPath -Payload $pidManifest
    while (-not $process.HasExited) {
        Write-Heartbeat -Status 'running' -Stage 'G0_G3_FULL_HISTORY_AUDIT' -StartedAt $startedAt -ChildPid $process.Id -ChildAlive $true
        Start-Sleep -Seconds $HeartbeatSeconds
        $process.Refresh()
    }
    $process.WaitForExit()
    $process.Refresh()
    $exitCode = [int]$process.ExitCode
    if ($exitCode -eq 0 -and (Test-Path -LiteralPath $outputJson)) {
        $status = 'COMPLETE'
    } else {
        $failure = "audit_exit_code=$exitCode output_exists=$(Test-Path -LiteralPath $outputJson)"
    }
} catch {
    $failure = $_.Exception.Message
} finally {
    $endedAt = [datetime]::UtcNow
    $childPid = if ($process) { $process.Id } else { 0 }
    Write-Heartbeat -Status $status.ToLowerInvariant() -Stage 'FINALIZE' -StartedAt $startedAt -ChildPid $childPid -ChildAlive $false -LastError $failure
    $auditPayload = $null
    if (Test-Path -LiteralPath $outputJson) {
        $auditPayload = Get-Content -LiteralPath $outputJson -Raw | ConvertFrom-Json
    }
    $finalManifest = [ordered]@{
        run_id = $runId
        final_status = $status
        started_at_utc = $startedAt.ToString('o')
        ended_at_utc = $endedAt.ToString('o')
        duration_seconds = [math]::Round(($endedAt - $startedAt).TotalSeconds, 3)
        exit_code = $exitCode
        success_rule = 'exit_code=0 and output JSON exists'
        output_root = $RuntimeRoot
        output_json = $outputJson
        output_json_sha256 = Get-FileSha256 $outputJson
        stdout_log = $stdoutPath
        stderr_log = $stderrPath
        g0 = if ($auditPayload) { $auditPayload.g0.g0_contract_gate } else { $null }
        g1 = if ($auditPayload) { $auditPayload.g1.gate } else { $null }
        g2 = if ($auditPayload) { $auditPayload.g2.gate } else { $null }
        g3 = if ($auditPayload) { $auditPayload.g3.gate } else { $null }
        selector_gate = if ($auditPayload) { $auditPayload.selector_gate } else { $null }
        warnings = @('read_only_proxy_fit_audit_only', 'no_selector_materialization', 'no_ta3_sample_freeze')
        failure_reason = $failure
        resume_instructions = 'create a new unique run_id after repairing any failed gate'
        promotion_state = 'EVIDENCE_ONLY_NOT_CANONICAL'
    }
    Write-AtomicJson -Path $finalManifestPath -Payload $finalManifest
    Write-Output ($finalManifest | ConvertTo-Json -Depth 10)
}

exit $exitCode
