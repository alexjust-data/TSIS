# Regime Indicators Inspection Dossier

This dossier records the foundation inspection package for:

```text
regime_indicators_v0_1
```

Physical root:

```text
E:/TSIS/data/regime_indicators
```

Data-quality state:

```text
blocked_daily_scoped_minute_review_v0_1
```

Foundations completion status:

```text
human_inspector_ready
```

Visual inspection status:

```text
visual_complete
```

`human_inspector_ready` does not mean the data is production-ready. It means the
blocked/scoped state is now documented with enough evidence for a human auditor.

## Dossier Map

| Area | Path | Purpose |
| --- | --- | --- |
| Primary readout | `regime_indicators_inspection_readout_v0_1.md` | Human-facing audit narrative and verdict. |
| Evidence assets | `evidence_assets/` | Stable CSV/JSON summaries and sample payloads. |
| Visual inspector pack | `visual_inspector_pack/regime_indicators_visual_inspector_pack_v0_1.md` | Visual blocker, review, coverage and consumption-boundary evidence. |
| Build note | `build_regime_indicators_inspection_pack.md` | Rebuild and provenance note for this dossier. |
| Good/scoped evidence | `good_justification/regime_indicators_minute_and_metadata_examples_v0_1.md` | Minute and metadata evidence that is usable for inspection only. |
| Bad/blocking evidence | `bad_case_evidence_packs/regime_indicators_daily_date_blocker_v0_1.md` | Daily date/datetime blocker. |
| Flagged evidence | `flagged_case_evidence_packs/regime_indicators_minute_review_cases_v0_1.md` | Minute review flags, including `high < low` rows. |
| Coverage evidence | `coverage_case_evidence_packs/regime_indicators_inventory_coverage_v0_1.md` | Physical inventory and read-error evidence. |
| Quality report | `../../data_quality_report/families/regime_indicators_quality_report_v0_1.md` | Normalized family quality report. |

## Current Evidence Snapshot

| Metric | Value |
| --- | ---: |
| Parquet files | 67 |
| JSON metadata files | 2 |
| Read errors | 0 |
| Daily files | 34 |
| Daily rows | 153,397 |
| Daily files with only `1970-01-01` as `date` | 34 |
| Minute files | 33 |
| Minute rows | 64,348,953 |
| Minute duplicate timestamp rows | 0 |
| Minute non-monotonic files | 0 |
| Minute `high < low` rows | 204 |

## Required Inspector Path

Read in this order:

1. `regime_indicators_inspection_readout_v0_1.md`
2. `visual_inspector_pack/regime_indicators_visual_inspector_pack_v0_1.md`
3. `visual_inspector_pack/regime_indicators_visual_case_manifest_v0_1.csv`
4. `evidence_assets/README.md`
5. `bad_case_evidence_packs/regime_indicators_daily_date_blocker_v0_1.md`
6. `flagged_case_evidence_packs/regime_indicators_minute_review_cases_v0_1.md`
7. `good_justification/regime_indicators_minute_and_metadata_examples_v0_1.md`
8. `coverage_case_evidence_packs/regime_indicators_inventory_coverage_v0_1.md`
9. `../../data_quality_report/families/regime_indicators_quality_report_v0_1.md`

## Final Rule

Daily regime bars are blocked for any calendar-keyed downstream use.

Minute files and metadata may be used only for source validation, forensic
review, repair planning and explicitly scoped research inspection.
