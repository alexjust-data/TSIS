# Financial Consumption Policy v0.1

## 1. Scope

This policy governs:

```text
financial_v0_1
```

Physical root:

```text
E:/TSIS/data/financial
```

It applies to:

- balance sheets;
- cash flow statements;
- income statements;
- ratios;
- operational audit artifacts;
- operational run artifacts.

## 2. Primary Rule

`financial_v0_1` is blocked for non-audit consumption while the operational audit reports:

```text
status = FAIL
```

Coverage completeness does not override audit failure.

## 3. Allowed Current Uses

Allowed:

- data-quality reporting;
- source validation;
- forensic review;
- schema review;
- repair planning;
- validator design;
- blocked research inspection.

Allowed outputs:

- audit summaries;
- quality tables;
- remediation plans;
- blocked/provisional flags.

## 4. Non-Enabled Uses

Not enabled:

- `master_daily_table`;
- `symbol_master`;
- `backtest_core`;
- `backtest_extended`;
- `ml_primary`;
- `ml_flagged`;
- `execution_simulator`;
- `rl_allowed`;
- `live_downstream_candidate`.

No feature pipeline may consume this root as clean fundamentals until a revised report explicitly promotes the required subfamily.

## 5. Empty Sentinel Rule

Financial files may contain empty sentinel rows:

```text
ticker
_empty
_dataset
_ingested_utc
```

Consumers must not count empty sentinels as business observations.

Current blocker:

- schema contracts describe empty sentinels as valid;
- the operational audit currently flags many zero-business statement files as `missing_required_cols`;
- this mismatch must be reconciled before promotion.

Until resolved, the most conservative reading applies:

```text
empty sentinel files are structurally recognized but not promotion-clean.
```

## 6. Statement Rules

For:

- `income_statements`
- `balance_sheets`
- `cash_flow_statements`

Consumers must:

- use `filing_date` as point-in-time availability;
- preserve `period_end` as accounting period, not market availability;
- preserve `cik` and ticker alias fields as identity risk evidence;
- avoid forward-fill across lifecycle boundaries;
- not convert missing accounting values to zero;
- surface restatements and duplicate keys instead of collapsing silently.

## 7. Ratio Rules

For `ratios`:

- treat ratios as vendor-derived financial/valuation snapshots;
- do not treat ratio `price` as TSIS OHLCV authority;
- do not treat `market_cap` as official point-in-time universe membership;
- do not assume universal coverage;
- do not use ratios as substitutes for accounting statement fields.

## 8. Temporal And Lifecycle Rules

Any downstream use must resolve or flag:

- `ANOMALY_PRE_START`;
- `ANOMALY_POST_END`;
- `NO_DATA`;
- CIK/lifecycle conflicts;
- ticker reuse;
- official list/delist boundaries.

The current temporal issue counts are blocking:

| Status | Tickers |
| --- | ---: |
| `ANOMALY_PRE_START` | 2,244 |
| `ANOMALY_POST_END` | 927 |

## 9. Root Drift Rule

Current financial schema contracts still mention `D:/financial`.

The current audited physical root for this policy is:

```text
E:/TSIS/data/financial
```

Consumers must not infer equivalence between roots without an explicit root audit or migration note.

## 10. Promotion Gate

Promotion requires:

1. revised or accepted validator output;
2. documented resolution of `audit_summary.status = FAIL`;
3. explicit handling of empty sentinel files;
4. temporal/lifecycle issue policy;
5. per-subfamily consumer matrix;
6. updated `financial_quality_report`;
7. changelog or promotion note.

## 11. Final Rule

`financial_v0_1` may explain data quality and remediation needs.

It must not silently feed research, backtests, ML, RL, execution, live systems or master tables until the blocking audit state is resolved.
