# Build Regime Indicators Inspection Pack

This note records how the current `regime_indicators_v0_1` evidence package was
derived.

Source root:

```text
E:/TSIS/data/regime_indicators
```

Dossier root:

```text
01_foundations/inspection_dossiers/regime_indicators
```

Generated evidence root:

```text
01_foundations/inspection_dossiers/regime_indicators/evidence_assets
```

## Build Logic

The evidence build inspected:

- every parquet file under `etfs/` and `indices/`;
- root JSON metadata files;
- daily `date` and `datetime` columns;
- minute `timestamp` parseability, uniqueness and monotonicity;
- OHLC sanity for both daily and minute bars;
- representative payload samples for ETF and index daily/minute files.

The build is intentionally read-only against `E:/TSIS/data/regime_indicators`.
It writes only derived inspection artifacts into this dossier.

## Generated Assets

Primary outputs:

- `evidence_assets/regime_indicators_audit_summary_v0_1.json`
- `evidence_assets/regime_indicators_inventory_v0_1.csv`
- `evidence_assets/regime_indicators_daily_date_quality_v0_1.csv`
- `evidence_assets/regime_indicators_daily_blocking_date_manifest_v0_1.csv`
- `evidence_assets/regime_indicators_minute_schema_review_v0_1.csv`
- `evidence_assets/regime_indicators_minute_flagged_issue_manifest_v0_1.csv`
- `evidence_assets/regime_indicators_metadata_summary_v0_1.csv`
- `evidence_assets/regime_indicators_evidence_assets_manifest_v0_1.csv`

Sample payloads:

- `evidence_assets/sample_payloads/spy_day_broken_sample_v0_1.csv`
- `evidence_assets/sample_payloads/i_ndx_day_broken_sample_v0_1.csv`
- `evidence_assets/sample_payloads/spy_minute_sample_v0_1.csv`
- `evidence_assets/sample_payloads/i_ndx_minute_sample_v0_1.csv`
- `evidence_assets/sample_payloads/minute_high_lt_low_issue_samples_v0_1.csv`

## Rebuild Requirement

If the physical regime data is repaired or regenerated, this evidence package
must be rebuilt and the following files must be reviewed together:

- `regime_indicators_inspection_readout_v0_1.md`;
- `../../data_quality_report/families/regime_indicators_quality_report_v0_1.md`;
- `../../data_quality_report/family_status_matrix_v0_1.md`;
- `../../../CHANGELOG.md`.
