# Daily Quality Report v0.1

## 1. Scope And Role

Family:

```text
daily_core_v0_1
```

Physical root:

```text
E:/TSIS/data/ohlcv_daily
```

Historical inspection examples also reference:

```text
D:/ohlcv_daily
```

Role:

- RAW/STAGED daily OHLCV market data;
- canonical raw daily bar authority for Module 01;
- base layer for governed daily research and backtest consumers;
- not intraday microstructure, execution tape, quotes, adjusted daily, or split-normalized intraday data.

## 2. Final Status

```text
complete_import_ready
```

`daily_core_v0_1` is already institutional. This report imports the existing audit, contract and inspection dossier into the normalized `data_quality_report/` surface.

## 3. Artifact Map

| Artifact | Status | Path |
| --- | --- | --- |
| Dataset contract | present | `01_foundations/contract_registry/dataset_contracts/daily_dataset_contract_v0_1.md` |
| Label taxonomy and cut policy | present | `01_foundations/contract_registry/dataset_contracts/daily_label_taxonomy_and_cut_policy.md` |
| Registry entry | present | `01_foundations/dataset_registry/daily/daily_registry_entry.yaml` |
| Consumption policy | present | `01_foundations/data_consumption_policies/daily_consumption_policy.md` |
| Schema contract | present | `01_foundations/canonical_schemas/daily/daily_schema_contract.md` |
| Validators | present | `01_foundations/validators/daily/daily_validators.md` |
| Inspection readout | present | `01_foundations/inspection_dossiers/daily/daily_inspection_readout_v0_1.md` |
| Bad case evidence | present | `01_foundations/inspection_dossiers/daily/bad_case_evidence_packs/daily_hard_invalid_cases_v0_1.md` |
| Flagged case evidence | present | `01_foundations/inspection_dossiers/daily/flagged_case_evidence_packs/daily_non_good_quality_cases_v0_1.md` |
| Good justification | present | `01_foundations/inspection_dossiers/daily/good_justification/daily_good_cases_v0_1.md` |
| Coverage evidence | present | `01_foundations/inspection_dossiers/daily/coverage_case_evidence_packs/daily_coverage_cases_v0_1.md` |

## 4. File Structure And Technical Profile

Primary audited unit:

```text
ticker-year file
```

Example:

```text
D:/ohlcv_daily/ticker=HMNY/year=2025/day_aggs_HMNY_2025.parquet
```

Expected logical content:

- `ticker`;
- session/date field;
- `open`, `high`, `low`, `close`;
- `volume`;
- optional or conditional `vw` and `n`.

The file must be interpreted as a daily market bar file, not as a complete lifecycle object, corporate-action table, execution source, or adjusted-return source.

## 5. Population And Coverage

The current institutional readout reports:

| Metric | Value |
| --- | ---: |
| visual inspection `bad` cases | 102 |
| visual inspection `non_good_quality` cases | 48 |
| visual inspection `good` sample | 24 |
| tickers without `complete_daily` | 653 |
| recoverable without penalty | 374 |
| recoverable with flag | 222 |
| open coverage frontier | 57 |

The run base spans the global audited period `2005-2026`. This means the dataset was inspected across that global period; it does not mean every ticker is expected to exist in every year.

## 6. Cleanliness And Interpretability

Daily has two separate decision axes:

| Axis | Meaning |
| --- | --- |
| quality axis | Whether the bar itself remains parseable and economically interpretable. |
| coverage axis | Whether missingness or gaps are expected, recoverable, ambiguous or still open. |

Quality mapping:

| State | Buckets |
| --- | --- |
| `good` | `schema_only_or_other`, `vw_edge_absmax_only` |
| `recoverable_with_flag` | `vw_low_ratio_limited_days`, `vw_mid_ratio_illiquid_regime`, `vw_high_ratio_illiquid_regime`, `vw_warn_minor_or_material` |
| `bad` | `hard_invalid_parse_or_price` |

Coverage mapping:

| State | Buckets |
| --- | --- |
| `recoverable_without_penalty` | `LIKELY_VALID_GAP_ONLY` |
| `recoverable_with_flag` | `AMBIGUOUS_REVIEW` |
| `review_not_rehabilitated` | `REALLY_PROBLEMATIC_UNEXPECTED` |

Observed hard-invalid patterns include:

- `OHLC = 0`;
- critical daily fields in zero, such as `open = 0`, `low = 0` or `close = 0`;
- non-defensible parse or price states;
- internal contradictions such as `vw > high` when `high = 0`.

Those rows are not authorized for `backtest_core` unless later evidence rehabilitates them under versioned policy.

## 7. Semantic Quality

Daily is not globally perfect, but it is institutionally usable because the defects are classified and routed:

- the hard invalid tail is small and isolated;
- the `vw` residue is mostly a secondary diagnostic issue, not the foundation of daily bar authority;
- many coverage gaps are recoverable or explainable rather than hard corruption;
- `good` means usable daily bar quality, not literal absence of every warning.

The primary authority of daily is:

- parse;
- session/date semantics;
- OHLCV range integrity;
- coverage state.

`vw` is useful for diagnostics and flags, but it does not displace OHLCV as the daily bar authority.

## 8. Case Evidence

The human auditor should read case evidence in this order:

1. `daily_inspection_readout_v0_1.md`
2. `daily_hard_invalid_cases_v0_1.md`
3. `daily_non_good_quality_cases_v0_1.md`
4. `daily_good_cases_v0_1.md`
5. `daily_coverage_cases_v0_1.md`

The casepacks answer different questions:

| Evidence | Answers |
| --- | --- |
| hard invalid cases | Where daily stops being a defensible market bar. |
| non-good quality cases | Which files are parseable but require `recoverable_with_flag`. |
| good cases | Why the main usable population is defensible even with bounded residue. |
| coverage cases | Which gaps are recoverable, ambiguous or still open. |

## 9. Consumer Matrix

| Consumer | Decision |
| --- | --- |
| `data_quality_report` | allowed |
| `backtest_core` | allowed for `good` quality and acceptable coverage state |
| `backtest_extended` | allowed with explicit flags |
| `ml_primary` | allowed only under policy and declared state |
| `ml_flagged` | allowed with explicit quality and coverage state |
| `research_only` | allowed |
| `forensic_only` | allowed for bad/open evidence |
| `execution_simulator` | prohibited as execution authority |
| `quotes/trades validation` | reference only, not replacement for their raw layers |
| `RL/live` | not enabled by this report |

## 10. Verdict

`daily_core_v0_1` meets the data-quality standard as the institutional raw daily market-bar layer.

Final verdict:

```text
complete_institutional_raw_daily_bar_layer_with_flagged_coverage_tail
```

## 11. Open Debt

- The `57` open coverage frontier cases remain outside automatic `backtest_core` authorization.
- `recoverable_with_flag` daily cases must stay explicitly flagged in downstream consumers.
- External chart comparisons must respect raw/adjusted/split-normalized price semantics.
- Any change to the daily quality taxonomy, coverage taxonomy or exclusion tail requires contract and changelog updates.
