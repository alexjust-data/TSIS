# Halts Raw Sources Schema Contract

Status: raw source schema contract for `D:\Halts\raw`.

## Purpose

This contract documents the raw halt/suspension source artifacts preserved under `D:\Halts\raw`. These files are source evidence used to build processed halt masters.

Raw source files must not be consumed directly by research modules unless a parser/normalization contract is explicitly applied.

## Physical Layout

Observed raw roots:

- `D:\Halts\raw\nasdaq`
- `D:\Halts\raw\nasdaq_rss_by_date`
- `D:\Halts\raw\nyse`
- `D:\Halts\raw\sec`

## Nasdaq RSS Raw Files

Observed root:

`D:\Halts\raw\nasdaq_rss_by_date`

Observed file pattern:

`<MMDDYYYY>.xml`

Observed count: 5662 XML files.

These files are raw Nasdaq Trader RSS responses by requested halt date. The processed raw CSV records request date, RSS title/publication data, raw description text and parse diagnostics.

## NYSE Raw Files

Observed files:

- `D:\Halts\raw\nyse\nyse_current_2026-03-13.csv`
- `D:\Halts\raw\nyse\nyse_historical_2025-03-13_to_2026-03-13.csv`
- `D:\Halts\raw\nyse\nyse_static_data.json`

NYSE CSV columns:

| Column | Logical role |
|---|---|
| `Halt Date` | event date |
| `Halt Time` | halt time |
| `Symbol` | ticker/symbol |
| `Name` | issuer/security name |
| `Exchange` | listing exchange |
| `Reason` | halt reason |
| `Resume Date` | resume date |
| `NYSE Resume Time` | NYSE resume time |

NYSE static JSON fields:

| Field | Logical role |
|---|---|
| `reasonCodes` | known NYSE reason labels |
| `exchanges` | known exchange labels |

## SEC Raw Files

Observed root:

`D:\Halts\raw\sec`

Observed file pattern:

`sec_trading_suspensions_page_<NN>.html`

These files are raw SEC trading suspension pages. Processed SEC outputs extract issuer name, release number, item link, event date and optional ticker.

## Required Consumer Rules

- Treat raw XML/HTML/CSV/JSON as immutable source evidence.
- Use processed contracts for downstream consumption.
- Preserve raw files for reproducibility and parser re-runs.
- Do not delete raw source evidence after master generation.

## Verdict

`D:\Halts\raw` contains the preserved source layer for Nasdaq, NYSE and SEC halt/suspension evidence. It is structurally coherent as provenance, not as canonical research input.
