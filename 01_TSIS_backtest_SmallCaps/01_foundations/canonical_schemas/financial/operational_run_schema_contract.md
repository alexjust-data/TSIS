# Financial Operational Run Schema Contract

Status: operational schema contract for `D:\financial\_run`.

## Purpose

This contract defines the canonical schemas for financial download run artifacts. These files describe execution progress, resume state and per-request errors or non-clean request outcomes.

These are operational artifacts, not model input datasets.

## Physical Layout

Observed root:

`D:\financial\_run`

Observed files:

- `download_fundamentals_v1.errors.csv`
- `download_fundamentals_v1.progress.json`

## download_fundamentals_v1.errors.csv

Canonical columns:

| Column | Logical role |
|---|---|
| `ticker` | requested ticker |
| `dataset` | financial endpoint/family |
| `http_status` | request status or normalized outcome |
| `msg` | diagnostic message |
| `rows_saved` | rows written for the request |
| `pages` | source pages consumed |
| `dropped_mismatch` | records dropped because ticker/source identity mismatched |
| `dropped_missing_ticker` | records dropped because ticker was missing |
| `out_file` | output file path |
| `ts_utc` | run event timestamp |

Rows in this file may include non-fatal outcomes. The file is a diagnostic log and must be interpreted with audit results before declaring a dataset valid or invalid.

## download_fundamentals_v1.progress.json

Canonical fields:

| Field | Logical role |
|---|---|
| `status` | run completion state |
| `updated_at_utc` | latest progress timestamp |
| `input` | input universe/reference path |
| `outdir` | financial output root |
| `datasets` | requested dataset families |
| `done_tickers` | processed ticker count |
| `total_tickers` | total ticker count |
| `progress_pct` | progress percentage |
| `resume` | whether resume mode was enabled |
| `resume_validate` | whether resume validation was enabled |
| `skipped_valid` | outputs skipped as already valid |
| `errors` | run-level error count |
| `workers` | worker count |
| `limit` | optional ticker limit |
| `max_pages` | per-endpoint/source page cap |
| `keep_records_without_ticker` | whether records without ticker were retained |

## Required Consumer Rules

- Use `_run` files for execution traceability only.
- Do not infer dataset quality from progress completion alone.
- Pair `_run` evidence with `_audit` evidence before any institutional promotion.
- Preserve these files outside analytical feature tables.

## Current Observed Evidence

The run artifacts are present and parseable. The progress artifact records the execution configuration and completion/progress state, while the errors CSV records request-level diagnostics.

## Verdict

`D:\financial\_run` has a coherent operational schema. It documents how the financial download ran, but it does not certify the financial datasets as good without the audit layer.
