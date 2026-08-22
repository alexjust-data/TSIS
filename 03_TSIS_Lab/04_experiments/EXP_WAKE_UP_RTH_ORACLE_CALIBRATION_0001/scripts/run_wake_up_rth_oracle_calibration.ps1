param(
    [Parameter(Mandatory = $true)]
    [string]$RunId,
    [string]$Config = "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\configs\wake_up_rth_calibration_v0_1.json",
    [ValidateSet("probe", "full")]
    [string]$Mode = "full",
    [int]$ProbePerCohort = 1,
    [switch]$Resume
)

$ErrorActionPreference = "Stop"
$configObject = Get-Content -LiteralPath $Config -Raw | ConvertFrom-Json
$runParent = [string]$configObject.outputs.run_parent
$runRoot = Join-Path $runParent $RunId
$panelRoot = Join-Path $runRoot "blind_panel"
$lockPath = Join-Path $runRoot "writer.lock"
$wrapperPidPath = Join-Path $runRoot "wrapper_pid.txt"
New-Item -ItemType Directory -Path $runRoot -Force | Out-Null

if (Test-Path -LiteralPath $lockPath) {
    $oldPid = [int](Get-Content -LiteralPath $lockPath -Raw)
    if (Get-Process -Id $oldPid -ErrorAction SilentlyContinue) {
        throw "A writer is already alive for this run root: PID=$oldPid"
    }
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
    Move-Item -LiteralPath $lockPath -Destination "$lockPath.stale.$stamp"
}
New-Item -ItemType File -Path $lockPath -Value ([string]$PID) -ErrorAction Stop | Out-Null
Set-Content -LiteralPath $wrapperPidPath -Value ([string]$PID) -Encoding ascii

try {
    $candidateArgs = @(
        (Join-Path $PSScriptRoot "build_wake_up_rth_candidate_pool.py"),
        "--config", $Config, "--run-id", $RunId, "--mode", $Mode,
        "--probe-per-cohort", [string]$ProbePerCohort
    )
    if ($Resume) { $candidateArgs += "--resume" }
    & python @candidateArgs
    if ($LASTEXITCODE -ne 0) { throw "Candidate search failed: $LASTEXITCODE" }

    if ((Test-Path -LiteralPath $panelRoot) -and -not (Test-Path -LiteralPath (Join-Path $panelRoot "panel_manifest.json"))) {
        $stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
        Move-Item -LiteralPath $panelRoot -Destination "$panelRoot.incomplete.$stamp"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $panelRoot "panel_manifest.json"))) {
        $panelArgs = @(
            (Join-Path $PSScriptRoot "build_wake_up_blind_panel.py"),
            "--config", $Config, "--candidate-run-root", $runRoot,
            "--output-root", $panelRoot
        )
        & python @panelArgs
        if ($LASTEXITCODE -ne 0) { throw "Blind panel build failed: $LASTEXITCODE" }
    }
    if (-not (Test-Path -LiteralPath (Join-Path $panelRoot "gallery_manifest.json"))) {
        $galleryArgs = @(
            (Join-Path $PSScriptRoot "render_wake_up_blind_gallery.py"),
            "--config", $Config, "--candidate-run-root", $runRoot,
            "--panel-root", $panelRoot
        )
        if ($Mode -eq "probe") { $galleryArgs += @("--max-cases", "8") }
        & python @galleryArgs
        if ($LASTEXITCODE -ne 0) { throw "Blind gallery render failed: $LASTEXITCODE" }
    }
    $validatorArgs = @(
        (Join-Path $PSScriptRoot "validate_wake_up_rth_run.py"),
        "--run-root", $runRoot
    )
    & python @validatorArgs
    if ($LASTEXITCODE -ne 0) { throw "Terminal validation failed: $LASTEXITCODE" }
    $handoff = @{
        status = "WAITING_HUMAN_BLIND_REVIEW"
        stage = "HUMAN_GATE"
        run_id = $RunId
        run_root = $runRoot
        gallery = (Join-Path $panelRoot "gallery.html")
        review_template = (Join-Path $panelRoot "review_template.csv")
        completed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        binding_a_consumed = $false
        binding_b_consumed = $false
        intraday_price_path_consumed = $false
        trade_price_used_only_via_dollar_notional = $true
    }
    $handoff | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $runRoot "human_gate_handoff.json") -Encoding UTF8
    Write-Host "WAITING_HUMAN_BLIND_REVIEW"
    Write-Host (Join-Path $panelRoot "gallery.html")
}
finally {
    if (Test-Path -LiteralPath $lockPath) { Remove-Item -LiteralPath $lockPath -Force }
}
