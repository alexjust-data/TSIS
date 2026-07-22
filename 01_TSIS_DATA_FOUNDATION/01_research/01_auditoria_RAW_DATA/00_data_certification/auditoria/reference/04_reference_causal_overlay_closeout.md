# Reference Causal Overlay Closeout

## Alcance de esta fase

Esta primera fase causal de `reference` ya no se limita a tres enlaces.

Queda materializada sobre cuatro frentes:

- `splits -> trades`
- `splits -> daily / ohlcv_1m`
- `events (ticker_change) -> halts`
- `events (ticker_change) -> quotes`
- `identity review -> trades sample`

La idea es medir si `reference` ya actua como capa explicativa real y no solo como repositorio de metadatos.

## Artefactos causales

- [reference_overview_market_identity_links.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_overview_market_identity_links.parquet)
- [reference_split_market_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_split_market_link_candidates.parquet)
- [reference_split_daily_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_split_daily_link_candidates.parquet)
- [reference_split_1m_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_split_1m_link_candidates.parquet)
- [reference_event_halt_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_event_halt_link_candidates.parquet)
- [reference_event_quotes_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_event_quotes_link_candidates.parquet)
- [reference_causal_alignment_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_causal_alignment_summary.parquet)

## 1. `splits -> trades`

El cruce se rehizo contra el artefacto masivo:

- `trades_cd_root_cause_final_bucket.parquet`

y no contra la muestra de `layer6_policy_examples`.

Resultado:

- `split_explains_trade_scale_mismatch`: `9`
- `split_near_scale_mismatch_review`: `13`

### Lectura

Aqui si aparece una senal causal defendible.

Los `9` casos `split_explains_trade_scale_mismatch` tienen esta forma:

- `scale_suspect` en `trades`
- ratio de split muy cercano al factor de escala observado
- distancia temporal `same_day` o `near_3d`

Casos representativos:

- `APCX`
- `CCTG`
- `GDEV`
- `NUTX`
- `VINO`

La lectura operativa es fuerte:

- `reference` si explica una parte real del bloque `scale_suspect`
- pero no explica el grueso del residuo global de `trades`

Eso ademas es coherente con lo ya cerrado en `trades`: la hipotesis "todo es split / corporate action" no aguanta como explicacion dominante, pero si explica un subconjunto real y quirurgico.

## 2. `splits -> daily / 1m`

Se anadio una segunda comprobacion contra raw market data:

- [reference_split_daily_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_split_daily_link_candidates.parquet)
- [reference_split_1m_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_split_1m_link_candidates.parquet)

Resultado:

- `splits_vs_daily`
  - `daily_split_ratio_review`: `1`
  - `review_no_daily_alignment`: `21`
- `splits_vs_1m`
  - `m1_split_ratio_review`: `1`
  - `review_no_1m_alignment`: `21`

### Lectura

- la explicacion por split si aparece con claridad en `trades`
- pero casi no se replica de forma limpia en el raw `daily` ni en el raw `1m` alrededor del `execution_date`

Esto no invalida la senal de `trades`, pero si obliga a una lectura mas estricta:

- `reference` ayuda a explicar un subconjunto de `scale_suspect`
- esa explicacion parece ser principalmente de comparabilidad `trades vs reference`
- no puede venderse todavia como explicacion ya confirmada por todas las capas de mercado

### Limite actual

Los `13` casos `split_near_scale_mismatch_review` quedan en zona gris:

- estan a `4-7` dias del split
- la proximidad es plausible
- pero no es todavia lo bastante estrecha para cerrar causalidad sin revision manual

### Calibracion visual manual

Se reviso manualmente una muestra amplia de casos visuales del bucket `split_explains_trade_scale_mismatch`:

- `SST`
- `NUTX`
- `APCX`
- `NLSP`
- `GDEV`
- `VINO`
- `CCTG`
- `LRHC`
- `RMTI`

Lectura consolidada:

- la familia aguanta bien como bucket `good`
- en casi todos los casos `quotes` y `trades` convergen en una historia de escala compatible con el split cercano
- algunos casos tienen limites parciales, por ejemplo falta de `raw quotes` o outliers tardios, pero no rompen la lectura principal

Decision:

- `split_explains_trade_scale_mismatch` pasa a `good`
- `split_near_scale_mismatch_review` se mantiene en `review`

## 3. `events (ticker_change) -> halts`

El primer cruce bruto inflaba resultados porque un mismo evento podia enlazar con muchos halts del mismo ticker.

Eso ya se corrigio:

- se conserva solo el halt mas cercano por evento

Resultado final:

- `ticker_change_near_halt`: `775`
- `reference_event_near_halt_review`: `173`

Desglose:

- `same_day`: `355`
- `near_3d`: `420`
- `near_30d`: `173`

### Lectura

Esta es una de las dos senales causales mas fuertes de `reference` por ahora.

Conclusion:

- el endpoint `events`, aunque hoy casi solo aporte `ticker_change`, si enlaza de forma material con secuencias de `halts`
- `ticker_change` no es una nota cosmetica: parece convivir con una parte relevante de la microestructura anomala o de los eventos de suspension/reanudacion

### Limite actual

No todo `ticker_change_near_halt` debe interpretarse como causalidad economica cerrada.

Todavia falta distinguir:

- cambio administrativo de simbolo
- cambio corporativo con friccion real
- simple coincidencia temporal en ventanas de dias cargados

### Calibracion visual manual

Se revisaron manualmente casos representativos:

- `AARD`
- `ACHV`
- `AISP`
- `AEYE`

Lectura consolidada:

- `AARD`, `ACHV` y `AISP` si dejan una secuencia visual coherente entre `reference`, `halt` y reaccion de mercado
- `AEYE` queda mas ambiguo por iliquidez extrema y libro demasiado escalonado

Decision:

- `ticker_change_near_halt` pasa a `good` cuando la reaccion visual del mercado y el halt son coherentes
- los casos con mercado demasiado ralo o ambiguo quedan en `review`

## 4. `events (ticker_change) -> quotes`

Este cruce ya aporta una segunda senal fuerte y, de hecho, mas grande en masa que `events -> halts`.

Resultado:

- `ticker_change_near_quotes_anomaly`: `2330`
- `reference_event_near_quotes_review`: `247`
- `reference_event_near_quotes_clean`: `18`

Desglose temporal:

- `ticker_change_near_quotes_anomaly`
  - `same_day`: `1836`
  - `near_3d`: `494`
- `reference_event_near_quotes_review`
  - `near_30d`: `247`
- `reference_event_near_quotes_clean`
  - `same_day`: `14`
  - `near_3d`: `2`
  - `near_30d`: `2`

Desglose de severidad en el bloque fuerte:

- `HARD_FAIL`: `431`
- `SOFT_FAIL`: `1899`
- `PASS`: `0`

Casos representativos con anomalia `same_day`:

- `SRTS | 2016-07-25`
- `SPAQ | 2023-01-30`
- `RILY | 2015-07-16`
- `RSSS | 2020-03-23`
- `BKKT | 2024-04-29`
- `MI | 2024-04-12`

Patron observado:

- `event_type = ticker_change`
- `quotes` con `SOFT_FAIL` o `HARD_FAIL`
- crossed ratio significativo, a veces extremo
- proximidad `same_day` o `near_3d`

Hechos adicionales:

- `513` casos marcan `timestamp_out_of_partition_day = True`
- `357` casos tienen `crossed_ratio_pct > 1`
- la mediana de `crossed_ratio_pct` es modesta en el bloque `SOFT_FAIL`, pero en `HARD_FAIL` sube a `2.08%`

### Lectura

Aqui ya no estamos ante un enlace marginal.

La lectura operativa correcta es:

- `ticker_change` convive de forma material con anomalias en `quotes`
- `reference` ya explica una parte real del residuo microestructural de `quotes`
- esa explicacion no es solo por volumen de filas, sino por proximidad temporal y severidad observable

Esto ademas es coherente con `halts`: una parte de los cambios de ticker no son neutrales, sino que coinciden con dias administrativamente o microestructuralmente fragiles.

### Limite actual

El bucket `ticker_change_near_quotes_anomaly` todavia mezcla:

- cambios de ticker con friccion real de mercado
- cambios de ticker que simplemente caen en un dia ya ruidoso
- casos donde la anomalia de `quotes` es pequena pero el bucket entra por regla mecanica

### Calibracion visual manual

Se revisaron manualmente casos representativos:

- `RSSS`
- `RDCM`
- `MVBF`
- `RZLT`

Lectura consolidada:

- la familia si contiene anomalia real en `quotes`
- pero visualmente no emerge todavia como bucket `good` limpio
- predominan mercados muy ralos, outliers extremos o libros tan pobres que cuesta atribuir causalidad fuerte al `ticker_change`

Decision:

- `ticker_change_near_quotes_anomaly` se mantiene en `review`
- el bucket sigue siendo valioso como detector y como fuente de casos, pero no cierra todavia como explicacion causal limpia

## 5. `identity review -> trades`

Resultado:

- `identity_review_without_trades_link`: `746`
- `identity_review_linked_to_scale_mismatch`: `2`
- `identity_review_linked_to_other_trades_case`: `2`

### Lectura

Aqui la senal es debil y eso tambien es informacion util.

Implica:

- la mayoria del residuo de identidad (`overview 404`, remaps y simbolos especiales) no aparece todavia en la muestra manual de `trades`
- por tanto, este frente no debe sobredimensionarse como explicacion del problema de mercado

La conclusion correcta no es "identity no importa", sino:

- identity ya es importante estructuralmente
- pero en esta primera capa causal todavia no emerge como explicador dominante de los casos de `trades` ya auditados

## Politica preliminar `good / review / bad`

Con la calibracion visual ya hecha:

- `good`
  - `split_explains_trade_scale_mismatch`
  - `ticker_change_near_halt` cuando el halt y la reaccion de mercado se ven de forma coherente
- `review`
  - `split_near_scale_mismatch_review`
  - `ticker_change_near_quotes_anomaly`
  - `ticker_change_near_halt` cuando el mercado es demasiado ralo, ambiguo o dominado por iliquidez
  - `reference_event_near_halt_review`
  - `reference_event_near_quotes_review`
  - `identity review` residual
- `bad`
  - no emerge todavia una familia agregada `bad`

## Decision operativa de esta fase

`reference` ya supera claramente el nivel de simple soporte estatico.

Con la evidencia actual:

- `splits` si explican un subconjunto real de `scale_suspect` en `trades`
- `ticker_change` si enlaza con `halts` de forma material
- `ticker_change` si enlaza con `quotes` de forma aun mas masiva
- `identity review` todavia tiene poca traccion causal directa sobre la muestra `trades`

La lectura fuerte es esta:

- el valor causal dominante de `reference` hoy no sale de `identity`
- sale de `corporate actions`, sobre todo `ticker_change`, y de una forma mas quirurgica de `splits`

## Que queda abierto

1. cruzar `events` tambien con casos de `trades`, no solo con `halts` y `quotes`
2. endurecer el tratamiento de outliers visuales extremos en algunos `quotes-only`
3. decidir si merece partir `ticker_change_near_quotes_anomaly` en subfamilias mas limpias

## Estado

`reference` queda ya en un nivel alto:

- fase estructural cerrada
- primera fase causal materializada
- `events -> quotes` ya confirmado como frente fuerte
- viewer causal ya implementado
- politica causal preliminar ya fijada
