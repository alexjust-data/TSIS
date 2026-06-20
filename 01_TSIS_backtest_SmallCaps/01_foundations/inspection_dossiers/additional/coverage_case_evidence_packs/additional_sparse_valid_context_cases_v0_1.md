# Additional Sparse Valid Context Cases v0.1

Some Additional subfamilies are expected to be sparse. Sparse does not automatically mean broken.

| dataset | quality_state | files_present | files_non_empty | coverage_non_empty_pct | master_table_destination | forbidden_interpretation |
| --- | --- | --- | --- | --- | --- | --- |
| ratios | review_sparse_snapshot | 4824.0 | 2232.0 | 46.269 | data_quality_report; deferred context only | Do not promote to primary ML feature layer from coverage alone. |
| ipos | good_review_sparse_event | 4824.0 | 1255.0 | 26.016 | symbol_master listing context; master_daily_table ipo_age/ipo_flag; data_quality_report | Do not treat sparse IPO files as missing-data failure for mature tickers. |

Institutional reading:

- IPO and ratios coverage must be interpreted by expectedness, not by file presence alone.
- Sparse context can still support `data_quality_report` and selected master-table fields.
- It cannot be promoted as broad feature coverage without a later point-in-time validator.
