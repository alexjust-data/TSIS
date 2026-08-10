param(
    [Parameter(Mandatory = $true)]
    [int]$BuilderPid,
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,
    [Parameter(Mandatory = $true)]
    [string]$RuntimeRoot,
    [int]$HeartbeatSeconds = 30
)

$ErrorActionPreference = 'Stop'
$config = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\trading_activity_ta3_stratified_sample_v0_1.json'
$validator = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\validate_trading_activity_ta3_stratified_sample.py'
$validation = Join-Path $OutputRoot 'independent_validation_v0_1.json'
$heartbeat = Join-Path $RuntimeRoot 'heartbeat_latest.json'
$history = Join-Path $RuntimeRoot 'heartbeat_history.jsonl'
$finalManifest = Join-Path $RuntimeRoot 'final_manifest.json'
$recoveryManifest = Join-Path $RuntimeRoot 'recovery_controller_manifest.json'
$validatorStdout = Join-Path $RuntimeRoot 'validator_stdout.log'
$validatorStderr = Join-Path $RuntimeRoot 'validator_stderr.log'
$builderStderr = Join-Path $RuntimeRoot 'builder_stderr.log'
$started = [DateTime]::UtcNow

function Write-AtomicJson {
    param([string]$Path, [object]$Payload)
    $json = $Payload | ConvertTo-Json -Depth 20
    $tmp = "$Path.tmp.$PID"
    [System.IO.File]::WriteAllText($tmp, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    for ($attempt = 1; $attempt -le 5; $attempt++) {
        try {
            Move-Item -LiteralPath $tmp -Destination $Path -Force
            return
        } catch {
            if ($attempt -eq 5) { throw }
            Start-Sleep -Milliseconds (100 * $attempt)
        }
    }
}

function Write-RecoveryHeartbeat {
    param([string]$Status, [string]$Stage)
    try {
        $files = @(Get-ChildItem -LiteralPath $OutputRoot -File -ErrorAction SilentlyContinue)
        $bytes = ($files | Measure-Object -Property Length -Sum).Sum
        if ($null -eq $bytes) { $bytes = 0 }
        $process = Get-Process -Id $BuilderPid -ErrorAction SilentlyContinue
        $payload = [ordered]@{
            observed_at_utc = [DateTime]::UtcNow.ToString('o')
            status = $Status
            stage = $Stage
            recovery_controller_pid = $PID
            child_pid = $BuilderPid
            child_alive = $null -ne $process
            child_cpu_seconds = if ($process) { [math]::Round($process.CPU, 3) } else { $null }
            child_working_set_gb = if ($process) { [math]::Round($process.WorkingSet64 / 1GB, 3) } else { $null }
            output_files = $files.Count
            output_bytes = [int64]$bytes
            output_free_gb = [math]::Round((Get-PSDrive -Name G).Free / 1GB, 2)
            last_builder_line = $null
        }
        Write-AtomicJson -Path $heartbeat -Payload $payload
        ($payload | ConvertTo-Json -Compress -Depth 20) | Add-Content -LiteralPath $history -Encoding UTF8
    } catch {
        Add-Content -LiteralPath (Join-Path $RuntimeRoot 'heartbeat_write_errors.log') -Value "[$([DateTime]::UtcNow.ToString('o'))] recovery_heartbeat_error=$($_.Exception.Message)" -Encoding UTF8
    }
}

Write-AtomicJson -Path $recoveryManifest -Payload ([ordered]@{
    recovery_status = 'ATTACHED'
    attached_at_utc = $started.ToString('o')
    recovery_controller_pid = $PID
    builder_pid = $BuilderPid
    reason = 'original wrapper stopped after stdout heartbeat lock'
    output_root = $OutputRoot
    runtime_root = $RuntimeRoot
})

while (Get-Process -Id $BuilderPid -ErrorAction SilentlyContinue) {
    Write-RecoveryHeartbeat -Status 'RUNNING' -Stage 'RECOVERY_MONITOR_BUILDER'
    Start-Sleep -Seconds $HeartbeatSeconds
}

$sampleManifest = Join-Path $OutputRoot 'sample_manifest_v0_1.json'
$builderStderrBytes = if (Test-Path -LiteralPath $builderStderr) { (Get-Item -LiteralPath $builderStderr).Length } else { 0 }
$validatorExit = $null
$validationGate = $null
if ((Test-Path -LiteralPath $sampleManifest) -and $builderStderrBytes -eq 0) {
    Write-RecoveryHeartbeat -Status 'RUNNING' -Stage 'RECOVERY_VALIDATOR'
    $validatorProcess = Start-Process -FilePath 'python' -ArgumentList @(
        $validator,
        '--config', $config,
        '--sample-root', $OutputRoot,
        '--output-json', $validation
    ) -NoNewWindow -PassThru -Wait -RedirectStandardOutput $validatorStdout -RedirectStandardError $validatorStderr
    $validatorExit = $validatorProcess.ExitCode
    if (Test-Path -LiteralPath $validation) {
        $validationGate = (Get-Content -LiteralPath $validation -Raw | ConvertFrom-Json).validation_gate
    }
}

$status = if ($validatorExit -eq 0 -and $validationGate -eq 'PASS_WITH_RESTRICTIONS') { 'COMPLETE_RECONCILED' } else { 'FAILED' }
$ended = [DateTime]::UtcNow
Write-AtomicJson -Path $finalManifest -Payload ([ordered]@{
    operation_id = 'trading_activity_ta3_stratified_sample_v0_1'
    final_status = $status
    normal_wrapper_completion = $false
    recovery_controller_used = $true
    original_wrapper_failure = 'stdout_tail_read_lock'
    builder_pid = $BuilderPid
    builder_exit_code = 'UNAVAILABLE_AFTER_WRAPPER_STOP'
    builder_stderr_bytes = $builderStderrBytes
    sample_manifest_exists = Test-Path -LiteralPath $sampleManifest
    validator_exit_code = $validatorExit
    validation_gate = $validationGate
    recovery_attached_at_utc = $started.ToString('o')
    ended_at_utc = $ended.ToString('o')
    output_root = $OutputRoot
    runtime_root = $RuntimeRoot
    sample_manifest = $sampleManifest
    independent_validation = $validation
})
Write-RecoveryHeartbeat -Status $(if ($status -eq 'COMPLETE_RECONCILED') { 'COMPLETE' } else { 'FAILED' }) -Stage 'FINAL'
if ($status -ne 'COMPLETE_RECONCILED') { exit 1 }
