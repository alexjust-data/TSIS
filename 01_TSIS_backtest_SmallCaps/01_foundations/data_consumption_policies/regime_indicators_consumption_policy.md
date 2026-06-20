# Regime Indicators Consumption Policy v0.1

## 1. Scope

This policy governs:

```text
regime_indicators_v0_1
```

Physical root:

```text
E:/TSIS/data/regime_indicators
```

## 2. Primary Rule

Daily ETF and index files are blocked for consumption until their date semantics are repaired and re-audited.

Minute files are readable at schema level but remain `review/scoped`, not production-approved.

## 3. Daily Bars

Current daily files must not be used for:

- `symbol + date` joins;
- calendar table inputs;
- regime features;
- backtest context;
- ML/RL/live inputs.

Reason:

```text
date = 1970-01-01 for all observed daily rows
```

and `datetime` values are also clustered in 1970.

## 4. Minute Bars

Minute bars may be used only for:

- data-quality inspection;
- timestamp coverage review;
- repair planning;
- scoped research prototypes with explicit warning.

Before feature use, a consumer must validate:

- timestamp range;
- duplicate timestamps;
- monotonicity;
- OHLC sanity;
- volume/VWAP availability where expected;
- timezone/session semantics;
- symbol mapping;
- missing minute coverage.

## 5. Metadata

`download_metadata.json` and `ticker_ranges.json` are coverage/provenance evidence.

They must not be used to silently repair daily bars unless a separate repair contract documents the method and validates the result.

## 6. Symbol Rules

ETF directory names are ETF symbols.

Index directory names must be mapped explicitly:

| Directory | Logical symbol |
| --- | --- |
| `I_COMP` | `I:COMP` |
| `I_NDX` | `I:NDX` |
| `I_SOX` | `I:SOX` |

## 7. Allowed Current Uses

Allowed:

- `data_quality_report`;
- `source_validation`;
- `forensic_review`;
- `repair_planning`;
- minute schema review;
- blocked/scoped research inspection.

Not enabled:

- master daily tables;
- regime feature production;
- backtest core;
- ML/RL/live;
- execution simulator.

## 8. Promotion Gate

Promotion requires:

1. regenerate or repair daily files;
2. demonstrate valid `symbol + date` uniqueness;
3. demonstrate realistic daily date ranges;
4. validate minute bars beyond schema;
5. produce case evidence;
6. update the quality report;
7. update registry, policy and changelog if status changes.

## 9. Final Rule

`regime_indicators_v0_1` may currently explain a data-quality problem.

It must not silently feed daily regime context.
