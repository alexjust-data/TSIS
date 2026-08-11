param([string]$TargetZip = 'C:\TSIS_Data\00_CTO\04_MARKET_STATES_CREATION\_DESCAGRA_DATOS_NECESARIA_\SEC_PIT_EXTERNAL_AUDIT_PACKAGE_v0_3.zip')

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$workspace = 'C:\TSIS_Data'
$df = Join-Path $workspace '01_TSIS_DATA_FOUNDATION'
$cto = Join-Path $workspace '00_CTO\04_MARKET_STATES_CREATION\_DESCAGRA_DATOS_NECESARIA_'
$dossier = Join-Path $df '01_foundations\inspection_dossiers\sec_pit'
$runtimeRoot = Join-Path $workspace 'runtime\sec_pit_external_audit_package_v0_3'
$stage = Join-Path $runtimeRoot 'stage'
$tempZip = Join-Path $runtimeRoot 'SEC_PIT_EXTERNAL_AUDIT_PACKAGE_v0_3.new.zip'
$adaptiveProbe = Join-Path $workspace 'runtime\sec_pit_stratified_owner_exclusion_v0_1\probes\sec_pit_owner_exclusion_7t_adaptive_v0_4_20260812T0030Z'
$companyFacts = Join-Path $workspace 'runtime\sec_pit_companyfacts_os_v0_1\runs\sec_pit_companyfacts_7t_reconciliation_v0_2_20260812T0400Z'
$certification = Join-Path $workspace 'runtime\sec_pit_stratified_owner_exclusion_v0_1\certifications\sec_pit_7t_variable_shard_certification_v0_1_20260812T0800Z'

foreach ($required in @($dossier,$adaptiveProbe,$companyFacts,$certification)) {
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

Copy-AuditFile (Join-Path $cto 'SEC_PIT_EXTERNAL_AUDIT_PACKAGE_CONTENTS_v0_3.md') '00_START_HERE.md'
Copy-AuditFile (Join-Path $dossier 'SEC_PIT_ADAPTIVE_BASELINE_COMPANYFACTS_FULL_INTERVAL_AND_SHARD_CERTIFICATION_READOUT_v0_1.md') '01_RESULT\FINAL_READOUT.md'
Copy-AuditFile (Join-Path $cto 'SEC_PIT_ADAPTIVE_BASELINE_AND_SCALE_GATE_HANDOFF_v0_1.md') '02_PROCESS\NEXT_SCALE_GATE.md'
Copy-AuditFile (Join-Path $cto 'SEC_PIT_FUNDAMENTAL_ACQUISITION_AND_RESOLUTION_CONTRACT_v0_1.md') '02_PROCESS\ACQUISITION_AND_RESOLUTION_CONTRACT.md'
Copy-AuditFile (Join-Path $cto 'SEC_PIT_OWNER_EXCLUSION_METHODOLOGY_CONTRACT_v0_1.md') '02_PROCESS\OWNER_EXCLUSION_METHODOLOGY.md'
Copy-AuditFile (Join-Path $df '01_foundations\canonical_schemas\sec_pit_resolved_daily_states_schema_contract_v0_2.md') '03_OUTPUT_SCHEMA\RESOLVED_DAILY_STATE_SCHEMA.md'
Copy-AuditFile (Join-Path $adaptiveProbe 'case_matrix.json') '04_MINIMUM_EVIDENCE\case_matrix.json'
Copy-AuditFile (Join-Path $adaptiveProbe 'final_manifest.json') '04_MINIMUM_EVIDENCE\adaptive_probe_final_manifest.json'
Copy-AuditFile (Join-Path $companyFacts 'final_manifest.json') '04_MINIMUM_EVIDENCE\companyfacts_final_manifest.json'
Copy-AuditFile (Join-Path $certification 'certification.json') '04_MINIMUM_EVIDENCE\shard_certification.json'

$gitCommit = (git -C $workspace rev-parse HEAD).Trim()
[ordered]@{
    package_id = 'SEC_PIT_EXTERNAL_AUDIT_PACKAGE_v0_3'
    created_at_utc = [DateTime]::UtcNow.ToString('o')
    purpose = 'MINIMAL_EXTERNAL_HANDOFF_NOT_APPLICATION_ARCHIVE'
    supersedes_external_review_package = 'SEC_PIT_EXTERNAL_AUDIT_PACKAGE_v0_2.zip'
    git_commit = $gitCommit
    status = 'SYSTEM_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING'
    authoritative_runs = [ordered]@{
        adaptive_probe = 'sec_pit_owner_exclusion_7t_adaptive_v0_4_20260812T0030Z'
        owner_results = 'sec_pit_<ticker>_owner_adaptive_v0_14_20260812T0730Z'
        full_interval = 'sec_pit_<ticker>_owner_full_interval_v0_2_20260812T0700Z'
        companyfacts = 'sec_pit_companyfacts_7t_reconciliation_v0_2_20260812T0400Z'
        shard_certification = 'sec_pit_7t_variable_shard_certification_v0_1_20260812T0800Z'
    }
    excluded_by_design = @('source code','tests','daily parquet runs','raw SEC payloads','historical duplicate readouts','Trading Activity','Graphify runtime')
    scale_authorization = 'NOT_GRANTED_REQUIRES_30_TO_50_CASE_GATE'
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $stage 'PACKAGE_BUILD_METADATA.json') -Encoding utf8

$rows = Get-ChildItem -LiteralPath $stage -Recurse -File | Where-Object Name -ne 'PACKAGE_FILE_MANIFEST.csv' | Sort-Object FullName | ForEach-Object {
    [pscustomobject]@{ relative_path=$_.FullName.Substring($stage.Length+1).Replace('\','/'); bytes=$_.Length; sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }
}
$rows | Export-Csv -LiteralPath (Join-Path $stage 'PACKAGE_FILE_MANIFEST.csv') -NoTypeInformation -Encoding utf8

if (Test-Path -LiteralPath $tempZip) { Remove-Item -LiteralPath $tempZip -Force }
[IO.Compression.ZipFile]::CreateFromDirectory($stage,$tempZip,[IO.Compression.CompressionLevel]::Optimal,$false)
$archive = [IO.Compression.ZipFile]::OpenRead($tempZip)
try {
    $names = @($archive.Entries | ForEach-Object { $_.FullName.Replace('\','/') })
    if ($archive.Entries.Count -ne 12) { throw "Minimal-package entry gate failed: expected 12, got $($archive.Entries.Count)" }
    if ($names.Count -ne (@($names | Select-Object -Unique)).Count) { throw 'Duplicate ZIP entry names detected' }
    foreach ($entry in $archive.Entries) { if ($entry.Name) { $stream=$entry.Open(); try { $stream.CopyTo([IO.Stream]::Null) } finally { $stream.Dispose() } } }
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
    validation = 'MINIMAL_12_ENTRY_AND_OPEN_READ_GATE_PASS'
} | ConvertTo-Json -Depth 4
