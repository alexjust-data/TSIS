# Regime Indicators Quality Notes

Status: quality note attached to `D:\regime_indicators` canonical schema review.

## Scope

This note records observed structural quality findings from representative and global schema inspection of `D:\regime_indicators`.

## Observed Inventory

Root contents:

- `etfs`
- `indices`
- `download_metadata.json`
- `ticker_ranges.json`

Observed file counts:

- JSON files: 2
- Parquet files: 67

Observed `day.parquet` files: 34.

Observed symbols in `ticker_ranges.json`: 34.

## Positive Findings

- ETF minute files have consistent columns: `timestamp`, `open`, `high`, `low`, `close`, `volume`, `vwap`.
- Index minute files have consistent index-level columns: `timestamp`, `open`, `high`, `low`, `close`.
- Directory structure cleanly separates `etfs` from `indices`.
- `ticker_ranges.json` provides explicit detected ranges for the regime symbol set.

## Blocking Finding

All 34 observed `day.parquet` files have invalid daily date semantics:

- `date` minimum: `1970-01-01`
- `date` maximum: `1970-01-01`
- `date` unique values: 1
- `datetime` values are also clustered in 1970

This affects both ETF and index daily files.

## Institutional Interpretation

`D:\regime_indicators` cannot be promoted as a clean daily regime-indicator dataset in its current state.

Minute regime bars can be considered structurally readable, subject to downstream price sanity and coverage validation.

Daily regime bars must be treated as blocked until a documented repair or re-materialization restores valid calendar dates.

## Required Next Audit Step

Before use in research:

1. Decide whether daily files are to be regenerated or repaired from source/raw timestamp fields.
2. Produce an audit showing valid `symbol + date` uniqueness and realistic date ranges.
3. Revisit this contract and update status only after evidence exists.

## Verdict

Regime indicators are partially usable at the schema level: minute files are structurally coherent, daily files are structurally readable but semantically blocked by invalid dates.
