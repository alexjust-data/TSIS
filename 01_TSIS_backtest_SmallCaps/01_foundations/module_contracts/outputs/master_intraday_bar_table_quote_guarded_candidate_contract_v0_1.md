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
Build the candidate route around the promoted LT1B quote-guarded repair
manifest. Final materialization of this master intraday candidate remains
blocked until the builder, preflight validators, tests and human review consume
the promoted manifest and produce candidate evidence.
```

## 2. Candidate Identity

Planned candidate:

```text
dataset_id: master_intraday_bar_table_v0_2_candidate_quote_guarded
promotion_state: scoped_candidate_materialized_not_official
materialization_scope: quote_guarded_lt1b_candidate_pending_builder_materialization
full_universe_claim: false
```

Target candidate path:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_2_candidate_quote_guarded/
```

The path above now exists as the first scoped E-root candidate materialization.
It is not an official/promoted table and does not claim full-universe coverage.

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

## 4. Current Official Quote-Guarded Source

The historical bridge source was the broad repair run. The current accepted
source is the promoted LT1B overlay manifest plus raw 1m:

```text
run_root: C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838
minute_root: E:/TSIS/data/ohlcv_1m
quotes_root: D:/quotes
output_root: E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded
```

Current bridge state:

```text
repair_run_state: PASS_promoted_lt1b_manifest
quotes_root_state: provisional_d_legacy_recovery_root_pending_e_parity
raw_1m_root_state: official_e_raw_root
official_quote_guarded_root_state: promoted_manifest_available
manifest_path: E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
manifest_rows: 301278342
```

The promoted manifest can now be used as the official quote-guarded source for
builder design, preflight checks and candidate materialization attempts. It
does not itself promote `master_intraday_bar_table_v0_2_candidate`.

## 5. Official Source

The official source lives under:

```text
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/
```

Quote-guarded artifacts available for candidate materialization attempts:

```text
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1_summary.json
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1_sample.csv
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_lt1b_consolidation_manual_20260703_094500/consolidation_summary.json
```

Remaining candidate-table gates are small-scope builder/materialization evidence,
validation reports, and explicit promotion review. The lightweight preflight now
passes against the promoted LT1B artifacts, but it does not materialize the
candidate table. Raw-only scanner artifacts remain non-canonical for the LT1B
quote-guarded route.

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
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
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

This route has cleared the upstream repair-manifest gate. Candidate table
materialization remains blocked until all remaining gates are true:

```text
quote_guarded repair run completed: true
final LT1B consolidation summary PASS: true
official E-root quote-guarded manifest exists: true
source quotes root state is resolved or explicitly accepted for candidate only
builder consumes manifest rather than blind recursive scan
tests pass against final artifacts
registry/schema/validator/status matrix/changelog updated
Graphify refresh queue updated
human review accepts the candidate evidence
```

## 12. Current Status

```text
status: scoped_candidate_materialized_not_official
official_dataset_created: false
e_root_candidate_created: true
safe_to_modify_v0_1: false
safe_to_launch_full_materialization: false
quote_guarded_manifest_gate: passed
lightweight_preflight_status: passed
latest_preflight_report: C:/TSIS_Data/tests/test_runs/2026-07-05/master_intraday_quote_guarded_candidate_preflight_v0_1/master_intraday_quote_guarded_candidate_preflight_v0_1.json
next_executable_action: decide wider or declared-universe scope after scoped E-root candidate passed
```

## 12.1 Latest Lightweight Preflight

Script:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/preflight_master_intraday_quote_guarded_candidate.py
```

Report:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/master_intraday_quote_guarded_candidate_preflight_v0_1/master_intraday_quote_guarded_candidate_preflight_v0_1.json
```

Resultado:

```text
validator_status = passed
validator_hard_fail_count = 0
validator_warning_count = 0
minute_root_exists = true
quotes_root_exists = true
quote_guarded_root_exists = true
repair_manifest_exists = true
repair_summary_exists = true
repair_sample_exists = true
consolidation_summary_exists = true
repair_sample_column_count = 36
manifest_rows = 301278342
completed_tickers = 4824
missing_tickers = 0
```

Lectura correcta:

```text
preflight passed = artifacts/config/lineage listos para disenar y probar builder candidate
preflight passed != master_intraday_bar_table_v0_2 materializada
preflight passed != full universe state table
preflight passed != ML/RL/AlphaEvolve habilitado
```

## 12.2 Controlled Sample Materialization

Script:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/materialize_master_intraday_quote_guarded_candidate_sample.py
```

Manifest:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/master_intraday_quote_guarded_candidate_sample_v0_1/_master_intraday_bar_table_v0_2_candidate_quote_guarded_controlled_sample_manifest.json
```

Output controlado:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/master_intraday_quote_guarded_candidate_sample_v0_1/master_intraday_bar_table_v0_2_candidate_quote_guarded_controlled_sample/data.parquet
```

Resultado:

```text
status = controlled_sample_materialized_not_official
source_sample_rows = 30
raw_rows_found = 30
raw_rows_missing = 0
raw_ohlc_match_rows = 30
raw_ohlc_mismatch_rows = 0
quote_guarded_repair_applied_source_rows = 20
qg_ohlc_changed_source_rows = 20
output_rows = 60
price_view_counts = {1m_raw: 30, 1m_quote_guarded_raw: 30}
full_universe_claim_rows = 0
ml_candidate_rows = 0
rl_candidate_rows = 0
validator_status = passed
validator_hard_fail_count = 0
```

Lectura correcta:

```text
controlled sample passed = el loader overlay raw + quote-guarded funciona en muestra real
controlled sample passed != candidate table materializada en E-root
controlled sample passed != full universe
controlled sample passed != scanner/eventos 1m
controlled sample passed != ML/RL/AlphaEvolve
```

## 12.3 Scoped Candidate Materialization

Script:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/materialize_master_intraday_quote_guarded_candidate_scoped.py
```

Manifest:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/master_intraday_quote_guarded_candidate_scoped_v0_1/_master_intraday_bar_table_v0_2_candidate_quote_guarded_scoped_manifest.json
```

Output scoped:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/master_intraday_quote_guarded_candidate_scoped_v0_1/master_intraday_bar_table_v0_2_candidate_quote_guarded_scoped/data.parquet
```

Scope:

```text
AACT:2025-09
AAGR:2023-12
AAMC:2023-12
```

Resultado:

```text
status = scoped_candidate_materialized_not_official
scope_count = 3
source_raw_file_count = 3
source_repair_shard_count = 3
raw_rows = 10835
repair_manifest_rows_in_scope = 1106
raw_ohlc_match_rows = 10835
raw_ohlc_mismatch_rows = 0
quote_guarded_repair_applied_rows = 96
qg_ohlc_changed_rows = 96
manifest_qg_diff_not_applied_rows = 10
output_rows = 21670
price_view_counts = {1m_raw: 10835, 1m_quote_guarded_raw: 10835}
full_universe_claim_rows = 0
ml_candidate_rows = 0
rl_candidate_rows = 0
validator_status = passed
validator_hard_fail_count = 0
```

Lectura correcta:

```text
scoped candidate passed = raw mensual completo + repair shard completo funcionan para scope acotado
scoped candidate passed != target E-root materializado
scoped candidate passed != full universe
scoped candidate passed != scanner/eventos 1m
scoped candidate passed != ML/RL/AlphaEvolve
```

Regla de overlay confirmada:

```text
OHLC quote-guarded efectivo solo cambia si quote_guarded_repair_applied = true.
Las diferencias de o_qg/h_qg/l_qg/c_qg con repair_applied=false se registran
como manifest_qg_diff_not_applied_rows, no se aplican al precio efectivo.
```

## 12.4 E-root Scoped Candidate Materialization

Manifest E-root:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/_master_intraday_bar_table_v0_2_candidate_quote_guarded_manifest.json
```

Output E-root:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_2_candidate_quote_guarded/data.parquet
```

Scope:

```text
AACT:2025-09
AAGR:2023-12
AAMC:2023-12
```

Resultado:

```text
status = scoped_candidate_materialized_not_official
writes_e_root_target = true
official_dataset_created = false
full_universe_claim = false
raw_rows = 10835
repair_manifest_rows_in_scope = 1106
raw_ohlc_mismatch_rows = 0
quote_guarded_repair_applied_rows = 96
qg_ohlc_changed_rows = 96
manifest_qg_diff_not_applied_rows = 10
output_rows = 21670
price_view_counts = {1m_raw: 10835, 1m_quote_guarded_raw: 10835}
validator_status = passed
validator_hard_fail_count = 0
```

Lectura correcta:

```text
E-root scoped candidate exists = primera candidate institucional acotada escrita
E-root scoped candidate exists != official/promoted
E-root scoped candidate exists != full universe
E-root scoped candidate exists != scanner/eventos 1m
E-root scoped candidate exists != ML/RL/AlphaEvolve
```




## 13. Downstream Scanner Dependency

This quote-guarded route is also a prerequisite for the next institutional
intraday scanner candidate.

Current scanner replay:

```text
dataset_id: intraday_scanner_candidates_table_v0_1
source_price_view: raw ohlcv_1m
status: controlled_replay_candidate_not_official
```

Required successor:

```text
dataset_id: intraday_scanner_candidates_table_v0_2_quote_guarded_candidate
source_price_view: ohlcv_1m_quote_guarded
storage_model: raw ohlcv_1m + repair_manifest_lt1b_v0_1.parquet overlay
```

The scanner must not promote a raw-only 20-year candidate as canonical because
the promoted LT1B quote-guarded overlay is now the required successor input. A
raw-only scanner run may be useful as a diagnostic denominator, but it must carry
raw diagnostic scope and must not be used as the official in-play candidate
surface for ML/RL state preparation.

Required scanner behavior after this manifest exists:

```text
1. compute raw first-cross evidence;
2. apply quote-guarded overlay for the same ticker/session/range;
3. compute quote-guarded first-cross evidence;
4. select candidates from quote-guarded evidence when repair rows apply;
5. preserve rejected raw spikes with explicit quality state.
```

Minimum downstream fields:

```text
first_cross_price_source
raw_first_cross_price
qg_first_cross_price
raw_move_vs_prev_close_pct
qg_move_vs_prev_close_pct
quote_guarded_repair_applied_at_cross
repair_state_at_cross
repair_reason_at_cross
scanner_quality_state
```
