# Reference Presence Coverage Cases v0.1

Fuente: cache historico read-only de `reference`.

## Lectura

Muestra que all_tickers soporta presencia temporal, pero no sustituye un universe builder final.

## Que muestra

Casos representativos derivados de los indices historicos.

## Responde

Que familias concretas sostienen el estado institucional del bucket.

## No responde

No reemplaza la lectura poblacional ni prueba causalidad economica universal.

## Consecuencia

Estos casos soportan estado `coverage` bajo las limitaciones del readout.

## Overview 404 buckets sample

| ticker | request_date | msg | out_file | ends_w | ends_ws | ends_u | ends_r | contains_dot | contains_slash | contains_eq | in_lt1b_universe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AHLP | 2005-12-14 00:00:00 | http_404 | D:\reference\overview\ticker=AHLP\overview_AHLP_2005-12-14.parquet | False | False | False | False | False | False | False | False |
| CLNSPF | 2017-01-17 00:00:00 | http_404 | D:\reference\overview\ticker=CLNSPF\overview_CLNSPF_2017-01-17.parquet | False | False | False | False | False | False | False | False |
| ENIR | 2013-03-17 00:00:00 | http_404 | D:\reference\overview\ticker=ENIR\overview_ENIR_2013-03-17.parquet | False | False | False | True | False | False | False | False |
| IMG | 2026-03-09 00:00:00 | http_404 | D:\reference\overview\ticker=IMG\overview_IMG_2026-03-09.parquet | False | False | False | False | False | False | False | True |
| IMHPC | 2005-02-23 00:00:00 | http_404 | D:\reference\overview\ticker=IMHPC\overview_IMHPC_2005-02-23.parquet | False | False | False | False | False | False | False | False |
| TCOPJ | 2012-08-19 00:00:00 | http_404 | D:\reference\overview\ticker=TCOPJ\overview_TCOPJ_2012-08-19.parquet | False | False | False | False | False | False | False | False |
| TEUPC | 2013-08-28 00:00:00 | http_404 | D:\reference\overview\ticker=TEUPC\overview_TEUPC_2013-08-28.parquet | False | False | False | False | False | False | False | False |
| CMG.BW | 2006-10-12 00:00:00 | http_404 | D:\reference\overview\ticker=CMG.BW\overview_CMG.BW_2006-10-12.parquet | True | False | False | False | True | False | False | False |
| MWA.BW | 2006-12-14 00:00:00 | http_404 | D:\reference\overview\ticker=MWA.BW\overview_MWA.BW_2006-12-14.parquet | True | False | False | False | True | False | False | False |
| OIBR.CW | 2014-12-29 00:00:00 | http_404 | D:\reference\overview\ticker=OIBR.CW\overview_OIBR.CW_2014-12-29.parquet | True | False | False | False | True | False | False | False |
| PRIS.BW | 2010-12-02 00:00:00 | http_404 | D:\reference\overview\ticker=PRIS.BW\overview_PRIS.BW_2010-12-02.parquet | True | False | False | False | True | False | False | False |
| RGA.BW | 2008-09-18 00:00:00 | http_404 | D:\reference\overview\ticker=RGA.BW\overview_RGA.BW_2008-09-18.parquet | True | False | False | False | True | False | False | False |


## Listing presence gap sample

| ticker | snapshot_rows | first_snapshot | last_snapshot | exchange_nunique | type_nunique | active_true_rows | in_lt1b_universe | presence_bucket | span_days | sparse_density |
|---|---|---|---|---|---|---|---|---|---|---|
| AANW | 3 | 2020-11-26 00:00:00 | 2020-11-30 00:00:00 | 1 | 1 | 3 | False | good_snapshot_presence | 4 | 0.75 |
| ABHW | 3 | 2010-12-13 00:00:00 | 2010-12-19 00:00:00 | 1 | 1 | 3 | False | good_snapshot_presence | 6 | 0.5 |
| ACVW | 3 | 2006-11-14 00:00:00 | 2006-11-16 00:00:00 | 1 | 1 | 3 | False | good_snapshot_presence | 2 | 1.5 |
| AHOW | 3 | 2007-08-23 00:00:00 | 2007-08-28 00:00:00 | 1 | 1 | 3 | False | good_snapshot_presence | 5 | 0.6 |
| AIRCW | 3 | 2020-12-09 00:00:00 | 2020-12-14 00:00:00 | 1 | 1 | 3 | False | good_snapshot_presence | 5 | 0.6 |
| AIVW | 3 | 2020-12-09 00:00:00 | 2020-12-14 00:00:00 | 1 | 1 | 3 | False | good_snapshot_presence | 5 | 0.6 |
| ALZH | 3 | 2018-04-12 00:00:00 | 2018-11-14 00:00:00 | 1 | 1 | 3 | False | good_snapshot_presence | 216 | 0.013889 |
| ARPW | 3 | 2012-02-29 00:00:00 | 2012-03-13 00:00:00 | 1 | 1 | 3 | False | good_snapshot_presence | 13 | 0.230769 |
| AXLLW | 3 | 2013-01-31 00:00:00 | 2013-02-04 00:00:00 | 1 | 1 | 3 | False | good_snapshot_presence | 4 | 0.75 |
| BDFC | 3 | 2017-05-04 00:00:00 | 2017-05-08 00:00:00 | 1 | 1 | 3 | False | good_snapshot_presence | 4 | 0.75 |
| BEPCW | 3 | 2020-07-26 00:00:00 | 2020-07-29 00:00:00 | 1 | 1 | 3 | False | good_snapshot_presence | 3 | 1.0 |
| BEPW | 3 | 2020-07-26 00:00:00 | 2020-07-29 00:00:00 | 1 | 1 | 3 | False | good_snapshot_presence | 3 | 1.0 |

