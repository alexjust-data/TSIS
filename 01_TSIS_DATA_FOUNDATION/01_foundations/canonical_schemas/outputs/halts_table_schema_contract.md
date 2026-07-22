# Halts Table Schema Contract `v0_1`

Status: `canonical_schema_contract`

Dataset: `halts_table_v0_1`

Physical target:

```text
E:/TSIS/data/data_foundation_outputs/halts_table/halts_table_v0_1.parquet
```

## 1. Role

`halts_table_v0_1` is the governed CAPA 1 output table derived from
`halts_v0_1`.

It converts the official halts/suspensions master into a downstream-safe table
with stable event ids, event-state flags, quality states and consumer gates.

It is not raw source authority. The raw/source-preserved authority remains:

```text
E:/TSIS/data/Halts/
```

## 2. Grain

One row per persisted source master row from:

```text
E:/TSIS/data/Halts/processed/halts_master_multisource.parquet
```

`halt_event_id` is unique by construction.

`source_event_key` intentionally may be duplicated because source rows can
represent repeated or duplicated source-level event keys.

## 3. Required Columns

| Column | Required | Semantics |
| --- | --- | --- |
| `halt_event_id` | yes | stable row-level event id for this output |
| `source_event_key` | yes | hash of source semantic event fields before row-number disambiguation |
| `source_row_number` | yes | zero-based row number in the source master parquet |
| `duplicate_source_event_key` | yes | true when the source semantic key appears more than once |
| `source_dataset_id` | yes | expected `halts_v0_1` |
| `source` | yes | `nasdaq`, `nyse` or `sec` |
| `source_priority` | yes | inherited source priority |
| `ticker` | nullable | event ticker when available |
| `issuer_name` | nullable | issuer/security name from source |
| `listing_exchange` | nullable | source exchange/listing field |
| `halt_date` | nullable | event date from source master |
| `halt_start_et` | nullable | halt start timestamp in Eastern Time semantics |
| `resume_quote_et` | nullable | quote resume timestamp in Eastern Time semantics |
| `resume_trade_et` | nullable | trade resume timestamp in Eastern Time semantics |
| `halt_code` | nullable | source halt code |
| `halt_type` | nullable | source normalized halt/suspension class |
| `raw_reason` | nullable | source reason text |
| `release_no` | nullable | SEC release number when available |
| `item_link` | nullable | source item URL when available |
| `url_source` | yes | source feed/page URL |
| `is_sec_suspension` | yes | SEC suspension flag |
| `halt_event_state` | yes | governed event taxonomy |
| `event_granularity` | yes | intraday/date/regulatory/review/invalid granularity |
| `quality_state` | yes | `good`, `review` or `bad` |
| `intraday_consumption_state` | yes | consumer state for intraday masks |
| `source_allowed` | yes | source allowlist check |
| `has_ticker` | yes | non-empty ticker flag |
| `has_halt_date` | yes | halt date present flag |
| `has_halt_start_et` | yes | start timestamp present flag |
| `has_resume_quote_et` | yes | quote resume present flag |
| `has_resume_trade_et` | yes | trade resume present flag |
| `future_date_flag` | yes | halt_date after v0.1 expected max event date |
| `timestamp_order_review_flag` | yes | resume before halt start |
| `parse_suspect_flag` | yes | future-date or timestamp-order anomaly |
| `missing_core_event_flag` | yes | missing source/date or non-SEC missing ticker |
| `valid_for_event_engine` | yes | allowed for event engine context |
| `valid_for_intraday_mask` | yes | allowed as precise intraday halt mask |
| `valid_for_date_context` | yes | allowed as date-level/regulatory context |
| `valid_for_backtest_event_mask_candidate` | yes | candidate mask for backtests with availability contract |
| `valid_for_ml_flagged_candidate` | yes | candidate for ML only with leakage controls |
| `valid_for_execution_context_candidate` | yes | candidate context only, not execution truth |
| `prohibited_as_alpha` | yes | always true |
| `requires_decision_time_availability_contract` | yes | always true |
| `visual_case_bucket` | yes | not materialized in this table v0.1 |
| `market_overlay_state` | yes | not materialized in this table v0.1 |
| `source_master_path` | yes | source parquet path |
| `source_master_sha256` | yes | source parquet hash |
| `schema_version` | yes | expected `halts_table_v0_1` |
| `build_run_id` | yes | materialization run id |
| `created_at_utc` | yes | materialization timestamp |

## 4. Event-State Vocabulary

Allowed `halt_event_state` values:

- `good_full_intraday_event`
- `good_date_level_event`
- `regulatory_context_only`
- `review_partial_identity`
- `bad_unusable_event`

Allowed `quality_state` values:

- `good`
- `review`
- `bad`

Allowed `intraday_consumption_state` values:

- `intraday_mask_allowed`
- `date_level_only`
- `regulatory_context_only`
- `review_only`
- `forensic_only`

## 5. Rules

Hard schema failures:

- missing required column;
- duplicate `halt_event_id`;
- source outside allowlist;
- missing `schema_version`;
- missing `build_run_id`;
- `prohibited_as_alpha` not true.

Review states are expected and must not be coerced to good.

## 6. Non-Goals

This schema does not:

- normalize timestamps to UTC;
- repair source parse anomalies;
- materialize visual overlay buckets;
- prove execution feasibility;
- create alpha;
- authorize live or RL consumption.

