# BT-GATE-013 - Physical Historical Replay Slice Contract V0.1

## 0. Document Control

```text
DOCUMENT_ID =
14_BT_GATE_013_PHYSICAL_HISTORICAL_REPLAY_SLICE_CONTRACT_V0_1

GATE_ID =
BT-GATE-013

GATE_NAME =
PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1

CONTRACT_VERSION =
V0.1

STATUS =
CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW

BT-GATE-013 =
NOT_OPEN

BT-GATE-013_IMPLEMENTATION =
NOT_AUTHORIZED

CODE_IMPLEMENTATION =
NOT_AUTHORIZED

READ_ONLY_REVIEW =
ACCEPTED

CONTRACT_REVIEW_RESULT =
CONTRACT_CORRECTIONS_REQUIRED_APPLIED
```

This corrected contract does not authorize code, tests, configs, scripts, runs,
provider modification, upstream rebuild, Market State consumption, Event State
consumption, StateReplayFeed, StateBundle reads, the full 2005-2026 backtest or
edge claims.

---

## 1. Accepted Starting Point

```text
BT-GATE-012 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
BT-GATE-012_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED
```

BT-GATE-012 demonstrated multi-symbol and multi-session replay, a single global
replay order, shared cash, positions, equity accounting, session enforcement,
orders, fills, trades, deterministic execution and manifests over controlled
fixtures.

BT-GATE-013 crosses one new boundary only:

```text
physical historical rows
        ->
canonical physical-bar adaptation
        ->
ReplayBarEvent / ReplayGapEvent
        ->
BT-GATE-012 accepted portfolio replay engine
```

---

## 2. Gate Question

```text
Can the accepted BT-GATE-012 engine consume a small physical historical slice
from 013_ohlcv_1m_quote_guarded and reproduce the result causally and
deterministically while preserving temporal availability, row lineage, session
legality, accounting and execution semantics?
```

The gate does not ask whether there is edge, economic realism, borrow
availability, locates, SSR, halts, liquidity/capacity, batch validity or
full-history scalability.

```text
ONE_GATE = ONE_PRIMARY_UNCERTAINTY
NEW_BOUNDARY = PHYSICAL_013_ROWS_TO_ACCEPTED_REPLAY_ENGINE
```

---

## 3. Source Identity Layering

The source identity is layered. The implementation must record every layer and
must not collapse them into one ambiguous id.

```text
SOURCE_TABLE_ID = 013_ohlcv_1m_quote_guarded
SOURCE_LOGICAL_DATASET_ID = ohlcv_1m_quote_guarded_v0_2_candidate
SOURCE_PHYSICAL_DATASET_ID = ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
SOURCE_ROOT_ID = ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
SOURCE_ROOT_RELATIVE = data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
SOURCE_VALIDATION_RUN_ID = qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z
SOURCE_VALIDATION_MANIFEST_RELATIVE = _validation_runs/qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z/final_manifest_validation.json
SOURCE_CONSUMPTION_POLICY = ohlcv_1m_quote_guarded_consumption_policy.md
AUTHORIZED_ACCESS = READ_ONLY
UPSTREAM_REBUILD = PROHIBITED
PROVIDER_CODE_MODIFICATION = PROHIBITED
```

For the proposed acceptance slice, inspected rows show:

```text
ROW_DATASET_ID_ALLOWED_VALUES_OBSERVED = ohlcv_1m_quote_guarded_full_universe_v0_1
ROW_BUILD_RUN_ID_ALLOWED_VALUES_OBSERVED = qg_1m_full_2025_2026_v0_1_20260707T095701Z
```

These row-level values are lineage evidence, not the source root identity.

Absolute paths may appear only as inspection locations. They are prohibited as
scientific input identity and must be excluded from the scientific hash.

```text
ABSOLUTE_PATH_IN_SCIENTIFIC_IDENTITY = PROHIBITED
ABSOLUTE_PATH_IN_INSPECTION_LOCATION = ALLOWED_WITH_EXCLUSION_FROM_SCIENTIFIC_HASH
```

---

## 4. Authorized Physical Data Product

BT-GATE-013 may consume only the physical bar product identified above. It may
not consume other provider tables, feature tables, StateBundles, Market State or
Event State.

The source is a quote-guarded derived 1-minute OHLCV price view. It is not raw
trade evidence, not quote evidence, not execution truth, not split-normalized or
dividend-adjusted data, and not an unrestricted institutional source of truth.

The run must classify itself as:

```text
RUN_PURPOSE = ENGINE_VALIDATION_RUN
EDGE_EVIDENCE = NOT_AUTHORIZED
ECONOMIC_REALISM = INCOMPLETE
STRATEGY_OPTIMIZATION = NOT_AUTHORIZED
```

---

## 5. Exact Physical Binding V0.1

The adapter must declare this binding in versioned, hashed configuration before
reading rows for replay:

```text
source_symbol_field = ticker
source_timestamp_field = ts_utc
source_epoch_ms_confirmation_field = t
source_date_field = date
source_year_field = year
source_month_field = month
source_open_field = o
source_high_field = h
source_low_field = l
source_close_field = c
source_volume_field = v
source_transaction_count_field = n
source_price_view_field = quote_guarded_view
source_repair_applied_field = quote_guarded_repair_applied
source_repair_lookup_state_field = repair_lookup_state
source_repair_state_field = repair_state
source_repair_reason_field = repair_reason
source_repair_manifest_field = source_quote_guarded_repair_manifest
source_dataset_id_field = dataset_id
source_build_run_id_field = build_run_id
source_created_utc_field = created_utc
source_raw_path_field = source_raw_path
```

Observed physical types for the selected files include:

```text
ticker:string
ts_utc:string
date:string
year:int64
month:int64
o/h/l/c:double
v:double
n:int64
t:int64
quote_guarded_repair_applied:bool
quote_guarded_view:string
repair_lookup_state:string
repair_state:string or null
repair_reason:string or null
dataset_id:string
build_run_id:string
created_utc:string
source_raw_path:string
```

`v` is physically `double`. Before conversion to the engine integer volume, it
must be finite, non-negative and integer-valued. Silent coercion is prohibited.

```text
VOLUME_DOUBLE_TO_INT_POLICY_V0_1 = REQUIRE_FINITE_NON_NEGATIVE_INTEGER_VALUED
SILENT_TYPE_COERCION = PROHIBITED
```

`vw` is a vendor-derived field. It must not be requested, propagated or used by
strategy, replay, execution, valuation, accounting or metrics.

```text
VW_POLICY = PRESENT_BUT_NON_CONSUMABLE_VENDOR_DERIVED_FIELD
```

---

## 6. Repair and Provenance Fields

Repair and provenance fields are admitted only for lineage and restriction
validation:

```text
repair_fields_consumption = LINEAGE_AND_RESTRICTION_VALIDATION_ONLY
repair_fields_strategy_input = PROHIBITED
repair_fields_execution_input = PROHIBITED
repair_fields_valuation_input = PROHIBITED
repair_fields_decision_input = PROHIBITED
```

These fields may be recorded in manifests and row lineage:

```text
quote_guarded_repair_applied
quote_guarded_view
repair_lookup_state
repair_state
repair_reason
source_quote_guarded_repair_manifest
dataset_id
build_run_id
created_utc
source_raw_path
```

`dataset_id`, `build_run_id`, `created_utc` and `source_raw_path` are provenance
fields. They are not market observations.

---

## 7. Component Boundary

The future component authorized only after owner approval is:

```text
PhysicalBarReplayAdapterV0_1
```

Responsibility:

```text
validated physical 013 row -> canonical ReplayBarEvent
missing contractually expected minute -> ReplayGapEvent
```

The adapter does not calculate features, Market State, Event State, signals,
orders, fills, accounting or repairs. It does not infer halts and does not alter
BT-GATE-012 execution or accounting semantics.

```text
StateReplayFeed = NOT_AUTHORIZED
```

---

## 8. Acceptance Slice Profile

The accepted candidate slice for final contract review is:

```text
SLICE_ID = BT_GATE_013_QG5_2026_01_05_2026_01_06_V0_1_CANDIDATE
SESSIONS = 2026-01-05, 2026-01-06
SYMBOLS = ABAT, ABEO, ABSI, ABTC, ACB
SYMBOL_SESSIONS = 10
SELECTION_POLICY = OPERATIONAL_COVERAGE_ONLY
PROFITABILITY_BASED_SELECTION = PROHIBITED
OUTCOME_BASED_SELECTION = PROHIBITED
```

The slice must satisfy:

```text
distinct_sessions >= 2
distinct_symbols_per_session >= 3
symbol_sessions >= 6
same_timestamp_cross_symbol_bars = REQUIRED
at_least_one_detectable_missing_expected_minute = REQUIRED
contractual_session_open_coverage = REQUIRED
contractual_session_close_coverage = REQUIRED
physical_source_rows = REQUIRED
portable_relative_paths = REQUIRED
all_input_files_hashed = REQUIRED
```

Observed inspection evidence for this slice:

```text
2026-01-05: ABAT 390 rows / 0 gaps; ABEO 338 / 52 gaps; ABSI 384 / 6 gaps; ABTC 390 / 0 gaps; ACB 326 / 64 gaps
2026-01-06: ABAT 390 rows / 0 gaps; ABEO 365 / 25 gaps; ABSI 385 / 5 gaps; ABTC 389 / 1 gap; ACB 343 / 47 gaps
open 14:30Z present for all selected symbol-sessions = true
close 20:59Z present for all selected symbol-sessions = true
duplicate timestamps observed in selected regular sessions = 0
invalid OHLC rows observed in selected regular sessions = 0
```

---

## 9. Temporal Contract

The source files do not expose native `bar_start_timestamp_utc`,
`bar_end_timestamp_utc`, `available_at_utc` or `source_as_of_utc` columns. These
are canonical derived fields and must be labeled as such.

```text
SOURCE_TIMESTAMP_FIELD = ts_utc
SOURCE_TIMESTAMP_SEMANTICS = BAR_START_UTC
EPOCH_MS_CONFIRMATION_FIELD = t
bar_start_timestamp_utc = parse_utc(ts_utc)
bar_end_timestamp_utc = bar_start_timestamp_utc + 1 minute
available_at_utc = bar_end_timestamp_utc
REPLAY_EVENT_AVAILABLE_AT = available_at_utc
```

`source_as_of_utc` must not be invented as physical evidence.

```text
SOURCE_AS_OF_NATIVE_FIELD = NONE
SOURCE_AS_OF_POLICY_V0_1 = NOT_APPLICABLE_FOR_STATIC_HASH_PINNED_PHYSICAL_FILE
```

`created_utc` is build/provenance time only. It is not market availability and
must not be used to delay or advance replay delivery.

A bar representing `[bar_start_timestamp_utc, bar_end_timestamp_utc)` may not
make high, low, close, volume or transaction count observable at the start of
the interval.

```text
NO_BAR_LOOKAHEAD = REQUIRED
EVENT_DELIVERY_CONDITION = event_loop.clock >= available_at_utc
```

---

## 10. Calendar and Sessions

```text
SESSION_POLICY = REGULAR_ONLY_XNYS_V0_1
CALENDAR_AUTHORITY = FROZEN_HASHED_SNAPSHOT
SESSION_CALENDAR_TIMEZONE = America/New_York
INTERNAL_TIME_STANDARD = UTC
OVERNIGHT_POSITIONS = PROHIBITED
SOURCE_ROWS_AS_CALENDAR_AUTHORITY = PROHIBITED
```

For each selected session the calendar snapshot must declare:

```text
session_date
market_open_utc
market_close_utc
early_close_flag
calendar_source_identity
calendar_snapshot_sha256
```

---

## 11. Row Key, Ordering and Locator

Canonical physical key:

```text
(session_date, canonical_symbol, bar_start_timestamp_utc)
```

Duplicate policy:

```text
EXACT_DUPLICATE_PHYSICAL_ROW = FAIL_DUPLICATE_PHYSICAL_BAR
CONFLICTING_DUPLICATE_PHYSICAL_ROW = FAIL_CONFLICTING_PHYSICAL_BAR
SILENT_DEDUPLICATION = PROHIBITED
```

The row locator is frozen as:

```text
SOURCE_ROW_LOCATOR_POLICY_V0_1 = SOURCE_FILE_SHA256_PLUS_PARQUET_ROW_GROUP_AND_ROW_INDEX
source_row_locator = {
  source_file_sha256,
  parquet_row_group_index,
  row_index_within_row_group
}
zero_based = true
computed_from_physical_parquet_order = true
dataframe_order = prohibited
filesystem_enumeration_order = prohibited
```

If this locator cannot be reproduced from identical bytes, implementation must
fail closed and return to owner review.

---

## 12. Row-to-Event Lineage

Every `ReplayBarEvent` must be traceable to exactly one physical source row.

Minimum lineage:

```text
source_table_id
source_logical_dataset_id
source_physical_dataset_id
source_root_id
source_relative_path
source_file_sha256
source_file_size_bytes
source_file_row_count
source_row_locator
source_symbol
source_timestamp_raw
canonical_symbol
bar_start_timestamp_utc
bar_end_timestamp_utc
available_at_utc
```

`ReplayGapEvent` has no physical source row. Its lineage must reference the
calendar snapshot, symbol-session, expected minute, neighbors if present and
gap detection rule version.

---

## 13. Gap Policy

```text
MISSING_EXPECTED_MINUTE = ReplayGapEvent
SYNTHETIC_FORWARD_FILL = PROHIBITED
SYNTHETIC_ZERO_VOLUME_BAR = PROHIBITED
INTERPOLATED_BAR = PROHIBITED
```

`ReplayGapEvent` semantics:

```text
supplies_execution_price = false
triggers_fill = false
updates_valuation_price = false
creates_trade = false
infers_halt = false
GAP_CAUSE_V0_1 = UNKNOWN_SOURCE_GAP
HALT_INFERENCE = NOT_AUTHORIZED
```

---

## 14. Strategy and Execution Semantics

```text
STRATEGY_PURPOSE = INFRASTRUCTURE_ACCEPTANCE_ONLY
STRATEGY_LOGIC = FROZEN_BEFORE_RESULT_INSPECTION
PARAMETER_SEARCH = PROHIBITED
OPTIMIZATION = PROHIBITED
OUTCOME_DRIVEN_ADJUSTMENT = PROHIBITED
EDGE_INTERPRETATION = PROHIBITED
EXECUTION_SEMANTICS = UNCHANGED_FROM_BT_GATE_012
COST_MODEL = UNCHANGED_FROM_BT_GATE_012
ACCOUNTING_MODEL = UNCHANGED_FROM_BT_GATE_012
PORTFOLIO_VALUATION_PRICE_FIELD = close
```

If physical data exposes a need to change fills, costs, accounting or strategy
semantics, the gate must stop and return to owner review.

---

## 15. Physical Integrity and Mutability Protection

```text
HASH_BEFORE_READ = REQUIRED
HASH_AFTER_READ = REQUIRED
HASH_BEFORE_READ = HASH_AFTER_READ
UNDECLARED_PHYSICAL_READ = PROHIBITED
FAIL_SOURCE_MUTATION
FAIL_SOURCE_HASH_MISMATCH
```

All physically read files, including calendar and metadata files that affect
selection, schema or adaptation, must be listed with relative path, size and
SHA-256.

---

## 16. Required Run Artifacts

```text
resolved_input_manifest
source_file_inventory
source_schema_binding
selected_symbol_sessions
selected_physical_rows
row_to_event_lineage
replay_bar_events
replay_gap_events
orders
fills
trades
cash_ledger
positions
equity_curve
performance_summary
validation_report
negative_derivative_report
final_manifest
```

The final manifest must declare source identities, validation manifest hash,
relative paths, source file hashes and sizes, selected rows, sessions, symbols,
timestamp ranges, available_at ranges, calendar hash, adapter/engine/strategy
versions, output hashes, deterministic output hash, validation status and
boundary preservation status.

---

## 17. Scientific Hash and Volatile Fields

The scientific hash must cover all causally relevant inputs, configuration and
outputs. It must not include package creation timestamp, wall-clock duration,
host name, user name, process id, temporary directory, absolute path,
installation path or log rendering timestamp.

```text
VOLATILE_FIELD_EXCLUSION_POLICY = FROZEN_CLOSED_LIST
```

---

## 18. Determinism

At least two clean extractions must reproduce identical canonical hashes for
resolved inputs, selected rows, replay events, orders, fills, trades, ledger,
equity curve, scientific manifest and deterministic output.

---

## 19. Negative Derivatives

```text
NEGATIVE_01 source file byte changed -> FAIL_SOURCE_HASH_MISMATCH
NEGATIVE_02 source changed between resolution and completed read -> FAIL_SOURCE_MUTATION
NEGATIVE_03 required physical field missing -> FAIL_SOURCE_SCHEMA_MISMATCH
NEGATIVE_04 exact physical row duplicated -> FAIL_DUPLICATE_PHYSICAL_BAR
NEGATIVE_05 duplicate symbol/timestamp with conflicting values -> FAIL_CONFLICTING_PHYSICAL_BAR
NEGATIVE_06 invalid OHLC or negative volume -> FAIL_INVALID_PHYSICAL_BAR
NEGATIVE_07 bar delivered before available_at_utc -> FAIL_TEMPORAL_AVAILABILITY_VIOLATION
NEGATIVE_08 naive or ambiguous timestamp -> FAIL_AMBIGUOUS_SOURCE_TIMESTAMP
NEGATIVE_09 fixed-offset DST handling -> FAIL_CALENDAR_TIMEZONE_CONTRACT
NEGATIVE_10 missing contractual session close -> FAIL_MISSING_CONTRACTUAL_CLOSE
NEGATIVE_11 truncated selected session -> FAIL_TRUNCATED_PHYSICAL_SESSION
NEGATIVE_12 symbol or session outside frozen selection enters replay -> FAIL_SCOPE_LEAKAGE
NEGATIVE_13 same bytes moved to a different absolute path -> PASS_WITH_IDENTICAL_SCIENTIFIC_HASH
NEGATIVE_14 physical rows enumerated in different input order -> PASS_WITH_IDENTICAL_CANONICAL_EVENT_SEQUENCE
NEGATIVE_15 expected minute removed -> ReplayGapEvent with no price, fill or valuation update
```

---

## 20. Acceptance Criteria

```text
contract_conformance = PASS
physical_input_integrity = PASS
source_schema_validation = PASS
source_quality_contract_validation = PASS
slice_selection_freeze = PASS
profitability_independent_selection = PASS
row_level_lineage = PASS
temporal_availability_validation = PASS
calendar_and_session_validation = PASS
gap_semantics = PASS
global_replay_order = PASS
multi_symbol_multi_session_execution = PASS
accounting_reconciliation = PASS
session_enforcement = PASS
negative_derivatives = PASS
clean_reproduction = PASS
deterministic_output = PASS
boundary_preservation = PASS
```

Permitted final state if all pass:

```text
BT-GATE-013 = CLOSED_PASS_PHYSICAL_HISTORICAL_REPLAY_ACCEPTED
```

This does not authorize `BACKTEST_ENGINE_READY`, `RESEARCH_RUNNER_READY`,
`FULL_HISTORY_READY`, `PRODUCTION_READY`, `ECONOMIC_REALISM_VALIDATED` or
`EDGE_PROVEN`.

---

## 21. Explicit Exclusions

```text
Market State consumption
Event State consumption
StateBundle physical reads
StateReplayFeed
feature engineering
014 master intraday feature consumption
015 microstructure feature consumption
point-in-time universe construction
stocks-in-play eligibility
news
fundamentals
short-interest data
borrow availability
locates
locate costs
hard-to-borrow modeling
SSR semantics
halt semantics or halt inference
corporate-action modeling beyond already-frozen source integrity
bid/ask execution
partial fills
queue position
liquidity constraints
participation limits
market impact
capital contention claims
batch strategy families
parameter optimization
train/test research orchestration
multiple-testing correction
DSR
PBO
CSCV
machine learning
reinforcement learning
AlphaEvolve
edge claims
full 2005-2026 backtest
provider modification
upstream data rebuild
live trading
```

```text
mechanically executable order != actually shortable action != economically valid trade != demonstrated edge
```

---

## 22. Material Stop Conditions

Future implementation must stop and return to owner review if source timestamp
or availability semantics cannot be proven, table 013 schema requires an
undeclared interpretation, BT-GATE-012 execution/accounting semantics must
change, calendar authority must change, data repair becomes necessary, another
physical source table becomes necessary, Market/Event State becomes necessary,
provider modification becomes necessary, scope expands beyond the frozen slice,
`source_as_of` becomes materially required, or the row locator cannot be
reproduced from identical bytes.

---

## 23. Evidence Required Before Implementation Authorization

The final authorization review package must include corrected full contract,
contractual diff, modified governance surfaces, clause-to-evidence matrix,
hashes of normative evidence, final acceptance slice proposal, package manifest
and reproducible no-implementation evidence.

```text
PROVIDER_EVIDENCE_REQUIRED = false
```

If later review finds an unresolved contradiction in source timestamp or
availability semantics, this must become `true`.

---

## 24. Authorization Flow

Current state:

```text
BT-GATE-013 = NOT_OPEN
CONTRACT = CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
IMPLEMENTATION = NOT_AUTHORIZED
```

Only after explicit owner approval may the state become:

```text
BT-GATE-013 = AUTHORIZED_FOR_CONTINUOUS_IMPLEMENTATION
BT-GATE-013_IMPLEMENTATION = AUTHORIZED
EXECUTION_MODE = CONTINUOUS_UNTIL_FINAL_ACCEPTANCE_PACKET
NO_INTERMEDIATE_MICROGATES = AUTHORIZED
NEXT_OWNER_REVIEW = FINAL_GATE_ACCEPTANCE_ONLY_UNLESS_MATERIAL_SCOPE_OR_SEMANTIC_CHANGE
```

This document does not itself grant that authorization.

---

## 25. Final Invariants

```text
BT-GATE-012_ACCEPTED_SEMANTICS = PRESERVED
ONE_NEW_BOUNDARY = PHYSICAL_013_ROWS_TO_ACCEPTED_REPLAY_EVENTS
NO_BAR_LOOKAHEAD = REQUIRED
ROW_LEVEL_LINEAGE = REQUIRED
PHYSICAL_INPUT_HASHING = REQUIRED
GAP_FORWARD_FILL = PROHIBITED
DETERMINISTIC_CLEAN_REPRODUCTION = REQUIRED
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
MARKET_STATE = NOT_AUTHORIZED
EVENT_STATE = NOT_AUTHORIZED
STATE_REPLAY_FEED = NOT_AUTHORIZED
PROVIDER_MODIFICATION = NOT_AUTHORIZED
FULL_2005_2026_BACKTEST = NOT_AUTHORIZED
EDGE_CLAIMS = NOT_AUTHORIZED
```

---

## 26. Decision Requested

```text
OPTION_A = CONTRACT_ACCEPTED_READY_FOR_IMPLEMENTATION_AUTHORIZATION_DECISION
OPTION_B = RETURN_WITH_REQUIRED_CONTRACT_CORRECTIONS
```

This document does not request code changes, physical run execution or gate
closure.
