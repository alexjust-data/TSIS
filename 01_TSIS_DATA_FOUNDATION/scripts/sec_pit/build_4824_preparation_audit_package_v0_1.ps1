param(
    [string]$TargetZip = 'C:\TSIS_Data\00_CTO\04_MARKET_STATES_CREATION\_DESCAGRA_DATOS_NECESARIA_\SEC_PIT_4824_PREPARATION_AUDIT_PACKAGE_v0_1.zip'
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem

$workspace = 'C:\TSIS_Data'
$df = Join-Path $workspace '01_TSIS_DATA_FOUNDATION'
$cto = Join-Path $workspace '00_CTO\04_MARKET_STATES_CREATION\_DESCAGRA_DATOS_NECESARIA_'
$dossier = Join-Path $df '01_foundations\inspection_dossiers\sec_pit'
$preflight = Join-Path $workspace 'runtime\sec_pit_4824_descending_acquisition_v0_1\preflight_20260813T215254Z'
$runtimeRoot = Join-Path $workspace 'runtime\sec_pit_4824_preparation_audit_package_v0_1'
$stage = Join-Path $runtimeRoot 'stage'
$tempZip = Join-Path $runtimeRoot 'SEC_PIT_4824_PREPARATION_AUDIT_PACKAGE_v0_1.new.zip'
$manifestName = 'PACKAGE_FILE_MANIFEST.csv'
$expectedEntryCount = 26

foreach ($required in @($workspace, $df, $cto, $dossier, $preflight)) {
    if (-not (Test-Path -LiteralPath $required -PathType Container)) {
        throw "Required package source root missing: $required"
    }
}
if (Test-Path -LiteralPath $TargetZip) {
    throw "Target ZIP already exists; version or remove explicitly: $TargetZip"
}

New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null
$resolvedRuntime = (Resolve-Path -LiteralPath $runtimeRoot).Path
if (Test-Path -LiteralPath $stage) {
    $resolvedStage = (Resolve-Path -LiteralPath $stage).Path
    if (-not $resolvedStage.StartsWith($resolvedRuntime, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Unsafe staging path: $resolvedStage"
    }
    Remove-Item -LiteralPath $resolvedStage -Recurse -Force
}
New-Item -ItemType Directory -Path $stage | Out-Null

function Copy-AuditFile {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$RelativeDestination
    )
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        throw "Missing audit source: $Source"
    }
    if ([IO.Path]::IsPathRooted($RelativeDestination) -or $RelativeDestination -match '(^|[\\/])\.\.([\\/]|$)') {
        throw "Unsafe relative destination: $RelativeDestination"
    }
    $destination = Join-Path $stage $RelativeDestination
    New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
    Copy-Item -LiteralPath $Source -Destination $destination
}

Copy-AuditFile (Join-Path $cto 'SEC_PIT_4824_PREPARATION_AUDIT_PACKAGE_CONTENTS_v0_1.md') '00_START_HERE.md'

Copy-AuditFile (Join-Path $workspace 'LONG_RUNNING_OPERATIONS_CONTRACT.md') '01_AUTHORITY\LONG_RUNNING_OPERATIONS_CONTRACT.md'
Copy-AuditFile (Join-Path $cto 'SEC_PIT_FUNDAMENTAL_ACQUISITION_AND_RESOLUTION_CONTRACT_v0_1.md') '01_AUTHORITY\ACQUISITION_AND_RESOLUTION_CONTRACT.md'
Copy-AuditFile (Join-Path $cto 'SEC_PIT_ADAPTIVE_BASELINE_AND_SCALE_GATE_HANDOFF_v0_1.md') '01_AUTHORITY\ADAPTIVE_SCALE_GATE_HANDOFF.md'
Copy-AuditFile (Join-Path $cto 'SEC_PIT_4824_DESCENDING_ACQUISITION_EXECUTION_PLAN_v0_1.md') '01_AUTHORITY\4824_DESCENDING_EXECUTION_PLAN.md'

Copy-AuditFile (Join-Path $dossier 'SEC_PIT_100_CASE_STRATIFIED_SCALE_GATE_READOUT_v0_1.md') '02_PRIOR_EVIDENCE\100_CASE_SCALE_GATE_READOUT.md'
Copy-AuditFile (Join-Path $dossier 'SEC_PIT_EXACT_SHARE_CLASS_RECOVERY_AND_V0_21_READOUT_v0_1.md') '02_PRIOR_EVIDENCE\V0_21_AUTHORITATIVE_READOUT.md'

Copy-AuditFile (Join-Path $dossier 'SEC_PIT_4824_DESCENDING_PREFLIGHT_READOUT_v0_1.md') '03_CURRENT_PREFLIGHT\PREFLIGHT_READOUT.md'
Copy-AuditFile (Join-Path $preflight 'final_manifest.json') '03_CURRENT_PREFLIGHT\final_manifest.json'
Copy-AuditFile (Join-Path $preflight 'cohort_summary.json') '03_CURRENT_PREFLIGHT\cohort_summary.json'
Copy-AuditFile (Join-Path $preflight 'operator_launch_plan.json') '03_CURRENT_PREFLIGHT\operator_launch_plan.json'
Copy-AuditFile (Join-Path $preflight 'full_universe_acquisition_order.csv') '03_CURRENT_PREFLIGHT\full_universe_acquisition_order.csv'
Copy-AuditFile (Join-Path $preflight 'cohort_01_0824.parquet') '03_CURRENT_PREFLIGHT\cohort_01_0824.parquet'

Copy-AuditFile (Join-Path $df 'configs\sec_pit_4824_descending_acquisition_preflight_v0_1.json') '04_NEXT_EXECUTION\sec_pit_4824_descending_acquisition_preflight_v0_1.json'
Copy-AuditFile (Join-Path $df 'scripts\sec_pit\build_4824_descending_acquisition_preflight.py') '04_NEXT_EXECUTION\build_4824_descending_acquisition_preflight.py'
Copy-AuditFile (Join-Path $df 'tests\test_sec_pit_4824_descending_acquisition_preflight.py') '04_NEXT_EXECUTION\test_sec_pit_4824_descending_acquisition_preflight.py'
Copy-AuditFile (Join-Path $df 'scripts\sec_pit\run_submissions_metadata_profile.py') '04_NEXT_EXECUTION\run_submissions_metadata_profile.py'
Copy-AuditFile (Join-Path $df 'scripts\sec_pit\monitor_sec_pit_run.ps1') '04_NEXT_EXECUTION\monitor_sec_pit_run.ps1'
foreach ($component in @('client.py', 'metadata.py', 'models.py', 'storage.py', 'telemetry.py')) {
    Copy-AuditFile (Join-Path $df "scripts\sec_pit\$component") "04_NEXT_EXECUTION\$component"
}

Copy-AuditFile (Join-Path $df 'scripts\sec_pit\build_4824_preparation_audit_package_v0_1.ps1') '05_PACKAGE_PROVENANCE\build_4824_preparation_audit_package_v0_1.ps1'

$gitBranch = (git -C $workspace branch --show-current).Trim()
$gitCommit = (git -C $workspace rev-parse HEAD).Trim()
$dirtyLines = @(git -C $workspace status --porcelain)
$preflightManifest = Get-Content -LiteralPath (Join-Path $preflight 'final_manifest.json') -Raw | ConvertFrom-Json

[ordered]@{
    package_id = 'SEC_PIT_4824_PREPARATION_AUDIT_PACKAGE_v0_1'
    created_at_utc = [DateTime]::UtcNow.ToString('o')
    purpose = 'MINIMAL_PRE_LAUNCH_AUDIT_HANDOFF_NOT_APPLICATION_ARCHIVE'
    status = 'PREFLIGHT_PASS_METADATA_COHORT_01_AWAITING_HUMAN_LAUNCH'
    expected_zip_entries = $expectedEntryCount
    selected_source_and_evidence_entries = 24
    parent_universe_ticker_rows = 4824
    unique_instrument_ids = 4626
    reused_instrument_identity_groups = 190
    cross_cik_identity_conflict_rows = 8
    cohort_sizes = @(824, 1000, 1000, 1000, 1000)
    priority_order = @('last_observed_date DESC', 'ticker ASC')
    authoritative_preflight_root = $preflight.Replace('\', '/')
    authoritative_preflight_status = $preflightManifest.status
    authoritative_preflight_gate = $preflightManifest.preflight_gate
    authoritative_preflight_network_requests = $preflightManifest.network_requests
    authoritative_preflight_script_sha256 = $preflightManifest.script_sha256
    prior_authority = [ordered]@{
        version = 'v0.21'
        eligible_cases = 99
        os_complete_cases = 71
        float_complete_cases = 28
        formula_or_pit_violations = 0
    }
    next_execution = 'HUMAN_LAUNCH_COHORT_01_SEC_SUBMISSIONS_METADATA_ONLY'
    primary_document_acquisition = 'NOT_AUTHORIZED'
    institutional_promotion = 'NOT_AUTHORIZED'
    verified_sec_pit_test_count = 288
    git_branch = $gitBranch
    git_commit_ancestry = $gitCommit
    git_dirty_state = ($dirtyLines.Count -gt 0)
    source_snapshot_rule = 'INCLUDED_FILE_HASHES_ARE_AUTHORITATIVE_BECAUSE_WORKTREE_IS_UNCOMMITTED'
    excluded_by_design = @(
        'raw SEC payloads',
        'content-addressed SEC objects',
        'primary documents and complete submissions',
        'daily resolution Parquets and full runtime trees',
        'historical duplicate or rejected readouts',
        'unrelated application source and tests',
        'Trading Activity, backtest and Graphify artifacts'
    )
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $stage 'PACKAGE_BUILD_METADATA.json') -Encoding utf8

$sourceRows = @(
    Get-ChildItem -LiteralPath $stage -Recurse -File |
        Where-Object Name -ne $manifestName |
        Sort-Object FullName |
        ForEach-Object {
            [pscustomobject]@{
                relative_path = $_.FullName.Substring($stage.Length + 1).Replace('\', '/')
                bytes = $_.Length
                sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            }
        }
)
if ($sourceRows.Count -ne ($expectedEntryCount - 1)) {
    throw "Allowlist gate failed before manifest: expected $($expectedEntryCount - 1), got $($sourceRows.Count)"
}
$sourceRows | Export-Csv -LiteralPath (Join-Path $stage $manifestName) -NoTypeInformation -Encoding utf8

$stageFiles = @(Get-ChildItem -LiteralPath $stage -Recurse -File | Sort-Object FullName)
if ($stageFiles.Count -ne $expectedEntryCount) {
    throw "Stage entry gate failed: expected $expectedEntryCount, got $($stageFiles.Count)"
}
$stageNames = @($stageFiles | ForEach-Object { $_.FullName.Substring($stage.Length + 1).Replace('\', '/') })
if ($stageNames.Count -ne @($stageNames | Select-Object -Unique).Count) {
    throw 'Duplicate stage entry names detected'
}

if (Test-Path -LiteralPath $tempZip) {
    Remove-Item -LiteralPath $tempZip -Force
}
[IO.Compression.ZipFile]::CreateFromDirectory(
    $stage,
    $tempZip,
    [IO.Compression.CompressionLevel]::Optimal,
    $false
)

$manifestByPath = @{}
foreach ($row in $sourceRows) {
    $manifestByPath[[string]$row.relative_path] = $row
}
$archive = [IO.Compression.ZipFile]::OpenRead($tempZip)
try {
    $entries = @($archive.Entries | Where-Object { $_.Name })
    $names = @($entries | ForEach-Object { $_.FullName.Replace('\', '/') })
    if ($entries.Count -ne $expectedEntryCount) {
        throw "ZIP entry gate failed: expected $expectedEntryCount, got $($entries.Count)"
    }
    if ($names.Count -ne @($names | Select-Object -Unique).Count) {
        throw 'Duplicate ZIP entry names detected'
    }
    foreach ($name in $names) {
        if ($name.StartsWith('/') -or $name -match '(^|/)\.\.(/|$)') {
            throw "Unsafe ZIP entry path: $name"
        }
    }
    foreach ($entry in $entries) {
        $name = $entry.FullName.Replace('\', '/')
        $stream = $entry.Open()
        try {
            $hasher = [Security.Cryptography.SHA256]::Create()
            try {
                $digest = [BitConverter]::ToString($hasher.ComputeHash($stream)).Replace('-', '').ToLowerInvariant()
            } finally {
                $hasher.Dispose()
            }
        } finally {
            $stream.Dispose()
        }
        if ($name -eq $manifestName) {
            continue
        }
        if (-not $manifestByPath.ContainsKey($name)) {
            throw "ZIP entry absent from file manifest: $name"
        }
        $expected = $manifestByPath[$name]
        if ([int64]$entry.Length -ne [int64]$expected.bytes -or $digest -ne [string]$expected.sha256) {
            throw "ZIP hash/size mismatch: $name"
        }
    }
    $entryCount = $entries.Count
    $uncompressedBytes = ($entries | Measure-Object Length -Sum).Sum
} finally {
    $archive.Dispose()
}

New-Item -ItemType Directory -Path (Split-Path -Parent $TargetZip) -Force | Out-Null
Move-Item -LiteralPath $tempZip -Destination $TargetZip

[ordered]@{
    target_zip = $TargetZip
    entries = $entryCount
    manifested_entries = $sourceRows.Count
    uncompressed_bytes = $uncompressedBytes
    zip_bytes = (Get-Item -LiteralPath $TargetZip).Length
    zip_sha256 = (Get-FileHash -LiteralPath $TargetZip -Algorithm SHA256).Hash.ToLowerInvariant()
    validation = 'EXACT_26_ENTRY_ALLOWLIST_UNIQUE_SAFE_PATH_FULL_DECOMPRESSION_SHA256_AND_SIZE_PASS'
} | ConvertTo-Json -Depth 4
