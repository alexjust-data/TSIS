# Intraday Regime Features Inspection Dossier

This dossier records the scoped semantic pilot package for:

```text
intraday_regime_features_v0_1
```

Physical root:

```text
E:/TSIS/data/intraday_regime_features
```

Data-quality state:

```text
complete_scoped_pilot
```

Foundations completion status:

```text
human_inspector_ready_scoped
```

Visual inspection status:

```text
visual_complete_scoped
```

This means the pilot is complete for its declared scope. It does not mean this
family is a production feature store.

## Dossier Map

| Area | Path | Purpose |
| --- | --- | --- |
| Primary readout | `intraday_regime_features_semantic_pilot_readout_v0_1.md` | Human-facing semantic pilot narrative. |
| Evidence assets | `evidence_assets/` | Stable CSV/JSON summaries, manifests and sample payloads. |
| Build note | `build_intraday_regime_features_inspection_pack.md` | Rebuild and provenance note for this dossier. |
| Good/scoped cases | `good_justification/intraday_regime_features_semantic_pilot_good_cases_v0_1.md` | Strong split cases, controls and provenance checks. |
| Review/boundary cases | `flagged_case_evidence_packs/intraday_regime_features_lookback_and_boundary_cases_v0_1.md` | Lookback nulls and coherent boundary cases. |
| Production boundary | `bad_case_evidence_packs/intraday_regime_features_production_boundary_v0_1.md` | Claims that are blocked by pilot scope. |
| Coverage evidence | `coverage_case_evidence_packs/intraday_regime_features_materialization_coverage_v0_1.md` | Physical materialization coverage and key checks. |
| Images | `images/` | Visual semantic pilot evidence. |
| Visual inspector pack | `visual_inspector_pack/` | Formal visual pack with aggregate panels, copied semantic case images, manifest and asset audit. |
| Quality report | `../../data_quality_report/families/intraday_regime_features_quality_report_v0_1.md` | Normalized family quality report. |

## Current Evidence Snapshot

| Metric | Value |
| --- | ---: |
| Parquet files | 8 |
| Read errors | 0 |
| Tickers | 8 |
| Ticker-day rows | 243 |
| Columns | 41 |
| Duplicate `ticker + date` rows | 0 |
| Image files | 10 |
| Formal visual pack images | 15 |
| Provenance checks matching expected values | 100% |

Materialized tickers:

- `BNGO`
- `BXRX`
- `CEI`
- `COSM`
- `EFSH`
- `LIVE`
- `PD`
- `SAVA`

## Required Inspector Path

Read in this order:

1. `intraday_regime_features_semantic_pilot_readout_v0_1.md`
2. `visual_inspector_pack/intraday_regime_features_visual_inspector_pack_v0_1.md`
3. `visual_inspector_pack/intraday_regime_features_visual_case_manifest_v0_1.csv`
4. `visual_inspector_pack/intraday_regime_features_visual_asset_audit_v0_1.csv`
5. `evidence_assets/README.md`
6. `good_justification/intraday_regime_features_semantic_pilot_good_cases_v0_1.md`
7. `flagged_case_evidence_packs/intraday_regime_features_lookback_and_boundary_cases_v0_1.md`
8. `bad_case_evidence_packs/intraday_regime_features_production_boundary_v0_1.md`
9. `coverage_case_evidence_packs/intraday_regime_features_materialization_coverage_v0_1.md`
10. `../../data_quality_report/families/intraday_regime_features_quality_report_v0_1.md`

## Final Rule

The family is valid as a semantic pilot consumer of
`ohlcv_1m_split_normalized`.

It is not valid as full-universe feature-store input, backtest-core input, ML
primary input, RL input or live input until a future promoted version closes the
production feature audit.
