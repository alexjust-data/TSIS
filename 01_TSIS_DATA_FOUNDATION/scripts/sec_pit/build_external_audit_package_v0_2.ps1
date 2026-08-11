param([string]$TargetZip = 'C:\TSIS_Data\00_CTO\04_MARKET_STATES_CREATION\_DESCAGRA_DATOS_NECESARIA_\SEC_PIT_EXTERNAL_AUDIT_PACKAGE_v0_2.zip')

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$workspace = 'C:\TSIS_Data'
$df = Join-Path $workspace '01_TSIS_DATA_FOUNDATION'
$cto = Join-Path $workspace '00_CTO\04_MARKET_STATES_CREATION\_DESCAGRA_DATOS_NECESARIA_'
$dossier = Join-Path $df '01_foundations\inspection_dossiers\sec_pit'
$runtimeRoot = Join-Path $workspace 'runtime\sec_pit_external_audit_package_v0_2'
$stage = Join-Path $runtimeRoot 'stage'
$tempZip = Join-Path $runtimeRoot 'SEC_PIT_EXTERNAL_AUDIT_PACKAGE_v0_2.new.zip'
$runs = Join-Path $workspace 'runtime\sec_pit_stratified_owner_exclusion_v0_1\runs'
$adaptiveProbe = Join-Path $workspace 'runtime\sec_pit_stratified_owner_exclusion_v0_1\probes\sec_pit_owner_exclusion_7t_adaptive_v0_4_20260812T0030Z'
$fullProbe = Join-Path $workspace 'runtime\sec_pit_stratified_owner_exclusion_v0_1\probes\sec_pit_owner_exclusion_3t_full_interval_v0_1_20260812T0530Z'
$companyFacts = Join-Path $workspace 'runtime\sec_pit_companyfacts_os_v0_1\runs\sec_pit_companyfacts_7t_reconciliation_v0_2_20260812T0400Z'
$certification = Join-Path $workspace 'runtime\sec_pit_stratified_owner_exclusion_v0_1\certifications\sec_pit_7t_variable_shard_certification_v0_1_20260812T0800Z'

foreach ($required in @($dossier,$adaptiveProbe,$fullProbe,$companyFacts,$certification)) {
    if (-not (Test-Path -LiteralPath $required)) { throw "Required package source missing: $required" }
}
New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null
$resolvedRuntime = (Resolve-Path -LiteralPath $runtimeRoot).Path
if (Test-Path -LiteralPath $stage) {
    $resolvedStage = (Resolve-Path -LiteralPath $stage).Path
    if (-not $resolvedStage.StartsWith($resolvedRuntime,[StringComparison]::OrdinalIgnoreCase)) { throw "Unsafe staging path: $resolvedStage" }
    Remove-Item -LiteralPath $stage -Recurse -Force
}
New-Item -ItemType Directory -Path $stage | Out-Null

function Copy-AuditFile {
    param([string]$Source,[string]$RelativeDestination)
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) { throw "Missing audit source: $Source" }
    $destination = Join-Path $stage $RelativeDestination
    New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
    Copy-Item -LiteralPath $Source -Destination $destination -Force
}
function Copy-TopLevelFiles {
    param([string]$SourceDirectory,[string]$RelativeDestination)
    if (-not (Test-Path -LiteralPath $SourceDirectory -PathType Container)) { throw "Missing audit directory: $SourceDirectory" }
    Get-ChildItem -LiteralPath $SourceDirectory -File | ForEach-Object { Copy-AuditFile $_.FullName (Join-Path $RelativeDestination $_.Name) }
}

Copy-AuditFile (Join-Path $cto 'SEC_PIT_EXTERNAL_AUDIT_PACKAGE_CONTENTS_v0_2.md') 'SEC_PIT_EXTERNAL_AUDIT_PACKAGE_CONTENTS_v0_2.md'
foreach ($name in @(
    'SEC_PIT_ADAPTIVE_BASELINE_COMPANYFACTS_FULL_INTERVAL_AND_SHARD_CERTIFICATION_READOUT_v0_1.md',
    'SEC_PIT_SEVEN_TICKER_OWNER_EXCLUSION_STRATIFIED_PROBE_READOUT_v0_1.md',
    'SEC_PIT_PGAC_OWNERSHIP_AND_OWNER_EXCLUSION_PROBE_READOUT_v0_1.md',
    'SEC_PIT_PGAC_NO_NETWORK_OS_PROBE_READOUT_v0_1.md'
)) { Copy-AuditFile (Join-Path $dossier $name) (Join-Path '01_RESULTADO' $name) }

foreach ($name in @(
    'SEC_PIT_ADAPTIVE_BASELINE_AND_SCALE_GATE_HANDOFF_v0_1.md',
    'SEC_PIT_FUNDAMENTAL_ACQUISITION_AND_RESOLUTION_CONTRACT_v0_1.md',
    'SEC_PIT_LIFECYCLE_SOURCE_SELECTION_POLICY_v0_2.md',
    'SEC_PIT_OWNER_EXCLUSION_METHODOLOGY_CONTRACT_v0_1.md',
    'SEC_PIT_SEVEN_TICKER_OWNER_EXCLUSION_STRATIFIED_PROBE_PLAN_v0_1.md',
    'SEC_PIT_PGAC_NO_NETWORK_OS_AND_OWNER_EXCLUSION_GATE_PLAN_v0_1.md',
    'SEC_PIT_PGAC_OWNERSHIP_CLASS_RECONCILIATION_PROBE_PLAN_v0_1.md'
)) { Copy-AuditFile (Join-Path $cto $name) (Join-Path '02_PROCESO_SEC' $name) }

Copy-AuditFile (Join-Path $df '01_foundations\canonical_schemas\sec_pit_resolved_daily_states_schema_contract_v0_2.md') '03_SCHEMA\sec_pit_resolved_daily_states_schema_contract_v0_2.md'
Copy-TopLevelFiles $adaptiveProbe '06_EVIDENCIA_ADAPTATIVA\seven_case_probe'
Copy-TopLevelFiles $fullProbe '06_EVIDENCIA_ADAPTATIVA\full_interval_probe'
Copy-TopLevelFiles $companyFacts '10_COMPANYFACTS'
Copy-TopLevelFiles $certification '11_SHARD_CERTIFICATION'

foreach ($ticker in @('alur','bbby','bgm','bnai','domh','pgac')) {
    Copy-TopLevelFiles (Join-Path $runs "sec_pit_${ticker}_os_stratified_v0_6_20260812T0330Z") ("07_RUNS_OS_V0_6\" + $ticker.ToUpperInvariant())
    Copy-TopLevelFiles (Join-Path $runs "sec_pit_${ticker}_owner_adaptive_v0_14_20260812T0730Z") ("08_RUNS_OWNER_V0_14\" + $ticker.ToUpperInvariant())
}
foreach ($ticker in @('alur','bnai','pgac')) {
    Copy-TopLevelFiles (Join-Path $runs "sec_pit_${ticker}_os_full_interval_v0_1_20260812T0600Z") ("09_FULL_INTERVAL\OS\" + $ticker.ToUpperInvariant())
    Copy-TopLevelFiles (Join-Path $runs "sec_pit_${ticker}_owner_full_interval_v0_2_20260812T0700Z") ("09_FULL_INTERVAL\OWNER\" + $ticker.ToUpperInvariant())
}

foreach ($name in @('sec_pit_owner_exclusion_stratified_probe_v0_2.json','sec_pit_owner_exclusion_full_interval_3t_probe_v0_1.json')) {
    Copy-AuditFile (Join-Path $df "configs\$name") (Join-Path '12_CODIGO_CONFIG_TESTS\configs' $name)
}
Get-ChildItem -LiteralPath (Join-Path $df 'scripts\sec_pit') -File | ForEach-Object {
    Copy-AuditFile $_.FullName (Join-Path '12_CODIGO_CONFIG_TESTS\scripts\sec_pit' $_.Name)
}
Get-ChildItem -LiteralPath (Join-Path $df 'tests') -Filter 'test_sec_pit_*.py' -File | ForEach-Object {
    Copy-AuditFile $_.FullName (Join-Path '12_CODIGO_CONFIG_TESTS\tests' $_.Name)
}

[ordered]@{
    package_id = 'SEC_PIT_EXTERNAL_AUDIT_PACKAGE_v0_2'
    created_at_utc = [DateTime]::UtcNow.ToString('o')
    status = 'SYSTEM_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING'
    authoritative_os_iteration = 'stratified_v0_6_20260812T0330Z'
    authoritative_owner_iteration = 'adaptive_v0_14_20260812T0730Z'
    authoritative_full_interval_iteration = 'owner_full_interval_v0_2_20260812T0700Z'
    companyfacts_iteration = 'reconciliation_v0_2_20260812T0400Z'
    shard_certification = 'sec_pit_7t_variable_shard_certification_v0_1_20260812T0800Z'
    sec_test_suite = 'PASS'
    scale_authorization = 'NOT_GRANTED_REQUIRES_HUMAN_OR_GOVERNED_GATE'
    manifest_scope = 'all package files except PACKAGE_FILE_MANIFEST.csv itself'
} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $stage 'PACKAGE_BUILD_METADATA.json') -Encoding utf8

$rows = Get-ChildItem -LiteralPath $stage -Recurse -File | Where-Object Name -ne 'PACKAGE_FILE_MANIFEST.csv' | Sort-Object FullName | ForEach-Object {
    [pscustomobject]@{
        relative_path = $_.FullName.Substring($stage.Length + 1).Replace('\','/')
        bytes = $_.Length
        sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}
$rows | Export-Csv -LiteralPath (Join-Path $stage 'PACKAGE_FILE_MANIFEST.csv') -NoTypeInformation -Encoding utf8

if (Test-Path -LiteralPath $tempZip) { Remove-Item -LiteralPath $tempZip -Force }
[IO.Compression.ZipFile]::CreateFromDirectory($stage,$tempZip,[IO.Compression.CompressionLevel]::Optimal,$false)
$archive = [IO.Compression.ZipFile]::OpenRead($tempZip)
try {
    $names = @($archive.Entries | ForEach-Object { $_.FullName.Replace('\','/') })
    if ($names.Count -ne (@($names | Select-Object -Unique)).Count) { throw 'Duplicate ZIP entry names detected' }
    foreach ($requiredEntry in @(
        'SEC_PIT_EXTERNAL_AUDIT_PACKAGE_CONTENTS_v0_2.md',
        '01_RESULTADO/SEC_PIT_ADAPTIVE_BASELINE_COMPANYFACTS_FULL_INTERVAL_AND_SHARD_CERTIFICATION_READOUT_v0_1.md',
        '08_RUNS_OWNER_V0_14/PGAC/daily_float_state.parquet',
        '10_COMPANYFACTS/final_manifest.json',
        '11_SHARD_CERTIFICATION/certification.json',
        'PACKAGE_FILE_MANIFEST.csv'
    )) { if ($requiredEntry -notin $names) { throw "Required ZIP entry missing: $requiredEntry" } }
    foreach ($entry in $archive.Entries) {
        if (-not $entry.Name) { continue }
        $stream = $entry.Open()
        try { $stream.CopyTo([IO.Stream]::Null) } finally { $stream.Dispose() }
    }
    $entryCount = $archive.Entries.Count
    $uncompressedBytes = ($archive.Entries | Measure-Object Length -Sum).Sum
} finally { $archive.Dispose() }

New-Item -ItemType Directory -Path (Split-Path -Parent $TargetZip) -Force | Out-Null
Move-Item -LiteralPath $tempZip -Destination $TargetZip -Force
[ordered]@{
    target_zip = $TargetZip
    entries = $entryCount
    uncompressed_bytes = $uncompressedBytes
    zip_bytes = (Get-Item -LiteralPath $TargetZip).Length
    zip_sha256 = (Get-FileHash -LiteralPath $TargetZip -Algorithm SHA256).Hash.ToLowerInvariant()
    validation = 'OPEN_READ_ALL_ENTRIES_AND_REQUIRED_ENTRY_GATE_PASS'
} | ConvertTo-Json -Depth 4
