# Experimental Core Four Scale A Eligible Representation Surface Authorization v0.1

Status: `authorized_with_restrictions_v0_1`
Date: `2026-07-22`
Scope: `bounded_eligible_representation_surface_construction_only`
Design: `core_four_scale_a_eligible_representation_surface_design_v0_1`
Scope Contract: `configs/experimental_core_four_scale_a_eligible_representation_surface_scope_v0_1.json`

This authorization opens only the bounded construction of the eligible
representation surface required before Scale A sample preflight can be rerun.

It authorizes a source snapshot, a bounded 014-derived intraday candidate
surface inside the run, and construction of a policy-selected eligible
instrument pool. It does not authorize Scale A sample preflight rerun, builders,
Information Object resolution, Market State integration, Market State
materialization, Market State parquet, production, downstream consumption,
dataset promotion, full-history execution or full-universe execution.

---

## 1. Authorized Gate

```text
gate = experimental_core_four_scale_a_eligible_representation_surface_construction
authorization = experimental_core_four_scale_a_eligible_representation_surface_authorization_v0_1
scope = configs/experimental_core_four_scale_a_eligible_representation_surface_scope_v0_1.json
design = core_four_scale_a_eligible_representation_surface_design_v0_1
design_contract = core_four_scale_a_eligible_representation_surface_design_contract_v0_1
eligible_surface_id = core_four_scale_a_eligible_representation_surface_v0_1
eligibility_rule_id = core_four_scale_a_eligibility_rule_v0_1
logical_profile_id = core_four_market_state_profile_v0_1
scale_stage = core_four_market_state_scale_a_multi_context_bounded
```

The construction must resolve only this question:

```text
Which instrument/session candidates are eligible to participate in the
authorized core-four Scale A experiment?
```

It must not produce the Scale A sample itself.

---

## 2. Current Blocker

Accepted blocked preflight:

```text
experimental_core_four_market_state_scale_a_sample_preflight_v0_1_20260722T123859Z
```

Observed source surface:

```text
required_instruments = 8
available_intraday_tickers = 3
eligible_instruments = 1
sample_manifest_rows = 0
blocker = BLOCKED_SAMPLE_CARDINALITY
```

The authorization is issued because the experiment requires an eligible
multi-instrument representation surface. It is not issued to create a general
universe, production table or trading list.

---

## 3. Internal Phases

The future construction run is one gate with four explicit internal phases.

### Phase 0 - Authority And Source Expansion Feasibility

Before writing any derived intraday surface, the constructor must validate
scope authority, resolve source paths and prove source expansion feasibility:

```text
resolved_intraday_source_distinct_instruments >= 10
candidate_instruments_with_daily_linkage >= 10
candidate_instruments_with_5_compatible_sessions >= 10
```

If this threshold cannot be demonstrated, the run must close as:

```text
BLOCKED_SOURCE_CARDINALITY
```

and must not write:

```text
014_scale_a_eligible_surface_candidate_v0_1.parquet
```

The feasibility evidence must be recorded in `pre_manifest.json` and
`eligible_surface_source_snapshot_manifest.json`; no separate required output
file is introduced by this precheck.

### Phase 1 - Source Snapshot

Freeze the bounded input evidence:

```text
eligible_surface_source_snapshot_manifest.json
```

The snapshot must record:

```text
resolved source paths
file hashes
row counts
date boundaries
candidate instruments discovered
candidate sessions discovered
source_snapshot_fingerprint
```

### Phase 2 - Bounded 014-Derived Candidate Surface

Create a bounded intraday surface only inside the construction run:

```text
014_scale_a_eligible_surface_candidate_v0_1.parquet
bounded_014_expansion_manifest.json
```

The original 014 source remains unchanged:

```text
original_014_modified = false
original_014_overwritten = false
official_014_promotion = false
```

### Phase 3 - Eligible Instrument Pool

Construct the policy-selected pool:

```text
eligible_instrument_pool.json
```

The pool must contain at least 10 and at most 20 eligible instrument identities.
It must not be a manual ticker list.

---

## 4. Exact Limits

```text
maximum_candidate_instruments_discovered = 40
maximum_instruments_fully_evaluated = 40
minimum_eligible_instruments = 10
maximum_eligible_instruments = 20

maximum_sessions_considered = 10
target_scale_a_sample_sessions = 5
minimum_eligible_sessions_per_instrument = 5

maximum_source_market_data_rows_read = 500000
maximum_expanded_intraday_rows_written = 200000
maximum_candidate_surface_files_written = 1
required_output_files = 17
maximum_output_files = 18
unexpected_output_files = 0
optional_error_or_supersession_files_maximum = 1
maximum_output_bytes = 50000000
```

The construction must fail closed if any hard limit is exceeded.

The eligible pool size cap limits emitted eligible instruments, not all
candidate instruments discovered. The constructor may inspect up to 40
candidate identities to obtain a reproducible pool of 10 to 20 eligible
identities.

---

## 5. Allowed Inputs

Allowed source aliases:

```text
004_master_daily_table
014_master_intraday_bar_table_candidate
013_ohlcv_1m_quote_guarded
```

Alias authority:

```text
004_master_daily_table
    allowed for identity, daily linkage and prior-20 trading-session coverage

014_master_intraday_bar_table_candidate
    allowed as the current bounded intraday candidate surface

013_ohlcv_1m_quote_guarded
    allowed only as bounded upstream evidence for constructing the run-local
    014-derived candidate surface
```

`013_ohlcv_1m_quote_guarded` is not authorized as a Market State input, builder
input, integration input, downstream input or production source in this gate.
It may not be used to consume raw quotes, quote-dependent objects or
microstructure features.

Allowed governance references:

```text
core_four_scale_a_eligible_representation_surface_design_v0_1.md
core_four_scale_a_eligible_representation_surface_design_contract_v0_1.json
configs/experimental_core_four_scale_a_eligible_representation_surface_scope_v0_1.json
configs/experimental_core_four_market_state_scale_a_scope_v0_1.json
05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/configs/experimental_source_binding_registry_v0_1.json
05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/configs/experimental_column_binding_registry_v0_1.json
05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/policies/004_price_view_selection_policy_v0_1.md
05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/policies/014_duplicate_intraday_bar_policy_v0_1.md
```

The future constructor must resolve concrete physical source paths from the
authorized registries and write those paths into
`eligible_surface_source_snapshot_manifest.json`.

Authorized intraday expansion origin:

```text
previous_preflight_014_surface =
    G:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/
    master_intraday_bar_table_v0_2_candidate_quote_guarded/data.parquet

previous_preflight_observed_intraday_tickers = 3
current_014_derivation_alone_can_increase_instrument_cardinality = false

bounded_upstream_intraday_alias =
    013_ohlcv_1m_quote_guarded

bounded_upstream_intraday_candidate_root =
    C:/TSIS_Data/data/data_foundation_outputs/
    ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
```

New instruments may appear only from the bounded, registry-resolved 013
candidate root above, under this gate's row, instrument, session and byte caps.
If that root cannot be resolved or cannot demonstrate at least 10 potential
eligible instrument identities before writing the derived surface, the run must
close as `BLOCKED_SOURCE_CARDINALITY`.

Forbidden inputs:

```text
015_microstructure_features_table_candidate
raw_quotes
quote-dependent object records
production State tables
official Market State tables
downstream feature stores
full-history market data scans
full-universe market data scans
00_CTO/99_REFERENCE_LIBRARY
```

---

## 6. Authority

```text
experimental_core_four_scale_a_eligible_representation_surface_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_scale_a_eligible_representation_surface_construction = NOT_EXECUTED

source_snapshot_allowed = true
bounded_014_derived_candidate_surface_creation_allowed = true
eligible_pool_construction_allowed = true

original_014_modification_allowed = false
official_014_promotion_allowed = false
Scale_A_sample_preflight_rerun_allowed = false
Scale_A_builder_execution_allowed = false
Information_Object_resolution_allowed = false
Market_State_integration_allowed = false
Market_State_materialization_allowed = false
Market_State_candidate_parquet_allowed = false
official_Market_State_allowed = false
production_builder_allowed = false
state_consumption_allowed = false
downstream_consumption_allowed = false
dataset_promotion_allowed = false
full_history_execution_allowed = false
full_universe_execution_allowed = false
```

The only parquet permitted by this authorization is the bounded derived 014
candidate surface inside the eligible-surface construction run. No Market State
parquet is authorized.

---

## 7. Session Eligibility

An eligible session must satisfy all conditions:

```text
calendar_guard_compatible = true
daily_linked = true
intraday_linked = true
prior_20_daily_volume_coverage_available = true
required_core_four_source_fields_present = true
excluded_context_class = false
```

The fixed UTC guard requires:

```text
regular_open_utc = 13:30:00
regular_close_utc = 20:00:00
session_type = regular
early_close_indicator = false
holiday_or_closed_indicator = false
calendar_compatibility_failures = 0
```

An eligible instrument must have:

```text
eligible_session_count >= 5
```

The future Scale A sample may later select five sessions from the accepted
eligible pool. This construction gate must not freeze the 60-context sample.

---

## 8. Prior-20 Daily Volume Coverage

The constructor does not calculate RVOL. It may only verify that the required
input coverage exists.

For every eligible instrument/session:

```text
prior_20_daily_volume_coverage =
    20 distinct prior trading sessions
    strictly before session_date
    after authorized daily price-view selection
```

Forbidden coverage shortcuts:

```text
20 calendar days
including current session
including future sessions
counting duplicate daily rows as extra sessions
repairing missing daily volume
inferring volume from intraday rows
```

If the authorized daily policy cannot select one usable daily row per prior
session, that session is not eligible.

---

## 9. Required Source Fields

Required daily fields for eligibility checks:

```text
instrument_id
ticker
session_date
open
prior_close
volume
price_view
```

Required intraday fields for eligibility checks:

```text
ticker
session_date
bar_end_utc
open
high
low
close
volume
```

The constructor may check field presence and non-null coverage. It must not
derive Information Object values.

---

## 10. Ranking Rules

Ranking must be deterministic and quantitatively defined.

Sort eligible candidates by:

```text
1. calendar_compatible_session_coverage_count descending
2. identity_completeness_score descending
3. daily_linkage_completeness_ratio descending
4. intraday_linkage_completeness_ratio descending
5. prior_20_daily_volume_complete_session_count descending
6. required_field_coverage_ratio descending
7. duplicate_risk_rank ascending
8. source_rows_per_eligible_session ascending
9. instrument_id ascending
10. ticker ascending
```

Metric definitions:

```text
calendar_compatible_session_coverage_count =
    count of sessions satisfying fixed UTC guard

identity_completeness_score =
    1 if one eligible instrument_id is resolved, else 0

daily_linkage_completeness_ratio =
    daily linked sessions / sessions considered

intraday_linkage_completeness_ratio =
    intraday linked sessions / sessions considered

prior_20_daily_volume_complete_session_count =
    count of sessions with 20 distinct prior trading-session volumes

required_field_coverage_ratio =
    present required source cells / expected required source cells

duplicate_risk_rank =
    0 no known duplicate risk
    1 identical duplicate groups only
    2 conflicting duplicate groups

source_rows_per_eligible_session =
    source rows read or written / eligible_session_count
```

The constructor must report rejected candidates and rejection reasons. It must
not silently replace or hand-pick candidates after ranking.

---

## 11. Required Outputs

The construction run must emit:

```text
pre_manifest.json
heartbeat.json
eligible_surface_source_snapshot_manifest.json
014_scale_a_eligible_surface_candidate_v0_1.parquet
bounded_014_expansion_manifest.json
eligible_instrument_pool.json
eligible_instrument_pool_summary.json
eligible_instrument_pool_report.csv
eligible_instrument_rejection_report.csv
eligible_session_coverage_report.csv
eligible_surface_calendar_guard_report.csv
eligible_surface_source_coverage_report.csv
eligible_surface_duplicate_status_report.csv
eligible_surface_authority_report.json
eligible_surface_determinism_report.json
eligible_surface_final_manifest.json
experimental_core_four_scale_a_eligible_representation_surface_construction_readout_v0_1.md
```

`bounded_014_expansion_manifest.json` must report:

```text
original_014_rows_observed
expanded_rows_added
candidate_instruments_added
sessions_added
source_evidence
output_fingerprint
original_014_modified = false
```

---

## 12. Fingerprints

The run must compute:

```text
source_snapshot_fingerprint
bounded_014_candidate_surface_fingerprint
eligibility_rule_fingerprint
eligible_surface_fingerprint
eligible_instrument_pool_fingerprint
```

Fingerprint payloads must be canonical JSON with sorted keys, UTF-8, no
insignificant whitespace, and stable ordering of arrays where order is part of
the contract.

The Scale A sample preflight rerun may only consume an accepted pool by exact
`eligible_instrument_pool_fingerprint`.

---

## 13. Status Model

Allowed terminal statuses:

```text
PASS_WITH_RESTRICTIONS
BLOCKED_SOURCE_CARDINALITY
BLOCKED_ELIGIBLE_POOL_CARDINALITY
BLOCKED_SESSION_COVERAGE
BLOCKED_CALENDAR_COMPATIBILITY
BLOCKED_DAILY_LINKAGE
BLOCKED_IDENTITY
BLOCKED_PRIOR_20_COVERAGE
FAILED_SOURCE_SNAPSHOT
FAILED_DETERMINISM
FAILED_AUTHORITY_BOUNDARY
FAILED_CONTRACT
```

If the run finds fewer than 10 eligible instruments, it must not emit an
accepted partial pool. It may emit diagnostic reports, but
`eligible_instrument_pool.json` must be empty or explicitly marked:

```text
accepted_pool = false
```

---

## 14. Acceptance Criteria

The construction can close successfully only with:

```text
eligible_instruments >= 10
eligible_instruments <= 20
candidate_instruments_discovered <= 40
instruments_fully_evaluated <= 40
sessions_considered <= 10
minimum_eligible_sessions_per_instrument = 5
source_market_data_rows_read <= 500000
expanded_intraday_rows_written <= 200000
candidate_surface_files_written = 1
required_output_files_present = 17
output_files <= 18
unexpected_output_files = 0
output_bytes <= 50000000

calendar_compatibility_failures = 0
identity_failures_for_eligible_instruments = 0
daily_linkage_failures_for_eligible_instruments = 0
intraday_linkage_failures_for_eligible_instruments = 0
prior_20_daily_volume_coverage_failures_for_eligible_instruments = 0
required_core_four_input_coverage_failures_for_eligible_instruments = 0
forbidden_source_reads = 0
formula_executions = 0
builder_records_emitted = 0
integrated_candidate_records_emitted = 0
market_state_parquet_files_written = 0
official_outputs_written = 0
determinism_failures = 0
authority_failures = 0
hard_contract_failures = 0
```

Expected close status if successful:

```text
experimental_core_four_scale_a_eligible_representation_surface_construction
    = CLOSED_PASS_WITH_RESTRICTIONS
```

---

## 15. Next Boundary

After a successful construction, the next allowed gate is not Scale A execution.
It is:

```text
experimental_core_four_market_state_scale_a_sample_preflight_rerun_authorization_v0_1
```

That future gate may authorize rerunning the existing Scale A sample preflight
against the accepted `eligible_instrument_pool_fingerprint`.

Still closed:

```text
Scale_A_sample_preflight_rerun = NOT_AUTHORIZED_BY_THIS_GATE
Scale_A_builder_execution = NOT_AUTHORIZED_BY_THIS_GATE
Market_State_integration = NOT_AUTHORIZED_BY_THIS_GATE
Market_State_materialization = NOT_AUTHORIZED_BY_THIS_GATE
Market_State_candidate_parquet = NOT_AUTHORIZED_BY_THIS_GATE
official_Market_State = NOT_OPEN
production_builder = NOT_AUTHORIZED
downstream_consumption = NOT_AUTHORIZED
dataset_promotion = NOT_AUTHORIZED
full_history_execution = NOT_AUTHORIZED
full_universe_execution = NOT_AUTHORIZED
Scale_B = BLOCKED_UNTIL_GOVERNED_EXCHANGE_SESSION_CALENDAR
Scale_C = NOT_AUTHORIZED
```
