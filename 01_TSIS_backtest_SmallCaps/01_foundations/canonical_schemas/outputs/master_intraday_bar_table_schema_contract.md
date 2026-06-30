# Master Intraday Bar Table Schema Contract `v0_1`

## 1. Role

This document defines the canonical schema for:

```text
master_intraday_bar_table_v0_1
```

`master_intraday_bar_table` is the governed intraday bar surface for CAPA 1.

v0.1 is a scoped materialization over the ticker-months already materialized in
`ohlcv_1m_split_normalized`. It is not a full-universe 1m copy.

`ohlcv_1m_split_normalized` itself is a validated proof/pilot of the 1m split
normalization process. The schema below makes that pilot queryable and
testable; it does not declare that the whole raw 1m universe has already been
normalized.

## 2. Logical Unit

Unit:

```text
instrument intraday bar price-view row
```

Grain:

```text
instrument_id + ticker + ts_utc + bar_size + price_view
```

## 3. Physical Layout

Root:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table
```

Artifacts:

```text
master_intraday_bar_table_v0_1/
_master_intraday_bar_table_summary_v0_1.csv
_master_intraday_bar_table_manifest_v0_1.json
```

Layout:

```text
partitioned parquet dataset by year/month/price_view
```

Builder:

```text
scripts/materialize_master_intraday_bar_table.py
```

## 4. Sources

Governed sources v0.1:

- `E:/TSIS/data/ohlcv_1m_split_normalized`
- `E:/TSIS/data/ohlcv_1m`
- `instrument_master_v0_1`
- `corporate_actions_table_v0_1`
- `dataset_certification_matrix_v0_1`
- `minute_core_quality_manifest_v0_1.parquet`

The physical row source is the split-normalized ticker-month set. Raw 1m is
linked through `source_1m_file_reported` and quality manifests, not copied as a
full-universe scan.

This source is a proof/inspection set. Future event-specific or broader
materializations must rerun the audited split-normalization pipeline for their
own declared ticker-month scope.

## 5. Required Columns

Identity:

- `master_intraday_bar_id`
- `ticker`
- `instrument_id`
- `ts_utc`
- `session_date`
- `year`
- `month`
- `bar_size`
- `price_view`

Source and price semantics:

- `quality_gate_family`
- `source_dataset`
- `source_root`
- `source_file`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `vwap`
- `transaction_count`
- `source_t_epoch_ms`

Raw and split lineage:

- `source_raw_open`
- `source_raw_high`
- `source_raw_low`
- `source_raw_close`
- `source_raw_vwap`
- `source_raw_volume`
- `source_raw_transaction_count`
- `future_split_factor`
- `o_split_normalized`
- `h_split_normalized`
- `l_split_normalized`
- `c_split_normalized`
- `vw_split_normalized`
- `materialized_source_price_view`
- `source_1m_file_reported`
- `source_splits_file`
- `source_split_normalized_file`

Pilot context:

- `pilot_role`
- `pilot_event_type`
- `pilot_event_date`
- `session_segment`

Raw 1m quality:

- `raw_quality_manifest_present`
- `raw_quality_manifest_rows`
- `raw_core_quality_state`
- `raw_core_issue_family`
- `raw_combined_quality_state`
- `raw_allowed_consumption`
- `raw_vw_quality_state`
- `raw_vw_issue_family`
- `raw_final_policy_bucket_lt1b`
- `raw_manifest_negative_or_zero_ohlc_rows`
- `raw_manifest_negative_volume_rows`
- `raw_manifest_high_low_inversion_rows`
- `raw_manifest_duplicate_ts_utc_rows`
- `raw_manifest_vw_outside_range_rows`

Corporate-action context:

- `corporate_action_count`
- `split_action_count`
- `dividend_action_count`
- `ticker_change_action_count`
- `has_split_action`
- `has_dividend_action`
- `has_ticker_change_action`
- `has_any_corporate_action`

Quality and consumption:

- `row_level_price_integrity_state`
- `selected_price_hard_invalid`
- `negative_volume`
- `core_ohlcv_consumption_allowed`
- `vwap_consumption_allowed`
- `vwap_consumption_state`
- `event_research_bar_candidate`
- `backtest_core_bar_candidate`
- `full_universe_claim`
- `materialization_scope`
- `family_data_quality_verdict`
- `family_foundations_completion_status`
- `family_visual_inspection_status`
- `family_production_use_gate`
- `family_event_consumption_gate`
- `gate_quality_policy_version`

Lineage:

- `dataset_certification_matrix_build_run_id`
- `instrument_master_build_run_id`
- `instrument_master_schema_version`
- `quality_policy_version`
- `schema_version`
- `build_run_id`
- `created_at_utc`

## 6. Price Views

Allowed `price_view` values v0.1:

- `1m_raw`
- `1m_split_normalized`

Rules:

- `1m_raw` uses observed raw OHLCV values preserved in the split-normalized files.
- `1m_split_normalized` uses split-normalized OHLCV fields and preserves raw lineage.
- `volume` and `transaction_count` remain raw observed fields for both views.
- `vwap` is quality-gated by raw 1m `vw` policy; many rows are blocked for direct VWAP consumption.

## 7. Scope Rules

v0.1 materialization scope:

```text
scoped_split_normalized_event_cases
```

This means:

- 8 tickers;
- 10 ticker-months;
- 87,626 source split-normalized bars;
- 175,252 output rows across two price views;
- no full-universe claim.

It also means:

- this table is evidence that the normalization method is operational;
- it is not the normalized 1m universe for all `<1B>` tickers;
- consumers must materialize additional ticker-months explicitly when needed.

`backtest_core_bar_candidate` is false for every row in v0.1. Event research may
use rows only with explicit scoped flags.

## 8. Structural Rules

Hard structural failures:

- zero rows;
- duplicate `ticker + ts_utc + bar_size + price_view`;
- missing one of the two price views;
- output row count not equal to `split_normalized_source_rows * 2`;
- any row with `full_universe_claim = true`;
- missing manifest or summary;
- missing contract/schema/policy/registry/validator paths.

Quality flags, not structural hard failures:

- missing raw 1m quality manifest for a scoped ticker-month;
- `vwap_consumption_state = blocked_by_raw_vw_quality`;
- `backtest_core_bar_candidate = false`;
- scoped-only family production gates.

## 9. Interpretation

Permitted:

- scoped intraday event-window research;
- verification of split-normalized 1m semantics;
- linking daily context to intraday bars for the audited split-event cases;
- downstream event-engine dry runs that preserve scoped flags.

Not permitted:

- full-universe 1m backtest feed;
- raw execution simulator truth;
- quote/trade microstructure substitute;
- unflagged ML or RL state source.

## 10. Quote-Guarded Candidate Addendum

Planned candidate:

```text
dataset_id: master_intraday_bar_table_v0_2_candidate_quote_guarded
status: candidate_contract_defined_not_materialized
```

This candidate is governed by:

```text
01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
configs/data_foundation_outputs/master_intraday_bar_table_quote_guarded_candidate_v0_2.json
```

It is blocked until the `ohlcv_1m_quote_guarded` repair run is completed and
validated under:

```text
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/
```

Expected candidate price views:

```text
1m_raw
1m_quote_guarded_raw
```

Additional required columns:

```text
quote_guarded_view
quote_guarded_repair_applied
repair_state
repair_reason
vw_quote_guarded_status
quote_bid_floor
quote_ask_cap
quote_count
source_quote_guarded_repair_manifest
source_quote_guarded_run_id
source_quotes_root
source_quotes_root_state
requires_rebuild_after_e_quotes_parity
requires_rebuild_after_quote_guarded_e_promotion
```

Candidate rule:

```text
full_universe_claim must remain false until a denominator manifest, final
quote-guarded validation report and promotion review exist.
```

Storage rule:

```text
1m_quote_guarded_raw is a view:
raw ohlcv_1m + repair_manifest_v0_2 = quote-guarded OHLCV view
```

The first candidate must not assume that
`E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/` contains a full
replacement tree of corrected monthly OHLCV parquets. The required source is a
repair manifest/overlay plus immutable raw 1m.

Required interpretation:

```text
repair_rows = affected manifest rows
ohlc_repair_rows = rows where OHLC changes
vw_invalid_rows = rows where VWAP is invalid/blocked without quote rebuild
```

`1m_quote_guarded_split_normalized` is intentionally excluded from the first
candidate schema until split normalization over quote-guarded OHLC is tested
and documented separately.
