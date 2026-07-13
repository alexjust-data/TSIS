# TRADES - Parquet Content Sample

## Purpose

This document prints a small human-readable sample from one parquet file that represents this audit folder.
It is a navigation and inspection aid, not a data certification artifact.

## Source

| item | value |
| --- | --- |
| source_parquet | `E:\TSIS\data\trades_ticks_prod_2005_2026\AATC\year=2025\month=05\day=2025-05-12\market.parquet` |
| parquet_rows | 36 |
| parquet_columns | 10 |
| row_groups | 1 |

## Sample Selection

One available ticker/day parquet from the trades tick production tree.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `ticker` | `string` |
| 1 | `date` | `string` |
| 2 | `timestamp` | `timestamp[us]` |
| 3 | `price` | `double` |
| 4 | `size` | `int64` |
| 5 | `exchange` | `int64` |
| 6 | `conditions` | `list<element: int64>` |
| 7 | `year` | `int64` |
| 8 | `month` | `int64` |
| 9 | `day` | `string` |

## Printed Sample

This is a printed content sample only. It does not certify the whole folder.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `ticker` | AATC | AATC | AATC | AATC | AATC |
| `date` | 2025-05-12 | 2025-05-12 | 2025-05-12 | 2025-05-12 | 2025-05-12 |
| `timestamp` | 2025-05-12T13:30:18.770626 | 2025-05-12T13:37:28.376394 | 2025-05-12T13:38:12.861039 | 2025-05-12T13:45:00.245259 | 2025-05-12T13:45:01.106921 |
| `price` | 7.605 | 7.62 | 7.605 | 7.61 | 7.604 |
| `size` | 3 | 42 | 2 | 1 | 1 |
| `exchange` | 62 | 62 | 62 | 62 | 62 |
| `conditions` | [37] | [37] | [37] | [37] | [37] |
| `year` | 2025 | 2025 | 2025 | 2025 | 2025 |
| `month` | 5 | 5 | 5 | 5 | 5 |
| `day` | 2025-05-12 | 2025-05-12 | 2025-05-12 | 2025-05-12 | 2025-05-12 |

## Interpretation

Use this file to understand the physical shape and example values of the represented parquet family.
For completeness, pass/fail status, and official scope, use the corresponding audit dossier and project-level status documentation.
