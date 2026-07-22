# Halts Universe Coverage Schema Contract

Status: coverage/evidence schema contract for halt coverage files under `D:\Halts\processed`.

## Purpose

This contract defines the schema for universe-to-halts coverage artifacts. These files answer which project-universe tickers have observed halt/suspension evidence and which do not.

These files are coverage evidence, not event masters.

## Observed Files

Multisource coverage:

- `D:\Halts\processed\universe_vs_halts_coverage_multisource.csv`
- `D:\Halts\processed\universe_tickers_with_halts_multisource.csv`
- `D:\Halts\processed\universe_tickers_without_halts_multisource.csv`

Legacy/single-source coverage:

- `D:\Halts\processed\universe_vs_halts_coverage.csv`
- `D:\Halts\processed\universe_tickers_with_halts.csv`
- `D:\Halts\processed\universe_tickers_without_halts.csv`

Summary:

- `D:\Halts\processed\halts_master_multisource_summary.csv`

## Coverage Columns

Coverage files use:

| Column | Logical role |
|---|---|
| `ticker` | project-universe ticker |
| `halt_events_count` | number of matched halt/suspension events |
| `source_count` | number of source families with events |
| `sources` | encoded source list |
| `first_halt_date` | first observed halt/suspension date |
| `last_halt_date` | last observed halt/suspension date |
| `has_halt_data` | boolean coverage flag |

`universe_tickers_with_halts*` is the `has_halt_data = true` subset.

`universe_tickers_without_halts*` is the `has_halt_data = false` subset.

## Summary Columns

`halts_master_multisource_summary.csv` uses:

| Column | Logical role |
|---|---|
| `source` | source family or aggregate `all` |
| `rows` | event rows |
| `tickers_nonnull` | rows with non-null ticker |

## Required Consumer Rules

- Use coverage files to audit universe intersection only.
- Do not use coverage files as substitutes for event-level halt data.
- `has_halt_data = false` means no matched halt event in the current halt master, not proof that no halt ever occurred outside the source scope.
- Prefer multisource coverage files over legacy/single-source coverage when available.

## Current Observed Evidence

Observed multisource coverage sample includes both tickers with halt history and tickers without halt matches. The summary file reports `nasdaq`, `nyse`, `sec` and `all` rows.

## Verdict

The halt coverage files are structurally coherent universe intersection evidence. They are not canonical event data.
