# Additional Economic Schema Contract

Status: canonical schema contract for `E:\TSIS\data\additional\economic`.

## Purpose

`additional\economic` stores non-ticker macro series from Polygon/Fed endpoints. It is a macro/regime overlay, not ticker-level causal evidence by itself.

## Physical Layout

Observed root:

`E:\TSIS\data\additional\economic`

Observed files:

- `inflation.parquet`
- `inflation_expectations.parquet`
- `treasury_yields.parquet`

## Inflation

Observed rows: 950.

Observed date range: `1947-01-01` to `2026-02-01`.

Observed columns:

`date`, `cpi`, `cpi_year_over_year`, `cpi_core`, `pce`, `pce_core`, `pce_spending`, `_dataset`, `_ingested_utc`.

Canonical key:

`dataset + date`

## Inflation Expectations

Observed rows: 531.

Observed date range: `1982-01-01` to `2026-03-01`.

Observed columns:

`date`, `model_1_year`, `model_5_year`, `model_10_year`, `model_30_year`, `market_5_year`, `market_10_year`, `forward_years_5_to_10`, `_dataset`, `_ingested_utc`.

Canonical key:

`dataset + date`

## Treasury Yields

Observed rows: 16047.

Observed date range: `1962-01-02` to `2026-04-02`.

Observed columns:

`date`, `yield_1_year`, `yield_5_year`, `yield_10_year`, `yield_2_year`, `yield_30_year`, `yield_3_month`, `yield_1_month`, `_dataset`, `_ingested_utc`.

Canonical key:

`dataset + date`

## Required Consumer Rules

- Use as macro/regime overlay.
- Do not infer direct ticker-level causality from this layer alone.
- Align by calendar date with explicit lag/availability assumptions.
- Preserve missing macro values as missing.

## Verdict

`additional\economic` is structurally good as a macro dataset. It remains review for direct ticker-level causal attribution.
