# Regime Index Bars Schema Contract

Status: canonical schema contract for index regime indicator bars under `D:\regime_indicators\indices`.

## Purpose

This contract defines the physical and logical schema for index regime indicator bar files. These instruments are broad-market/sector regime proxies.

The dataset contains daily bars for all observed indices and minute bars for a subset.

## Physical Layout

Observed root:

`D:\regime_indicators\indices\<INDEX_SYMBOL_DIRECTORY>`

Observed index directories:

| Directory | Logical symbol |
|---|---|
| `I_COMP` | `I:COMP` |
| `I_NDX` | `I:NDX` |
| `I_SOX` | `I:SOX` |

Observed file availability:

| Directory | Files |
|---|---|
| `I_COMP` | `day.parquet`, `minute.parquet` |
| `I_NDX` | `day.parquet`, `minute.parquet` |
| `I_SOX` | `day.parquet` |

## Minute Bar Schema

Observed representative file:

`D:\regime_indicators\indices\I_NDX\minute.parquet`

Observed rows: 25701.

Canonical columns:

| Column | Logical role | Type expectation |
|---|---|---|
| `timestamp` | minute timestamp | timestamp |
| `open` | minute open index level | numeric |
| `high` | minute high index level | numeric |
| `low` | minute low index level | numeric |
| `close` | minute close index level | numeric |

Index minute files do not include `volume` or `vwap` in the observed schema.

Representative timestamp evidence ranges from `2023-08-01 13:30:00` to `2025-12-01 22:15:00`.

## Daily Bar Schema

Observed representative files:

- `D:\regime_indicators\indices\I_NDX\day.parquet`
- `D:\regime_indicators\indices\I_SOX\day.parquet`

Observed rows per representative daily index file: 705.

Observed columns:

| Column | Logical role | Type expectation |
|---|---|---|
| `open` | daily open index level | numeric |
| `close` | daily close index level | numeric |
| `high` | daily high index level | numeric |
| `low` | daily low index level | numeric |
| `datetime` | intended daily timestamp | timestamp |
| `date` | intended daily date | date |

## Known Blocking Issue: Daily Dates

All observed index `day.parquet` files have `date = 1970-01-01` for every row and `datetime` values clustered in 1970. This makes the daily timestamp/date columns semantically invalid as calendar keys.

The daily files are structurally readable but must not be used as point-in-time regime inputs until the date semantics are repaired or externally reconstructed under a documented contract.

## Canonical Keys

Minute bars:

`logical_symbol + timestamp`

Daily bars, after repair only:

`logical_symbol + date`

Until daily date repair is documented, no valid daily key exists inside the physical daily files.

## Required Consumer Rules

- Map directory names back to logical index symbols using `I_COMP -> I:COMP`, `I_NDX -> I:NDX`, `I_SOX -> I:SOX`.
- Do not expect index minute bars to contain volume or VWAP.
- Do not consume index daily files using their current `date` or `datetime` columns.
- Treat missing `I_SOX\minute.parquet` as observed dataset availability, not as a read failure.

## Verdict

Index minute bars have a coherent physical schema for available symbols. Index daily bars have a coherent column layout but a blocking date-semantics defect and are not certified as usable daily regime inputs.
