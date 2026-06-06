# FINRA Short Volume Schema Contract v0.1

## Dataset

- `dataset_id`: `short_review_finra_short_volume_v0_1`
- `physical_root`: `E:\TSIS\data\short_review\finra_short`
- `aggregate_file`: `artifacts\short_volume_all_daily_finra.parquet`
- `normalized_layout`: `normalized\short_volume\TICKER.parquet`
- `grain`: `ticker` x `date`
- `source_scope`: FINRA official/free daily short-sale volume files
- `status`: `official_free_baseline_provenance`

## Purpose

This schema defines the FINRA daily short-volume baseline used to validate and contextualize the operational `short` layer.

It represents FINRA source-scope short-sale volume, not consolidated market-wide shorting truth.

## Physical Schema

| Column | Type | Required | Semantics |
|---|---|---:|---|
| `ticker` | `string` | yes | Ticker symbol after normalization to the project ticker universe. |
| `date` | `timestamp[ns]` | yes | Trading date represented by the FINRA daily file. |
| `total_volume` | `double` | yes | FINRA total volume in source scope. |
| `short_volume` | `double` | yes | FINRA reported short volume. |
| `exempt_volume` | `double` | yes | FINRA reported short-exempt volume. |
| `non_exempt_volume` | `double` | yes | Short volume excluding exempt volume. |
| `short_volume_ratio` | `double` | yes | `short_volume / total_volume` in FINRA source scope. |
| `nyse_short_volume` | `double` | yes | NYSE venue component. |
| `nyse_short_volume_exempt` | `double` | yes | NYSE short-exempt component. |
| `nasdaq_carteret_short_volume` | `double` | yes | Nasdaq Carteret venue component. |
| `nasdaq_carteret_short_volume_exempt` | `double` | yes | Nasdaq Carteret short-exempt component. |
| `nasdaq_chicago_short_volume` | `double` | yes | Nasdaq Chicago venue component. |
| `nasdaq_chicago_short_volume_exempt` | `double` | yes | Nasdaq Chicago short-exempt component. |
| `adf_short_volume` | `double` | yes | FINRA ADF component. |
| `adf_short_volume_exempt` | `double` | yes | FINRA ADF short-exempt component. |
| `orf_short_volume` | `double` | yes | FINRA ORF component. |
| `orf_short_volume_exempt` | `double` | yes | FINRA ORF short-exempt component. |

## Coverage Snapshot

From `E:\TSIS\data\short_review\finra_short\artifacts\short_volume_manifest.json`:

- rows: `4689038`
- tickers: `4623`
- date_min: `2018-08-01`
- date_max: `2026-04-29`

## Source Components

The pipeline documents these FINRA daily file families:

- `CNMS`
- `FNSQ`
- `FNQC`
- `FNYX`
- `FNRA`
- `FORF`

## Consumption Notes

- Preserve venue/source scope.
- Do not treat `short_volume_ratio` as universal market shorting pressure.
- Do not claim pre-2018 official/free short-volume completeness.
- Use as official/free baseline, forensic comparator, or declared feature source with scope limits.

## Related Documents

- `01_foundations/contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/short_review_consumption_policy.md`
- `01_foundations/inspection_dossiers/short/short_institutional_closeout_v0_1.md`
