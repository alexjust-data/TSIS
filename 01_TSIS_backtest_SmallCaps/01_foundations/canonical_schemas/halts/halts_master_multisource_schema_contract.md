# Halts Master Multisource Schema Contract

Status: canonical schema contract for `D:\Halts\processed\halts_master_multisource`.

## Purpose

This contract defines the canonical schema for the consolidated trading halt and SEC suspension event master. Each row represents one halt/suspension event from a normalized source feed.

This is an event dataset. It must be consumed as dated market-structure/reference evidence, not as OHLCV, quotes or trades data.

## Physical Layout

Observed files:

- `D:\Halts\processed\halts_master_multisource.parquet`
- `D:\Halts\processed\halts_master_multisource.csv`

Observed representative parquet rows: 133116.

## Canonical Columns

| Column | Logical role | Type expectation |
|---|---|---|
| `source` | normalized source family | string; observed `nasdaq`, `nyse`, `sec` |
| `source_priority` | source precedence/order marker | int |
| `ticker` | event ticker when available | nullable string |
| `issuer_name` | issuer/security name from source | nullable string |
| `listing_exchange` | source-listed exchange/venue | nullable string |
| `halt_date` | event date | nullable timestamp/date |
| `halt_start_et` | halt start timestamp in US Eastern semantics | nullable timestamp |
| `resume_quote_et` | quote-resumption timestamp in US Eastern semantics | nullable timestamp |
| `resume_trade_et` | trade-resumption timestamp in US Eastern semantics | nullable timestamp |
| `halt_code` | source halt code | nullable string |
| `halt_type` | normalized halt/suspension class | nullable string |
| `raw_reason` | source reason text | nullable string |
| `release_no` | SEC release number when source is SEC | nullable string |
| `item_link` | source item URL when available | nullable string |
| `url_source` | feed/list source URL | nullable string |
| `is_sec_suspension` | SEC suspension flag | bool |

## Canonical Event Identity

Recommended logical identity:

`source + ticker + issuer_name + halt_date + halt_start_et + halt_code + release_no + item_link`

Because SEC rows may have missing tickers and source pages may revise links or names, consumers must not rely on `ticker` alone as a unique key.

## Source Semantics

- `nasdaq`: Nasdaq Trader halt RSS/history-derived events.
- `nyse`: NYSE trade halt current/historical source.
- `sec`: SEC trading suspension pages.

`is_sec_suspension = true` is expected for SEC rows and false for exchange halt rows.

## Time Semantics

Columns ending in `_et` must be interpreted as US Eastern time semantics. They are not UTC-normalized timestamps unless a downstream contract explicitly materializes UTC fields.

`halt_date` is the event date and may be present even when intraday timestamps are missing.

## Required Consumer Rules

- Preserve rows with missing `ticker`; SEC suspension evidence can be issuer-name/release driven.
- Do not assume all source families contain quote/trade resumption timestamps.
- Treat `halt_code` values as source-code strings, not numeric codes.
- Use `source` and `is_sec_suspension` to separate exchange halts from SEC suspensions.
- Do not promote source-specific intermediate files over this master without a documented reason.

## Current Observed Evidence

Observed `halts_master_multisource.parquet` has 133116 rows with sources summarized as:

| source | rows | tickers_nonnull |
|---|---:|---:|
| `nasdaq` | 119630 | 119619 |
| `nyse` | 13178 | 13178 |
| `sec` | 1346 | 250 |
| `all` | 133116 | 132009 |

## Verdict

`D:\Halts\processed\halts_master_multisource.parquet` is the canonical consolidated halts/suspensions dataset. It is structurally coherent and should be preferred over raw and source-specific intermediate outputs for downstream consumption.
