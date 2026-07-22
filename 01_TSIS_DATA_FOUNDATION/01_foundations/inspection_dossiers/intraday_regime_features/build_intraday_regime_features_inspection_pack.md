# Build Intraday Regime Features Inspection Pack

This note records how the current `intraday_regime_features_v0_1` evidence
package was derived.

Source root:

```text
E:/TSIS/data/intraday_regime_features
```

Dossier root:

```text
01_foundations/inspection_dossiers/intraday_regime_features
```

Generated evidence root:

```text
01_foundations/inspection_dossiers/intraday_regime_features/evidence_assets
```

## Build Logic

The evidence build inspected:

- every feature parquet under the physical root;
- `_intraday_regime_features_materialization_summary.csv`;
- `ticker + date` uniqueness;
- path ticker/year agreement with payload values;
- expected provenance values;
- per-column nulls;
- numeric extrema and infinite values;
- existing semantic pilot images.

The build is read-only against `E:/TSIS/data/intraday_regime_features`. It
writes only derived inspection artifacts into this dossier.

## Generated Assets

Primary outputs:

- `evidence_assets/intraday_regime_features_audit_summary_v0_1.json`
- `evidence_assets/intraday_regime_features_inventory_v0_1.csv`
- `evidence_assets/intraday_regime_features_key_quality_summary_v0_1.csv`
- `evidence_assets/intraday_regime_features_provenance_summary_v0_1.csv`
- `evidence_assets/intraday_regime_features_null_summary_v0_1.csv`
- `evidence_assets/intraday_regime_features_numeric_extreme_summary_v0_1.csv`
- `evidence_assets/intraday_regime_features_semantic_case_manifest_v0_1.csv`
- `evidence_assets/intraday_regime_features_image_manifest_v0_1.csv`

## Rebuild Requirement

If the feature data is expanded, repaired or regenerated, this evidence package
must be rebuilt and the following files must be reviewed together:

- `intraday_regime_features_semantic_pilot_readout_v0_1.md`;
- `../../data_quality_report/families/intraday_regime_features_quality_report_v0_1.md`;
- `../../data_quality_report/family_status_matrix_v0_1.md`;
- `../../../CHANGELOG.md`.
