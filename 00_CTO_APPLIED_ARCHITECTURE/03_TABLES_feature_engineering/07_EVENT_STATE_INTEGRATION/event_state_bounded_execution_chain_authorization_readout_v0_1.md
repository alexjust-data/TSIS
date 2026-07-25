# Event State Bounded Execution Chain Authorization Readout v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_NOT_EXECUTED`
Date: `2026-07-24`
Authorization Run: `event_state_bounded_execution_chain_authorization_v0_1_20260724T153000Z`

## 1. Decision

```text
event_state_bounded_execution_chain_authorization = AUTHORIZED_WITH_RESTRICTIONS_NOT_EXECUTED
event_state_bounded_execution_chain_execution = NOT_EXECUTED
```

This gate freezes the first bounded Event State execution scope. It does not
run the execution chain.

## 2. Frozen Scope

```text
event_type_id = event_type:market_data:session_opened
event_subject_scope = exchange_session
exchange_id = XNYS
sessions = 3
instruments = 3
max_instrument_session_contexts = 9
```

Authorized sessions:

```text
2021-01-19
2021-03-15
2022-11-25
```

Authorized instruments:

```text
AAME | figi_share_class:BBG001S5N8T1
ABEO | figi_share_class:BBG001S8T7K0
ABUS | figi_share_class:BBG001S6RSK0
```

## 3. Market State Physical Source

```text
source_status = non_official_candidate_reference_only
candidate_materialization_run_id = experimental_scale_c_ms_candidate_materialization_v0_1_20260723T184752Z
candidate_physical_validation_run_id = core_four_market_state_scale_c_candidate_physical_validation_v0_1_20260723T184900Z
candidate_parquet_rows = 104
candidate_parquet_sha256 = b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2
```

This is the only physical Market State source authorized for the future bounded
run. It is not promoted and not downstream-consumable.

## 4. Binding Policy

```text
market_state_candidate_row_identity_field = materialized_state_candidate_id
market_state_content_integrity_field = state_output_fingerprint
both_fields_required = true
fingerprint_only_identity_allowed = false
exact_event_anchor_to_market_state_decision_timestamp = true
latest_prior_fallback_allowed = false
```

## 5. Still Closed

```text
event_state_records_emitted = 0
event_state_parquet_files_written = 0
official_event_state_profile_promotion = false
official_event_state_dataset_promotion = false
production = false
downstream_consumption = false
backtesting = false
ML_RL_consumption = false
```

## 6. Next Gate

The next gate, only if explicitly executed, is:

```text
event_state_bounded_execution_chain_execution_v0_1
```
