# Reference Causal Overlay Cases v0.1

Fuente: cache historico read-only de `reference`.

## Lectura

Muestra los tres frentes causales principales: splits->trades quirurgico, events->halts fuerte, events->quotes detector/review.

## Que muestra

Casos representativos derivados de los indices historicos.

## Responde

Que familias concretas sostienen el estado institucional del bucket.

## No responde

No reemplaza la lectura poblacional ni prueba causalidad economica universal.

## Consecuencia

Estos casos soportan estado `causal` bajo las limitaciones del readout.

## Splits -> trades candidates

| execution_date | id | split_from | split_to | ticker | _dataset | _ingested_utc | in_lt1b_universe | split_ratio | split_bucket | file | date |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022-01-05 00:00:00 | Ea35cdf5de94be8b29146166fb557fa0b2b5963d291bc8c88a3bbfdbc694ef1fd | 9.5 | 1.0 | APCX | splits | 2026-03-11T16:56:51.282906+00:00 | True | 0.10526315789473684 | good_split_event | D:\trades_ticks_prod_2005_2026\APCX\year=2022\month=01\day=2022-01-04\market.parquet | 2022-01-04 00:00:00 |
| 2026-01-23 00:00:00 | E64d37123f0e0465b3ebd8febdb0abf206d3f466f9aeb498abeab88eaea80f4e7 | 10.0 | 1.0 | CCTG | splits | 2026-03-11T17:00:46.042743+00:00 | True | 0.1 | good_split_event | D:\trades_ticks_prod_2005_2026\CCTG\year=2026\month=01\day=2026-01-20\market.parquet | 2026-01-20 00:00:00 |
| 2024-08-29 00:00:00 | Ea122bda39592c508ab219160433faaca201a8022b58673f12f0105ff915cfb6b | 10.0 | 1.0 | GDEV | splits | 2026-03-11T17:06:52.065806+00:00 | True | 0.1 | good_split_event | C:\TSIS_Data\data\trades_ticks_prod_2005_2026\GDEV\year=2024\month=08\day=2024-08-28\market.parquet | 2024-08-28 00:00:00 |
| 2026-01-26 00:00:00 | E11cfdd1b0c368c198cfac9c6e22b2e78c1de83567e22b906a2a4483afa65677b | 10.0 | 1.0 | LRHC | splits | 2026-03-11T17:12:16.322594+00:00 | True | 0.1 | good_split_event | C:\TSIS_Data\data\trades_ticks_prod_2005_2026\LRHC\year=2026\month=01\day=2026-01-23\market.parquet | 2026-01-23 00:00:00 |
| 2025-10-31 00:00:00 | E7b6837ef402df3d01f61cad4824b5dad0912356d8c898cc5f2c6a9037c54818a | 10.0 | 1.0 | NLSP | splits | 2026-03-11T17:15:11.667270+00:00 | True | 0.1 | good_split_event | C:\TSIS_Data\data\trades_ticks_prod_2005_2026\NLSP\year=2025\month=10\day=2025-10-29\market.parquet | 2025-10-29 00:00:00 |
| 2024-04-10 00:00:00 | E38c7ca4ae1a3bdd3c9d1787cdbf120688482dc9cf6392a98af3d42f9f527fbcb | 15.0 | 1.0 | NUTX | splits | 2026-03-11T17:15:55.373319+00:00 | True | 0.06666666666666667 | good_split_event | C:\TSIS_Data\data\trades_ticks_prod_2005_2026\NUTX\year=2024\month=04\day=2024-04-10\market.parquet | 2024-04-10 00:00:00 |
| 2022-05-13 00:00:00 | Ed3720e4d1d96a4909324ec23592876c6abedd6a500bed255b163cc3f6f7fd439 | 11.0 | 1.0 | RMTI | splits | 2026-03-11T17:19:41.930536+00:00 | True | 0.09090909090909091 | good_split_event | C:\TSIS_Data\data\trades_ticks_prod_2005_2026\RMTI\year=2022\month=05\day=2022-05-12\market.parquet | 2022-05-12 00:00:00 |
| 2025-06-12 00:00:00 | E778c73919b6731487cf1cd4d5327cabd2d04c8d04a84f96d8f00a6bc582d95da | 10.0 | 1.0 | SST | splits | 2026-03-11T17:22:12.062585+00:00 | True | 0.1 | good_split_event | C:\TSIS_Data\data\trades_ticks_prod_2005_2026\SST\year=2025\month=06\day=2025-06-10\market.parquet | 2025-06-10 00:00:00 |
| 2023-09-25 00:00:00 | Ea160d7ea5c11335893a1193d63b0dbd58f1296282ba199ddaa32c1388993f947 | 10.0 | 1.0 | VINO | splits | 2026-03-11T17:25:23.151405+00:00 | True | 0.1 | good_split_event | C:\TSIS_Data\data\trades_ticks_prod_2005_2026\VINO\year=2023\month=09\day=2023-09-27\market.parquet | 2023-09-27 00:00:00 |
| 2020-09-02 00:00:00 | E8bac0dd6158e0c034cef091e299523fc517c654cdc2d33123bfea24186ec9638 | 10.0 | 1.0 | APEX | splits | 2026-03-11T16:56:52.322865+00:00 | True | 0.1 | good_split_event | C:\TSIS_Data\data\trades_ticks_prod_2005_2026\APEX\year=2020\month=08\day=2020-08-28\market.parquet | 2020-08-28 00:00:00 |
| 2026-01-23 00:00:00 | E64d37123f0e0465b3ebd8febdb0abf206d3f466f9aeb498abeab88eaea80f4e7 | 10.0 | 1.0 | CCTG | splits | 2026-03-11T17:00:46.042743+00:00 | True | 0.1 | good_split_event | D:\trades_ticks_prod_2005_2026\CCTG\year=2026\month=01\day=2026-01-16\market.parquet | 2026-01-16 00:00:00 |
| 2024-02-29 00:00:00 | E59816c6d76e1eaa6de7b525e2317da585d12de4822a12e3fcac396300a7ebf80 | 10.0 | 1.0 | CELU | splits | 2026-03-11T17:00:55.735226+00:00 | True | 0.1 | good_split_event | C:\TSIS_Data\data\trades_ticks_prod_2005_2026\CELU\year=2024\month=02\day=2024-02-23\market.parquet | 2024-02-23 00:00:00 |


## Events -> halts candidates

| ticker | event_idx | event_type | event_date | event_status | ticker_change_to | event_payload | in_lt1b_universe | event_id_canonical | halt_date | halt_start_et | resume_trade_et |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ABAT | 2.0 | ticker_change | 2023-09-11 00:00:00 | ok_event | ABML | {"date": "2023-09-11", "ticker_change": {"ticker": "ABML"}, "type": "ticker_change"} | True | ABAT/2023-09-21/2023-09-21 09:31:12/LUDP/LUDP | 2023-09-21 00:00:00 | 2023-09-21 09:31:12 | 2023-09-21 09:36:12 |
| ABOS | 1.0 | ticker_change | 2021-07-01 00:00:00 | ok_event | ABOS | {"date": "2021-07-01", "ticker_change": {"ticker": "ABOS"}, "type": "ticker_change"} | True | ABOS/2021-07-26/2021-07-26 09:30:18/LUDP/LUDP | 2021-07-26 00:00:00 | 2021-07-26 09:30:18 | 2021-07-26 09:35:18 |
| ACB | 1.0 | ticker_change | 2024-02-20 00:00:00 | ok_event | ACB | {"date": "2024-02-20", "ticker_change": {"ticker": "ACB"}, "type": "ticker_change"} | True | ACB/2024-02-16/2024-02-16 19:50:00/T3/T3 | 2024-02-16 00:00:00 | 2024-02-16 19:50:00 | 2024-02-20 09:00:00 |
| ACRV | 1.0 | ticker_change | 2022-11-10 00:00:00 | ok_event | ACRV | {"date": "2022-11-10", "ticker_change": {"ticker": "ACRV"}, "type": "ticker_change"} | True | ACRV/2022-11-25/2022-11-25 09:34:45/LUDP/LUDP | 2022-11-25 00:00:00 | 2022-11-25 09:34:45 | 2022-11-25 09:39:45 |
| AGH | 1.0 | ticker_change | 2025-02-12 00:00:00 | ok_event | AGH | {"date": "2025-02-12", "ticker_change": {"ticker": "AGH"}, "type": "ticker_change"} | True | AGH/2025-02-18/2025-02-18 13:26:20/LUDP/LUDP | 2025-02-18 00:00:00 | 2025-02-18 13:26:20 | 2025-02-18 13:36:20 |
| AHT | 1.0 | ticker_change | 2024-10-28 00:00:00 | ok_event | AHT | {"date": "2024-10-28", "ticker_change": {"ticker": "AHT"}, "type": "ticker_change"} | True | AHT/2024-11-21/2024-11-21 09:36:50/M/M | 2024-11-21 00:00:00 | 2024-11-21 09:36:50 | 2024-11-21 09:41:53 |
| AIM | 2.0 | ticker_change | 2025-06-12 00:00:00 | ok_event | AIMI | {"date": "2025-06-12", "ticker_change": {"ticker": "AIMI"}, "type": "ticker_change"} | True | AIM/2025-06-17/2025-06-17 09:44:34/M/M | 2025-06-17 00:00:00 | 2025-06-17 09:44:34 | 2025-06-17 09:49:34 |
| AKA | 1.0 | ticker_change | 2023-10-02 00:00:00 | ok_event | AKA | {"date": "2023-10-02", "ticker_change": {"ticker": "AKA"}, "type": "ticker_change"} | True | AKA/2023-10-23/2023-10-23 09:46:47/M/M | 2023-10-23 00:00:00 | 2023-10-23 09:46:47 | 2023-10-23 09:51:52 |
| AKBA | 1.0 | ticker_change | 2014-03-20 00:00:00 | ok_event | AKBA | {"date": "2014-03-20", "ticker_change": {"ticker": "AKBA"}, "type": "ticker_change"} | True | AKBA/2014-04-14/2014-04-14 14:36:17/LUDP/LUDP | 2014-04-14 00:00:00 | 2014-04-14 14:36:17 | 2014-04-14 14:41:17 |
| ALT | 1.0 | ticker_change | 2018-09-14 00:00:00 | ok_event | ALT | {"date": "2018-09-14", "ticker_change": {"ticker": "ALT"}, "type": "ticker_change"} | True | ALT/2018-09-19/2018-09-19 10:03:54/LUDP/LUDP | 2018-09-19 00:00:00 | 2018-09-19 10:03:54 | 2018-09-19 10:13:54 |
| ALTI | 1.0 | ticker_change | 2023-04-25 00:00:00 | ok_event | ALTI | {"date": "2023-04-25", "ticker_change": {"ticker": "ALTI"}, "type": "ticker_change"} | True | ALTI/2023-05-03/2023-05-03 09:36:40/LUDP/LUDP | 2023-05-03 00:00:00 | 2023-05-03 09:36:40 | 2023-05-03 09:41:40 |
| ALXO | 1.0 | ticker_change | 2020-07-17 00:00:00 | ok_event | ALXO | {"date": "2020-07-17", "ticker_change": {"ticker": "ALXO"}, "type": "ticker_change"} | True | ALXO/2020-08-05/2020-08-05 13:17:09/LUDP/LUDP | 2020-08-05 00:00:00 | 2020-08-05 13:17:09 | 2020-08-05 13:22:09 |


## Events -> quotes candidates

| ticker | event_idx | event_type | event_date | event_status | ticker_change_to | event_payload | in_lt1b_universe | date | severity | m.crossed_ratio_pct | m.crossed_rows |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ALTS | 2.0 | ticker_change | 2019-09-11 00:00:00 | ok_event | JAN | {"date": "2019-09-11", "ticker_change": {"ticker": "JAN"}, "type": "ticker_change"} | True | 2019-09-11 00:00:00 | PASS | 0.0 | 0 |
| BGM | 1.0 | ticker_change | 2024-08-12 00:00:00 | ok_event | BGM | {"date": "2024-08-12", "ticker_change": {"ticker": "BGM"}, "type": "ticker_change"} | True | 2024-08-12 00:00:00 | PASS | 0.0 | 0 |
| CDZI | 1.0 | ticker_change | 2005-06-20 00:00:00 | ok_event | CDZI | {"date": "2005-06-20", "ticker_change": {"ticker": "CDZI"}, "type": "ticker_change"} | True | 2005-06-20 00:00:00 | PASS | 0.0 | 0 |
| CMCL | 1.0 | ticker_change | 2017-07-27 00:00:00 | ok_event | CMCL | {"date": "2017-07-27", "ticker_change": {"ticker": "CMCL"}, "type": "ticker_change"} | True | 2017-07-27 00:00:00 | PASS | 0.0 | 0 |
| ELA | 1.0 | ticker_change | 2019-12-18 00:00:00 | ok_event | ELA | {"date": "2019-12-18", "ticker_change": {"ticker": "ELA"}, "type": "ticker_change"} | True | 2019-12-18 00:00:00 | PASS | 0.0 | 0 |
| FBIZ | 1.0 | ticker_change | 2005-10-07 00:00:00 | ok_event | FBIZ | {"date": "2005-10-07", "ticker_change": {"ticker": "FBIZ"}, "type": "ticker_change"} | True | 2005-10-07 00:00:00 | PASS | 0.0 | 0 |
| GRNT | 1.0 | ticker_change | 2022-10-25 00:00:00 | ok_event | GRNT | {"date": "2022-10-25", "ticker_change": {"ticker": "GRNT"}, "type": "ticker_change"} | True | 2022-10-25 00:00:00 | PASS | 0.0 | 0 |
| IG | 1.0 | ticker_change | 2018-04-19 00:00:00 | ok_event | IG | {"date": "2018-04-19", "ticker_change": {"ticker": "IG"}, "type": "ticker_change"} | True | 2018-04-24 00:00:00 | PASS | 0.0 | 0 |
| IOR | 1.0 | ticker_change | 2017-07-03 00:00:00 | ok_event | IOR | {"date": "2017-07-03", "ticker_change": {"ticker": "IOR"}, "type": "ticker_change"} | True | 2017-07-05 00:00:00 | PASS | 0.0 | 0 |
| MPB | 1.0 | ticker_change | 2008-08-01 00:00:00 | ok_event | MPB | {"date": "2008-08-01", "ticker_change": {"ticker": "MPB"}, "type": "ticker_change"} | True | 2008-08-01 00:00:00 | PASS | 0.0 | 0 |
| PCB | 1.0 | ticker_change | 2019-07-03 00:00:00 | ok_event | PCB | {"date": "2019-07-03", "ticker_change": {"ticker": "PCB"}, "type": "ticker_change"} | True | 2019-07-03 00:00:00 | PASS | 0.0 | 0 |
| PKBK | 1.0 | ticker_change | 2005-06-01 00:00:00 | ok_event | PKBK | {"date": "2005-06-01", "ticker_change": {"ticker": "PKBK"}, "type": "ticker_change"} | True | 2005-06-01 00:00:00 | PASS | 0.0 | 0 |

