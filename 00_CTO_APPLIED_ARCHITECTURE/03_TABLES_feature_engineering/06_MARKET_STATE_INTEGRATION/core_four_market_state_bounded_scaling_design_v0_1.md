# Core Four Market State Bounded Scaling Design v0.1

Status: `design_ready_with_restrictions_v0_1`
Date: `2026-07-22`
Scope: `design_only_no_execution`
Logical Profile: `core_four_market_state_profile_v0_1`
Physical Schema: `core_four_market_state_candidate_physical_schema_v0_1`

This document defines the next bounded scaling path after the first complete
vertical core-four Market State candidate chain was physically validated.

It does not authorize builder execution, integration execution, parquet
writing, production builders, State consumption, dataset promotion,
downstream use, full-history execution or full-universe execution.

---

## 1. Decision

```text
core_four_builder_validation = CLOSED_PASS_WITH_RESTRICTIONS
core_four_resolution_record_acceptance_review = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_integration_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
experimental_core_four_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_materialization_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
experimental_core_four_market_state_materialization_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_candidate_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS

core_four_market_state_bounded_scaling_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

bounded_scale_a_authorization = NOT_OPEN
bounded_scale_a_execution = NOT_AUTHORIZED
bounded_scale_b_authorization = NOT_OPEN
bounded_scale_b_execution = NOT_AUTHORIZED
bounded_scale_c_authorization = NOT_OPEN
bounded_scale_c_execution = NOT_AUTHORIZED

official_market_state = NOT_OPEN
production_builder = NOT_AUTHORIZED
state_consumption = NOT_AUTHORIZED
downstream_consumption = NOT_AUTHORIZED
dataset_promotion = NOT_AUTHORIZED
full_history_execution = NOT_AUTHORIZED
full_universe_execution = NOT_AUTHORIZED
```

The design gate closes because the staged scaling path, sample boundaries,
calendar requirements, authority restrictions and validation criteria are now
explicit.

---

## 2. Reference Evidence

The validated vertical chain is:

```text
40 accepted core-four resolution records
    -> 8 integrated Market State candidate records
    -> 8 physical candidate rows
    -> 1 bounded experimental parquet
    -> independent physical validation
```

Accepted physical validation run:

```text
core_four_market_state_candidate_physical_validation_v0_1_20260722T093828Z
```

Reference source runs:

```text
integration_run =
experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z

materialization_run =
experimental_core_four_market_state_materialization_v0_1_20260722T081155Z
```

Validated facts:

```text
input_candidate_records = 8
output_physical_rows = 8
physical_column_count = 40
physical_value_column_count = 17
value_mappings_checked = 136
source_to_physical_value_mismatches = 0
rvol_rename_passed = true
state_output_fingerprint_mismatches = 0
materialized_state_candidate_id_mismatches = 0
semantic_rebuild_differences = 0
hard_validation_failures = 0
```

The superseded validation attempt:

```text
core_four_market_state_candidate_physical_validation_v0_1_20260722T093513Z
```

is not closure evidence. It is superseded by the accepted run above because its
validator contract was too strict for candidate-record authority keys. It is
not evidence of a candidate parquet defect.

---

## 3. Scaling Objective

The next question is not whether one parquet can be written correctly. That is
already proven for the bounded eight-row sample.

The next question is:

```text
Can the same core-four architecture remain correct across more contexts,
sessions, calendar regimes and historical periods without acquiring production
or official Market State authority?
```

This design separates that question into three bounded stages:

```text
Scale A = multi-context bounded validation
Scale B = multi-session calendar-aware validation
Scale C = multi-period historical bounded validation
```

The stages must not be collapsed into one execution.

---

## 4. Non-Goals

This design does not open:

```text
full-universe execution
full-history execution
2005-2026 materialization
official 016 Market State table
downstream ML/RL/Event Research consumption
production State Builder
schema promotion
core-four promotion to complete TSIS Market State
quote-dependent object integration
microstructure object integration
```

The core-four profile remains:

```text
experimental core-four Market State candidate profile
not complete TSIS Market State
not official production State
```

---

## 5. Stage Model

### Scale A - Multi-Context Bounded

Purpose:

```text
validate grain, identity, lineage, schema stability and deterministic rebuild
across more instruments and decision timestamps
```

Allowed shape for a future authorization:

```text
stage_id = core_four_market_state_scale_a_multi_context_bounded
candidate_row_cap = 50 to 250 rows
instrument_cap = explicit finite list
session_cap = explicit finite list
decision_timestamp_cap = explicit finite list
source_market_data_read_cap = explicit finite number
output_parquet_cap = explicit finite number
official_output_root_allowed = false
downstream_consumption_allowed = false
```

Scale A may use the existing fixed UTC probe calendar only if the authorization
explicitly preserves the same restriction and does not present the result as
calendar-aware evidence.

Required acceptance questions:

```text
0 duplicate primary keys
0 duplicate source candidate record ids
0 duplicate materialized state candidate ids
0 context identity inconsistencies
0 rejected or blocked contexts materialized as rows
0 missing required core-four objects in emitted rows
0 source-to-physical value mismatches
0 lineage content mismatches
0 fingerprint mismatches
0 roundtrip mismatches
0 semantic rebuild differences
```

### Scale B - Multi-Session Calendar-Aware

Purpose:

```text
validate temporal legality, exchange session boundaries and decision-case
semantics across calendar regimes
```

Scale B is not authorized until a governed exchange session calendar is
available to the builder/integration path.

Minimum calendar contract:

```text
exchange
session_date
regular_open_utc
regular_close_utc
session_type
early_close_indicator
holiday_or_closed_indicator
calendar_version
DST_treatment
source_authority
```

Required sample coverage for a future authorization:

```text
winter regular sessions
summer regular sessions
US DST transition neighborhood
Europe/US DST desynchronization neighborhood when relevant
early close session if observable and in-scope
pre-bar contexts
regular intraday contexts
after_last_sampled_bar contexts explicitly not labeled as market close
```

Scale B must retire `fixed_utc_probe_calendar_v0_1` from the authoritative
temporal boundary for the scaled sample. It may preserve the old calendar only
as lineage for earlier probe evidence.

### Scale C - Multi-Period Historical Bounded

Purpose:

```text
validate schema drift, identity history, data coverage, formula stability and
historical reproducibility across a larger but still bounded period
```

Scale C is not full history. A future authorization must define:

```text
year or period cap
instrument cap
session cap
row cap
source market-data row-read cap
calendar version
identity-history version
corporate-action policy version
output byte cap
rebuild determinism requirement
```

Scale C should only open after Scale B has either closed or explicitly scoped
calendar limitations that do not affect the selected historical sample.

---

## 6. Calendar Governance Requirement

The fixed probe calendar:

```text
fixed_utc_probe_calendar_v0_1
```

was acceptable for the first eight-row vertical proof. It is not acceptable as
the long-term temporal authority for scaled calendar-aware validation.

Before Scale B execution, the project must provide or reference:

```text
governed_exchange_session_calendar
```

with versioned session open/close boundaries. The calendar version must be
embedded into:

```text
resolution records
integrated candidate records
physical candidate rows
lineage reports
validation manifests
```

No future scaled artifact may silently treat:

```text
13:30-20:00 UTC
```

as a universal US market session rule.

---

## 7. RVOL Semantics

The current physical column remains valid and versioned:

```text
trading_activity__session_volume_to_time_over_prior_20_full_session_volume_mean
```

It represents:

```text
session_volume_to_time / prior_20_full_session_volume_mean
```

It must not be renamed back to ambiguous `rvol_20d` in physical output.

If the project later needs an intraday time-adjusted RVOL, it must be added as
a distinct capability and formula, for example:

```text
session_volume_to_time / historical_mean_volume_to_same_time
```

That capability is not opened by this design.

---

## 8. Required Future Authorization Inputs

Any future Scale A/B/C authorization must define:

```text
stage_id
source builder scope
source integration profile
logical State profile
physical schema id
instrument selection rule
session selection rule
decision timestamp selection rule
maximum source rows read
maximum resolution records
maximum integrated candidate records
maximum physical candidate rows
maximum parquet files
maximum output bytes
allowed input artifacts
allowed output artifacts
calendar version
identity version
formula version policy
lineage policy
restriction policy
rebuild determinism policy
authority false flags
```

It must also declare:

```text
schema_inference_from_sample = false
object_atomicity = required
blocked_required_objects_admitted = false
partial_required_object_payloads_admitted = false
official_market_state_allowed = false
downstream_consumption_allowed = false
dataset_promotion_allowed = false
```

---

## 9. Required Future Output Evidence

Each future scaling execution must emit, at minimum:

```text
pre_manifest.json
heartbeat.json
builder_or_resolution_report
integration_report
candidate_record_manifest
materialization_manifest.json
schema_report.json
grain_report.csv
value_reconciliation_report.csv
lineage_content_report.json
restriction_report.csv
fingerprint_report.csv
roundtrip_report.csv
semantic_rebuild_report.json
calendar_report.json
authority_report.json
final_manifest.json
readout.md
```

If parquet is written, it must remain under an explicit experimental candidate
run path and must not be placed under an official State table path.

---

## 10. Acceptance Criteria For Each Stage

Each stage may close only if:

```text
input records = expected bounded count
emitted candidate rows <= authorized cap
physical rows = accepted integrated candidate records
rejected contexts materialized as rows = 0
blocked required object values admitted = 0
duplicate primary keys = 0
duplicate source candidate record ids = 0
duplicate materialized state candidate ids = 0
missing physical columns = 0
extra physical columns = 0
schema inference from sample = false
source-to-physical value mismatches = 0
lineage content mismatches = 0
restriction mismatches = 0
fingerprint mismatches = 0
roundtrip mismatches = 0
semantic rebuild differences = 0
authority failures = 0
```

Scale B and Scale C additionally require:

```text
calendar version present = true
calendar session boundary mismatches = 0
decision_case semantic mismatches = 0
after_last_sampled_bar_not_promoted_to_session_close = true
```

---

## 11. Preserved Restrictions

```text
candidate artifacts remain non-canonical
candidate artifacts remain not downstream-consumable
core-four profile is not complete TSIS Market State
quote-dependent objects remain excluded
fixed UTC probe calendar blocks calendar-aware scaling
after_last_sampled_bar is not end_of_session
RVOL semantic naming must remain explicit
duplicate request impact must not be confused with physical duplicate groups
```

---

## 12. Next Allowed Gate

The next allowed gate is a separate authorization, not execution by implication:

```text
experimental_core_four_market_state_scale_a_authorization = NOT_OPEN_NEXT
```

That future authorization may only target:

```text
Scale A - multi-context bounded validation
```

unless a governed exchange session calendar is first designed and made
available for Scale B.

Still closed:

```text
official Market State
production builder
downstream State consumption
dataset promotion
full-history execution
full-universe execution
quote-dependent object integration
operational promotion
```
