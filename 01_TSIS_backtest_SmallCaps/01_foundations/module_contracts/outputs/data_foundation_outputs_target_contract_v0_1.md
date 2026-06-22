# Data Foundation Outputs Target Contract v0.1

## Estado

Tipo: module contract.

Modulo: `01_TSIS_backtest_SmallCaps`.

Ambito: `CAPA 1 - DATA FOUNDATION`.

Status: `provisional_design_contract`.

Este documento no materializa tablas. Define que outputs deben existir, para que
sirven, de donde debe salir su informacion, como trabajan cuando aparece un
evento y que no deben contener.

## Graphify Context Consultado

Este contrato fue preparado despues de consultar tres contextos Graphify del
proyecto:

```text
C:/TSIS_Data/00_CTO/graphify-out/graph.json
C:/TSIS_Data/00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/graphify-out/graph.json
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/graphify-out/_graphify_staging_foundations_authority_20260620/graphify-out/graph.json
```

Lectura usada:

- `00_CTO` fija la arquitectura de laboratorio y la separacion entre datos,
  eventos, outcomes, estrategias, ML, decision y ejecucion.
- `10_DATA_QUALITY_HARNESS` refuerza que todo dataset consumible debe tener
  evidence assets, validator contract, registry entry, visual reading protocol y
  final acceptance criteria.
- `foundations_authority` enlaza dataset contracts, data audit standard,
  completion standard, inspection dossiers, validators, registries y consumption
  policies.

Limitacion conocida:

```text
foundations_authority_20260620 existe y es consultable, pero tiene remediation
Graphify pendiente para chunks 13-16. Por tanto se usa como mapa de orientacion,
no como unica autoridad final.
```

La autoridad final de este contrato debe seguir siendo:

```text
contrato + certificacion + evidencia + profiling fisico + validator
```

## Principio Central

Las tablas objetivo de Data Foundation no son otra copia de toda la raw data.

Son una capa canonicamente organizada para que las capas posteriores puedan
preguntar:

```text
que instrumento era?
que sesion era?
que precio/view corresponde?
que corporate actions aplican?
que contexto diario existia?
que paso intradia?
que microestructura habia?
que calidad tiene este dato?
puedo usar este caso para backtest, ML, ejecucion o solo forense?
```

La informacion completa se conserva en las fuentes raw/auditadas. Las tablas
maestras deben guardar lo necesario para operar y enlazar el resto mediante
keys estables.

## Cuando Aparece Un Evento

Supongamos que el Event Engine evalua:

```text
ticker = ABCD
date = 2021-05-14
event_window = 09:30:00-10:15:00 ET
```

El uso correcto de Data Foundation no es leer un parquet gigante unico.

El flujo correcto es:

1. `instrument_master`
   - resuelve identidad temporal;
   - confirma si `ABCD` era common stock, warrant, ETF, ADR, ticker antiguo,
     ticker activo/inactivo o remap;
   - evita survivorship bias y errores por ticker label.

2. `market_calendar`
   - define si `2021-05-14` fue trading day;
   - define premarket, regular session, after-hours, early close y timezone;
   - evita construir eventos en ventanas no comparables.

3. `corporate_actions_table`
   - identifica splits, dividends, ticker events y remaps relevantes;
   - decide que price view usar: `raw`, `split_normalized`, `adjusted` o
     `adjusted_proxy`;
   - evita que un split o dividendo se lea como gap/evento falso.

4. `master_daily_table`
   - entrega el contexto diario del ticker/date;
   - gap, volumen, RVOL, market cap/float cuando existan, flags de noticia,
     halt, calidad y price view;
   - permite decidir si el dia entra en el universo de investigacion.

5. `master_intraday_bar_table`
   - entrega barras intradia canonicas, normalmente 1m;
   - permite detectar primer push, HOD, pullbacks, VWAP, PM volume,
     opening drive y evolucion del evento;
   - no debe contener todo quotes/trades bruto.

6. `microstructure_features_table`
   - consulta solo la ventana del evento cuando se necesita libro/tape;
   - calcula spread, crossed/locked, bid/ask depth, trade intensity,
     odd-lots, fuera de NBBO y liquidez usable;
   - alimenta execution realism y filtros de viabilidad.

7. `halts_table`
   - detecta si el evento fue interrumpido por halt, resume quote/trade o SEC
     suspension;
   - ajusta outcomes y simulacion.

8. `fundamentals_asof_table`, `short_context_table`, `regime_context_table`,
   `news_context_table`, `real_time_corporate_event_alerts_table`
   - agregan contexto solo si tienen semantica `as-of`;
   - capturan eventos corporativos market-moving publicados en segundos o
     minutos;
   - no deben contaminar el evento con informacion publicada despues.

9. `dataset_certification_matrix` y `data_quality_report`
   - deciden si el caso es `backtest_core`, `research`, `ml_flagged`,
     `forensic` o `quarantine`;
   - no son fuentes de mercado, son gates y evidencia.

Resultado:

```text
Data Foundation no produce el evento.
Data Foundation produce el estado defendible que permite detectar el evento.
```

El Event Engine consumira estas tablas y escribira `event_table` en una capa
posterior.

## Regla De Diseno: Core Delgado + Sidecars Pesados

El error a evitar es crear una tabla diaria/intradia enorme con todo mezclado.

La forma correcta es:

```text
raw/audited sources
  -> canonical compact master tables
  -> sidecar context/microstructure tables
  -> event-window joins controlados
```

Esto no pierde informacion. La conserva en capas con roles claros:

- master tables: estado canonico y keys;
- sidecars: informacion pesada o especializada;
- raw/audited sources: verdad completa preservada;
- data_quality_report: evidencia de auditoria y gates.

## Outputs Objetivo

### 1. `instrument_master`

Alias historico/arquitectonico:

```text
symbol_master
```

Nombre preferido:

```text
instrument_master
```

Motivo: `symbol` o `ticker` es una etiqueta temporal. La identidad economica
real puede sobrevivir a ticker changes, remaps, splits, mergers o cambios de
listing.

Clase:

```text
reference/context table
```

Grain recomendado:

```text
instrument_id + valid_from + valid_to
```

Keys:

```text
instrument_id
ticker
date/as_of_date
composite_figi
share_class_figi
cik
```

Fuentes candidatas:

```text
E:/TSIS/data/reference/all_tickers/
E:/TSIS/data/reference/overview/
E:/TSIS/data/reference/events/
E:/TSIS/data/reference/ticker_types/
E:/TSIS/data/reference/exchanges/
E:/TSIS/data/additional/ipos/
E:/TSIS/data/financial/
```

Muestra fisica:

```text
file: E:/TSIS/data/reference/all_tickers/snapshot_date=2005-01-02.parquet
rows_in_file: 2632
columns: ticker, name, market, locale, primary_exchange, type, active,
currency_name, cik, composite_figi, share_class_figi, last_updated_utc,
snapshot_date

ticker  name                         market  locale  primary_exchange  type  active
A       AGILENT TECHNOLOGIES, INC    stocks  us      XNYS              CS    True
AA      ALCOA INC                    stocks  us      XNYS              CS    True
```

Materializacion actual:

```text
dataset_id: instrument_master_v0_1
path: E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet
rows: 4824
tickers: 4824
build_run_id: instrument_master_v0_1_20260621T145725Z
sha256: 69104387d2607306c3fa1740573d130db5e7c30b1d1527d3ee8a8d2b4d53c2d2
manifest: E:/TSIS/data/data_foundation_outputs/instrument_master/_instrument_master_manifest_v0_1.json
summary: E:/TSIS/data/data_foundation_outputs/instrument_master/_instrument_master_summary_v0_1.csv
hard_fail_count: 0
duplicate_ticker_count: 0
```

Lectura institucional:

```text
instrument_master_v0_1 existe como primera materializacion compacta.
Su grano actual es ticker del universo lt1b_universe_v0_1.
No resuelve continuidad economica completa ni membership diaria fully PTI.
```

Uso en evento:

- confirma que el ticker era instrumento elegible ese dia;
- evita tratar warrants, preferred, ETFs o ADRs como common stock si la
  estrategia exige common stock;
- resuelve cambios de ticker antes de unir historico.

No debe contener:

- OHLCV;
- features de estrategia;
- resultados forward-looking;
- labels ML.

### 2. `corporate_actions_table`

Clase:

```text
reference/context table
```

Grain recomendado:

```text
instrument_id/ticker + action_date + action_type + source
```

Fuentes candidatas:

```text
E:/TSIS/data/reference/splits/
E:/TSIS/data/reference/dividends/
E:/TSIS/data/reference/events/
E:/TSIS/data/additional/corporate_actions/
01_foundations/module_contracts/corporate_actions_adjustment_methodology.md
```

Muestra fisica:

```text
file: E:/TSIS/data/reference/splits/ticker=A/splits_A.parquet
rows_in_file: 1
columns: execution_date, id, split_from, split_to, ticker, _dataset,
_ingested_utc

execution_date  split_from  split_to  ticker
2014-11-03      1000        1398      A
```

Muestra fisica adicional:

```text
file: E:/TSIS/data/reference/dividends/ticker=A/dividends_A.parquet
rows_in_file: 1
columns: ticker, _dataset, _ingested_utc

ticker  _dataset
A       dividends
```

Uso en evento:

- decide si un gap es movimiento de mercado o ajuste corporativo;
- alimenta `split_normalized` y `adjusted`;
- evita que ML aprenda splits/dividendos como alpha;
- separa `signal_price_view`, `execution_price_view` y
  `valuation_price_view`.

No debe contener:

- precios OHLCV ya ajustados como unica verdad;
- decisiones de estrategia;
- reparaciones manuales sin lineage.

Estado materializado inicial:

```text
dataset_id: corporate_actions_table_v0_1
path: E:/TSIS/data/data_foundation_outputs/corporate_actions_table/corporate_actions_table_v0_1.parquet
rows: 104757
tickers: 3621
instrument_ids: 3497
action_type_counts:
  dividend: 92033
  split: 6630
  ticker_change: 6094
source_system_counts:
  additional: 52490
  reference: 52267
first_action_date: 1969-12-31
last_action_date: 2027-06-15
build_run_id: corporate_actions_table_v0_1_20260622T144845Z
output_sha256: 01989eb301a2cdd83e297fbf6384e0bd4d5b4fb300bdccee6b1adbde87d5e4ce
hard_fail_count: 0
duplicate_corporate_action_id_count: 0
invalid_split_terms_count: 0
negative_dividend_amount_count: 0
within_instrument_valid_window_false_count: 39525
cross_source_overlap_groups: 51336
test_evidence: C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_four_tables_v0_1/
```

Lectura institucional:

```text
corporate_actions_table_v0_1 existe como tabla de contexto corporativo y
lineage de ajustes. reference se conserva como fuente primaria y additional
como fuente secundaria/reconciliacion. La tabla no resuelve continuidad
economica completa entre ticker changes ni produce precios ajustados finales.
```

### 3. `market_calendar`

Alias arquitectonico:

```text
calendar_table
```

Clase:

```text
reference/context table
```

Grain recomendado:

```text
date + market + session
```

Fuentes candidatas:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/data/reference/market_calendar_official_XNYS_20050101_20251231.parquet
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/data/reference/market_calendar_official_XNYS_20050101_20251231.meta.json
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/agent05_build_market_calendar_official.py
exchange_calendars calendar = XNYS
timezone = America/New_York
01_foundations/module_contracts/market_session_scope.md
```

Estado:

```text
TSIS official local calendar candidate, replicable byte-for-byte with the
current builder and dependency version.
```

Verificacion local:

```text
builder: C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/agent05_build_market_calendar_official.py
dependency: exchange_calendars 4.13.1
command:
python scripts/agent05_build_market_calendar_official.py ^
  --calendar XNYS ^
  --start 2005-01-01 ^
  --end 2025-12-31 ^
  --tz America/New_York ^
  --out-dir <output_dir>

current parquet sha256:
8aac3ea4f7fbcaf6c394320f53acc1524bf5e5e3addbcd48ef31718bc0214228

regenerated parquet sha256:
8aac3ea4f7fbcaf6c394320f53acc1524bf5e5e3addbcd48ef31718bc0214228

match: True
rows: 5283
first_session: 2005-01-03
last_session: 2025-12-31
early_close_sessions: 45
calendar: XNYS
timezone: America/New_York
```

Uso en evento:

- define premarket, regular, after-hours y early close;
- permite calcular `minute_index`, PM volume, opening drive y event windows;
- evita comparar una sesion incompleta con una sesion normal.

No debe contener:

- datos por ticker salvo excepciones de expected coverage;
- halts como si fueran calendario base;
- features de precio.

Fuentes externas para contraste y replicacion:

```text
exchange_calendars project:
https://github.com/gerrymanoim/exchange_calendars

NYSE Holidays & Trading Hours:
https://www.nyse.com/markets/hours-calendars

Nasdaq Stock Market Holiday Schedule:
https://www.nasdaq.com/market-activity/stock-market-holiday-schedule
```

Nota institucional:

```text
El fichero local puede llamarse oficial dentro de TSIS porque tiene builder,
metadata, hashes y reproduccion exacta. No debe describirse como descarga raw
directa de NYSE. Su fuente tecnica directa es exchange_calendars; NYSE/Nasdaq
son fuentes externas de contraste para reglas de holidays, early closes y
regular trading hours.
```

Materializacion actual:

```text
dataset_id: market_calendar_v0_1
path: E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet
rows: 5283
calendar: XNYS
timezone: America/New_York
first_session: 2005-01-03
last_session: 2025-12-31
early_close_sessions: 45
build_run_id: market_calendar_v0_1_20260622T072422Z
source_parquet_sha256: 8aac3ea4f7fbcaf6c394320f53acc1524bf5e5e3addbcd48ef31718bc0214228
output_sha256: 96bd60c124e6552d269f8846205ed28bf6e58881453a5bbb4f73ced0657b56d5
hard_fail_count: 0
duplicate_session_count: 0
```

Lectura institucional:

```text
market_calendar_v0_1 existe como tabla limpia de CAPA 1.
El source local conserva el calendario oficial candidato reproducible.
El output materializado normaliza tipos y agrega lineage para consumo downstream.
```

### 4. `expected_data_calendar`

Clase:

```text
certification/quality table
```

Grain recomendado:

```text
dataset_family + ticker/instrument_id + date + expected_session
```

Motivo:

`market_calendar` dice si el mercado existe. `expected_data_calendar` dice si
esperamos que una familia tenga dato para un ticker/date concreto.

Fuentes candidatas:

```text
instrument_master
market_calendar
dataset_registry/
data_consumption_policies/
inspection_dossiers/
data_quality_report/
```

Uso en evento:

- diferencia `missing porque no debia existir` de `missing porque fallo data`;
- gobierna `expected`, `present`, `healthy`, `usable`.

No debe contener:

- precio;
- retornos;
- features de estrategia.

Estado materializado inicial:

```text
dataset_id: expected_data_calendar_v0_1
path: E:/TSIS/data/data_foundation_outputs/expected_data_calendar/expected_data_calendar_v0_1
layout: partitioned parquet dataset by dataset_family/year
rows: 29029152
dataset_families: daily_raw, ohlcv_1m_raw, quotes_raw, trades_raw
rows_per_family: 7257288
tickers: 4824
first_session: 2005-01-03
last_session: 2025-12-31
parquet_file_count: 84
tree_sha256: 1c7571cdcefc1ffd3f0f6cda921d32d64dee33cc41c3676809686c1bc575a57f
build_run_id: expected_data_calendar_v0_1_20260622T141019Z
hard_fail_count: 0
duplicate_key_groups: 0
invalid_window_count: 0
test_evidence: C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_instrument_master_market_calendar_expected_data_calendar_v0_1/
```

Lectura institucional:

```text
expected_data_calendar_v0_1 existe como denominador contractual de cobertura.
Declara expectativas por familia/ticker/sesion; no mide presencia real ni
calidad. Los reports posteriores deben unirlo contra presencia fisica,
validadores de familia y data_quality_report.
```

### 5. `master_daily_table`

Clase:

```text
analytical master table
```

Grain recomendado:

```text
instrument_id/ticker + date + price_view
```

Price views permitidas:

```text
daily_raw
split_normalized
adjusted
adjusted_proxy solo para evidencia forense, no como vista core final
```

Fuentes candidatas:

```text
E:/TSIS/data/ohlcv_daily/
E:/TSIS/data/ohlcv_daily_adjusted/
E:/TSIS/data/reference/
E:/TSIS/data/additional/news/
E:/TSIS/data/additional/ipos/
E:/TSIS/data/financial/
E:/TSIS/data/short/
E:/TSIS/data/Halts/
E:/TSIS/data/regime_indicators/
```

Muestra fisica raw:

```text
file: E:/TSIS/data/ohlcv_daily/ticker=ZZ/year=2006/day_aggs_ZZ_2006.parquet
rows_in_file: 185
columns: ticker, date, year, o, h, l, c, v, vw, n, t

ticker  date        o      h      l      c      v
ZZ      2006-04-07  17.50  18.20  17.30  17.50  23847400.0
ZZ      2006-04-10  17.61  17.62  16.76  16.84   2916300.0
```

Muestra fisica adjusted:

```text
file: E:/TSIS/data/ohlcv_daily_adjusted/ticker=ZZ/year=2006/day_aggs_ZZ_2006_adjusted.parquet
rows_in_file: 185
columns: ticker, date, year, o, h, l, c, v, vw, n, t,
future_split_factor, o_split_normalized, h_split_normalized,
l_split_normalized, c_split_normalized, future_dividend_factor,
future_adjustment_factor, o_adjusted, h_adjusted, l_adjusted, c_adjusted
```

Uso en evento:

- calcula contexto previo: gap, prior close, daily range, dollar volume, RVOL;
- identifica si el dia cumple filtros de universo/evento;
- aporta market cap/float solo si vienen de fuentes `as-of`;
- alimenta Event Engine y Outcome Research diario.

No debe contener:

- todo el libro quotes;
- todo el tape trades;
- fundamentales sin `filing_date`;
- noticias sin `published_utc`;
- labels forward-looking como features.

Estado materializado inicial:

```text
dataset_id: master_daily_table_v0_1
path: E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1
layout: partitioned parquet dataset by year/price_view
rows: 21771864
expected_daily_rows: 7257288
price_views: daily_raw, split_normalized, adjusted
rows_per_price_view: 7257288
data_present_rows: 19782153
missing_expected_data_rows: 1989711
selected_price_hard_invalid_rows: 0
negative_volume_rows: 0
backtest_core_row_candidate_rows: 19782153
rows_with_corporate_action: 92979
parquet_file_count: 63
tree_sha256: 1c9c39202514e41a879261a62e0dbcae054bb7e503b40e6e0e44138f38894e9e
build_run_id: master_daily_table_v0_1_20260622T161747Z
hard_fail_count: 0
test_evidence: C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_six_tables_v0_1/
```

Lectura institucional:

```text
master_daily_table_v0_1 existe como superficie diaria compacta para eventos,
backtest diario y research. Mantiene grano instrument/ticker/session/price_view
y no mezcla `daily_raw`, `split_normalized` y `adjusted` en una fila opaca.
Conserva filas missing esperadas para coverage accounting y marca
`backtest_core_row_candidate`. v0.1 no une fundamentals, news, short, halts ni
regime context.
```

### 6. `master_intraday_bar_table`

Alias arquitectonico:

```text
master_intraday_table
```

Nombre preferido:

```text
master_intraday_bar_table
```

Motivo: deja claro que es una tabla de barras intradia, no una tabla que mezcla
quotes, trades y todo microstructure raw.

Clase:

```text
analytical master table
```

Grain recomendado:

```text
instrument_id/ticker + ts_utc + bar_size + price_view
```

Fuentes candidatas:

```text
E:/TSIS/data/ohlcv_1m/
E:/TSIS/data/ohlcv_1m_split_normalized/
E:/TSIS/data/intraday_regime_features/
E:/TSIS/data/Halts/
market_calendar
corporate_actions_table
```

Muestra fisica raw:

```text
file: E:/TSIS/data/ohlcv_1m/ticker=ZZ/year=2013/month=01/minute_aggs_ZZ_2013_01.parquet
rows_in_file: 3631
columns: ticker, ts_utc, date, year, month, o, h, l, c, v, vw, n, t

ticker  ts_utc                date        o     h     l
ZZ      2013-01-02T14:30:00Z  2013-01-02  2.19  2.19  2.1799
ZZ      2013-01-02T14:32:00Z  2013-01-02  2.18  2.19  2.1800
```

Muestra fisica split-normalized:

```text
file: E:/TSIS/data/ohlcv_1m_split_normalized/ticker=SAVA/year=2023/month=12/minute_aggs_SAVA_2023_12_split_normalized.parquet
rows_in_file: 7760
columns: ticker, ts_utc, date, year, month, o, h, l, c, v, vw, n, t,
future_split_factor, o_split_normalized, h_split_normalized,
l_split_normalized, c_split_normalized, vw_split_normalized,
materialized_price_view, source_1m_file, source_splits_file
```

Uso en evento:

- detecta PM volume, first push, HOD, LOD, VWAP reclaim, pullback y event_end;
- sirve para outcomes intradia;
- permite materializar event windows sin escanear todo raw.

No debe contener:

- todos los quotes;
- todos los trades;
- fields de fundamentals;
- labels que solo se conocen despues de la ventana.

### 7. `microstructure_features_table`

Clase:

```text
execution/microstructure table
```

Grain recomendado:

```text
instrument_id/ticker + ts_utc or event_window_id + feature_window
```

Fuentes candidatas:

```text
E:/TSIS/data/quotes/
E:/TSIS/data/trades_ticks_prod_2005_2026/
inspection_dossiers/quotes/
inspection_dossiers/trades/
data_consumption_policies/quotes_consumption_policy.md
data_consumption_policies/trades_consumption_policy.md
```

Muestra fisica quotes:

```text
file: E:/TSIS/data/quotes/ZYXI/year=2025/month=12/day=03/quotes.parquet
rows_in_file: 5940
columns: ask_exchange, ask_price, ask_size, bid_exchange, bid_price, bid_size,
conditions, indicators, participant_timestamp, sequence_number, timestamp,
tape, trf_timestamp, year, month, day

ask_exchange  ask_price  ask_size  bid_exchange  bid_price  bid_size  conditions
20            0.0        0         20            0.0        0         [1]
8             1.4        100       0             0.0        0         [2]
```

Muestra fisica trades:

```text
file: E:/TSIS/data/trades_ticks_prod_2005_2026/ZYXI/year=2025/month=12/day=2025-12-01/market.parquet
rows_in_file: 18182
columns: ticker, date, timestamp, price, size, exchange, conditions, year,
month, day

ticker  date        timestamp                   price  size   exchange  conditions
ZYXI    2025-12-01  2025-12-01 14:30:00.772845  1.21   29595  12        [17, 9, 41]
ZYXI    2025-12-01  2025-12-01 14:30:00.772855  1.21   29595  12        [16]
```

Uso en evento:

- calcula spread, quoted liquidity, tape intensity, print size distribution,
  outside-range flags, odd-lot texture y execution feasibility;
- se consulta por ventana de evento, no como join permanente full-history;
- alimenta Execution Models y filtros de realismo.

No debe contener:

- todo quotes/trades bruto duplicado;
- price adjustment economico;
- targets de outcome.

### 8. `fundamentals_asof_table`

Clase:

```text
reference/context table
```

Grain recomendado:

```text
instrument_id/ticker + as_of_date + statement_period + source
```

Fuentes candidatas:

```text
E:/TSIS/data/financial/
E:/TSIS/data/additional/
E:/TSIS/data/reference/overview/
```

Muestra fisica:

```text
file: E:/TSIS/data/financial/ratios/ticker=A/ratios_A.parquet
rows_in_file: 1
columns: ticker, cik, date, price, average_volume, market_cap,
earnings_per_share, price_to_earnings, price_to_book, price_to_sales,
debt_to_equity, enterprise_value

ticker  cik         date        price   average_volume  market_cap
A       0001090872  2026-03-06  115.07  2424738.0       32519050000.0
```

Uso en evento:

- aporta market cap, float, dilution risk y financial context cuando hay
  `filing_date` o `as_of_date` defendible;
- permite filtrar smallcaps sin lookahead;
- alimenta Pattern Discovery y ML despues de pasar leakage checks.

No debe contener:

- datos conocidos despues del evento como si fueran presentes;
- period_end tratado como availability date;
- causalidad por defecto.

### 9. `news_context_table`

Clase:

```text
reference/context table
```

Grain recomendado:

```text
article_id + published_utc + ticker/requested_ticker
```

Fuentes candidatas:

```text
E:/TSIS/data/additional/news/
C:/TSIS_Data/data/additional/news/
```

Uso en evento:

- aporta `news_flag`, catalyst timing y contexto narrativo;
- permite distinguir evento tecnico sin noticia de evento con catalyst;
- debe preservar `published_utc` y ambiguedad multi-ticker.

No debe contener:

- prueba de causalidad por si sola;
- articulo posterior al evento como feature pre-event.

### 10. `short_context_table`

Clase:

```text
reference/context table
```

Grain recomendado:

```text
ticker/instrument_id + settlement_date/date + source
```

Fuentes candidatas:

```text
E:/TSIS/data/short/
E:/TSIS/data/short_review/
C:/TSIS_Data/data/short/
```

Muestra fisica:

```text
file: E:/TSIS/data/short/short_interest/AACT.parquet
rows_in_file: 54
columns: settlement_date, ticker, short_interest, avg_daily_volume,
days_to_cover

settlement_date  ticker  short_interest  avg_daily_volume  days_to_cover
2023-06-15       AACT    101578          255782            1.0
2023-06-30       AACT    1572            190387            1.0
```

Uso en evento:

- contexto de crowding y squeeze risk;
- no tiene granularidad intradia fina;
- debe consumirse con lag/availability explicitos.

No debe contener:

- tape;
- borrow real-time si no existe fuente;
- causalidad intradia no demostrada.

### 11. `real_time_corporate_event_alerts_table`

Clase:

```text
reference/event table + live alert stream
```

Grain recomendado:

```text
alert_id + source + received_utc + ticker/instrument_id + event_type
```

Motivo:

Las capturas revisadas muestran una clase de dato que hoy no queda cubierta por
las tablas objetivo: alertas en tiempo real de eventos corporativos que pueden
mover precio en segundos.

Ejemplo observado en captura:

```text
source: PR Newswire
headline: IceCure Announces Pricing of $5.5 Million Private Placement...
published/display time: Jun 17 13:14 EDT
ticker: ICCM
event family: offering/private placement/warrants
```

Otro panel observado muestra alertas mezcladas de:

```text
PRN  = PR Newswire
GLB  = GlobeNewswire
SEC  = SEC filing
forms/events: 8-K, 6-K, 424B3, offerings, warrants, reverse split
```

Fuentes actuales en TSIS:

```text
E:/TSIS/data/additional/news/
```

Estado de cobertura actual:

```text
historical/contextual news exists
real-time low-latency alert feed does not exist as governed Data Foundation output
offering-specific alert stream does not exist
SEC filing stream does not exist as live operational feed
```

Muestra fisica actual de `additional/news`:

```text
file: E:/TSIS/data/additional/news/news/ticker=AACT/news_AACT.parquet
rows_in_file: 3
columns: id, title, author, published_utc, article_url, tickers, image_url,
description, keywords, insights, ticker, publisher.name, _dataset,
_ingested_utc

publisher.name examples: Benzinga, MarketWatch
published_utc example: 2025-09-24T20:05:00Z
```

Interpretacion:

```text
additional/news puede servir para research historico y contexto narrativo.
No prueba que TSIS tenga un feed de alertas sub-segundo o de pocos segundos.
No debe tratarse como sustituto de un sistema live de offerings/filings.
```

Campos minimos:

```text
alert_id
event_id_vendor
source
source_channel
ticker
instrument_id
cik
headline
event_type
event_subtype
form_type
published_utc
accepted_utc
received_utc
first_seen_utc
latency_ms_from_source_if_available
url
raw_text
parsed_terms
offering_amount
offering_price
warrant_flag
warrant_terms
discount_or_premium_to_last_close
shares_or_units
underwriter_or_placement_agent
is_amendment
is_correction
confidence
severity
trading_action_hint
raw_payload_path
source_terms
```

Event types iniciales:

```text
offering_pricing
registered_direct
private_placement
atm_offering
shelf_registration
424B_filing
S1_or_S3_registration
F1_or_F3_registration
8K_material_event
6K_foreign_issuer_event
warrant_issuance
reverse_split
delisting_notice
going_concern
clinical_regulatory_update
merger_spac_business_combination
halt_related_news
```

Uso en evento:

- veto o degradacion inmediata de long momentum cuando aparece offering
  dilutivo;
- explicacion causal de collapses intradia;
- generacion de `corporate_event_risk_state` para Event Engine, Strategy
  Research, Execution Models y live trading;
- separacion entre evento tecnico de mercado y evento informacional externo;
- labeling historico de reacciones post-offering.

No debe contener:

- precio como fuente primaria;
- decision automatica de trading sin risk policy;
- inferencias no trazables de LLM sin raw text y confidence;
- noticias historicas sin timestamp de publicacion/recepcion.

Fuentes para conseguirlo en tiempo real:

1. SEC EDGAR APIs / SEC submissions stream.

   Fuente oficial:

   ```text
   https://www.sec.gov/search-filings/edgar-application-programming-interfaces
   ```

   Uso:

   - polling de `data.sec.gov/submissions/CIK##########.json`;
   - forms relevantes: `8-K`, `6-K`, `424B3`, `424B5`, `S-1`, `S-3`,
     `F-1`, `F-3`, `POS AM`, `FWP`;
   - SEC indica que submissions API se actualiza en real time as filings are
     disseminated, con typical processing delay menor a un segundo para
     submissions, aunque puede ser mayor en picos.

   Limitacion:

   - EDGAR llega cuando se presenta el filing;
   - muchas offerings impactantes salen primero por PR Newswire/GlobeNewswire
     y el filing puede llegar despues;
   - por tanto SEC solo no basta para alerta de segundos.

2. Newswire / financial news vendor low-latency.

   Fuentes candidatas:

   ```text
   PR Newswire / Cision
   GlobeNewswire
   Business Wire
   Benzinga Pro / Benzinga news feed
   Dow Jones / FactSet / Refinitiv / MT Newswires / similares institucionales
   ```

   Uso:

   - capturar headlines como las de las capturas;
   - filtrar keywords: `offering`, `registered direct`, `private placement`,
     `warrants`, `ATM`, `priced`, `securities purchase agreement`,
     `gross proceeds`, `shelf`, `424B`;
   - normalizar ticker, source, timestamp y raw text.

   Limitacion:

   - feeds verdaderamente low-latency suelen ser de pago;
   - hay que medir latencia real `published_utc -> received_utc`;
   - no basta con APIs historicas actualizadas por lotes.

3. DAS Trader / NewsWare investigation note.

   Fuentes publicas revisadas:

   ```text
   https://dastrader.com/
   https://dastrader.com/das-api-services/
   https://newsware.com/
   https://newsware.com/newswatch/
   ```

   Lectura tecnica:

   - DAS anuncia servicios de real-time market data y real-time streaming news
     from Newsware dentro de su servicio Market Data Vendor.
   - NewsWare anuncia delivery en tiempo real directamente desde publishers,
     alertas por portfolio/eventos y NewsWare API para entregar noticias de
     cientos de fuentes en un formato.
   - La pagina publica de DAS API no confirma que el API de DAS Trader Pro
     exponga el stream de noticias de NewsWare.
   - La pagina publica de DAS API indica que el uso requiere certificacion, que
     sus documentos/source code estan protegidos, que FIX API es order entry
     only y que sus API services no estan disenados para redistribucion de
     market data o aplicaciones comerciales.

   Decision institucional:

   ```text
   DAS/NewsWare = candidate live alert source.
   DAS Trader Pro API public docs = not enough evidence for governed ingestion.
   NewsWare API direct feed = preferred route to evaluate for TSIS ingestion.
   ```

   Regla:

   ```text
   No asumir que DAS Trader Pro API entrega offerings/news en tiempo real hasta
   obtener documentacion certificada de DAS o contrato directo con NewsWare.
   ```

4. Polygon/Massive News API como historical/context feed.

   Fuente:

   ```text
   https://polygon.io/docs/rest/stocks/news
   ```

   Uso:

   - research historico;
   - contexto narrativo;
   - backfill de news.

   Limitacion:

   - la documentacion muestra endpoint de noticias con metadata, tickers,
     publisher, sentiment y `published_utc`;
   - en los planes visibles la recencia se muestra como `Updated hourly`;
   - no debe asumirse apto para alertas de segundos.

Arquitectura live recomendada:

```text
SEC EDGAR poller
Newswire/vendor websocket or polling feed
  -> raw_alert_log append-only
  -> event classifier deterministic + LLM optional with audit
  -> real_time_corporate_event_alerts_table
  -> live risk/event bus
  -> historical replay dataset
```

Regla institucional:

```text
Para backtest puede bastar `published_utc`.
Para live trading hace falta tambien `received_utc` y medicion de latencia.
Sin `received_utc`, no se puede simular honestamente una alerta en segundos.
```

### 12. `halts_table`

Clase:

```text
reference/event table
```

Grain recomendado:

```text
ticker/instrument_id + halt_start + source
```

Fuentes candidatas:

```text
E:/TSIS/data/Halts/processed/halts_master_multisource.parquet
D:/Halts/processed/halts_master_multisource.parquet
```

Muestra fisica:

```text
file: E:/TSIS/data/Halts/processed/halts_master_multisource.parquet
rows_in_file: 133116
columns: source, source_priority, ticker, issuer_name, listing_exchange,
halt_date, halt_start_et, resume_quote_et, resume_trade_et, halt_code,
halt_type, raw_reason, release_no, item_link, url_source, is_sec_suspension

source  source_priority  ticker  issuer_name                          halt_date
sec     1                <NA>    Garcis U.S.A., Inc.                  1995-10-13
sec     1                <NA>    Environmental Chemicals Group, Inc.   1995-12-12
```

Uso en evento:

- interrumpe event windows;
- ajusta outcome horizons;
- alimenta execution risk y continuation/failure research.

No debe contener:

- OHLCV;
- inferencias de estrategia;
- timestamps inventados cuando solo existe fecha.

### 12. `regime_context_table`

Clase:

```text
reference/context table
```

Grain recomendado:

```text
date or timestamp + regime_source + market_proxy
```

Fuentes candidatas:

```text
E:/TSIS/data/regime_indicators/
E:/TSIS/data/intraday_regime_features/
E:/TSIS/data/additional/economic/
```

Muestra fisica regime:

```text
file: E:/TSIS/data/regime_indicators/indices/I_COMP/day.parquet
rows_in_file: 705
columns: open, close, high, low, datetime, date

open         close        high         low          datetime
11905.1231   12070.5929   12071.2871   11876.8166  1970-01-01 00:27:56.440800
11896.3086   11855.8341   12040.3359   11853.3602  1970-01-01 00:27:56.527200
```

Nota:

```text
La muestra de regime_indicators muestra datetime/date sospechosos 1970-01-01.
No debe consumirse como tabla institucional sin auditoria y validator.
```

Muestra fisica macro:

```text
file: E:/TSIS/data/additional/economic/inflation.parquet
rows_in_file: 950
columns: date, cpi, cpi_year_over_year, cpi_core, pce, pce_core,
pce_spending, _dataset, _ingested_utc

date        cpi    cpi_year_over_year  _dataset
1947-01-01  21.48  NaN                 inflation
1947-02-01  21.62  NaN                 inflation
```

Uso en evento:

- marca contexto de mercado: risk-on/risk-off, volatility, index trend,
  liquidity regime;
- permite Pattern Discovery y ML condicionado por regimen.

No debe contener:

- ticker-level causality por defecto;
- fechas erroneas sin correction contract;
- labels forward-looking.

### 13. `dataset_certification_matrix`

Clase:

```text
certification/quality table
```

Grain recomendado:

```text
dataset_family + scope + ticker/date optional + quality_version
```

Materializacion v0.1:

```text
dataset_family + family_level + dataset_certification_matrix_policy_v0_1
```

Fuentes candidatas:

```text
01_foundations/data_quality_report/
01_foundations/inspection_dossiers/
01_foundations/dataset_registry/
01_foundations/data_consumption_policies/
01_foundations/validators/
01_foundations/FOUNDATIONS_FAMILY_COMPLETION_STANDARD.md
01_foundations/DATA_AUDIT_QUALITY_STANDARD.md
```

Uso en evento:

- decide si cada input del evento es `good`, `review`, `bad`,
  `recoverable_with_flag` o `quarantine`;
- permite excluir casos del backtest core sin borrar evidencia;
- permite ML con flags de calidad cuando aplique.

No debe contener:

- precios;
- book/tape;
- fundamentales;
- estrategia.

Estado materializado inicial:

```text
dataset_id: dataset_certification_matrix_v0_1
path: E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix/dataset_certification_matrix_v0_1.parquet
rows: 13
family_count: 13
human_inspector_ready_count: 13
visual_casepack_complete_count: 13
blocked_from_backtest_core_count: 2
scoped_only_count: 5
data_quality_verdict_counts:
  blocked_by_data_defect: 2
  complete_scoped: 5
  usable_for_declared_scope: 6
build_run_id: dataset_certification_matrix_v0_1_20260622T154116Z
output_sha256: e7803e3ec58cfb92c1313efc09bdd3a015800c4680437e4567a0174b257f1fb0
source_family_status_matrix_sha256: c380c7a5f85c14925410899b264de4e52c62571a1b1ff7b359cec733f16f5d35
hard_fail_count: 0
test_evidence: C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_five_tables_v0_1/
```

Lectura institucional:

```text
dataset_certification_matrix_v0_1 existe como gate familiar de calidad y
evidencia. Convierte `family_status_matrix_v0_1.md` en tabla gobernada y
verifica que cada familia tenga root fisico, report, dossier, schema,
contract, registry, policy, validator y evidencia visual. No valida filas de
mercado y no repara familias bloqueadas.
```

### 14. `data_quality_report`

Clase:

```text
forensic evidence / human inspection package
```

No es una tabla de mercado.

Contenido esperado:

```text
family_status_matrix
visual inspection dossiers
good/review/bad case packs
schema validation results
missing data analysis
outlier analysis
format analysis
coverage analysis
known limitations
promotion status
links to evidence assets
```

Fuentes candidatas:

```text
01_foundations/data_quality_report/
01_foundations/inspection_dossiers/
01_foundations/validators/
01_foundations/contract_registry/
01_foundations/canonical_schemas/
```

Uso en evento:

- no se une al evento como feature;
- se consulta para saber si las fuentes que alimentan ese evento son
  defendibles;
- sirve para auditor humano e institucional promotion gates.

No debe contener:

- informacion completa del mercado;
- una copia de raw parquet;
- decisiones operativas de estrategia.

## Mapa De Dependencias Por Evento

```text
instrument_master
  -> valida identidad y universo

market_calendar
  -> valida sesion y ventanas

corporate_actions_table
  -> define price views y evita falsos gaps

master_daily_table
  -> contexto diario pre-evento y dia del evento

master_intraday_bar_table
  -> evolucion intradia y deteccion del evento

microstructure_features_table
  -> solo si hace falta realismo de ejecucion o diagnostico tape/book

halts_table
  -> interrumpe o clasifica el evento

real_time_corporate_event_alerts_table
  -> captura catalysts corporativos publicados en segundos/minutos

fundamentals/news/short/regime context
  -> explica contexto con as-of semantics

dataset_certification_matrix + data_quality_report
  -> decide si el caso se puede usar y bajo que restricciones

Event Engine
  -> escribe event_table downstream
```

## Root Comun De Outputs CAPA 1

Los outputs gobernados por este contrato deben vivir bajo:

```text
E:/TSIS/data/data_foundation_outputs/
```

Layout objetivo:

```text
E:/TSIS/data/data_foundation_outputs/instrument_master/
E:/TSIS/data/data_foundation_outputs/market_calendar/
E:/TSIS/data/data_foundation_outputs/corporate_actions_table/
E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix/
E:/TSIS/data/data_foundation_outputs/master_daily_table/
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/
E:/TSIS/data/data_foundation_outputs/microstructure_features_table/
E:/TSIS/data/data_foundation_outputs/real_time_corporate_event_alerts_table/
E:/TSIS/data/data_foundation_outputs/halts_table/
E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/
E:/TSIS/data/data_foundation_outputs/news_context_table/
E:/TSIS/data/data_foundation_outputs/short_context_table/
E:/TSIS/data/data_foundation_outputs/regime_context_table/
E:/TSIS/data/data_foundation_outputs/data_quality_report/
```

Regla:

```text
Estas tablas no deben materializarse como carpetas sueltas al mismo nivel que
raw/source folders (`reference`, `ohlcv_daily`, `quotes`, `trades`, etc.).
```

Excepcion live-ingestion:

```text
raw_alert_log append-only no es una tabla limpia de CAPA 1. Debe vivir separado:

E:/TSIS/data/live_ingestion/raw_alert_log/
```

## Politica De Tamano Y Optimizacion

Data actual observada por el humano:

```text
raw/audited data actual ~= 1 TB
```

El objetivo no es duplicar ese terabyte.

### Escenarios

```text
Malo: copiar raw completo en master tables
  incremento esperado: +1.0 TB a +2.0 TB

Institucional recomendado: core compacto + sidecars + lineage
  incremento esperado: +150 GB a +450 GB

Muy eficiente: materializacion por ventanas/eventos + sidecars bajo demanda
  incremento esperado: +80 GB a +250 GB
```

### Target

```text
target recomendado CAPA 1 materializada adicional: +150 GB a +450 GB
limite de alerta: >700 GB
mala senal: acercarse a +1 TB salvo justificacion explicita
```

### Reglas Para No Perder Informacion

1. No borrar raw/audited sources.
2. No copiar quotes/trades completos en master tables.
3. Guardar lineage hacia source files, dataset version y run_id.
4. Materializar microstructure por ventanas o agregados.
5. Mantener sidecars especializados.
6. Usar Parquet + ZSTD + tipos estrictos.
7. Particionar por `date/year/month/ticker` segun patron de consumo.
8. Separar features de labels.
9. Separar signal, execution, valuation y benchmark price views.
10. Mantener `data_quality_report` como evidencia, no como base de datos.

## Politica De Materializacion

Formato recomendado:

```text
parquet
compression = zstd
dictionary_encoding = true para categoricas
```

Tipos recomendados:

```text
ticker/instrument_id: dictionary/string controlado
date: date32
timestamp: timestamp[us/ns, UTC declarado]
flags: bool/int8
categorias: dictionary
price: float32 o decimal segun precision requerida por policy
volume/size: int64
quality_state: dictionary
```

Particionado recomendado:

```text
master_daily_table/year=YYYY/
master_intraday_bar_table/year=YYYY/month=MM/
microstructure_features_table/year=YYYY/month=MM/date=YYYY-MM-DD/
dataset_certification_matrix/family=.../version=.../
```

No usar una particion que produzca millones de ficheros minusculos sin plan de
compaction.

## Campos Minimos Transversales

Toda tabla materializada de CAPA 1 debe incluir o poder enlazar:

```text
dataset_version
source_dataset
source_root
build_run_id
quality_policy_version
schema_version
price_view si aplica
as_of_semantics si aplica
created_at/build_timestamp
```

## Reglas De Consumo Downstream

### Event Engine

Consume:

```text
instrument_master
market_calendar
corporate_actions_table
master_daily_table
master_intraday_bar_table
real_time_corporate_event_alerts_table
halts_table
dataset_certification_matrix
```

Consulta bajo demanda:

```text
microstructure_features_table
news_context_table
short_context_table
regime_context_table
fundamentals_asof_table
```

### Outcome Research

Consume:

```text
event_table
master_daily_table
master_intraday_bar_table
corporate_actions_table
halts_table
```

Regla:

```text
outcome no debe usar informacion posterior como feature pre-evento.
```

### Strategy Research

Consume:

```text
event_table
outcome_table
master_intraday_bar_table
microstructure_features_table
real_time_corporate_event_alerts_table
halts_table
execution constraints
```

Regla:

```text
senal puede vivir en adjusted/split-normalized; ejecucion debe mirar raw
quotes/trades o features derivadas de raw.
```

### ML / Offline RL

Consume:

```text
features as-of
labels/outcomes separados
quality flags
instrument identity
regime context
execution feasibility
```

Regla:

```text
labels no pueden mezclarse con features.
```

## Promotion Barrier

Ningun output de este documento queda materializado o institucional solo por
estar descrito aqui.

Para pasar a `validated` o `institutional`, cada output necesita:

```text
canonical schema
dataset registry entry
data consumption policy
validator
profiling fisico
quality report
manifest/run_id
changelog
Graphify refresh queue si altera el mapa semantico
```

## Work Order Recomendado

1. `instrument_master`
2. `corporate_actions_table`
3. `market_calendar` + `expected_data_calendar`
4. `dataset_certification_matrix`
5. `master_daily_table`
6. `master_intraday_bar_table`
7. `microstructure_features_table`
8. `real_time_corporate_event_alerts_table`
9. `halts_table`
10. `fundamentals_asof_table`
11. `news_context_table`
12. `short_context_table`
13. `regime_context_table`

Motivo:

```text
primero identidad, calendario, actions y calidad;
despues precio diario/intradia;
despues microestructura, alertas corporativas live y contexto;
despues consumo por eventos, outcomes, strategy, ML/RL.
```

## Regla Final

Estas tablas existen para que un evento tenga un estado defendible.

No existen para duplicar toda la historia.
No existen para esconder informacion.
No existen para mezclar eventos, estrategias y outcomes.

La arquitectura correcta es:

```text
raw/audited truth
  -> governed compact outputs
  -> event-state reconstruction
  -> event_table downstream
  -> outcome/strategy/ML/execution/RL
```

Si un futuro agente no puede explicar que hace una tabla cuando aparece un
evento concreto, esa tabla todavia no esta suficientemente bien definida.
