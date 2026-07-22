# Core Four Market State Materialization Design v0.1

Status: `design_ready_with_restrictions_v0_1`
Date: `2026-07-22`
Scope: `design_only_no_execution`
Logical Profile: `core_four_market_state_profile_v0_1`
Physical Schema: `core_four_market_state_candidate_physical_schema_v0_1`

This document defines how the eight accepted core-four Market State candidate
records may later be converted into a bounded physical candidate artifact.

It does not authorize parquet writing, production builders, State consumption,
dataset promotion, downstream use, full-history execution or full-universe
execution.

---

## 1. Decision

```text
core_four_resolution_record_acceptance_review = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_integration_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
experimental_core_four_market_state_integration_execution = PASS_WITH_RESTRICTIONS
core_four_market_state_materialization_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

experimental_core_four_market_state_materialization_authorization = NOT_OPEN
experimental_core_four_market_state_materialization_execution = NOT_AUTHORIZED
market_state_parquet_materialization = NOT_AUTHORIZED
production_builder = NOT_AUTHORIZED
state_consumption = NOT_AUTHORIZED
downstream_consumption = NOT_AUTHORIZED
full_history_execution = NOT_AUTHORIZED
full_universe_execution = NOT_AUTHORIZED
official_market_state = NOT_OPEN
```

The design gate closes because the logical profile, physical candidate schema,
restriction classification, lineage/fingerprint requirements and next
authorization boundary are now explicit.

---

## 2. Materialization Input Boundary

The only allowed input evidence for a future bounded materialization
authorization is:

```text
source_integration_run_id =
experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z

source_profile_id =
market_state_core_four_intraday_experimental_v0_1

input_candidate_records_expected = 8
```

Allowed source artifacts from that run:

```text
market_state_candidate_records.jsonl
integration_context_report.csv
integration_value_manifest.csv
rejected_context_report.csv
core_four_market_state_integration_execution_summary.json
final_manifest.json
```

The eight `market_state_candidate_records.jsonl` records are accepted only as:

```text
accepted_inputs_for_materialization_design
non_canonical_market_state_candidate_records
bounded_experimental_evidence
```

They are not:

```text
official Market State
production State
downstream-consumable State
full-history evidence
full-universe evidence
```

A future materializer must not reread `004`, `014` or any other physical market
data source under this design. The future bounded materialization may only test
JSONL candidate-record to physical candidate artifact transformation.

---

## 3. Logical Profile Contract

```text
logical_profile_id = core_four_market_state_profile_v0_1
profile_family = experimental_market_state_candidate
profile_authority = non_canonical_bounded_phase_b_design
```

Required Information Objects:

```text
trading_activity
price_movement
price_location_structure
volatility_range_state
```

Excluded from this profile:

```text
liquidity
market_microstructure_state
order_flow_pressure
news_catalyst_context
fundamental_context
short_side_context
broad_market_context
halt_context
event_window_context
```

Completeness rule:

```text
exactly 4 required object payloads per emitted Market State candidate row
0 blocked required objects admitted
0 partial required-object payloads admitted
object_atomicity = required
context_completeness = required
```

The profile represents a bounded four-object intraday State profile. It does
not claim to be complete TSIS Market State v1.

---

## 4. Physical Candidate Schema Contract

```text
physical_schema_id = core_four_market_state_candidate_physical_schema_v0_1
physical_artifact_class = experimental_candidate
official_table_id = none
official_table_name = none
```

Recommended grain:

```text
instrument_id
+ decision_timestamp_utc
+ state_profile_id
+ state_schema_version
```

`context_id` must be preserved as lineage, but it should not become the
canonical primary identity of a future physical State row.

Ticker is allowed as a denormalized readability field only. It must not replace
`instrument_id` in the primary key.

Candidate physical row identity:

```text
materialized_state_candidate_id =
stable_hash(
    state_profile_id,
    state_schema_version,
    instrument_id,
    decision_timestamp_utc,
    context_input_fingerprint,
    state_output_fingerprint
)
```

Minimum required physical fields:

```text
materialized_state_candidate_id
state_profile_id
state_schema_version
materialization_run_id
source_integration_run_id
source_candidate_record_id

instrument_id
ticker
session_date
decision_timestamp_utc
decision_case
context_id

integration_status
object_completeness_status
quality_status

trading_activity__*
price_movement__*
price_location_structure__*
volatility_range_state__*

source_lineage_json
policy_versions_json
formula_versions_json
calendar_version
restriction_codes_json

context_input_fingerprint
state_output_fingerprint
```

Physical naming restriction:

```text
Do not name the output 016_market_state_table_v0_1.
Do not place the artifact under an official production State table path.
Use explicit experimental candidate naming.
```

Recommended bounded artifact name for a future authorization:

```text
core_four_market_state_candidate_v0_1.parquet
```

This name is a candidate artifact label, not an official TSIS Market State table
name.

---

## 5. Partitioning And Storage Boundary

For the eight-record experimental candidate materialization, partitioning is
not a performance requirement. If a future authorization writes parquet, the
design allows only simple, inspectable partitioning:

```text
state_profile_id
state_schema_version
session_date
```

Future larger runs may replace `session_date` with governed date hierarchy
partitions only after a separate scaling design.

Storage boundary for the next gate:

```text
output_root = 06_MARKET_STATE_INTEGRATION/runs/<materialization_run_id>/
official_dataset_root = NOT_AUTHORIZED
production_dataset_root = NOT_AUTHORIZED
```

---

## 6. Restriction Classification

| Restriction | Class | Materialization effect |
| --- | --- | --- |
| Fixed UTC session window in the core-four probe | `promotion_blocker` and `operational_consumption_blocker` | Does not block an eight-record candidate artifact if `calendar_version = fixed_utc_probe_calendar_v0_1` is explicit. |
| Missing governed exchange calendar | `promotion_blocker` | Must be resolved before historical scaling or operational use. |
| `after_last_sampled_bar` semantics | `semantic_restriction_only` unless mislabeled | May be materialized only as `after_last_sampled_bar`, never as market close or end-of-session State. |
| Current `rvol_20d` semantics | `materialization_blocker_if_ambiguous_name` | A physical field must preserve the exact formula or use a non-ambiguous semantic name. |
| Duplicate counts reported as request impact | `validation_requirement` and `promotion_blocker` | Does not block eight-record candidate materialization, but reports must distinguish physical duplicate groups from affected requests before scaling. |
| Quote-dependent objects blocked | `out_of_profile_hard_exclusion` | No quote-dependent object values may enter this profile. |
| Source market-data reread | `hard_execution_blocker` | A future bounded materializer must consume only accepted candidate records. |
| Downstream consumption | `hard_authority_blocker` | No downstream ML, RL, scanner, backtest or research consumption is authorized. |
| Official Market State naming | `hard_authority_blocker` | No official State table naming or promotion is authorized. |

---

## 7. Value Namespace Rules

Each value column must retain its owning object namespace:

```text
trading_activity__<capability_or_field>
price_movement__<capability_or_field>
price_location_structure__<capability_or_field>
volatility_range_state__<capability_or_field>
```

No un-namespaced output value columns are allowed in the candidate physical
schema.

Known semantic equality across namespaces must be preserved without merging:

```text
price_movement__return_vs_prior_close
=
price_location_structure__return_vs_prior_close

price_movement__return_vs_session_open
=
price_location_structure__return_vs_session_open
```

They may be numerically equal while remaining separate semantic fields.

---

## 8. Status And Nullability Rules

Allowed candidate row status:

```text
INTEGRABLE_COMPLETE_WITH_RESTRICTIONS
```

Rejected contexts from the integration run must not become physical candidate
rows. They may appear only in diagnostic reports.

Required identity/status fields are non-null:

```text
materialized_state_candidate_id
state_profile_id
state_schema_version
materialization_run_id
source_integration_run_id
instrument_id
session_date
decision_timestamp_utc
decision_case
integration_status
object_completeness_status
context_input_fingerprint
state_output_fingerprint
```

Value fields may be nullable only when the source candidate record explicitly
marks the capability as not applicable under the accepted profile. Required
capability values may not silently become null during materialization.

---

## 9. Lineage And Fingerprints

A future materializer must preserve:

```text
source integration run id
source candidate record id
context id
object ids
object record ids
source evidence lineage
cutoff evidence
quality evidence
policy versions
formula versions
restriction codes
```

Required fingerprints:

```text
context_input_fingerprint
state_output_fingerprint
materialized_state_candidate_id
```

`state_output_fingerprint` must be deterministic from:

```text
state_profile_id
state_schema_version
instrument_id
decision_timestamp_utc
context_input_fingerprint
admitted value payload hash
policy versions
formula versions
restriction codes
```

The later physical validation gate must prove:

```text
input candidate records = output physical rows
0 primary-key duplicates
0 lineage losses
0 restriction losses
0 fingerprint mismatches
JSONL-to-Parquet roundtrip = deterministic
rebuild run 1 fingerprint = rebuild run 2 fingerprint
```

---

## 10. Next Gate Required

The next gate is a separate authorization, not execution by implication:

```text
experimental_core_four_market_state_materialization_authorization_v0_1 = NOT_OPEN
```

That authorization must explicitly declare:

```text
input_run_id = experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z
input_candidate_records = 8
source_market_data_reread = false
max_output_records = 8
output_artifact_class = experimental_candidate_parquet
official_state_table = false
production_builder = false
downstream_consumption = false
dataset_promotion = false
full_history_execution = false
full_universe_execution = false
```

If runtime or filesystem scope crosses the thresholds in
`LONG_RUNNING_OPERATIONS_CONTRACT.md`, the future execution must create a
premanifest and heartbeat before starting.

---

## 11. Explicit Non-Authority

This document does not authorize:

```text
writing parquet
creating a physical Market State table
creating 016_market_state_table_v0_1
executing a materializer
reading source market data
running full-history or full-universe jobs
integrating quote-dependent objects
promoting a candidate dataset
feeding downstream ML/RL/Event Research/backtests/scanners
declaring official TSIS Market State
```

---

## 12. Evidence TSIS

Primary evidence:

```text
05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/experimental_core_four_resolution_record_acceptance_review_v0_1.md
05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/experimental_core_four_resolution_record_acceptance_summary_v0_1.json
06_MARKET_STATE_INTEGRATION/core_four_market_state_integration_design_v0_1.md
06_MARKET_STATE_INTEGRATION/core_four_market_state_integration_design_contract_v0_1.json
06_MARKET_STATE_INTEGRATION/experimental_core_four_market_state_integration_execution_authorization_v0_1.md
06_MARKET_STATE_INTEGRATION/experimental_core_four_market_state_integration_execution_readout_v0_1.md
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/final_manifest.json
```

Machine-readable contract:

```text
06_MARKET_STATE_INTEGRATION/core_four_market_state_materialization_design_contract_v0_1.json
```
