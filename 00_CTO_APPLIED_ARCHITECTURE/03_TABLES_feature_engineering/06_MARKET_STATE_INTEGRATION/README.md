# 06_MARKET_STATE_INTEGRATION

Status: `phase_b_core_four_scale_a_authorization_opened_v0_1`
Date: `2026-07-22`

Esta carpeta registra disenos y ejecuciones experimentales no productivas de
integracion de Information Objects admitidos en perfiles de `Market State`.

No es autoridad de produccion. No promociona schemas, builders,
materializaciones ni consumo downstream por si misma.

## Current Phase Boundary

```text
TSIS Market Ontology Phase = CLOSED
TSIS Market Ontology v1 = FROZEN
Phase B = OPEN
Market State Integration Expansion = CORE_FOUR_SCALE_A_AUTHORIZATION_BOUNDED
core_four_builder_validation = CLOSED_PASS_WITH_RESTRICTIONS
core_four_resolution_record_acceptance_review = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_integration_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
experimental_core_four_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_materialization_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
experimental_core_four_market_state_materialization_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_candidate_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_bounded_scaling_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_execution = NOT_EXECUTED
experimental_candidate_parquet_output_allowed = true
production_builder_authorized = false
state_consumption_authorized = false
official_physical_materialization_authorized = false
official_parquet_materialization_authorized = false
downstream_consumption_authorized = false
official_market_state_authorized = false
```

Regla:

```text
No integrar nuevos Objetos en Market State operativo hasta que exista
Operational Mapping gobernado, Builder Validation aprobada, aceptacion de
resolution records, integration execution experimental y autorizacion separada
de materializacion/promocion.
```

## Pilot Artifact

La integracion de `Trading Activity` se conserva como:

```text
market_state_integration_design
proof_of_process
not_operational_authority
```

No autoriza schemas, builders, materializaciones ni consumo downstream.

## Core Four Integration Design

```text
profile_id = market_state_core_four_intraday_experimental_v0_1
core_four_market_state_integration_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
```

Artefactos:

```text
core_four_market_state_integration_design_v0_1.md
core_four_market_state_integration_design_contract_v0_1.json
```

Reglas principales:

```text
join experimental = context_id
join semantico = instrument_id + ticker + session_date + decision_timestamp_utc + decision_case
request_id no es clave de join
object_atomicity = required
blocked object records = diagnostic_only_not_admitted
```

## Core Four Integration Execution

```text
execution_authorization = experimental_core_four_market_state_integration_execution_authorization_v0_1.md
execution_scope = configs/core_four_market_state_integration_execution_scope_v0_1.json
script = scripts/core_four_market_state_integration_probe.py
reference_run = experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z
experimental_core_four_market_state_integration_execution = PASS_WITH_RESTRICTIONS
```

Resultado:

```text
contexts_seen = 10
input_resolution_records = 40
candidate_records_emitted = 8
rejected_contexts = 2
rejected_required_object_blocked_contexts = 2
failed_context_consistency = 0
failed_contract_or_determinism = 0
future_bar_leaks = 0
blocked_values_admitted = 0
admitted_value_rows = 136
source_market_data_rows_read = 0
parquet_files_written = 0
```

Readout:

```text
experimental_core_four_market_state_integration_execution_readout_v0_1.md
```

Run artifacts:

```text
runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/
```

The emitted `market_state_candidate_records.jsonl` file is diagnostic and
non-canonical. It is not a Market State table.

## Core Four Materialization Design

```text
logical_profile_id = core_four_market_state_profile_v0_1
physical_schema_id = core_four_market_state_candidate_physical_schema_v0_1
core_four_market_state_materialization_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
candidate_records_accepted_for_materialization_design = true
experimental_core_four_market_state_materialization_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS
```

Artefactos:

```text
core_four_market_state_materialization_design_v0_1.md
core_four_market_state_materialization_design_contract_v0_1.json
```

El diseno separa el perfil logico core-four del schema fisico candidato y
clasifica las restricciones vivas por etapa: blockers de materializacion,
blockers de promocion, blockers de consumo operativo y restricciones
semanticas.

El diseno no ejecuto escrituras parquet. La autorizacion acotada posterior ya
existe y la ejecucion experimental ya cerro con restricciones sobre 8 records
candidatos. El parquet resultante sigue siendo candidato, no oficial y sin
consumo downstream.

## Core Four Materialization Authorization

```text
authorization = experimental_core_four_market_state_materialization_authorization_v0_1.md
scope = configs/experimental_core_four_market_state_materialization_scope_v0_1.json
experimental_core_four_market_state_materialization_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_candidate_parquet_output_allowed = true
candidate_parquet_filename = core_four_market_state_candidate_v0_1.parquet
schema_inference_from_sample = false
physical_value_columns_closed = true
json_field_serialization = canonical_utf8_json_string
state_output_fingerprint_payload = exact_non_circular
semantic_rebuild_determinism = required
byte_identical_parquet_rebuild = not_required
```

La autorizacion fijo la frontera de ejecucion. La ejecucion experimental
posterior consumio solo los 8 candidate JSONL records aceptados, genero un
unico parquet candidato no oficial y emitio evidencia de schema, grain,
lineage, restrictions, fingerprints, roundtrip y rebuild determinism.

## Core Four Materialization Execution

```text
script = scripts/core_four_market_state_materialization_probe.py
reference_run = experimental_core_four_market_state_materialization_v0_1_20260722T081155Z
readout = experimental_core_four_market_state_materialization_execution_readout_v0_1.md
experimental_core_four_market_state_materialization_execution = PASS_WITH_RESTRICTIONS
```

Resultado:

```text
input_candidate_records = 8
output_candidate_rows = 8
rejected_contexts_materialized_as_rows = 0
source_market_data_rows_read = 0
candidate_parquet_files_written = 1
candidate_parquet_bytes = 34097
physical_column_count = 40
physical_value_column_count = 17
schema_match = true
hard_validation_failures = 0
roundtrip_failures = 0
semantic_rebuild_differences = 0
semantic_rebuild_compare_field_count = 37
```

Run artifacts:

```text
runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/
```

The emitted `core_four_market_state_candidate_v0_1.parquet` file is bounded
experimental candidate evidence. It is not an official Market State table and
is not downstream-consumable.

## Core Four Candidate Physical Validation

```text
script = scripts/core_four_market_state_candidate_physical_validation.py
reference_run = core_four_market_state_candidate_physical_validation_v0_1_20260722T093828Z
readout = core_four_market_state_candidate_physical_validation_readout_v0_1.md
core_four_market_state_candidate_physical_validation = PASS_WITH_RESTRICTIONS
```

Result:

```text
input_candidate_records = 8
output_physical_rows = 8
candidate_parquet_files = 1
candidate_parquet_bytes = 34097
physical_column_count = 40
physical_value_column_count = 17
parquet_sha256_matches_manifest = true
parquet_bytes_match_manifest = true
schema_match = true
column_order_exact = true
timestamp_timezone_utc = true
value_mappings_checked = 136
source_to_physical_value_mismatches = 0
rvol_rename_passed = true
source_lineage_content_mismatches = 0
policy_version_mismatches = 0
formula_version_mismatches = 0
restriction_mismatches = 0
context_fingerprint_mismatches = 0
state_output_fingerprint_mismatches = 0
materialized_state_candidate_id_mismatches = 0
roundtrip_row_mismatches = 0
semantic_rebuild_differences = 0
authority_failures = 0
hard_validation_failures = 0
```

Run artifacts:

```text
runs/core_four_market_state_candidate_physical_validation_v0_1_20260722T093828Z/
```

The first validation attempt at `runs/core_four_market_state_candidate_physical_validation_v0_1_20260722T093513Z/` is superseded by the accepted run above. It failed because the validator checked non-existent candidate-record authority keys; it is not accepted closure evidence.

The candidate parquet is independently validated as a faithful bounded physical representation of the eight accepted candidate records. It remains non-official and not downstream-consumable.


## Core Four Bounded Scaling Design

```text
design = core_four_market_state_bounded_scaling_design_v0_1.md
contract = core_four_market_state_bounded_scaling_design_contract_v0_1.json
core_four_market_state_bounded_scaling_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
```

Purpose:

```text
Scale A = multi-context bounded validation
Scale B = multi-session calendar-aware validation
Scale C = multi-period historical bounded validation
```

The design does not authorize execution. It defines how to move beyond the eight-row proof without promoting the candidate parquet to official Market State.

Current boundaries after the follow-on Scale A authorization:

```text
Scale A authorization = AUTHORIZED_WITH_RESTRICTIONS
Scale A execution = NOT_EXECUTED
Scale B execution = BLOCKED_UNTIL_GOVERNED_EXCHANGE_SESSION_CALENDAR
Scale C execution = NOT_AUTHORIZED
official Market State = NOT_OPEN
production builder = NOT_AUTHORIZED
downstream consumption = NOT_AUTHORIZED
full-history execution = NOT_AUTHORIZED
full-universe execution = NOT_AUTHORIZED
```

Scale B requires a governed exchange session calendar before execution. The fixed UTC probe calendar remains acceptable only as restricted lineage for the original eight-row proof or explicitly bounded non-calendar-aware Scale A evidence.

## Experimental Core Four Scale A Authorization

```text
authorization = experimental_core_four_market_state_scale_a_authorization_v0_1.md
scope = configs/experimental_core_four_market_state_scale_a_scope_v0_1.json
experimental_core_four_market_state_scale_a_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_execution = NOT_EXECUTED
```

Exact limits:

```text
target_requested_contexts = 60
maximum_requested_contexts = 80
required_objects_per_context = 4
target_resolution_records = 240
maximum_resolution_records = 320
target_expected_blocked_contexts = 8
maximum_blocked_contexts = 16
target_integrated_candidate_records = 52
maximum_integrated_candidate_records = 80
maximum_physical_candidate_rows = 80
instrument_count = 8
session_count = 5
decision_case_family_count = 4
maximum_source_market_data_rows_read = 250000
maximum_candidate_parquet_files = 1
maximum_output_bytes = 5000000
```

Calendar guard:

```text
scale_a_calendar_policy = fixed_utc_probe_calendar_compatibility_guarded
scale_a_session_selection_excludes_calendar_mismatch_dates = true
regular_open_utc = 13:30:00
regular_close_utc = 20:00:00
session_type = regular
early_close_indicator = false
holiday_or_closed_indicator = false
calendar_compatibility_failures = 0 required
```

Scale A is authorized only as a bounded non-production execution. It remains not calendar-aware validation, not full-history, not full-universe and not downstream-consumable.


## Experimental Core Four Scale A Sample Preflight

```text
script = scripts/experimental_core_four_market_state_scale_a_sample_preflight.py
reference_run = experimental_core_four_market_state_scale_a_sample_preflight_v0_1_20260722T123859Z
superseded_runs = experimental_core_four_market_state_scale_a_sample_preflight_v0_1_20260722T123132Z, experimental_core_four_market_state_scale_a_sample_preflight_v0_1_20260722T123330Z
readout = experimental_core_four_market_state_scale_a_sample_preflight_readout_v0_1.md
experimental_core_four_market_state_scale_a_sample_preflight = BLOCKED_SAMPLE_CARDINALITY
experimental_core_four_market_state_scale_a_execution = BLOCKED_NOT_STARTED
```

Result:

```text
requested_contexts = 60
sample_manifest_rows = 0
required_instruments = 8
available_intraday_tickers = 3
eligible_instruments = 1
calendar_sessions_checked = 5
calendar_compatible_sessions = 5
calendar_compatibility_failures = 0
expected_resolution_records = 240
expected_blocked_contexts = 8
expected_integrable_contexts = 52
estimated_daily_rows = 588
estimated_intraday_rows = 21670
estimated_total_source_rows = 22258
maximum_source_market_data_rows_read = 250000
identity_failures = 0
hard_preflight_failures = 1
```

The preflight did not freeze the 60-context sample because the authorized 014 candidate source surface contains only 3 intraday tickers and only 1 eligible instrument under the fixed UTC Scale A calendar guard. No builders were executed, no Information Object resolution records were emitted, no Market State integration ran and no parquet was written.

The preflight attempts at `runs/experimental_core_four_market_state_scale_a_sample_preflight_v0_1_20260722T123132Z/` and `runs/experimental_core_four_market_state_scale_a_sample_preflight_v0_1_20260722T123330Z/` are superseded by the accepted run above. They reached the same cardinality blocker but are not accepted closure evidence because the first used a non-zero process exit for a governed blocked status and the second had an imprecise stratification finding.

## Core Four Scale A Eligible Representation Surface Design

```text
design = core_four_scale_a_eligible_representation_surface_design_v0_1.md
contract = core_four_scale_a_eligible_representation_surface_design_contract_v0_1.json
core_four_scale_a_eligible_representation_surface_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
experimental_core_four_scale_a_eligible_representation_surface_authorization = NOT_OPEN_NEXT
experimental_core_four_scale_a_eligible_representation_surface_construction = NOT_AUTHORIZED
eligible_instrument_pool = NOT_CONSTRUCTED
```

The blocked Scale A preflight revealed a missing governed layer: an eligible
representation surface for the experiment. The problem is not merely that more
tickers are needed; Scale A requires a minimum multi-instrument surface to test
grain, identity, lineage, schema stability and deterministic rebuild.

The design defines `core_four_scale_a_eligible_representation_surface_v0_1`
and `core_four_scale_a_eligibility_rule_v0_1`. A future construction run must
produce a policy-selected eligible pool, not a manually chosen ticker list.

Target future pool limits:

```text
minimum_eligible_instrument_pool = 10
target_scale_a_sample_instruments = 8
maximum_eligible_instrument_pool = 20
target_scale_a_sample_sessions = 5
maximum_sessions_considered = 10
maximum_source_market_data_rows_read = 500000
```

The design remains non-executive. It does not authorize 014 expansion,
eligible-pool construction, sample preflight rerun, builders, integration,
materialization, parquet writing, production, promotion or downstream
consumption.

## Preserved Restrictions

```text
governed_exchange_session_calendar_required_before_operational_integration
after_last_sampled_bar_is_not_end_of_session
trading_activity_rvol_20d_name_must_preserve_volume_to_time_over_prior_full_session_mean_semantics
duplicate_counts_are_request_impact_not_physical_group_counts
quote_dependent_objects_remain_blocked
```

## Next Gate

Scale A authorization remains open with restrictions, but the sample preflight is blocked until an eligible representation surface is authorized, constructed and accepted:

```text
core_four_scale_a_eligible_representation_surface_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
experimental_core_four_scale_a_eligible_representation_surface_authorization = NOT_OPEN_NEXT
experimental_core_four_scale_a_eligible_representation_surface_construction = NOT_AUTHORIZED
eligible_instrument_pool = NOT_CONSTRUCTED
experimental_core_four_market_state_scale_a_sample_preflight = BLOCKED_SAMPLE_CARDINALITY
experimental_core_four_market_state_scale_a_execution = BLOCKED_NOT_STARTED
```

The next allowed work is `experimental_core_four_scale_a_eligible_representation_surface_authorization_v0_1`. Do not construct the pool, expand 014, rerun the Scale A sample preflight, start builders, run integration, materialize parquet or open physical validation until that authorization exists.

Still closed:

```text
official Market State parquet materialization = NOT_AUTHORIZED
production builder = NOT_AUTHORIZED
state consumption = NOT_AUTHORIZED
downstream ML/RL consumption = NOT_AUTHORIZED
full-history execution = NOT_AUTHORIZED
full-universe execution = NOT_AUTHORIZED
quote-dependent object integration = NOT_AUTHORIZED
official Market State = NOT_OPEN
operational promotion = NOT_AUTHORIZED
```
