# Short Review Visual Inspector Pack

Fecha: 2026-06-20
Estado: `visual_complete_v0_1`

## Role

This folder is the visual inspection layer for:

```text
short_review_finra_v0_1
```

It closes the visual evidence requirement defined by:

```text
../../../VISUAL_INSPECTION_PACK_REQUIREMENTS.md
```

The visual pack does not change the scoped data-quality verdict:

```text
complete_scoped_provenance_with_short_volume_key_flags
```

## Reading Order

1. `short_review_visual_inspector_pack_v0_1.md`
2. `short_review_visual_case_manifest_v0_1.csv`
3. `short_review_visual_asset_audit_v0_1.csv`
4. `images/*.png`
5. `build_short_review_visual_inspector_pack.py`

## Generated Assets

| Visual | Role |
| --- | --- |
| `images/short_review_finra_coverage_timeline_v0_1.png` | FINRA baseline coverage and date windows |
| `images/short_review_duplicate_key_concentration_v0_1.png` | duplicate-key concentration |
| `images/short_review_duplicate_key_case_panel_v0_1.png` | concrete duplicate-key cases |
| `images/short_review_finra_vs_local_overlap_panel_v0_1.png` | FINRA vs local overlap |
| `images/short_review_numeric_sanity_panel_v0_1.png` | numeric sanity |
| `images/short_review_provenance_history_boundary_panel_v0_1.png` | provenance and history limits |

## Evidence Sources

All visuals are generated from dossier-local evidence in:

```text
../evidence_assets/
```

Primary source CSVs:

- `short_review_aggregate_profile_v0_1.csv`
- `short_review_short_volume_duplicate_key_by_ticker_v0_1.csv`
- `short_review_short_volume_duplicate_key_manifest_v0_1.csv`
- `short_review_local_comparison_summary_v0_1.csv`
- `short_review_numeric_sanity_v0_1.csv`
- `short_review_null_profile_v0_1.csv`
- `short_review_scope_limitations_v0_1.csv`
- `short_review_provenance_assets_v0_1.csv`
- `sample_payloads/*.csv`

## Final Rule

This package makes the scoped FINRA baseline/provenance state visually
inspectable. It does not make `short_review` a production replacement for local
short data.

Correct reading:

```text
foundations_completion_status = human_inspector_ready_scoped
visual_inspection_status = visual_complete
data_quality_verdict = complete_scoped_provenance_with_short_volume_key_flags
```
