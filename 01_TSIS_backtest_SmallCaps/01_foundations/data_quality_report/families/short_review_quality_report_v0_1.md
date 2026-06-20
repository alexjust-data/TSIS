# Short Review Quality Report v0.1

## 1. Scope And Role

Family:

```text
short_review_finra_v0_1
```

Physical root:

```text
E:/TSIS/data/short_review/finra_short
```

Role:

- FINRA official/free baseline;
- provenance layer;
- comparator for `E:/TSIS/data/short`;
- source-scope short-side context.

## 2. Final Status

```text
complete_scoped_provenance_with_short_volume_key_flags
```

This family is complete for baseline/provenance use.

It is not a clean full-history short replacement.

Foundations completion status:

```text
human_inspector_ready_scoped
```

Visual inspection status:

```text
visual_complete
```

Important scoped flag:

```text
short_volume has duplicate ticker + date keys requiring explicit handling
```

## 3. Artifact Map

| Artifact | Status | Path |
| --- | --- | --- |
| Dataset contract | present | `01_foundations/contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md` |
| Registry entry | present | `01_foundations/dataset_registry/short_review/short_review_registry_entry.yaml` |
| Consumption policy | present | `01_foundations/data_consumption_policies/short_review_consumption_policy.md` |
| Validators | present as contract | `01_foundations/validators/short_review/short_review_validators.md` |
| Inspection readout | present | `01_foundations/inspection_dossiers/short_review/short_review_inspection_readout_v0_1.md` |
| Schemas | present | `01_foundations/canonical_schemas/short_review/` |
| Related short closeout | present | `01_foundations/inspection_dossiers/short/short_institutional_closeout_v0_1.md` |
| Source research | present | `E:/TSIS/data/short_review/research_short_sources.md` |
| Dossier evidence assets | present | `01_foundations/inspection_dossiers/short_review/evidence_assets/` |
| Visual inspector pack | present | `01_foundations/inspection_dossiers/short_review/visual_inspector_pack/short_review_visual_inspector_pack_v0_1.md` |
| Good/scoped cases | present | `01_foundations/inspection_dossiers/short_review/good_justification/short_review_finra_baseline_good_cases_v0_1.md` |
| Flagged key cases | present | `01_foundations/inspection_dossiers/short_review/flagged_case_evidence_packs/short_review_short_volume_key_flags_v0_1.md` |
| Scope/history boundaries | present | `01_foundations/inspection_dossiers/short_review/bad_case_evidence_packs/short_review_scope_and_history_boundaries_v0_1.md` |
| Coverage/provenance evidence | present | `01_foundations/inspection_dossiers/short_review/coverage_case_evidence_packs/short_review_coverage_and_provenance_v0_1.md` |

## 4. File Structure And Technical Profile

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

- `short_volume_all_daily_finra.parquet`;
- `short_interest_all_biweekly_finra.parquet`.

Compact physical footprint:

| Segment | Logical group | Files |
| --- | --- | ---: |
| `artifacts` | aggregate artifacts/manifests | 4 |
| `logs` | download logs | 2 |
| `normalized` | short interest | 4,687 |
| `normalized` | short volume | 4,623 |
| `raw` | short interest | 193 |
| `raw` | short volume | 11,676 |

## 5. Coverage

| Dataset | Rows | Tickers | Date range |
| --- | ---: | ---: | --- |
| FINRA short interest | 505,745 | 4,687 | `2017-12-29` to `2026-04-15` |
| FINRA short volume | 4,689,038 | 4,623 | `2018-08-01` to `2026-04-29` |

Aggregate key quality:

| Dataset | Key | Rows | Unique keys | Duplicate excess rows |
| --- | --- | ---: | ---: | ---: |
| FINRA short interest | `ticker + settlement_date` | 505,745 | 505,745 | 0 |
| FINRA short volume | `ticker + date` | 4,689,038 | 4,683,788 | 5,250 |

## 6. Local Comparison

| Dataset | Local/Polygon files | FINRA files | Intersection | Local-only | FINRA-only |
| --- | ---: | ---: | ---: | ---: | ---: |
| `short_volume` | 4,824 | 4,623 | 4,623 | 201 | 0 |
| `short_interest` | 4,824 | 4,687 | 4,687 | 137 | 0 |

## 7. Cleanliness And Interpretability

`short_review` is interpretable when its source scope is preserved.

Required interpretation:

- FINRA short volume is source-scope, not consolidated market-wide shorting truth;
- FINRA short interest is slow/biweekly and requires lag assumptions;
- pre-2018 short-volume completeness is not proven with official/free sources;
- old short-interest history is not fully proven back to 2005 with equivalent semantics.
- FINRA short volume has duplicate `ticker + date` keys in `CPS`, `OP` and `LFTR`; consumers must not collapse these silently.

## 8. Case Evidence

| Evidence group | Path | Reading |
| --- | --- | --- |
| Good/scoped baseline | `01_foundations/inspection_dossiers/short_review/good_justification/short_review_finra_baseline_good_cases_v0_1.md` | Aggregate artifacts are readable and useful as official/free FINRA baseline/provenance. |
| Flagged key cases | `01_foundations/inspection_dossiers/short_review/flagged_case_evidence_packs/short_review_short_volume_key_flags_v0_1.md` | Short volume has duplicate `ticker + date` keys requiring explicit handling. |
| Scope/history boundaries | `01_foundations/inspection_dossiers/short_review/bad_case_evidence_packs/short_review_scope_and_history_boundaries_v0_1.md` | Blocks full-history and replacement claims. |
| Coverage/provenance | `01_foundations/inspection_dossiers/short_review/coverage_case_evidence_packs/short_review_coverage_and_provenance_v0_1.md` | Physical file counts, logs, manifests and source documents. |
| Visual inspector pack | `01_foundations/inspection_dossiers/short_review/visual_inspector_pack/short_review_visual_inspector_pack_v0_1.md` | Visualizes FINRA coverage, duplicate-key flags, local overlap, numeric sanity and provenance/history boundaries. |
| Evidence assets | `01_foundations/inspection_dossiers/short_review/evidence_assets/` | Stable CSV/JSON summaries and payload samples. |

## 9. Consumer Matrix

| Consumer | Decision |
| --- | --- |
| `source_validation` | allowed |
| `coverage_comparison` | allowed |
| `forensic_review` | allowed |
| `research_only` | allowed with source scope |
| `backtest_extended` | restricted |
| `ml_flagged` | restricted |
| `backtest_core` | not enabled |
| `execution_simulator` | not enabled |
| `rl_allowed` | not enabled |
| `live_downstream_candidate` | not enabled |

Backtest/ML restrictions require source scope, date window, short-interest lag
and duplicate-key handling.

## 10. Open Debt

- no official/free full-history proof for `short_volume` 2005-2018;
- no official/free full-history proof for `short_interest` 2005-2013;
- local-only tickers require review;
- duplicate FINRA short-volume keys require explicit repair or consumer policy;
- full historical completion may require paid/commercial sources.

## 11. Verdict

`short_review_finra_v0_1` meets the standard for a scoped provenance/baseline layer.

Final verdict:

```text
official_free_baseline_provenance_not_short_replacement_with_short_volume_key_flags
```
