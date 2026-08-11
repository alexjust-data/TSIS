param(
    [string]$TargetZip = 'C:\TSIS_Data\00_CTO\04_MARKET_STATES_CREATION\_DESCAGRA_DATOS_NECESARIA_\SEC_PIT_PGAC_EXTERNAL_AUDIT_PACKAGE_v0_1.zip',
    [string]$UpdatedContentsManifest = 'C:\TSIS_Data\00_CTO\04_MARKET_STATES_CREATION\_DESCAGRA_DATOS_NECESARIA_\SEC_PIT_PGAC_EXTERNAL_AUDIT_PACKAGE_CONTENTS_v0_1.md'
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem

$workspace = 'C:\TSIS_Data'
$runtimeRoot = 'C:\TSIS_Data\runtime\sec_pit_external_audit_package_v0_1'
$stage = Join-Path $runtimeRoot 'stage'
$tempZip = Join-Path $runtimeRoot 'SEC_PIT_PGAC_EXTERNAL_AUDIT_PACKAGE_v0_1.new.zip'
$backupZip = Join-Path $runtimeRoot 'SEC_PIT_PGAC_EXTERNAL_AUDIT_PACKAGE_v0_1.pre_stratified.zip'
$cto = 'C:\TSIS_Data\00_CTO\04_MARKET_STATES_CREATION\_DESCAGRA_DATOS_NECESARIA_'
$dossier = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\inspection_dossiers\sec_pit'
$probe = 'C:\TSIS_Data\runtime\sec_pit_stratified_owner_exclusion_v0_1\probes\sec_pit_owner_exclusion_7t_stratified_v0_1_20260811T1600Z'
$runs = 'C:\TSIS_Data\runtime\sec_pit_stratified_owner_exclusion_v0_1\runs'
$acquisition = 'D:\TSIS\fundamental_context\sec_pit_v0_1\runs\sec_pit_owner_exclusion_7t_missing_primary_v0_1_20260811T1600Z'
$df = 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION'

foreach ($required in @($TargetZip, $UpdatedContentsManifest, $probe, $runs, $acquisition)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Required package source missing: $required"
    }
}

New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null
$resolvedRuntime = (Resolve-Path -LiteralPath $runtimeRoot).Path
if (Test-Path -LiteralPath $stage) {
    $resolvedStage = (Resolve-Path -LiteralPath $stage).Path
    if (-not $resolvedStage.StartsWith($resolvedRuntime, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to clear staging outside runtime root: $resolvedStage"
    }
    Remove-Item -LiteralPath $resolvedStage -Recurse -Force
}
New-Item -ItemType Directory -Path $stage | Out-Null

[IO.Compression.ZipFile]::ExtractToDirectory($TargetZip, $stage)

function Copy-AuditFile {
    param([string]$Source, [string]$RelativeDestination)
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        throw "Audit source file missing: $Source"
    }
    $destination = Join-Path $stage $RelativeDestination
    $parent = Split-Path -Parent $destination
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    Copy-Item -LiteralPath $Source -Destination $destination -Force
}

function Copy-AuditDirectoryFiles {
    param([string]$SourceDirectory, [string]$RelativeDestination)
    if (-not (Test-Path -LiteralPath $SourceDirectory -PathType Container)) {
        throw "Audit source directory missing: $SourceDirectory"
    }
    $destination = Join-Path $stage $RelativeDestination
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    Get-ChildItem -LiteralPath $SourceDirectory -File | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $destination $_.Name) -Force
    }
}

Copy-AuditFile $UpdatedContentsManifest 'SEC_PIT_PGAC_EXTERNAL_AUDIT_PACKAGE_CONTENTS_v0_1.md'

foreach ($name in @(
    'SEC_PIT_SEVEN_TICKER_OWNER_EXCLUSION_STRATIFIED_PROBE_READOUT_v0_1.md',
    'SEC_PIT_PGAC_OWNERSHIP_AND_OWNER_EXCLUSION_PROBE_READOUT_v0_1.md',
    'SEC_PIT_PGAC_NO_NETWORK_OS_PROBE_READOUT_v0_1.md'
)) {
    Copy-AuditFile (Join-Path $dossier $name) (Join-Path '01_RESULTADO' $name)
}

foreach ($name in @(
    'SEC_PIT_SEVEN_TICKER_OWNER_EXCLUSION_STRATIFIED_PROBE_PLAN_v0_1.md',
    'SEC_PIT_PGAC_NO_NETWORK_OS_AND_OWNER_EXCLUSION_GATE_PLAN_v0_1.md',
    'SEC_PIT_PGAC_OWNERSHIP_CLASS_RECONCILIATION_PROBE_PLAN_v0_1.md'
)) {
    Copy-AuditFile (Join-Path $cto $name) (Join-Path '02_PROCESO_SEC' $name)
}

Copy-AuditFile `
    (Join-Path $df '01_foundations\canonical_schemas\sec_pit_resolved_daily_states_schema_contract_v0_2.md') `
    '05_SCHEMA_REFERENCIA\sec_pit_resolved_daily_states_schema_contract_v0_2.md'

foreach ($name in @(
    'case_matrix.json',
    'gate_matrix.parquet',
    'document_selection_plan_v0_1.parquet',
    'missing_document_selection.parquet',
    'reusable_acquisition_ledger.jsonl',
    'composite_acquisition_ledger.jsonl',
    'composite_acquisition_ledger.manifest.json',
    'final_manifest.json',
    'owner_exclusion_certification_audit_v0_1.json'
)) {
    Copy-AuditFile (Join-Path $probe $name) (Join-Path '06_EVIDENCIA_ESTRATIFICADA_CONTROL\probe' $name)
}
Copy-AuditDirectoryFiles (Join-Path $probe 'acquisition_probe') '06_EVIDENCIA_ESTRATIFICADA_CONTROL\acquisition_probe'
Copy-AuditDirectoryFiles $acquisition '06_EVIDENCIA_ESTRATIFICADA_CONTROL\acquisition_run'

foreach ($ticker in @('alur', 'bbby', 'bgm', 'bnai', 'domh', 'pgac')) {
    $osRun = Join-Path $runs "sec_pit_${ticker}_os_stratified_v0_5_20260811T1730Z"
    $ownerRun = Join-Path $runs "sec_pit_${ticker}_owner_stratified_v0_5_20260811T2200Z"
    Copy-AuditDirectoryFiles $osRun ("07_RUNS_OS_V0_5\" + $ticker.ToUpperInvariant())
    Copy-AuditDirectoryFiles $ownerRun ("08_RUNS_OWNER_V0_5\" + $ticker.ToUpperInvariant())
}

Copy-AuditFile `
    (Join-Path $df 'configs\sec_pit_owner_exclusion_stratified_probe_v0_1.json') `
    '09_CODIGO_Y_CONFIG\configs\sec_pit_owner_exclusion_stratified_probe_v0_1.json'

foreach ($name in @(
    'build_owner_exclusion_stratified_probe.py',
    'build_composite_acquisition_ledger.py',
    'build_stratified_owner_case_configs.py',
    'run_authorized_primary_acquisition_v0_2.py',
    'run_no_network_os_probe.py',
    'run_no_network_owner_exclusion_probe.py',
    'class_os_extract_v2.py',
    'ixbrl_class_os_extract_v2.py',
    'class_os_reconcile_v2.py',
    'ownership_v2.py',
    'ownership_class_reconcile.py',
    'holders.py',
    'holders_v2.py',
    'holders_v3.py',
    'float_estimate.py',
    'float_estimate_v2.py',
    'audit_stratified_owner_exclusion_results.py',
    'build_external_audit_package_v0_1.ps1',
    'authorization.py',
    'storage.py',
    'telemetry.py'
)) {
    Copy-AuditFile (Join-Path $df "scripts\sec_pit\$name") (Join-Path '09_CODIGO_Y_CONFIG\scripts\sec_pit' $name)
}

foreach ($name in @(
    'test_sec_pit_owner_exclusion_stratified_probe.py',
    'test_sec_pit_class_os_extract_v2.py',
    'test_sec_pit_no_network_os_probe.py',
    'test_sec_pit_authorized_acquisition_scope.py',
    'test_sec_pit_ownership_v2.py',
    'test_sec_pit_holder_aggregate_precedence_v3.py',
    'test_sec_pit_management_aggregate_class_reconcile_v2.py',
    'test_sec_pit_stratified_owner_result_audit.py'
)) {
    Copy-AuditFile (Join-Path $df "tests\$name") (Join-Path '09_CODIGO_Y_CONFIG\tests' $name)
}

$buildMetadata = [ordered]@{
    package_id = 'SEC_PIT_PGAC_EXTERNAL_AUDIT_PACKAGE_v0_1'
    updated_at_utc = [DateTime]::UtcNow.ToString('o')
    status = 'PARTIAL_PASS_SCALE_BLOCKED'
    authoritative_os_iteration = 'stratified_v0_5_20260811T1730Z'
    authoritative_owner_iteration = 'stratified_v0_5_20260811T2200Z'
    sec_test_suite = '142_PASS'
    acquisition = [ordered]@{
        planned = 247
        fetched = 247
        failed = 0
        bytes = 29122331
    }
    manifest_scope = 'all package files except PACKAGE_FILE_MANIFEST.csv itself'
}
$buildMetadata | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $stage 'PACKAGE_BUILD_METADATA.json') -Encoding utf8

$manifestRows = Get-ChildItem -LiteralPath $stage -Recurse -File |
    Where-Object { $_.Name -ne 'PACKAGE_FILE_MANIFEST.csv' } |
    Sort-Object FullName |
    ForEach-Object {
        [pscustomobject]@{
            relative_path = $_.FullName.Substring($stage.Length + 1).Replace('\', '/')
            bytes = $_.Length
            sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    }
$manifestRows | Export-Csv -LiteralPath (Join-Path $stage 'PACKAGE_FILE_MANIFEST.csv') -NoTypeInformation -Encoding utf8

if (Test-Path -LiteralPath $tempZip) {
    Remove-Item -LiteralPath $tempZip -Force
}
[IO.Compression.ZipFile]::CreateFromDirectory(
    $stage,
    $tempZip,
    [IO.Compression.CompressionLevel]::Optimal,
    $false
)

$archive = [IO.Compression.ZipFile]::OpenRead($tempZip)
try {
    $entryNames = @(
        $archive.Entries | ForEach-Object { $_.FullName.Replace('\', '/') }
    )
    if ($entryNames.Count -ne (@($entryNames | Select-Object -Unique)).Count) {
        throw 'Duplicate ZIP entry names detected'
    }
    foreach ($requiredEntry in @(
        'SEC_PIT_PGAC_EXTERNAL_AUDIT_PACKAGE_CONTENTS_v0_1.md',
        '01_RESULTADO/SEC_PIT_SEVEN_TICKER_OWNER_EXCLUSION_STRATIFIED_PROBE_READOUT_v0_1.md',
        '06_EVIDENCIA_ESTRATIFICADA_CONTROL/probe/owner_exclusion_certification_audit_v0_1.json',
        '08_RUNS_OWNER_V0_5/PGAC/daily_float_state.parquet',
        '09_CODIGO_Y_CONFIG/scripts/sec_pit/holders_v3.py',
        'PACKAGE_FILE_MANIFEST.csv'
    )) {
        if ($requiredEntry -notin $entryNames) {
            throw "Required ZIP entry missing: $requiredEntry"
        }
    }
    foreach ($entry in $archive.Entries) {
        if (-not $entry.Name) { continue }
        $input = $entry.Open()
        try { $input.CopyTo([IO.Stream]::Null) } finally { $input.Dispose() }
    }
    $entryCount = $archive.Entries.Count
    $uncompressedBytes = ($archive.Entries | Measure-Object -Property Length -Sum).Sum
}
finally {
    $archive.Dispose()
}

if (-not (Test-Path -LiteralPath $backupZip)) {
    Copy-Item -LiteralPath $TargetZip -Destination $backupZip
}
Move-Item -LiteralPath $tempZip -Destination $TargetZip -Force
$governedContents = Join-Path $cto 'SEC_PIT_PGAC_EXTERNAL_AUDIT_PACKAGE_CONTENTS_v0_1.md'
if ((Resolve-Path -LiteralPath $UpdatedContentsManifest).Path -ne (Resolve-Path -LiteralPath $governedContents).Path) {
    Copy-Item -LiteralPath $UpdatedContentsManifest -Destination $governedContents -Force
}

$result = [ordered]@{
    target_zip = $TargetZip
    backup_zip = $backupZip
    entries = $entryCount
    uncompressed_bytes = $uncompressedBytes
    zip_bytes = (Get-Item -LiteralPath $TargetZip).Length
    zip_sha256 = (Get-FileHash -LiteralPath $TargetZip -Algorithm SHA256).Hash.ToLowerInvariant()
    validation = 'OPEN_READ_ALL_ENTRIES_AND_REQUIRED_ENTRY_GATE_PASS'
}
$result | ConvertTo-Json -Depth 4
