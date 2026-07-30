## Current Authoritative State - BT-GATE-014 final closure

```text
BT-GATE-014 = CLOSED_PASS_POINT_IN_TIME_MARKET_STATE_CONSUMPTION_WITH_RESTRICTIONS
BT-GATE-014_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED
V0.5 = CONSUMED_FINAL
SECOND_EXECUTION_V0.5 = PROHIBITED
physical files / rows / events / inserts / observations = 1 / 2 / 2 / 2 / 2
early delivered / orders / fills / PnL = 0 / 0 / 0 / false
deterministic_output_hash = 6331839dfc6538f7dd6fda9a1fd7efbc7497d541dcb0c0d89cfd679762067cb1
BT-GATE-015 = NOT_OPEN
BT-GATE-015_IMPLEMENTATION = NOT_AUTHORIZED
Event State = NOT_AUTHORIZED
```

Mandatory restart handoff:
`docs/00_system/CURRENT_PROJECT_HANDOFF.md`

All subsequent status blocks are historical snapshots and are superseded by
this block.
## BT-GATE-014 V0.5 R2 pre-execution correction

```text
V0.5 R1 external pre-execution review = FAIL_TARGETED_CORRECTIONS_REQUIRED
V0.5 authorization consumption = NOT_CONSUMED
V0.5 physical read = NOT_EXECUTED
R2 correction = closed configuration accepts and validates the two restriction-domain binding fields
governed physical and metadata inputs = 10
physical command = NOT_APPROVED_PENDING_R2_EXTERNAL_PREEXECUTION_REVIEW
```

## Historical Snapshot - Superseded - Current Authoritative State - BT-GATE-014 V0.5

```text
BT-GATE-014 = OPEN_PENDING_V0_5_EXTERNAL_PREEXECUTION_REVIEW
V0.3 = CONSUMED_FAILED_FINAL
V0.4 = CONSUMED_FAILED_FINAL
SECOND_EXECUTION_V0.3/V0.4 = PROHIBITED
RESTRICTION_DOMAIN_BINDING = ADOPTED
V0.5 = AUTHORIZED_NOT_CONSUMED
PHYSICAL_COMMAND_V0.5 = NOT_APPROVED_PENDING_EXTERNAL_PREEXECUTION_REVIEW
PHYSICAL_READ_V0.5 = NOT_EXECUTED
BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED
Event State = NOT_OPEN
```

The provider/shared-boundary clarification separates physical provenance,
bounded replay-consumption and component replay restriction domains. V0.5 may
be executed once only after an independent pre-execution PASS.

# CHANGELOG - TSIS Backtest Engine

## 2026-07-28 | clean implementation reset

- Emptied the previous `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE` implementation shell.
- Recreated a clean implementation root aligned with the current CTO direction.
- Added root operational documents: `README.md`, `AGENTS.md`, `LOCAL_RULES.md`, `CHANGELOG.md` and `pyproject.toml`.
- Created minimal folders for `src`, `tests`, `configs`, `runs` and `docs`.
- Preserved the architectural boundary: `00_CTO/14_BACKTEST_ENGINE` decides and documents; `02_TSIS_BACKTEST_ENGINE` implements and executes.
- Current implementation priority: `RunPreflight` contracts and synthetic fail-closed tests.

No production engine code, real-data consumption, backtest run or dataset promotion was introduced in this reset.

## 2026-07-28 | RunPreflight synthetic increment

- Added `docs/00_system/01_RUNPREFLIGHT_IMPLEMENTATION_PLAN_V0_1.md` as a short execution micro-plan.
- Added preflight contracts, registries, manifest writers and `RunPreflight` implementation.
- Added synthetic unit tests for fail-closed dataset, price-view, universe and candidate-policy cases.
- Added temporal legality test for `MarketDataBar1m.available_at`.
- Added deterministic manifest test with fixed `generated_at_utc`.
- Verification: `$env:PYTHONPATH='src'; python -m unittest discover -s tests` -> 17 tests OK.

No real TSIS data was consumed in this increment.

## 2026-07-28 | RunPreflight hardening before real fixture

- Added missing fail-closed tests for `DATASET_ROOT_NOT_FOUND`, `INVALID_DATE_RANGE`, `CANDIDATE_RUN_PURPOSE_NOT_PERMITTED` and `SYMBOL_NOT_IN_UNIVERSE`.
- Changed output behavior: manifests are written under `output_root/run_id`; a non-empty run output directory is rejected with `RUN_OUTPUT_NOT_EMPTY` and no old output is deleted.
- Added full `MissingDataPolicy` and `CorporateActionPolicy` serialization into `data_manifest.json`.
- Clarified that missing-data detection, corporate-action lookup, file discovery, row counts and SHA-256 hashes still require the real-data inspector.
- Verification: `$env:PYTHONPATH='src'; python -m unittest discover -s tests` -> 17 tests OK.

## 2026-07-28 | RunPreflight pre-real guard hardening

- Added safe `run_id` validation with `INVALID_RUN_ID` and containment under `output_root` before writing run outputs.
- Added exact candidate manifest binding: candidate datasets now require a registered `DatasetDefinition.validation_manifest`, and the accepted manifest must match it exactly.
- Added fail-closed outcomes: `CANDIDATE_REGISTERED_VALIDATION_MANIFEST_REQUIRED` and `CANDIDATE_VALIDATION_MANIFEST_MISMATCH`.
- Added explicit report status fields: `context_resolution_status`, `physical_inspection_status` and `preflight_status`.
- Added a real-fixture guard: `TSIS_REAL_DATA_FIXTURE` cannot pass while physical inspection is not implemented; it fails with `PHYSICAL_INSPECTION_NOT_IMPLEMENTED` after context resolution.
- Verification: `$env:PYTHONPATH='src'; python -m unittest discover -s tests` -> 21 tests OK.

No real TSIS data was consumed in this increment.

## 2026-07-28 | Physical layout discovery and fixture selection

- Read the active physical data-plane README and quote-guarded materialization evidence.
- Inspected the candidate dataset root and confirmed layout: `year=YYYY/ticker=SYMBOL/month=MM/part-000.parquet`.
- Inspected parquet metadata and sample rows with `pyarrow`; no full-universe processing was run.
- Confirmed observed timestamp semantics: `ts_utc` is UTC minute-start string, `t` matches epoch milliseconds, and the engine must derive `available_at = ts_start + 1 minute`.
- Located `lt1b_universe_v0_1` physical parquet and confirmed the selected symbols are `active_lt_1b_last_classifiable` inside PTI windows.
- Located `corporate_actions_table_v0_1` under the active `G:/TSIS/data` mount and confirmed zero exact/nearby actions for the selected fixture symbols.
- Selected fixture `TSIS_REAL_DATA_FIXTURE_2026_01_05_LT1B_QG5_V0_1` with symbols `ABAT`, `ABEO`, `ABSI`, `ABTC`, `ACB`.
- Added discovery artifacts: `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/docs/00_system/02_PHYSICAL_LAYOUT_DISCOVERY_V0_1.md`, `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/docs/00_system/02_PHYSICAL_LAYOUT_DISCOVERY_V0_1.json`.
- Added fixture config: `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/configs/fixtures/TSIS_REAL_DATA_FIXTURE_2026_01_05_LT1B_QG5_V0_1.json`.
- Verification: `$env:PYTHONPATH='src'; python -m unittest discover -s tests` -> 21 tests OK; fixture JSON validates with `python -m json.tool`.

State after this increment:

```text
PHYSICAL_LAYOUT_DISCOVERED = PASS
TSIS_REAL_DATA_FIXTURE_SELECTED = SELECTED_NOT_INSPECTED
REAL_DATA_INSPECTION = NOT_IMPLEMENTED
REAL_DATA_PREFLIGHT = NOT_EXECUTED
```

## 2026-07-28 | RealDataInspector and bounded real preflight

- Corrected the fixture `price_view_policy` so `execution` is structured as a resolvable `price_view` plus explicit allowed use and execution-semantics state.
- Added `pyarrow>=21` as an explicit dependency for parquet inspection.
- Added `src/tsis_backtest/preflight/real_data_inspector.py` with `PhysicalDataInspection` and `TickerDayInspection`.
- Integrated `RealDataInspector` into `RunPreflight` for `TSIS_REAL_DATA_FIXTURE` runs.
- Added physical checks for missing files, required schema, open/close proxy rows, duplicate timestamps, invalid OHLCV, row lineage, corporate actions and discovery-evidence drift.
- Implemented the data rule that vendor-derived `vw` is non-consumable: it is neither required nor validated by DATA/RunPreflight/RealDataInspector.
- Added synthetic parquet tests for the inspector and integration path.
- Verification: `$env:PYTHONPATH='src'; python -m unittest discover -s tests` -> 32 tests OK.
- Executed bounded real-data preflight for `TSIS_REAL_DATA_FIXTURE_2026_01_05_LT1B_QG5_V0_1`.
- Real run output: `runs/run_preflight_real_fixture_2026_01_05_qg5_v0_1`.
- Real run result: `PREFLIGHT_PASS`, `PHYSICAL_INSPECTION_PASS`, 1,828 rows, 5 source files consumed, 8 content hashes, zero exact corporate actions.
- Expected interior gaps were recorded as `OBSERVED_MINUTE_GAP` for `ABEO`, `ABSI` and `ACB`; the policy `EMIT_GAP_WITHOUT_IMPUTATION` allowed them.

State after this increment:

```text
REAL_DATA_INSPECTOR_IMPLEMENTED = PASS
SYNTHETIC_UNIT_TESTS = PASS, 32 tests
REAL_DATA_INSPECTION = PASS
REAL_DATA_PREFLIGHT = PASS
BACKTEST_VERTICAL_SLICE = NOT_STARTED
```

## 2026-07-28 | RealDataInspector auditability sealing before replay

- Added `RunDataRequest.fixture_id` for real-fixture binding.
- Added fail-closed request/fixture checks: fixture id, dataset id, universe id, session date, calendar, session policy, timezone, price views and selected symbols must match the fixture.
- Added failure code `REAL_FIXTURE_REQUEST_MISMATCH`.
- Added dataset validation-manifest SHA-256 verification inside `RealDataInspector`.
- Added failure code `VALIDATION_MANIFEST_HASH_MISMATCH`.
- Added the validation manifest to `snapshot_or_content_hashes`; active real fixture hash count is now 9.
- Added synthetic tests for request/fixture mismatch and validation-manifest hash mismatch.
- Verification: `$env:PYTHONPATH='src'; python -m unittest discover -s tests` -> 34 tests OK.
- Executed sealed real preflight run `run_preflight_real_fixture_2026_01_05_qg5_v0_2` -> `PREFLIGHT_PASS`, `PHYSICAL_INSPECTION_PASS`, 1,828 rows, 5 source files, 9 hashes.

State after this sealing:

```text
REAL_DATA_PREFLIGHT_SEALED_FOR_REPLAY = PASS
SYNTHETIC_UNIT_TESTS = PASS, 34 tests
VALIDATION_MANIFEST_HASH = VERIFIED
FIXTURE_REQUEST_BINDING = ENFORCED
NEXT_INCREMENT = REPLAY_MINIMUM
```

## 2026-07-28 | Minimum replay/event-loop increment

- Added `src/tsis_backtest/replay/` with replay contracts and `HistoricalReplayFeed`.
- Replay now requires `PREFLIGHT_PASS` and `PHYSICAL_INSPECTION_PASS` before reading market data.
- Replay verifies consumed source-file hashes from `snapshot_or_content_hashes` before reading bars.
- Added deterministic event ordering: `available_at`, event priority (`GAP` before `BAR`), `ticker`.
- Added `ReplayBarEvent` and `ReplayGapEvent`; interior gaps are emitted without imputing bars.
- Preserved legal bar timing: `available_at = ts_start + 1 minute`; bars are not observable before `available_at`.
- Excluded vendor-derived fields such as `vw` from the replay event contract.
- Added synthetic tests and real fixture smoke test.
- Verification: `$env:PYTHONPATH='src'; python -m unittest discover -s tests` -> 43 tests OK.
- Wrote real replay evidence under `runs/replay_real_fixture_2026_01_05_qg5_v0_1`.

Real replay result:

```text
event_count = 1950
bar_count = 1828
gap_count = 122
first_available_at = 2026-01-05T14:31:00+00:00
last_available_at = 2026-01-05T21:00:00+00:00
```

State after this increment:

```text
REPLAY_MINIMUM_IMPLEMENTED = PASS
ENGINE_TEST_SUITE = PASS, 43 tests
REAL_FIXTURE_REPLAY_SMOKE = PASS
NEXT_INCREMENT = MECHANICAL_DECISION_ORDER_FILL_POSITION
```

## 2026-07-28 | Mechanical ABAT round trip

- Hardened replay: `verify_hashes=False` is rejected with `REPLAY_HASH_VERIFICATION_REQUIRED`.
- Added explicit test that `GAP` precedes `BAR` when `available_at` matches.
- Added replay lineage hashes: `replay_preflight_report_sha256` and `replay_event_sequence_sha256`.
- Added `src/tsis_backtest/mechanics/` with `ScheduledDecision`, `OrderIntent`, `Order`, `Fill`, `Position`, `TradeLedger`, `MechanicalRunSummary` and `MechanicalEventLoop`.
- Implemented programmed open/close proxy short path for one ticker.
- Added synthetic tests and real ABAT smoke test.
- Verification: `$env:PYTHONPATH='src'; python -m unittest discover -s tests` -> 51 tests OK.
- Wrote real ABAT evidence under `runs/mechanical_abat_short_open_close_v0_1`.

Real ABAT result:

```text
ticker = ABAT
quantity = 100
entry_price = 3.87
exit_price = 4.665
gross_pnl = -79.5
linear_reference_gross_pnl = -79.5
final_position_quantity = 0
execution_realism_claimed = false
edge_evaluated = false
```

State after this increment:

```text
MECHANICAL_TRADE_PATH_IMPLEMENTED = PASS
ENGINE_TEST_SUITE = PASS, 51 tests
REAL_ABAT_MECHANICAL_SMOKE = PASS
NEXT_INCREMENT = COST_CASH_NET_PNL_MINIMUM
```

## 2026-07-28 | Minimum accounting gross-to-net increment

- Added `src/tsis_backtest/accounting/` with accounting contracts and `AccountingEngine`.
- Added `CostComponent`, `CostBreakdown`, `CostModel`, `CashLedgerEntry`, `AccountState`, `AccountingRunSummary` and `AccountingRunResult`.
- Implemented deterministic gross-to-net reconciliation from the mechanical `TradeLedger`.
- Kept cost categories separate: commission, routing/ECN, regulatory, locate, borrow and other.
- Added cash ledger entries for short-sale proceeds, cover payment and transaction costs.
- Added tests for zero costs, per-share commission, minimum commission, multiple components, short loser, open-position rejection, gross mismatch reporting and deterministic accounting hash.
- Verification: `$env:PYTHONPATH='src'; python -m unittest discover -s tests` -> 61 tests OK.
- Wrote real ABAT accounting smoke under `runs/accounting_abat_short_open_close_v0_1`.
- Preserved sub-cent cost-model rates in serialized manifests, e.g. `commission_per_share = 0.005`.

Real ABAT accounting result:

```text
gross_pnl = -79.50
total_costs = 2.00
realized_net_pnl = -81.50
ending_equity = 9918.50
final_position_quantity = 0
```

State after this increment:

```text
ACCOUNTING_MINIMUM_IMPLEMENTED = PASS
ENGINE_TEST_SUITE = PASS, 61 tests
REAL_ABAT_ACCOUNTING_SMOKE = PASS
BROKER_COST_REALISM = NOT_CLAIMED
FILL_REALISM = NOT_CLAIMED
SHORT_TRADABILITY = NOT_EVALUATED
EDGE = NOT_EVALUATED
NEXT_INCREMENT = CHOOSE_BOUNDED_NEXT_STEP
```
## 2026-07-29 | Execution semantics and cost-model contract

- Added `docs/00_system/07_EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1.md` as a documentation-only contract-definition increment.
- Set `CONTRACT_DEFINITION = AUTHORIZED` and `CODE_IMPLEMENTATION = NOT_AUTHORIZED`.
- Defined `bar_based_execution_profile_v0_1` as the primary next implementation profile and `quote_aware_execution_profile_v0_1` as reserved/not authorized.
- Defined decision/order/fill timing terms: `decision_timestamp`, `order_submission_timestamp`, `first_eligible_fill_timestamp`, `economic_execution_timestamp` and `fill_recorded_at`.
- Added explicit same-bar lookahead prohibition and programmed open/close proxy legality rules.
- Defined initial market, limit and stop semantics for bar-based execution.
- Defined adverse deterministic slippage rules, cost components, decimal/money rounding, missing bar/gap outcomes and acceptance tests.
- Preserved non-claims: `BROKER_COST_REALISM = NOT_CLAIMED`, `FILL_REALISM = NOT_CLAIMED`, `SHORT_TRADABILITY = NOT_EVALUATED`, `EDGE = NOT_EVALUATED`.
- Preserved state-consumption boundary: `BACKTEST_STATE_CONSUMPTION = NOT_AUTHORIZED`, `STATE_REPLAY_FEED = NOT_AUTHORIZED`.

No code implementation, provider edit, state consumption, physical StateBundle read, StateReplayFeed, production, downstream, full 2005-2026 backtest or execution-realism claim was introduced.
## 2026-07-29 | Execution semantics contract semantic correction

- Corrected `docs/00_system/07_EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1.md` before any code authorization.
- Changed contract state to `CORRECTED_DRAFT_READY_FOR_REVIEW`; `CODE_IMPLEMENTATION = NOT_AUTHORIZED` remains active.
- Fixed material limit-order semantics: slippage cannot violate limit-price protection.
- Added stop gap-through semantics: `BUY/BUY_TO_COVER` stop-market base uses `max(stop_price, source_bar.open)` and `SELL/SELL_SHORT` uses `min(stop_price, source_bar.open)` before adverse slippage.
- Added canonical calculation sequence: base price -> gap policy -> slippage -> tick handling -> notional -> costs -> sub-cent preservation -> ledger rounding -> reconciliation.
- Declared `decimal_rounding_mode = ROUND_HALF_EVEN`.
- Defined the future V0.1 implementation subset: `MARKET_PROXY`, `LIMIT`, `STOP_MARKET_PROXY`, `FULL_FILL_ONLY`, `DAY`; partial fills, liquidity sizing, cancellation race and broker/risk rejection remain reserved/not implemented.
- Tightened close proxy legality: `order_submission_timestamp <= final_regular_bar.ts_start`.
- Added acceptance tests for limit protection, stop gap-through, deterministic rounding sequence, unsupported partial fills and late close orders.
- Updated `AGENTS.md` and `README.md` so the live gate is contract review, not choosing the next bounded increment.

No code implementation, provider edit, state consumption, physical StateBundle read, StateReplayFeed, production, downstream, full 2005-2026 backtest or execution-realism claim was introduced.

## 2026-07-29 | Deterministic fill simulator V0.1 implementation

- Added `src/tsis_backtest/execution/` with deterministic fill simulator contracts and engine.
- Implemented the BT-GATE-009 authorized scope only: `MARKET_PROXY`, `LIMIT`, `STOP_MARKET_PROXY`, `FULL_FILL_ONLY`, `DAY`, bar-based profile, deterministic slippage, deterministic costs and canonical outcomes.
- Added `tests/unit/test_deterministic_fill_simulator.py`.
- Verification: `$env:PYTHONPATH='src'; python -B -m unittest discover -s tests` -> 91 tests OK.
- Generated acceptance run `runs/deterministic_fill_simulator_v0_1_acceptance_v0_2` with manifests, outcomes, fills, costs, determinism report, validation report and artifact hashes.
- Preserved prohibitions on partial fills, quote-aware fills, borrow/locates, StateReplayFeed, Market State, Event State and edge claims.

State after this increment:

```text
DETERMINISTIC_FILL_SIMULATOR_V0_1 = IMPLEMENTED_PENDING_ACCEPTANCE_REVIEW
BT-GATE-010 = IMPLEMENTED_PENDING_ACCEPTANCE_REVIEW
CODE_IMPLEMENTATION = IMPLEMENTED_FOR_DETERMINISTIC_FILL_SIMULATOR_V0_1_ONLY
```

## 2026-07-29 BT-GATE-010 Acceptance Evidence Correction

        Regenerated acceptance evidence for `DETERMINISTIC_FILL_SIMULATOR_V0_1`.

        - Acceptance run: `runs/deterministic_fill_simulator_v0_1_acceptance_v0_3`
        - Required outcome coverage: PASS
        - Package-reproducible simulator subset: 30 tests OK
        - Full repository tests: 91 OK
        - StateReplayFeed and Market/Event State consumption remain NOT_AUTHORIZED.

## 2026-07-29 BT-GATE-010 Package Reproducibility Correction

        Corrected package-test reproducibility without changing simulator semantics.

        - `tsis_backtest.replay.__init__` now imports `HistoricalReplayFeed` lazily.
        - `python -B RUN_INCLUDED_TESTS.py` no longer requires `pyarrow` for simulator-only tests.
        - Acceptance run remains `deterministic_fill_simulator_v0_1_acceptance_v0_3`.
        - BT-GATE-010 remains `IMPLEMENTED_PENDING_ACCEPTANCE_REVIEW`.

## 2026-07-29 | Gate granularity and development velocity policy

- Added a normative policy to `AGENTS.md`: one gate equals one scientifically usable capability.
- Documented that minor fixes to imports, packaging, manifests, tests or evidence must remain inside the currently open capability gate.
- Added `docs/00_system/BACKTEST_ENGINE_ROADMAP.md` with the preferred next macrogates: `BT-GATE-011`, `BT-GATE-012` and `BT-GATE-013`.
- Added `docs/00_system/GOVERNANCE_OPERATING_MODEL.md` to define the operating rule against microgates.
- Preserved state-consumption restrictions: `StateReplayFeed`, Market State and Event State remain not authorized.

## 2026-07-29 | BT-GATE-010 administrative closure and BT-GATE-011 start

        - Closed `BT-GATE-010` as `CLOSED_PASS_IMPLEMENTATION_ACCEPTED`.
        - Recorded `DETERMINISTIC_FILL_SIMULATOR_V0_1 = IMPLEMENTED_AND_ACCEPTED`.
        - Started `BT-GATE-011 = SINGLE_STRATEGY_END_TO_END_BACKTEST` as contract proposal pending owner approval.
        - Implementation of BT-GATE-011 remains not authorized until the integral contract is approved once.
        - Preserved StateReplayFeed, Market State, Event State and provider restrictions.

## 2026-07-29 | BT-GATE-011 single-strategy end-to-end implementation

```text
BT-GATE-011 = IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED
run_id = bt_gate_011_open_short_close_qg5_v0_1
validation_status = PASS
engine_suite = 95 tests OK
NEXT_OWNER_REVIEW = FINAL_GATE_ACCEPTANCE_ONLY
```

Implemented path:

```text
StrategySpec -> HistoricalReplayFeed -> point-in-time decisions -> ExecutionOrder -> DeterministicFillSimulator V0.1 -> accounting -> Trade Ledger -> equity curve -> Unified Run Manifest
```

The run remains `ENGINE_VALIDATION_RUN`, `EDGE_EVIDENCE = NOT_AUTHORIZED`, `ECONOMIC_REALISM = INCOMPLETE`.

## 2026-07-29 | BT-GATE-011 Corrections For Final Acceptance Review

```text
BT-GATE-011 = IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW
PACKAGE_TEST_REPRODUCIBILITY = PASS
END_TO_END_RUN_REPRODUCIBILITY = PASS_WITH_PORTABLE_QG5_FIXTURE
EVENT_LOOP_INTEGRATION = PROVEN_BY_ONLINE_REPLAY_COORDINATOR_V0_1
ENGINE_TEST_SUITE = 99 tests OK
```

- Added a portable QG5 acceptance fixture under `tests/fixtures/bt_gate_011_qg5_portable`.
- Updated the runner to coordinate orders through `ONLINE_REPLAY_COORDINATOR_V0_1`.
- Added `event_loop_trace.json` to the run artifacts.
- Added tests for no future event access and truncated datasets not redefining close.
- Preserved StateReplayFeed, Market State, Event State and provider restrictions.

## 2026-07-29 | BT-GATE-011 causal EventLoop correction

```text
BT-GATE-011 = IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW
ONLINE_EVENT_DRIVEN_CAUSALITY = CORRECTED
ORDERS_PRE_REGISTERED_BEFORE_REPLAY = PASS
ORDER_CREATED_DURING_EVENT_PROCESSING = false
ACCOUNTING_APPLIED_INSIDE_EVENT_LOOP = PASS
ENGINE_TEST_SUITE = 99 tests OK
```

The gate remains open only for final owner acceptance review.

## 2026-07-29 | BT-GATE-011 closed and BT-GATE-012 contract draft opened

```text
BT-GATE-011_FINAL_ACCEPTANCE_REVIEW = PASS
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED_AND_ACCEPTED
FINAL_OWNER_REVIEW = ACCEPTED
ZIP_SHA256 = 33376d73eeba6963d63bffbbf782c2a08e67ed741f6d16675fe6cc4cc44e8dfa

BT-GATE-012 = CONTRACT_DRAFT_PENDING_OWNER_REVIEW
BT-GATE-012_IMPLEMENTATION = NOT_AUTHORIZED
```

Created:

```text
docs/00_system/12_BT_GATE_012_MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE_CONTRACT_V0_1.md
```

No code, tests, runs, provider, Market State, Event State or StateReplayFeed were modified by this administrative closure.

## 2026-07-29 | BT-GATE-012 contract review findings corrected

```text
BT-GATE-012 = CONTRACT_DRAFT_CORRECTED_PENDING_OWNER_REVIEW
BT-GATE-012_IMPLEMENTATION = NOT_AUTHORIZED
GLOBAL_REPLAY_ORDER_V0_1 = DEFINED
ACTIVE_ORDER_EVALUATION_ORDER_V0_1 = DEFINED
PORTFOLIO_EQUITY_POLICY_V0_1 = DEFINED
SESSION_POLICY = REGULAR_ONLY_XNYS_V0_1
CAPITAL_CONTENTION_CLAIM = NOT_AUTHORIZED
```

Corrected:

```text
docs/00_system/12_BT_GATE_012_MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE_CONTRACT_V0_1.md
```

No code, tests, runs, provider, Market State, Event State or StateReplayFeed were modified.
## 2026-07-29 | BT-GATE-012 final contract review corrections

```text
BT-GATE-012 = CONTRACT_DRAFT_CORRECTED_PENDING_OWNER_REVIEW
BT-GATE-012_IMPLEMENTATION = NOT_AUTHORIZED
PORTFOLIO_VALUATION_PRICE_FIELD = close
CALENDAR_AUTHORITY = TSIS_PORTABLE_SESSION_CALENDAR_SNAPSHOT_V0_1
SESSION_CALENDAR_SNAPSHOT_SHA256 = REQUIRED
BT-GATE-011 evidence hash = f5bccea7d6f5f6eff0647a66d4827a011e5854af9644a8854b10135da883cc2b
BT-GATE-011 engine_suite = 99 tests OK
```

No code, tests, runs, provider, Market State, Event State or StateReplayFeed were modified.

## 2026-07-29 | BT-GATE-012 owner contract review accepted

```text
BT-GATE-012_OWNER_CONTRACT_REVIEW = PASS
BT-GATE-012 = AUTHORIZED_FOR_CONTINUOUS_IMPLEMENTATION
BT-GATE-012_IMPLEMENTATION = AUTHORIZED
EXECUTION_MODE = CONTINUOUS_UNTIL_FINAL_ACCEPTANCE_PACKET
NO_INTERMEDIATE_MICROGATES = AUTHORIZED
NEXT_OWNER_REVIEW = FINAL_GATE_ACCEPTANCE_ONLY_UNLESS_MATERIAL_SCOPE_OR_SEMANTIC_CHANGE
IMPLEMENTATION_ACCEPTANCE = NOT_YET_GRANTED
AUTHORIZATION_PACKET = bt_gate_012_contract_review_packet_20260729T164056Z.zip
AUTHORIZATION_PACKET_SHA256 = b8bb2e5641db2cd3aee8ede94d571a1176479e27cbdf5a05602e1111163b6f40
```

StateReplayFeed, StateBundle physical reads, Market State, Event State and provider modification remain `NOT_AUTHORIZED`.

## 2026-07-29 | BT-GATE-012 implementation evidence prepared

- Implemented the multi-symbol, multi-session portfolio slice under the accepted BT-GATE-012 contract.
- Added `src/tsis_backtest/portfolio/`, `tests/unit/test_portfolio_slice_runner.py`, `configs/runs/bt_gate_012_multi_symbol_multi_session_qg5_v0_1.json`, `scripts/run_bt_gate_012_portfolio_slice.py`, `scripts/package_bt_gate_012_acceptance.py`, and `docs/00_system/13_BT_GATE_012_MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE_ACCEPTANCE_PACKET_V0_1.md`.
- Generated canonical run `runs/bt_gate_012_multi_symbol_multi_session_qg5_v0_1`.
- Recorded `ENGINE_TEST_SUITE = 106 tests OK` and `BT-GATE-012_FOCUSED_TESTS = 7 portfolio tests OK`.
- Recorded `BT-GATE-012_VALIDATION_STATUS = PASS`, `BT-GATE-012_DETERMINISM_STATUS = PASS`, and `BT-GATE-012_DETERMINISTIC_OUTPUT_HASH = 414aceb2bc80836f8fa821cd4d14071e54c86f3c7855c0a34c82ffd8b1c79182`.
- Set `BT-GATE-012 = IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW` and `IMPLEMENTATION_ACCEPTANCE = PENDING_FINAL_OWNER_REVIEW` pending final owner/external review.
- Preserved StateReplayFeed, StateBundle physical reads, Market State, Event State and provider modification as `NOT_AUTHORIZED`.

## 2026-07-29 | BT-GATE-012 final acceptance closed

- Registered `BT-GATE-012_FINAL_OWNER_REVIEW = PASS`.
- Closed `BT-GATE-012 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED`.
- Set `IMPLEMENTATION_ACCEPTANCE = ACCEPTED` and `BT-GATE-012_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED`.
- Final packet: `bt_gate_012_portfolio_slice_acceptance_packet_20260729T172450Z.zip`.
- Final packet SHA-256: `4181d42a61a66ce8f71b7ce3156bff586c756154a2b86c95676bc9efe8c87975`.
- Deterministic output hash: `414aceb2bc80836f8fa821cd4d14071e54c86f3c7855c0a34c82ffd8b1c79182`.
- Engine suite: 106 tests OK.
- End-to-end validation, accounting reconciliation, determinism and boundary preservation: PASS.
- `BT-GATE-013` remains not opened; StateReplayFeed, StateBundle physical reads, Market State, Event State and provider modification remain `NOT_AUTHORIZED`.

## 2026-07-29 | BT-GATE-013 boundary corrected

```text
BT-GATE-013_NAME = PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
BT-GATE-013_NEW_BOUNDARY = PHYSICAL_013_ROWS_TO_ACCEPTED_REPLAY_ENGINE
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
SMALL_CAPS_RIGOROUS_RESEARCH_RUNNER = FUTURE_GATE_FAMILY_NOT_YET_OPEN
```

Rationale: BT-GATE-013 must cross exactly one new boundary after BT-GATE-012: from accepted portable fixture replay to reproducible physical historical data. It must prove physical row lineage, timestamp availability, session legality, replay determinism and accounting preservation before any small-caps tradability, SSR, borrow, locates, liquidity/capacity, batch research, DSR/PBO/CSCV or edge-evidence gates are opened.

Central rule preserved for future gates:

```text
mechanically executable order != actually shortable security != economically valid trade != demonstrated edge
```

The next work is contract definition only:

```text
docs/00_system/14_BT_GATE_013_PHYSICAL_HISTORICAL_REPLAY_SLICE_CONTRACT_V0_1.md
Status = HISTORICAL_CONTRACT_DRAFT_PENDING_OWNER_REVIEW_SUPERSEDED_BY_CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
Implementation = NOT_AUTHORIZED
```

## 2026-07-29 | BT-GATE-013 contract draft placed in canonical backtester docs

```text
BT-GATE-013 = PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
BT-GATE-013_CONTRACT = HISTORICAL_CONTRACT_DRAFT_PENDING_OWNER_REVIEW_SUPERSEDED_BY_CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
CONTRACT_ARTIFACT = docs/00_system/14_BT_GATE_013_PHYSICAL_HISTORICAL_REPLAY_SLICE_CONTRACT_V0_1.md
```

The contract draft was copied into the canonical backtester document location. This does not authorize implementation, Market State consumption, Event State consumption, StateReplayFeed, provider modification or full 2005-2026 execution.

## 2026-07-29 | BT-GATE-013 corrected contract after read-only review

```text
READ_ONLY_REVIEW = ACCEPTED
REVIEW_RESULT = CONTRACT_CORRECTIONS_REQUIRED
BT-GATE-013_CONTRACT = CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
PROVIDER_EVIDENCE_REQUIRED = false
```

Applied contractual corrections only: source identity layering, exact physical binding,
derived time-field semantics without native `source_as_of_utc`, stable source row locator,
portable relative paths, repair/provenance field restrictions and living-surface cleanup.
No code, tests, configs, scripts, runs, data, provider, Market State, Event State or StateReplayFeed were modified.

## 2026-07-29 | BT-GATE-013 corrected contract after read-only review

```text
READ_ONLY_REVIEW = ACCEPTED
REVIEW_RESULT = CONTRACT_CORRECTIONS_REQUIRED
BT-GATE-013_CONTRACT = CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
PROVIDER_EVIDENCE_REQUIRED = false
```

Applied contractual corrections only: source identity layering, exact physical binding,
derived time-field semantics without native `source_as_of_utc`, stable source row locator,
portable relative paths, repair/provenance field restrictions and living-surface cleanup.
No code, tests, configs, scripts, runs, data, provider, Market State, Event State or StateReplayFeed were modified.


## 2026-07-29 | BT-GATE-013 implementation evidence prepared

- Implemented `PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1` against the accepted BT-GATE-013 contract.
- Added `src/tsis_backtest/physical_replay/`, `tests/unit/test_physical_replay_adapter.py`, `configs/runs/bt_gate_013_physical_historical_replay_slice_v0_1.json`, `scripts/run_bt_gate_013_physical_replay_slice.py`, and portable fixture `tests/fixtures/bt_gate_013_physical_qg5_slice/`.
- Generated canonical run `runs/bt_gate_013_physical_historical_replay_slice_v0_1`.
- Recorded `ENGINE_TEST_SUITE = 119 tests PASS`, `BT-GATE-013_FOCUSED_TESTS = 13 physical replay tests PASS`, `BT-GATE-013_VALIDATION_STATUS = PASS`, and `BT-GATE-013_DETERMINISTIC_OUTPUT_HASH = ede33c7037a0bd08670423a4ac05b4836aa1472163027c7a86e883fca0b5c019`.
- Set `BT-GATE-013 = IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW`; final acceptance remains pending external review.
- Preserved StateReplayFeed, StateBundle physical reads, Market State, Event State, provider modification, full 2005-2026 backtest, optimization and edge claims as not authorized.

## 2026-07-30 | BT-GATE-013 corrected acceptance evidence regenerated

- Corrected the BT-GATE-013 acceptance evidence rejected under package SHA-256 `42421cbe0668c458b4559eadf0aad44f2ec8f00a64956622920a384586c1fe1d`.
- The physical replay adapter now consumes `portable_fixture_manifest_sha256`, validates `FIXTURE_MANIFEST.json`, verifies the validation manifest identity, and compares each authorized Parquet file by SHA-256 and size before reading.
- `negative_derivative_report.json` is generated from 15 executed derivative checks, including source hash mismatch, source mutation during read, duplicate/conflicting physical bars, temporal availability violation, calendar timezone contract and truncated session failures.
- `final_manifest.json` now declares the section 16 evidence directly, including validation/calendar manifests, source files, timestamp and availability ranges, component versions, output hashes and negative-test aggregate results.
- Recorded `ENGINE_TEST_SUITE = 119 tests PASS`, `BT-GATE-013_FOCUSED_TESTS = 13 physical replay tests PASS`, and deterministic output hash `ede33c7037a0bd08670423a4ac05b4836aa1472163027c7a86e883fca0b5c019`.
- `BT-GATE-013` remains `IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW`; do not record `CLOSED_PASS` until external final review accepts the corrected package.

## 2026-07-30 | BT-GATE-013 targeted contract-conformance corrections

- Executed exactly `NEGATIVE_01` through `NEGATIVE_15` from contract section 19; relocation, physical-row reordering and full replay gap semantics now produce executed evidence.
- Retained fixture/validation manifest checks as five supplemental metadata and identity cases.
- Resolved `portfolio_run_manifest_hash` against the manifest actually written with `output_artifacts`, with artifact-reference validation.
- Removed repair metadata from operational `MarketDataBar1m.quality_flags`; repair fields remain only in `physical_lineage`.
- Added hash-before/hash-after mutation protection for fixture manifest, validation manifest and calendar.
- Recorded `ENGINE_TEST_SUITE = 119 tests PASS`, `BT-GATE-013_FOCUSED_TESTS = 13 PASS`, and deterministic output hash `ede33c7037a0bd08670423a4ac05b4836aa1472163027c7a86e883fca0b5c019`.
- `BT-GATE-013` remains `IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW`; `CLOSED_PASS` is not authorized before external acceptance.

## 2026-07-30 | BT-GATE-013 scientific manifest portability correction

- Canonicalized `configuration_snapshot.json` before artifact hashing: `output_root` and `session_calendar_snapshot_path` are portable relative paths.
- Recomputed the written portfolio manifest after canonical configuration hashing and preserved final-manifest resolution against that artifact.
- Extended `NEGATIVE_13` to execute and write two runs under different absolute roots and compare configuration, portfolio and final scientific manifests.
- Recorded `NEGATIVE_13 = PASS_WITH_IDENTICAL_SCIENTIFIC_HASH`, `ENGINE_TEST_SUITE = 119 tests PASS`, and deterministic output hash `ede33c7037a0bd08670423a4ac05b4836aa1472163027c7a86e883fca0b5c019`.
- `BT-GATE-013` remains `IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW`; final closure remains unauthorized pending external acceptance.


## 2026-07-30 | BT-GATE-013 final external acceptance

```text
BT-GATE-013_FINAL_EXTERNAL_REVIEW = PASS
BT-GATE-013 = CLOSED_PASS_PHYSICAL_HISTORICAL_REPLAY_ACCEPTED
BT-GATE-013_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED
FINAL_ACCEPTANCE_PACKET_SHA256 = 4c89a8279ee7a999fc2774cbac06e15d8779ba347aaf28aa1d9fd7bba2895f9d
DETERMINISTIC_OUTPUT_HASH = ede33c7037a0bd08670423a4ac05b4836aa1472163027c7a86e883fca0b5c019
CLEAN_EXTRACTIONS = 2
ENGINE_TEST_SUITE_A_B = 119 tests PASS
RUN_END_TO_END_A_B = PASS
CURRENT_GATE = NONE
NEXT_GATE = NOT_OPEN
```

This administrative closure does not authorize StateReplayFeed, Market State, Event State, StateBundle reads, provider modification, the full 2005-2026 backtest, Small-Caps Rigorous Research Runner, optimization or edge claims.
## 2026-07-30 - BT-GATE-014 non-physical consumer phase

- Adopted provider handoff by exact SHA-256 without reusing consumed physical authorization.
- Implemented typed core-four `BoundedMarketStateAvailable`, immutable PIT store and bounded probe.
- Executed 15 positive and 33 negative contract cases; full engine suite: 128 tests PASS.
- Physical provider rows read: 0. Next requirement: new single-use physical authorization.
## 2026-07-30 - BT-GATE-014 Phase B external corrections

- Corrected temporal derivation, stored-at visibility, 1:1 row-sidecar join and frozen authority validation.
- Bound all synthetic inputs by hash/size and replaced overdeclared permutation/root tests with executed evidence.
- Added six external-review regressions; included tests: 15 PASS; complete suite: 134 PASS.
- Physical read remains NOT_EXECUTED; new single-use physical authorization remains NOT_AUTHORIZED pending external re-review.
## 2026-07-30 - BT-GATE-014 second Phase B correction round

- Required all sidecar identity fields from section 14 and rejected missing fields.
- Added defensive store validation against forged/unvalidated events.
- Enforced closed fixture inventory, mandatory config path and exact request/config authority equality.
- Replaced three local skips with portable QG5 fixtures.
- External-review regressions: 11 PASS; included tests: 20 PASS; complete suite: 139 PASS, 0 skipped.
- Physical Market State rows remain unread; single-use authorization remains NOT_AUTHORIZED.
## 2026-07-30 - BT-GATE-014 third Phase B correction round

- MarketStateStore now accepts only a typed validation wrapper with receipt bound to event bytes and frozen authority.
- Store rejects raw events and altered post-validation events; sidecar profile, policy, schema and identifiers are enforced.
- Remaining governance current-state block marked historical/superseded.
- ZIP manifest status corrected and package-local JSON counts made reproducible.
- External-review regressions: 13 PASS; included tests: 22 PASS; complete suite: 141 PASS, 0 skipped.
- Physical Market State rows remain unread; single-use authorization remains NOT_AUTHORIZED.



## 2026-07-30 - BT-GATE-014 contract-conformance correction round

- Bound provider package identity directly to compiled frozen hashes, adoption
  before/after values, configuration pins and nested bytes.
- Replaced event-only sealing with atomic raw-row/sidecar validation and receipt.
- Adopted provider component status `available` while preserving row status
  `available_for_decision_replay`.
- Separated consumed synthetic sidecar hash from provider sidecar authority hash.
- Added an independent, hashed synthetic market-bar fixture.
- Corrected POSITIVE_10, POSITIVE_12, NEGATIVE_18 and NEGATIVE_31 evidence.
- Tests: 146/146 PASS; included BT-GATE-014 tests: 27/27 PASS; external-review
  regressions: 18/18 PASS; skipped: 0.
- Physical Market State rows read: 0. New single-use authorization remains
  NOT_AUTHORIZED.

## 2026-07-30 - BT-GATE-014 final Phase B contract-conformance hardening

- Unified row-sidecar bijection, validation and sealing in the actual runner;
  duplicate sidecars can no longer be overwritten by dictionary construction.
- Added recursive immutability and raw/parsed consistency checks for audit
  lineage.
- Closed row, sidecar, component and fixture-document schemas; enforced strict
  JSON without `NaN`, infinities or duplicate keys.
- Bound validation receipts to dataset, provider authority, structural schema
  and consumed sidecar identity; store insertion independently reconstructs
  fingerprint and candidate identity.
- Canonicalized all Market State output timestamps to UTC `Z`.
- Added nine external-review regressions and governance cross-surface hash
  validation.
- Tests: 155/155 PASS; included BT-GATE-014 tests: 36/36 PASS;
  external-review regressions: 27/27 PASS; skipped: 0.
- Deterministic output hash:
  `bb499dd82edf7b7fb165aa9d5e088468e946138c16b1ffce89a4bbb74b8bd7fd`.
- Scientific manifest hash:
  `25f80ee5c11aadd2838fbc8a54aa7b182ed2583fc49f1ba78c1cb26e235456ee`.
- Physical Market State rows read: 0. New single-use authorization remains
  NOT_AUTHORIZED.

## 2026-07-30 - BT-GATE-014 Phase B external re-review accepted

- Recorded `BT-GATE-014_PHASE_B_EXTERNAL_RE_REVIEW = PASS`.
- Accepted the bounded non-physical consumer implementation only.
- Adopted `bt_gate_014_non_physical_consumer_acceptance_packet_20260730T150834Z.zip` with SHA-256 `6881b6b485f7e6aed6744e609b1e61f66073dc3e20c0e807245a3b38a35f7645`.
- Preserved deterministic output `bb499dd82edf7b7fb165aa9d5e088468e946138c16b1ffce89a4bbb74b8bd7fd` and scientific manifest `25f80ee5c11aadd2838fbc8a54aa7b182ed2583fc49f1ba78c1cb26e235456ee`.
- Set `BT-GATE-014 = PHASE_B_ACCEPTED_PENDING_SINGLE_USE_PHYSICAL_AUTHORIZATION`.
- Set `NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION = ELIGIBLE_NOT_ISSUED`.
- Preserved `PHYSICAL_CONSUMER_READ = NOT_EXECUTED`, `PHYSICAL_STATE_ROWS_READ = 0`, and `BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED`.

## 2026-07-30 - BT-GATE-014 single-use physical authorization issued

- Bound executable binding prepared and tested without Market State physical reads.
- `NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION = AUTHORIZED_NOT_CONSUMED`.
- `PHYSICAL_CONSUMER_READ = NOT_EXECUTED`; `PHYSICAL_STATE_ROWS_READ = 0`.
- BT-GATE-014 remains open and CLOSED_PASS remains unauthorized.

## 2026-07-30 - BT-GATE-014 physical authorization V0.2

- V0.1 superseded unconsumed after pre-execution review failure.
- V0.2 binds the accepted consumer pipeline, nine frozen inputs and complete success/failure evidence.
- `V0_2 = AUTHORIZED_NOT_CONSUMED`; physical rows read remain zero.

## 2026-07-30 - BT-GATE-014 physical authorization V0.3

- Preserved V0.1 and V0.2 as superseded, unconsumed historical authorizations.
- Corrected the common causal key so equal-timestamp delivery is exactly `BAR → STATE`.
- Armed and fsynced `failure_manifest.json` before the atomic authorization transition.
- Covered consumption, receipt-writing, second-use and state-transition failures with fail-closed tests.
- Bound V0.3 to the exact two ACIU rows, nine provider inputs, two adopted handoffs and complete success/failure evidence.
- `V0_3 = AUTHORIZED_NOT_CONSUMED`; no physical Market State row was opened and `BT-GATE-014` remains open.

## 2026-07-30 - BT-GATE-014 V0.3 consumed failure and V0.4 preparation

- Preserved V0.3 receipt, pre-run and failure evidence; V0.3 is CONSUMED_FAILED_FINAL and cannot be reused.
- Effective physical progress was one file and two rows; zero Market State events, orders, fills or PnL.
- Corrected restriction equivalence to exact-set semantics with duplicate/omission/extra rejection while preserving raw JSON.
- Added durable physical progress telemetry and failure-manifest propagation.
- Prepared V0.4 with the identical two-row ACIU scope; physical execution remains NOT_APPROVED pending external pre-execution review.
- Focused V0.4 suite: 17 PASS (14 functional V0.4 + 3 canonical). Full repository suite: 197 PASS.

## 2026-07-30 - BT-GATE-014 V0.4 R2 preconsumption failure and R3 correction

- The externally approved R2 command failed during closed configuration validation before authorization consumption, run-directory creation or physical access.
- Cause: PRODUCTION_SPEC retained the V0.3 barrier hash while V0.4 configuration correctly pinned the V0.4 barrier hash.
- V0.4 remained AUTHORIZED_NOT_CONSUMED; no Parquet was opened and no physical row was read.
- Corrected the literal and added a canonical PRODUCTION_SPEC/configuration regression.
- R3 requires a new external pre-execution PASS. Focused: 18 PASS. Full suite: 198 PASS.

## 2026-07-30 - BT-GATE-014 V0.4 consumed physical failure

- V0.4 consumed exactly one authorized run and read one Parquet / two ACIU rows.
- Fail-closed result: FAIL_MARKET_STATE_RESTRICTION_PROPAGATION before event emission or store insertion.
- Physical rows expose 26 design/provenance restrictions; sidecar/components expose four bounded-consumption restrictions. These are distinct governed domains, not reordered equivalent sets.
- Zero Market State events, observations, strategy decisions, orders, fills and PnL. Provider modification remains false.
- V0.4 cannot be reused. A contract correction and a separately audited future authorization are required.
