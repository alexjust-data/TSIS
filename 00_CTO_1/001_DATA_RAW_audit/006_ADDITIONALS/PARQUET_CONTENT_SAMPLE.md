# ADDITIONALS - Parquet Content Sample

## Purpose

This document prints a small human-readable sample from one parquet file that represents this audit folder.
It is a navigation and inspection aid, not a data certification artifact.

## Source

| item | value |
| --- | --- |
| source_parquet | `E:\TSIS\data\additional\corporate_actions\dividends\ticker=AACT\dividends_AACT.parquet` |
| parquet_rows | 1 |
| parquet_columns | 4 |
| row_groups | 1 |

## Sample Selection

One available parquet from the additional corporate actions tree.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `ticker` | `string` |
| 1 | `_empty` | `bool` |
| 2 | `_dataset` | `string` |
| 3 | `_ingested_utc` | `string` |

## Printed Sample

This is a printed content sample only. It does not certify the whole folder.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 |
| --- | --- |
| `ticker` | AACT |
| `_empty` | True |
| `_dataset` | dividends |
| `_ingested_utc` | 2026-04-05T18:21:09.142400+00:00 |

## Interpretation

Use this file to understand the physical shape and example values of the represented parquet family.
For completeness, pass/fail status, and official scope, use the corresponding audit dossier and project-level status documentation.
