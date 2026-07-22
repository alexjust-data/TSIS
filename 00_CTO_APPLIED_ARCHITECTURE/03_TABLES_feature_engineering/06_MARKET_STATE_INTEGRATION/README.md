# 06_MARKET_STATE_INTEGRATION

Status: `phase_b_core_four_scale_a_physical_validation_closed_v0_1`
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
Market State Integration Expansion = CORE_FOUR_SCALE_A_CLOSED_WITH_RESTRICTIONS
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
experimental_core_four_market_state_scale_a_sample_preflight = SUPERSEDED_BLOCKED_SAMPLE_CARDINALITY
core_four_scale_a_eligible_representation_surface_construction = CLOSED_PASS_WITH_RESTRICTIONS
eligible_instrument_pool = ACCEPTED
experimental_core_four_market_state_scale_a_sample_preflight_rerun_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_sample_preflight_rerun = CLOSED_PASS_WITH_RESTRICTIONS
scale_a_sample_manifest = FROZEN
experimental_core_four_market_state_scale_a_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_builder_resolution_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_candidate_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_candidate_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS
governed_exchange_session_calendar_design = NOT_OPEN_NEXT
experimental_core_four_market_state_scale_b_authorization = BLOCKED_UNTIL_GOVERNED_EXCHANGE_SESSION_CALENDAR
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
Scale A execution = PARTIAL_CHAIN_BUILDER_RESOLUTION_CLOSED
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
experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS
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
experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS
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
experimental_core_four_scale_a_eligible_representation_surface_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_scale_a_eligible_representation_surface_construction = CLOSED_PASS_WITH_RESTRICTIONS
eligible_instrument_pool = ACCEPTED
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

The design artifact itself remains non-executive. The follow-on
authorization below opens only bounded eligible-surface construction with a
run-local 014-derived candidate surface. It still does not authorize original
014 modification, sample preflight rerun, builders, integration, Market State
materialization, Market State parquet writing, production, promotion or
downstream consumption.

## Experimental Core Four Scale A Eligible Representation Surface Authorization

```text
authorization = experimental_core_four_scale_a_eligible_representation_surface_authorization_v0_1.md
scope = configs/experimental_core_four_scale_a_eligible_representation_surface_scope_v0_1.json
experimental_core_four_scale_a_eligible_representation_surface_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_scale_a_eligible_representation_surface_construction = CLOSED_PASS_WITH_RESTRICTIONS
eligible_instrument_pool = ACCEPTED
experimental_core_four_market_state_scale_a_sample_preflight_rerun_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_sample_preflight_rerun = CLOSED_PASS_WITH_RESTRICTIONS
scale_a_sample_manifest = FROZEN
experimental_core_four_market_state_scale_a_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_builder_resolution_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS
```

The authorization opens only bounded eligible-surface construction. It permits
a source snapshot, one bounded 014-derived intraday candidate surface inside
the construction run, and construction of a policy-selected pool of 10 to 20
eligible instrument identities.

Exact construction limits:

```text
maximum_candidate_instruments_discovered = 40
maximum_instruments_fully_evaluated = 40
minimum_eligible_instruments = 10
maximum_eligible_instruments = 20
maximum_sessions_considered = 10
minimum_eligible_sessions_per_instrument = 5
maximum_source_market_data_rows_read = 500000
maximum_expanded_intraday_rows_written = 200000
maximum_candidate_surface_files_written = 1
required_output_files = 17
maximum_output_files = 18
unexpected_output_files = 0
maximum_output_bytes = 50000000
```

The original `014_master_intraday_bar_table_candidate` must not be modified or
promoted. The preflight used the registry-resolved 014 `data.parquet` and
observed only 3 intraday tickers, so deriving from that file alone cannot create
10 eligible instruments. The construction may use `013_ohlcv_1m_quote_guarded`
only as bounded upstream evidence for a run-local 014-derived candidate surface,
with raw quotes and microstructure still forbidden.

Before writing `014_scale_a_eligible_surface_candidate_v0_1.parquet`, the
constructor must prove source expansion feasibility:

```text
resolved_intraday_source_distinct_instruments >= 10
candidate_instruments_with_daily_linkage >= 10
candidate_instruments_with_5_compatible_sessions >= 10
```

If that fails, construction must close `BLOCKED_SOURCE_CARDINALITY` and write
no derived parquet. The only parquet allowed by this authorization is the
run-local `014_scale_a_eligible_surface_candidate_v0_1.parquet`; no Market State
parquet is authorized.

## Experimental Core Four Scale A Eligible Representation Surface Construction

```text
script = scripts/experimental_core_four_scale_a_eligible_representation_surface_construction.py
reference_run = experimental_core_four_scale_a_eligible_representation_surface_construction_v0_1_20260722T184904Z
readout = experimental_core_four_scale_a_eligible_representation_surface_construction_readout_v0_1.md
experimental_core_four_scale_a_eligible_representation_surface_construction = CLOSED_PASS_WITH_RESTRICTIONS
eligible_instrument_pool = ACCEPTED
experimental_core_four_market_state_scale_a_sample_preflight_rerun_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_sample_preflight_rerun = CLOSED_PASS_WITH_RESTRICTIONS
scale_a_sample_manifest = FROZEN
experimental_core_four_market_state_scale_a_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_builder_resolution_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS
```

Result:

```text
candidate_instruments_discovered = 40
resolved_intraday_source_distinct_instruments = 40
candidate_instruments_with_daily_linkage = 14
candidate_instruments_with_5_compatible_sessions = 38
eligible_candidates_before_cap = 13
eligible_instruments_emitted = 13
selected_sessions_count = 10
source_market_data_rows_read = 221183
derived_014_rows_written = 91830
candidate_surface_parquet_files_written = 1
market_state_parquet_files_written = 0
required_output_files = 17
final_output_file_count = 17
unexpected_output_files = 0
authority_failures = 0
determinism_failures = 0
hard_contract_failures = 0
```

The run-local `014_scale_a_eligible_surface_candidate_v0_1.parquet` is eligible
surface evidence only. It is not Market State parquet and is not downstream
consumable. The original 014 candidate file remained unchanged by SHA-256 and
mtime.

Accepted pool fingerprint:

```text
eligible_instrument_pool_fingerprint =
57e22e7eb616c0682db1d094e19dff2b31e35ca23320ec1757acf4e19323853d
```

Superseded attempts `20260722T184113Z`, `20260722T184220Z` and
`20260722T184456Z` are not closure evidence; they exposed script/reporting
defects and are superseded by the accepted run above.

## Experimental Core Four Market State Scale A Sample Preflight Rerun

```text
authorization = experimental_core_four_market_state_scale_a_sample_preflight_rerun_authorization_v0_1.md
scope = configs/experimental_core_four_market_state_scale_a_sample_preflight_rerun_scope_v0_1.json
script = scripts/experimental_core_four_market_state_scale_a_sample_preflight.py
reference_run = experimental_core_four_market_state_scale_a_sample_preflight_rerun_v0_1_20260722T194905Z
readout = experimental_core_four_market_state_scale_a_sample_preflight_rerun_readout_v0_1.md
experimental_core_four_market_state_scale_a_sample_preflight_rerun = CLOSED_PASS_WITH_RESTRICTIONS
scale_a_sample_manifest = FROZEN
experimental_core_four_market_state_scale_a_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_builder_resolution_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS
```

Result:

```text
sample_manifest_rows = 60
selected_instruments = 8
selected_sessions = 5
eligible_instruments = 13
expected_resolution_records = 240
expected_blocked_contexts = 8
expected_integrable_contexts = 52
calendar_compatibility_failures = 0
identity_failures = 0
source_coverage_failures_in_frozen_sample = 0
stratification_failures = 0
duplicate_status_diversity_frozen_contexts = 5
hard_preflight_failures = 0
builders_executed = false
resolution_records_emitted = 0
integration_executed = false
materialization_executed = false
candidate_parquet_files_written = 0
```

Accepted sample fingerprint:

```text
scale_a_sample_fingerprint =
65a05b1c0637a7473380e9a04705a6c5879a921a0196dbad0a1815a19e8edea1
```

The superseded rerun `experimental_core_four_market_state_scale_a_sample_preflight_rerun_v0_1_20260722T194131Z` is not closure evidence. It exposed a
preflight defect where duplicate-status diversity could remain blocked while
the summary still closed PASS. The accepted run corrected that issue and froze
5 duplicate-evidence contexts against a requirement of 4.

## Experimental Core Four Market State Scale A Execution Authorization

```text
authorization = experimental_core_four_market_state_scale_a_execution_authorization_v0_1.md
scope = configs/experimental_core_four_market_state_scale_a_execution_scope_v0_1.json
experimental_core_four_market_state_scale_a_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_builder_resolution_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS
```

The authorization binds the next execution chain to the frozen sample:

```text
sample_preflight_rerun_run = experimental_core_four_market_state_scale_a_sample_preflight_rerun_v0_1_20260722T194905Z
scale_a_sample_fingerprint = 65a05b1c0637a7473380e9a04705a6c5879a921a0196dbad0a1815a19e8edea1
requested_contexts = 60
expected_resolution_records = 240
expected_integrable_contexts = 52
expected_blocked_contexts = 8
```

Authorized chain:

```text
builder/resolution
    -> integration
    -> candidate materialization
    -> independent physical validation
```

The first executable subgate,
`experimental_core_four_market_state_scale_a_builder_resolution_execution`,
closed `CLOSED_PASS_WITH_RESTRICTIONS` in accepted run
`experimental_core_four_market_state_scale_a_builder_resolution_execution_v0_1_20260722T202557Z`.
It consumed the frozen sample, emitted Information Object resolution records and did not integrate Market State.
It did not reselect the sample, read `013`, consume raw quotes, write official Market State, promote datasets or authorize downstream consumption.

## Experimental Core Four Market State Scale A Builder/Resolution Execution

```text
script = scripts/experimental_core_four_market_state_scale_a_builder_resolution_execution.py
reference_run = experimental_core_four_market_state_scale_a_builder_resolution_execution_v0_1_20260722T202557Z
readout = experimental_core_four_market_state_scale_a_builder_resolution_execution_readout_v0_1.md
experimental_core_four_market_state_scale_a_builder_resolution_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS
```

The run consumed frozen sample fingerprint `65a05b1c0637a7473380e9a04705a6c5879a921a0196dbad0a1815a19e8edea1` from `experimental_core_four_market_state_scale_a_sample_preflight_rerun_v0_1_20260722T194905Z` and emitted 240 Information Object resolution records:

```text
requested_contexts = 60
resolution_records = 240
pass_or_pass_with_restrictions_records = 208
blocked_input_unavailable_records = 32
integrable_contexts = 52
blocked_contexts = 8
failed_contexts = 0
source_market_data_rows_read = 5761
formula_rows = 1020
formula_failures = 0
future_bar_leaks = 0
output_contract_failures = 0
nondeterministic_records = 0
semantic_equality_failures = 0
hard_validation_failures = 0
```

Superseded attempts `experimental_core_four_market_state_scale_a_builder_resolution_execution_v0_1_20260722T202216Z`, `experimental_core_four_market_state_scale_a_builder_resolution_execution_v0_1_20260722T202243Z` and `experimental_core_four_market_state_scale_a_builder_resolution_execution_v0_1_20260722T202407Z` are not accepted closure evidence. They exposed wrapper/output-order and source-read-boundary reporting issues, not candidate-record formula defects.

## Experimental Core Four Market State Scale A Market State Integration Execution

```text
script = scripts/experimental_core_four_market_state_scale_a_market_state_integration_execution.py
reference_run = experimental_core_four_market_state_scale_a_market_state_integration_execution_v0_1_20260722T204126Z
readout = experimental_core_four_market_state_scale_a_market_state_integration_execution_readout_v0_1.md
experimental_core_four_market_state_scale_a_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_candidate_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS
```

Result:

```text
input_resolution_records = 240
contexts_seen = 60
candidate_records_emitted = 52
rejected_contexts = 8
rejected_required_object_blocked_contexts = 8
admitted_value_rows = 884
source_market_data_rows_read = 0
blocked_values_admitted = 0
future_bar_leaks = 0
hard_validation_failures = 0
candidate_parquet_files_written = 0
```

Superseded integration attempts `20260722T203507Z`, `20260722T203635Z` and `20260722T204045Z` are not accepted closure evidence for the Scale A chain. The accepted run is `experimental_core_four_market_state_scale_a_market_state_integration_execution_v0_1_20260722T204126Z` because it emits the materialization-compatible `integration_summary.json`.

## Experimental Core Four Market State Scale A Candidate Materialization Execution

```text
scope = configs/experimental_core_four_market_state_scale_a_candidate_materialization_scope_v0_1.json
script = scripts/core_four_market_state_materialization_probe.py
reference_run = experimental_scale_a_ms_candidate_materialization_v0_1_20260722T204356Z
readout = experimental_core_four_market_state_scale_a_candidate_materialization_execution_readout_v0_1.md
experimental_core_four_market_state_scale_a_candidate_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_candidate_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS
```

Result:

```text
input_candidate_records = 52
output_candidate_rows = 52
rejected_contexts_materialized_as_rows = 0
source_market_data_rows_read = 0
candidate_parquet_files_written = 1
candidate_parquet_bytes = 66399
physical_column_count = 40
physical_value_column_count = 17
schema_match = true
hard_validation_failures = 0
roundtrip_failures = 0
semantic_rebuild_differences = 0
```

The emitted `core_four_market_state_scale_a_candidate_v0_1.parquet` is bounded experimental candidate evidence only. It is not an official Market State table and is not downstream-consumable.

## Experimental Core Four Market State Scale A Candidate Physical Validation

```text
script = scripts/core_four_market_state_candidate_physical_validation.py
reference_run = experimental_core_four_market_state_scale_a_candidate_physical_validation_v0_1_20260722T204600Z
readout = experimental_core_four_market_state_scale_a_candidate_physical_validation_readout_v0_1.md
experimental_core_four_market_state_scale_a_candidate_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS
```

Result:

```text
input_candidate_records = 52
output_physical_rows = 52
candidate_parquet_files = 1
candidate_parquet_bytes = 66399
physical_column_count = 40
physical_value_column_count = 17
parquet_sha256_matches_manifest = true
schema_match = true
column_order_exact = true
value_mappings_checked = 884
source_to_physical_value_mismatches = 0
rvol_rename_checks = 52
rvol_rename_mismatches = 0
state_output_fingerprint_matches = 52
materialized_state_candidate_id_matches = 52
roundtrip_rows_checked = 52
roundtrip_field_mismatches = 0
semantic_rebuild_field_comparisons = 1924
semantic_rebuild_differences = 0
authority_failures = 0
hard_validation_failures = 0
```

The validator rebuilt expected rows independently from the accepted integration JSONL and the closed physical schema, then compared the real parquet artifact. It did not rewrite parquet and did not read source market data.

## Preserved Restrictions

```text
governed_exchange_session_calendar_required_before_operational_integration
after_last_sampled_bar_is_not_end_of_session
trading_activity_rvol_20d_name_must_preserve_volume_to_time_over_prior_full_session_mean_semantics
duplicate_counts_are_request_impact_not_physical_group_counts
quote_dependent_objects_remain_blocked
```

## Next Gate

Scale A is closed through independent candidate physical validation:

```text
experimental_core_four_market_state_scale_a_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS
scale_a_sample_fingerprint = 65a05b1c0637a7473380e9a04705a6c5879a921a0196dbad0a1815a19e8edea1
experimental_core_four_market_state_scale_a_builder_resolution_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_candidate_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_candidate_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS
```

The next allowed work is not Scale B execution. It should be a separately authorized design/review gate, most likely `governed_exchange_session_calendar_design`, because Scale B remains blocked until governed calendar evidence replaces the fixed UTC probe guard.

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
Scale B execution = BLOCKED_UNTIL_GOVERNED_EXCHANGE_SESSION_CALENDAR
Scale C execution = NOT_OPEN
```
