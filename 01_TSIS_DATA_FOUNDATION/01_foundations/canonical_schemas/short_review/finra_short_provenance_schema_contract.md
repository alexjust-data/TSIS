# FINRA Short Provenance Schema Contract v0.1

## Dataset

- `dataset_id`: `short_review_finra_provenance_v0_1`
- `physical_root`: `E:\TSIS\data\short_review\finra_short`
- `status`: `provenance_metadata`

This contract covers manifests and download logs that explain how the FINRA review layer was built.

## Manifest Schemas

### `artifacts\short_interest_manifest.json`

| Field | Type | Semantics |
|---|---|---|
| `rows` | integer | Row count in `short_interest_all_biweekly_finra.parquet`. |
| `tickers` | integer | Unique ticker count. |
| `date_min` | string date | Earliest `settlement_date`. |
| `date_max` | string date | Latest `settlement_date`. |
| `columns` | list[string] | Physical column list. |

### `artifacts\short_volume_manifest.json`

| Field | Type | Semantics |
|---|---|---|
| `rows` | integer | Row count in `short_volume_all_daily_finra.parquet`. |
| `tickers` | integer | Unique ticker count. |
| `date_min` | string date | Earliest `date`. |
| `date_max` | string date | Latest `date`. |
| `columns` | list[string] | Physical column list. |

## Download Log Schemas

### `logs\download_short_interest_raw.csv`

| Column | Type | Semantics |
|---|---|---|
| `dataset` | string | Source family. |
| `settlement_date` | integer | FINRA settlement date encoded as `YYYYMMDD`. |
| `url` | string | Source URL where available. |
| `status` | string | Download status. |
| `detail` | integer/string | Source-specific detail or status payload. |
| `bytes` | double | Downloaded byte count where available. |

### `logs\download_short_volume_raw.csv`

| Column | Type | Semantics |
|---|---|---|
| `dataset` | string | Source family. |
| `date` | integer | FINRA file date encoded as `YYYYMMDD`. |
| `prefix` | string | FINRA file prefix. |
| `venue` | string | Venue/source component. |
| `status` | string | Download status. |
| `url` | string | Source URL where available. |
| `detail` | double/string | Source-specific detail or status payload. |

## Consumption Notes

These files are provenance assets. They are required for auditability but are not model features and must not be joined into a training matrix except as explicitly declared source-quality metadata.

## Related Documents

- `01_foundations/contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/short_review_consumption_policy.md`
- `E:\TSIS\data\short_review\finra_short_build_status.md`
