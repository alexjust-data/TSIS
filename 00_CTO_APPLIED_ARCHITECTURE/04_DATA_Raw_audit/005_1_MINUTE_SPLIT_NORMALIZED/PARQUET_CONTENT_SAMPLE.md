# 1 MINUTE SPLIT NORMALIZED - Parquet Content Sample

## Purpose

This document prints a small human-readable sample from one parquet file that represents this audit folder.
It is a navigation and inspection aid, not a data certification artifact.

## Source

| item | value |
| --- | --- |
| source_parquet | `E:\TSIS\data\ohlcv_1m_split_normalized\ticker=BNGO\year=2025\month=01\minute_aggs_BNGO_2025_01_split_normalized.parquet` |
| parquet_rows | 10560 |
| parquet_columns | 25 |
| row_groups | 1 |

## Sample Selection

One available ticker/month parquet from the split-normalized 1 minute OHLCV tree.

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
| 13 | `future_split_factor` | `double` |
| 14 | `o_split_normalized` | `double` |
| 15 | `h_split_normalized` | `double` |
| 16 | `l_split_normalized` | `double` |
| 17 | `c_split_normalized` | `double` |
| 18 | `vw_split_normalized` | `double` |
| 19 | `materialized_price_view` | `string` |
| 20 | `source_1m_file` | `string` |
| 21 | `source_splits_file` | `string` |
| 22 | `pilot_role` | `string` |
| 23 | `pilot_event_type` | `string` |
| 24 | `pilot_event_date` | `string` |

## Printed Sample

This is a printed content sample only. It does not certify the whole folder.
The printed sample is transposed for readability: fields are rows and sample records are columns.
Printed sample shows the first 20 fields only; the schema above lists all 25 fields.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `ticker` | BNGO | BNGO | BNGO | BNGO | BNGO |
| `ts_utc` | 2025-01-01T00:02:00Z | 2025-01-01T00:03:00Z | 2025-01-01T00:04:00Z | 2025-01-01T00:06:00Z | 2025-01-01T00:21:00Z |
| `date` | 2025-01-01 | 2025-01-01 | 2025-01-01 | 2025-01-01 | 2025-01-01 |
| `year` | 2025 | 2025 | 2025 | 2025 | 2025 |
| `month` | 1 | 1 | 1 | 1 | 1 |
| `o` | 16.8 | 17.1 | 16.8 | 17.184 | 17.646 |
| `h` | 16.8 | 17.1 | 17.184 | 17.184 | 17.646 |
| `l` | 16.8 | 17.1 | 16.8 | 17.184 | 17.646 |
| `c` | 16.8 | 17.1 | 17.184 | 17.184 | 17.646 |
| `v` | 3.033333 | 16.666667 | 67.8 | 16.666667 | 3.333333 |
| `vw` | 16.8 | 17.1 | 17.0945 | 17.184 | 17.646 |
| `n` | 1 | 1 | 5 | 1 | 1 |
| `t` | 1735689720000 | 1735689780000 | 1735689840000 | 1735689960000 | 1735690860000 |
| `future_split_factor` | 0.016666666666666666 | 0.016666666666666666 | 0.016666666666666666 | 0.016666666666666666 | 0.016666666666666666 |
| `o_split_normalized` | 0.28 | 0.28500000000000003 | 0.28 | 0.2864 | 0.29410000000000003 |
| `h_split_normalized` | 0.28 | 0.28500000000000003 | 0.2864 | 0.2864 | 0.29410000000000003 |
| `l_split_normalized` | 0.28 | 0.28500000000000003 | 0.28 | 0.2864 | 0.29410000000000003 |
| `c_split_normalized` | 0.28 | 0.28500000000000003 | 0.2864 | 0.2864 | 0.29410000000000003 |
| `vw_split_normalized` | 0.28 | 0.28500000000000003 | 0.2849083333333333 | 0.2864 | 0.29410000000000003 |
| `materialized_price_view` | 1m_split_normalized_v0_1 | 1m_split_normalized_v0_1 | 1m_split_normalized_v0_1 | 1m_split_normalized_v0_1 | 1m_split_normalized_v0_1 |

## Interpretation

Use this file to understand the physical shape and example values of the represented parquet family.
For completeness, pass/fail status, and official scope, use the corresponding audit dossier and project-level status documentation.
