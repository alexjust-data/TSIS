# Build Short Review Inspection Pack

This note records how the current `short_review_finra_v0_1` evidence package
was derived.

Source root:

```text
E:/TSIS/data/short_review/finra_short
```

Outer source documentation root:

```text
E:/TSIS/data/short_review
```

Dossier root:

```text
01_foundations/inspection_dossiers/short_review
```

Generated evidence root:

```text
01_foundations/inspection_dossiers/short_review/evidence_assets
```

## Build Logic

The evidence build inspected:

- aggregate FINRA parquet artifacts;
- normalized per-ticker parquet counts;
- raw/log/artifact/provenance file presence;
- aggregate logical key uniqueness;
- aggregate date ranges and ticker counts;
- numeric nonnegative/null/infinite checks;
- artifact manifests;
- download logs;
- known FINRA vs local/Polygon comparison snapshot;
- sample payload rows.

The build is read-only against `E:/TSIS/data/short_review`. It writes only
derived inspection artifacts into this dossier.

## Generated Assets

Primary outputs:

- `evidence_assets/short_review_audit_summary_v0_1.json`
- `evidence_assets/short_review_aggregate_profile_v0_1.csv`
- `evidence_assets/short_review_key_quality_v0_1.csv`
- `evidence_assets/short_review_numeric_sanity_v0_1.csv`
- `evidence_assets/short_review_compact_file_count_summary_v0_1.csv`
- `evidence_assets/short_review_local_comparison_summary_v0_1.csv`
- `evidence_assets/short_review_short_volume_duplicate_key_by_ticker_v0_1.csv`
- `evidence_assets/short_review_scope_limitations_v0_1.csv`
- `evidence_assets/short_review_evidence_assets_manifest_v0_1.csv`

## Rebuild Requirement

If the FINRA artifacts, local `short` comparison or short-data policy changes,
this evidence package must be rebuilt and the following files must be reviewed
together:

- `short_review_inspection_readout_v0_1.md`;
- `../../data_quality_report/families/short_review_quality_report_v0_1.md`;
- `../../data_quality_report/family_status_matrix_v0_1.md`;
- `../../../CHANGELOG.md`.
