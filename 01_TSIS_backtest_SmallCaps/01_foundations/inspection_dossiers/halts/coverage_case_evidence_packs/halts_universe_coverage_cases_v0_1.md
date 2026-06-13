# Halts Universe Coverage Cases v0.1

Fuente: cache historico read-only de `halts`.

## Lectura

Muestra coverage y concentracion: ausencia de evento no equivale a missing data.

## Que muestra

Casos o tablas representativas derivados de los indices historicos.

## Responde

Que familias concretas sostienen el estado institucional del bucket.

## No responde

No reemplaza la inspeccion manual de todos los eventos ni prueba calidad de quotes/trades por si solo.

## Consecuencia

Estos casos soportan estado `coverage` bajo las limitaciones del readout.

## Top halt-count tickers

| ticker | halt_events_count | source_count | first_halt_date | last_halt_date | event_taxonomy_top | has_halt_data | in_universe |
|---|---|---|---|---|---|---|---|
| RDIB | 1206 | 1 | 2013-10-01 00:00:00 | 2026-02-09 00:00:00 | good_full_intraday_event | True | True |
| KELYB | 944 | 1 | 2013-09-26 00:00:00 | 2026-02-06 00:00:00 | good_full_intraday_event | True | True |
| LTRPB | 504 | 1 | 2014-09-16 00:00:00 | 2023-10-27 00:00:00 | good_full_intraday_event | True | True |
| WINS | 279 | 1 | 2004-08-30 00:00:00 | 2020-08-18 00:00:00 | good_full_intraday_event | True | True |
| KBSF | 231 | 1 | 2014-11-05 00:00:00 | 2021-09-16 00:00:00 | good_full_intraday_event | True | True |
| DGICB | 193 | 1 | 2013-12-26 00:00:00 | 2021-09-20 00:00:00 | good_full_intraday_event | True | True |
| QMMM | 179 | 1 | 2024-07-19 00:00:00 | 2025-09-26 00:00:00 | good_full_intraday_event | True | True |
| PNRG | 178 | 1 | 2013-10-08 00:00:00 | 2021-02-25 00:00:00 | good_full_intraday_event | True | True |
| AFJK | 177 | 1 | 2025-11-06 00:00:00 | 2026-03-13 00:00:00 | good_full_intraday_event | True | True |
| IMTE | 172 | 1 | 2017-09-20 00:00:00 | 2025-10-31 00:00:00 | good_full_intraday_event | True | True |
| SENEB | 167 | 1 | 2010-10-28 00:00:00 | 2026-02-06 00:00:00 | good_full_intraday_event | True | True |
| HVT.A | 164 | 1 | 2013-10-22 00:00:00 | 2026-02-10 00:00:00 | good_full_intraday_event | True | True |


## Tickers without halt matches sample

| ticker | halt_events_count | source_count | first_halt_date | last_halt_date | event_taxonomy_top | has_halt_data | in_universe |
|---|---|---|---|---|---|---|---|
| AACT | 0 |  |  |  |  | False | True |
| AAIC | 0 |  |  |  |  | False | True |
| AAQC | 0 |  |  |  |  | False | True |
| ABGI | 0 |  |  |  |  | False | True |
| ABSI | 0 |  |  |  |  | False | True |
| ACCO | 0 |  |  |  |  | False | True |
| ACDC | 0 |  |  |  |  | False | True |
| ACDI | 0 |  |  |  |  | False | True |
| ACFN | 0 |  |  |  |  | False | True |
| ACIC | 0 |  |  |  |  | False | True |
| ACII | 0 |  |  |  |  | False | True |
| ACNT | 0 |  |  |  |  | False | True |


## Multisource reconciliation

| scope | rows_pre_concat | rows_post_builder_dedup | dedup_delta |
|---|---|---|---|
| nasdaq | 119630 | 118594 | 1036 |
| nyse | 13178 | 13178 | 0 |
| sec | 1346 | 1346 | 0 |
| all_sources_concat | 134154 | 133118 | 1036 |
| persisted_multisource_parquet | 133116 | 133116 | 0 |

