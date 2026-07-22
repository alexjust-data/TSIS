# Daily Adjusted Inspection Dossier

Family:

```text
daily_adjusted_v0_1
```

Physical root:

```text
E:/TSIS/data/ohlcv_daily_adjusted
```

Foundations completion status:

```text
human_inspector_ready
```

Visual inspection status:

```text
visual_complete
```

## Role

This wrapper dossier gives `daily_adjusted_v0_1` its own inspector surface while
preserving the historical audit evidence under:

```text
../daily/
```

The governed evidence sources remain:

- `../daily/daily_adjusted_full_universe_audit_v0_1.md`
- `../daily/daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md`
- `../daily/evidence_assets/daily_adjusted_full_universe_audit/`
- `../daily/evidence_assets/daily_adjusted_complex_actions_tail_audit/`

## Dossier Map

| Area | Path | Purpose |
| --- | --- | --- |
| Visual inspector pack | `visual_inspector_pack/` | Formal visual readout, images, manifest and asset audit for daily adjusted. |
| Full-universe audit | `../daily/daily_adjusted_full_universe_audit_v0_1.md` | Materialization coverage, factor validation and activation profile. |
| Complex corporate-action tail audit | `../daily/daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md` | Boundary debt for ticker changes and non-CD dividend subtype. |
| Normalized quality report | `../../data_quality_report/families/daily_adjusted_quality_report_v0_1.md` | Family-level data quality report. |

## Required Inspector Path

1. `visual_inspector_pack/daily_adjusted_visual_inspector_pack_v0_1.md`
2. `visual_inspector_pack/daily_adjusted_visual_case_manifest_v0_1.csv`
3. `visual_inspector_pack/daily_adjusted_visual_asset_audit_v0_1.csv`
4. `../daily/daily_adjusted_full_universe_audit_v0_1.md`
5. `../daily/daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md`
6. `../../data_quality_report/families/daily_adjusted_quality_report_v0_1.md`

## Final Rule

`daily_adjusted_v0_1` is a full-universe derived economic daily price view.

It is not raw daily authority, quotes/trades validation authority, execution
authority, live/RL input, or a replacement for explicit consumer contracts.
