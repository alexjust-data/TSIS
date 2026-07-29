# Changelog

## 2026-07-29 â€” Integrated governance baseline V0.1.1

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

## 2026-07-29 â€” Initial governance baseline V0.1

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
BT-GATE-013_CONTRACT = CONTRACT_DRAFT_PENDING_OWNER_REVIEW
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
CONTRACT_ARTIFACT = docs/00_system/14_BT_GATE_013_PHYSICAL_HISTORICAL_REPLAY_SLICE_CONTRACT_V0_1.md
```

The contract draft was copied into the canonical backtester document location. This does not authorize implementation, Market State consumption, Event State consumption, StateReplayFeed, provider modification or full 2005-2026 execution.
