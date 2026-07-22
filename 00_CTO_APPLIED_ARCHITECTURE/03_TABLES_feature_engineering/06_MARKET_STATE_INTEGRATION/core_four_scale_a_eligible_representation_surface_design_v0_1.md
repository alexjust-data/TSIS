# Core Four Scale A Eligible Representation Surface Design v0.1

Status: `design_ready_with_restrictions_v0_1`
Date: `2026-07-22`
Scope: `design_only_no_construction_no_execution`
Eligible Surface: `core_four_scale_a_eligible_representation_surface_v0_1`
Eligibility Rule: `core_four_scale_a_eligibility_rule_v0_1`
Logical Profile: `core_four_market_state_profile_v0_1`

This document defines the governed eligible representation surface required to
remediate the Scale A sample cardinality blocker. It does not authorize source
surface expansion, eligible-pool construction, builder execution, integration,
materialization, parquet writing, production use, dataset promotion,
downstream consumption, full-history execution or full-universe execution.

---

## 1. Decision

```text
core_four_market_state_candidate_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_bounded_scaling_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_sample_preflight = BLOCKED_SAMPLE_CARDINALITY
experimental_core_four_market_state_scale_a_execution = BLOCKED_NOT_STARTED

core_four_scale_a_eligible_representation_surface_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

experimental_core_four_scale_a_eligible_representation_surface_authorization = NOT_OPEN_NEXT
experimental_core_four_scale_a_eligible_representation_surface_construction = NOT_AUTHORIZED
eligible_instrument_pool = NOT_CONSTRUCTED
scale_a_sample_preflight_rerun = NOT_AUTHORIZED

official_market_state = NOT_OPEN
production_builder = NOT_AUTHORIZED
state_consumption = NOT_AUTHORIZED
downstream_consumption = NOT_AUTHORIZED
dataset_promotion = NOT_AUTHORIZED
full_history_execution = NOT_AUTHORIZED
full_universe_execution = NOT_AUTHORIZED
```

The design closes because the project now has an explicit scientific and
architectural definition of the eligible surface needed before Scale A can
freeze a valid 60-context sample.

---

## 2. Problem Reference

Accepted blocked preflight run:

```text
experimental_core_four_market_state_scale_a_sample_preflight_v0_1_20260722T123859Z
```

Observed blocker:

```text
required_instruments = 8
available_intraday_tickers = 3
eligible_instruments = 1
requested_contexts = 60
sample_manifest_rows = 0
hard_preflight_failures = 1
blocker = BLOCKED_SAMPLE_CARDINALITY
```

The blocker is not a builder, integration, materialization or parquet failure.
It is a mismatch between the authorized Scale A experimental question and the
currently eligible source surface.

Scale A is intended to validate:

```text
grain
identity
lineage
schema stability
deterministic rebuild
```

across multiple instruments and contexts. The current surface cannot answer
that question because it exposes too few eligible instrument identities.

---

## 3. Governing Concept

The eligible representation surface answers this question:

```text
Which instrument/session candidates are eligible to participate in this
specific core-four Scale A experiment under the active authority boundaries?
```

It does not answer:

```text
Which tickers exist?
Which data files exist?
Which universe is investable?
Which instruments should be traded?
Which instruments belong in production?
```

Eligibility is gate-specific. This design defines:

```text
eligible_surface_id = core_four_scale_a_eligible_representation_surface_v0_1
eligibility_rule_id = core_four_scale_a_eligibility_rule_v0_1
```

Future experiments may reuse the pattern, but must declare their own surface
or explicitly inherit this one.

---

## 4. Authority Boundary

This design allows only documentation and contract definition.

It does not authorize:

```text
014 source surface expansion
eligible pool construction
Scale A sample manifest generation
Information Object builder execution
Market State integration execution
Market State materialization execution
candidate parquet writing
official 016 Market State table creation
production builder development
downstream ML/RL/Event Research consumption
dataset promotion
full-history execution
full-universe execution
quote-dependent object integration
```

The next gate must be an authorization, not construction:

```text
experimental_core_four_scale_a_eligible_representation_surface_authorization_v0_1
```

---

## 5. Eligibility Definition

An instrument is eligible only if the future construction run can prove all of
the following without executing core-four formulas.

```text
identity_resolvable = true
daily_linkage_available = true
intraday_linkage_available = true
calendar_guard_compatible = true
required_core_four_input_coverage_present = true
excluded_context_class = false
```

Eligibility is based on distinct instrument identity, not ticker string alone.
If the intraday source lacks a trusted `instrument_id`, ticker/session linkage
must reconcile to the daily identity under an explicit restricted identity
policy.

Required evidence for each eligible instrument:

```text
instrument_id
ticker
identity_source_alias
identity_policy_id
eligible_session_count
calendar_compatible_session_count
daily_linked_session_count
intraday_linked_session_count
prior_20_daily_volume_coverage_status
required_core_four_input_coverage_status
rejection_reasons = []
```

The future construction may check that source fields required by the core-four
objects are present. It must not calculate object values, run formulas,
integrate State or infer success from resolved Information Object outputs.

---

## 6. Source Boundaries

The future authorization must explicitly declare allowed source aliases. The
expected aliases for eligibility construction are:

```text
004_master_daily_table
014_master_intraday_bar_table_candidate
```

Allowed use:

```text
identity and daily linkage checks
intraday availability checks
session coverage checks
required input-field coverage checks
row-count and byte-limit estimates
duplicate-risk classification for reporting
```

Forbidden use:

```text
013_ohlcv_1m_quote_guarded
015_microstructure_features_table_candidate
raw_quotes
quote-dependent objects
production State tables
official Market State tables
downstream feature stores
00_CTO/99_REFERENCE_LIBRARY
```

If the current `014_master_intraday_bar_table_candidate` surface is still too
small, a future authorization may define a bounded 014 candidate-surface
expansion. That expansion must be separately capped and reported. This design
does not authorize it.

---

## 7. Calendar Guard

Scale A remains non-calendar-aware validation. Therefore the eligible surface
must either use the fixed UTC compatibility guard or explicitly defer until a
governed calendar is available.

For this design, the allowed guard is:

```text
calendar_policy = fixed_utc_probe_calendar_compatibility_guarded
regular_open_utc = 13:30:00
regular_close_utc = 20:00:00
session_type = regular
early_close_indicator = false
holiday_or_closed_indicator = false
calendar_compatibility_failures_allowed = 0
```

The guard may select only sessions compatible with the fixed UTC probe window.
It must not claim calendar-aware validation and must not promote
`13:30-20:00 UTC` as a canonical US market session rule.

Scale B remains blocked until a governed exchange session calendar exists.

---

## 8. Pool Size And Caps

The future eligible surface construction should target a pool larger than the
Scale A sample requirement so that one later rejection does not immediately
block the sample.

```text
minimum_eligible_instrument_pool = 10
target_scale_a_sample_instruments = 8
maximum_eligible_instrument_pool = 20
target_scale_a_sample_sessions = 5
maximum_sessions_considered = 10
maximum_source_market_data_rows_read = 500000
full_history_execution = false
full_universe_execution = false
production_surface = false
```

The construction must preserve finite limits for instruments, sessions, rows,
files and bytes. It must not read or generate a full historical surface.

---

## 9. Selection Policy

The eligible pool must be policy-selected, not manually ticker-selected.

Candidate instruments should be ranked deterministically by:

```text
1. calendar-compatible session coverage
2. identity completeness
3. daily linkage completeness
4. intraday linkage completeness
5. prior-20 daily volume coverage
6. required core-four input-field coverage
7. duplicate-risk classification for reporting
8. source row economy
9. stable instrument_id and ticker tie-breakers
```

Manual allowlists or ticker picking are not valid unless a future
authorization explicitly declares them and explains why they are scientifically
necessary.

The ranking policy must be stable. Re-running construction against the same
authorized source snapshot should produce the same eligible pool and
fingerprint.

---

## 10. Required Future Outputs

A future construction gate should emit at least:

```text
pre_manifest.json
heartbeat.json
eligible_instrument_pool.json
eligible_instrument_pool_summary.json
eligible_instrument_pool_report.csv
eligible_instrument_rejection_report.csv
eligible_session_coverage_report.csv
eligible_surface_calendar_guard_report.csv
eligible_surface_source_coverage_report.csv
eligible_surface_duplicate_status_report.csv
eligible_surface_authority_report.json
eligible_surface_final_manifest.json
readout.md
```

The main pool artifact should contain one record per eligible instrument with
stable ordering and enough evidence for Scale A preflight to select exactly
eight instruments without rediscovering eligibility.

Required fingerprints:

```text
eligibility_rule_fingerprint
eligible_surface_fingerprint
eligible_instrument_pool_fingerprint
source_snapshot_fingerprint
```

---

## 11. Construction Acceptance Criteria

A future construction run may close successfully only if:

```text
eligible_instruments >= 10
eligible_instruments <= 20
sessions_considered <= 10
target_scale_a_sample_instruments = 8
target_scale_a_sample_sessions = 5
calendar_compatibility_failures = 0
identity_failures_for_eligible_instruments = 0
daily_linkage_failures_for_eligible_instruments = 0
intraday_linkage_failures_for_eligible_instruments = 0
required_core_four_input_coverage_failures_for_eligible_instruments = 0
forbidden_source_reads = 0
formula_executions = 0
builder_records_emitted = 0
integrated_candidate_records_emitted = 0
candidate_parquet_files_written = 0
official_outputs_written = 0
hard_authority_failures = 0
```

If `eligible_instruments < 10`, the run must close as a governed blocker and
must not fabricate a partial pool.

---

## 12. Relationship To Scale A Preflight

The Scale A sample preflight remains blocked until the eligible representation
surface has been authorized, constructed and validated.

Required sequence:

```text
core_four_scale_a_eligible_representation_surface_design
    CLOSED_DESIGN_READY_WITH_RESTRICTIONS

experimental_core_four_scale_a_eligible_representation_surface_authorization
    AUTHORIZED_WITH_RESTRICTIONS

experimental_core_four_scale_a_eligible_representation_surface_construction
    CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_a_sample_preflight
    rerun against eligible_instrument_pool_fingerprint

experimental_core_four_market_state_scale_a_execution
    only after preflight freezes a 60-context sample fingerprint
```

The preflight should consume the accepted `eligible_instrument_pool.json` and
prove that the frozen 60-context sample derives from the accepted pool
fingerprint. It must not rediscover or mutate the pool.

---

## 13. Preserved Restrictions

```text
candidate_artifacts_remain_non_canonical
candidate_artifacts_remain_not_downstream_consumable
core_four_profile_is_not_complete_tsis_market_state
quote_dependent_objects_remain_excluded
fixed_utc_probe_calendar_remains_restricted_non_calendar_aware_evidence
governed_exchange_session_calendar_required_before_scale_b
after_last_sampled_bar_is_not_end_of_session
rvol_semantic_naming_must_remain_explicit
duplicate_request_impact_must_not_be_confused_with_physical_duplicate_groups
```

---

## 14. Next Allowed Gate

```text
experimental_core_four_scale_a_eligible_representation_surface_authorization_v0_1
```

The next gate may authorize only bounded eligible-surface construction and
validation. It must keep Scale A builder execution, integration,
materialization, candidate parquet writing, official Market State, production,
downstream consumption, full-history/full-universe execution and promotion
closed.
