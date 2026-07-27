# TSIS Backtesting — Construction Scope and Detail Checklist V0_1

## Purpose

Build a rigorous, reproducible small-cap backtesting capability over TSIS local data.

This document does **not** define a live runtime, broker adapter, desktop application, GUI, or operational control panel. Notebooks are acceptable where they improve inspection and iteration.

The priority is to make every assumption explicit, testable, versioned, and reproducible.

---

## Core principle

```text
A backtest is only as valid as:

data
+
historical universe
+
temporal legality
+
execution assumptions
+
cost assumptions
+
validation protocol
```

The main risk is not unattractive code. The main risk is a hidden assumption creating a false edge.

---

## Target workflow

```text
TSIS Data Foundation
        ↓
Dataset / Price-View Resolution
        ↓
Point-in-Time Daily Universe
        ↓
Historical Intraday Feed
        ↓
Strategy Rules
        ↓
Order Intent
        ↓
Execution Simulation
        ↓
Positions / Accounting
        ↓
Closed Trades / Equity
        ↓
Performance Metrics
        ↓
Robustness and Validation
        ↓
Reproducible Research Dossier
```

Replay, live feed, DAS integration, GUI and app construction are outside the current scope.

---

# 1. Data contract before strategy

Every run must declare:

```text
dataset_id
dataset_version
physical_paths
schema_version
price_view
date_range
symbols
timezone
session_scope
corporate_action_policy
repair_manifest
known_failures
```

Allowed price-view examples:

```text
raw
split_normalized
quote_guarded
other_governed_view
```

A path alone does not define meaning. The active TSIS contract defines what the dataset represents and whether it is authorized for the experiment.

---

# 2. Point-in-time universe

The backtest must reconstruct the symbols eligible on each historical date. It must not use a current ticker list retrospectively.

The universe specification must declare:

```text
eligibility_timestamp
security_lifecycle
listing_start
delisting_date
ticker_changes
exchange
security_type
price_filter
market_cap_filter
volume_filter
float_or_fundamental_availability
premarket_condition
news_condition
other_filters
```

Every universe row should preserve:

```text
session_date
symbol
eligible
eligibility_reason
source_timestamp
data_available_at
universe_version
```

The universe is part of the experiment, not an administrative input.

---

# 3. Temporal legality

Every input must be available at the simulated decision time.

Required decisions:

```text
timestamp convention
timezone conversion
DST handling
session calendar
premarket start/end
regular session start/end
after-hours treatment
holiday handling
early closes
data publication delays
fundamental availability timestamps
news availability timestamps
```

Prohibited:

```text
using corrected future values
using end-of-day values intraday
using current fundamentals historically
using a completed bar before its close
using future universe membership
```

---

# 4. Missing and irregular bars

Small caps often contain missing minutes. The engine must distinguish:

```text
no trade occurred
vendor data missing
symbol halted
symbol not listed
outside session
corrupt observation
```

The policy must define:

```text
whether empty minutes are materialized
whether price is forward-filled
whether volume is zero-filled
how rolling windows treat missing minutes
whether indicators use elapsed time or observation count
```

Forward-filling price must never create fictitious liquidity or executable volume.

---

# 5. Premarket

Premarket is mandatory where the strategy depends on gappers, catalysts, early volume, HOD, VWAP, or opening context.

Declare:

```text
premarket window
premarket volume definition
premarket high/low
gap reference price
previous close definition
news cutoff
opening-state snapshot time
```

---

# 6. Halts and exceptional events

Minimum halt policy:

```text
no new fills during halt
no stop execution during halt
orders remain pending or are cancelled according to policy
first executable price after resumption is not assumed favorable
gap risk after resume is preserved
```

Also document treatment of:

```text
LULD pauses
news halts
suspensions
delistings
symbol changes
reverse splits
corporate actions
bad prints
```

---

# 7. Strategy specification

A strategy must be frozen before the test.

Minimum specification:

```text
strategy_id
strategy_version
research_hypothesis
entry_rules
exit_rules
stop_rules
time_rules
position-sizing rules
universe dependency
required features
parameters and ranges
forbidden future information
```

Separate:

```text
event or market condition
strategy decision
execution instruction
```

---

# 8. Order-intent model

Even in notebooks, represent an order intent explicitly.

```text
order_intent_id
strategy_id
symbol
decision_timestamp
side
quantity
order_type
limit_price
stop_price
time_in_force
entry_or_exit
reason
state_snapshot_id
```

This prevents equating “signal appeared” with “trade was executed”.

---

# 9. Fill model

The fill model must specify:

```text
market-order fill rule
limit-order fill rule
stop-order trigger rule
same-bar ambiguity
intrabar path assumption
bid/ask availability
spread model
available volume
participation cap
partial fills
queue-position assumption
latency
rejections
halts
price limits
```

With 1-minute bars, the true intrabar sequence is unknown. The run must declare one of:

```text
conservative path
optimistic path
worst-case path
multi-path sensitivity
higher-resolution confirmation
```

A stop and target touched in the same minute cannot be resolved favorably by default.

---

# 10. Liquidity and capacity

Minimum controls:

```text
max participation in bar volume
max participation in rolling volume
minimum dollar volume
minimum observed trade count
maximum spread
maximum position relative to ADV
partial-fill logic
unfilled remainder policy
```

The existence of a bar does not prove that the desired quantity was executable.

---

# 11. Spread model

Preferred evidence order:

```text
historical quotes
historical trade/quote reconstruction
empirical spread model by context
fixed conservative fallback
```

Every result must state whether P&L is:

```text
mid-to-mid
trade-price based
bid/ask executable
spread-adjusted estimate
```

---

# 12. Slippage model

Slippage is distinct from spread.

Possible components:

```text
decision-to-order delay
order-to-market delay
market movement
market impact
adverse selection
route/venue effects
```

Minimum testing:

```text
base slippage
moderate stress
severe stress
```

---

# 13. Short availability, locates and borrow

For short strategies, a signal is not sufficient.

Declare:

```text
shortable-status source
locate availability policy
locate price
borrow fee
hard-to-borrow treatment
quantity available
locate expiration
forced buy-in policy
missing-data fallback
```

Where historical locate data do not exist, results must be labeled conditional and tested under conservative scenarios.

---

# 14. Costs

Model separately:

```text
broker commission
ECN/routing fees
SEC fee
TAF fee
locate fee
borrow fee
other operational costs
```

Store both:

```text
gross_pnl
net_pnl
```

---

# 15. Position and accounting rules

Freeze:

```text
average cost vs FIFO/LIFO
partial-entry handling
partial-exit handling
position reversal
realized PnL
unrealized PnL
cash
equity
fees allocation
daily reset rules
```

Accounting identities must be tested with hand-calculated examples before large runs.

---

# 16. Output ledgers

Every run should produce:

```text
universe_membership
signals_or_decisions
order_intents
orders_simulated
fills
positions
closed_trades
equity_curve
daily_returns
cost_breakdown
exceptions
```

Minimum reproducibility package:

```text
strategy_spec
dataset_manifest
universe_manifest
run_manifest
orders
fills
positions
trades
equity
metrics
robustness_report
limitations
```

---

# 17. Performance metrics

Minimum:

```text
trade count
win rate
average win
average loss
expectancy
profit factor
gross PnL
net PnL
max drawdown
drawdown duration
Sharpe
Sortino
turnover
exposure
fees
slippage
capacity estimate
MAE
MFE
```

Metrics must declare:

```text
return frequency
annualization convention
equity base
treatment of inactive periods
sample size
```

---

# 18. Robustness protocol

Required tests:

```text
chronological holdout
walk-forward
parameter-neighborhood stability
cost stress
spread stress
slippage stress
fill-model stress
universe perturbation
subperiod analysis
regime analysis
ticker concentration
day concentration
bootstrap or resampling
multiple-testing control
```

A strategy is not robust because one parameter set produces a good curve.

---

# 19. Construction phases

## Phase 1 — Book and evidence study

```text
read index
classify chapters
extract methodological requirements
map each requirement to TSIS
```

## Phase 2 — Backtest contract

Freeze:

```text
data view
universe
time
sessions
missing bars
halts
fills
spread
slippage
locates
costs
accounting
outputs
validation
```

## Phase 3 — Minimal vertical slice

```text
one session
few symbols
OHLCV 1m
one trivial strategy
explicit order intents
simulated fills
positions
PnL verified by hand
```

## Phase 4 — Multi-session engine

```text
continuous sessions
daily universe changes
cash/equity continuity
premarket
halts
corporate events
```

## Phase 5 — Full historical experiment

```text
larger universe
2005–2026 where authorized
batch or parallel execution
run manifests
result aggregation
```

## Phase 6 — Realism

```text
quotes/trades where needed
spread
slippage
partial fills
capacity
locates
borrow
fees
```

## Phase 7 — Validation

```text
holdout
walk-forward
sensitivity
stress
bootstrap
multiple-testing controls
robustness dossier
```

Replay and live are outside the current scope.

---

# 20. Notebook policy

Notebooks are permitted for:

```text
data inspection
single-case reconstruction
strategy prototyping
manual verification
plots
robustness analysis
```

Reusable logic should move into tested Python modules when duplication or inconsistency appears.

Each notebook should record:

```text
run_id
strategy_version
dataset_version
universe_version
code commit or source hash
parameters
execution assumptions
output paths
```

---

# 21. Agent working contract

Before changing or running anything, an agent must:

```text
1. read this document;
2. read the active TSIS data contracts;
3. declare the dataset and price view;
4. state the exact scope;
5. list assumptions;
6. avoid modifying RAW;
7. produce manifests and validation outputs;
8. distinguish fact, assumption and limitation.
```

An agent may not call a strategy robust without completing the robustness protocol.

---

# 22. Definition of done

The backtesting foundation is ready when:

```text
the same run is reproducible;
the historical universe is point-in-time;
all inputs are temporally legal;
orders and fills are separate;
PnL is independently verifiable;
costs and execution assumptions are explicit;
halts and missing bars have defined policies;
short availability is not assumed silently;
results include manifests and ledgers;
robustness tests are completed;
limitations are documented.
```

The objective is not to build an attractive platform.

The objective is to make it difficult for a false edge to survive.
