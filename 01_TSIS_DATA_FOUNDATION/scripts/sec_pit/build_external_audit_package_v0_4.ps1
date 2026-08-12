param([string]$TargetZip = 'C:\TSIS_Data\00_CTO\04_MARKET_STATES_CREATION\_DESCAGRA_DATOS_NECESARIA_\SEC_PIT_EXTERNAL_AUDIT_PACKAGE_v0_4.zip')

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$workspace = 'C:\TSIS_Data'
$df = Join-Path $workspace '01_TSIS_DATA_FOUNDATION'
$cto = Join-Path $workspace '00_CTO\04_MARKET_STATES_CREATION\_DESCAGRA_DATOS_NECESARIA_'
$dossier = Join-Path $df '01_foundations\inspection_dossiers\sec_pit'
$runtimeRoot = Join-Path $workspace 'runtime\sec_pit_external_audit_package_v0_4'
$stage = Join-Path $runtimeRoot 'stage'
$tempZip = Join-Path $runtimeRoot 'SEC_PIT_EXTERNAL_AUDIT_PACKAGE_v0_4.new.zip'
$gateRoot = Join-Path $workspace 'runtime\sec_pit_100_case_scale_gate_v0_1\bounded_probe_authorized_v0_4_20260812T0530Z'
$resolutionRoot = Join-Path $workspace 'runtime\sec_pit_100_case_resolution_v0_5'
$batchRoot = Join-Path $resolutionRoot 'batches\sec_pit_100_case_resolution_v0_5_20260812T1210Z'

foreach ($required in @($dossier,$gateRoot,$resolutionRoot,$batchRoot)) {
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

Copy-AuditFile (Join-Path $cto 'SEC_PIT_EXTERNAL_AUDIT_PACKAGE_CONTENTS_v0_4.md') '00_START_HERE.md'
Copy-AuditFile (Join-Path $dossier 'SEC_PIT_100_CASE_STRATIFIED_SCALE_GATE_READOUT_v0_1.md') '01_RESULT\FINAL_100_CASE_READOUT.md'
Copy-AuditFile (Join-Path $dossier 'SEC_PIT_100_CASE_OS_MULTI_EVIDENCE_SHARD_CERTIFICATION_v0_1.md') '01_RESULT\OS_MULTI_EVIDENCE_CERTIFICATION.md'
Copy-AuditFile (Join-Path $cto 'SEC_PIT_FUNDAMENTAL_ACQUISITION_AND_RESOLUTION_CONTRACT_v0_1.md') '02_PROCESS\ACQUISITION_AND_RESOLUTION_CONTRACT.md'
Copy-AuditFile (Join-Path $cto 'SEC_PIT_OWNER_EXCLUSION_METHODOLOGY_CONTRACT_v0_1.md') '02_PROCESS\OWNER_EXCLUSION_METHODOLOGY.md'
Copy-AuditFile (Join-Path $df '01_foundations\canonical_schemas\sec_pit_resolved_daily_states_schema_contract_v0_2.md') '03_OUTPUT_SCHEMA\RESOLVED_DAILY_STATE_SCHEMA.md'
Copy-AuditFile (Join-Path $gateRoot 'case_matrix.json') '04_MINIMUM_EVIDENCE\case_matrix.json'
Copy-AuditFile (Join-Path $batchRoot 'final_manifest.json') '04_MINIMUM_EVIDENCE\resolution_batch_final_manifest.json'
Copy-AuditFile (Join-Path $resolutionRoot 'certification_v0_1\certification.json') '04_MINIMUM_EVIDENCE\four_shard_certification.json'
Copy-AuditFile (Join-Path $resolutionRoot 'scale_gate_summary_v0_1\summary.json') '04_MINIMUM_EVIDENCE\scale_gate_summary.json'

$gitCommit = (git -C $workspace rev-parse HEAD).Trim()
[ordered]@{
    package_id = 'SEC_PIT_EXTERNAL_AUDIT_PACKAGE_v0_4'
    created_at_utc = [DateTime]::UtcNow.ToString('o')
    purpose = 'MINIMAL_100_CASE_EXTERNAL_HANDOFF_NOT_APPLICATION_ARCHIVE'
    supersedes_external_review_package = 'SEC_PIT_EXTERNAL_AUDIT_PACKAGE_v0_3.zip'
    package_builder_commit = $gitCommit
    authoritative_source_snapshot_commit = '27607c8'
    status = 'SYSTEM_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING'
    authoritative_run = 'sec_pit_100_case_resolution_v0_5_20260812T1210Z'
    coverage = [ordered]@{ os_full_cases = 56; os_sessions = 280; float_full_cases = 11; float_sessions = 55; eligible_sessions = 495 }
    excluded_by_design = @('source code','tests','raw SEC payloads','daily parquet runs','historical duplicate readouts','Trading Activity','Graphify runtime')
    scale_authorization = 'NOT_GRANTED_OWNERSHIP_COVERAGE_AND_HISTORICAL_TRANSITION_GATES_REQUIRED'
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
