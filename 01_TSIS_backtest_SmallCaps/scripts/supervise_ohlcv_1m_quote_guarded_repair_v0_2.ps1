param(
    [Parameter(Mandatory=$true)]
    [string]$RunRoot,
    [string]$ProjectRoot = "C:\TSIS_Data\01_TSIS_backtest_SmallCaps",
    [string]$RunnerScript = "",
    [int]$Workers = 12,
    [int]$PollSeconds = 60,
    [int]$StaleMinutes = 20,
    [int]$OrphanGraceMinutes = 3,
    [int]$MaxRestarts = 0,
    [string]$PythonExe = "python",
    [switch]$Once,
    [switch]$NoPromoteManifest
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RunnerScript)) {
    $RunnerScript = Join-Path $ProjectRoot "scripts\run_ohlcv_1m_quote_guarded_repair_v0_2.ps1"
}

function Read-JsonFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }
    try {
        return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Get-LatestOutputWriteUtc {
    param([string]$Root)
    $candidates = @()
    foreach ($relative in @(
        "progress_snapshot.json",
        "ticker_status",
        "ticker_summaries",
        "month_summaries",
        "repair_shards"
    )) {
        $path = Join-Path $Root $relative
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            $candidates += (Get-Item -LiteralPath $path).LastWriteTimeUtc
        } elseif (Test-Path -LiteralPath $path -PathType Container) {
            $latest = Get-ChildItem -LiteralPath $path -File -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTimeUtc -Descending |
                Select-Object -First 1
            if ($latest -ne $null) {
                $candidates += $latest.LastWriteTimeUtc
            }
        }
    }
    if ($candidates.Count -eq 0) {
        return $null
    }
    return ($candidates | Sort-Object -Descending | Select-Object -First 1)
}

function Get-MatchingRepairProcesses {
    param(
        [string]$Root,
        [string]$Project
    )
    $needleRun = $Root.ToLowerInvariant()
    $needleScript = "build_ohlcv_1m_quote_guarded_repairs_v0_2.py"
    $needleRunner = "run_ohlcv_1m_quote_guarded_repair_v0_2.ps1"
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.CommandLine -and
            $_.CommandLine.ToLowerInvariant().Contains($needleRun) -and
            (
                $_.CommandLine.Contains($needleScript) -or
                $_.CommandLine.Contains($needleRunner)
            )
        } |
        Select-Object ProcessId,ParentProcessId,Name,CommandLine
}

function Get-ChildProcessMap {
    $map = @{}
    Get-CimInstance Win32_Process | ForEach-Object {
        $parent = [int]$_.ParentProcessId
        if (-not $map.ContainsKey($parent)) {
            $map[$parent] = @()
        }
        $map[$parent] += $_
    }
    return $map
}

function Get-DescendantProcesses {
    param(
        [int]$ProcessId,
        [hashtable]$ChildMap
    )
    $out = @()
    $queue = New-Object System.Collections.Queue
    $queue.Enqueue($ProcessId)
    while ($queue.Count -gt 0) {
        $parent = [int]$queue.Dequeue()
        if ($ChildMap.ContainsKey($parent)) {
            foreach ($child in $ChildMap[$parent]) {
                $out += $child
                $queue.Enqueue([int]$child.ProcessId)
            }
        }
    }
    return $out
}

function Get-StaleOrphanRunnerWrappers {
    param(
        [object[]]$Processes
    )
    $childMap = Get-ChildProcessMap
    $orphans = @()
    foreach ($proc in $Processes) {
        $cmd = [string]$proc.CommandLine
        if (-not $cmd.Contains("run_ohlcv_1m_quote_guarded_repair_v0_2.ps1")) {
            continue
        }
        $descendants = @(Get-DescendantProcesses -ProcessId ([int]$proc.ProcessId) -ChildMap $childMap)
        $pythonDescendants = @($descendants | Where-Object { $_.Name -eq "python.exe" })
        if ($pythonDescendants.Count -eq 0) {
            $orphans += $proc
        }
    }
    return $orphans
}

function Write-SupervisorEvent {
    param(
        [string]$Root,
        [hashtable]$Payload
    )
    $path = Join-Path $Root "supervisor_events.jsonl"
    $Payload["observed_at"] = (Get-Date).ToString("o")
    $line = ($Payload | ConvertTo-Json -Compress -Depth 5)
    Add-Content -LiteralPath $path -Value $line -Encoding UTF8
}

function Start-RepairRunner {
    param(
        [string]$Root,
        [string]$Runner,
        [string]$Project,
        [int]$WorkerCount,
        [string]$PythonPath,
        [bool]$SkipPromotion
    )
    $stdoutLog = Join-Path $Root ("supervisor_runner_{0}.stdout.log" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
    $stderrLog = Join-Path $Root ("supervisor_runner_{0}.stderr.log" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
    $args = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", $Runner,
        "-ProjectRoot", $Project,
        "-RunRoot", $Root,
        "-Workers", [string]$WorkerCount,
        "-PythonExe", $PythonPath
    )
    if ($SkipPromotion) {
        $args += "-NoPromoteManifest"
    }
    $proc = Start-Process -FilePath "powershell.exe" -ArgumentList $args -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog
    Write-SupervisorEvent -Root $Root -Payload @{
        event = "restart_started"
        pid = $proc.Id
        stdout_log = $stdoutLog
        stderr_log = $stderrLog
        workers = $WorkerCount
    }
    return $proc
}

if (-not (Test-Path -LiteralPath $RunRoot)) {
    throw "Missing RunRoot: $RunRoot"
}
if (-not (Test-Path -LiteralPath $RunnerScript)) {
    throw "Missing RunnerScript: $RunnerScript"
}

$restartCount = 0
Write-Host "TSIS quote-guarded v0_2 supervisor"
Write-Host ("Run root: {0}" -f $RunRoot)
Write-Host ("Runner: {0}" -f $RunnerScript)
Write-Host ("Workers: {0} | poll: {1}s | stale: {2}m | orphan grace: {3}m" -f $Workers, $PollSeconds, $StaleMinutes, $OrphanGraceMinutes)
Write-Host ""

while ($true) {
    $summaryPath = Join-Path $RunRoot "repair_summary.json"
    $finalSummary = Read-JsonFile -Path $summaryPath
    if ($finalSummary -ne $null) {
        Write-SupervisorEvent -Root $RunRoot -Payload @{ event = "completed"; summary = $summaryPath }
        Write-Host ("[{0}] completed: {1}" -f (Get-Date).ToString("s"), $summaryPath)
        break
    }

    $procs = @(Get-MatchingRepairProcesses -Root $RunRoot -Project $ProjectRoot)
    $orphanWrappers = @(Get-StaleOrphanRunnerWrappers -Processes $procs)
    $latestUtc = Get-LatestOutputWriteUtc -Root $RunRoot
    $ageMin = $null
    if ($latestUtc -ne $null) {
        $ageMin = [Math]::Round(((Get-Date).ToUniversalTime() - $latestUtc).TotalMinutes, 2)
    }
    $snapshot = Read-JsonFile -Path (Join-Path $RunRoot "progress_snapshot.json")

    $line = "[{0}] processes={1} orphan_wrappers={2} latest_age_min={3}" -f (Get-Date).ToString("s"), $procs.Count, $orphanWrappers.Count, $ageMin
    if ($snapshot -ne $null) {
        $line += " months={0}/{1} repairs={2}" -f $snapshot.months_done, $snapshot.months_planned_in_started_tickers, $snapshot.repair_rows
    }
    Write-Host $line

    Write-SupervisorEvent -Root $RunRoot -Payload @{
        event = "heartbeat"
        matching_processes = $procs.Count
        orphan_wrappers = $orphanWrappers.Count
        latest_output_age_min = $ageMin
        months_done = if ($snapshot -ne $null) { $snapshot.months_done } else { $null }
        repair_rows = if ($snapshot -ne $null) { $snapshot.repair_rows } else { $null }
    }

    $isStale = ($latestUtc -eq $null) -or ($ageMin -ge $StaleMinutes)
    $isOrphanRestartable = $orphanWrappers.Count -gt 0 -and (
        $latestUtc -eq $null -or
        $ageMin -ge $OrphanGraceMinutes
    )
    if ($isOrphanRestartable) {
        foreach ($orphan in $orphanWrappers) {
            Write-Host ("[{0}] orphan runner wrapper exceeded {1}m grace; stopping PID {2}" -f (Get-Date).ToString("s"), $OrphanGraceMinutes, $orphan.ProcessId)
            Write-SupervisorEvent -Root $RunRoot -Payload @{
                event = "orphan_wrapper_grace_exceeded_stopped"
                pid = $orphan.ProcessId
                latest_output_age_min = $ageMin
                orphan_grace_minutes = $OrphanGraceMinutes
                command_line = $orphan.CommandLine
            }
            Stop-Process -Id ([int]$orphan.ProcessId) -Force -ErrorAction SilentlyContinue
        }
        $procs = @(Get-MatchingRepairProcesses -Root $RunRoot -Project $ProjectRoot)
    }

    if ($procs.Count -eq 0 -and ($isStale -or $isOrphanRestartable)) {
        if ($MaxRestarts -gt 0 -and $restartCount -ge $MaxRestarts) {
            Write-Host ("[{0}] restart limit reached ({1}); supervisor stays alive without starting a duplicate." -f (Get-Date).ToString("s"), $MaxRestarts)
        } else {
            $restartCount += 1
            $reason = if ($isOrphanRestartable) { "orphan wrapper grace exceeded" } else { "output stale" }
            Write-Host ("[{0}] no matching process after {1}; starting runner, restart #{2}" -f (Get-Date).ToString("s"), $reason, $restartCount)
            Start-RepairRunner -Root $RunRoot -Runner $RunnerScript -Project $ProjectRoot -WorkerCount $Workers -PythonPath $PythonExe -SkipPromotion ([bool]$NoPromoteManifest) | Out-Null
        }
    }

    if ($Once) {
        break
    }

    Start-Sleep -Seconds $PollSeconds
}
