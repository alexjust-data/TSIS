<# 
Clone D:\quotes into E:\TSIS\data\quotes_ as a safe staging root.

Default mode is dry-run. Use -Run for the real copy.

Examples:
  powershell -ExecutionPolicy Bypass -File .\scripts\data_ops\clone_quotes_to_staging.ps1

  powershell -ExecutionPolicy Bypass -File .\scripts\data_ops\clone_quotes_to_staging.ps1 -Run

  powershell -ExecutionPolicy Bypass -File .\scripts\data_ops\clone_quotes_to_staging.ps1 -Run -AllowNonEmptyTarget

  powershell -ExecutionPolicy Bypass -File .\scripts\data_ops\clone_quotes_to_staging.ps1 -Run -SubPath "SGC\year=2013\month=11\day=04"
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$SourceRoot = "D:\quotes",

    [Parameter()]
    [string]$TargetRoot = "E:\TSIS\data\quotes_",

    [Parameter()]
    [string]$LogRoot = "E:\TSIS\data\data_ops_manifests\quotes_clone",

    [Parameter()]
    [string[]]$SubPath = @(),

    [Parameter()]
    [switch]$Run,

    [Parameter()]
    [switch]$AllowNonEmptyTarget,

    [Parameter()]
    [switch]$VerboseFileList,

    [Parameter()]
    [switch]$Unbuffered,

    [Parameter()]
    [ValidateRange(1, 128)]
    [int]$ThreadCount = 32,

    [Parameter()]
    [ValidateRange(0, 100000)]
    [int]$Retries = 3,

    [Parameter()]
    [ValidateRange(0, 3600)]
    [int]$WaitSeconds = 5
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-NormalizedPath {
    param([Parameter(Mandatory = $true)][string]$PathValue)
    return [System.IO.Path]::GetFullPath($PathValue).TrimEnd("\")
}

function Assert-SourceRoot {
    param([Parameter(Mandatory = $true)][string]$PathValue)

    $normalized = Get-NormalizedPath -PathValue $PathValue
    if (-not (Test-Path -LiteralPath $normalized -PathType Container)) {
        throw "Source root does not exist: $normalized"
    }
    return (Get-Item -LiteralPath $normalized).FullName.TrimEnd("\")
}

function Assert-SafeTargetRoot {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$PathValue
    )

    $normalized = Get-NormalizedPath -PathValue $PathValue
    $forbiddenLiveQuotesRoot = Get-NormalizedPath -PathValue "E:\TSIS\data\quotes"

    if ($normalized -ieq $forbiddenLiveQuotesRoot) {
        throw "Refusing to use live quotes root as target: $normalized"
    }
    if ((Split-Path -Leaf $normalized) -ne "quotes_") {
        throw "Target root must end in quotes_ for this staging operation: $normalized"
    }
    if ($normalized -ieq $Source) {
        throw "Source and target resolve to the same path: $normalized"
    }

    $targetParent = Split-Path -Parent $normalized
    if (-not (Test-Path -LiteralPath $targetParent -PathType Container)) {
        throw "Target parent does not exist: $targetParent"
    }

    New-Item -ItemType Directory -Force -Path $normalized | Out-Null
    return (Get-Item -LiteralPath $normalized).FullName.TrimEnd("\")
}

function Test-DirectoryHasAnyEntry {
    param([Parameter(Mandatory = $true)][string]$PathValue)

    $firstEntry = Get-ChildItem -LiteralPath $PathValue -Force -ErrorAction Stop | Select-Object -First 1
    return $null -ne $firstEntry
}

function Quote-Argument {
    param([Parameter(Mandatory = $true)][string]$Value)

    if ($Value -match "\s") {
        return '"' + $Value.Replace('"', '\"') + '"'
    }
    return $Value
}

function Resolve-SafeRelativeSubPath {
    param([Parameter(Mandatory = $true)][string]$PathValue)

    $clean = $PathValue.Trim().Trim("\", "/")
    if ([string]::IsNullOrWhiteSpace($clean)) {
        throw "SubPath cannot be empty."
    }
    if ([System.IO.Path]::IsPathRooted($clean)) {
        throw "SubPath must be relative, not rooted: $PathValue"
    }
    $parts = $clean -split "[\\/]+"
    foreach ($part in $parts) {
        if ($part -eq "." -or $part -eq ".." -or [string]::IsNullOrWhiteSpace($part)) {
            throw "SubPath contains an unsafe segment: $PathValue"
        }
    }
    return ($parts -join "\")
}

$source = Assert-SourceRoot -PathValue $SourceRoot
$target = Assert-SafeTargetRoot -Source $source -PathValue $TargetRoot
$targetWasNonEmpty = Test-DirectoryHasAnyEntry -PathValue $target

if ($Run -and $targetWasNonEmpty -and -not $AllowNonEmptyTarget) {
    throw "Target already has content: $target. Re-run with -AllowNonEmptyTarget if this is an intentional resume/update."
}

New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
$logRootItem = Get-Item -LiteralPath $LogRoot
$runId = "quotes_clone_to_staging_{0}" -f (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$robocopyLog = Join-Path $logRootItem.FullName "$runId.robocopy.log"
$manifestPath = Join-Path $logRootItem.FullName "$runId.manifest.json"

$copyPairs = @()
if ($SubPath.Count -gt 0) {
    foreach ($item in $SubPath) {
        $relative = Resolve-SafeRelativeSubPath -PathValue $item
        $pairSource = Join-Path $source $relative
        if (-not (Test-Path -LiteralPath $pairSource -PathType Container)) {
            throw "SubPath does not exist under source root: $pairSource"
        }
        $copyPairs += [ordered]@{
            relative_subpath = $relative
            source = (Get-Item -LiteralPath $pairSource).FullName.TrimEnd("\")
            target = (Join-Path $target $relative)
        }
    }
}
else {
    $copyPairs += [ordered]@{
        relative_subpath = $null
        source = $source
        target = $target
    }
}

$baseRobocopyOptions = @(
    "/E",
    "/MT:$ThreadCount",
    "/R:$Retries",
    "/W:$WaitSeconds",
    "/FFT",
    "/XJ",
    "/COPY:DAT",
    "/DCOPY:DAT",
    "/IT",
    "/BYTES",
    "/NP",
    "/TEE"
)

if (-not $VerboseFileList) {
    $baseRobocopyOptions += "/NFL"
    $baseRobocopyOptions += "/NDL"
}

if ($Unbuffered) {
    $baseRobocopyOptions += "/J"
}

if (-not $Run) {
    $baseRobocopyOptions += "/L"
}

$mode = if ($Run) { "copy" } else { "dry_run" }
if ($SubPath.Count -gt 0) {
    $mode = "${mode}_scoped"
}
$startedAtUtc = (Get-Date).ToUniversalTime().ToString("o")

Write-Host "TSIS quotes staging clone"
Write-Host "Mode: $mode"
Write-Host "Source: $source"
Write-Host "Target: $target"
if ($SubPath.Count -gt 0) {
    Write-Host "Scoped subpaths:"
    foreach ($pair in $copyPairs) {
        Write-Host "  - $($pair.relative_subpath)"
    }
}
Write-Host "Log: $robocopyLog"
Write-Host "Manifest: $manifestPath"
Write-Host "Robocopy success convention: exit codes 0-7 are success; >=8 is failure."

$pairResults = @()
$robocopyExitCode = 0
$commandText = @()
for ($i = 0; $i -lt $copyPairs.Count; $i++) {
    $pair = $copyPairs[$i]
    $logOption = if ($i -eq 0) { "/LOG:$robocopyLog" } else { "/LOG+:$robocopyLog" }
    $robocopyArgs = @($pair.source, $pair.target) + $baseRobocopyOptions + @($logOption)
    $commandText += "robocopy " + (($robocopyArgs | ForEach-Object { Quote-Argument -Value ([string]$_) }) -join " ")

    Write-Host ""
    if ($null -ne $pair.relative_subpath) {
        Write-Host "Running scoped copy: $($pair.relative_subpath)"
    }

    & robocopy @robocopyArgs
    $pairExitCode = $LASTEXITCODE
    if ($pairExitCode -gt $robocopyExitCode) {
        $robocopyExitCode = $pairExitCode
    }
    $pairResults += [ordered]@{
        relative_subpath = $pair.relative_subpath
        source = $pair.source
        target = $pair.target
        robocopy_exit_code = $pairExitCode
        robocopy_success = [bool]($pairExitCode -le 7)
    }
}
$endedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
$robocopySucceeded = $robocopyExitCode -le 7

$manifest = [ordered]@{
    run_id = $runId
    mode = $mode
    source_root = $source
    target_root = $target
    scoped_subpaths = @($SubPath)
    target_was_non_empty = [bool]$targetWasNonEmpty
    allow_non_empty_target = [bool]$AllowNonEmptyTarget
    thread_count = $ThreadCount
    retries = $Retries
    wait_seconds = $WaitSeconds
    verbose_file_list = [bool]$VerboseFileList
    unbuffered = [bool]$Unbuffered
    started_at_utc = $startedAtUtc
    ended_at_utc = $endedAtUtc
    robocopy_exit_code = $robocopyExitCode
    robocopy_success = [bool]$robocopySucceeded
    robocopy_pair_results = @($pairResults)
    robocopy_success_rule = "0-7 success, >=8 failure"
    copy_policy = [ordered]@{
        deletes_target_extra_files = $false
        uses_mirror = $false
        uses_purge = $false
        overwrites_changed_files_inside_target = [bool]$Run
        preserves_existing_live_quotes_root = $true
        live_quotes_root = "E:\TSIS\data\quotes"
    }
    robocopy_command = @($commandText)
    robocopy_log = $robocopyLog
    manifest_path = $manifestPath
}

$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

if (-not $robocopySucceeded) {
    Write-Error "Robocopy failed with exit code $robocopyExitCode. See log: $robocopyLog"
    exit $robocopyExitCode
}

if ($Run) {
    Write-Host "Copy completed or resumed successfully under robocopy success semantics."
} else {
    Write-Host "Dry-run completed. No files were copied. Review the robocopy summary before running with -Run."
}

exit 0
