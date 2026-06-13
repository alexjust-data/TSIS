# Reference Good Identity And Payload Cases v0.1

Fuente: cache historico read-only de `reference`.

## Lectura

Muestra que la capa principal de identidad, splits y dividends tiene payload real y consumible con flags.

## Que muestra

Casos representativos derivados de los indices historicos.

## Responde

Que familias concretas sostienen el estado institucional del bucket.

## No responde

No reemplaza la lectura poblacional ni prueba causalidad economica universal.

## Consecuencia

Estos casos soportan estado `good` bajo las limitaciones del readout.

## Good identity sample

| ticker | request_date | name | type | primary_exchange | active | market_cap | ticker_root | list_date | identity_bucket | transient_symbol_flag | suffix_variant_flag |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 2022-02-08 00:00:00 | Agilent Technologies Inc. | CS | XNYS | True | 42294551949.1 | A | 1999-11-18 00:00:00 | good_identity_snapshot | False | False |
| AA | 2016-10-31 00:00:00 | Alcoa, Inc. | CS | XNYS | True | 5373602381.84 | AA | 2016-10-18 00:00:00 | good_identity_snapshot | False | False |
| AAA | 2007-05-21 00:00:00 | ALTANA AKTIENGESELLSCHAFT SPON ADR | CS | XNYS | True |  | AAA |  | good_identity_snapshot | False | False |
| AABA | 2019-10-06 00:00:00 | Altaba Inc. Common Stock | CS | XNAS | True |  | AABA |  | good_identity_snapshot | False | False |
| AAC | 2010-02-07 00:00:00 | ABLEAUCTIONS, COM, INC. | CS | XASE | True |  | AAC |  | good_identity_snapshot | False | False |
| AACB | 2026-03-09 00:00:00 | Artius II Acquisition Inc. Class A Ordinary Shares | CS | XNAS | True | 286159500.0 | AACB | 2025-04-07 00:00:00 | good_identity_snapshot | False | False |
| AACI | 2025-10-29 00:00:00 | Armada Acquisition Corp. II Class A Ordinary Shares | CS | XNAS | True | 325061100.0 | AACI | 2025-06-24 00:00:00 | good_identity_snapshot | False | False |
| AACQ | 2021-06-24 00:00:00 | Artius Acquisition Inc. Class A Common Stock | CS | XNAS | True |  | AACQ |  | good_identity_snapshot | False | False |
| AACT | 2025-09-24 00:00:00 | Ares Acquisition Corporation II | CS | XNYS | True | 587048666.88 | AACT | 2023-06-12 00:00:00 | good_identity_snapshot | False | False |
| AAGR | 2024-09-25 00:00:00 | African Agriculture Holdings Inc. Common Stock | CS | XNAS | True | 7673141.658 | AAGR | 2023-12-07 00:00:00 | good_identity_snapshot | False | True |


## Good split event sample

| execution_date | id | split_from | split_to | ticker | _dataset | _ingested_utc | in_lt1b_universe | split_ratio | split_bucket |
|---|---|---|---|---|---|---|---|---|---|
| 2014-11-03 00:00:00 | P0aaf033e6aef34f079ad26bca97901315558d2724efa7085cf4668790481ed84 | 1000.0 | 1398.0 | A | splits | 2026-03-11T10:17:39.101290+00:00 | False | 1.398 | good_split_event |
| 2016-10-06 00:00:00 | P715dae3fd2648963d34ceb3071a443a55df15931623c0f2e489ac7b1f389d346 | 3.0 | 1.0 | AA | splits | 2026-03-11T10:17:39.101290+00:00 | False | 0.3333333333333333 | good_split_event |
| 2016-11-01 00:00:00 | P9fc8565ef1c585f2961910ccfadfc9dfcf169569e6ac33cab84ef5620cbceacb | 801.0 | 1000.0 | AA | splits | 2026-03-11T10:17:39.101290+00:00 | False | 1.2484394506866416 | good_split_event |
| 2004-05-12 00:00:00 | E8cd57402e059ac7a943b0ebadef35f723d73bd58dca379cc19e12888b63704a8 | 1.0 | 2.0 | AABA | splits | 2026-03-11T10:17:39.119054+00:00 | False | 2.0 | good_split_event |
| 2009-01-15 00:00:00 | Ed0a982e38d42bc3612de8ce3083b3d3dc8d22057fb7c5ffac5c710fd7fee4844 | 12.0 | 1.0 | AAC | splits | 2026-03-11T10:17:40.082132+00:00 | False | 0.08333333333333333 | good_split_event |
| 2010-02-05 00:00:00 | E08cc0dd6db945be498e364ac1f8cd28757afd555d523f5838cc08f094b440fa8 | 20.0 | 1.0 | AAC | splits | 2026-03-11T10:17:40.082132+00:00 | False | 0.05 | good_split_event |
| 2009-10-07 00:00:00 | E801b7d99d0d4dbb65401d5309ef09db1700a93d4262f0b28996ea8a78fbbe1f6 | 20.0 | 1.0 | AAIC | splits | 2026-03-11T10:17:41.142742+00:00 | True | 0.05 | good_split_event |
| 2023-11-01 00:00:00 | E3ce0c5695f4f8a1d657a878973380d58690d8283f93eca63cc1690cdd5c4fefe | 1.0 | 1.7 | AAMC | splits | 2026-03-11T10:17:41.627809+00:00 | True | 1.7 | good_split_event |
| 2006-01-09 00:00:00 | E62636711084c9f5255b5b4a9c9450312c67106ab94c2c5fb7b7c8c9501878d22 | 20.0 | 1.0 | AAMI | splits | 2026-03-11T10:17:42.069748+00:00 | False | 0.05 | good_split_event |
| 2007-08-22 00:00:00 | Ef20b5bad4fa10d4b7f406c9bbbeda94c49a7769612a53b6ae5899667a6390c3d | 1.0 | 1.5 | AAON | splits | 2026-03-11T10:17:42.255371+00:00 | False | 1.5 | good_split_event |


## Good dividend event sample

| ticker | cash_amount | currency | dividend_type | ex_dividend_date | pay_date | record_date | dividend_bucket | in_lt1b_universe |
|---|---|---|---|---|---|---|---|---|
| AAT | 0.17 | USD | CD | 2011-03-11 | 2011-03-31 | 2011-03-15 | good_dividend_event | False |
| AAT | 0.21 | USD | CD | 2011-06-13 | 2011-06-30 | 2011-06-15 | good_dividend_event | False |
| AAT | 0.21 | USD | CD | 2011-09-13 | 2011-09-30 | 2011-09-15 | good_dividend_event | False |
| AAT | 0.21 | USD | CD | 2011-12-13 | 2011-12-29 | 2011-12-15 | good_dividend_event | False |
| AAT | 0.21 | USD | CD | 2012-03-13 | 2012-03-30 | 2012-03-15 | good_dividend_event | False |
| AAT | 0.21 | USD | CD | 2012-06-13 | 2012-06-29 | 2012-06-15 | good_dividend_event | False |
| AAT | 0.21 | USD | CD | 2012-09-12 | 2012-09-28 | 2012-09-14 | good_dividend_event | False |
| AAT | 0.21 | USD | CD | 2012-12-12 | 2012-12-28 | 2012-12-14 | good_dividend_event | False |
| AAT | 0.21 | USD | CD | 2013-03-13 | 2013-03-29 | 2013-03-15 | good_dividend_event | False |
| AAT | 0.21 | USD | CD | 2013-06-12 | 2013-06-28 | 2013-06-14 | good_dividend_event | False |

