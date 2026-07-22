# Halts Source-Specific Outputs Schema Contract

Status: source/intermediate schema contract for source-specific files under `D:\Halts\processed`.

## Purpose

This contract documents the source-specific and intermediate halt outputs. These files are evidence and transformation inputs for the consolidated master, not the preferred downstream contract.

## Observed Files

- `D:\Halts\processed\halts_master.parquet`
- `D:\Halts\processed\halts_master.csv`
- `D:\Halts\processed\halts_master_nasdaq_for_run_dates.parquet`
- `D:\Halts\processed\halts_master_nasdaq_for_run_dates.csv`
- `D:\Halts\processed\halts_master_nyse_1y.parquet`
- `D:\Halts\processed\halts_master_nyse_1y.csv`
- `D:\Halts\processed\halts_master_sec.parquet`
- `D:\Halts\processed\halts_master_sec.csv`
- `D:\Halts\processed\nasdaq_tradehalts_for_run_dates_raw.csv`
- `D:\Halts\processed\nasdaq_halts_raw.csv`
- `D:\Halts\processed\sec_suspensions_raw.csv`

## Empty Legacy Master

`halts_master.parquet` and `halts_master.csv` were observed with zero rows and columns:

`ticker`, `halt_date`, `halt_start_et`, `halt_end_et`, `halt_code`, `halt_type`, `respondents`, `url_source`, `source`, `source_priority`.

This is a valid empty legacy/placeholder artifact. It must not be treated as evidence that no halt events exist because the multisource master contains events.

## Nasdaq Run-Dates Output

Observed file:

`D:\Halts\processed\halts_master_nasdaq_for_run_dates.parquet`

Observed rows: 119630.

Observed columns:

`ticker`, `halt_date`, `halt_start_et`, `resume_quote_et`, `resume_trade_et`, `halt_code`, `halt_type`, `title`, `url_source`, `item_link`, `source_priority`, `raw_description_text`.

Observed representative rows contain RSS/title and `raw_description_text` with parsed fields not fully normalized in the visible sample. This file is therefore an intermediate Nasdaq evidence layer, not the canonical cross-source master.

## Nasdaq Raw Processed CSV

Observed file:

`D:\Halts\processed\nasdaq_tradehalts_for_run_dates_raw.csv`

Observed columns:

`source`, `request_haltdate_mmddyyyy`, `title`, `pub_date`, `url_source`, `item_link`, `ticker`, `halt_code`, `halt_date_text`, `halt_time_text`, `resume_date_text`, `resume_quote_time_text`, `resume_trade_time_text`, `raw_description_text`, `fetch_error`.

This file captures raw RSS-derived request rows and parsing diagnostics. Consumers must not use it as the final normalized halt event table.

## NYSE 1Y Output

Observed file:

`D:\Halts\processed\halts_master_nyse_1y.parquet`

Observed rows: 13178.

Canonical columns align with the multisource master:

`source`, `source_priority`, `ticker`, `issuer_name`, `listing_exchange`, `halt_date`, `halt_start_et`, `resume_quote_et`, `resume_trade_et`, `halt_code`, `halt_type`, `raw_reason`, `release_no`, `item_link`, `url_source`, `is_sec_suspension`.

NYSE output is normalized but has a one-year source window in the observed filename.

## SEC Output

Observed file:

`D:\Halts\processed\halts_master_sec.parquet`

Observed rows: 1346.

Canonical columns align with the multisource master:

`source`, `source_priority`, `ticker`, `issuer_name`, `listing_exchange`, `halt_date`, `halt_start_et`, `resume_quote_et`, `resume_trade_et`, `halt_code`, `halt_type`, `raw_reason`, `release_no`, `item_link`, `url_source`, `is_sec_suspension`.

SEC rows may have missing ticker and must preserve `issuer_name`, `release_no`, `item_link` and `url_source`.

## Required Consumer Rules

- Prefer `halts_master_multisource` for downstream consumption.
- Treat source-specific files as provenance, debugging or source-family audits.
- Preserve raw/intermediate files when reconciling parser failures.
- Do not infer no halts from empty placeholder files.

## Verdict

Source-specific halt outputs are structurally useful evidence layers. The canonical consumable event table remains `halts_master_multisource`.
