param(
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,
    [Parameter(Mandatory = $true)]
    [string]$RuntimeRoot,
    [int]$Threads = 4,
    [string]$MemoryLimit = '12GB',
    [int]$HeartbeatSeconds = 30,
    [double]$MinimumFreeGB = 50
)

$ErrorActionPreference = 'Stop'
$config = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\trading_activity_ta3_stratified_sample_v0_1.json'
$builder = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\build_trading_activity_ta3_stratified_sample.py'
$validator = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\validate_trading_activity_ta3_stratified_sample.py'
$tempDirectory = Join-Path $RuntimeRoot 'duckdb_temp'
$stopFile = Join-Path $RuntimeRoot 'STOP_REQUESTED'
$stdout = Join-Path $RuntimeRoot 'builder_stdout.log'
$stderr = Join-Path $RuntimeRoot 'builder_stderr.log'
$validatorStdout = Join-Path $RuntimeRoot 'validator_stdout.log'
$validatorStderr = Join-Path $RuntimeRoot 'validator_stderr.log'
$heartbeat = Join-Path $RuntimeRoot 'heartbeat_latest.json'
$history = Join-Path $RuntimeRoot 'heartbeat_history.jsonl'
$preManifest = Join-Path $RuntimeRoot 'pre_manifest.json'
$pidManifest = Join-Path $RuntimeRoot 'pid_manifest.json'
$finalManifest = Join-Path $RuntimeRoot 'final_manifest.json'
$validation = Join-Path $OutputRoot 'independent_validation_v0_1.json'

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

function Write-Heartbeat {
    param([string]$Status, [string]$Stage, [int]$ChildPid)
    try {
        $files = if (Test-Path -LiteralPath $OutputRoot) {
            Get-ChildItem -LiteralPath $OutputRoot -File -ErrorAction SilentlyContinue
        } else { @() }
        $bytes = ($files | Measure-Object -Property Length -Sum).Sum
        if ($null -eq $bytes) { $bytes = 0 }

        $payload = [ordered]@{
            observed_at_utc = [DateTime]::UtcNow.ToString('o')
            status = $Status
            stage = $Stage
            wrapper_pid = $PID
            child_pid = $ChildPid
            output_files = @($files).Count
            output_bytes = [int64]$bytes
            output_free_gb = [math]::Round((Get-PSDrive -Name G).Free / 1GB, 2)
            last_builder_line = $null
        }
        Write-AtomicJson -Path $heartbeat -Payload $payload
        ($payload | ConvertTo-Json -Compress -Depth 20) | Add-Content -LiteralPath $history -Encoding UTF8
    } catch {
        $message = "[$([DateTime]::UtcNow.ToString('o'))] heartbeat_write_error=$($_.Exception.Message)"
        Add-Content -LiteralPath (Join-Path $RuntimeRoot 'heartbeat_write_errors.log') -Value $message -Encoding UTF8
    }
}

if ((Test-Path -LiteralPath $OutputRoot) -and (Get-ChildItem -LiteralPath $OutputRoot -Force -ErrorAction SilentlyContinue)) {
    throw "OutputRoot must not exist or must be empty: $OutputRoot"
}
if ((Test-Path -LiteralPath $RuntimeRoot) -and (Get-ChildItem -LiteralPath $RuntimeRoot -Force -ErrorAction SilentlyContinue)) {
    throw "RuntimeRoot must not exist or must be empty: $RuntimeRoot"
}
$freeGB = (Get-PSDrive -Name G).Free / 1GB
if ($freeGB -lt $MinimumFreeGB) {
    throw "Insufficient G: free space: $([math]::Round($freeGB,2)) GB < $MinimumFreeGB GB"
}

New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
New-Item -ItemType Directory -Path $RuntimeRoot -Force | Out-Null
New-Item -ItemType Directory -Path $tempDirectory -Force | Out-Null
$started = [DateTime]::UtcNow
$pre = [ordered]@{
    operation_id = 'trading_activity_ta3_stratified_sample_v0_1'
    started_at_utc = $started.ToString('o')
    output_root = $OutputRoot
    runtime_root = $RuntimeRoot
    config = $config
    config_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $config).Hash.ToLowerInvariant()
    builder = $builder
    builder_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $builder).Hash.ToLowerInvariant()
    validator = $validator
    validator_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $validator).Hash.ToLowerInvariant()
    threads = $Threads
    memory_limit = $MemoryLimit
    free_gb_at_start = [math]::Round($freeGB, 2)
    minimum_free_gb = $MinimumFreeGB
    overwrite_policy = 'NEVER'
    cooperative_stop_file = $stopFile
}
Write-AtomicJson -Path $preManifest -Payload $pre

$arguments = @(
    '-u', $builder,
    '--config', $config,
    '--output-root', $OutputRoot,
    '--threads', [string]$Threads,
    '--memory-limit', $MemoryLimit,
    '--temp-directory', $tempDirectory,
    '--stop-file', $stopFile
)
$process = Start-Process -FilePath 'python' -ArgumentList $arguments -NoNewWindow -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Write-AtomicJson -Path $pidManifest -Payload ([ordered]@{
    wrapper_pid = $PID
    child_pid = $process.Id
    started_at_utc = $started.ToString('o')
    command = 'python ' + ($arguments -join ' ')
})

Write-Heartbeat -Status 'RUNNING' -Stage 'BUILDER' -ChildPid $process.Id
while (-not $process.HasExited) {
    Start-Sleep -Seconds $HeartbeatSeconds
    $process.Refresh()
    Write-Heartbeat -Status 'RUNNING' -Stage 'BUILDER' -ChildPid $process.Id
}
$builderExit = $process.ExitCode

$validatorExit = $null
if ($builderExit -eq 0) {
    Write-Heartbeat -Status 'RUNNING' -Stage 'VALIDATOR' -ChildPid 0
    $validatorProcess = Start-Process -FilePath 'python' -ArgumentList @(
        $validator,
        '--config', $config,
        '--sample-root', $OutputRoot,
        '--output-json', $validation
    ) -NoNewWindow -PassThru -Wait -RedirectStandardOutput $validatorStdout -RedirectStandardError $validatorStderr
    $validatorExit = $validatorProcess.ExitCode
}

$validationGate = $null
if (Test-Path -LiteralPath $validation) {
    $validationGate = (Get-Content -LiteralPath $validation -Raw | ConvertFrom-Json).validation_gate
}
$status = if ($builderExit -eq 0 -and $validatorExit -eq 0 -and $validationGate -eq 'PASS_WITH_RESTRICTIONS') { 'COMPLETE' } else { 'FAILED' }
$ended = [DateTime]::UtcNow
$final = [ordered]@{
    operation_id = 'trading_activity_ta3_stratified_sample_v0_1'
    final_status = $status
    started_at_utc = $started.ToString('o')
    ended_at_utc = $ended.ToString('o')
    elapsed_seconds = [math]::Round(($ended - $started).TotalSeconds, 3)
    builder_exit_code = $builderExit
    validator_exit_code = $validatorExit
    validation_gate = $validationGate
    output_root = $OutputRoot
    runtime_root = $RuntimeRoot
    sample_manifest = Join-Path $OutputRoot 'sample_manifest_v0_1.json'
    independent_validation = $validation
    stdout = $stdout
    stderr = $stderr
}
Write-AtomicJson -Path $finalManifest -Payload $final
Write-Heartbeat -Status $status -Stage 'FINAL' -ChildPid 0
$final | ConvertTo-Json -Depth 20
if ($status -ne 'COMPLETE') { exit 1 }
