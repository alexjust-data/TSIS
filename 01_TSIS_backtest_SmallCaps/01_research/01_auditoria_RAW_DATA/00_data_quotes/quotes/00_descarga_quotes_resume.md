Polygon/Massive no tiene “endpoints distintos para CS” en elsentido de URL separadas.

Tiene endpoints de stocks, y tú filtras Common Stock con:

- market=stocks
- type=CS
- locale=us

La referencia maestra oficial es:

- Stocks Overview (https://massive.com/docs/stocks/)
- All Tickers (https://massive.com/docs/rest/stocks/tickers/all-tickers?auth=login)
- Ticker Overview (https://polygon.io/docs/rest/stocks/tickers/ticker-overview/)
- Changelog (https://www.massive.com/changelog)

Lista práctica de endpoints oficiales para U.S. common stocks (type=CS)

**Reference / Universe**

- GET /v3/reference/tickers
    - universo de tickers; aquí filtras market=stocks&type=CS&active=...&date=...
- GET /v3/reference/tickers/{ticker}
    - detalle del ticker; aquí salen market_cap, weighted_shares_outstanding, etc.
- GET /v3/reference/tickers/types
- GET /v3/reference/exchanges
- GET /vX/reference/tickers/{id}/events
    - experimental
- GET /v3/reference/splits
- GET /v3/reference/dividends

**Market Data / Historical**

- GET /v2/aggs/ticker/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}
- GET /v2/aggs/grouped/locale/us/market/stocks/{date}
- GET /v1/open-close/{stocksTicker}/{date}
- GET /v3/trades/{stockTicker}
- GET /v3/quotes/{stockTicker}

**Snapshots**

- GET /v2/snapshot/locale/us/markets/stocks/tickers
- GET /v2/snapshot/locale/us/markets/stocks/tickers/{stocksTicker}

**Fundamentals**

- GET /stocks/financials/v1/income-statements
- GET /stocks/financials/v1/balance-sheets
- GET /stocks/financials/v1/cash-flow-statements
- GET /stocks/financials/v1/ratios
- GET /stocks/financials/v1/short-interest
- GET /stocks/financials/v1/short-volume

**News**

- GET /v2/reference/news

**WebSocket**

- Stocks trades stream
- Stocks quotes stream
Links oficiales:
- Stocks WebSocket Quotes (https://massive.com/docs/websocket/stocks/quotes)
- Stocks WebSocket Trades (https://massive.com/docs/stocks/ws_stocks_t)

**Flat Files**

- us_stocks_sip/day_aggs_v1
- us_stocks_sip/minute_aggs_v1
- us_stocks_sip/quotes_v1
- us_stocks_sip/trades_v1
Ejemplo oficial:
- Day Aggregates Flat Files (https://massive.com/docs/flat-files/stocks/day-aggregates/2025/05)

Lo que necesitas para market cap PTI

- universo PTI:
    - GET /v3/reference/tickers
- market cap por ticker:
    - GET /v3/reference/tickers/{ticker}?date=YYYY-MM-DD

Ese segundo es el endpoint clave.

Sobre C:\TSIS_Data\data\reference
He revisado C:\TSIS_Data\data\reference y ahí solo hay:

- condition_codes.parquet
- exchanges.parquet
- market_status_upcoming.parquet
- ticker_types.parquet

No hay ahí:

- all tickers
- ticker overview
- market_cap
- weighted_shares_outstanding

O sea: en ese path no está toda la data que Polygon ofrece para esos endpoints.

PTI
PTI = Point In Time
Significa usar solo la información que estaba disponible en la fecha t, sin mirar el futuro.

Si quieres, el siguiente paso te hago:

- un script download_polygon_overview_marketcap_pti.py
- y otro audit_reference_coverage_vs_polygon_endpoints.py para dejar cerrado qué os falta descargar.



## cómo se construyeron tickers_2005_2026.parquet y tickers_2005_2026_upper.parquet.

**1. Origen base del universo**

  El universo base se construyó con `build_universe_pti.py`.

  Ese script llama a Polygon:

  - `GET /v3/reference/tickers`

  Y aplica estos filtros exactos en cada corte temporal:

```
  - market = stocks
  - locale = us
  - type = CS
  - exchange IN {XNAS, XNYS, XASE, ARCX}
  - date = snapshot_date
  - active:
      - por defecto all (activos + inactivos)
      - en vuestra corrida real fue all
```
  - date en la llamada es la fecha que se consulta a Polygon
  - snapshot_date en el parquet es esa misma fecha guardada localmente como sello del corte


  Eso se ve en el código:

```
  - params["market"] = "stocks"
  - params["locale"] = "us"
  - params["type"] = "CS"
  - params["exchange"] = exchange
  - params["date"] = date_str
  - active_filter = "all" por defecto, y solo cambia si pasas true/false

```

  **2. Frecuencia temporal usada**

**Qué significa PTI** Point In Time.

  Significa:

  - usar solo la información que estaba disponible en una fecha concreta t
  - sin usar datos del futuro
  - para evitar look-ahead bias

  Ejemplo:

  - si el 15 de marzo de 2014 quieres saber si un ticker era small-cap,
  - solo puedes usar:
      - el precio conocido ese día
      - y el último shares_outstanding que ya estuviera publicado en esa fecha
  - no puedes usar un filing de abril de 2014 para clasificar marzo de 2014

  La corrida real del panel PTI fue:
```
  - `frequency = daily`
```
  Eso está en:
```
  - `build_universe_pti.meta.json`
  - `build_universe_pti.progress.json`
```
  Y sus métricas reales fueron:

```
  - start = 2005-01-01
  - end = 2026-03-09
  - requested_cuts = 7738
  - successful_cuts = 7738
  - frequency = daily
  - active_filter = all
```

  **3. Cómo se deduplicó dentro de cada snapshot**

  Dentro de cada fecha, el script no se queda con todas las filas brutas. Deduplica por:

```
  - snapshot_date
  - entity_id
```
  Y prioriza calidad de registro con este orden:

```
  - has_composite_figi desc
  - has_share_class_figi desc
  - active desc
  - has_list_date desc
  - exchange_priority asc
```
  Además exchange_priority se define así:

```
  - XNAS = 0
  - XNYS = 1
  - XASE = 2
  - ARCX = 3
  - otros = 999
```

  **4. Cómo se construyó tickers_all.parquet**

  Después de construir el panel diario tickers_panel_pti, el script agrupa por entity_id y calcula:

```
  - first_seen_date = min(snapshot_date)
  - last_seen_date = max(snapshot_date)
```

  Luego toma la última fila observada por entity_id y genera:

```
  - tickers_all.parquet
```
  Y clasifica:
```
  - status = active si last_seen_date == last_snapshot
  - status = inactive si no
```
  En vuestra corrida:
```
  - entities = 15979
  - active = 5256
  - inactive = 10723
```

  **5. Cómo se construyó tickers_2005_2026.parquet**

  Ese archivo no se genera directamente desde Polygon. Se genera desde `tickers_all.parquet` usando
  `build_tickers_2005_2026.py`.

  Filtro exacto aplicado:

  - incluir si el intervalo `[first_seen_date, last_seen_date]` intersecta `[2005-01-01, 2026-12-31]`

  En código:
```
  - first_seen_date.notna()
  - last_seen_date.notna()
  - first_seen_date <= end
  - last_seen_date >= start
```
  Eso es todo.

  Por eso:
```
  - tickers_2005_2026.parquet
  - tiene 15979 filas
  - exactamente igual que tickers_all.parquet
```
  Eso te dice que, en vuestra corrida real, todas las entidades de *tickers_all* intersectaban la ventana
  2005-2026.

**  6. Cómo se construyó tickers_2005_2026_upper.parquet**

  Este archivo no añade filtros de negocio nuevos.
  Se construyó en notebook con esta transformación sobre tickers_2005_2026.parquet:

```
  - ticker = upper(trim(ticker))
  - eliminar ticker nulos o vacíos
  - drop_duplicates(subset=["ticker"])
  - sort_values("ticker")
```

  Ese paso está documentado en `01_data_fundamentals.ipynb`, donde se dejó esta lógica:

```
  - leer tickers_2005_2026.parquet
  - ticker a uppercase
  - deduplicar por ticker
  - guardar tickers_2005_2026_upper.parquet
```
  Por eso:
```
  - tickers_2005_2026.parquet = 15979 filas
  - tickers_2005_2026_upper.parquet = 12468 filas
```
  La diferencia exacta es:

  - 15979 - 12468 = 3511
  - esas 3511 filas no son “filtradas por fundamentals” ni “quitadas por market cap”
  - son colapsadas al deduplicar múltiples filas que compartían el mismo ticker


**7. Qué filtros exactos hubo, resumidos**

  Filtros de negocio reales del universo PTI original:
```
  - market = stocks
  - locale = us
  - type = CS
  - exchange ∈ {XNAS, XNYS, XASE, ARCX}
  - date diario entre 2005-01-01 y 2026-03-09
  - active_filter = all
```

  Filtro temporal para tickers_2005_2026.parquet:
```
  - intersección de [first_seen_date, last_seen_date] con [2005-01-01, 2026-12-31]
```
  Transformación para tickers_2005_2026_upper.parquet:
```
  - uppercase del ticker
  - trim
  - quitar nulos/vacíos
  - deduplicar por ticker
```

**8. Interpretación importante**

  `tickers_2005_2026_upper.parquet` **no es un universo PTI** “científico” completo.  
  Es un universo operativo por ticker único para descargas masivas por símbolo.

  Al deduplicar por ticker:

  - pierdes multiplicidad de entidades/cortes
  - ganas una lista limpia de símbolos para downloaders

  Por eso era válido para:

  - daily
  - 1m
  - fundamentals

  Pero no es la misma cosa que:

  - el panel PTI diario
  - ni el universo enriquecido por entidad

  Si quieres, el siguiente paso te hago un script de auditoría audit_universe_filters_exact.py que te deje
  en una celda:

  - filtros aplicados
  - conteos por fase
  - y diferencias exactas entre:
      - tickers_all
      - tickers_2005_2026
      - tickers_2005_2026_upper


### Un universo PTI completo sería:

```
- para cada fecha t
- la lista de todos los instrumentos que realmente existían y eran elegibles en t
- con sus atributos conocidos en t
- sin usar información futura
- y sin perder los que luego desaparecieron
```

En vuestro caso, para US Common Stocks, eso significa:

```
- fecha a fecha
- market=stocks
- locale=us
- type=CS
- exchanges objetivo
- activos e inactivos históricos que en esa fecha seguían vivos
- con identidad estable por entity_id/FIGI si es posible, no solo por ticker
```

Qué tendría un PTI completo de verdad

Para cada date:

```
- ticker
- entity_id
- primary_exchange
- type
- active/as-of
- list_date si ya era conocida
- delist_date solo si ya había ocurrido o era inferible sin futuro
- campos de identificación consistentes
- continuidad ante ticker changes / mergers / delistings
```

Y además:

```
- si una acción existió en 2008 y murió en 2011, tiene que estar en 2008-2011
- aunque hoy ya no exista
- si cambia de ticker, debes preservar la continuidad de identidad
- si el ticker se recicla, no debes mezclar dos entidades distintas
```

Qué sería “completo” en la práctica

Completo no significa “perfecto”.

Significa que cubre estas tres cosas:

**1. Cobertura temporal** - todos los cortes del periodo objetivo  
**2. Cobertura de entidades** - todos los CS elegibles en cada corte  
**3. Cobertura de lifecycle** - altas, bajas, cambios y discontinuidades sin survivorship bias  

Qué tenéis vosotros ahora

Lo más cercano a eso es: - `tickers_panel_pti`

Porque:

```
- está construido por fecha
- con date = snapshot_date
- con active_filter = all
- y luego se resume a tickers_all
```

Pero no es necesariamente “completo perfecto” porque depende de lo que Polygon resuelva bien
históricamente en All Tickers.

Por eso luego necesitasteis reforzar con:

```
- lifecycle oficial
- inactive catalog
- ticker events
- hybrid enriched
```

**Diferencia con una simple lista de tickers**

- `tickers_2005_2026_upper.parquet` no es un universo PTI completo

Es solo:
```
- una lista operativa de tickers únicos
- útil para descargar por símbolo
- pero no conserva la dimensión fecha-entidad
```

**Definición corta**


Un universo PTI completo es una tabla diaria histórica de elegibilidad e identidad, donde cada fila
responde:
```
“¿Qué acción común de EE. UU. existía ese día,   
    bajo qué identidad,   
    en qué exchange,   
    y con qué estado conocido en ese momento?”  
```



## Estamos descargando quotes y tiks... seguimos hilo conductor

 Cadena real

  1. En `00_descarga_datos_polygon_00.md` se define primero el universo base PTI, no el universo de quotes de producción.
  2. Ese universo base se construye con `build_universe_pti.py`, guardando en `data/reference/universe_pti`.
  3. Luego se audita con `agent_universe_audit.py`.
  4. Después se deriva un universo filtrado `“listed/deslisted” 2005-2026` a partir de ese panel PTI.
  5. Luego se enriquece con `build_universe_hybrid_enriched.py`.
  6. Después se aplica el filtro de población objetivo small-cap.
  7. De ahí sale el parquet que luego usa la corrida de quotes de producción para cruzarlo con lifecycle oficial y construir `tickers_quotes_prod.csv` y `tasks_quotes_prod.csv`.

**Cómo se llega al parquet upstream**

El markdown inicial no menciona directamente `tickers_2005_2026_upper_excluding_ohlcv_1m_missing_vs_daily_ge_2B_or_null.parquet` en el primer bloque porque ese archivo es posterior, no fundacional.

El hilo es:

- `build_universe_pti.py`
  genera:

  ```
    - *tickers_all.parquet*
    - *tickers_active.parquet*
    - *tickers_inactive.parquet*
    - panel PTI y QA
  ```

- Luego se deriva:

  ```
    - *tickers_2005_2026.parquet*
    - *tickers_2005_2026_upper.parquet*
  ```

Eso también está explicado en el propio `00_descarga_datos_polygon_00.md`: upper es la lista operativa deduplicada por ticker.

Después aparecen pasos de auditoría de cobertura entre daily y ohlcv_1m, y de ahí salen varios archivos derivados dentro de `data/reference/universe_pti`, entre ellos:

```
- tickers_missing_in_ohlcv_1m_vs_daily.csv
- tickers_missing_in_ohlcv_1m_vs_daily_lt_2B.csv
- tickers_2005_2026_upper_excluding_ohlcv_1m_missing_vs_daily_ge_2B_or_null.csv
- tickers_2005_2026_upper_excluding_ohlcv_1m_missing_vs_daily_ge_2B_or_null.parquet
```

El nombre te dice la lógica del filtro:

- partir de tickers_2005_2026_upper
- excluir tickers faltantes en ohlcv_1m frente a daily
- pero solo excluir los que sean >= 2B o market cap null
- preservar los missing con < 2B

Eso ya no es universo PTI bruto; es un universo operativo refinado para la población target.

**Cómo entra en quotes de producción**  

La celda del notebook de producción de quotes, en 

`agent_03_monitor_coverage_and_stats_realtime_v2_production.ipynb`,


usa explícitamente:

```
- universe = ...tickers_2005_2026_upper_excluding_ohlcv_1m_missing_vs_daily_ge_2B_or_null.parquet
- lifecycle = official_lifecycle_compiled.csv
```
Luego hace:
```
- u = pd.read_parquet(universe)
- lc = pd.read_csv(lifecycle)
- base = lc[lc["ticker"].isin(set(u["ticker"]))]
```
y de ahí construye:

```
- tickers_quotes_prod.csv
- tasks_quotes_prod.csv
- tasks_quotes_prod_meta.json
```

O sea:

- el parquet upstream no sale “directamente” del markdown inicial
- sale de varias transformaciones posteriores del universo PTI y de la población target

Punto fino importante
El markdown inicial mezcla varias capas:

- universo PTI base
- universo operativo por ticker
- universo híbrido enriquecido
- filtro de población target
- inputs concretos de descarga

Mi error fue tratar como si el parquet final fuese “el universo inicial”. No lo es. Es un universo derivado bastante
aguas abajo.

Dónde auditar el salto exacto
Si quieres seguir el hilo sin saltos, yo lo haría en este orden:

1. 00_descarga_datos_polygon_00.md
2. build_universe_pti.py
3. agent_universe_audit.py
4. build_tickers_2005_2026.py
5. build_tickers_2005_2026_upper_clean.py
6. Los artefactos de universe_pti que comparan ohlcv_1m vs daily
7. La celda de agent_03_monitor_coverage_and_stats_realtime_v2_production.ipynb que materializa
    tickers_quotes_prod.csv y tasks_quotes_prod.csv

**Mapa general**

  La tubería tiene 6 capas de transformación:

  1. Construcción del universo PTI base
  2. Derivación a lista operativa única de tickers
  3. Enriquecimiento e inferencia de estado/lifecycle
  4. Filtro de población target small-cap y filtro de cobertura ohlcv_1m vs daily
  5. Materialización del universo específico de quotes de producción
  6. Reconstrucción de faltantes reales hasta llegar a tasks_quotes_prod_missing_only_final_v2.csv



  **Rama 1. Universo PTI base**

  Objetivo:

  - construir un universo histórico 2005-2026 sin survivorship bias, no un snapshot actual

  Documento que lo define:

  - 00_descarga_datos_polygon_00.md

  Script que lo ejecuta:

  - build_universe_pti.py

  Qué hace:

  - llama a GET /v3/reference/tickers
  - por cortes temporales diarios
  - con:
      - market=stocks
      - locale=us
      - type=CS
      - exchanges XNAS, XNYS, XASE, ARCX
      - active_filter=all

  Salida principal:

  - tickers_panel_pti
  - tickers_all.parquet
  - tickers_active.parquet
  - tickers_inactive.parquet
  - QA:
      - qa_coverage_by_cut.csv
      - build_universe_pti.meta.json
      - build_universe_pti.progress.json

  Por qué se hizo:

  - para tener el spine temporal verdadero
  - no depender de tickers actuales
  - preservar activos e inactivos históricos

  Auditoría de cierre:

  - agent_universe_audit.py

  **Rama 2. Del panel PTI a lista operativa de tickers**


  Objetivo:

  - pasar del panel por entidad/corte a una lista práctica por ticker para descargas masivas

  Documento que lo explica:

  - el mismo 00_descarga_datos_polygon_00.md

  Paso 2A:

  - derivación de tickers_2005_2026.parquet
  - origen: tickers_all.parquet

  Lógica:

  - incluir entidades cuyo intervalo [first_seen_date, last_seen_date] intersecta [2005-01-01, 2026-12-31]

  Script asociado:

  - build_tickers_2005_2026.py

  Paso 2B:

  - derivación de tickers_2005_2026_upper.parquet

  Lógica:

  - ticker -> upper(trim())
  - quitar nulos/vacíos
  - deduplicar por ticker
  - ordenar

  Scripts asociados:

  - build_tickers_2005_2026_upper_clean.py
  - build_tickers_2005_2026_upper_remapped_review.py

  Por qué se hizo:

  - el PTI base trabaja bien para auditoría científica
  - pero los downloaders masivos necesitan una lista simple por símbolo

  **Rama 3. Enriquecimiento híbrido**


  Objetivo:

  - añadir market_cap, shares, cik, delisted, descripciones, etc.

  Script:

  - build_universe_hybrid_enriched.py

  Entrada:

  - tickers_2005_2026.parquet

  Salidas:

  - universe_hybrid_enriched_with_financial_ranges.parquet
  - QA en la carpeta hybrid_enriched

  Por qué se hizo:

  - el universo base no basta para decidir small-cap target
  - hacía falta información económica e histórica adicional

  **Rama 4. Del universo operativo al filtro target**


  Aquí está el punto clave que pedías.

  Antes del punto crítico
  Antes de tickers_2005_2026_upper_excluding_ohlcv_1m_missing_vs_daily_ge_2B_or_null.parquet, el flujo es:

  - universo por ticker único:
      - tickers_2005_2026_upper.parquet
  - auditoría de cobertura entre daily y ohlcv_1m
      - artefactos:
          - tickers_missing_in_ohlcv_1m_vs_daily.csv
          - tickers_missing_in_ohlcv_1m_vs_daily_lt_2B.csv
          - tickers_missing_in_ohlcv_1m_vs_daily.summary.json

  Scripts relacionados:

  - audit_ohlcv_input_vs_daily_vs_1m.py
  - audit_population_target_pti.py
  - build_population_target_pti.py

  Lógica de negocio:

  - no basta con ser ticker del universo
  - si un ticker falta en ohlcv_1m frente a daily, hay que decidir si excluirlo
  - pero no se excluye todo ciegamente
  - se preservan los que siguen siendo relevantes para small-cap target

  El punto crítico
  Archivo:

  - tickers_2005_2026_upper_excluding_ohlcv_1m_missing_vs_daily_ge_2B_or_null.parquet

  Qué significa exactamente:

  - parte de tickers_2005_2026_upper
  - detecta faltantes en ohlcv_1m frente a daily
  - excluye de la lista operativa los faltantes cuya condición es:
      - market cap >= 2B
      - o market cap null
  - mantiene los faltantes < 2B

  Por qué se hizo:

  - el objetivo no era tener “todo common stock”
  - era tener una población operativa centrada en small caps
  - un faltante en ohlcv_1m para un ticker grande o sin clasificación útil no merecía seguir en la cola operativa
  - en cambio los <2B sí se preservan por relevancia estratégica

  Ese parquet ya no es el universo PTI fundacional.
  Es un universo operativo refinado para el target final de trabajo.

  Después del punto crítico
  A partir de ese parquet, el flujo ya no es “construcción de universo” sino “materialización para quotes”.

  - agent_03_monitor_coverage_and_stats_realtime_v2_production.ipynb

  Celda relevante:

  - carga ese parquet como universe
  - carga official_lifecycle_compiled.csv como lifecycle
  - hace base = lc[lc["ticker"].isin(set(u["ticker"]))]
  - convierte list_date / delist_date
  - define end_date = delist_date.fillna(cutoff)
  - guarda:
      - tickers_quotes_prod.csv
      - tasks_quotes_prod.csv
      - tasks_quotes_prod_meta.json

  Por qué se hizo esa rama:

  - la descarga de quotes no se monta ya sobre el panel PTI ni sobre el híbrido completo
  - se monta sobre:
      - tickers del universo refinado
      - y su lifecycle oficial
  - eso permite generar el contrato de tareas ticker,date

  Importante
  Aquí está el origen directo del problema temporal que ya vimos:

  - esa celda usa pd.bdate_range(list_date, end_date)
  - no recorta a 2005-01-01
  - no usa calendario oficial XNYS
  - por eso tasks_quotes_prod.csv contiene fechas:
      - anteriores a 2005
      - posteriores a 2025
      - y algunos días hábiles no negociables por calendario real

  Ese error nace aquí, no en download_quotes.py.

  Rama 5. De tasks completas a faltantes
  Ahora el último tramo, hasta tu comando.

  Punto de partida:

  - tasks_quotes_prod.csv


• ARBOL DE DESARROLLO

  Nota de método
  Este texto no describe un pipeline formal perfectamente encapsulado en scripts únicos. Describe la reconstrucción más
  sólida del flujo realmente llevado a cabo hasta el último run, distinguiendo:

  - pasos confirmados por archivos, celdas o artefactos presentes
  - pasos inferidos con alta confianza a partir de nombres, outputs y dependencias visibles

  ———

  Mapa general

  La reconstrucción del flujo real hasta el último run puede dividirse en 6 ramas lógicas:

  1. Construcción del universo PTI base
  2. Derivación a lista operativa única de tickers
  3. Enriquecimiento e inferencia de estado/lifecycle
  4. Filtro de población target small-cap y filtro de cobertura ohlcv_1m vs daily
  5. Materialización manual-operativa del universo específico de quotes de producción
  6. Reconstrucción de faltantes reales hasta llegar a tasks_quotes_prod_missing_only_final_v2.csv

  ———

  Rama 1. Universo PTI base

  Objetivo

  - construir un universo histórico 2005-2026 sin survivorship bias, no un snapshot actual

  Documento que lo define

  - 00_descarga_datos_polygon_00.md

  Script que lo ejecuta

  - build_universe_pti.py

  Qué hace

  - llama a GET /v3/reference/tickers
  - por cortes temporales diarios
  - con:
      - market=stocks
      - locale=us
      - type=CS
      - exchanges XNAS, XNYS, XASE, ARCX
      - active_filter=all

  Salida principal

  - tickers_panel_pti
  - tickers_all.parquet
  - tickers_active.parquet
  - tickers_inactive.parquet
  - QA:
      - qa_coverage_by_cut.csv
      - build_universe_pti.meta.json
      - build_universe_pti.progress.json

  Por qué se hizo

  - para tener el spine temporal verdadero
  - no depender de tickers actuales
  - preservar activos e inactivos históricos

  Auditoría de cierre

  - agent_universe_audit.py

  Estado de esta rama

  - confirmado

  ———

  Rama 2. Del panel PTI a lista operativa de tickers

  Objetivo

  - pasar del panel por entidad/corte a una lista práctica por ticker para descargas masivas

  Documento que lo explica

  - el mismo 00_descarga_datos_polygon_00.md

  Paso 2A

  - derivación de tickers_2005_2026.parquet
  - origen: tickers_all.parquet

  Lógica

  - incluir entidades cuyo intervalo [first_seen_date, last_seen_date] intersecta [2005-01-01, 2026-12-31]

  Script asociado

  - build_tickers_2005_2026.py

  Paso 2B

  - derivación de tickers_2005_2026_upper.parquet

  Lógica

  - ticker -> upper(trim())
  - quitar nulos/vacíos
  - deduplicar por ticker
  - ordenar

  Scripts asociados

  - build_tickers_2005_2026_upper_clean.py
  - build_tickers_2005_2026_upper_remapped_review.py

  Por qué se hizo

  - el PTI base trabaja bien para auditoría científica
  - pero los downloaders masivos necesitan una lista simple por símbolo

  Estado de esta rama

  - confirmado en lo esencial
  - la secuencia exacta entre scripts auxiliares es consistente con los artefactos presentes

  ———

  Rama 3. Enriquecimiento híbrido

  Objetivo

  - añadir market_cap, shares, cik, delisted, descripciones y otros campos operativos

  Script

  - build_universe_hybrid_enriched.py

  Entrada

  - tickers_2005_2026.parquet

  Salidas

  - universe_hybrid_enriched_with_financial_ranges.parquet
  - QA en la carpeta hybrid_enriched

  Por qué se hizo

  - el universo base no basta para decidir small-cap target
  - hacía falta información económica e histórica adicional

  Estado de esta rama

  - confirmado como rama existente
  - no está demostrado que todos los artefactos finales de quotes dependan directamente de esta rama en todos sus campos,
    pero sí forma parte del ecosistema de refinamiento del universo

  ———

  Rama 4. Del universo operativo al filtro target

  Aquí está el punto clave.

  Antes del punto crítico

  Antes de tickers_2005_2026_upper_excluding_ohlcv_1m_missing_vs_daily_ge_2B_or_null.parquet, el flujo visible es:

  - universo por ticker único:
      - tickers_2005_2026_upper.parquet
  - auditoría de cobertura entre daily y ohlcv_1m
      - artefactos:
          - tickers_missing_in_ohlcv_1m_vs_daily.csv
          - tickers_missing_in_ohlcv_1m_vs_daily_lt_2B.csv
          - tickers_missing_in_ohlcv_1m_vs_daily.summary.json

  Scripts relacionados

  - audit_ohlcv_input_vs_daily_vs_1m.py
  - audit_population_target_pti.py
  - build_population_target_pti.py

  Lógica de negocio

  - no basta con ser ticker del universo
  - si un ticker falta en ohlcv_1m frente a daily, hay que decidir si excluirlo
  - no se excluye todo automáticamente
  - se preservan los que siguen siendo relevantes para small-cap target

  Estado de esta subrama

  - confirmado en artefactos
  - la lógica exacta final de composición del parquet resultante es inferida fuerte por nombre y outputs

  ———

  El punto crítico

  Archivo

  - tickers_2005_2026_upper_excluding_ohlcv_1m_missing_vs_daily_ge_2B_or_null.parquet

  Qué significa exactamente

  - parte de tickers_2005_2026_upper
  - detecta faltantes en ohlcv_1m frente a daily
  - excluye de la lista operativa los faltantes cuya condición es:
      - market cap >= 2B
      - o market cap null
  - mantiene los faltantes < 2B

  Por qué se hizo

  - el objetivo no era tener “todo common stock”
  - era tener una población operativa centrada en small caps
  - un faltante en ohlcv_1m para un ticker grande o sin clasificación útil no merecía seguir en la cola operativa
  - en cambio los <2B sí se preservan por relevancia estratégica

  Qué representa este parquet

  - ya no es el universo PTI fundacional
  - es un universo operativo refinado para el target final de trabajo

  Estado de esta subrama

  - confirmado como input real de la corrida de quotes
  - inferido fuerte en cuanto a la semántica exacta de su construcción por nombre y artefactos intermedios

  ———

  Después del punto crítico

  A partir de ese parquet, en esta corrida concreta, el flujo observado ya no sigue como “construcción de universo PTI”,
  sino como “materialización operativa de inputs para la descarga de quotes”.

  Notebook que hace el salto en esta corrida

  - agent_03_monitor_coverage_and_stats_realtime_v2_production.ipynb

  Aclaración crítica

  Esto no significa que “Agent03” sea conceptualmente el origen del flujo de negocio.
  Significa que, en esta corrida concreta, dentro de ese notebook se metió una celda manual de preparación operativa que
  se usó como puente para materializar inputs de producción.

  Es decir:

  - el notebook de Agent03 fue usado como contenedor operativo
  - esa celda construyó los CSV de entrada para Agent01
  - eso no convierte a Agent03 en la capa arquitectónica dueña del universo

  Celda relevante

  - carga ese parquet como universe
  - carga official_lifecycle_compiled.csv como lifecycle
  - hace base = lc[lc["ticker"].isin(set(u["ticker"]))]
  - convierte list_date / delist_date
  - define end_date = delist_date.fillna(cutoff)
  - guarda:
      - tickers_quotes_prod.csv
      - tasks_quotes_prod.csv
      - tasks_quotes_prod_meta.json

  Por qué se hizo esta rama

  - en esta corrida, la descarga de quotes se montó operativamente sobre:
      - tickers del universo refinado
      - y su lifecycle oficial
  - eso permitió generar el contrato de tareas ticker,date

  Importante

  Aquí está el origen directo del problema temporal que ya vimos:

  - esa celda usa pd.bdate_range(list_date, end_date)
  - no recorta a 2005-01-01
  - no usa calendario oficial XNYS
  - por eso tasks_quotes_prod.csv contiene fechas:
      - anteriores a 2005
      - posteriores a 2025
      - y algunos días hábiles no negociables por calendario real

  Ese error nace aquí, no en download_quotes.py.

  Estado de esta subrama

  - confirmado por lectura directa de la celda
  - confirmado por los outputs materializados en el run

  ———

  Rama 5. De tasks completas a faltantes

  Ahora el último tramo, hasta el comando actual.

  Punto de partida

  - tasks_quotes_prod.csv

  Ese archivo es el contrato completo ticker,date que se quiso descargar para la corrida de producción.

  Qué ocurre después

  A partir de ese contrato completo, corrió Agent01 y generó:

  - download_events_history.csv
  - download_events_current.csv
  - download_live_status.json
  - download_state.json

  Después aparece una fase de reparación y reconciliación, visible en estos artefactos:

  - download_events_current.repaired_from_history.csv
  - download_events_current.repaired_summary.json
  - disk_quotes_inventory.csv
  - disk_quotes_inventory.refreshed_after_powerloss.csv
  - disk_quotes_inventory.full_refreshed.csv
  - reconcile_disk_vs_history_summary.json
  - reconcile_history_not_in_disk.csv
  - reconcile_disk_not_in_history.csv

  Qué indica esto

  - no se siguió solo el estado normal current/history de Agent01
  - hubo una fase extraordinaria de reconciliación entre:
      - historia lógica de descargas
      - y presencia física real en disco

  Por qué se hizo

  - para reconstruir con mayor fidelidad qué faltaba de verdad
  - especialmente tras inconsistencias de estado, refresh de inventario o powerloss

  Estado de esta subrama

  - confirmado en artefactos
  - el script exacto que produce el CSV final no está identificado de forma única, pero la reconstrucción del proceso es
    fuerte

  ———

  Rama 6. Llegada a tasks_quotes_prod_missing_only_final_v2.csv

  Output final previo al comando actual

  - tasks_quotes_prod_missing_only_final_v2.csv

  Qué representa

  - no es el contrato completo original
  - es el subconjunto final de tareas consideradas faltantes tras:
      - el contrato inicial tasks_quotes_prod.csv
      - la historia de descargas
      - la reparación de current desde history
      - el inventario real de disco
      - y una segunda pasada de reconciliación/ajuste

  Qué sabemos verificado

  - está contenido en tasks_quotes_prod.csv
  - no contiene tickers fuera de tickers_quotes_prod.csv
  - no se corresponde con una resta simple tasks_quotes_prod - current
  - ni tampoco una simple resta única frente a repaired_from_history
  - incorpora una pasada adicional de ajuste, consistente con la reconciliación real del run

  Por qué se hizo

  - para no relanzar el universo completo
  - para reintentar solo los faltantes reales reconstruidos con mejor fidelidad

  Estado de esta subrama

  - confirmado como artefacto final usado por el run
  - inferido fuerte en cuanto al proceso exacto de composición

  ———

  Comando final actual

  Con ese CSV final, se ejecuta:

  python C:\TSIS_Data\02_backtest_SmallCaps\scripts\download_quotes.py --csv C:
  \TSIS_Data\v1\backtest_SmallCaps\runs\polygon_realtime_audit\20260313_quotes_prod_full_12133_clean\inputs\tasks_quotes
  _prod_missing_only_final_v2.csv --output D:\quotes --concurrent 24 --run-id 20260313_quotes_prod_full_12133_clean
  --run-dir C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit\20260313_quotes_prod_full_12133_clean
  --resume --task-batch-size 500

  Qué hace aquí download_quotes.py

  - toma como contrato de trabajo solo el CSV de faltantes finales
  - con --resume vuelve a excluir task_key ya cerrados en download_events_current.csv
  - si el parquet ya existe y es legible, lo cierra como resume_existing_file
  - intenta descargar únicamente el subconjunto todavía abierto

  Estado de esta rama

  - confirmado

  ———

  Resumen final del hilo real

  00_descarga_datos_polygon_00.md
  -> build_universe_pti.py
  -> tickers_all.parquet
  -> tickers_2005_2026.parquet
  -> tickers_2005_2026_upper.parquet
  -> auditoría/filtro ohlcv_1m vs daily + target
  -> tickers_2005_2026_upper_excluding_ohlcv_1m_missing_vs_daily_ge_2B_or_null.parquet
  -> celda manual-operativa en agent_03_monitor_coverage_and_stats_realtime_v2_production.ipynb
  -> tickers_quotes_prod.csv
  -> tasks_quotes_prod.csv
  -> primera descarga Agent01
  -> repair current from history
  -> disk inventory + reconciliation
  -> tasks_quotes_prod_missing_only_final.csv
  -> tasks_quotes_prod_missing_only_final_v2.csv
  -> comando actual de download_quotes.py

  ———

  Conclusión de auditoría

  La mejor reconstrucción del flujo realmente ejecutado en el último run es:

  - el universo nace en build_universe_pti.py
  - luego se transforma en una lista operativa de tickers
  - luego se refina por cobertura y target
  - en esta corrida concreta, una celda manual dentro de un notebook de Agent03 se utilizó como puente operativo para
    materializar tickers_quotes_prod.csv y tasks_quotes_prod.csv
  - después corrió Agent01
  - y finalmente hubo una fase extraordinaria de reparación y reconciliación que produjo
    tasks_quotes_prod_missing_only_final_v2.csv, que es el input del comando actual



## Continuación: reconstrucción limpia v2 hasta el comando nuevo de quotes

Una vez reconstruido el hilo real del run histórico, se decidió no seguir extendiendo el estado viejo
`20260313_quotes_prod_full_12133_clean` como fuente única de verdad.

La decisión operativa fue:

- mantener `D:\quotes` como repositorio físico de parquets ya descargados
- pero reconstruir un contrato limpio nuevo de tareas
- con ventana temporal explícita y corregida
- y lanzar un `Agent01` nuevo con `--resume` sobre ese mismo root

Eso da lugar a un run nuevo:

- `20260319_quotes_clean_v2_draft`

La idea no es redescargar todo desde cero, sino:

- regenerar el contrato correcto
- reaprovechar `D:\quotes`
- y descargar solo los `ticker,date` que sigan ausentes


## principio rector de la v2

La v2 no cambia el universo refinado upstream.

Sigue usando:

- `tickers_2005_2026_upper_excluding_ohlcv_1m_missing_vs_daily_ge_2B_or_null.parquet`
- `official_lifecycle_compiled.csv`

Lo que sí cambia es la forma de materializar el contrato de `ticker,date`:

- se recorta explícitamente a `2005-01-01 .. 2026-12-31`
- se evita el desborde temporal del run viejo
- se prepara un `run_dir` nuevo
- se deja `QUOTES_ROOT = D:\quotes`
- y se usa `--resume`


## dónde se materializó la v2

La materialización de la v2 se dejó en:

- `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification_v2\04_agent01_clean_run_preparation.ipynb`

Ese notebook:

- no descarga datos
- no valida datos
- no hace coverage
- no hace recovery
- solo construye los inputs del run limpio nuevo


## artefactos fuente de la v2

Inputs oficiales usados por el builder limpio:

- `C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti\tickers_2005_2026_upper_excluding_ohlcv_1m_missing_vs_daily_ge_2B_or_null.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\data\reference\official_lifecycle_compiled.csv`

Política temporal explícita:

- `RUN_DATE_FROM = 2005-01-01`
- `RUN_DATE_TO = 2026-12-31`

Política operativa provisional:

- `business_day_intersection_with_run_window`

Importante:

- esta v2 sigue usando `pd.bdate_range`
- no usa todavía calendario oficial XNYS
- pero ya corrige el principal error del run viejo:
  - no genera fechas anteriores a 2005
  - no genera fechas posteriores a 2026-12-31


## construcción del universo efectivo del run limpio

El notebook v2 hace:

- `u = read_parquet(universe_refined)`
- `lc = read_csv(official_lifecycle)`
- normaliza `ticker`
- convierte `list_date` y `delist_date`

Luego construye `base` así:

- `base = lc[lc["ticker"].isin(set(u["ticker"]))]`
- `run_start = max(list_date, 2005-01-01)`
- `run_end = min(delist_date or 2026-12-31, 2026-12-31)`
- elimina filas inválidas
- deja una fila por ticker

Resultado observado en la corrida limpia:

- `universe_refined_rows = 12133`
- `universe_refined_unique_tickers = 12133`
- `official_lifecycle_rows = 1970`
- `effective_run_tickers = 1961`

Esto mantiene exactamente la intersección operativa que ya se había observado en producción:

- universo refinado upstream
- cruzado con lifecycle oficial
- universo efectivo final = `1961` tickers


## construcción de tasks_quotes_prod_v2_clean.csv

Sobre `base`, la v2 expande por día hábil:

- para cada ticker
- desde `run_start`
- hasta `run_end`

Y materializa:

- `ticker`
- `date`

Sin permitir:

- fechas anteriores a `2005-01-01`
- fechas posteriores a `2026-12-31`

Artefactos generados:

- `C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit\20260319_quotes_clean_v2_draft\inputs\tickers_quotes_prod_v2_clean.csv`
- `C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit\20260319_quotes_clean_v2_draft\inputs\tasks_quotes_prod_v2_clean.csv`
- `C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit\20260319_quotes_clean_v2_draft\inputs\tasks_quotes_prod_v2_clean.meta.json`

Metadatos observados:

- `run_id = 20260319_quotes_clean_v2_draft`
- `tickers_count = 1961`
- `tasks_total = 3304899`
- `date_min = 2005-01-03`
- `date_max = 2026-12-31`

Interpretación:

- `2005-01-03` es correcto
- porque `2005-01-01` cayó en sábado
- y la política actual sigue siendo `bdate_range`


## por qué se lanza una corrida nueva y no se sigue solo con la vieja

El run viejo `20260313_quotes_prod_full_12133_clean` quedó operativamente útil, pero con dos problemas:

1. El contrato de tareas venía contaminado por el builder viejo:

- fechas anteriores a 2005
- fechas posteriores al rango deseado
- días hábiles no equivalentes a trading days oficiales

2. El estado `download_events_current.csv` quedó mezclado con scopes distintos:

- task_keys del recovery actual
- task_keys heredados de otras fases
- lo que degradó la interpretación de `tasks_already_ok`

Por eso, la estrategia v2 fue:

- no tocar el universo refinado upstream
- no borrar `D:\quotes`
- no perder el trabajo ya descargado
- pero reconstruir un `run_dir` limpio y un `tasks.csv` limpio


## cómo funciona el resume en la v2

El comando nuevo usa:

- `--resume`
- `--output D:\quotes`
- `run_id` nuevo
- `run_dir` nuevo

Eso implica dos niveles distintos de resume:

1. Resume por estado del run nuevo

- al inicio es cero
- porque `download_events_current.csv` del run nuevo nace vacío

2. Resume por disco existente

- cada tarea calcula su path esperado en `D:\quotes`
- si el parquet ya existe
- y es legible
- se cierra como `resume_existing_file`

Conclusión:

- el run nuevo no empieza de cero físicamente
- pero sí recorre de cero el contrato v2
- y va cerrando como `OK` gran parte de lo ya presente en disco


## artefactos que deja el run nuevo al arrancar

En el `run_dir` nuevo:

- `download_events_current.csv`
- `download_events_history.csv`
- `download_live_status.json`
- `download_state.json`
- `download_retry_queue_current.csv`

Lectura inicial observada:

- `tasks_total = 3304899`
- `tasks_current_rows = 8000`
- `DOWNLOADED_OK = 4793`
- `DOWNLOADED_EMPTY = 3207`
- `done_bad = 0`

Y, muy importante:

- la mayoría de los primeros `DOWNLOADED_OK` eran `resume_existing_file`

Eso confirma que:

- el reaprovechamiento de `D:\quotes` funciona
- el run nuevo está reconociendo parquets ya existentes
- y no está pegando a Polygon para todos esos casos


## lectura operativa de salud del run nuevo

Estado observado al arranque:

- run limpio nuevo correctamente separado por `run_id`
- `run_dir` nuevo
- contrato v2 correcto
- `resume` sobre disco funcionando
- sin `DOWNLOAD_FAIL` en el tramo inicial observado

Eso significa que la mecánica básica de la v2 es sana:

- contrato corregido
- estado limpio
- disco reutilizado
- progreso incremental consistente

Lo que todavía no resuelve esta v2:

- no usa calendario oficial XNYS
- no presemilla el estado desde disco antes de arrancar
- por tanto el arranque recorre todo el contrato y detecta `resume_existing_file` tarea a tarea


## comando final de quotes v2

Una vez materializados los artefactos de entrada, el comando lanzado para quotes v2 es:

```powershell
python C:\TSIS_Data\02_backtest_SmallCaps\scripts\download_quotes.py --csv C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit\20260319_quotes_clean_v2_draft\inputs\tasks_quotes_prod_v2_clean.csv --output D:\quotes --concurrent 32 --run-id 20260319_quotes_clean_v2_draft --run-dir C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit\20260319_quotes_clean_v2_draft --resume --task-batch-size 1000
```

Qué hace este comando:

- toma el contrato limpio `tasks_quotes_prod_v2_clean.csv`
- usa `D:\quotes` como repositorio compartido ya poblado
- usa `--resume`
- reutiliza parquets ya presentes si son legibles
- descarga desde Polygon solo lo que siga faltando


## resumen final del nuevo hilo v2

```text
00_descarga_datos_polygon_00.md
-> build_universe_pti.py
-> tickers_all.parquet
-> tickers_2005_2026.parquet
-> tickers_2005_2026_upper.parquet
-> auditoría/filtro ohlcv_1m vs daily + target
-> tickers_2005_2026_upper_excluding_ohlcv_1m_missing_vs_daily_ge_2B_or_null.parquet
-> official_lifecycle_compiled.csv
-> 04_agent01_clean_run_preparation.ipynb
-> tickers_quotes_prod_v2_clean.csv
-> tasks_quotes_prod_v2_clean.csv
-> tasks_quotes_prod_v2_clean.meta.json
-> nuevo run_id 20260319_quotes_clean_v2_draft
-> download_quotes.py con --resume sobre D:\quotes
```


## conclusión operativa

La v2 de quotes no cambia la base del universo.

Lo que cambia es:

- el contrato temporal
- la limpieza del `run_dir`
- la trazabilidad del run
- y la forma de reutilizar el disco ya descargado

Por eso, el objetivo de la v2 no es:

- reconstruir `D:\quotes` desde cero

Sino:

- tener un contrato limpio y auditable
- reaprovechar el trabajo ya hecho
- y cerrar solo los `ticker,date` que faltan de verdad bajo la ventana correcta `2005-2026`
