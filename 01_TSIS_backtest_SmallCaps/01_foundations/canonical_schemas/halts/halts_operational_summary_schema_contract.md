# Halts Operational Summary Schema Contract

Status: operational schema contract for root and summary artifacts under `D:\Halts`.

## Purpose

This contract defines operational summary artifacts for halt download/build runs. These files describe execution scope and output locations; they are not event-level datasets.

## Observed Files

- `D:\Halts\download_summary.json`
- `D:\Halts\processed\halts_master_multisource_summary.csv`

## download_summary.json

Canonical fields:

| Field | Logical role |
|---|---|
| `root` | halt dataset root |
| `dates_requested` | count of requested Nasdaq halt dates |
| `raw_rows` | rows extracted into raw processed layer |
| `raw_xml_files` | count of preserved raw XML files |
| `raw_csv` | path to raw processed CSV |
| `master_csv` | path to generated master CSV |
| `master_parquet` | path to generated master parquet |

The observed file currently describes the Nasdaq run-dates build and points to `halts_master_nasdaq_for_run_dates`, not the final multisource master.

## halts_master_multisource_summary.csv

Canonical columns:

| Column | Logical role |
|---|---|
| `source` | source family or aggregate `all` |
| `rows` | number of rows in master |
| `tickers_nonnull` | number of rows with non-null ticker |

## Required Consumer Rules

- Use operational summaries for traceability only.
- Do not certify dataset quality from summary existence alone.
- Distinguish the Nasdaq run summary from the multisource consolidated master.

## Current Observed Evidence

Observed `download_summary.json` reports:

- `dates_requested`: 5662
- `raw_rows`: 119630
- `raw_xml_files`: 5662
- `master_parquet`: `D:\Halts\processed\halts_master_nasdaq_for_run_dates.parquet`

Observed multisource summary reports rows for `nasdaq`, `nyse`, `sec` and `all`.

## Verdict

Halts operational summary artifacts are structurally coherent traceability evidence. They are not the canonical halt event dataset.
