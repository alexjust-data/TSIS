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

# Changelog

## 2026-07-29 — Integrated governance baseline V0.1.1

- Integrated the pre-existing `14_BACKTEST_ENGINE` guide and root documentation.
- Preserved all pre-governance root files under `11_HISTORICAL_SNAPSHOTS` as non-authoritative evidence.
- Consolidated the live agent contract under the single canonical name `AGENTS.md`.
- Incorporated the valid legacy operating rules into `LOCAL_RULES.md`.
- Updated the guide index and historical next-step pointers to the current execution-contract review gate.
- Registered `00_CTO_APPLIED_ARCHITECTURE` as external context only.
- Registered `FUTURE_PROVIDER_REGISTRY_INTEGRATION = NOT_AUTHORIZED`.
- Kept StateReplayFeed, physical StateBundle reads and state-driven backtests blocked.

The detailed 2026-07-28 construction history remains available at:

```text
11_HISTORICAL_SNAPSHOTS/
2026-07-28_PRE_GOVERNANCE_ROOT/
CHANGELOG_HISTORY_SOURCE.md
```

It is provenance, not a competing live-state document.

## 2026-07-29 — Initial governance baseline V0.1

- Created the backtest-engine authority root from an audit of the 92-entry implementation snapshot.
- Registered 16 decisions, 23 policies, 8 gates and 8 exceptions/limitations.
- Bound closed capabilities to implementation, tests and preserved runs.
- Preserved all current non-claims.
- Recorded the execution-contract header contradiction as open documentation debt.
- Kept deterministic fill implementation and all state consumption unauthorized.
## 2026-07-29 — Execution contract governance sync correction

- Corrected the source execution-contract header in `02_TSIS_BACKTEST_ENGINE/docs/00_system/07_EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1.md` to match `CORRECTED_DRAFT_READY_FOR_REVIEW`.
- Updated `BT-EXC-001` to `DOCUMENTARY_CONTRADICTION_CORRECTED_PENDING_INDEPENDENT_REVIEW` without closing it.
- Preserved `BT-GATE-006 = OPEN_REVIEW_REQUIRED` and `CODE_IMPLEMENTATION = NOT_AUTHORIZED`.
- Regenerated `PACKAGE_MANIFEST.json` over the controlled canonical set and added `08_GATES_AND_REVIEWS/GOVERNANCE_UPDATE_PROTOCOL.md`.
- Re-ran governance validation: JSON parse, register references, duplicate IDs, manifest coverage/hash integrity and State Provider restrictions all passed.
- Independent review remains not recorded; `DETERMINISTIC_FILL_SIMULATOR_V0_1` remains not authorized.
## 2026-07-29 — Execution contract semantic review findings corrected

- Recorded independent semantic review as `COMPLETED_WITH_FINDINGS` for `BT-GATE-006`.
- Corrected `docs/00_system/07_EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1.md` for exact bar eligibility, LIMIT/STOP first evaluable bars, V0.1 tick policy, nonpositive fill rejection, slippage formulas, cost formulas and canonical outcome precedence.
- Added decisions `BT-EXEC-006`, `BT-EXEC-007` and `BT-EXEC-008`.
- Added policies `BT-POL-EXEC-007` through `BT-POL-EXEC-011`.
- Updated `BT-CAP-EXECUTION-CONTRACT` traceability to `CORRECTED_DRAFT_PENDING_SEMANTIC_RE_REVIEW`.
- Updated `BT-EXC-001` to `DOCUMENTARY_CONTRADICTION_CORRECTED` and added `BT-EXC-009 = CORRECTED_PENDING_INDEPENDENT_REVIEW_ACCEPTANCE`.
- Kept `BT-GATE-006 = OPEN_REVIEW_REQUIRED`; remaining blocker is semantic correction re-review not recorded.
- Kept `CODE_IMPLEMENTATION = NOT_AUTHORIZED` and `DETERMINISTIC_FILL_SIMULATOR_V0_1_AUTHORIZATION = NOT_OPEN`.

No code implementation, executable tests, runs, State Provider changes, Market/Event State consumption, StateReplayFeed, production, downstream or realism claim was introduced.
## 2026-07-29 — Execution contract residual semantic findings corrected

- Recorded independent semantic re-review as `COMPLETED_WITH_RESIDUAL_FINDINGS` for `BT-GATE-006`.
- Corrected residual finding 1 by separating `EVALUATION_OUTCOME` from `TERMINAL_ORDER_OUTCOME`; `NO_FILL_GAP` and `NO_FILL_MISSING_PRICE` remain recorded even if the order later expires.
- Corrected residual finding 2 by setting `ambiguous_bar_policy = FAIL_AMBIGUOUS_BAR_ONLY` and reserving `PESSIMISTIC = RESERVED_NOT_IMPLEMENTED`.
- Added gross notional precision: `gross_notional = abs(fill_quantity) * fill_price`.
- Added decisions `BT-EXEC-009`, `BT-EXEC-010` and `BT-EXEC-011`.
- Added policies `BT-POL-EXEC-012` through `BT-POL-EXEC-014`.
- Updated `BT-CAP-EXECUTION-CONTRACT` to `CORRECTED_DRAFT_PENDING_FINAL_SEMANTIC_REVIEW`.
- Updated `BT-EXC-009` to `CORRECTED_RE_REVIEWED_WITH_RESIDUAL_FINDINGS_PENDING_FINAL_REVIEW`.
- Kept `BT-GATE-006 = OPEN_REVIEW_REQUIRED`; remaining blocker is final semantic review not recorded.
- Kept `CODE_IMPLEMENTATION = NOT_AUTHORIZED` and `DETERMINISTIC_FILL_SIMULATOR_V0_1_AUTHORIZATION = NOT_OPEN`.

No code implementation, executable tests, runs, State Provider changes, Market/Event State consumption, StateReplayFeed, production, downstream or realism claim was introduced.

## 2026-07-29 - Ambiguous-Bar Semantic Contradiction Corrected

- Corrected the final residual contradiction in `07_EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1.md`.
- Canonicalized `FAIL_AMBIGUOUS_BAR` as the V0.1 `EVALUATION_OUTCOME`.
- Mapped `FAIL_AMBIGUOUS_BAR` to `TERMINAL_ORDER_OUTCOME = REJECTED_BY_CONTRACT`.
- Kept `PESSIMISTIC = RESERVED_NOT_IMPLEMENTED`.
- Kept `BT-EXC-009` open pending final focused semantic review.
- Kept `BT-GATE-006 = OPEN_REVIEW_REQUIRED` and `CODE_IMPLEMENTATION = NOT_AUTHORIZED`.

## 2026-07-29 - Supported Outcome Enumeration Corrected

- Replaced the generic `Supported V0.1 outcomes` list with separate `EVALUATION_OUTCOME` and `TERMINAL_ORDER_OUTCOME` enumerations.
- Added `FAIL_AMBIGUOUS_BAR` to the supported V0.1 evaluation outcomes.
- Preserved `FAIL_AMBIGUOUS_BAR -> TERMINAL_ORDER_OUTCOME = REJECTED_BY_CONTRACT`.
- Kept `BT-EXC-009 = CORRECTED_PENDING_FINAL_ENUMERATION_REVIEW`.
- Kept `BT-GATE-006 = OPEN_REVIEW_REQUIRED` and `CODE_IMPLEMENTATION = NOT_AUTHORIZED`.

## 2026-07-29 - BT-GATE-006 Closed Pass

- Recorded `FINAL_ENUMERATION_REVIEW = PASS` for `EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1`.
- Closed `BT-EXC-009` as `CLOSED_CORRECTED_AND_FINAL_REVIEW_ACCEPTED`.
- Closed `BT-GATE-006` as `CLOSED_PASS`.
- Opened `DETERMINISTIC_FILL_SIMULATOR_V0_1_AUTHORIZATION` / `BT-GATE-009` for decision only.
- Kept `CODE_IMPLEMENTATION = NOT_AUTHORIZED`.
- Preserved all State Provider, Market State, Event State and StateReplayFeed restrictions.

## 2026-07-29 - BT-GATE-009 Authorization Granted

- Registered external final review PASS for `08_DETERMINISTIC_FILL_SIMULATOR_V0_1_AUTHORIZATION.md`.
- Closed `BT-GATE-009` as `CLOSED_PASS_AUTHORIZATION_GRANTED`.
- Set `CODE_IMPLEMENTATION = AUTHORIZED_FOR_DETERMINISTIC_FILL_SIMULATOR_V0_1_ONLY`.
- Opened `BT-GATE-010 = DETERMINISTIC_FILL_SIMULATOR_V0_1_IMPLEMENTATION_AND_ACCEPTANCE`.
- Preserved all prohibitions on StateReplayFeed, StateBundle physical reads, Market State, Event State, partial fills, quote-aware fills, borrow/locates and edge claims.

## 2026-07-29 - BT-GATE-010 Implementation Pending Acceptance Review

- Registered bounded implementation of `DETERMINISTIC_FILL_SIMULATOR_V0_1`.
- Added traceability capability `BT-CAP-DETERMINISTIC-FILL-SIMULATOR`.
- Recorded engine suite `91 tests OK` and acceptance run `runs/deterministic_fill_simulator_v0_1_acceptance_v0_2`.
- Kept `BT-GATE-010 = IMPLEMENTED_PENDING_ACCEPTANCE_REVIEW`; not closed yet.
- Preserved all State Provider, Market State, Event State, StateReplayFeed and prohibited execution-realism boundaries.

## 2026-07-29 BT-GATE-010 Acceptance Evidence Correction

        Regenerated deterministic fill simulator acceptance evidence without changing execution semantics.

        - Acceptance run: `deterministic_fill_simulator_v0_1_acceptance_v0_3`
        - Required EVALUATION_OUTCOME coverage: PASS
        - Required TERMINAL_ORDER_OUTCOME coverage: PASS
        - Full repository suite: 91 tests OK
        - Package-reproducible simulator subset: 30 tests OK
        - BT-GATE-010 remains IMPLEMENTED_PENDING_ACCEPTANCE_REVIEW.

## 2026-07-29 BT-GATE-010 Package Reproducibility Correction

        Corrected the residual external package reproducibility blocker for BT-GATE-010.

        - Semantic implementation review remains PASS.
        - Acceptance outcome coverage remains PASS.
        - Package-reproducible simulator tests now run without importing `pyarrow`.
        - BT-GATE-010 remains `IMPLEMENTED_PENDING_ACCEPTANCE_REVIEW`.

## 2026-07-29 BT-GATE-010 Administrative Closure And BT-GATE-011 Start

        BT-GATE-010 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
        DETERMINISTIC_FILL_SIMULATOR_V0_1 = IMPLEMENTED_AND_ACCEPTED
        IMPLEMENTATION_ACCEPTANCE = ACCEPTED

        BT-GATE-011 = SINGLE_STRATEGY_END_TO_END_BACKTEST
        BT-GATE-011_STATUS = CONTRACT_PROPOSAL_PENDING_OWNER_APPROVAL
        BT-GATE-011_IMPLEMENTATION = NOT_AUTHORIZED_UNTIL_OWNER_APPROVES_INTEGRAL_CONTRACT

## 2026-07-29 | Historical BT-GATE-011 Implementation Awaiting Final Acceptance Review

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED_AND_ACCEPTED
run_id = bt_gate_011_open_short_close_qg5_v0_1
validation_status = PASS
engine_suite = 95 tests OK
HISTORICAL_FINAL_OWNER_REVIEW_STATE = AWAITING_REVIEW_AT_TIME_OF_ENTRY_SUPERSEDED_BY_ACCEPTED
```

The run validates the engine path only:

```text
RUN_PURPOSE = ENGINE_VALIDATION_RUN
EDGE_EVIDENCE = NOT_AUTHORIZED
ECONOMIC_REALISM = INCOMPLETE
```

State Provider, Market State, Event State and StateReplayFeed restrictions remain closed.

## 2026-07-29 | BT-GATE-011 Corrective Acceptance Evidence

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
PACKAGE_TEST_REPRODUCIBILITY = PASS
END_TO_END_RUN_REPRODUCIBILITY = PASS_WITH_PORTABLE_QG5_FIXTURE
EVENT_LOOP_INTEGRATION = PROVEN_BY_ONLINE_REPLAY_COORDINATOR_V0_1
ENGINE_TEST_SUITE = 99 tests OK
HISTORICAL_FINAL_OWNER_REVIEW_STATE = AWAITING_REVIEW_AT_TIME_OF_ENTRY_SUPERSEDED_BY_ACCEPTED
```

State Provider, Market State, Event State and StateReplayFeed restrictions remain closed.

## 2026-07-29 | BT-GATE-011 causal EventLoop correction

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
ONLINE_EVENT_DRIVEN_CAUSALITY = CORRECTED
ORDERS_PRE_REGISTERED_BEFORE_REPLAY = PASS
ORDER_CREATED_DURING_EVENT_PROCESSING = false
ACCOUNTING_APPLIED_INSIDE_EVENT_LOOP = PASS
ENGINE_TEST_SUITE = 99 tests OK
```

The gate is closed after final owner acceptance review.

## 2026-07-29 | BT-GATE-011 closed and BT-GATE-012 contract draft opened

```text
BT-GATE-011_FINAL_ACCEPTANCE_REVIEW = PASS
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED_AND_ACCEPTED
FINAL_OWNER_REVIEW = ACCEPTED
ZIP_SHA256 = 33376d73eeba6963d63bffbbf782c2a08e67ed741f6d16675fe6cc4cc44e8dfa

BT-GATE-012 = CONTRACT_DRAFT_CORRECTED_PENDING_OWNER_REVIEW
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

`BT-GATE-013` is not a small-caps research runner. It is the physical historical replay bridge from `013_ohlcv_1m_quote_guarded` rows into the accepted replay/portfolio engine. Future small-caps rigorous research capability remains deferred until the physical bar boundary, Market/Event State consumption gates, scaling/batch gates, tradability/execution-realism gates and statistical validation gates are separately authorized.

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

```text
BT-GATE-013 = IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW
BT-GATE-013_IMPLEMENTATION = IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW
PHYSICAL_RUN = AUTHORIZED_ONLY_FOR_THE_FROZEN_ACCEPTANCE_SLICE_EXECUTED
IMPLEMENTATION_ACCEPTANCE = PENDING_FINAL_EXTERNAL_REVIEW
ENGINE_TEST_SUITE = 119 tests PASS
BT-GATE-013_VALIDATION_STATUS = PASS
BT-GATE-013_DETERMINISTIC_OUTPUT_HASH = ede33c7037a0bd08670423a4ac05b4836aa1472163027c7a86e883fca0b5c019
```

The gate is not closed. Final acceptance requires external review of the package. StateReplayFeed, Market State, Event State, StateBundle reads, provider modification, full 2005-2026 backtest, optimization and edge claims remain not authorized.

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

- Recorded the closed runner bijection, recursive immutable store lineage,
  strict JSON and closed sidecar/component/fixture schemas.
- Recorded canonical UTC `Z` serialization and defensive reconstruction of
  Market State fingerprints at store insertion.
- Cross-bound the live deterministic hash across policy, gate, traceability,
  governance package and canonical run.
- Tests: 155/155 PASS; included BT-GATE-014 tests: 36/36 PASS;
  external-review regressions: 27/27 PASS; skipped: 0.
- Deterministic output hash:
  `bb499dd82edf7b7fb165aa9d5e088468e946138c16b1ffce89a4bbb74b8bd7fd`.
- Scientific manifest hash:
  `25f80ee5c11aadd2838fbc8a54aa7b182ed2583fc49f1ba78c1cb26e235456ee`.
- Physical consumer read remains NOT_EXECUTED and new single-use physical
  authorization remains NOT_AUTHORIZED.

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

- Registered V0.1 and V0.2 as superseded and unconsumed after their pre-execution review failures.
- Registered the corrected `BAR → STATE` causal key and durable pre-consumption failure guard.
- Bound V0.3 to the exact two-row ACIU scope, nine frozen inputs and complete deterministic/scientific evidence.
- Added semantic governance validation across authorization states, gate, policy, traceability, exception, document, config and executable hashes.
- `V0_3 = AUTHORIZED_NOT_CONSUMED`; physical rows read remain zero and closure remains unauthorized.

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
