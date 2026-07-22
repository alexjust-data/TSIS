# Daily Adjusted Consumption Policy v0.1

## 1. Scope

This policy governs:

```text
daily_adjusted_v0_1
```

Physical root:

```text
E:/TSIS/data/ohlcv_daily_adjusted
```

## 2. Primary Rule

`daily_adjusted_v0_1` is a derived ETL price view.

It is not raw daily data.

It is not quote, trade, book, tape or execution authority.

## 3. Allowed Uses

Allowed:

- slow economic daily returns;
- daily return labels when the label contract says so;
- split/dividend-aware daily research;
- daily-level historical analytics;
- CAPA 1 data-quality reporting;
- forensic comparison against raw daily.

## 4. Restricted Uses

Restricted:

- feature engineering that requires decision-time raw prices;
- anything that mixes raw and adjusted price views without explicit declaration;
- daily-to-intraday joins without a price-view bridge.

## 5. Prohibited Uses

Prohibited by default:

- execution simulation;
- raw intraday truth;
- quote/trade validation;
- live trading feed substitute;
- RL state source without a dedicated downstream contract;
- replacement for raw `daily`.

## 6. Required Consumer Rules

Consumers must:

- declare this is an adjusted daily view;
- preserve adjustment factors when needed;
- avoid mixing raw close and adjusted close silently;
- use raw daily when raw price truth is required;
- use `reference` as the upstream corporate-action authority;
- preserve known corporate-action tail restrictions.

## 7. Current Evidence

Primary evidence:

- `inspection_dossiers/daily/daily_adjusted_full_universe_audit_v0_1.md`
- `inspection_dossiers/daily/daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md`
- `contract_registry/dataset_contracts/daily_adjusted_dataset_contract_v0_1.md`
- `dataset_registry/daily/daily_adjusted_registry_entry.yaml`
- `canonical_schemas/daily/daily_adjusted_schema_contract.md`

## 8. Current Status

Current status:

```text
promoted_full_universe_derived_daily_price_view
```

The full-universe audit reports:

- 100% ticker-with-files coverage against raw daily files;
- 100% year-file coverage;
- no read errors;
- no missing required columns;
- no nonpositive factor rows;
- no bad price-view rows.

## 9. Final Rule

`daily_adjusted_v0_1` is allowed as an institutional adjusted daily view for declared daily consumers.

It must not be used as raw market truth.
