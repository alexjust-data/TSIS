# Event State Bounded Execution Chain Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_NOT_EXECUTED`
Date: `2026-07-24`
Scope: `session_opened_core_four_bounded_execution_chain_v0_1`

## 1. Authorization

This gate authorizes a future bounded execution-chain run for the first Event
State path:

```text
event_type_id = event_type:market_data:session_opened
event_subject_scope = exchange_session
event_state_profile_id = event_state_core_four_intraday_profile_v0_1
source_market_state_profile_id = market_state_core_four_intraday_profile_v0_1
```

This document does not execute the chain. It freezes the exact bounded scope
and the physical evidence source that a later execution may consume.

## 2. Prior Gate Authority

The authorization consumes:

```text
event_state_execution_chain_joint_review_readout_v0_1.md
event_state_execution_chain_joint_review_matrix_v0_1.json
```

Accepted review decision:

```text
CLOSED_APPROVED_FOR_BOUNDED_EXECUTION_AUTHORIZATION_WITH_RESTRICTIONS_NO_EXECUTION
blocking_design_findings = 0
```

## 3. Bounded Scope

Authorized exchange:

```text
exchange_id = XNYS
calendar_version = governed_exchange_session_calendar_xnys_v0_1
```

Authorized sessions:

```text
2021-01-19  # winter regular, standard time
2021-03-15  # US DST transition neighborhood
2022-11-25  # early close
```

Authorized instruments:

```text
AAME | figi_share_class:BBG001S5N8T1
ABEO | figi_share_class:BBG001S8T7K0
ABUS | figi_share_class:BBG001S6RSK0
```

Maximum authorized instrument-session contexts:

```text
3 instruments * 3 sessions = 9
```

This is a structural execution test, not a research sample and not a
performance study.

## 4. Market State Evidence Source

Future execution may read only this bounded non-official Market State physical
evidence:

```text
source_kind = candidate_market_state_physical_evidence
source_status = non_official_candidate_reference_only
source_profile_id = market_state_core_four_intraday_profile_v0_1
source_materialization_run_id = experimental_scale_c_ms_candidate_materialization_v0_1_20260723T184752Z
source_physical_validation_run_id = core_four_market_state_scale_c_candidate_physical_validation_v0_1_20260723T184900Z
candidate_parquet_relative_path = ../06_MARKET_STATE_INTEGRATION/runs/experimental_scale_c_ms_candidate_materialization_v0_1_20260723T184752Z/core_four_market_state_scale_c_candidate_v0_1.parquet
candidate_parquet_rows = 104
candidate_parquet_sha256 = b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2
```

This authorization does not promote that parquet and does not make it an
official Event State or Market State dataset.

## 5. Market State Row Identity Policy

Future execution must not treat Market State row id and content fingerprint as
interchangeable alternatives.

Policy:

```text
market_state_candidate_row_identity_field = materialized_state_candidate_id
market_state_content_integrity_field = state_output_fingerprint
both_fields_required = true
exactly_one_market_state_binding_required = true
```

If a stable `materialized_state_candidate_id` is missing, duplicate or
ambiguous, the Event State row must be blocked. If the
`state_output_fingerprint` is missing or mismatched, the row must be blocked.

## 6. Event Window Definition

Authorized initial Event Window Definition:

```text
event_window_definition_id = event_window_definition:market_data:session_opened:at_open_v0_1
window_subject_scope = exchange_session
state_role = at_event
consumption_legality = decision_safe_only_if_market_state_cutoff_proves_as_of_legality
anchor = governed_session_open_utc
window_start = event_anchor_timestamp_utc
window_end = event_anchor_timestamp_utc
matching_policy = exact_event_anchor_to_market_state_decision_timestamp
```

If no Market State record exists exactly at the governed session open for the
projected instrument-session context, the binding must be blocked. No latest
prior fallback is authorized in v0.1.

## 7. Instrument Projection Authority

Future projection execution may use only:

```text
instrument_source_scope = selected Scale C sample instruments listed above
instrument_identity_source = 000_instrument_master Data Foundation restricted evidence or accepted Scale C sample manifest identity
allowed_projection_rows_max = 9
```

Execution must prove:

```text
instrument_id resolves exactly once
ticker resolves as-of the session date if used
instrument exchange is compatible with XNYS
instrument lifecycle permits session association
ambiguous or missing identity blocks the projection
```

Current listing metadata must not be used as a retroactive point-in-time truth.

## 8. Authorized Future Execution Actions

Within the exact bounded scope above, a later execution may:

```text
read governed calendar rows for the 3 authorized sessions
create session_opened Event Instances for the 3 authorized exchange sessions
create Event Window Bindings for the at_open window definition
create Instrument Session Projections for the 9 authorized instrument-session contexts
read only the authorized Scale C candidate Market State parquet
resolve exact-one Market State bindings
emit candidate Event State records
emit blocked-binding reports
emit validation reports
write controlled candidate outputs under a run-local folder
```

## 9. Still Prohibited

Not authorized:

```text
new Event Types
halt_resumed
inferential detectors
window definitions other than at_open_v0_1
full Scale C Event State execution
full-history execution
full-universe execution
official Event State profile promotion
official Event State dataset promotion
production
downstream consumption
backtesting
ML/RL consumption
Execution State
Outcome labels
Strategy logic
```

## 10. Quantitative Limits

```text
max_exchange_sessions = 3
max_instruments = 3
max_instrument_session_projections = 9
max_event_instances = 3
max_event_window_bindings = 3
max_market_state_rows_consumed = 9
max_event_state_candidate_records = 9
max_event_state_parquet_files = 1
max_output_files = 16
max_output_bytes = 5000000
```

## 11. Required Future Execution Outputs

If executed later, the run must produce:

```text
pre_manifest.json
heartbeat.json
event_instance_report.csv
event_window_binding_report.csv
instrument_session_projection_report.csv
market_state_binding_report.csv
event_state_candidate_records.jsonl
event_state_candidate_manifest.json
event_state_validation_report.json
determinism_report.json
final_manifest.json
event_state_bounded_execution_chain_readout_v0_1.md
```

## 12. Next Gate

The next gate, only if explicitly executed, is:

```text
event_state_bounded_execution_chain_execution_v0_1
```

This authorization does not run that gate.
