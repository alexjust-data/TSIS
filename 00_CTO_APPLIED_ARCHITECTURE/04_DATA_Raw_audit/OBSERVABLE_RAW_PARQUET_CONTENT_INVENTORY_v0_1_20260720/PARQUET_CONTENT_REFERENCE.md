# REFERENCE - Parquet Content Sample

## Purpose

This document prints a small human-readable sample from one parquet file that represents this audit folder.
It is a navigation and inspection aid, not a data certification artifact.

## Source

| item | value |
| --- | --- |
| source_parquet | `E:\TSIS\data\reference\all_tickers\snapshot_date=2005-01-02.parquet` |
| parquet_rows | 2632 |
| parquet_columns | 16 |
| row_groups | 1 |

## Sample Selection

One available parquet from the reference all-tickers snapshot tree.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `ticker` | `large_string` |
| 1 | `name` | `large_string` |
| 2 | `market` | `large_string` |
| 3 | `locale` | `large_string` |
| 4 | `primary_exchange` | `large_string` |
| 5 | `type` | `large_string` |
| 6 | `active` | `bool` |
| 7 | `currency_name` | `large_string` |
| 8 | `cik` | `large_string` |
| 9 | `composite_figi` | `large_string` |
| 10 | `share_class_figi` | `large_string` |
| 11 | `last_updated_utc` | `large_string` |
| 12 | `snapshot_date` | `large_string` |
| 13 | `_exchange_filter` | `large_string` |
| 14 | `_dataset` | `large_string` |
| 15 | `_ingested_utc` | `large_string` |

## Printed Sample

This is a printed content sample only. It does not certify the whole folder.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `ticker` | A | AA | AAA | AAI | AAP |
| `name` | AGILENT TECHNOLOGIES, INC | ALCOA INC | ALTANA AKTIENGESELLSCHAFT SPON ADR | AIRTRAN HOLDINGS INC | ADVANCE AUTO PARTS INC |
| `market` | stocks | stocks | stocks | stocks | stocks |
| `locale` | us | us | us | us | us |
| `primary_exchange` | XNYS | XNYS | XNYS | XNYS | XNYS |
| `type` | CS | CS | CS | CS | CS |
| `active` | True | True | True | True | True |
| `currency_name` | usd | usd | usd | usd | usd |
| `cik` | 0001090872 | 0000004281 |  | 0000948846 | 0001158449 |
| `composite_figi` | BBG000C2V3D6 |  |  |  | BBG000F7RCJ1 |
| `share_class_figi` | BBG001SCTQY4 |  |  |  | BBG001SD2SB2 |
| `last_updated_utc` | 2025-01-16T17:24:39.467326Z | 2025-01-16T17:24:39.468845Z | 2025-01-16T17:24:39.469061Z | 2025-01-16T17:24:39.469072Z | 2025-01-16T17:24:39.468415Z |
| `snapshot_date` | 2005-01-02 | 2005-01-02 | 2005-01-02 | 2005-01-02 | 2005-01-02 |
| `_exchange_filter` | XNYS | XNYS | XNYS | XNYS | XNYS |
| `_dataset` | all_tickers | all_tickers | all_tickers | all_tickers | all_tickers |
| `_ingested_utc` | 2026-03-11T10:28:25.701670+00:00 | 2026-03-11T10:28:25.701670+00:00 | 2026-03-11T10:28:25.701670+00:00 | 2026-03-11T10:28:25.701670+00:00 | 2026-03-11T10:28:25.701670+00:00 |

## Interpretation

Use this file to understand the physical shape and example values of the represented parquet family.
For completeness, pass/fail status, and official scope, use the corresponding audit dossier and project-level status documentation.
