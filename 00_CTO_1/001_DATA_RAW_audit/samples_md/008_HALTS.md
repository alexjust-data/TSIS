# HALTS - Parquet Content Sample

## Purpose

This document prints a small human-readable sample from one parquet file that represents this audit folder.
It is a navigation and inspection aid, not a data certification artifact.

## Source

| item | value |
| --- | --- |
| source_parquet | `E:\TSIS\data\Halts\processed\halts_master_multisource.parquet` |
| parquet_rows | 133116 |
| parquet_columns | 16 |
| row_groups | 1 |

## Sample Selection

One non-empty halt master parquet from the processed halts tree.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `source` | `string` |
| 1 | `source_priority` | `int64` |
| 2 | `ticker` | `string` |
| 3 | `issuer_name` | `string` |
| 4 | `listing_exchange` | `string` |
| 5 | `halt_date` | `timestamp[ns]` |
| 6 | `halt_start_et` | `timestamp[ns]` |
| 7 | `resume_quote_et` | `timestamp[ns]` |
| 8 | `resume_trade_et` | `timestamp[ns]` |
| 9 | `halt_code` | `string` |
| 10 | `halt_type` | `string` |
| 11 | `raw_reason` | `string` |
| 12 | `release_no` | `string` |
| 13 | `item_link` | `string` |
| 14 | `url_source` | `string` |
| 15 | `is_sec_suspension` | `bool` |

## Printed Sample

This is a printed content sample only. It does not certify the whole folder.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `source` | sec | sec | sec | sec | sec |
| `source_priority` | 1 | 1 | 1 | 1 | 1 |
| `ticker` |  |  |  |  |  |
| `issuer_name` | Garcis U.S.A., Inc. | Environmental Chemicals Group, Inc. | The Enstar Group, Inc. | Lanstar Semiconductor, Inc. | Comparator Systems Corp. |
| `listing_exchange` |  |  |  |  |  |
| `halt_date` | 1995-10-13T00:00:00 | 1995-12-12T00:00:00 | 1996-03-29T00:00:00 | 1996-05-03T00:00:00 | 1996-05-14T00:00:00 |
| `halt_start_et` |  |  |  |  |  |
| `resume_quote_et` |  |  |  |  |  |
| `resume_trade_et` |  |  |  |  |  |
| `halt_code` | SEC | SEC | SEC | SEC | SEC |
| `halt_type` | SEC suspension | SEC suspension | SEC suspension | SEC suspension | SEC suspension |
| `raw_reason` | SEC suspension | SEC suspension | SEC suspension | SEC suspension | SEC suspension |
| `release_no` | 34-36366 | 34-36571 | 34-37043 | 34-37166 | 34-37209 |
| `item_link` | https://www.sec.gov/files/litigation/admin/3436366.txt | https://www.sec.gov/enforcement-litigation/trading-suspensions/34-36571 | https://www.sec.gov/files/litigation/admin/3437043.txt | https://www.sec.gov/files/litigation/admin/3437166.txt | https://www.sec.gov/files/litigation/admin/3437209.txt |
| `url_source` | https://www.sec.gov/enforcement-litigation/trading-suspensions?page=13 | https://www.sec.gov/enforcement-litigation/trading-suspensions?page=13 | https://www.sec.gov/enforcement-litigation/trading-suspensions?page=13 | https://www.sec.gov/enforcement-litigation/trading-suspensions?page=13 | https://www.sec.gov/enforcement-litigation/trading-suspensions?page=13 |
| `is_sec_suspension` | True | True | True | True | True |

## Interpretation

Use this file to understand the physical shape and example values of the represented parquet family.
For completeness, pass/fail status, and official scope, use the corresponding audit dossier and project-level status documentation.
