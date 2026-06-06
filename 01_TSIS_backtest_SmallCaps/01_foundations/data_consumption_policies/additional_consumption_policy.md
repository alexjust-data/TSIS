# Additional Consumption Policy - Modulo 01

## 1. Rol

This policy defines how `additional` may be consumed inside module 01.

It does not replace the dataset contract. It operationalizes it.

## 2. Principle

`additional` is not one dataset. It is a composite auxiliary block.

Consumption must distinguish:

- financial statements
- ratios
- news
- IPOs
- corporate actions
- macro/economic series

## 3. Allowed Use By Subblock

### financials_core

Includes:

- `income_statements`
- `balance_sheets`
- `cash_flow_statements`

Status: `good`.

Allowed for:

- `research_only`
- `backtest_extended`
- `ml_flagged`
- factor/context research

Not automatically allowed for:

- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

### financials_ratios

Includes:

- `ratios`

Status: `review`.

Allowed for:

- `research_only`
- sparse auxiliary context

Not allowed as:

- primary valuation/fundamentals layer
- mandatory feature with universal coverage assumption

### news

Status: `good/review`.

Allowed for:

- causal overlay
- halt/anomaly context
- forensic explanation
- research-only event studies

Rules:

- strongest class is `news_near_halt_market_event`
- multi-ticker news must carry attribution ambiguity
- `published_utc` must be aligned to market timezone before intraday causal claims
- same-day news is not causal proof if market disorder predates publication

### ipos

Status: `good/review`.

Allowed for:

- early-life behavior analysis
- IPO fragility context
- halt/anomaly overlay

Rules:

- strongest class is `ipo_near_halt_market_event`
- `ipo_market_clean` is context, not causal proof

### corporate_actions_additional

Includes:

- `splits`
- `dividends`
- `ticker_events`

Status: `review`.

Allowed for:

- secondary confirmation
- reference overlap review
- ticker event investigation

Not allowed as:

- primary split/dividend adjustment source
- replacement for `reference`

### economic

Includes:

- `inflation`
- `inflation_expectations`
- `treasury_yields`

Status:

- `good` as macro dataset
- `review` as direct ticker-level causal layer

Allowed for:

- macro/regime overlay
- date-level context
- broad market state analysis

Not allowed as:

- direct ticker causal proof without an additional model/contract

## 4. Empty Sentinel Rule

Ticker-based additional datasets may contain empty sentinel rows:

- `ticker`
- `_empty`
- `_dataset`
- `_ingested_utc`

These are valid no-data outputs.

Consumers must use effective non-empty coverage, not files-present coverage, to assess usefulness.

## 5. Merge Reading Rule

Consumers must not rely on blind directory-level dataset merging when it triggers partition/schema conflicts.

Preferred read discipline:

- read physical files directly
- preserve partition ticker separately from payload ticker
- validate `_empty` before counting business rows

## 6. Final Rule

`additional` may be used as an auxiliary institutional block.

It must not be promoted as a uniform core dataset. The most restrictive applicable subblock status governs consumption.
