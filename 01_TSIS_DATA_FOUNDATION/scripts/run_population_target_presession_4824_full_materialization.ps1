param(
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,
    [int]$HeartbeatSeconds = 10,
    [int]$Threads = 4,
    [string]$MemoryLimit = '12GB'
)

$ErrorActionPreference = 'Stop'
$runId = Split-Path -Leaf $OutputRoot
$builderPath = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\materialize_population_target_presession_4824_candidate.py'
$validatorPath = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\validate_population_target_presession_4824_candidate.py'
$monitorPath = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\monitor_population_target_presession_4824_materialization.ps1'
$configPath = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\population_target_presession_4824_audit_v0_1.json'
$masterRoot = 'G:\TSIS\data\data_foundation_outputs\master_daily_table\master_daily_table_v0_1'
$instrumentMaster = 'G:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet'
$fundamentalsRoot = 'G:\TSIS\data\data_foundation_outputs\fundamentals_asof_table\fundamentals_asof_table_v0_1'
$marketCalendar = 'G:\TSIS\data\data_foundation_outputs\market_calendar\market_calendar_v0_1.parquet'

$candidateParquet = Join-Path $OutputRoot 'population_target_presession_4824_candidate_v0_1.parquet'
$candidateManifest = Join-Path $OutputRoot 'population_target_presession_4824_candidate_v0_1_manifest.json'
$validationJson = Join-Path $OutputRoot 'population_target_presession_4824_candidate_validation_v0_1.json'
$preManifestPath = Join-Path $OutputRoot 'pre_manifest.json'
$pidManifestPath = Join-Path $OutputRoot 'pid_manifest.json'
$heartbeatPath = Join-Path $OutputRoot 'heartbeat_latest.json'
$heartbeatJsonlPath = Join-Path $OutputRoot 'heartbeat.jsonl'
$materializeStdout = Join-Path $OutputRoot 'materialize_stdout.log'
$materializeStderr = Join-Path $OutputRoot 'materialize_stderr.log'
$validateStdout = Join-Path $OutputRoot 'validate_stdout.log'
$validateStderr = Join-Path $OutputRoot 'validate_stderr.log'
$finalManifestPath = Join-Path $OutputRoot 'final_manifest.json'
$spillPath = Join-Path $OutputRoot 'duckdb_spill'
$monitorCommand = "powershell -NoProfile -File `"$monitorPath`" -OutputRoot `"$OutputRoot`" -Compact -IntervalSeconds 10"

function Write-AtomicJson {
    param([string]$Path, [object]$Payload)
    $json = $Payload | ConvertTo-Json -Depth 30
    $temporary = "$Path.$PID.$([guid]::NewGuid().ToString('N')).tmp"
    [System.IO.File]::WriteAllText($temporary, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    if (Test-Path -LiteralPath $Path) {
        $backup = "$Path.$PID.bak"
        [System.IO.File]::Replace($temporary, $Path, $backup, $true)
        if (Test-Path -LiteralPath $backup) { Remove-Item -LiteralPath $backup -Force }
    } else {
        [System.IO.File]::Move($temporary, $Path)
    }
}

function Get-FileSha256 {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-OutputBytes {
    $bytes = 0L
    if (Test-Path -LiteralPath $OutputRoot) {
        Get-ChildItem -LiteralPath $OutputRoot -File -ErrorAction SilentlyContinue | ForEach-Object { $bytes += $_.Length }
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
        [string]$CurrentOutput,
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
        progress_reason = 'total_known_after_single_parquet_materialization'
        current_output = $CurrentOutput
        source_root = $masterRoot
        target_root = $OutputRoot
        output_bytes = Get-OutputBytes
        output_free_gb = [math]::Round($drive.Free / 1GB, 3)
        last_error = $LastError
    }
    try {
        Write-AtomicJson -Path $heartbeatPath -Payload $payload
    } catch {
        Add-Content -LiteralPath (Join-Path $OutputRoot 'heartbeat_write_errors.log') -Value ("$([datetime]::UtcNow.ToString('o')) $($_.Exception.Message)") -Encoding utf8 -ErrorAction SilentlyContinue
    }
    try {
        Add-Content -LiteralPath $heartbeatJsonlPath -Value ($payload | ConvertTo-Json -Compress -Depth 10) -Encoding utf8
    } catch {
        Add-Content -LiteralPath (Join-Path $OutputRoot 'heartbeat_write_errors.log') -Value ("$([datetime]::UtcNow.ToString('o')) JSONL $($_.Exception.Message)") -Encoding utf8 -ErrorAction SilentlyContinue
    }
}

function Invoke-GovernedChild {
    param(
        [string]$Stage,
        [string[]]$Arguments,
        [string]$StdoutPath,
        [string]$StderrPath,
        [datetime]$StartedAt,
        [string]$CurrentOutput
    )
    $process = Start-Process -FilePath 'python' -ArgumentList $Arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $StdoutPath -RedirectStandardError $StderrPath
    $pidPayload = [ordered]@{
        run_id = $runId
        wrapper_pid = $PID
        child_pid = $process.Id
        child_process_name = 'python'
        child_command_summary = 'python ' + (($Arguments | ForEach-Object { '"' + $_ + '"' }) -join ' ')
        started_at_utc = $StartedAt.ToString('o')
        current_stage = $Stage
        wrapper_expected_alive = $true
        child_expected_alive = $true
    }
    Write-AtomicJson -Path $pidManifestPath -Payload $pidPayload
    while (-not $process.HasExited) {
        Write-Heartbeat -Status 'running' -Stage $Stage -StartedAt $StartedAt -ChildPid $process.Id -ChildAlive $true -CurrentOutput $CurrentOutput
        Start-Sleep -Seconds $HeartbeatSeconds
        $process.Refresh()
    }
    $process.WaitForExit()
    $process.Refresh()
    return [int]$process.ExitCode
}

if (Test-Path -LiteralPath $OutputRoot) {
    $existing = Get-ChildItem -LiteralPath $OutputRoot -Force -ErrorAction SilentlyContinue
    if ($existing) { throw "Refusing non-empty output root: $OutputRoot" }
} else {
    New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
}
New-Item -ItemType Directory -Path $spillPath -Force | Out-Null

$startedAt = [datetime]::UtcNow
$gitBranch = (& git -C 'C:\TSIS_Data' branch --show-current 2>$null)
$gitCommit = (& git -C 'C:\TSIS_Data' rev-parse HEAD 2>$null)
$gitDirty = [bool]((& git -C 'C:\TSIS_Data' status --porcelain 2>$null))
$materializeArguments = @(
    $builderPath,
    '--config', $configPath,
    '--master-daily-root', $masterRoot,
    '--instrument-master', $instrumentMaster,
    '--fundamentals-root', $fundamentalsRoot,
    '--market-calendar', $marketCalendar,
    '--output-parquet', $candidateParquet,
    '--share-policy', 'S1_DILUTED_FIRST',
    '--ttl-days', '180',
    '--threads', [string]$Threads,
    '--memory-limit', $MemoryLimit,
    '--temp-directory', $spillPath
)
$validateArguments = @(
    $validatorPath,
    '--candidate-parquet', $candidateParquet,
    '--candidate-manifest', $candidateManifest,
    '--fundamentals-root', $fundamentalsRoot,
    '--output-json', $validationJson
)
$preManifest = [ordered]@{
    run_id = $runId
    status = 'starting'
    created_at_utc = $startedAt.ToString('o')
    builder_path = $builderPath
    builder_sha256 = Get-FileSha256 $builderPath
    validator_path = $validatorPath
    validator_sha256 = Get-FileSha256 $validatorPath
    config_path = $configPath
    config_sha256 = Get-FileSha256 $configPath
    cwd = 'C:\TSIS_Data'
    host = $env:COMPUTERNAME
    user = $env:USERNAME
    parent_pid = $PID
    wrapper_pid = $PID
    git_branch = $gitBranch
    git_commit = $gitCommit
    git_dirty_state = $gitDirty
    mode = 'full_experimental_materialization_and_validation'
    dry_run = $false
    input_roots = @($masterRoot, $instrumentMaster, $fundamentalsRoot, $marketCalendar)
    output_root = $OutputRoot
    candidate_parquet = $candidateParquet
    validation_json = $validationJson
    log_roots = @($materializeStdout, $materializeStderr, $validateStdout, $validateStderr)
    expected_scope = '7,369,699 daily_raw parent ticker-session rows'
    binding = 'S1_DILUTED_FIRST x SHARES_TTL_180D'
    resume_policy = 'new_run_id_no_in_place_resume'
    overwrite_policy = 'refuse_non_empty_output_root'
    success_criteria = 'materializer exit 0; validator exit 0; validation gate PASS'
    monitor_command = $monitorCommand
}
Write-AtomicJson -Path $preManifestPath -Payload $preManifest
Write-Heartbeat -Status 'starting' -Stage 'LAUNCH' -StartedAt $startedAt -ChildPid 0 -ChildAlive $false -CurrentOutput $candidateParquet

Write-Output "run_id=$runId"
Write-Output 'mode=full_experimental_materialization_and_validation'
Write-Output "input_root=$masterRoot"
Write-Output "output_root=$OutputRoot"
Write-Output "pre_manifest=$preManifestPath"
Write-Output "heartbeat=$heartbeatPath"
Write-Output "pid_manifest=$pidManifestPath"
Write-Output "monitor_command=$monitorCommand"
Write-Output 'success_rule=materializer_exit_0_validator_exit_0_validation_gate_PASS'
Write-Output 'resume_policy=new_run_id_no_in_place_resume'

$materializeExit = 1
$validateExit = 1
$status = 'FAILED'
$failure = $null
try {
    $materializeExit = Invoke-GovernedChild -Stage 'MATERIALIZE' -Arguments $materializeArguments -StdoutPath $materializeStdout -StderrPath $materializeStderr -StartedAt $startedAt -CurrentOutput $candidateParquet
    if ($materializeExit -ne 0) { throw "materializer_exit_code=$materializeExit" }
    $validateExit = Invoke-GovernedChild -Stage 'VALIDATE' -Arguments $validateArguments -StdoutPath $validateStdout -StderrPath $validateStderr -StartedAt $startedAt -CurrentOutput $validationJson
    if ($validateExit -ne 0) { throw "validator_exit_code=$validateExit" }
    $validation = Get-Content -LiteralPath $validationJson -Raw | ConvertFrom-Json
    if ($validation.validation_gate -ne 'PASS') { throw "validation_gate=$($validation.validation_gate)" }
    $status = 'COMPLETE'
} catch {
    $failure = $_.Exception.Message
} finally {
    $endedAt = [datetime]::UtcNow
    Write-Heartbeat -Status $status.ToLowerInvariant() -Stage 'FINALIZE' -StartedAt $startedAt -ChildPid 0 -ChildAlive $false -CurrentOutput $candidateParquet -LastError $failure
    $candidateSummary = $null
    if (Test-Path -LiteralPath $candidateManifest) {
        $candidateSummary = (Get-Content -LiteralPath $candidateManifest -Raw | ConvertFrom-Json).summary
    }
    $validationGate = $null
    if (Test-Path -LiteralPath $validationJson) {
        $validationGate = (Get-Content -LiteralPath $validationJson -Raw | ConvertFrom-Json).validation_gate
    }
    $final = [ordered]@{
        run_id = $runId
        final_status = $status
        started_at_utc = $startedAt.ToString('o')
        ended_at_utc = $endedAt.ToString('o')
        duration_seconds = [math]::Round(($endedAt - $startedAt).TotalSeconds, 3)
        materializer_exit_code = $materializeExit
        validator_exit_code = $validateExit
        validation_gate = $validationGate
        candidate_parquet = $candidateParquet
        candidate_sha256 = Get-FileSha256 $candidateParquet
        candidate_size_bytes = if (Test-Path -LiteralPath $candidateParquet) { (Get-Item -LiteralPath $candidateParquet).Length } else { $null }
        candidate_summary = $candidateSummary
        validation_json = $validationJson
        validation_sha256 = Get-FileSha256 $validationJson
        output_root = $OutputRoot
        failure_reason = $failure
        promotion_state = 'VALIDATED_EXPERIMENTAL_CANDIDATE_NOT_CANONICAL'
        ta3_sample_freeze_state = if ($status -eq 'COMPLETE') { 'AUTHORIZED_NEXT_STEP' } else { 'NOT_AUTHORIZED' }
    }
    Write-AtomicJson -Path $finalManifestPath -Payload $final
    Write-Output ($final | ConvertTo-Json -Depth 20)
}

if ($status -eq 'COMPLETE') { exit 0 }
exit 1
