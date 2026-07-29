# 07 Execution Semantics And Cost Model Contract V0.1

Status: CLOSED_REVIEWED_READY_FOR_BOUNDED_IMPLEMENTATION_AUTHORIZATION
Date: 2026-07-29
Scope: backtester execution semantics and minimum cost-model contract after `ACCOUNTING_VERTICAL_SLICE_CLOSED`.

This document belongs only to:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE
```

It is a contract-definition increment. It does not authorize code implementation, real broker simulation, `StateReplayFeed`, Market State, Event State, production, downstream use or a full 2005-2026 backtest.

## 1. Current State

Closed backtester chain before this document:

```text
DATA = PASS
REPLAY_FEED = PASS
MECHANICAL_TRADE_PATH = PASS
ACCOUNTING_MINIMUM = PASS
BACKTEST_VERTICAL_SLICE = ACCOUNTING_VERTICAL_SLICE_CLOSED
```

Current validated real fixture path:

```text
RunPreflight
  -> HistoricalReplayFeed
  -> MechanicalEventLoop
  -> AccountingEngine
  -> real ABAT gross-to-net smoke
```

Current non-claims:

```text
BROKER_COST_REALISM = NOT_CLAIMED
FILL_REALISM = NOT_CLAIMED
SHORT_TRADABILITY = NOT_EVALUATED
EDGE = NOT_EVALUATED
```

## 2. Authorization Boundary

```text
CONTRACT_DEFINITION = AUTHORIZED
CONTRACT_REVIEW_STATE = CORRECTED_DRAFT_READY_FOR_REVIEW
CODE_IMPLEMENTATION = NOT_AUTHORIZED
BROKER_COST_REALISM = NOT_CLAIMED
FILL_REALISM = NOT_CLAIMED
SHORT_TRADABILITY = NOT_EVALUATED
EDGE = NOT_EVALUATED
```

Out of scope:

```text
StateReplayFeed
Market State
Event State
state bundle physical reads
RunPreflight state consumption
strategy access to Market/Event State
orders/fills/PnL driven by states
borrow realism
locates
full fill realism
production
downstream
full 2005-2026 backtest
```

## 3. Purpose

The next implementation increment must not merely produce more trades. It must first define what an executable order means inside TSIS.

This contract fixes the minimum path:

```text
decision
  -> order submission
  -> first eligible fill opportunity
  -> execution price policy
  -> deterministic slippage policy
  -> cost model
  -> accounting
```

The purpose is to prevent these errors:

```text
same-bar lookahead
retroactive fills
using a signal price as an execution price without declaring it
confusing a short PnL calculation with real short availability
mixing broker realism claims into a mechanical proxy run
rounding or cost drift between execution and accounting
```

## 4. Execution Profiles

TSIS separates execution profiles because the current bounded fixture guarantees bars, not quote-level execution semantics.

### 4.1 `bar_based_execution_profile_v0_1`

Status:

```text
PRIMARY_FOR_NEXT_IMPLEMENTATION
```

Inputs:

```text
ReplayBarEvent
ReplayGapEvent
execution_price_view = quote_guarded_1m
session = REGULAR_ONLY
timezone = America/New_York
bar_interval = [ts_start, ts_end)
available_at = ts_end
```

Allowed use:

```text
engine mechanics
causal timing validation
order lifecycle validation
accounting reconciliation
```

Not allowed as proof of:

```text
bid/ask spread realism
queue priority
liquidity availability
partial fill realism
borrow availability
locate availability
trading edge
```

### 4.2 `quote_aware_execution_profile_v0_1`

Status:

```text
RESERVED_NOT_AUTHORIZED_FOR_IMPLEMENTATION
```

This profile requires an explicitly authorized quote source and a later contract. It must not be inferred from OHLCV bars or vendor-derived fields.

Minimum future requirements:

```text
bid/ask timestamps
quote availability policy
stale quote policy
spread policy
side-aware marketable price
quote hash lineage
quote/source authorization
```

Until authorized:

```text
quote_aware_execution_profile_v0_1 = NOT_IMPLEMENTED
```

## 5. Core Time Semantics

### 5.1 `decision_timestamp`

The event-loop clock at which a strategy or mechanical policy forms a decision.

A decision may only depend on facts where:

```text
fact.available_at <= decision_timestamp
```

A decision at `09:31:00 America/New_York` may observe the completed bar `[09:30:00, 09:31:00)`. It may not retroactively fill at the `09:30:00` open unless the order was already live before that open.

### 5.2 `order_submission_timestamp`

The timestamp at which an `OrderIntent` becomes an executable order request in the simulator.

Invariant:

```text
order_submission_timestamp >= decision_timestamp
```

Exception for programmed orders:

```text
programmed_order_created_at <= session_open
order_submission_timestamp <= first eligible execution timestamp
```

A programmed order is allowed only if its rule was fixed before the price interval it uses.

### 5.3 `first_eligible_fill_timestamp`

The earliest economic timestamp where the order may receive a fill.

General invariant:

```text
first_eligible_fill_timestamp >= order_submission_timestamp
```

Canonical bar eligibility invariant:

```text
order_submission_timestamp <= source_bar.ts_start
```

A bar whose `source_bar.ts_start` is earlier than `order_submission_timestamp` is not evaluable for `MARKET_PROXY`, `LIMIT` or `STOP_MARKET_PROXY` fills. This rule is what makes equality deterministic: an order submitted exactly at `source_bar.ts_start` may evaluate that bar; an order submitted after `source_bar.ts_start` may not.

Pre-scheduled open/close proxies remain legal only under their explicit programmed-order rules, and they must still prove the order was logically active before the interval whose price proxy is used.

### 5.4 `fill_recorded_at`

The timestamp at which the simulator can record and expose the fill to downstream accounting or strategy state.

Invariant:

```text
fill_recorded_at >= source_price.available_at
```

This allows a pre-scheduled open order to have:

```text
economic_execution_timestamp = session_open
fill_recorded_at = first_bar.available_at
```

The strategy cannot observe that open fill before `fill_recorded_at`.

## 6. Same-Bar Lookahead Prohibition

Illegal:

```text
observe bar [t, t+1m) at available_at = t+1m
create decision at t+1m
fill at open/high/low/close inside [t, t+1m)
```

Legal patterns:

```text
pre-scheduled open order -> fill on first regular bar open proxy
pre-scheduled close order -> fill on final regular bar close proxy
post-bar decision -> fill no earlier than the next eligible bar or later order rule
```

The engine must be able to explain each fill with:

```text
decision_timestamp
order_submission_timestamp
first_eligible_fill_timestamp
economic_execution_timestamp
source_bar_id
source_bar_interval
source_bar_available_at
fill_recorded_at
```

## 7. Bar-Based Execution Semantics V0.1

### 7.1 Open Proxy

Allowed only when:

```text
order is scheduled/submitted before session_open
source bar = first regular bar
execution_price = source_bar.open
fill_recorded_at = source_bar.available_at
```

Use case:

```text
programmed validation smoke
open-entry systems where the order existed before the opening print proxy
```

### 7.2 Close Proxy

Allowed only when:

```text
order rule exists before the final regular bar starts
order_submission_timestamp <= final_regular_bar.ts_start
source bar = final regular bar
execution_price = source_bar.close
fill_recorded_at = source_bar.available_at
```

A decision made after seeing the final close cannot receive that same close as a fill.

### 7.3 Next-Bar Market Proxy

For a decision made after bar `B` is available:

```text
source bar for fill = first eligible bar after B satisfying order_submission_timestamp <= source_bar.ts_start
execution_price = next_bar.open, unless another explicit policy is selected
fill_recorded_at = next_bar.available_at
```

This remains a bar proxy, not proof that the open price was actually available for the requested size.

### 7.4 Limit Order V0.1

Minimum deterministic rule:

```text
source_bar may be evaluated only if order_submission_timestamp <= source_bar.ts_start
BUY limit eligible if source_bar.low <= limit_price
SELL limit eligible if source_bar.high >= limit_price
SELL_SHORT limit eligible if source_bar.high >= limit_price
BUY_TO_COVER limit eligible if source_bar.low <= limit_price
```

Limit price protection:

```text
BUY / BUY_TO_COVER limit:
fill_price <= limit_price

SELL / SELL_SHORT limit:
fill_price >= limit_price
```

Default V0.1 fill price:

```text
LIMIT_PRICE_IMPROVEMENT = DISABLED
LIMIT_SLIPPAGE_BEYOND_LIMIT = PROHIBITED
eligible limit fill base_price = limit_price
final fill_price = limit_price
```

Adverse slippage may apply to market proxy and stop-market proxy orders. It must not violate the economic protection of a limit order.

Ambiguity rule:

```text
ambiguous_bar_policy = FAIL_AMBIGUOUS_BAR_ONLY
PESSIMISTIC = RESERVED_NOT_IMPLEMENTED
```

If a bar could trigger both favorable and adverse outcomes and intrabar order is unknowable, V0.1 must not invent an intrabar sequence. The outcome is fail-closed under the explicit ambiguous-bar policy.

```text
ambiguous intrabar sequence under V0.1 -> EVALUATION_OUTCOME = FAIL_AMBIGUOUS_BAR
FAIL_AMBIGUOUS_BAR -> TERMINAL_ORDER_OUTCOME = REJECTED_BY_CONTRACT
```

A future `PESSIMISTIC` policy requires its own contract defining the exact event chosen, price selected and precedence against stops/limits. It is not available to `DETERMINISTIC_FILL_SIMULATOR_V0_1`.

### 7.5 Stop Order V0.1

Minimum deterministic trigger rule:

```text
source_bar may be evaluated only if order_submission_timestamp <= source_bar.ts_start
BUY stop triggers if source_bar.high >= stop_price
SELL stop triggers if source_bar.low <= stop_price
SELL_SHORT stop triggers if source_bar.low <= stop_price
BUY_TO_COVER stop triggers if source_bar.high >= stop_price
```

After trigger, V0.1 models the order as:

```text
STOP_MARKET_PROXY
```

Gap-through base-price rule:

```text
BUY / BUY_TO_COVER stop-market:
base_price = max(stop_price, source_bar.open)

SELL / SELL_SHORT stop-market:
base_price = min(stop_price, source_bar.open)
```

Then apply adverse slippage by side:

```text
fill_price = base_price + adverse_slippage for BUY / BUY_TO_COVER
fill_price = base_price - adverse_slippage for SELL / SELL_SHORT
```

A stop gapped through may not fill at a better price than the source bar open. This is still a conservative bar proxy, not proof of real stop execution quality.

## 8. Order And Fill States

Minimum order states:

```text
CREATED
SUBMITTED
ACCEPTED
REJECTED
LIVE
PARTIALLY_FILLED
FILLED
CANCEL_PENDING
CANCELED
EXPIRED
NOT_EXECUTED
```

Minimum fill facts:

```text
fill_id
order_id
ticker
side
quantity
fill_quantity
remaining_quantity
economic_execution_timestamp
fill_recorded_at
execution_price_before_slippage
slippage_amount
fill_price
gross_notional
source_price_profile
source_bar_id
source_bar_available_at
cost_breakdown_id
```

Gross notional formula:

```text
gross_notional = abs(fill_quantity) * fill_price
```

Contract vocabulary may include reserved lifecycle states. The first implementation subset is narrower.

Implemented in `DETERMINISTIC_FILL_SIMULATOR_V0_1` only after later code authorization:

```text
order types:
  MARKET_PROXY
  LIMIT
  STOP_MARKET_PROXY

fill capability:
  FULL_FILL_ONLY

partial fills:
  RESERVED_NOT_IMPLEMENTED

liquidity sizing:
  NOT_MODELED

cancellation race:
  NOT_MODELED

risk rejection:
  contract-validation rejection only

time in force:
  DAY only
```

Supported V0.1 EVALUATION_OUTCOME:

```text
FULL_FILL
NO_FILL_NOT_ELIGIBLE
NO_FILL_MISSING_PRICE
NO_FILL_GAP
FAIL_AMBIGUOUS_BAR
REJECTED_BY_CONTRACT
```

Supported V0.1 TERMINAL_ORDER_OUTCOME:

```text
FILLED
EXPIRED_UNFILLED
REJECTED_BY_CONTRACT
```

Reserved outcomes not implemented in V0.1:

```text
PARTIAL_FILL
REJECTED_BY_RISK_OR_BROKER
CANCEL_RACE_OUTCOME
```

## 9. Side Semantics

Sides:

```text
BUY
SELL
SELL_SHORT
BUY_TO_COVER
```

Gross PnL sign rules:

```text
long round trip  = quantity * (exit_price - entry_price)
short round trip = quantity * (entry_price - exit_price)
```

Cash-flow direction for shorts:

```text
SELL_SHORT proceeds increase cash
BUY_TO_COVER payment decreases cash
short proceeds are not realized profit by themselves
```

Accounting must keep separate:

```text
cash
position_quantity
position_market_value
realized_pnl
unrealized_pnl
costs
equity
```

## 10. Slippage V0.1

Status:

```text
DETERMINISTIC_PROXY_ONLY
```

Allowed first policies:

```text
ZERO_SLIPPAGE
FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE
BPS_OF_PRICE_ADVERSE
```

`FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE` is an adjustment to the unit execution price, not a separate cost component. Do not interpret it as commission or total per-share fee.

Slippage amount formulas:

```text
ZERO_SLIPPAGE:
slippage_amount = 0

FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE:
slippage_amount = per_share_price_adjustment

BPS_OF_PRICE_ADVERSE:
slippage_amount = base_price * slippage_bps / 10000
```

Slippage inputs must satisfy:

```text
base_price > 0
slippage_amount >= 0
```

Adverse direction:

```text
BUY: fill_price = base_price + slippage_amount
BUY_TO_COVER: fill_price = base_price + slippage_amount
SELL: fill_price = base_price - slippage_amount
SELL_SHORT: fill_price = base_price - slippage_amount
```

Post-slippage guard:

```text
if fill_price <= 0:
    outcome = REJECTED_BY_CONTRACT
```

The run manifest must record:

```text
slippage_model_id
slippage_model_version
slippage_unit
slippage_value
side_adjustment_rule
```

Non-claims:

```text
spread modeled = false unless quote-aware profile is authorized
market impact modeled = false
queue priority modeled = false
liquidity cap modeled = false
```

## 11. Cost Model V0.1

The existing accounting component categories remain canonical for the next contract:

```text
commission
routing_or_ecn_fee
regulatory_fee
locate_fee
borrow_fee
other_fee
```

Minimum cost policy fields:

```text
cost_model_id
cost_model_version
commission_per_share
minimum_commission_per_order
fixed_fee_per_order
routing_or_ecn_fee_per_share
regulatory_fee_per_share_or_notional
locate_fee_per_share
borrow_fee_policy
other_fee_policy
rounding_policy_id
```

V0.1 implementation may keep several components at zero, but the zero must be explicit.

V0.1 deterministic cost formulas:

```text
commission:
  applies_to = BUY, SELL, SELL_SHORT, BUY_TO_COVER
  raw = abs(fill_quantity) * commission_per_share
  component = max(raw, minimum_commission_per_order) when order has a fill

fixed_fee_per_order:
  applies_to = BUY, SELL, SELL_SHORT, BUY_TO_COVER
  component = fixed_fee_per_order when order has a fill

routing_or_ecn_fee:
  applies_to = BUY, SELL, SELL_SHORT, BUY_TO_COVER
  component = abs(fill_quantity) * routing_or_ecn_fee_per_share

regulatory_fee:
  applies_to = SELL, SELL_SHORT
  per_share mode: component = abs(fill_quantity) * regulatory_fee_per_share
  notional_bps mode: component = gross_notional * regulatory_fee_bps / 10000
  exactly one regulatory mode may be active, or both must be explicitly zero

locate_fee:
  applies_to = SELL_SHORT
  component = abs(fill_quantity) * locate_fee_per_share when explicitly configured
  default = 0 under SHORT_TRADABILITY_NOT_EVALUATED

borrow_fee:
  V0.1 = ZERO_ONLY unless a later borrow model is authorized
  nonzero borrow fee without authorized borrow model = REJECTED_BY_CONTRACT

other_fee:
  applies_to = BUY, SELL, SELL_SHORT, BUY_TO_COVER
  component = other_fixed_fee_per_filled_order, if configured
```

Costs are applied only to filled quantity unless a later explicit rejection/cancel fee policy exists. V0.1 does not charge costs for `NO_FILL_*`, `EXPIRED_UNFILLED` or `REJECTED_BY_CONTRACT` outcomes.

Required invariant:

```text
total_costs = sum(cost_components)
net_pnl = gross_pnl - total_costs
ending_equity = starting_equity + realized_net_pnl + unrealized_pnl
```

## 12. Decimal, Tick Size And Rounding

Money arithmetic must use deterministic decimal semantics. Binary floating point must not decide final cents.

Canonical execution/accounting calculation sequence:

```text
1. determine source/base price
2. apply stop gap-through policy, if applicable
3. apply adverse slippage, if applicable and permitted for the order type
4. apply V0.1 execution-price tick policy
5. compute gross notional
6. calculate each cost component
7. preserve internal sub-cent precision
8. round ledger monetary postings
9. reconcile gross PnL, costs, net PnL and equity
```

Minimum monetary rounding:

```text
decimal_rounding_mode = ROUND_HALF_EVEN
cash and realized PnL rounded to cents at ledger/report boundary
internal per-share rates may retain sub-cent precision
rounding_policy_id recorded in manifest
```

Price tick handling:

```text
tick_size_policy_id = PASSTHROUGH_SOURCE_PRICE_WITH_DECLARED_DECIMAL_PRECISION
source bar prices are consumed as provided and are not forcibly snapped to cents
order limit/stop prices are accepted at their declared decimal precision
no historical tick-size legality is inferred from OHLCV bars alone
```

If any run or implementation requires a different tick policy, the V0.1 outcome is:

```text
FAIL_CLOSED_WHEN_TICK_POLICY_REQUIRED
```

The run manifest must always record `tick_size_policy_id`.

## 13. Missing Data And Non-Executable Bars

If the required source bar is absent:

```text
NO_FILL_MISSING_PRICE
```

If a `ReplayGapEvent` appears where the order would need a price:

```text
NO_FILL_GAP
```

If the first regular open proxy or final close proxy is missing for a ticker-day:

```text
FAIL_TICKER_DAY_FOR_EXECUTION_PROXY
```

Canonical outcome precedence separates per-bar evaluation from terminal order state.

`EVALUATION_OUTCOME` for each selected evaluation opportunity:

```text
1. invalid order/configuration/capability/tick/slippage/borrow requirement -> REJECTED_BY_CONTRACT
2. selected source interval is an explicit ReplayGapEvent -> NO_FILL_GAP
3. selected source bar or required OHLC field is absent/null/nonpositive/nonfinite -> NO_FILL_MISSING_PRICE
4. selected source_bar.ts_start < order_submission_timestamp -> NO_FILL_NOT_ELIGIBLE
5. ambiguous intrabar sequence under V0.1 -> FAIL_AMBIGUOUS_BAR
6. limit or stop trigger is not reached -> NO_FILL_NOT_ELIGIBLE
7. computed fill_price <= 0 -> REJECTED_BY_CONTRACT
8. otherwise, if all checks pass -> FULL_FILL
```

`TERMINAL_ORDER_OUTCOME` for a DAY order:

```text
if any evaluation outcome is FULL_FILL -> FILLED
elif any evaluation outcome is REJECTED_BY_CONTRACT or FAIL_AMBIGUOUS_BAR -> REJECTED_BY_CONTRACT
elif no later eligible opportunity remains before DAY expiry -> EXPIRED_UNFILLED
```

A gap or missing price remains recorded as that evaluation outcome. `EXPIRED_UNFILLED` is the terminal state only after the order reaches DAY expiry without a fill or rejection.

The same input must produce exactly one canonical `EVALUATION_OUTCOME` per evaluated opportunity and exactly one final `TERMINAL_ORDER_OUTCOME`.

The engine must not:

```text
forward-fill execution prices
use a later bar silently
use valuation price as execution price
use signal price as execution price without declaring it as the execution price view
```

## 14. Short Mechanics Versus Short Tradability

TSIS must separate:

```text
SHORT_EXECUTION_MECHANICS
```

from:

```text
SHORT_TRADABILITY
```

`SELL_SHORT` and `BUY_TO_COVER` may be implemented mechanically to test order lifecycle, accounting and PnL. That does not prove:

```text
shares were borrowable
locate was available
locate cost was known
borrow rate was acceptable
broker would accept the short
forced buy-in risk was modeled
```

Default claim state:

```text
SHORT_EXECUTION_MECHANICS = ALLOWED_FOR_ENGINE_VALIDATION
SHORT_TRADABILITY = NOT_EVALUATED
```

Any future short-realism increment must introduce separate inputs and gates for:

```text
locate availability
hard-to-borrow status
borrow fee
locate fee
short sale restrictions
halts and forced buy-ins
broker-specific constraints
```

## 15. Relationship To Existing Components

The next implementation must integrate with, not replace:

```text
RunPreflight
HistoricalReplayFeed
MechanicalEventLoop
AccountingEngine
```

Expected later responsibility split:

```text
ExecutionModel
  receives Order
  consumes authorized replay price events
  applies execution profile and slippage
  emits Fill or NoFill outcome

AccountingEngine
  consumes fills and cost breakdowns
  updates cash, position, realized PnL and equity
```

Execution must not compute final accounting totals independently from `AccountingEngine`.

## 16. Minimum Run Manifest Fields

A future run manifest must record:

```text
execution_profile_id
execution_profile_version
price_view_policy.signal
price_view_policy.execution
price_view_policy.valuation
fill_model_id
fill_model_version
slippage_model_id
slippage_model_version
cost_model_id
cost_model_version
rounding_policy_id
tick_size_policy_id
missing_execution_price_policy
ambiguous_bar_policy
terminal_order_outcome_policy_id
short_execution_mechanics_state
short_tradability_state
broker_cost_realism_claimed
fill_realism_claimed
edge_evaluated
```

## 17. Acceptance Tests For Future Implementation

Contract-definition acceptance:

```text
this document exists
CONTRACT_DEFINITION = AUTHORIZED
CODE_IMPLEMENTATION = NOT_AUTHORIZED
state consumption remains NOT_AUTHORIZED
bar_based_execution_profile_v0_1 is primary
quote_aware_execution_profile_v0_1 is reserved
temporal bar eligibility is exact
limit protection is exact
stop gap-through is exact
tick policy is exact
slippage formulas are exact
cost formulas are exact
ambiguous bar policy is exact
outcome precedence separates evaluation and terminal outcomes
gross notional formula is exact
claims not made are explicit
```

Future implementation tests:

```text
post-bar decision cannot fill inside the observed bar
pre-scheduled open order can fill first regular open proxy and is recorded only after availability
pre-scheduled close order can fill final close proxy only when order_submission_timestamp <= final_regular_bar.ts_start
next-bar market proxy uses first source bar satisfying order_submission_timestamp <= source_bar.ts_start
LIMIT evaluates no bar whose source_bar.ts_start < order_submission_timestamp
STOP_MARKET_PROXY evaluates no bar whose source_bar.ts_start < order_submission_timestamp
limit protection is never violated by slippage
BUY/BUY_TO_COVER stop gapped through uses max(stop_price, source_bar.open) before slippage
SELL/SELL_SHORT stop gapped through uses min(stop_price, source_bar.open) before slippage
tick_size_policy_id is always recorded
unsupported tick policy fails closed under FAIL_CLOSED_WHEN_TICK_POLICY_REQUIRED
FIXED_PER_SHARE_PRICE_ADJUSTMENT_ADVERSE adjusts unit price, not cost
BPS_OF_PRICE_ADVERSE computes base_price * slippage_bps / 10000
computed fill_price <= 0 returns REJECTED_BY_CONTRACT
cost components use declared side applicability and formulas
borrow_fee nonzero without authorized borrow model returns REJECTED_BY_CONTRACT
outcome precedence produces one canonical evaluation outcome and one terminal order outcome
NO_FILL_GAP remains recorded even if the order later expires
NO_FILL_MISSING_PRICE remains recorded even if the order later expires
PESSIMISTIC ambiguous-bar policy is reserved/not implemented
FAIL_AMBIGUOUS_BAR_ONLY is the only V0.1 ambiguous-bar policy
gross_notional = abs(fill_quantity) * fill_price
rounding sequence is deterministic and uses ROUND_HALF_EVEN
unsupported partial fill request fails closed as RESERVED_NOT_IMPLEMENTED
close order submitted after final_regular_bar.ts_start is ineligible for the final close proxy
missing required open proxy fails ticker-day
ReplayGapEvent at needed price produces NO_FILL_GAP
BUY slippage is adverse
SELL slippage is adverse
SELL_SHORT slippage is adverse
BUY_TO_COVER slippage is adverse
zero slippage preserves base price
commission minimum applies per order
sub-cent rates are preserved before final money rounding
short cash proceeds do not equal realized profit
final net PnL reconciles to accounting
limit order crossing rule is deterministic
stop order trigger rule is deterministic
ambiguous intrabar stop/target sequence produces EVALUATION_OUTCOME = FAIL_AMBIGUOUS_BAR
FAIL_AMBIGUOUS_BAR produces TERMINAL_ORDER_OUTCOME = REJECTED_BY_CONTRACT
quote-aware profile cannot run without quote authorization
short mechanics do not set short tradability evaluated
same inputs produce deterministic fills, costs and hashes
```

## 18. Done Criteria For The Next Code Increment

The later implementation may be closed only when:

```text
ExecutionModel contract exists in code
bar-based execution profile implemented for the selected subset
slippage model implemented deterministically
cost model integrates with AccountingEngine
all acceptance tests pass
real ABAT smoke is rerun through ExecutionModel rather than direct mechanical fill injection
run manifests record execution/cost assumptions
AGENTS.md and CHANGELOG.md are updated
```

The later implementation still must not claim:

```text
broker realism
fill realism
short tradability
edge
```

## 19. Open Ambiguities

These are intentionally not solved by this document:

```text
exact US equity tick-size source for every historical timestamp
broker-specific commission/routing schedules
real borrow/locate availability
spread and quote staleness
partial-fill probability
liquidity participation caps
halt handling
same-bar high/low sequence without intrabar data
market impact
```

Each requires a later bounded increment.

## 20. Summary Decision

```text
EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1 = CLOSED_REVIEWED_READY_FOR_BOUNDED_IMPLEMENTATION_AUTHORIZATION
CODE_IMPLEMENTATION = NOT_AUTHORIZED
NEXT_GATE_IF_REVIEW_ACCEPTED = DETERMINISTIC_FILL_SIMULATOR_V0_1_AUTHORIZATION
```






## Final External Review Result

FINAL_ENUMERATION_REVIEW = PASS
SUPPORTED_EVALUATION_OUTCOME_ENUMERATION = PASS
SUPPORTED_TERMINAL_ORDER_OUTCOME_ENUMERATION = PASS
AMBIGUOUS_BAR_MAPPING = PASS
PACKAGE_INTEGRITY = PASS

EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1 = CLOSED_REVIEWED_READY_FOR_BOUNDED_IMPLEMENTATION_AUTHORIZATION
BT-GATE-006 = CLOSED_PASS
CODE_IMPLEMENTATION = NOT_AUTHORIZED
DETERMINISTIC_FILL_SIMULATOR_V0_1_AUTHORIZATION = OPEN_FOR_DECISION
