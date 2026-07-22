# Ohlcv 1m Schema Contract - Modulo 01

## 1. Rol

Este documento define el schema logico canonico para `ohlcv_1m_raw`.

Su objetivo es fijar la unidad semantica minima del dataset `ohlcv_1m` sin depender de detalles accidentales del layout legacy ni de una vista derivada posterior.

Este schema gobierna la capa raw observada de barras intradia de un minuto.

No gobierna por si solo:

- `ohlcv_1m_split_normalized`
- `daily_adjusted`
- `quotes_raw`
- `trades_raw`

La capa `ohlcv_1m_split_normalized` tiene su contrato especifico en:

- `01_foundations/contract_registry/dataset_contracts/ohlcv_1m_split_normalized_dataset_contract_v0_1.md`

## 2. Unidad logica

La unidad logica canonica es:

- `ticker-minute bar`

Cada fila representa una barra agregada de un minuto para un instrumento y un timestamp intradia concreto.

## 3. Claves logicas

Claves minimas:

- `ticker`
- `minute_timestamp`

Notas:

- `ticker` puede venir como columna o derivarse de metadata, particion o file identity;
- `minute_timestamp` puede materializarse fisicamente como `ts_utc`, `ts` o equivalente parseable;
- `date`, `year` y `month` pueden vivir como columnas, particion, metadata o derivarse desde `minute_timestamp`.

## 4. Campos requeridos

Campos requeridos del schema logico:

- `ticker`
- `minute_timestamp`
- `date`
- `year`
- `month`
- `open`
- `high`
- `low`
- `close`
- `volume`

## 5. Alias fisicos observados

El layout raw observado en `D:\ohlcv_1m` puede usar nombres fisicos abreviados.

Mapeo fisico -> logico:

- `ts_utc` -> `minute_timestamp`
- `ts` -> `minute_timestamp`
- `o` -> `open`
- `h` -> `high`
- `l` -> `low`
- `c` -> `close`
- `v` -> `volume`
- `vw` -> `vwap`
- `n` -> `bar_count`
- `t` -> `epoch_millis` o timestamp vendor-equivalente

Ejemplo inspeccionado:

- `D:\ohlcv_1m\ticker=HSLV\year=2026\month=03\minute_aggs_HSLV_2026_03.parquet`

Schema fisico observado:

- `ticker`
- `ts_utc`
- `date`
- `year`
- `month`
- `o`
- `h`
- `l`
- `c`
- `v`
- `vw`
- `n`
- `t`

## 6. Campos condicionales relevantes

Campos relevantes cuando existan:

- `vw`
- `n`
- `t`

Interpretacion:

- `vw` = precio medio ponderado o VWAP de la barra de un minuto cuando la fuente lo provee;
- `n` = numero de eventos, prints o agregados usados para construir la barra, segun semantica vendor;
- `t` = timestamp numerico vendor-equivalente, normalmente util para trazabilidad o reconciliacion temporal.

## 7. Tipos semanticos esperados

- `ticker`: identificador simbolico de instrumento
- `minute_timestamp`: timestamp parseable, preferentemente UTC
- `date`: fecha de sesion o fecha calendario asociada a la barra, parseable como fecha
- `year`: entero coherente con `date` o `minute_timestamp`
- `month`: entero coherente con `date` o `minute_timestamp`
- `open`, `high`, `low`, `close`: numericos positivos o validamente parseables
- `volume`: numerico no negativo
- `vwap`: numerico o nulo segun fuente y caso
- `bar_count`: entero o numerico no negativo cuando exista

## 8. Reglas estructurales minimas

Las siguientes reglas forman parte del schema operativo:

- `minute_timestamp` debe ser parseable;
- `ticker` debe ser estable dentro del file salvo limitacion declarada;
- `date`, `year` y `month` deben ser reconciliables con la particion y el timestamp;
- `high` no debe ser menor que `open`, `low` o `close` en filas validas;
- `low` no debe ser mayor que `open`, `high` o `close` en filas validas;
- `open`, `high`, `low`, `close` no deben ser cero o negativos en filas validas;
- `volume` no debe ser negativo;
- `minute_timestamp` no debe duplicarse dentro de un mismo `ticker` y file mensual salvo que exista semantica documentada de duplicacion;
- `vw`, cuando exista, no debe evaluarse de forma binaria ingenua fuera de su policy de calidad.

## 9. Reglas de interpretacion

Este schema no declara que cualquier desviacion de `vw` implique corrupcion dura.

La auditoria raw historica de `1m` muestra que el problema dominante puede vivir en familias `vw_*`, pero la interpretacion de esas familias corresponde a:

- `01_foundations/inspection_dossiers/minute/raw_1m_lt1b_closeout_recalculation_v0_1.md`
- `01_foundations/module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md`

La lectura correcta separa:

- schema y parseabilidad;
- integridad primaria OHLCV;
- comportamiento de `vw`;
- coverage real del universo `lt1b`;
- y vistas derivadas como `1m_split_normalized`.

## 10. Relacion con `ohlcv_1m_split_normalized`

`ohlcv_1m_raw` representa la barra observada en escala raw.

`ohlcv_1m_split_normalized` representa esa misma barra reexpresada por `future_split_factor` para comparabilidad mecanica entre sesiones.

Por tanto:

- este schema raw define la estructura minima de entrada;
- el contrato `ohlcv_1m_split_normalized_dataset_contract_v0_1.md` define la vista derivada y sus columnas adicionales.

## 11. Exclusiones duras

Las filas o files con problemas como:

- timestamp no parseable;
- OHLC no positivo en filas validas;
- `high < max(open, low, close)`;
- `low > min(open, high, close)`;
- volumen negativo;
- identidad temporal o de ticker irreconciliable;

no deben entrar en consumo principal sin rehabilitacion explicita.

Eso no convierte automaticamente todo warning `vw` en exclusion dura.

La decision final debe pasar por validators y policies del bloque `1m`.

## 12. Relacion con consumidores

`ohlcv_1m_raw` es valido como verdad local observada de barras intradia para:

- features intrasesion locales;
- inspeccion de estructura intradia;
- arbitro fino frente a `trades_raw`;
- comparacion forense con `daily_raw`.

No debe usarse sin declaracion semantica para:

- features cross-session afectadas por splits;
- labels economicos diarios;
- portfolio valuation;
- benchmarking ajustado.

Para features cross-session con riesgo de split contamination debe usarse la disciplina de:

- `ohlcv_1m_split_normalized`

segun su contrato propio.

## 13. Evidencia fisica inicial

El file:

- `D:\ohlcv_1m\ticker=HSLV\year=2026\month=03\minute_aggs_HSLV_2026_03.parquet`

fue inspeccionado como primer ejemplo fisico del schema raw.

Resultado observado:

- `rows = 2616`
- columnas presentes: `ticker`, `ts_utc`, `date`, `year`, `month`, `o`, `h`, `l`, `c`, `v`, `vw`, `n`, `t`
- `ticker_unique = 1`
- `year_month_unique = 2026-03`
- `ts_utc_parse_nulls = 0`
- `duplicate_ts_utc = 0`
- `nonpositive_ohlc = 0`
- `negative_volume = 0`
- `high_rule_violations = 0`
- `low_rule_violations = 0`
- rango temporal observado: `2026-03-11 13:45:00+00:00` a `2026-03-27 20:00:00+00:00`

Este ejemplo confirma el layout fisico raw actual y justifica el alias canonico:

- `ts_utc` -> `minute_timestamp`

## 14. Politica de cambio

Requieren actualizar este documento:

- cambio en columnas raw minimas;
- cambio de alias fisicos aceptados;
- cambio en la unidad logica `ticker-minute bar`;
- cambio en reglas estructurales de OHLCV;
- cambio en la interpretacion de `ts_utc`, `ts` o `t`;
- incorporacion de un validator institucional especifico de `ohlcv_1m_raw`.

## 15. Conclusion operacional

`ohlcv_1m_raw` queda definido como dataset intradia raw de barras de un minuto.

Su schema canonico es compatible con el layout fisico observado en `D:\ohlcv_1m`, siempre que se declare explicitamente el mapeo de alias fisicos abreviados a campos logicos.

Este contrato no promueve por si solo la calidad raw de todo `1m`.

Solo fija la estructura canonica minima que deben usar validators, dossiers y vistas derivadas posteriores.
