# Experimental Core Four Market State Materialization Authorization v0.1

Status: `authorized_for_bounded_candidate_materialization_execution_v0_1`
Date: `2026-07-22`
Scope: `eight_accepted_core_four_candidate_records_only`

This authorization opens a future bounded execution gate for converting the
eight accepted core-four Market State candidate JSONL records into one
experimental candidate parquet artifact.

It does not execute a materializer, write parquet now, authorize production,
create an official Market State table, authorize downstream State consumption,
read source market data, run full history or promote any dataset.

---

## 1. Authorized Gate

```text
gate = experimental_core_four_market_state_materialization_execution
authorization = experimental_core_four_market_state_materialization_authorization_v0_1
scope = configs/experimental_core_four_market_state_materialization_scope_v0_1.json
design = core_four_market_state_materialization_design_v0_1
design_contract = core_four_market_state_materialization_design_contract_v0_1
logical_profile_id = core_four_market_state_profile_v0_1
physical_schema_id = core_four_market_state_candidate_physical_schema_v0_1
source_integration_run_id = experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z
```

The only purpose of the future execution is to test whether the accepted
candidate records can be represented as a deterministic physical candidate
artifact with closed schema, preserved lineage and reversible roundtrip.

---

## 2. Allowed Inputs

Allowed input root:

```text
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/
```

Allowed input artifacts:

```text
market_state_candidate_records.jsonl
integration_context_report.csv
integration_value_manifest.csv
rejected_context_report.csv
core_four_market_state_integration_execution_summary.json
final_manifest.json
```

No physical market-data source root is authorized.

Forbidden inputs:

```text
004_master_daily_table
014_master_intraday_bar_table_candidate
raw_quotes
full-history market data
full-universe market data
production State tables
downstream feature stores
```

---

## 3. Authority

```text
experimental_core_four_market_state_materialization_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_materialization_execution = NOT_EXECUTED
experimental_candidate_parquet_output_allowed = true
candidate_parquet_filename = core_four_market_state_candidate_v0_1.parquet

source_market_data_reread_allowed = false
filesystem_market_data_reads_allowed = false
full_history_execution_allowed = false
full_universe_execution_allowed = false
production_builder_allowed = false
state_consumption_allowed = false
downstream_consumption_allowed = false
dataset_promotion_allowed = false
official_market_state_allowed = false
official_state_table_write_allowed = false
```

This authority is limited to one future bounded experimental candidate
materialization run. It does not authorize official Market State parquet
materialization.

---

## 4. Execution Limits

```text
maximum_input_candidate_records = 8
maximum_output_candidate_rows = 8
maximum_input_rejected_context_records = 2
maximum_source_market_data_rows_read = 0
maximum_candidate_parquet_files = 1
maximum_output_bytes = 1000000
output_root = 06_MARKET_STATE_INTEGRATION/runs/<materialization_run_id>/
```

The future materializer must fail if any limit is exceeded.

---

## 5. Closed Physical Schema

Schema inference from the eight candidate records is not allowed.

```text
schema_first_records_second = true
schema_inference_from_sample = false
physical_value_columns_closed = true
physical_column_count = 40
physical_value_column_count = 17
json_field_serialization = canonical_utf8_json_string
json_keys = sorted
json_whitespace = none
```

Required primary key:

```text
instrument_id
+ decision_timestamp_utc
+ state_profile_id
+ state_schema_version
```

The future materializer must write exactly the closed column set declared in the
scope JSON. Any missing column, extra column or type mismatch is a contract
failure.

### Value Columns

| Physical column | Source value field | Type | Nullable | Formula ID |
| --- | --- | --- | --- | --- |
| `price_location_structure__daily_open_price` | `price_location_structure__daily_open_price` | `float64` | `false` | `daily_open_price_after_session_open_v0_1` |
| `price_location_structure__daily_prior_close` | `price_location_structure__daily_prior_close` | `float64` | `false` | `daily_prior_close_value_v0_1` |
| `price_location_structure__intraday_bar_close_price` | `price_location_structure__intraday_bar_close_price` | `float64` | `false` | `selected_closed_bar_close_v0_1` |
| `price_location_structure__intraday_return_vs_prior_close_ratio_as_location` | `price_location_structure__intraday_return_vs_prior_close_ratio_as_location` | `float64` | `false` | `location_closed_bar_close_over_prior_close_minus_one_v0_1` |
| `price_location_structure__intraday_return_vs_session_open_ratio_as_location` | `price_location_structure__intraday_return_vs_session_open_ratio_as_location` | `float64` | `false` | `location_closed_bar_close_over_session_open_minus_one_v0_1` |
| `price_movement__daily_gap_pct` | `price_movement__daily_gap_pct` | `float64` | `false` | `daily_open_over_prior_close_minus_one_v0_1` |
| `price_movement__daily_prior_close` | `price_movement__daily_prior_close` | `float64` | `false` | `daily_prior_close_value_v0_1` |
| `price_movement__intraday_bar_close_price` | `price_movement__intraday_bar_close_price` | `float64` | `false` | `selected_closed_bar_close_v0_1` |
| `price_movement__intraday_return_vs_prior_close_ratio` | `price_movement__intraday_return_vs_prior_close_ratio` | `float64` | `false` | `closed_bar_close_over_prior_close_minus_one_v0_1` |
| `price_movement__intraday_return_vs_session_open_ratio` | `price_movement__intraday_return_vs_session_open_ratio` | `float64` | `false` | `closed_bar_close_over_session_open_minus_one_v0_1` |
| `trading_activity__session_volume_to_time_over_prior_20_full_session_volume_mean` | `trading_activity__daily_rvol_20d` | `float64` | `false` | `session_volume_to_time_over_prior_20_volume_mean_v0_1` |
| `trading_activity__daily_volume_20d_avg` | `trading_activity__daily_volume_20d_avg` | `float64` | `false` | `prior_20_session_volume_mean_v0_1` |
| `trading_activity__intraday_bar_volume` | `trading_activity__intraday_bar_volume` | `float64` | `false` | `selected_closed_bar_volume_v0_1` |
| `trading_activity__intraday_session_volume_to_time` | `trading_activity__intraday_session_volume_to_time` | `float64` | `false` | `closed_bar_session_volume_sum_v0_1` |
| `volatility_range_state__intraday_high_so_far` | `volatility_range_state__intraday_high_so_far` | `float64` | `false` | `closed_bar_high_so_far_max_v0_1` |
| `volatility_range_state__intraday_low_so_far` | `volatility_range_state__intraday_low_so_far` | `float64` | `false` | `closed_bar_low_so_far_min_v0_1` |
| `volatility_range_state__intraday_range_so_far_ratio` | `volatility_range_state__intraday_range_so_far_ratio` | `float64` | `false` | `high_so_far_over_low_so_far_minus_one_v0_1` |

`trading_activity__daily_rvol_20d` is not authorized as a physical output
column name. The future materializer must map it to:

```text
trading_activity__session_volume_to_time_over_prior_20_full_session_volume_mean
```

while preserving formula id:

```text
session_volume_to_time_over_prior_20_volume_mean_v0_1
```

---

## 6. Canonical JSON Field Rule

The following physical fields must be UTF-8 canonical JSON strings, not inferred
Arrow structs, maps or lists:

```text
source_lineage_json
policy_versions_json
formula_versions_json
restriction_codes_json
```

Serialization rule:

```text
sort_keys = true
separators = [",", ":"]
ensure_ascii = true
no insignificant whitespace
stable scalar normalization
```

This keeps fingerprints, roundtrip validation and deterministic rebuild simple
for the eight-row candidate proof.

Canonical derived field rules:

```text
policy_versions_json =
canonical JSON copied from accepted candidate record policy_versions

restriction_codes_json =
canonical JSON array from accepted restrictions,
sorted lexicographically and deduplicated
```

---

## 7. Fingerprint Payload And Rebuild Determinism

`state_output_fingerprint` must not hash the full 40-column physical row. The
payload is exact and non-circular:

```text
state_profile_id
state_schema_version
source_integration_profile_id
instrument_id
ticker
session_date
decision_timestamp_utc
decision_case
context_id
integration_status
object_completeness_status
quality_status
price_location_structure__daily_open_price
price_location_structure__daily_prior_close
price_location_structure__intraday_bar_close_price
price_location_structure__intraday_return_vs_prior_close_ratio_as_location
price_location_structure__intraday_return_vs_session_open_ratio_as_location
price_movement__daily_gap_pct
price_movement__daily_prior_close
price_movement__intraday_bar_close_price
price_movement__intraday_return_vs_prior_close_ratio
price_movement__intraday_return_vs_session_open_ratio
trading_activity__session_volume_to_time_over_prior_20_full_session_volume_mean
trading_activity__daily_volume_20d_avg
trading_activity__intraday_bar_volume
trading_activity__intraday_session_volume_to_time
volatility_range_state__intraday_high_so_far
volatility_range_state__intraday_low_so_far
volatility_range_state__intraday_range_so_far_ratio
calendar_version
source_lineage_json
policy_versions_json
formula_versions_json
restriction_codes_json
context_input_fingerprint
```

Excluded from `state_output_fingerprint`:

```text
materialized_state_candidate_id
materialization_run_id
state_output_fingerprint
physical_parquet_metadata
parquet_writer_version
parquet_encoding_metadata
```

Rule:

```text
state_output_fingerprint =
sha256(canonical_json(state_output_fingerprint_payload))

materialized_state_candidate_id =
sha256(
    state_profile_id,
    state_schema_version,
    instrument_id,
    decision_timestamp_utc,
    context_input_fingerprint,
    state_output_fingerprint
)
```

Rebuild determinism is semantic, not byte-identical parquet determinism.

Required semantic rebuild equality:

```text
same primary keys
same 17 physical value columns
same source_lineage_json
same policy_versions_json
same formula_versions_json
same restriction_codes_json
same context_input_fingerprint
same state_output_fingerprint
same materialized_state_candidate_id
```

Ignored across separate rebuild runs:

```text
materialization_run_id
physical parquet metadata
parquet writer version
parquet encoding metadata
file creation timestamp
```

Roundtrip validation is within a single execution and must compare rows before
parquet with rows read back from that same parquet, including that run's
`materialization_run_id`.

## 8. Required Future Outputs

A future execution may write only small run artifacts under its run directory:

```text
pre_manifest.json
heartbeat.json
core_four_market_state_candidate_v0_1.parquet
materialization_manifest.json
schema_report.json
grain_report.csv
lineage_report.json
restriction_report.csv
fingerprint_report.csv
roundtrip_report.csv
reconciliation_report.csv
rebuild_determinism_report.json
final_manifest.json
```

No output may be written to an official dataset root.

---

## 9. Required Validation In The Future Execution

The future execution must prove:

```text
input_candidate_records = 8
output_candidate_rows = 8
rejected_contexts_materialized_as_rows = 0
source_market_data_rows_read = 0
candidate_parquet_files_written = 1
0 duplicate primary keys
0 missing required columns
0 extra columns
0 namespace collisions
0 nulls in non-nullable columns
0 type coercion failures
0 lineage losses
0 restriction losses
0 fingerprint mismatches
JSONL-to-candidate-parquet roundtrip within one run = deterministic
semantic rebuild differences = 0
byte-identical parquet rebuild = not required
```

---

## 10. Non-Authority

This authorization does not open:

```text
production Market State Builder
official Market State table creation
016_market_state_table_v0_1
source market-data reread
full-history execution
full-universe execution
quote-dependent object integration
downstream ML/RL consumption
event detection consumption
backtest consumption
scanner consumption
operational promotion
dataset promotion
```

---

## 11. Next Gate

The next possible gate is:

```text
experimental_core_four_market_state_materialization_execution
```

That execution must use only:

```text
configs/experimental_core_four_market_state_materialization_scope_v0_1.json
```

and must close with a readout before any physical validation gate is opened.
