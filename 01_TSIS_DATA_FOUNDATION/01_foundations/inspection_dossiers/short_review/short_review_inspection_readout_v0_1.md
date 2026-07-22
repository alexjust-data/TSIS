# Short Review Inspection Readout v0.1

## 1. Verdict

`short_review_finra_v0_1` is accepted as:

```text
official_free_baseline_provenance
```

Foundations completion status:

```text
human_inspector_ready_scoped
```

Visual inspection status:

```text
visual_complete
```

It is a FINRA official/free baseline and provenance layer for the module's short-side context.

It is not:

- a silent replacement for `E:/TSIS/data/short`;
- proof of full 2005-2026 short completeness;
- consolidated market-wide shorting truth;
- executable quote/trade data.

## 2. Scope

Physical root:

```text
E:/TSIS/data/short_review/finra_short
```

Outer documentation root:

```text
E:/TSIS/data/short_review
```

Observed first-level structure:

- `raw`;
- `normalized`;
- `artifacts`;
- `logs`;
- `finra_short_pipeline.py`;
- `README.md`.

## 3. Authorities

Contracts and registry:

- `../../contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md`
- `../../dataset_registry/short_review/short_review_registry_entry.yaml`
- `../../data_consumption_policies/short_review_consumption_policy.md`
- `../../validators/short_review/short_review_validators.md`

Schemas:

- `../../canonical_schemas/short_review/finra_short_interest_schema_contract.md`
- `../../canonical_schemas/short_review/finra_short_volume_schema_contract.md`
- `../../canonical_schemas/short_review/finra_short_provenance_schema_contract.md`

Related short dossier:

- `../short/short_institutional_closeout_v0_1.md`

Data-quality report:

- `../../data_quality_report/families/short_review_quality_report_v0_1.md`

Dossier-local evidence:

- `evidence_assets/README.md`
- `evidence_assets/short_review_evidence_assets_manifest_v0_1.csv`
- `visual_inspector_pack/README.md`
- `visual_inspector_pack/short_review_visual_inspector_pack_v0_1.md`
- `visual_inspector_pack/short_review_visual_case_manifest_v0_1.csv`
- `visual_inspector_pack/short_review_visual_asset_audit_v0_1.csv`
- `good_justification/short_review_finra_baseline_good_cases_v0_1.md`
- `flagged_case_evidence_packs/short_review_short_volume_key_flags_v0_1.md`
- `bad_case_evidence_packs/short_review_scope_and_history_boundaries_v0_1.md`
- `coverage_case_evidence_packs/short_review_coverage_and_provenance_v0_1.md`
- `build_short_review_inspection_pack.md`

## 4. Source Research

The source research concluded:

- FINRA official/free `short_volume` can be reconstructed from `2018-08-01+`;
- FINRA official/free modern `short_interest` can be reconstructed from available historical files;
- official/free evidence does not support claiming complete equivalent `short_volume` from 2005-2018;
- official/free evidence does not support claiming fully equivalent exchange-listed `short_interest` from 2005-2013.

## 5. Physical And Technical Profile

Expected structure:

```text
raw/short_volume/daily/date=YYYYMMDD/*.txt
raw/short_interest/biweekly/settlement_date=YYYYMMDD/*.csv
normalized/short_volume/TICKER.parquet
normalized/short_interest/TICKER.parquet
artifacts/*.parquet
logs/*.csv
```

Aggregate artifacts:

- `artifacts/short_volume_all_daily_finra.parquet`;
- `artifacts/short_interest_all_biweekly_finra.parquet`.

Observed compact footprint:

| Segment | Logical group | Files |
| --- | --- | ---: |
| `artifacts` | aggregate artifacts/manifests | 4 |
| `logs` | download logs | 2 |
| `normalized` | short interest | 4,687 |
| `normalized` | short volume | 4,623 |
| `raw` | short interest | 193 |
| `raw` | short volume | 11,676 |

## 6. Coverage Snapshot

FINRA short interest:

| Metric | Value |
| --- | ---: |
| rows | 505,745 |
| tickers | 4,687 |
| date min | `2017-12-29` |
| date max | `2026-04-15` |

FINRA short volume:

| Metric | Value |
| --- | ---: |
| rows | 4,689,038 |
| tickers | 4,623 |
| date min | `2018-08-01` |
| date max | `2026-04-29` |

Aggregate key quality:

| Dataset | Key | Rows | Unique keys | Duplicate excess rows |
| --- | --- | ---: | ---: | ---: |
| FINRA short interest | `ticker + settlement_date` | 505,745 | 505,745 | 0 |
| FINRA short volume | `ticker + date` | 4,689,038 | 4,683,788 | 5,250 |

Short volume duplicate-key rows are concentrated in:

| Ticker | Duplicate keys | Duplicate rows | Excess rows | Date range |
| --- | ---: | ---: | ---: | --- |
| `CPS` | 638 | 5,188 | 4,550 | 2018-08-01 to 2021-02-11 |
| `OP` | 173 | 828 | 655 | 2024-01-23 to 2024-09-27 |
| `LFTR` | 13 | 58 | 45 | 2022-01-20 to 2022-02-10 |

## 7. Comparison To Local `short`

Short volume:

| Metric | Value |
| --- | ---: |
| local/Polygon files | 4,824 |
| FINRA files | 4,623 |
| intersection | 4,623 |
| only local/Polygon | 201 |
| only FINRA | 0 |

Short interest:

| Metric | Value |
| --- | ---: |
| local/Polygon files | 4,824 |
| FINRA files | 4,687 |
| intersection | 4,687 |
| only local/Polygon | 137 |
| only FINRA | 0 |

Interpretation:

- FINRA is strong as an official/free comparator;
- local-only tickers are review cases, not automatic bad data;
- FINRA does not close the full historical gap.

## 8. Semantic Quality

Short interest:

- slow/biweekly;
- use `settlement_date`;
- requires lag assumptions before any event/backtest use;
- not same-day intraday pressure.

Short volume:

- daily;
- FINRA source-scope;
- `short_volume_ratio` is not consolidated market-wide shorting pressure;
- source/venue components must be preserved.

## 9. Case Evidence

| Evidence group | Path | Reading |
| --- | --- | --- |
| Good/scoped FINRA baseline | `good_justification/short_review_finra_baseline_good_cases_v0_1.md` | Aggregate artifacts are readable and useful as official/free FINRA baseline/provenance. |
| Flagged short-volume keys | `flagged_case_evidence_packs/short_review_short_volume_key_flags_v0_1.md` | Short volume has duplicate `ticker + date` keys that require explicit handling. |
| Scope/history boundaries | `bad_case_evidence_packs/short_review_scope_and_history_boundaries_v0_1.md` | Source limitations block full-history and replacement claims. |
| Coverage/provenance | `coverage_case_evidence_packs/short_review_coverage_and_provenance_v0_1.md` | Physical counts, logs, manifests and provenance are documented. |
| Visual inspector pack | `visual_inspector_pack/short_review_visual_inspector_pack_v0_1.md` | Shows FINRA coverage windows, duplicate-key concentration/cases, FINRA/local overlap, numeric sanity and provenance/history limits. |
| Stable evidence assets | `evidence_assets/` | CSV/JSON summaries and payload samples used by this readout. |

This satisfies the human-inspector scoped package requirement because the visual
inspection layer is now present. It does not make short review a clean
production short dataset.

## 10. Consumer Matrix

| Consumer | Status | Reason |
| --- | --- | --- |
| `source_validation` | allowed | Primary purpose. |
| `coverage_comparison` | allowed | FINRA vs local short. |
| `forensic_review` | allowed | Explains source scope. |
| `research_only` | allowed with scope | Must preserve date window and source. |
| `backtest_extended` | restricted | Only with declared source window, lag and duplicate-key handling. |
| `ml_flagged` | restricted | Only with source-scope and duplicate-key flags. |
| `backtest_core` | not enabled | Not full-history/core truth. |
| `execution_simulator` | not enabled | Not execution data. |
| `RL/live` | not enabled | Scope and history gaps remain. |

## 11. Open Debt

Open limitations:

- no official/free proof of full 2005-2026 short volume;
- no official/free proof of full 2005-2013 short interest equivalence;
- local-only tickers require review;
- duplicate short-volume `ticker + date` keys require explicit repair or consumer handling;
- paid/commercial sources may be required for literal full-history completeness.

## 12. Final Verdict

`short_review_finra_v0_1` is complete as a provenance/baseline layer.

It is not complete as a production short dataset replacement, and short volume
is not clean analytic input until duplicate-key semantics are defined.

Final state:

```text
official_free_baseline_provenance_not_short_replacement_with_short_volume_key_flags
```
