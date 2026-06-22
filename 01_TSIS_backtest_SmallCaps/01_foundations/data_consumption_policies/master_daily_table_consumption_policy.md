# Master Daily Table Consumption Policy `v0_1`

## 1. Scope

Dataset:

```text
master_daily_table_v0_1
```

## 2. Permitted Meaning

This table is the governed daily context table for CAPA 1.

Consumers may use it for:

- daily event context;
- prior close and gap;
- daily return and range;
- dollar volume and RVOL;
- split/dividend/ticker-change day flags;
- price-view-aware daily research;
- backtest candidate filtering.

## 3. Required Price-View Discipline

Consumers must choose explicitly:

- `daily_raw` for raw observed daily price context;
- `split_normalized` for split-comparable daily price context;
- `adjusted` for economic return and benchmark context.

Consumers must not silently mix:

- raw close with adjusted close;
- adjusted daily prices with raw intraday execution;
- raw VWAP with adjusted price fields.

## 4. Consumer Classes

Permitted:

- `event_engine`
- `outcome_research`
- `backtest_core`
- `backtest_extended`
- `ml_primary`
- `ml_flagged`
- `research_only`
- `forensic_only`

Restricted:

- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

## 5. Row-Level Gates

`backtest_core` may use only rows where:

```text
backtest_core_row_candidate = true
```

That requires:

- `data_present = true`;
- `selected_price_hard_invalid = false`;
- `negative_volume = false`;
- `family_production_use_gate = declared_scope_allowed`.

`missing_expected_data = true` rows are not usable market observations. They
exist to preserve coverage accounting.

## 6. ML Rules

`ml_primary` may consume selected daily fields only when:

- price view is declared;
- row candidate flag is true;
- label leakage is avoided;
- downstream feature builder preserves `price_view`, `schema_version`,
  `build_run_id` and quality gates.

`ml_flagged` may include missing/review context only as masks, sample metadata
or explicit quality features.

## 7. Prohibited Uses

This table must not be used as:

- quote book;
- trade tape;
- execution simulator input;
- raw intraday truth;
- live feed substitute;
- full fundamentals/news/short/regime source.

## 8. Final Rule

`master_daily_table` makes daily state easy to consume. It does not remove the
need to respect raw/adjusted price semantics, row flags and downstream leakage
rules.

