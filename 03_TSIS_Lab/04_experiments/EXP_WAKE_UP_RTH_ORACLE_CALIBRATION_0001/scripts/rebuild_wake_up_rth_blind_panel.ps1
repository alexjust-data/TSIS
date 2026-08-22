param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,
    [string]$Config = "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\configs\wake_up_rth_calibration_v0_1.json",
    [string]$RepairId = "blind_panel_rth_stratification_v0_2",
    [switch]$Resume
)

$ErrorActionPreference = "Stop"
$RunRoot = (Resolve-Path -LiteralPath $RunRoot).Path
$finalPath = Join-Path $RunRoot "final_manifest.json"
if (-not (Test-Path -LiteralPath $finalPath)) {
    throw "Missing candidate final_manifest.json: $finalPath"
}
$candidateFinal = Get-Content -LiteralPath $finalPath -Raw | ConvertFrom-Json
if ([string]$candidateFinal.status -ne "COMPLETE") {
    throw "Candidate run is not COMPLETE"
}
$targetProgress = "{0}/{1}" -f $candidateFinal.completed_targets, $candidateFinal.expected_targets

$repairParent = Join-Path $RunRoot "repairs"
$repairRoot = Join-Path $repairParent $RepairId
$stagingRoot = Join-Path $RunRoot "blind_panel_rebuild_v0_2_staging"
$canonicalPanel = Join-Path $RunRoot "blind_panel"
$quarantineParent = Join-Path $RunRoot "quarantine"
$quarantineRoot = Join-Path $quarantineParent "blind_panel_invalid_rth_stratification_v0_1"
$lockPath = Join-Path $RunRoot "blind_panel_repair.lock"
$runHeartbeat = Join-Path $RunRoot "heartbeat_latest.json"
$repairHeartbeat = Join-Path $repairRoot "heartbeat_latest.json"
$wrapperPidPath = Join-Path $repairRoot "wrapper_pid.txt"
$logPath = Join-Path $repairRoot "repair.log"

if ((Test-Path -LiteralPath $repairRoot) -and -not $Resume) {
    throw "Repair root already exists; use -Resume only for this exact repair: $repairRoot"
}
New-Item -ItemType Directory -Path $repairRoot -Force | Out-Null
Set-Content -LiteralPath $wrapperPidPath -Value ([string]$PID) -Encoding ascii

if (Test-Path -LiteralPath $lockPath) {
    $oldPid = [int](Get-Content -LiteralPath $lockPath -Raw)
    if (Get-Process -Id $oldPid -ErrorAction SilentlyContinue) {
        throw "A blind-panel repair writer is already alive: PID=$oldPid"
    }
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
    Move-Item -LiteralPath $lockPath -Destination "$lockPath.stale.$stamp"
}
New-Item -ItemType File -Path $lockPath -Value ([string]$PID) -ErrorAction Stop | Out-Null

$panelScript = Join-Path $PSScriptRoot "build_wake_up_blind_panel.py"
$galleryScript = Join-Path $PSScriptRoot "render_wake_up_blind_gallery.py"
$validatorScript = Join-Path $PSScriptRoot "validate_wake_up_rth_run.py"
$runnerPath = $MyInvocation.MyCommand.Path

function Write-JsonAtomic([string]$Path, [object]$Payload) {
    $token = [guid]::NewGuid().ToString("N")
    $temp = "$Path.tmp.$PID.$token"
    $Payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $temp -Encoding UTF8
    if (Test-Path -LiteralPath $Path) {
        $backup = "$Path.bak.$PID.$token"
        try {
            [System.IO.File]::Replace($temp, $Path, $backup, $true)
        }
        catch {
            Copy-Item -LiteralPath $temp -Destination $Path -Force
            Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
        }
        Remove-Item -LiteralPath $backup -Force -ErrorAction SilentlyContinue
    }
    else {
        [System.IO.File]::Move($temp, $Path)
    }
}

function New-HeartbeatPayload([string]$Status, [string]$Stage) {
    return @{
        status = $Status
        stage = $Stage
        target_progress = $targetProgress
        ticker = ""
        repair_id = $RepairId
        wrapper_pid = $PID
        updated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    }
}

function Write-Heartbeat([string]$Status, [string]$Stage) {
    $payload = New-HeartbeatPayload $Status $Stage
    Write-JsonAtomic $runHeartbeat $payload
    Write-JsonAtomic $repairHeartbeat $payload
}

function Invoke-PythonStage([string]$Stage, [string[]]$PythonArgs) {
    Write-Heartbeat "RUNNING" $Stage
    $heartbeatJob = Start-Job -ScriptBlock {
        param($RunPath, $RepairPath, $StageName, $RepairName, $OwnerPid, $TargetProgress)
        while ($true) {
            $payload = @{
                status = "RUNNING"
                stage = $StageName
                target_progress = $TargetProgress
                ticker = ""
                repair_id = $RepairName
                wrapper_pid = $OwnerPid
                updated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
            }
            foreach ($path in @($RunPath, $RepairPath)) {
                $token = [guid]::NewGuid().ToString("N")
                $temp = "$path.tmp.$PID.$token"
                $payload | ConvertTo-Json -Depth 8 |
                    Set-Content -LiteralPath $temp -Encoding UTF8
                if (Test-Path -LiteralPath $path) {
                    $backup = "$path.bak.$PID.$token"
                    try {
                        [System.IO.File]::Replace($temp, $path, $backup, $true)
                    }
                    catch {
                        Copy-Item -LiteralPath $temp -Destination $path -Force
                        Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
                    }
                    Remove-Item -LiteralPath $backup -Force -ErrorAction SilentlyContinue
                }
                else {
                    [System.IO.File]::Move($temp, $path)
                }
            }
            Start-Sleep -Seconds 10
        }
    } -ArgumentList $runHeartbeat, $repairHeartbeat, $Stage, $RepairId, $PID, $targetProgress
    try {
        & python @PythonArgs 2>&1 | Tee-Object -FilePath $logPath -Append
        $stageExitCode = $LASTEXITCODE
    }
    finally {
        Stop-Job -Job $heartbeatJob -ErrorAction SilentlyContinue
        Remove-Job -Job $heartbeatJob -Force -ErrorAction SilentlyContinue
    }
    if ($stageExitCode -ne 0) {
        throw "$Stage failed with exit code $stageExitCode"
    }
    Write-Heartbeat "RUNNING" ("{0}_COMPLETE" -f $Stage)
}

$preManifestPath = Join-Path $repairRoot "pre_manifest.json"
if (-not (Test-Path -LiteralPath $preManifestPath)) {
    $preManifest = @{
        repair_id = $RepairId
        status = "PREPARED"
        created_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        run_root = $RunRoot
        candidate_final_manifest_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $finalPath).Hash.ToLowerInvariant()
        config_path = $Config
        config_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $Config).Hash.ToLowerInvariant()
        runner_path = $runnerPath
        runner_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $runnerPath).Hash.ToLowerInvariant()
        panel_script_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $panelScript).Hash.ToLowerInvariant()
        gallery_script_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $galleryScript).Hash.ToLowerInvariant()
        validator_script_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $validatorScript).Hash.ToLowerInvariant()
        network_access = "PROHIBITED"
        promotion_policy = "STAGING_VALIDATE_THEN_QUARANTINE_AND_PROMOTE"
        expected_scope = $targetProgress
        output_root = $stagingRoot
        log_path = $logPath
        heartbeat_path = $repairHeartbeat
        wrapper_pid_path = $wrapperPidPath
        resume_policy = "RESUME_ONLY_WHEN_ALL_HASH_BOUND_INPUTS_AND_SCRIPTS_MATCH"
        overwrite_policy = "NO_DELETE; INVALID_CANONICAL_PANEL_MOVED_TO_QUARANTINE_AFTER_STAGING_PASS"
        success_rule = "STAGING_AND_CANONICAL_TERMINAL_VALIDATION_PASS"
        monitor_command = ('& "{0}" -RunRoot "{1}" -RepairId "{2}" -IntervalSeconds 10 -Compact -Watch' -f (Join-Path $PSScriptRoot "monitor_wake_up_rth_blind_panel_repair.ps1"), $RunRoot, $RepairId)
    }
    Write-JsonAtomic $preManifestPath $preManifest
}
else {
    $preManifest = Get-Content -LiteralPath $preManifestPath -Raw | ConvertFrom-Json
    $resumeChecks = @(
        ([string]$preManifest.candidate_final_manifest_sha256 -eq
            (Get-FileHash -Algorithm SHA256 -LiteralPath $finalPath).Hash.ToLowerInvariant()),
        ([string]$preManifest.config_sha256 -eq
            (Get-FileHash -Algorithm SHA256 -LiteralPath $Config).Hash.ToLowerInvariant()),
        ([string]$preManifest.runner_sha256 -eq
            (Get-FileHash -Algorithm SHA256 -LiteralPath $runnerPath).Hash.ToLowerInvariant()),
        ([string]$preManifest.panel_script_sha256 -eq
            (Get-FileHash -Algorithm SHA256 -LiteralPath $panelScript).Hash.ToLowerInvariant()),
        ([string]$preManifest.gallery_script_sha256 -eq
            (Get-FileHash -Algorithm SHA256 -LiteralPath $galleryScript).Hash.ToLowerInvariant()),
        ([string]$preManifest.validator_script_sha256 -eq
            (Get-FileHash -Algorithm SHA256 -LiteralPath $validatorScript).Hash.ToLowerInvariant())
    )
    if ($resumeChecks -contains $false) {
        throw "Resume refused: candidate/config/runner/panel/gallery/validator identity changed"
    }
}

$monitorPath = Join-Path $PSScriptRoot "monitor_wake_up_rth_blind_panel_repair.ps1"
$monitorCommand = '& "{0}" -RunRoot "{1}" -RepairId "{2}" -IntervalSeconds 10 -Compact -Watch' -f $monitorPath, $RunRoot, $RepairId
Write-Host "repair_id=$RepairId"
Write-Host "mode=blind_panel_repair"
Write-Host "input_root=$RunRoot"
Write-Host "output_root=$stagingRoot"
Write-Host "pre_manifest=$preManifestPath"
Write-Host "heartbeat=$repairHeartbeat"
Write-Host "log=$logPath"
Write-Host "pid_manifest=$wrapperPidPath"
Write-Host "monitor_command=$monitorCommand"
Write-Host "success_rule=STAGING_AND_CANONICAL_TERMINAL_VALIDATION_PASS"
Write-Host "resume_policy=HASH_BOUND_RESUME_ONLY"

try {
    $stagingPanelManifestPath = Join-Path $stagingRoot "panel_manifest.json"
    if (Test-Path -LiteralPath $stagingPanelManifestPath) {
        $stagingPanelManifest = Get-Content -LiteralPath $stagingPanelManifestPath -Raw | ConvertFrom-Json
        $stagingPanelCurrent = (
            [string]$stagingPanelManifest.script_sha256 -eq
                (Get-FileHash -Algorithm SHA256 -LiteralPath $panelScript).Hash.ToLowerInvariant() -and
            [string]$stagingPanelManifest.config_sha256 -eq
                (Get-FileHash -Algorithm SHA256 -LiteralPath $Config).Hash.ToLowerInvariant() -and
            [string]$stagingPanelManifest.candidate_final_manifest_sha256 -eq
                (Get-FileHash -Algorithm SHA256 -LiteralPath $finalPath).Hash.ToLowerInvariant()
        )
        if (-not $stagingPanelCurrent) {
            $stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
            Move-Item -LiteralPath $stagingRoot -Destination (Join-Path $repairRoot "staging_version_mismatch_$stamp")
        }
    }
    if ((Test-Path -LiteralPath $stagingRoot) -and
        -not (Test-Path -LiteralPath (Join-Path $stagingRoot "panel_manifest.json"))) {
        $stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
        Move-Item -LiteralPath $stagingRoot -Destination (Join-Path $repairRoot "staging_incomplete_$stamp")
    }
    if (-not (Test-Path -LiteralPath (Join-Path $stagingRoot "panel_manifest.json"))) {
        $panelArgs = @(
            $panelScript,
            "--config", $Config,
            "--candidate-run-root", $RunRoot,
            "--output-root", $stagingRoot
        )
        Invoke-PythonStage "BLIND_PANEL_REBUILD" $panelArgs
    }
    $stagingGalleryManifestPath = Join-Path $stagingRoot "gallery_manifest.json"
    if (Test-Path -LiteralPath $stagingGalleryManifestPath) {
        $stagingGalleryManifest = Get-Content -LiteralPath $stagingGalleryManifestPath -Raw | ConvertFrom-Json
        $stagingGalleryCurrent = (
            [string]$stagingGalleryManifest.script_sha256 -eq
                (Get-FileHash -Algorithm SHA256 -LiteralPath $galleryScript).Hash.ToLowerInvariant() -and
            [string]$stagingGalleryManifest.config_sha256 -eq
                (Get-FileHash -Algorithm SHA256 -LiteralPath $Config).Hash.ToLowerInvariant() -and
            [string]$stagingGalleryManifest.panel_manifest_sha256 -eq
                (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $stagingRoot "panel_manifest.json")).Hash.ToLowerInvariant()
        )
        if (-not $stagingGalleryCurrent) {
            $stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
            $galleryQuarantine = Join-Path $repairRoot "gallery_version_mismatch_$stamp"
            New-Item -ItemType Directory -Path $galleryQuarantine -Force | Out-Null
            foreach ($name in @("charts", "gallery.html", "gallery_manifest.json")) {
                $oldGalleryPart = Join-Path $stagingRoot $name
                if (Test-Path -LiteralPath $oldGalleryPart) {
                    Move-Item -LiteralPath $oldGalleryPart -Destination $galleryQuarantine
                }
            }
        }
    }
    if (-not (Test-Path -LiteralPath (Join-Path $stagingRoot "gallery_manifest.json"))) {
        $galleryArgs = @(
            $galleryScript,
            "--config", $Config,
            "--candidate-run-root", $RunRoot,
            "--panel-root", $stagingRoot
        )
        if ([string]$candidateFinal.mode -eq "probe") {
            $galleryArgs += @("--max-cases", "8")
        }
        Invoke-PythonStage "BLIND_GALLERY_REBUILD" $galleryArgs
    }

    $stagingValidation = Join-Path $repairRoot "staging_terminal_validation_manifest.json"
    $validatorArgs = @(
        $validatorScript,
        "--run-root", $RunRoot,
        "--panel-root", $stagingRoot,
        "--output", $stagingValidation
    )
    Invoke-PythonStage "STAGING_TERMINAL_VALIDATION" $validatorArgs
    $stagingResult = Get-Content -LiteralPath $stagingValidation -Raw | ConvertFrom-Json
    if ([string]$stagingResult.status -ne "PASS") {
        throw "Staging terminal validation did not PASS"
    }

    Write-Heartbeat "RUNNING" "ATOMIC_PROMOTION"
    New-Item -ItemType Directory -Path $quarantineParent -Force | Out-Null
    if (Test-Path -LiteralPath $quarantineRoot) {
        throw "Quarantine target already exists: $quarantineRoot"
    }
    New-Item -ItemType Directory -Path $quarantineRoot -Force | Out-Null
    if (Test-Path -LiteralPath $canonicalPanel) {
        Move-Item -LiteralPath $canonicalPanel -Destination (Join-Path $quarantineRoot "blind_panel")
    }
    foreach ($name in @("terminal_validation_manifest.json", "human_gate_handoff.json")) {
        $oldPath = Join-Path $RunRoot $name
        if (Test-Path -LiteralPath $oldPath) {
            Move-Item -LiteralPath $oldPath -Destination (Join-Path $quarantineRoot $name)
        }
    }
    Move-Item -LiteralPath $stagingRoot -Destination $canonicalPanel

    $canonicalValidation = Join-Path $RunRoot "terminal_validation_manifest.json"
    $canonicalValidatorArgs = @(
        $validatorScript,
        "--run-root", $RunRoot,
        "--output", $canonicalValidation
    )
    Invoke-PythonStage "CANONICAL_TERMINAL_VALIDATION" $canonicalValidatorArgs

    $handoff = @{
        status = "WAITING_HUMAN_BLIND_REVIEW"
        stage = "HUMAN_GATE"
        run_id = [string]$candidateFinal.run_id
        run_root = $RunRoot
        repair_id = $RepairId
        gallery = (Join-Path $canonicalPanel "gallery.html")
        review_template = (Join-Path $canonicalPanel "review_template.csv")
        completed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        binding_a_consumed = $false
        binding_b_consumed = $false
        intraday_price_path_consumed = $false
        trade_price_used_only_via_dollar_notional = $true
        invalid_panel_quarantine = $quarantineRoot
    }
    Write-JsonAtomic (Join-Path $RunRoot "human_gate_handoff.json") $handoff

    $finalRepair = @{
        repair_id = $RepairId
        status = "COMPLETE_PASS"
        completed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        run_root = $RunRoot
        canonical_panel = $canonicalPanel
        invalid_panel_quarantine = $quarantineRoot
        terminal_validation_manifest = $canonicalValidation
        staging_validation_status = [string]$stagingResult.status
        network_access = "PROHIBITED_AND_NOT_USED"
    }
    Write-JsonAtomic (Join-Path $repairRoot "final_manifest.json") $finalRepair
    Write-Heartbeat "WAITING_HUMAN_BLIND_REVIEW" "HUMAN_GATE"
    Write-Host "WAITING_HUMAN_BLIND_REVIEW"
    Write-Host (Join-Path $canonicalPanel "gallery.html")
}
catch {
    $failure = @{
        repair_id = $RepairId
        status = "FAILED"
        failed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        error = [string]$_
        run_root = $RunRoot
    }
    Write-JsonAtomic (Join-Path $repairRoot "final_manifest.json") $failure
    Write-Heartbeat "FAILED" "FINAL"
    throw
}
finally {
    if (Test-Path -LiteralPath $lockPath) {
        Remove-Item -LiteralPath $lockPath -Force
    }
}
