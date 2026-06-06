# FINRA Short Interest Schema Contract v0.1

## Dataset

- `dataset_id`: `short_review_finra_short_interest_v0_1`
- `physical_root`: `E:\TSIS\data\short_review\finra_short`
- `aggregate_file`: `artifacts\short_interest_all_biweekly_finra.parquet`
- `normalized_layout`: `normalized\short_interest\TICKER.parquet`
- `grain`: `ticker` x `settlement_date`
- `source_scope`: FINRA official/free equity short interest files
- `status`: `official_free_baseline_provenance`

## Purpose

This schema defines the FINRA short-interest baseline used to validate and contextualize the operational `short` layer.

It is a slow, biweekly crowding dataset. It must not be interpreted as same-day intraday pressure or as proof of full 2005-2026 short-interest completeness.

## Physical Schema

| Column | Type | Required | Semantics |
|---|---|---:|---|
| `settlement_date` | `timestamp[ns]` | yes | FINRA settlement date for the short-interest observation. |
| `ticker` | `string` | yes | Ticker symbol after normalization to the project ticker universe. |
| `short_interest` | `int64` | yes | Reported short interest shares. |
| `avg_daily_volume` | `int64` | yes | FINRA-reported average daily volume used for days-to-cover context. |
| `days_to_cover` | `double` | yes | Short interest divided by average daily volume under FINRA semantics. |

## Coverage Snapshot

From `E:\TSIS\data\short_review\finra_short\artifacts\short_interest_manifest.json`:

- rows: `505745`
- tickers: `4687`
- date_min: `2017-12-29`
- date_max: `2026-04-15`

## Consumption Notes

- Use `settlement_date` as the observation date.
- Preserve source scope as FINRA official/free.
- Use as provenance, coverage comparison, and source validation baseline.
- Do not assume full ticker lifetime coverage.
- Do not use as same-day causal evidence without explicit lag assumptions.

## Related Documents

- `01_foundations/contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/short_review_consumption_policy.md`
- `01_foundations/inspection_dossiers/short/short_institutional_closeout_v0_1.md`
