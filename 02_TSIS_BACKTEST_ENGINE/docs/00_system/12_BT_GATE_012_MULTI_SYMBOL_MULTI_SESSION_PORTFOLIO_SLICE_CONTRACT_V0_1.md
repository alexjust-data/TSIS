# BT-GATE-012 - Multi-Symbol Multi-Session Portfolio Slice Contract V0.1

Status: AUTHORIZED_FOR_CONTINUOUS_IMPLEMENTATION
Gate: BT-GATE-012
Capability: MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE
Code implementation: AUTHORIZED
Last updated: 2026-07-29T16:47:47Z
Review result: BT_GATE_012_OWNER_CONTRACT_REVIEW_PASS

## 1. Purpose

BT-GATE-012 extends the accepted BT-GATE-011 end-to-end path from a bounded
single-session engine-validation run into a portfolio-capable slice over
multiple symbols and multiple sessions.

The objective is still engine validation, not edge discovery. This gate must
prove deterministic portfolio state, shared cash ledger behavior, deterministic
global ordering, session transitions, trade ledger aggregation, equity curve
semantics and portable rerun evidence.

## 2. Prior Accepted Baseline

```text
BT-GATE-010 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
DETERMINISTIC_FILL_SIMULATOR_V0_1 = IMPLEMENTED_AND_ACCEPTED

BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED_AND_ACCEPTED
ONLINE_EVENT_DRIVEN_CAUSALITY = PASS
ORDER_CREATED_DURING_EVENT_PROCESSING = false
ACCOUNTING_APPLIED_INSIDE_EVENT_LOOP = true
```

BT-GATE-012 may reuse the accepted Data, Replay, Fill Simulator, accounting,
Trade Ledger and Unified Run Manifest capabilities. It must not reinterpret the
accepted execution semantics.

## 3. Authorization State

```text
BT-GATE-012 = AUTHORIZED_FOR_CONTINUOUS_IMPLEMENTATION
BT-GATE-012_IMPLEMENTATION = AUTHORIZED
OWNER_CONTRACT_REVIEW = PASS
EXECUTION_MODE = CONTINUOUS_UNTIL_FINAL_ACCEPTANCE_PACKET
NO_INTERMEDIATE_MICROGATES = AUTHORIZED
NEXT_OWNER_REVIEW = FINAL_GATE_ACCEPTANCE_ONLY,
UNLESS MATERIAL SCOPE OR SEMANTIC CHANGE
```

This document now records owner approval for bounded continuous implementation. Implementation may run continuously inside the same gate until the final acceptance packet unless a material stop condition is triggered.

## 4. Capability Scope

The implementation scope to be approved later should include:

- PortfolioRunSpec or equivalent run contract.
- Multi-session fixture derived only from already admitted 1m quote-guarded data.
- Fixed StrategySpec reused across symbol-days.
- Global replay ordering across symbols and sessions.
- Pre-registered decisions and orders before eligible bars.
- Active order registry shared across symbols.
- Shared cash ledger and shared position registry.
- Per-symbol, per-session and portfolio Trade Ledger.
- Portfolio equity curve with deterministic valuation semantics.
- Session boundary handling and DAY order expiry.
- Deterministic end-of-session flatness policy for this validation strategy.
- Unified Run Manifest extended with portfolio identities and hashes.
- Tests for temporal, accounting, ordering, session and determinism invariants.
- Portable final acceptance package.

## 5. Validation Strategy

Use a fixed and deliberately simple strategy family derived from
`open_short_close_cover_v0_1`:

```text
For each authorized symbol-session:
pre-register SELL_SHORT MARKET_PROXY before the first regular bar
pre-register BUY_TO_COVER MARKET_PROXY before the final regular bar
quantity = fixed per symbol-session
FULL_FILL_ONLY
DAY
deterministic costs and slippage from accepted contracts
```

This remains an engine-validation strategy. No optimization, parameter search or
edge interpretation is authorized.

`OPEN` and `CLOSE` remain strategy labels. They do not authorize MOO/MOC order
semantics or any execution path outside the accepted Deterministic Fill
Simulator V0.1.

## 6. Fixture Acceptance Profile V0.1

The final BT-GATE-012 acceptance fixture must satisfy:

```text
sessions >= 2 distinct XNYS regular-session dates
symbols >= 3 per session
symbol_sessions >= 6
same_timestamp_cross_symbol_events = REQUIRED
ReplayGapEvent_presence = REQUIRED
contractual_open_close_coverage = REQUIRED for every symbol-session
portable_relative_paths = REQUIRED
all_physical_or_portable_inputs_hashed = REQUIRED
negative_truncated_session_derivative = REQUIRED
```

Allowed data boundary:

```text
fixture_kind = TSIS_REAL_DATA_FIXTURE or portable derivative of accepted input
price_view = quote_guarded_1m or exact accepted equivalent
session_policy = REGULAR_ONLY_XNYS_V0_1
CALENDAR_AUTHORITY = TSIS_PORTABLE_SESSION_CALENDAR_SNAPSHOT_V0_1
CALENDAR_ID = XNYS
CALENDAR_TIMEZONE = America/New_York
SESSION_CALENDAR_SNAPSHOT = REQUIRED
SESSION_CALENDAR_SNAPSHOT_SHA256 = REQUIRED
```

If a new physical data source is required, implementation must stop for owner
approval. Portable fixture construction is allowed only if derived from already
accepted inputs and fully hashed.

## 7. Global Ordering Semantics V0.1

BT-GATE-012 must use one executable total order for replay events:

```text
GLOBAL_REPLAY_ORDER_V0_1 =
(
    available_at_utc,
    session_date,
    event_type_priority,
    ticker_normalized,
    source_event_identity
)
```

Required event priority:

```text
ReplayGapEvent = 0
ReplayBarEvent = 1
```

Normalization and identity:

```text
ticker_normalized = uppercase ASCII ticker string
source_event_identity = stable serialized identity from the replay event contract
available_at_utc = timezone-aware UTC instant
session_date = contract session date in YYYY-MM-DD
```

If two replay events remain tied after all fields in `GLOBAL_REPLAY_ORDER_V0_1`,
the run must fail closed with an unresolved-ordering error. The implementation
may not silently refine this order after approval.

Replay gap rule:

```text
ReplayGapEvent never supplies an execution price.
ReplayGapEvent never triggers a fill.
ReplayGapEvent participates in event ordering, traceability and validation.
```

Active order evaluation order:

```text
ACTIVE_ORDER_EVALUATION_ORDER_V0_1 =
(
    eligible_event_index,
    order_activation_timestamp,
    order_id
)
```

If multiple active orders remain tied after this tuple, the run must fail closed.
All ordering fields and normalized values must be persisted and hashed.

## 8. Portfolio Capital Boundary V0.1

BT-GATE-012 does not implement capital allocation, buying-power checks or margin
models. Its portfolio scope is ledger and state integration, not capital
contention realism.

```text
CAPITAL_ALLOCATION = NOT_IMPLEMENTED
BUYING_POWER_MODEL = NOT_IMPLEMENTED
MARGIN_MODEL = NOT_IMPLEMENTED
CAPITAL_CONTENTION_CLAIM = NOT_AUTHORIZED

SHARED_CASH_LEDGER = IMPLEMENTED_IN_SCOPE after approval
SHARED_POSITION_REGISTRY = IMPLEMENTED_IN_SCOPE after approval
FIXED_QUANTITY_POLICY = IMPLEMENTED_IN_SCOPE after approval
```

Required V0.1 policy:

```text
initial_cash = explicitly configured fixed Decimal amount
short_sale_proceeds_accounting = inherited from accepted BT-GATE-011 accounting policy
order_sizing_depends_on_portfolio_cash = false
buying_power_rejection = NOT_AUTHORIZED in V0.1
```

No order may be rejected for buying-power reasons in V0.1. Rejections may occur
only through accepted execution-contract, data/session or fail-closed validation
rules.

## 9. Portfolio Equity Policy V0.1

Portfolio equity must be computed point-in-time with deterministic valuation:

```text
PORTFOLIO_EQUITY_POLICY_V0_1

cash:
updated immediately after every fill and cost

open_position_valuation:
latest legally available regular-session ReplayBarEvent close price per symbol

PORTFOLIO_VALUATION_PRICE_FIELD:
close

valuation_price:
close of the latest ReplayBarEvent legally available at or before equity_timestamp

ReplayGapEvent valuation rule:
ReplayGapEvent never updates valuation_price

short_market_value:
-quantity * valuation_price

long_market_value:
quantity * valuation_price

unrealized_pnl:
calculated point-in-time from accepted fill prices and valuation prices

equity:
cash + total_signed_market_value

equity_timestamp:
event available_at after any fill, cost, accounting and valuation update caused by that globally ordered replay event

equity_curve_frequency:
one equity point after every globally ordered replay event

between_sessions:
cash and realized PnL carry forward;
all positions must already be flat;
no overnight mark is required for V0.1
```

A symbol without any legally observable valuation price at a timestamp has no
open position valuation until its first accepted price. If it has an open
position and no legal valuation price is available, the run fails closed. The
equity curve must state whether each point was produced by event arrival, fill
application, session boundary or final run close.

## 10. Session Policy V0.1

```text
SESSION_POLICY = REGULAR_ONLY_XNYS_V0_1
CALENDAR_AUTHORITY = TSIS_PORTABLE_SESSION_CALENDAR_SNAPSHOT_V0_1
CALENDAR_ID = XNYS
CALENDAR_TIMEZONE = America/New_York
SESSION_CALENDAR_SNAPSHOT = REQUIRED
SESSION_CALENDAR_SNAPSHOT_SHA256 = REQUIRED
CALENDAR_VERSION = snapshot identity and SHA-256 declared in run manifest
SESSION_OPEN = snapshot regular open for session date
SESSION_CLOSE = snapshot regular close for session date
DAY_ORDER_EXPIRY = CONTRACTUAL_SESSION_CLOSE
OVERNIGHT_POSITIONS = PROHIBITED
SESSION_END_POSITION = ZERO_PER_SYMBOL
MISSING_CONTRACTUAL_CLOSE = FAIL_RUN
TRUNCATED_SESSION = FAIL_RUN
UNEXECUTED_REQUIRED_EXIT = FAIL_RUN
UNEXPLAINED_OPEN_ORDER_AT_SESSION_END = FAIL_RUN
```

Early-close sessions are not admitted in BT-GATE-012 V0.1 unless the fixture and
calendar contract explicitly include and test them. Cash and realized PnL carry
forward across sessions; open positions do not.

For this gate, required contractual failures invalidate the full run. The
implementation must not downgrade missing close, truncated session, unexplained
open order or residual position to a symbol-session-only warning.

## 11. Portfolio State Invariants

The implementation must prove:

- One shared account state across all symbols and sessions.
- Every fill updates cash, position and equity before the next event is handled.
- Position state is keyed by symbol.
- This V0.1 validation strategy finishes every symbol-session flat.
- Unexplained residual cash, position, PnL or costs fail the run.
- Costs are counted exactly once.
- Portfolio gross PnL equals the sum of trade gross PnL.
- Portfolio net PnL equals gross PnL minus total costs.
- Ending equity equals starting equity plus realized net PnL after all positions
  are flat.
- Session results sum exactly to portfolio results.

## 12. Acceptance Criteria

BT-GATE-012 can be accepted only when the final package proves:

- BT-GATE-011 remains closed and unchanged.
- Multi-symbol and multi-session run completes with validation_status = PASS.
- Fixture satisfies `FIXTURE_ACCEPTANCE_PROFILE_V0_1`.
- Global event sequence uses `GLOBAL_REPLAY_ORDER_V0_1` and is hashed.
- Active order evaluation uses `ACTIVE_ORDER_EVALUATION_ORDER_V0_1` and is hashed.
- Decisions/orders are pre-registered before eligible bars.
- No future event is visible to strategy, order creation or simulator.
- Every simulator call receives only the current eligible event.
- Accounting is applied inside the event loop before the next event.
- Shared cash and positions reconcile after every fill.
- Per-trade, per-symbol, per-session and portfolio totals reconcile.
- Portfolio equity curve follows `PORTFOLIO_EQUITY_POLICY_V0_1`, using `PORTFOLIO_VALUATION_PRICE_FIELD = close`.
- Truncated or missing contractual close fails the full run.
- Unsupported cross-symbol behavior fails closed.
- Same inputs and configuration reproduce identical semantic output hashes.
- Package commands reproduce tests and the run from extracted contents.

## 13. Required Tests

At minimum:

- global ordering across same-timestamp symbols;
- ReplayGapEvent ordered before ReplayBarEvent at the same `available_at`;
- ReplayGapEvent cannot trigger a fill or supply an execution price;
- active order evaluation order is deterministic;
- unresolved ordering tie fails closed;
- multi-session session boundary handling;
- DAY orders expire at contractual session close;
- pre-registration before replay for all symbol-sessions;
- no order created during event processing;
- current-event-only simulator invocation;
- online accounting after each fill;
- shared cash ledger reconciliation;
- position isolation by symbol;
- end-of-day flatness for the validation strategy;
- missing contractual close fails full run;
- truncated session derivative fails full run;
- equity curve uses latest legal close valuation price;
- open position without legal valuation fails closed;
- session calendar snapshot identity and SHA-256 recorded;
- deterministic rerun hash equality;
- package reproducibility command.

## 14. Required Outputs

The final implementation gate must produce:

- portfolio_run_manifest.json;
- configuration_snapshot.json;
- portfolio_strategy_spec.json;
- event_sequence_manifest.json;
- decisions.json;
- order_intents.json;
- orders.json;
- fills.json;
- event_loop_trace.json;
- trade_ledger.json;
- cash_ledger.json;
- positions_by_symbol.json;
- session_results.json;
- portfolio_equity_curve.json;
- session_calendar_snapshot.json;
- metrics_summary.json;
- validation_report.json;
- determinism_report.json;
- artifact_hashes.json;
- final acceptance ZIP.

Names may follow repository conventions, but the information must be explicit
and hash-verifiable.

## 15. Explicit Non-Claims

```text
RUN_PURPOSE = ENGINE_VALIDATION_RUN
EDGE_EVIDENCE = NOT_AUTHORIZED
ECONOMIC_REALISM = INCOMPLETE
STRATEGY_OPTIMIZATION = NOT_AUTHORIZED
CAPITAL_CONTENTION_CLAIM = NOT_AUTHORIZED
```

BT-GATE-012 does not authorize:

- borrow or locates;
- SSR;
- halts;
- liquidity or capacity modeling;
- capital allocation or buying-power modeling;
- partial fills;
- bid/ask or quote-aware execution;
- broker realism;
- state-driven strategy decisions;
- optimization;
- edge or profitability claims.

## 16. State Provider Boundary

The following remain closed:

```text
StateReplayFeed = NOT_AUTHORIZED
StateBundle physical reads = NOT_AUTHORIZED
Market State consumption = NOT_AUTHORIZED
Event State consumption = NOT_AUTHORIZED
provider modification = NOT_AUTHORIZED
```

## 17. Stop Conditions

Stop and request owner decision if implementation requires:

- changing accepted Fill Simulator semantics;
- using future information;
- adding MOO/MOC semantics;
- changing accounting model materially;
- consuming State Provider, Market State or Event State;
- adding small-caps realism features assigned to future gates after the physical historical replay boundary;
- introducing a new physical data source;
- adding capital contention, buying-power or margin semantics;
- expanding from engine validation into edge research.

## 18. After Owner Approval

Owner review accepted this corrected contract:

```text
BT-GATE-012_OWNER_CONTRACT_REVIEW = PASS
BT-GATE-012 = AUTHORIZED_FOR_CONTINUOUS_IMPLEMENTATION
BT-GATE-012_IMPLEMENTATION = AUTHORIZED
EXECUTION_MODE = CONTINUOUS_UNTIL_FINAL_ACCEPTANCE_PACKET
NO_INTERMEDIATE_MICROGATES = AUTHORIZED
NEXT_OWNER_REVIEW = FINAL_GATE_ACCEPTANCE_ONLY,
UNLESS MATERIAL SCOPE OR SEMANTIC CHANGE
```

Implementation acceptance is not yet granted. BT-GATE-012 can close only after the final acceptance packet proves the criteria in this contract.
