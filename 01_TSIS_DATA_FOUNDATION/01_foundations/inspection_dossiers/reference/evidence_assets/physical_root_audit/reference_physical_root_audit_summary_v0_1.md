# Reference Physical Root Audit v0.1

- Physical root: `E:/TSIS/data/reference`
- Policy: read-only. Este builder no modifica ni reorganiza el root fisico.

| subfamily | dirs | files | parquet_files | csv_files | other_files | sample_file | write_policy |
|---|---|---|---|---|---|---|---|
| _run | 0 | 3 | 0 | 2 | 1 | E:/TSIS/data/reference/_run/download_reference_universe_polygon.audit.csv | read_only |
| all_tickers | 0 | 3109 | 3109 | 0 | 0 | E:/TSIS/data/reference/all_tickers/snapshot_date=2005-01-02.parquet | read_only |
| dividends | 12468 | 12468 | 12468 | 0 | 0 | E:/TSIS/data/reference/dividends/ticker=A/dividends_A.parquet | read_only |
| events | 12468 | 12468 | 12468 | 0 | 0 | E:/TSIS/data/reference/events/ticker=A/events_A.parquet | read_only |
| exchanges | 0 | 1 | 1 | 0 | 0 | E:/TSIS/data/reference/exchanges/exchanges.parquet | read_only |
| overview | 12468 | 12468 | 12468 | 0 | 0 | E:/TSIS/data/reference/overview/ticker=A/overview_A_2022-02-08.parquet | read_only |
| splits | 12468 | 12468 | 12468 | 0 | 0 | E:/TSIS/data/reference/splits/ticker=A/splits_A.parquet | read_only |
| ticker_types | 0 | 1 | 1 | 0 | 0 | E:/TSIS/data/reference/ticker_types/ticker_types.parquet | read_only |
