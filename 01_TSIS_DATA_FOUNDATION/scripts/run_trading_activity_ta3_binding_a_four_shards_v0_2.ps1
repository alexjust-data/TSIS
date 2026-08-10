param(
    [string]$SampleManifest = "G:\TSIS\data\data_foundation_outputs\trading_activity_ta3_stratified_sample\trading_activity_ta3_stratified_sample_v0_1_20260807T175808Z\sample_manifest_v0_2.json",
    [string]$BaseConfig = "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\trading_activity_binding_a_multisession_pilot_v0_2.json",
    [string]$BindingRoot = "D:\TSIS\IO\wake_up\trading_activity\pit_marked_activity\binding_a_v02",
    [string]$RunPrefix = "ba2r2",
    [int]$HeartbeatSeconds = 30
)

$ErrorActionPreference = "Stop"
$runner = "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\run_trading_activity_ta3_binding_a.py"
$outputRoot = Join-Path $BindingRoot "runs"
$runtimeRoot = Join-Path $BindingRoot "operations"
$pointerRoot = Join-Path $BindingRoot "pointers"
$controllerRoot = Join-Path $runtimeRoot ("controller_" + $RunPrefix)
$logRoot = Join-Path $controllerRoot "logs"

foreach ($path in @($outputRoot, $runtimeRoot, $pointerRoot, $controllerRoot, $logRoot)) {
    New-Item -ItemType Directory -Path $path -Force | Out-Null
}

function Write-JsonAtomic([string]$Path, [object]$Payload) {
    $temp = "$Path.$PID.tmp"
    $Payload | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $temp -Encoding UTF8
    Move-Item -LiteralPath $temp -Destination $Path -Force
}

$startedAt = [datetimeoffset]::UtcNow
$preManifest = [ordered]@{
    operation = "trading_activity_ta3_binding_a_four_shards_v0_2"
    run_prefix = $RunPrefix
    status = "STARTING"
    created_at_utc = $startedAt.ToString("o")
    sample_manifest = (Resolve-Path -LiteralPath $SampleManifest).Path
    base_config = (Resolve-Path -LiteralPath $BaseConfig).Path
    binding_root = $BindingRoot
    output_root = $outputRoot
    runtime_root = $runtimeRoot
    pointer_root = $pointerRoot
    shard_count = 4
    maximum_concurrent_workers = 2
    wave_plan = @(@(0, 1), @(2, 3))
    promotion_status = "NOT_AUTHORIZED"
}
Write-JsonAtomic (Join-Path $controllerRoot "pre_manifest.json") $preManifest
Write-JsonAtomic (Join-Path $controllerRoot "pid_manifest.json") ([ordered]@{
    controller_pid = $PID
    created_at_utc = [datetimeoffset]::UtcNow.ToString("o")
})

$results = New-Object System.Collections.Generic.List[object]
$failed = $false

foreach ($wave in @(@(0, 1), @(2, 3))) {
    $processes = @()
    foreach ($shard in $wave) {
        $runId = "${RunPrefix}_s${shard}of4"
        $stdout = Join-Path $logRoot "$runId.stdout.log"
        $stderr = Join-Path $logRoot "$runId.stderr.log"
        $arguments = @(
            $runner,
            "--sample-manifest", $SampleManifest,
            "--base-config", $BaseConfig,
            "--run-id", $runId,
            "--output-root", $outputRoot,
            "--runtime-root", $runtimeRoot,
            "--pointer-root", $pointerRoot,
            "--shard-index", "$shard",
            "--shard-count", "4"
        )
        $process = Start-Process -FilePath "python" -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
        $processes += [pscustomobject]@{ shard = $shard; run_id = $runId; process = $process; stdout = $stdout; stderr = $stderr }
    }

    while (($processes | Where-Object { -not $_.process.HasExited }).Count -gt 0) {
        $active = @($processes | Where-Object { -not $_.process.HasExited } | ForEach-Object { $_.shard })
        Write-JsonAtomic (Join-Path $controllerRoot "heartbeat_latest.json") ([ordered]@{
            timestamp_utc = [datetimeoffset]::UtcNow.ToString("o")
            status = "RUNNING"
            active_wave = $wave
            active_shards = $active
            completed_shards = @($results | Where-Object { $_.exit_code -eq 0 } | ForEach-Object { $_.shard })
            failed_shards = @($results | Where-Object { $_.exit_code -ne 0 } | ForEach-Object { $_.shard })
            controller_pid = $PID
        })
        Start-Sleep -Seconds $HeartbeatSeconds
        foreach ($entry in $processes) { $entry.process.Refresh() }
    }

    foreach ($entry in $processes) {
        $entry.process.WaitForExit()
        $results.Add([ordered]@{
            shard = $entry.shard
            run_id = $entry.run_id
            exit_code = $entry.process.ExitCode
            stdout = $entry.stdout
            stderr = $entry.stderr
        })
        if ($entry.process.ExitCode -ne 0) { $failed = $true }
    }
    if ($failed) { break }
}

$status = if ($failed) { "FAILED" } else { "COMPLETE" }
Write-JsonAtomic (Join-Path $controllerRoot "final_manifest.json") ([ordered]@{
    operation = "trading_activity_ta3_binding_a_four_shards_v0_2"
    run_prefix = $RunPrefix
    status = $status
    started_at_utc = $startedAt.ToString("o")
    completed_at_utc = [datetimeoffset]::UtcNow.ToString("o")
    binding_root = $BindingRoot
    shard_results = $results
    promotion_status = "NOT_AUTHORIZED"
})
Write-JsonAtomic (Join-Path $controllerRoot "heartbeat_latest.json") ([ordered]@{
    timestamp_utc = [datetimeoffset]::UtcNow.ToString("o")
    status = $status
    active_shards = @()
    controller_pid = $PID
})

if ($failed) { exit 1 }
exit 0
