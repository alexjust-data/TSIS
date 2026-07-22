# Financial Visual Inspector Pack

Fecha: 2026-06-20
Estado: `visual_complete_v0_1`

## Role

This folder is the visual inspection layer for:

```text
financial_v0_1
```

It closes the visual evidence requirement defined by:

```text
../../../VISUAL_INSPECTION_PACK_REQUIREMENTS.md
```

The visual pack does not change the data-quality verdict. The family remains:

```text
blocked_by_data_defect
```

## Reading Order

1. `financial_visual_inspector_pack_v0_1.md`
2. `financial_visual_case_manifest_v0_1.csv`
3. `financial_visual_asset_audit_v0_1.csv`
4. `images/*.png`
5. `build_financial_visual_inspector_pack.py`

## Generated Assets

| Visual | Role |
| --- | --- |
| `images/financial_endpoint_coverage_heatmap_v0_1.png` | population and coverage context |
| `images/financial_severe_issue_distribution_v0_1.png` | blocking issue distribution |
| `images/financial_temporal_issue_timeline_v0_1.png` | lifecycle and PIT review |
| `images/financial_empty_sentinel_case_panel_v0_1.png` | bad/blocking sentinel examples |
| `images/financial_multi_cik_identity_panel_v0_1.png` | identity review |
| `images/financial_payload_schema_drift_panel_v0_1.png` | schema/form interpretation |

## Evidence Sources

All visuals are generated from dossier-local evidence in:

```text
../evidence_assets/
```

Primary source CSVs:

- `financial_coverage_by_endpoint_v0_1.csv`
- `financial_file_level_quality_summary_v0_1.csv`
- `financial_severe_issue_summary_v0_1.csv`
- `financial_temporal_status_summary_v0_1.csv`
- `financial_temporal_issue_sample_manifest_v0_1.csv`
- `financial_empty_sentinel_example_manifest_v0_1.csv`
- `financial_multi_cik_example_manifest_v0_1.csv`
- `financial_date_range_summary_v0_1.csv`
- `sample_payloads/*.csv`

## Final Rule

This package makes the financial family inspectable at the visual evidence
standard. It does not make the data consumable.

Correct reading:

```text
foundations_completion_status = human_inspector_ready
visual_inspection_status = visual_complete
data_quality_verdict = blocked_by_data_defect
```
