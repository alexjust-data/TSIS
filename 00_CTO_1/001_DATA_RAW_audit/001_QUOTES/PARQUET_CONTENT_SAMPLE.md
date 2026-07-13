# QUOTES - Parquet Content Sample

## Purpose

This document prints a small human-readable sample from one parquet file that represents this audit folder.
It is a navigation and inspection aid, not a data certification artifact.

## Source

| item | value |
| --- | --- |
| source_parquet | `E:\TSIS\data\quotes_\AABA\year=2017\month=06\day=19\quotes.parquet` |
| parquet_rows | 156436 |
| parquet_columns | 16 |
| row_groups | 4 |

## Sample Selection

One available ticker/day parquet from the quotes tree.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `ask_exchange` | `int64` |
| 1 | `ask_price` | `double` |
| 2 | `ask_size` | `int64` |
| 3 | `bid_exchange` | `int64` |
| 4 | `bid_price` | `double` |
| 5 | `bid_size` | `int64` |
| 6 | `conditions` | `large_list<element: int64>` |
| 7 | `indicators` | `large_list<element: int64>` |
| 8 | `participant_timestamp` | `int64` |
| 9 | `sequence_number` | `int64` |
| 10 | `timestamp` | `int64` |
| 11 | `tape` | `int64` |
| 12 | `trf_timestamp` | `int64` |
| 13 | `year` | `int32` |
| 14 | `month` | `int32` |
| 15 | `day` | `int32` |

## Printed Sample

This is a printed content sample only. It does not certify the whole folder.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `ask_exchange` | 0 | 0 | 0 | 0 | 0 |
| `ask_price` | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| `ask_size` | 0 | 0 | 0 | 0 | 0 |
| `bid_exchange` | 12 | 12 | 12 | 12 | 12 |
| `bid_price` | 52.58 | 52.7 | 52.82 | 52.95 | 53.0 |
| `bid_size` | 100 | 100 | 100 | 100 | 100 |
| `conditions` | [1] | [1] | [1] | [1] | [1] |
| `indicators` | [] | [] | [] | [] | [] |
| `participant_timestamp` | 1497859670896653506 | 1497859698805110500 | 1497859737580851849 | 1497860045561475015 | 1497860319572635199 |
| `sequence_number` | 5288 | 5479 | 5861 | 7548 | 8586 |
| `timestamp` | 1497859670896675723 | 1497859698805130110 | 1497859737580871610 | 1497860045561494378 | 1497860319572657996 |
| `tape` | 3 | 3 | 3 | 3 | 3 |
| `trf_timestamp` |  |  |  |  |  |
| `year` | 2017 | 2017 | 2017 | 2017 | 2017 |
| `month` | 6 | 6 | 6 | 6 | 6 |
| `day` | 19 | 19 | 19 | 19 | 19 |

## Interpretation

Use this file to understand the physical shape and example values of the represented parquet family.
For completeness, pass/fail status, and official scope, use the corresponding audit dossier and project-level status documentation.
