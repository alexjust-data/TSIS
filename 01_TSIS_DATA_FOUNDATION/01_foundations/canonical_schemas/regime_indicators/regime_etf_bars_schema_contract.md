# Regime ETF Bars Schema Contract

Status: canonical schema contract for ETF regime indicator bars under `D:\regime_indicators\etfs`.

## Purpose

This contract defines the physical and logical schema for ETF regime indicator bar files. These instruments are market/regime proxies, not part of the small-cap tradable universe itself.

The dataset contains daily and minute bars by ETF symbol.

## Physical Layout

Observed root:

`D:\regime_indicators\etfs\<ETF_SYMBOL>`

Observed files per ETF:

- `day.parquet`
- `minute.parquet`

Observed ETF symbols:

`DIA`, `EEM`, `EFA`, `FXE`, `GLD`, `HYG`, `IWM`, `LQD`, `QQQ`, `SLV`, `SPSM`, `SPY`, `TLT`, `UNG`, `USO`, `UUP`, `UVXY`, `VB`, `VIXY`, `VXX`, `XLB`, `XLC`, `XLE`, `XLF`, `XLI`, `XLK`, `XLP`, `XLRE`, `XLU`, `XLV`, `XLY`.

## Minute Bar Schema

Observed representative file:

`D:\regime_indicators\etfs\SPY\minute.parquet`

Observed rows: 4021590.

Canonical columns:

| Column | Logical role | Type expectation |
|---|---|---|
| `timestamp` | minute timestamp | timestamp |
| `open` | minute open price | numeric |
| `high` | minute high price | numeric |
| `low` | minute low price | numeric |
| `close` | minute close price | numeric |
| `volume` | minute volume | numeric |
| `vwap` | minute VWAP | numeric |

Minute timestamp evidence in the representative file ranges from `2004-01-02 13:00:00` to `2025-12-02 14:27:00`.

## Daily Bar Schema

Observed representative file:

`D:\regime_indicators\etfs\SPY\day.parquet`

Observed rows: 5593.

Observed columns:

| Column | Logical role | Type expectation |
|---|---|---|
| `volume` | daily volume | numeric |
| `vwap` | daily VWAP | numeric |
| `open` | daily open price | numeric |
| `close` | daily close price | numeric |
| `high` | daily high price | numeric |
| `low` | daily low price | numeric |
| `trades` | daily trade count | int |
| `datetime` | intended daily timestamp | timestamp |
| `date` | intended daily date | date |

## Known Blocking Issue: Daily Dates

All observed ETF `day.parquet` files have `date = 1970-01-01` for every row and `datetime` values clustered in 1970. This makes the daily timestamp/date columns semantically invalid as calendar keys.

The daily files are structurally readable but must not be used as point-in-time regime inputs until the date semantics are repaired or externally reconstructed under a documented contract.

## Canonical Keys

Minute bars:

`symbol + timestamp`

Daily bars, after repair only:

`symbol + date`

Until daily date repair is documented, no valid daily key exists inside the physical daily files.

## Required Consumer Rules

- Treat the directory name as the ETF symbol; the files do not contain a symbol column.
- Use minute ETF files only when timestamp coverage and price sanity are validated for the required window.
- Do not consume ETF daily files using their current `date` or `datetime` columns.
- Do not treat ETF regime indicators as tradable small-cap securities.

## Verdict

ETF minute bars have a coherent physical schema. ETF daily bars have a coherent column layout but a blocking date-semantics defect and are not certified as usable daily regime inputs.
