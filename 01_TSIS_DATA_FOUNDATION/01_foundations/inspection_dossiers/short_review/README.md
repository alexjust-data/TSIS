# Short Review Inspection Dossier

This dossier records the scoped FINRA official/free baseline package for:

```text
short_review_finra_v0_1
```

Physical root:

```text
E:/TSIS/data/short_review/finra_short
```

Data-quality state:

```text
complete_scoped_provenance_with_short_volume_key_flags
```

Foundations completion status:

```text
human_inspector_ready_scoped
```

Visual inspection status:

```text
visual_complete
```

This means the family is complete for official/free FINRA baseline and
provenance review. It does not mean it is a production short-data replacement.

## Dossier Map

| Area | Path | Purpose |
| --- | --- | --- |
| Primary readout | `short_review_inspection_readout_v0_1.md` | Human-facing baseline/provenance verdict. |
| Evidence assets | `evidence_assets/` | Stable CSV/JSON summaries, manifests and samples. |
| Visual inspector pack | `visual_inspector_pack/short_review_visual_inspector_pack_v0_1.md` | Visual coverage, duplicate-key, overlap, numeric sanity and provenance-boundary evidence. |
| Build note | `build_short_review_inspection_pack.md` | Rebuild and provenance note for this dossier. |
| Good/scoped cases | `good_justification/short_review_finra_baseline_good_cases_v0_1.md` | Positive FINRA baseline and numeric/provenance evidence. |
| Flagged cases | `flagged_case_evidence_packs/short_review_short_volume_key_flags_v0_1.md` | Duplicate short-volume `ticker + date` keys. |
| Scope/history boundaries | `bad_case_evidence_packs/short_review_scope_and_history_boundaries_v0_1.md` | Claims blocked by source scope and official/free history gaps. |
| Coverage evidence | `coverage_case_evidence_packs/short_review_coverage_and_provenance_v0_1.md` | Physical file counts, logs and provenance. |
| Quality report | `../../data_quality_report/families/short_review_quality_report_v0_1.md` | Normalized family quality report. |

## Current Evidence Snapshot

| Metric | Short interest | Short volume |
| --- | ---: | ---: |
| Rows | 505,745 | 4,689,038 |
| Tickers | 4,687 | 4,623 |
| Date min | 2017-12-29 | 2018-08-01 |
| Date max | 2026-04-15 | 2026-04-29 |
| Aggregate read errors | 0 | 0 |
| Duplicate logical keys | 0 | 824 |
| Duplicate excess rows | 0 | 5,250 |

Affected duplicate-key short-volume tickers:

- `CPS`
- `OP`
- `LFTR`

## Required Inspector Path

Read in this order:

1. `short_review_inspection_readout_v0_1.md`
2. `visual_inspector_pack/short_review_visual_inspector_pack_v0_1.md`
3. `visual_inspector_pack/short_review_visual_case_manifest_v0_1.csv`
4. `evidence_assets/README.md`
5. `good_justification/short_review_finra_baseline_good_cases_v0_1.md`
6. `flagged_case_evidence_packs/short_review_short_volume_key_flags_v0_1.md`
7. `bad_case_evidence_packs/short_review_scope_and_history_boundaries_v0_1.md`
8. `coverage_case_evidence_packs/short_review_coverage_and_provenance_v0_1.md`
9. `../../data_quality_report/families/short_review_quality_report_v0_1.md`

## Final Rule

`short_review` is valid as official/free FINRA baseline and provenance.

It is not valid as a silent replacement for `E:/TSIS/data/short`, not valid as
full-history proof, and not valid as direct clean short-volume analytic input
until duplicate-key handling is explicitly defined.
