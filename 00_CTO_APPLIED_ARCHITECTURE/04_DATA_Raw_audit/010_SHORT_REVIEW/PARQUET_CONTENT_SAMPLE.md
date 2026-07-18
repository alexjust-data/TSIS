# SHORT REVIEW - Parquet Content Sample

## Purpose

This document prints a small human-readable sample from one parquet file that represents this audit folder.
It is a navigation and inspection aid, not a data certification artifact.

## Source

| item | value |
| --- | --- |
| source_parquet | `E:\TSIS\data\short_review\finra_short\artifacts\short_interest_all_biweekly_finra.parquet` |
| parquet_rows | 505745 |
| parquet_columns | 5 |
| row_groups | 1 |

## Sample Selection

One available parquet from the short review FINRA artifacts tree.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `settlement_date` | `timestamp[ns]` |
| 1 | `ticker` | `string` |
| 2 | `short_interest` | `int64` |
| 3 | `avg_daily_volume` | `int64` |
| 4 | `days_to_cover` | `double` |

## Printed Sample

This is a printed content sample only. It does not certify the whole folder.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `settlement_date` | 2023-06-15T00:00:00 | 2023-06-30T00:00:00 | 2023-07-31T00:00:00 | 2023-08-15T00:00:00 | 2023-08-31T00:00:00 |
| `ticker` | AACT | AACT | AACT | AACT | AACT |
| `short_interest` | 101578 | 1572 | 25385 | 86 | 4241 |
| `avg_daily_volume` | 255782 | 190387 | 38565 | 60149 | 417016 |
| `days_to_cover` | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |

## Interpretation

Use this file to understand the physical shape and example values of the represented parquet family.
For completeness, pass/fail status, and official scope, use the corresponding audit dossier and project-level status documentation.
