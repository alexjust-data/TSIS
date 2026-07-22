# Regime Indicators Visual Inspector Pack

Fecha: 2026-06-20
Estado: `visual_complete_v0_1`

## Role

This folder is the visual inspection layer for:

```text
regime_indicators_v0_1
```

It closes the visual evidence requirement defined by:

```text
../../../VISUAL_INSPECTION_PACK_REQUIREMENTS.md
```

The visual pack does not change the data-quality verdict. The family remains:

```text
blocked_daily_scoped_minute_review
```

## Reading Order

1. `regime_indicators_visual_inspector_pack_v0_1.md`
2. `regime_indicators_visual_case_manifest_v0_1.csv`
3. `regime_indicators_visual_asset_audit_v0_1.csv`
4. `images/*.png`
5. `build_regime_indicators_visual_inspector_pack.py`

## Generated Assets

| Visual | Role |
| --- | --- |
| `images/regime_indicators_daily_date_collapse_panel_v0_1.png` | bad/blocking daily date case |
| `images/regime_indicators_daily_file_date_heatmap_v0_1.png` | daily file-level blocker map |
| `images/regime_indicators_minute_high_low_inversion_panel_v0_1.png` | flagged minute OHLC case |
| `images/regime_indicators_minute_coverage_readability_map_v0_1.png` | scoped minute coverage/readability |
| `images/regime_indicators_metadata_good_examples_v0_1.png` | metadata good/scoped examples |
| `images/regime_indicators_blocked_vs_scoped_consumption_panel_v0_1.png` | consumption boundary |

## Evidence Sources

All visuals are generated from dossier-local evidence in:

```text
../evidence_assets/
```

Primary source CSVs:

- `regime_indicators_daily_date_quality_v0_1.csv`
- `regime_indicators_daily_blocking_date_manifest_v0_1.csv`
- `regime_indicators_minute_schema_review_v0_1.csv`
- `regime_indicators_minute_flagged_issue_manifest_v0_1.csv`
- `regime_indicators_metadata_summary_v0_1.csv`
- `sample_payloads/*.csv`

## Final Rule

This package makes the blocked/scoped regime indicators state inspectable at
the visual evidence standard. It does not make daily bars usable.

Correct reading:

```text
foundations_completion_status = human_inspector_ready
visual_inspection_status = visual_complete
data_quality_verdict = blocked_daily_scoped_minute_review
```
