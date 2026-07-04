<#
Audit parity between D:\quotes and E:\TSIS\data\quotes_.

This script is read-only for the quotes roots. It writes audit manifests and
per-ticker evidence under E:\TSIS\data\data_ops_manifests\quotes_parity_audit.

Default audit:
  - top-level ticker roster parity;
  - per-ticker recursive file count;
  - per-ticker recursive byte count;
  - per-ticker relative file inventory comparison by path and byte length.

Optional robocopy dry-run:
  - Use -UseRobocopyDryRun only as a diagnostic layer. It can be very slow on
    large ticker trees, so it is not part of the default full-universe audit.

Optional hash modes:
  - None: no hashes.
  - MismatchesOnly: hash only tickers that fail structural/robocopy parity.
  - Full: hash every file in every ticker tree. This is strongest but can take
    a very long time on millions of files.

Examples:
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\data_ops\audit_quotes_clone_parity.ps1 -Workers 12 -HashMode MismatchesOnly

  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\monitor_long_running_operation.ps1 -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "<run_id>" -Compact -Watch
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$SourceRoot = "D:\quotes",

    [Parameter()]
    [string]$TargetRoot = "E:\TSIS\data\quotes_",

    [Parameter()]
    [string]$LogRoot = "E:\TSIS\data\data_ops_manifests\quotes_parity_audit",

    [Parameter()]
    [ValidateRange(1, 32)]
    [int]$Workers = 12,

    [Parameter()]
    [ValidateSet("None", "MismatchesOnly", "Full")]
    [string]$HashMode = "MismatchesOnly",

    [Parameter()]
    [switch]$UseRobocopyDryRun,

    [Parameter()]
    [ValidateRange(10, 3600)]
    [int]$HeartbeatSeconds = 30,

    [Parameter()]
    [ValidateRange(0, 100000)]
    [int]$MaxTickers = 0,

    [Parameter()]
    [ValidateRange(0, 1024)]
    [int]$ShardIndex = 0,

    [Parameter()]
    [ValidateRange(1, 1024)]
    [int]$ShardCount = 1,

    [Parameter()]
    [string]$StartAtTicker = "",

    [Parameter()]
    [string]$RunId = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptStartedAtUtc = (Get-Date).ToUniversalTime()
$scriptPath = $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($RunId)) {
    $RunId = "quotes_parity_audit_{0}" -f $scriptStartedAtUtc.ToString("yyyyMMddTHHmmssZ")
}

function Get-NormalizedPath {
    param([Parameter(Mandatory = $true)][string]$PathValue)
    return [System.IO.Path]::GetFullPath($PathValue).TrimEnd("\")
}

function Write-JsonAtomic {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object]$Payload,
        [int]$Depth = 10
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
    }
    catch {
        $snapshot.dirty_state = "unavailable"
    }
    return $snapshot
}

function Get-DriveFreeGb {
    param([Parameter(Mandatory = $true)][string]$PathValue)
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

function Write-Heartbeat {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Status,
        [Parameter(Mandatory = $true)][string]$Stage,
        [int]$CurrentIndex,
        [int]$TotalCount,
        [string]$Item,
        [int]$MismatchCount,
        [int]$FailedWorkerCount,
        [string]$Message = ""
    )
    $nowUtc = (Get-Date).ToUniversalTime()
    $payload = [ordered]@{
        run_id = $RunId
        status = $Status
        stage = $Stage
        observed_at_utc = $nowUtc.ToString("o")
        elapsed_seconds = [Math]::Round(($nowUtc - $scriptStartedAtUtc).TotalSeconds, 1)
        current_index = $CurrentIndex
        total_count = $TotalCount
        item = $Item
        mismatch_count = $MismatchCount
        failed_worker_count = $FailedWorkerCount
        hash_mode = $HashMode
        source_root = $script:sourceRoot
        target_root = $script:targetRoot
        wrapper_pid = $PID
        active_pid = $PID
        output_free_gb = Get-DriveFreeGb -PathValue $script:targetRoot
        message = $Message
    }
    Write-JsonAtomic -Path $Path -Payload $payload -Depth 8
}

function Get-TickerDirs {
    param([Parameter(Mandatory = $true)][string]$Root)
    return @(Get-ChildItem -LiteralPath $Root -Directory -ErrorAction Stop |
        Sort-Object Name |
        Select-Object -ExpandProperty Name)
}

$script:sourceRoot = Get-NormalizedPath -PathValue $SourceRoot
$script:targetRoot = Get-NormalizedPath -PathValue $TargetRoot
$script:logRoot = Get-NormalizedPath -PathValue $LogRoot

if (-not (Test-Path -LiteralPath $script:sourceRoot -PathType Container)) {
    throw "Source root does not exist: $script:sourceRoot"
}
if (-not (Test-Path -LiteralPath $script:targetRoot -PathType Container)) {
    throw "Target root does not exist: $script:targetRoot"
}
if ($script:sourceRoot -ieq $script:targetRoot) {
    throw "Source and target resolve to the same path: $script:sourceRoot"
}

New-Item -ItemType Directory -Force -Path $script:logRoot | Out-Null
$runRoot = $script:logRoot
$tickerResultsRoot = Join-Path $runRoot "$RunId.ticker_results"
$mismatchRoot = Join-Path $runRoot "$RunId.mismatches"
$workerRoot = Join-Path $runRoot "$RunId.worker_inputs"
New-Item -ItemType Directory -Force -Path $tickerResultsRoot | Out-Null
New-Item -ItemType Directory -Force -Path $mismatchRoot | Out-Null
New-Item -ItemType Directory -Force -Path $workerRoot | Out-Null

$preManifestPath = Join-Path $runRoot "$RunId.pre_manifest.json"
$heartbeatPath = Join-Path $runRoot "$RunId.heartbeat.json"
$pidManifestPath = Join-Path $runRoot "$RunId.pids.json"
$manifestPath = Join-Path $runRoot "$RunId.manifest.json"
$summaryCsvPath = Join-Path $runRoot "$RunId.summary.csv"
$mismatchCsvPath = Join-Path $runRoot "$RunId.mismatches.csv"

Write-Host "TSIS quotes clone parity audit"
Write-Host "Run ID: $RunId"
Write-Host "Source: $script:sourceRoot"
Write-Host "Target: $script:targetRoot"
Write-Host "Log root: $runRoot"
Write-Host "Workers: $Workers"
Write-Host "HashMode: $HashMode"
Write-Host "UseRobocopyDryRun: $UseRobocopyDryRun"
Write-Host "Shard: $ShardIndex / $ShardCount"
Write-Host ""

Write-Heartbeat -Path $heartbeatPath -Status "running" -Stage "build_pre_manifest" -CurrentIndex 0 -TotalCount 0 -Item "" -MismatchCount 0 -FailedWorkerCount 0

$sourceTickers = Get-TickerDirs -Root $script:sourceRoot
$targetTickers = Get-TickerDirs -Root $script:targetRoot
$targetSet = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($ticker in $targetTickers) { [void]$targetSet.Add($ticker) }
$sourceSet = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($ticker in $sourceTickers) { [void]$sourceSet.Add($ticker) }

$missingTopLevel = @($sourceTickers | Where-Object { -not $targetSet.Contains($_) })
$extraTopLevel = @($targetTickers | Where-Object { -not $sourceSet.Contains($_) })

$auditTickers = @($sourceTickers)
if (-not [string]::IsNullOrWhiteSpace($StartAtTicker)) {
    $auditTickers = @($auditTickers | Where-Object { [StringComparer]::OrdinalIgnoreCase.Compare($_, $StartAtTicker) -ge 0 })
}
if ($ShardCount -gt 1) {
    if ($ShardIndex -ge $ShardCount) {
        throw "ShardIndex must be lower than ShardCount. Got ShardIndex=$ShardIndex ShardCount=$ShardCount"
    }
    $totalBeforeShard = $auditTickers.Count
    $startOffset = [int][Math]::Floor($totalBeforeShard * ($ShardIndex / [double]$ShardCount))
    $endOffsetExclusive = [int][Math]::Floor($totalBeforeShard * (($ShardIndex + 1) / [double]$ShardCount))
    $takeCount = [Math]::Max(0, $endOffsetExclusive - $startOffset)
    $auditTickers = @($auditTickers | Select-Object -Skip $startOffset -First $takeCount)
}
if ($MaxTickers -gt 0) {
    $auditTickers = @($auditTickers | Select-Object -First $MaxTickers)
}

$preManifest = [ordered]@{
    run_id = $RunId
    script_path = $scriptPath
    started_at_utc = $scriptStartedAtUtc.ToString("o")
    source_root = $script:sourceRoot
    target_root = $script:targetRoot
    log_root = $runRoot
    workers = $Workers
    hash_mode = $HashMode
    use_robocopy_dry_run = [bool]$UseRobocopyDryRun
    shard_index = $ShardIndex
    shard_count = $ShardCount
    max_tickers = $MaxTickers
    start_at_ticker = $StartAtTicker
    source_ticker_dirs = $sourceTickers.Count
    target_ticker_dirs = $targetTickers.Count
    audit_ticker_count = $auditTickers.Count
    missing_top_level_count = $missingTopLevel.Count
    extra_top_level_count = $extraTopLevel.Count
    missing_top_level_sample = @($missingTopLevel | Select-Object -First 50)
    extra_top_level_sample = @($extraTopLevel | Select-Object -First 50)
    git = Get-GitSnapshot
    parity_policy = "pass requires target ticker exists, recursive file counts equal, recursive bytes equal, relative path inventory equal, relative file sizes equal, optional robocopy clean when enabled, and hash pass when hash mode applies"
}
Write-JsonAtomic -Path $preManifestPath -Payload $preManifest -Depth 8

$monitorCommand = 'powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "{0}" -RunId "{1}" -Compact -Watch' -f $runRoot, $RunId
$pidManifest = [ordered]@{
    run_id = $RunId
    observed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    wrapper_pid = $PID
    active_pid = $PID
    active_stage = "ticker_parity_audit"
    command = "powershell"
    script_path = $scriptPath
    monitor_command = $monitorCommand
}
Write-JsonAtomic -Path $pidManifestPath -Payload $pidManifest -Depth 8

Write-Host "Pre-manifest: $preManifestPath"
Write-Host "Heartbeat: $heartbeatPath"
Write-Host "PID manifest: $pidManifestPath"
Write-Host "Monitor command:"
Write-Host "  $monitorCommand"
Write-Host ""

if ($auditTickers.Count -eq 0) {
    throw "No tickers selected for audit."
}

$effectiveWorkers = [Math]::Min($Workers, $auditTickers.Count)
$chunks = @()
for ($i = 0; $i -lt $effectiveWorkers; $i++) {
    $chunks += ,([System.Collections.Generic.List[string]]::new())
}
for ($i = 0; $i -lt $auditTickers.Count; $i++) {
    $chunks[$i % $effectiveWorkers].Add($auditTickers[$i])
}

$workerInputFiles = @()
for ($i = 0; $i -lt $effectiveWorkers; $i++) {
    $path = Join-Path $workerRoot ("worker_{0:000}.txt" -f $i)
    $chunks[$i] | Set-Content -LiteralPath $path -Encoding UTF8
    $workerInputFiles += $path
}

$workerScript = {
    param(
        [string]$InputFile,
        [string]$SourceRoot,
        [string]$TargetRoot,
        [string]$ResultRoot,
        [string]$MismatchRoot,
        [string]$HashMode,
        [bool]$UseRobocopyDryRun
    )

    Set-StrictMode -Version Latest
    $ErrorActionPreference = "Stop"

    function Write-JsonAtomicWorker {
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
        $Payload | ConvertTo-Json -Depth $Depth | Set-Content -LiteralPath $tmp -Encoding UTF8
        if (Test-Path -LiteralPath $Path -PathType Leaf) {
            Remove-Item -LiteralPath $Path -Force
        }
        [System.IO.File]::Move($tmp, $Path)
    }

    function Get-RelativePath {
        param([string]$Root, [string]$Path)
        $rootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd("\") + "\"
        $pathFull = [System.IO.Path]::GetFullPath($Path)
        return $pathFull.Substring($rootFull.Length)
    }

    function Get-FileInventory {
        param([Parameter(Mandatory = $true)][string]$Root)
        $count = 0L
        $bytes = 0L
        $map = @{}
        $errors = [System.Collections.Generic.List[string]]::new()
        if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
            return [ordered]@{ exists = $false; file_count = 0L; bytes = 0L; file_map = $map; errors = @("missing_root") }
        }
        $pending = [System.Collections.Generic.Stack[string]]::new()
        $pending.Push($Root)
        while ($pending.Count -gt 0) {
            $current = $pending.Pop()
            try {
                foreach ($filePath in [System.IO.Directory]::EnumerateFiles($current, "*", [System.IO.SearchOption]::TopDirectoryOnly)) {
                    try {
                        $info = [System.IO.FileInfo]::new($filePath)
                        $rel = Get-RelativePath -Root $Root -Path $filePath
                        $count += 1
                        $bytes += [int64]$info.Length
                        $map[$rel] = [int64]$info.Length
                    }
                    catch {
                        $errors.Add("file_error:${filePath}:$($_.Exception.Message)")
                    }
                }
            }
            catch {
                $errors.Add("enumerate_files_error:${current}:$($_.Exception.Message)")
            }

            try {
                foreach ($dirPath in [System.IO.Directory]::EnumerateDirectories($current, "*", [System.IO.SearchOption]::TopDirectoryOnly)) {
                    try {
                        $dirInfo = [System.IO.DirectoryInfo]::new($dirPath)
                        if (($dirInfo.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                            $errors.Add("skipped_reparse_point:${dirPath}")
                            continue
                        }
                        $pending.Push($dirPath)
                    }
                    catch {
                        $errors.Add("directory_error:${dirPath}:$($_.Exception.Message)")
                    }
                }
            }
            catch {
                $errors.Add("enumerate_directories_error:${current}:$($_.Exception.Message)")
            }
        }
        return [ordered]@{ exists = $true; file_count = $count; bytes = $bytes; file_map = $map; errors = @($errors) }
    }

    function Get-FileHashMap {
        param([Parameter(Mandatory = $true)][string]$Root)
        $map = @{}
        $errors = [System.Collections.Generic.List[string]]::new()
        if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
            return [ordered]@{ hashes = $map; errors = @("missing_root") }
        }
        $pending = [System.Collections.Generic.Stack[string]]::new()
        $pending.Push($Root)
        while ($pending.Count -gt 0) {
            $current = $pending.Pop()
            try {
                foreach ($filePath in [System.IO.Directory]::EnumerateFiles($current, "*", [System.IO.SearchOption]::TopDirectoryOnly)) {
                    try {
                        $rel = Get-RelativePath -Root $Root -Path $filePath
                        $hash = (Get-FileHash -LiteralPath $filePath -Algorithm SHA256).Hash
                        $map[$rel] = $hash
                    }
                    catch {
                        $errors.Add("hash_error:${filePath}:$($_.Exception.Message)")
                    }
                }
            }
            catch {
                $errors.Add("hash_enumerate_files_error:${current}:$($_.Exception.Message)")
            }

            try {
                foreach ($dirPath in [System.IO.Directory]::EnumerateDirectories($current, "*", [System.IO.SearchOption]::TopDirectoryOnly)) {
                    try {
                        $dirInfo = [System.IO.DirectoryInfo]::new($dirPath)
                        if (($dirInfo.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                            $errors.Add("hash_skipped_reparse_point:${dirPath}")
                            continue
                        }
                        $pending.Push($dirPath)
                    }
                    catch {
                        $errors.Add("hash_directory_error:${dirPath}:$($_.Exception.Message)")
                    }
                }
            }
            catch {
                $errors.Add("hash_enumerate_directories_error:${current}:$($_.Exception.Message)")
            }
        }
        return [ordered]@{ hashes = $map; errors = @($errors) }
    }

    <#
    Legacy direct-recursive implementation intentionally disabled. It followed
    filesystem reparse points, unlike robocopy /XJ, and can hang on large trees.
    #>
    function Get-FileHashMap_Disabled {
        param([Parameter(Mandatory = $true)][string]$Root)
        $map = @{}
        $errors = [System.Collections.Generic.List[string]]::new()
        if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
            return [ordered]@{ hashes = $map; errors = @("missing_root") }
        }
        try {
            foreach ($filePath in [System.IO.Directory]::EnumerateFiles($Root, "*", [System.IO.SearchOption]::AllDirectories)) {
                try {
                    $rel = Get-RelativePath -Root $Root -Path $filePath
                    $hash = (Get-FileHash -LiteralPath $filePath -Algorithm SHA256).Hash
                    $map[$rel] = $hash
                }
                catch {
                    $errors.Add("hash_error:${filePath}:$($_.Exception.Message)")
                }
            }
        }
        catch {
            $errors.Add("hash_enumerate_error:$($_.Exception.Message)")
        }
        return [ordered]@{ hashes = $map; errors = @($errors) }
    }

    function Invoke-RobocopyDryRun {
        param([string]$Source, [string]$Target)
        if (-not (Test-Path -LiteralPath $Source -PathType Container) -or
            -not (Test-Path -LiteralPath $Target -PathType Container)) {
            return [ordered]@{ exit_code = $null; clean = $false; errors = @("source_or_target_missing") }
        }
        $args = @(
            $Source,
            $Target,
            "*.*",
            "/MIR",
            "/L",
            "/FFT",
            "/DST",
            "/XJ",
            "/R:0",
            "/W:0",
            "/BYTES",
            "/MT:1",
            "/NP",
            "/NDL",
            "/NFL",
            "/NJH",
            "/NJS"
        )
        $errors = @()
        try {
            $null = & robocopy @args
            $exitCode = $LASTEXITCODE
            return [ordered]@{ exit_code = $exitCode; clean = ($exitCode -eq 0); errors = $errors }
        }
        catch {
            return [ordered]@{ exit_code = $null; clean = $false; errors = @($_.Exception.Message) }
        }
    }

    $tickers = @(Get-Content -LiteralPath $InputFile | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $workerStartedAt = (Get-Date).ToUniversalTime()
    foreach ($ticker in $tickers) {
        $startedAt = (Get-Date).ToUniversalTime()
        $source = Join-Path $SourceRoot $ticker
        $target = Join-Path $TargetRoot $ticker
        $sourceMeasure = Get-FileInventory -Root $source
        $targetMeasure = Get-FileInventory -Root $target
        $robocopy = if ($UseRobocopyDryRun) {
            Invoke-RobocopyDryRun -Source $source -Target $target
        }
        else {
            [ordered]@{ exit_code = $null; clean = $null; errors = @("not_enabled") }
        }

        $countDelta = [int64]$targetMeasure.file_count - [int64]$sourceMeasure.file_count
        $bytesDelta = [int64]$targetMeasure.bytes - [int64]$sourceMeasure.bytes
        $sourceKeys = @($sourceMeasure.file_map.Keys)
        $targetKeys = @($targetMeasure.file_map.Keys)
        $targetSet = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
        foreach ($key in $targetKeys) { [void]$targetSet.Add($key) }
        $sourceSet = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
        foreach ($key in $sourceKeys) { [void]$sourceSet.Add($key) }
        $missingRelative = @($sourceKeys | Where-Object { -not $targetSet.Contains($_) })
        $extraRelative = @($targetKeys | Where-Object { -not $sourceSet.Contains($_) })
        $sizeMismatch = [System.Collections.Generic.List[string]]::new()
        foreach ($key in $sourceKeys) {
            if ($targetSet.Contains($key) -and ([int64]$sourceMeasure.file_map[$key] -ne [int64]$targetMeasure.file_map[$key])) {
                $sizeMismatch.Add($key)
            }
        }

        $robocopyOk = if ($UseRobocopyDryRun) { [bool]$robocopy.clean } else { $true }
        $structuralOk = [bool]$sourceMeasure.exists -and [bool]$targetMeasure.exists -and
            ($countDelta -eq 0) -and ($bytesDelta -eq 0) -and
            ($missingRelative.Count -eq 0) -and ($extraRelative.Count -eq 0) -and
            ($sizeMismatch.Count -eq 0) -and $robocopyOk

        $hashChecked = $false
        $hashOk = $null
        $hashMismatchCount = $null
        $hashMissingInTargetCount = $null
        $hashExtraInTargetCount = $null
        $hashErrors = @()
        $shouldHash = ($HashMode -eq "Full") -or (($HashMode -eq "MismatchesOnly") -and (-not $structuralOk))
        if ($shouldHash) {
            $hashChecked = $true
            $sourceHashes = Get-FileHashMap -Root $source
            $targetHashes = Get-FileHashMap -Root $target
            $hashErrors = @($sourceHashes.errors + $targetHashes.errors)
            $sourceKeys = @($sourceHashes.hashes.Keys)
            $targetKeys = @($targetHashes.hashes.Keys)
            $targetSet = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
            foreach ($key in $targetKeys) { [void]$targetSet.Add($key) }
            $sourceSet = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
            foreach ($key in $sourceKeys) { [void]$sourceSet.Add($key) }
            $missing = @($sourceKeys | Where-Object { -not $targetSet.Contains($_) })
            $extra = @($targetKeys | Where-Object { -not $sourceSet.Contains($_) })
            $mismatch = 0
            foreach ($key in $sourceKeys) {
                if ($targetSet.Contains($key) -and $sourceHashes.hashes[$key] -ne $targetHashes.hashes[$key]) {
                    $mismatch += 1
                }
            }
            $hashMismatchCount = $mismatch
            $hashMissingInTargetCount = $missing.Count
            $hashExtraInTargetCount = $extra.Count
            $hashOk = ($hashErrors.Count -eq 0 -and $mismatch -eq 0 -and $missing.Count -eq 0 -and $extra.Count -eq 0)
        }

        $parityOk = $structuralOk -and (($hashChecked -eq $false) -or ($hashOk -eq $true))
        $result = [ordered]@{
            ticker = $ticker
            started_at_utc = $startedAt.ToString("o")
            ended_at_utc = (Get-Date).ToUniversalTime().ToString("o")
            source = $source
            target = $target
            source_exists = [bool]$sourceMeasure.exists
            target_exists = [bool]$targetMeasure.exists
            source_file_count = [int64]$sourceMeasure.file_count
            target_file_count = [int64]$targetMeasure.file_count
            source_bytes = [int64]$sourceMeasure.bytes
            target_bytes = [int64]$targetMeasure.bytes
            file_count_delta = $countDelta
            bytes_delta = $bytesDelta
            missing_relative_count = $missingRelative.Count
            extra_relative_count = $extraRelative.Count
            size_mismatch_count = $sizeMismatch.Count
            missing_relative_sample = @($missingRelative | Select-Object -First 20)
            extra_relative_sample = @($extraRelative | Select-Object -First 20)
            size_mismatch_sample = @($sizeMismatch | Select-Object -First 20)
            source_errors = @($sourceMeasure.errors)
            target_errors = @($targetMeasure.errors)
            use_robocopy_dry_run = $UseRobocopyDryRun
            robocopy_exit_code = $robocopy.exit_code
            robocopy_clean = $robocopy.clean
            robocopy_errors = @($robocopy.errors)
            hash_mode = $HashMode
            hash_checked = $hashChecked
            hash_ok = $hashOk
            hash_mismatch_count = $hashMismatchCount
            hash_missing_in_target_count = $hashMissingInTargetCount
            hash_extra_in_target_count = $hashExtraInTargetCount
            hash_errors = @($hashErrors)
            parity_ok = $parityOk
        }

        $resultPath = Join-Path $ResultRoot "$ticker.json"
        Write-JsonAtomicWorker -Path $resultPath -Payload $result -Depth 8
        if (-not $parityOk) {
            $mismatchPath = Join-Path $MismatchRoot "$ticker.json"
            Write-JsonAtomicWorker -Path $mismatchPath -Payload $result -Depth 8
        }
    }
    return [ordered]@{
        input_file = $InputFile
        ticker_count = $tickers.Count
        started_at_utc = $workerStartedAt.ToString("o")
        ended_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        worker_pid = $PID
    }
}

Write-Heartbeat -Path $heartbeatPath -Status "running" -Stage "ticker_parity_audit" -CurrentIndex 0 -TotalCount $auditTickers.Count -Item "" -MismatchCount 0 -FailedWorkerCount 0

$jobs = @()
foreach ($inputFile in $workerInputFiles) {
    $jobs += Start-Job -ScriptBlock $workerScript -ArgumentList @(
        $inputFile,
        $script:sourceRoot,
        $script:targetRoot,
        $tickerResultsRoot,
        $mismatchRoot,
        $HashMode,
        [bool]$UseRobocopyDryRun
    )
}

$failedWorkerCount = 0
$lastPrintedCompleted = -1
while ($true) {
    $completedCount = @(Get-ChildItem -LiteralPath $tickerResultsRoot -Filter "*.json" -File -ErrorAction SilentlyContinue).Count
    $mismatchCount = @(Get-ChildItem -LiteralPath $mismatchRoot -Filter "*.json" -File -ErrorAction SilentlyContinue).Count
    $latestFile = Get-ChildItem -LiteralPath $tickerResultsRoot -Filter "*.json" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
    $latestTicker = if ($latestFile -ne $null) { [System.IO.Path]::GetFileNameWithoutExtension($latestFile.Name) } else { "" }
    $runningJobs = @($jobs | Where-Object { $_.State -eq "Running" })
    $failedJobs = @($jobs | Where-Object { $_.State -eq "Failed" })
    $failedWorkerCount = $failedJobs.Count
    Write-Heartbeat -Path $heartbeatPath -Status "running" -Stage "ticker_parity_audit" -CurrentIndex $completedCount -TotalCount $auditTickers.Count -Item $latestTicker -MismatchCount $mismatchCount -FailedWorkerCount $failedWorkerCount

    $now = (Get-Date).ToString("s")
    $freeGb = Get-DriveFreeGb -PathValue $script:targetRoot
    if ($completedCount -ne $lastPrintedCompleted -or $runningJobs.Count -eq 0) {
        Write-Host ("[{0}] status=running stage=ticker_parity_audit workers_running={1} progress={2}/{3} mismatches={4} latest={5} output_free_GB={6}" -f $now, $runningJobs.Count, $completedCount, $auditTickers.Count, $mismatchCount, $latestTicker, $freeGb)
        $lastPrintedCompleted = $completedCount
    }

    if ($runningJobs.Count -eq 0) {
        break
    }
    Start-Sleep -Seconds $HeartbeatSeconds
}

$workerResults = @()
foreach ($job in $jobs) {
    try {
        $workerResults += Receive-Job -Job $job -ErrorAction Stop
    }
    catch {
        $workerResults += [ordered]@{
            job_id = $job.Id
            state = $job.State
            error = $_.Exception.Message
        }
    }
}
Remove-Job -Job $jobs -Force -ErrorAction SilentlyContinue

$resultFiles = @(Get-ChildItem -LiteralPath $tickerResultsRoot -Filter "*.json" -File -ErrorAction SilentlyContinue | Sort-Object Name)
$results = @()
foreach ($file in $resultFiles) {
    try {
        $results += (Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json)
    }
    catch {
        $results += [PSCustomObject]@{
            ticker = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
            parity_ok = $false
            read_error = $_.Exception.Message
        }
    }
}

$mismatches = @($results | Where-Object { $_.parity_ok -ne $true })
$missingResults = @($auditTickers | Where-Object { -not (Test-Path -LiteralPath (Join-Path $tickerResultsRoot "$_.json") -PathType Leaf) })

$results |
    Select-Object ticker,parity_ok,source_file_count,target_file_count,file_count_delta,source_bytes,target_bytes,bytes_delta,missing_relative_count,extra_relative_count,size_mismatch_count,use_robocopy_dry_run,robocopy_exit_code,robocopy_clean,hash_mode,hash_checked,hash_ok,hash_mismatch_count,hash_missing_in_target_count,hash_extra_in_target_count |
    Export-Csv -LiteralPath $summaryCsvPath -NoTypeInformation -Encoding UTF8

$mismatches |
    Select-Object ticker,parity_ok,source_exists,target_exists,source_file_count,target_file_count,file_count_delta,source_bytes,target_bytes,bytes_delta,missing_relative_count,extra_relative_count,size_mismatch_count,use_robocopy_dry_run,robocopy_exit_code,robocopy_clean,hash_checked,hash_ok,hash_mismatch_count,hash_missing_in_target_count,hash_extra_in_target_count |
    Export-Csv -LiteralPath $mismatchCsvPath -NoTypeInformation -Encoding UTF8

$endedAtUtc = (Get-Date).ToUniversalTime()
$failedWorkerCount = @($jobs | Where-Object { $_.State -eq "Failed" }).Count
$finalStatus = if ($mismatches.Count -eq 0 -and $missingResults.Count -eq 0 -and $failedWorkerCount -eq 0) { "completed_pass" } else { "completed_fail" }
$manifest = [ordered]@{
    run_id = $RunId
    status = $finalStatus
    script_path = $scriptPath
    source_root = $script:sourceRoot
    target_root = $script:targetRoot
    log_root = $runRoot
    started_at_utc = $scriptStartedAtUtc.ToString("o")
    ended_at_utc = $endedAtUtc.ToString("o")
    elapsed_seconds = [Math]::Round(($endedAtUtc - $scriptStartedAtUtc).TotalSeconds, 1)
    workers = $Workers
    hash_mode = $HashMode
    use_robocopy_dry_run = [bool]$UseRobocopyDryRun
    shard_index = $ShardIndex
    shard_count = $ShardCount
    source_ticker_dirs = $sourceTickers.Count
    target_ticker_dirs = $targetTickers.Count
    audit_ticker_count = $auditTickers.Count
    result_count = $results.Count
    missing_result_count = $missingResults.Count
    missing_result_sample = @($missingResults | Select-Object -First 50)
    parity_ok_count = @($results | Where-Object { $_.parity_ok -eq $true }).Count
    mismatch_count = $mismatches.Count
    mismatch_sample = @($mismatches | Select-Object -First 50 ticker,source_file_count,target_file_count,file_count_delta,source_bytes,target_bytes,bytes_delta,robocopy_exit_code,robocopy_clean,hash_checked,hash_ok)
    missing_top_level_count = $missingTopLevel.Count
    extra_top_level_count = $extraTopLevel.Count
    summary_csv = $summaryCsvPath
    mismatch_csv = $mismatchCsvPath
    ticker_results_root = $tickerResultsRoot
    mismatch_root = $mismatchRoot
    pre_manifest_path = $preManifestPath
    heartbeat_path = $heartbeatPath
    pid_manifest_path = $pidManifestPath
    worker_results = $workerResults
    pass_policy = "pass requires all selected tickers to produce result, parity_ok true for all results, no worker failures; default parity compares relative paths and byte lengths, optional robocopy/hash layers are recorded when enabled"
}
Write-JsonAtomic -Path $manifestPath -Payload $manifest -Depth 8

Write-Heartbeat -Path $heartbeatPath -Status $finalStatus -Stage "final_manifest_written" -CurrentIndex $results.Count -TotalCount $auditTickers.Count -Item "" -MismatchCount $mismatches.Count -FailedWorkerCount $failedWorkerCount -Message "manifest=$manifestPath"

Write-Host ""
Write-Host "Completed."
Write-Host "Status: $finalStatus"
Write-Host "Audit tickers: $($auditTickers.Count)"
Write-Host "Results: $($results.Count)"
Write-Host "Mismatches: $($mismatches.Count)"
Write-Host "Missing results: $($missingResults.Count)"
Write-Host "Manifest: $manifestPath"
Write-Host "Summary CSV: $summaryCsvPath"
Write-Host "Mismatch CSV: $mismatchCsvPath"

if ($finalStatus -ne "completed_pass") {
    exit 2
}
