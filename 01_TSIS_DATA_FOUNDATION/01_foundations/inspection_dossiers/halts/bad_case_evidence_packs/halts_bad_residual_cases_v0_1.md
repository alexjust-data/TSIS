# Halts Bad Residual Cases v0.1

Fuente: cache historico read-only de `halts`.

## Lectura

Muestra el residuo estructural duro: un evento canonico y 11 raws Nasdaq vacios.

## Que muestra

Casos o tablas representativas derivados de los indices historicos.

## Responde

Que familias concretas sostienen el estado institucional del bucket.

## No responde

No reemplaza la inspeccion manual de todos los eventos ni prueba calidad de quotes/trades por si solo.

## Consecuencia

Estos casos soportan estado `bad_residual_marginal` bajo las limitaciones del readout.

## Bad unusable canonical event

| event_id_canonical | rows | source_count | sources | ticker | issuer_name | halt_date | halt_start_et | resume_trade_et | halt_code | halt_type | release_no | is_sec_suspension | has_cross_source_overlap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NA/NA/NA/NA/NA | 11 | 1 | nasdaq |  |  |  |  |  |  |  |  | False | False |


## Nasdaq raw missing payload residual rows

| residual_reason | ticker | issuer_name | halt_date | halt_start_et | resume_trade_et | halt_code | halt_type | url_source | raw_description_text |
|---|---|---|---|---|---|---|---|---|---|
| raw_missing_payload |  |  |  |  |  |  |  | https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts&haltdate=01022020 |  |
| raw_missing_payload |  |  |  |  |  |  |  | https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts&haltdate=01022024 |  |
| raw_missing_payload |  |  |  |  |  |  |  | https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts&haltdate=01032007 |  |
| raw_missing_payload |  |  |  |  |  |  |  | https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts&haltdate=01032008 |  |
| raw_missing_payload |  |  |  |  |  |  |  | https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts&haltdate=02232018 |  |
| raw_missing_payload |  |  |  |  |  |  |  | https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts&haltdate=03192004 |  |
| raw_missing_payload |  |  |  |  |  |  |  | https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts&haltdate=04292020 |  |
| raw_missing_payload |  |  |  |  |  |  |  | https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts&haltdate=04292021 |  |
| raw_missing_payload |  |  |  |  |  |  |  | https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts&haltdate=10302006 |  |
| raw_missing_payload |  |  |  |  |  |  |  | https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts&haltdate=10302007 |  |
| raw_missing_payload |  |  |  |  |  |  |  | https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts&haltdate=10302008 |  |

