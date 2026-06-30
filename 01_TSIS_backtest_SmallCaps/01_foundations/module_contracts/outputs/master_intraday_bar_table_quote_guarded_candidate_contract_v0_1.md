# Master Intraday Bar Table Quote-Guarded Candidate Contract `v0_1`

## 1. Role

This document defines the candidate route for the next
`master_intraday_bar_table` expansion that depends on the
`ohlcv_1m_quote_guarded` repair workstream.

It does not materialize a parquet dataset.
It does not promote `master_intraday_bar_table_v0_2`.
It does not modify `master_intraday_bar_table_v0_1`.

Its purpose is to make the current decision explicit:

```text
Build everything that can be built now around the future quote-guarded
intraday source, but leave final materialization and source-path promotion
blocked until the quote-guarded repair run is completed and validated under
the official E-root output.
```

## 2. Candidate Identity

Planned candidate:

```text
dataset_id: master_intraday_bar_table_v0_2_candidate_quote_guarded
promotion_state: candidate_contract_defined_not_materialized
materialization_scope: quote_guarded_full_universe_candidate_pending_final_repair
full_universe_claim: false
```

Target candidate path:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_2_candidate_quote_guarded/
```

The path above must not be created by a smoke run or an incomplete repair run.
It is reserved for the first governed candidate materialization after the
quote-guarded source root is complete enough to validate.

## 3. Relationship To `v0_1`

Current official scoped table:

```text
dataset_id: master_intraday_bar_table_v0_1
scope: scoped_split_normalized_event_cases
full_universe_claim: false
status: scoped_pilot
```

The candidate route in this document must not overwrite or reinterpret v0.1.

Forbidden:

```text
reuse v0_1 path
turn v0_1 into full-universe by documentation
claim backtest_core eligibility from v0_1
mix v0_1 scoped split-normalized pilot rows with quote-guarded candidate rows
```

## 4. Current Bridge Source

The active bridge source is the live repair run:

```text
run_root: C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838
minute_root: E:/TSIS/data/ohlcv_1m
quotes_root: D:/quotes
output_root: E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded
```

Current bridge state:

```text
repair_run_state: running_or_not_final_validated
quotes_root_state: provisional_d_legacy_recovery_root_pending_e_parity
raw_1m_root_state: official_e_raw_root
official_quote_guarded_root_state: pending_final_manifest_and_validation
```

The bridge source can be used for contract design, builder design, tests over
small fixtures and preflight checks.

It must not be used to promote `master_intraday_bar_table_v0_2_candidate`.

## 5. Future Official Source

The future official source must live under:

```text
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/
```

Required final artifacts before the candidate table may be materialized:

```text
repair_summary_v0_2_or_later.json
repair_manifest_v0_2_or_later.parquet
validation_report_final.json
run_config.json
source lineage for E:/TSIS/data/ohlcv_1m
source lineage for quotes root used to build the repair manifest
```

If the final quote-guarded contract chooses different filenames, this
candidate contract must be updated before materialization.

## 6. Required Storage Semantics

The quote-guarded source for this table is an overlay/delta, not a complete
replacement copy of the 20-year OHLCV 1m universe.

The correct model is:

```text
raw ohlcv_1m + repair_manifest = ohlcv_1m_quote_guarded view
```

The repair process:

1. reads raw monthly parquets from `E:/TSIS/data/ohlcv_1m`;
2. reads quotes from `D:/quotes` while E-root quotes parity is pending;
3. detects minutes where `o/h/l/c` or `vw` are incompatible with the quote
   envelope;
4. writes only affected rows to repair manifests;
5. does not modify `E:/TSIS/data/ohlcv_1m`;
6. does not create a complete corrected tree with every original monthly
   parquet.

During the active run, affected rows are written under:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838/repair_shards/
```

Each shard is a ticker-month manifest, conceptually:

```text
TICKER_YYYY_MM_repair_manifest.parquet
```

Expected repair row fields include:

```text
ticker
ts_utc
o_raw
h_raw
l_raw
c_raw
o_qg
h_qg
l_qg
c_qg
repair_state
repair_reason
quote_bid_floor
quote_ask_cap
quote_count
source_ohlcv_path
source_quotes_path
```

At completion, the run consolidates shards into:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838/repair_manifest.parquet
```

If promotion is enabled and validation passes, the promoted artifact should be:

```text
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_v0_2.parquet
```

That promoted parquet is the main artifact for this table route. It is not
"all corrected market data"; it is the institutional list of affected minutes
and the OHLC overlay to apply.

Loader semantics required by this table:

1. load the raw monthly OHLCV parquet;
2. find matching rows in the repair manifest for the ticker/date range;
3. replace `o/h/l/c` in memory with `o_qg/h_qg/l_qg/c_qg` only on affected
   minutes;
4. add flags such as `quote_guarded_repair_applied`, `repair_state` and
   `repair_reason`;
5. return a quote-guarded view without mutating raw storage.

Important row-count interpretation:

```text
repair_rows != full replacement bars
```

A large `repair_rows` value means many affected rows exist in the manifest,
including rows where only VWAP is invalid. The subset that actually changes
OHLC is `ohlc_repair_rows`.

Future performance optimization may materialize a full corrected physical
tree, but that would require a separate contract, schema, output path,
manifest and promotion decision. This candidate route is manifest-first.

## 7. Price View Strategy

The first quote-guarded candidate must separate observed raw bars from repaired
raw-scale bars.

Required candidate price views:

```text
1m_raw
1m_quote_guarded_raw
```

Optional later price view:

```text
1m_quote_guarded_split_normalized
```

`1m_quote_guarded_split_normalized` is blocked until the builder proves that
quote-guarded OHLC fields can be split-normalized with the same corporate
action policy as raw 1m without changing volume, transaction count or VWAP
semantics incorrectly.

## 8. Required Candidate Columns

The candidate must preserve the v0.1 identity and lineage style and add
quote-guarded repair lineage.

Required added fields:

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

VWAP rule:

```text
Do not reconstruct VWAP from quotes.
If VWAP is invalid under the quote-guarded repair manifest, preserve the
invalid status and block direct VWAP consumption.
```

## 9. Builder Requirements

The builder must be config-driven before any broad run.

Required config:

```text
configs/data_foundation_outputs/master_intraday_bar_table_quote_guarded_candidate_v0_2.json
```

The builder must accept:

- dataset id;
- output root;
- raw 1m root;
- quote-guarded repair manifest root;
- quote-guarded run id;
- source quote root state;
- materialization scope;
- full-universe claim flag defaulting to false;
- overwrite policy that refuses to write into v0.1 paths.

The builder must not use recursive blind discovery over millions of files as
the primary denominator. It must consume a manifest or partition list produced
by the quote-guarded repair workstream.

The builder must not require or expect a complete corrected parquet tree. The
governed input is the raw 1m tree plus repair manifest overlay.

## 10. Required Validators

Before materialization:

- config exists and is internally consistent;
- target path is not a v0.1 path;
- final quote-guarded E-root requirement is explicit;
- provisional `D:/quotes` lineage is explicit;
- `full_universe_claim=false`;
- promotion blockers are present.

After materialization:

- denominator manifest reconciliation;
- row count by price view;
- duplicate key check;
- raw vs quote-guarded OHLC overlay check;
- VWAP invalid-status preservation;
- non-negative volume;
- no execution truth claim;
- no direct ML/RL eligibility;
- no backtest-core eligibility unless quality gates explicitly allow it.

## 11. Promotion Blockers

This route remains blocked until all are true:

```text
quote_guarded repair run completed
final validation report passed
official E-root quote-guarded manifest exists
source quotes root state is resolved or explicitly accepted for candidate only
builder consumes manifest rather than blind recursive scan
tests pass against final artifacts
registry/schema/validator/status matrix/changelog updated
Graphify refresh queue updated
human review accepts the candidate evidence
```

## 12. Current Status

```text
status: candidate_contract_defined_not_materialized
official_dataset_created: false
safe_to_modify_v0_1: false
safe_to_launch_full_materialization: false
next_executable_action: implement config/preflight tests and wait for final quote-guarded E-root repair output
```
