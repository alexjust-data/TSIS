# DAILY - Parquet Content Sample

## Purpose

This document prints a small human-readable sample from one parquet file that represents this audit folder.
It is a navigation and inspection aid, not a data certification artifact.

## Source

| item | value |
| --- | --- |
| source_parquet | `E:\TSIS\data\ohlcv_daily\ticker=A\year=2005\day_aggs_A_2005.parquet` |
| parquet_rows | 252 |
| parquet_columns | 11 |
| row_groups | 1 |

## Sample Selection

One available ticker/year parquet from the daily OHLCV tree.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `ticker` | `string` |
| 1 | `date` | `string` |
| 2 | `year` | `int64` |
| 3 | `o` | `double` |
| 4 | `h` | `double` |
| 5 | `l` | `double` |
| 6 | `c` | `double` |
| 7 | `v` | `double` |
| 8 | `vw` | `double` |
| 9 | `n` | `int64` |
| 10 | `t` | `int64` |

## Printed Sample

This is a printed content sample only. It does not certify the whole folder.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `ticker` | A | A | A | A | A |
| `date` | 2005-01-03 | 2005-01-04 | 2005-01-05 | 2005-01-06 | 2005-01-07 |
| `year` | 2005 | 2005 | 2005 | 2005 | 2005 |
| `o` | 17.2389 | 17.01 | 16.5737 | 16.7382 | 16.2232 |
| `h` | 17.2961 | 17.1602 | 16.917 | 16.7668 | 16.4163 |
| `l` | 16.8097 | 16.4878 | 16.5379 | 16.2303 | 16.1874 |
| `c` | 17.0815 | 16.6309 | 16.6237 | 16.2589 | 16.2446 |
| `v` | 3378966.0 | 3746919.6 | 3899161.8 | 3158781.0 | 2624325.6 |
| `vw` | 17.0712 | 16.8187 | 16.7566 | 16.429 | 16.2616 |
| `n` | 3498 | 3356 | 3589 | 3396 | 2890 |
| `t` | 1104728400000 | 1104814800000 | 1104901200000 | 1104987600000 | 1105074000000 |

## Interpretation

Use this file to understand the physical shape and example values of the represented parquet family.
For completeness, pass/fail status, and official scope, use the corresponding audit dossier and project-level status documentation.
