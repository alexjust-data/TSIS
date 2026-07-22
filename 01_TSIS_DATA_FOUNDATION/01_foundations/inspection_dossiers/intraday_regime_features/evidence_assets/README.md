# Intraday Regime Features Evidence Assets v0.1

This directory contains stable derived evidence for:

```text
intraday_regime_features_v0_1
```

Source root:

```text
E:/TSIS/data/intraday_regime_features
```

These files are evidence assets for the scoped semantic pilot. They are not a
full-universe feature-store audit.

## Asset Index

| Asset | Purpose |
| --- | --- |
| `intraday_regime_features_audit_summary_v0_1.json` | Compact audit summary for physical materialization, keys, provenance and images. |
| `intraday_regime_features_inventory_v0_1.csv` | File-level parquet inventory. |
| `intraday_regime_features_materialization_summary_v0_1.csv` | Copy of the source materialization summary. |
| `intraday_regime_features_key_quality_v0_1.csv` | File-level key checks. |
| `intraday_regime_features_key_quality_summary_v0_1.csv` | Aggregate key-quality summary. |
| `intraday_regime_features_provenance_value_profile_v0_1.csv` | File-level provenance value checks. |
| `intraday_regime_features_provenance_summary_v0_1.csv` | Aggregate provenance checks. |
| `intraday_regime_features_null_profile_v0_1.csv` | File-level null profile. |
| `intraday_regime_features_null_summary_v0_1.csv` | Aggregate null profile. |
| `intraday_regime_features_numeric_extreme_profile_v0_1.csv` | File-level numeric extrema. |
| `intraday_regime_features_numeric_extreme_summary_v0_1.csv` | Aggregate numeric extrema. |
| `intraday_regime_features_semantic_case_manifest_v0_1.csv` | Semantic pilot case manifest with visual evidence links. |
| `intraday_regime_features_image_manifest_v0_1.csv` | Existing image evidence inventory. |
| `intraday_regime_features_sample_payload_manifest_v0_1.csv` | Feature payload sample manifest. |
| `intraday_regime_features_read_errors_v0_1.csv` | Read-error table. Empty means no read errors were observed by this evidence build. |
| `intraday_regime_features_evidence_assets_manifest_v0_1.csv` | Manifest of all evidence assets in this directory. |
| `sample_payloads/` | Representative feature rows for pilot tickers. |

## Current Evidence Snapshot

| Metric | Value |
| --- | ---: |
| Parquet files | 8 |
| Read errors | 0 |
| Tickers | 8 |
| Rows | 243 |
| Columns | 41 |
| Duplicate `ticker + date` rows | 0 |
| Image files | 10 |
| Provenance checks matching expected values | 100% |

Expected provenance values:

| Field | Expected value |
| --- | --- |
| `feature_contract` | `intraday_regime_features_v0_1` |
| `feature_grain` | `ticker_day` |
| `cross_session_price_view` | `1m_split_normalized_v0_1` |
| `intraday_price_view` | `1m_raw` |

## Scope Boundary

This evidence supports:

- `human_inspector_ready_scoped`;
- semantic validation of a real downstream consumer;
- research-only use inside the pilot scope.

It does not support:

- full-universe feature-store promotion;
- production model consumption;
- live/RL/backtest-core dependency.
