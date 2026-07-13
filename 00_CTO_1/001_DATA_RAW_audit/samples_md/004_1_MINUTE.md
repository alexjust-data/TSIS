# 1 MINUTE - Parquet Content Sample

## Purpose

This document prints a small human-readable sample from one parquet file that represents this audit folder.
It is a navigation and inspection aid, not a data certification artifact.

## Source

| item | value |
| --- | --- |
| source_parquet | `E:\TSIS\data\ohlcv_1m\ticker=AAA\year=2005\month=01\minute_aggs_AAA_2005_01.parquet` |
| parquet_rows | 221 |
| parquet_columns | 13 |
| row_groups | 1 |

## Sample Selection

One available ticker/month parquet from the raw 1 minute OHLCV tree.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `ticker` | `string` |
| 1 | `ts_utc` | `string` |
| 2 | `date` | `string` |
| 3 | `year` | `int64` |
| 4 | `month` | `int64` |
| 5 | `o` | `double` |
| 6 | `h` | `double` |
| 7 | `l` | `double` |
| 8 | `c` | `double` |
| 9 | `v` | `double` |
| 10 | `vw` | `double` |
| 11 | `n` | `int64` |
| 12 | `t` | `int64` |

## Printed Sample

This is a printed content sample only. It does not certify the whole folder.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `ticker` | AAA | AAA | AAA | AAA | AAA |
| `ts_utc` | 2005-01-03T14:32:00Z | 2005-01-03T15:49:00Z | 2005-01-03T15:50:00Z | 2005-01-03T15:54:00Z | 2005-01-03T20:56:00Z |
| `date` | 2005-01-03 | 2005-01-03 | 2005-01-03 | 2005-01-03 | 2005-01-03 |
| `year` | 2005 | 2005 | 2005 | 2005 | 2005 |
| `month` | 1 | 1 | 1 | 1 | 1 |
| `o` | 62.8 | 62.85 | 62.88 | 62.9 | 62.8 |
| `h` | 62.8 | 62.86 | 62.89 | 62.9 | 62.8 |
| `l` | 62.8 | 62.85 | 62.88 | 62.9 | 62.8 |
| `c` | 62.8 | 62.86 | 62.89 | 62.9 | 62.8 |
| `v` | 100.0 | 600.0 | 200.0 | 100.0 | 100.0 |
| `vw` | 62.8 | 62.8567 | 62.885 | 62.9 | 62.8 |
| `n` | 1 | 2 | 2 | 1 | 1 |
| `t` | 1104762720000 | 1104767340000 | 1104767400000 | 1104767640000 | 1104785760000 |

## Interpretation

Use this file to understand the physical shape and example values of the represented parquet family.
For completeness, pass/fail status, and official scope, use the corresponding audit dossier and project-level status documentation.
