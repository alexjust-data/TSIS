# Reference Review Identity And Quotes Cases v0.1

Fuente: cache historico read-only de `reference`.

## Lectura

Muestra los residuos que deben conservar review: simbolos transitorios y ticker_change cerca de quotes anomalies.

## Que muestra

Casos representativos derivados de los indices historicos.

## Responde

Que familias concretas sostienen el estado institucional del bucket.

## No responde

No reemplaza la lectura poblacional ni prueba causalidad economica universal.

## Consecuencia

Estos casos soportan estado `review` bajo las limitaciones del readout.

## Review identity sample

| ticker | request_date | name | type | primary_exchange | active | market_cap | ticker_root | list_date | identity_bucket | transient_symbol_flag | suffix_variant_flag |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ABV.C | 2013-11-10 00:00:00 | COMPANHIA BEBIDA ADS EACH RPTNG 1 COM SH) | CS | XNYS | True |  | ABV |  | review_transient_symbol | True | False |
| AGM.A | 2026-03-09 00:00:00 | Federal Agricultural Mortgage Corporation Class A Voting | CS | XNYS | True | 1394144930.21 | AGM | 1993-12-16 00:00:00 | review_transient_symbol | True | False |
| AGR.A | 2005-05-30 00:00:00 | AGERE SYSTEMS INC CL-A | CS | XNYS | True |  | AGR |  | review_transient_symbol | True | False |
| AGR.B | 2005-05-30 00:00:00 | AGERE SYSTEMS INC. CL B | CS | XNYS | True |  | AGR |  | review_transient_symbol | True | False |
| AKO.A | 2016-10-25 00:00:00 | EMBOTELLADORA ANDINA S.A.SER-A | CS | XNYS | True | 3527553110.12 | AKO | 1994-07-07 00:00:00 | review_transient_symbol | True | False |
| AKO.B | 2016-10-24 00:00:00 | EMBOTELLADORA ANDINA S.A. S-B | CS | XNYS | True | 3802058584.7000003 | AKO | 1997-04-07 00:00:00 | review_transient_symbol | True | False |
| AMV.U | 2009-08-02 00:00:00 | ALETERNATIVE ASSET MGT ACQUISITION  CORP | CS | XASE | True |  | AMV |  | review_transient_symbol | True | True |
| ANE.U | 2008-11-09 00:00:00 | AMERICAN COMNTY NEWSPAPERS INC UTS 1 COM & 2 WT EXP 6/30/09 | CS | XASE | True |  | ANE |  | review_transient_symbol | True | True |
| AUO.T | 2005-07-31 00:00:00 | AU OPTRONICS CORP SPON ADR (TEMP) | CS | XNYS | True |  | AUO |  | review_transient_symbol | True | False |
| AXC.U | 2009-07-06 00:00:00 | ADVANCED TECHNOLOGY ACQUISITION CORP UNITS | CS | XASE | True |  | AXC |  | review_transient_symbol | True | True |


## Events -> quotes review/anomaly sample

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

