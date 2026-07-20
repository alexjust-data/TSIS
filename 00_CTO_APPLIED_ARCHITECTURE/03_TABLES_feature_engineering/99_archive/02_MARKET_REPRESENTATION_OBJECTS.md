# Representacion Del Mercado - Atributos Por Familia Y Tabla

Status: `consolidated_family_attribute_index_v0_1`  
Date: `2026-07-16`

Este documento consolida las familias de representacion de mercado y los  
atributos/variables ya identificados en las lecturas de tabla `000` a `012`.  
No sustituye los contratos, schemas ni manifests.  
Su funcion es responder rapidamente:  

```text
- Que familia representa cada variable?
- En que tabla debe vivir?
- Que queda cubierto?
- Que falta por construir en 013-018?
```

**Representacion Del Mercado**

```text
Familias de Objetos de Información

|-- Precio
|-- Tendencia
|-- Volatilidad
|-- Liquidez
|-- Participacion
|-- Microestructura
|-- Temporalidad
|-- Contexto diario
|-- Contexto intradia
|-- Noticias
|-- Fundamentales
|-- Regimen
|-- Eventos
|-- Estructura
```

## Familias de `Objetos de información`

<!-- TOC_START -->
- [Precio](#precio)
  - [004 master_daily_table](#004-master_daily_table)
  - [008 outcomes_table](#008-outcomes_table)
- [Tendencia](#tendencia)
- [Volatilidad](#volatilidad)
  - [004 master_daily_table](#004-master_daily_table-1)
- [Liquidez](#liquidez)
  - [004 master_daily_table](#004-master_daily_table-2)
  - [008 outcomes_table](#008-outcomes_table-1)
- [Participacion](#participacion)
  - [004 master_daily_table](#004-master_daily_table-3)
  - [011 short_context_table](#011-short_context_table)
- [Microestructura](#microestructura)
- [Temporalidad](#temporalidad)
  - [000 instrument_master](#000-instrument_master)
  - [001 market_calendar](#001-market_calendar)
  - [002 expected_data_calendar](#002-expected_data_calendar)
  - [006 halts_table](#006-halts_table)
  - [007 event_windows_table](#007-event_windows_table)
  - [009 fundamentals_asof_table](#009-fundamentals_asof_table)
  - [011 short_context_table](#011-short_context_table-1)
  - [012 regime_context_table](#012-regime_context_table)
- [Contexto Diario](#contexto-diario)
  - [004 master_daily_table](#004-master_daily_table-4)
  - [005 corporate_actions_table](#005-corporate_actions_table)
  - [006 halts_table](#006-halts_table-1)
- [Contexto Intradia](#contexto-intradia)
- [Noticias](#noticias)
  - [010 news_context_table](#010-news_context_table)
- [Fundamentales](#fundamentales)
  - [009 fundamentals_asof_table](#009-fundamentals_asof_table-1)
- [Regimen](#regimen)
  - [012 regime_context_table](#012-regime_context_table-1)
- [Eventos](#eventos)
  - [005 corporate_actions_table](#005-corporate_actions_table-1)
  - [006 halts_table](#006-halts_table-2)
  - [007 event_windows_table](#007-event_windows_table-1)
  - [010 news_context_table](#010-news_context_table-1)
- [Estructura](#estructura)
  - [000 instrument_master](#000-instrument_master-1)
  - [001 market_calendar](#001-market_calendar-1)
  - [002 expected_data_calendar](#002-expected_data_calendar-1)
  - [003 dataset_certification_matrix](#003-dataset_certification_matrix)
  - [005 corporate_actions_table](#005-corporate_actions_table-2)
  - [006 halts_table](#006-halts_table-3)
  - [007 event_windows_table](#007-event_windows_table-2)
- [Lectura Final](#lectura-final)
<!-- TOC_END -->

---


### `Precio`

Las siguiente tablas materializadas en este proyecto contienen las variables 

**Esquema** : [004_master_daily_table.md](../../00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/004_master_daily_table/004_master_daily_table.md)  
**Path** : 
[master_daily_table_v0_1](E:\TSIS\data\data_foundation_outputs\master_daily_table\master_daily_table_v0_1)

contenido/schema de la tabla real


#### 004 master_daily_table

Variables que lo componene

```text
daily open,
high,
low,
close,
prior_close,
gap_percent,
daily_range.
```

Uso:

```text
Contexto diario para Market State,
Event State,
scanners,
backtests,
ML/RL.
```

### 008 outcomes_table

```text
future_return,
MFE,
MAE,
break_flag,
failure_flag.
```

Uso:

```text
Solo labels/outcomes.
No debe alimentar Market State ni Event State observable.
```

Pendiente:

```text
013/014 deben aportar precio intradia quote-guarded y barras intradia.
016/017 consumiran agregaciones legales en t.
```

---

## Tendencia

Cubierto actualmente en `000-012`:

```text
No hay tabla 000-012 cuya responsabilidad primaria sea tendencia intradia.
```

Pendiente:

```text
014 master_intraday_bar_table:
return_1m,
return_5m,
return_15m,
slope,
rolling_close_change,
consecutive_up_down_minutes.

016 market_state_table:
tendencia agregada legal en t.

017 event_state_table:
tendencia relativa al evento.
```

---

## Volatilidad

### 004 master_daily_table

```text
daily_range,
range_pct,
true_range_proxy,
volatility_bucket.
```

Uso:

```text
Contexto diario de riesgo para Market State,
Event State,
risk controls,
ML/RL.
```

Pendiente:

```text
014/015 deben aportar volatilidad intradia y microestructural.
016/017 deben consumir volatilidad legal en t.
```

---

## Liquidez

### 004 master_daily_table

```text
daily_volume,
dollar_volume,
relative_daily_volume,
liquidity_bucket.
```

Uso:

```text
Scanners,
Market State,
Event State,
execution research,
backtests.
```

### 008 outcomes_table

```text
future_spread,
future_liquidity,
price_impact,
response_latency.
```

Uso:

```text
Evaluacion futura,
execution research,
backtests,
RL como reward/label si hay contrato.
```

Pendiente:

```text
014/015 deben aportar liquidez intradia,
spread proxy,
quote/trade availability,
tradability gates.
```

---

## Participacion

### 004 master_daily_table

```text
daily_volume,
dollar_volume,
relative_daily_volume,
liquidity_bucket.
```

### 011 short_context_table

```text
short_interest,
short_volume,
short_ratio,
days_to_cover,
source_family,
source_scope.
```

Uso:

```text
Market State,
Event State,
clustering,
ML,
IRL,
RL,
AlphaEvolve,
siempre con politica de lag/as-of.
```

Pendiente:

```text
014/015 deben aportar participacion intradia:
relative_volume,
volume_zscore,
volume_acceleration,
trade_count_proxy.
```

---

## Microestructura

Cubierto actualmente en `000-012`:

```text
No cubierta como microestructura real.
```

Motivo:

```text
Las tablas 000-012 no representan interaccion fina trade/quote,
spread,
depth,
order flow,
microprice
u OFI.
```

Pendiente:

```text
013 ohlcv_1m_quote_guarded:
base intradia quote-guarded.

015 microstructure_features_table:
spread,
quote_count,
quote_guarded_repair_applied,
signed_flow,
OFI,
microprice,
imbalance,
depth_proxy.
```

---

## Temporalidad

### 000 instrument_master

```text
valid_from,
valid_to.
```

### 001 market_calendar

```text
session_date,
open_utc,
close_utc,
open_et,
close_et,
session_minutes,
is_early_close,
calendar,
timezone,
year,
month,
dow.
```

### 002 expected_data_calendar

```text
instrument_id,
ticker,
session_date,
valid_from,
month.
```

### 006 halts_table

```text
halt_start,
resume_time,
halt_duration,
session_date.
```

### 007 event_windows_table

```text
window_start,
window_end,
window_role,
event_timestamp.
```

### 009 fundamentals_asof_table

```text
filing_date,
as_of_date,
availability_flag,
metric_staleness.
```

### 011 short_context_table

```text
observation_date_type,
observation_date,
settlement_date,
trade_date,
as_of_date,
as_of_semantics.
```

### 012 regime_context_table

```text
trading_date,
session_open_utc,
as_of_utc,
as_of_date,
as_of_semantics,
source_granularity.
```

Uso:

```text
Legalidad temporal para Market State,
Event State,
backtests,
ML,
IRL,
RL,
AlphaEvolve.
```

---

## Contexto Diario

### 004 master_daily_table

```text
daily open,
high,
low,
close,
prior_close,
gap_percent,
daily_range,
daily_volume.
```

### 005 corporate_actions_table

```text
action_type,
action_date,
action_year,
source_system,
source_priority.
```

### 006 halts_table

```text
halt_event_id,
halt_date,
halt_start_et,
resume_time,
halt_reason.
```

Uso:

```text
Market State,
Event State,
scanners,
backtests.
```

Pendiente:

```text
016 debe decidir que contexto diario entra al estado observable en t.
```

---

## Contexto Intradia

Cubierto actualmente en `000-012`:

```text
No cubierto como tabla primaria.
```

Pendiente:

```text
014 master_intraday_bar_table:
session_hod,
session_lod,
distance_to_session_hod,
distance_to_session_lod,
intraday_vwap_distance,
rolling_activity_state.

017 event_state_table:
pre_event_context,
at_event_context,
post_event_context si aplica solo para review/outcomes.
```

---

## Noticias

### 010 news_context_table

```text
news_context_id,
article_id,
news_timestamp,
article_url_hash,
title_hash,
source_type,
topic_or_category.
```

Uso:

```text
Market State,
Event State,
clustering,
ML,
IRL,
RL,
AlphaEvolve,
siempre con timestamp legality.
```

---

## Fundamentales

### 009 fundamentals_asof_table

```text
as_of_date,
filing_date,
period_end,
fiscal_year,
fiscal_quarter,
timeframe,
CIK,
fundamental_metric,
staleness.
```

Uso:

```text
Market State,
Event State,
clustering,
ML,
IRL,
RL,
AlphaEvolve,
solo con point-in-time/as-of enforcement.
```

---

## Regimen

### 012 regime_context_table

```text
regime_symbol,
regime_proxy_role,
index_return,
volatility_proxy,
risk_on_off_state,
regime_quality,
trading_date,
session_open_utc,
as_of_utc,
as_of_semantics.
```

Uso:

```text
Market State,
Event State,
clustering,
backtests,
ML,
IRL,
RL,
AlphaEvolve.
```

---

## Eventos

### 005 corporate_actions_table

```text
action_type,
action_date,
source_event_id.
```

### 006 halts_table

```text
halt_event_id,
source_event_key,
halt_date,
halt_start_et,
resume_time,
halt_reason.
```

### 007 event_windows_table

```text
event_window_id,
source_event_id,
event_family,
event_type,
event_code,
event_source,
window_start,
window_end,
window_role,
event_timestamp.
```

### 010 news_context_table

```text
article_id,
event_source,
published_at/as_of,
ticker/instrument_id.
```

Uso:

```text
Event State,
outcomes,
research experiments,
backtests,
ML/IRL/RL cuando exista separacion X/y.
```

---

## Estructura

### 000 instrument_master

```text
instrument_id,
ticker,
identity_resolution_level,
ticker_identity_scope,
market,
primary_exchange,
ticker_type,
valid_from,
valid_to.
```

### 001 market_calendar

```text
calendar,
timezone,
year,
month,
dow.
```

### 002 expected_data_calendar

```text
expected_dataset_id,
expected_source_root,
expected_session,
expected_reason,
expectation_scope.
```

### 003 dataset_certification_matrix

```text
dataset_family,
certification_scope,
physical_root,
data_quality_verdict,
production_use_gate,
event_consumption_gate.
```

### 005 corporate_actions_table

```text
corporate_action_id,
source_system,
source_priority,
is_reference_primary_source.
```

### 006 halts_table

```text
source_event_key,
duplicate_source_event_key,
source_dataset_id,
source_priority.
```

### 007 event_windows_table

```text
event_source_dataset_id,
ticker,
instrument_id,
issuer_name,
listing_exchange.
```

Uso:

```text
Todos los consumidores downstream,
governance,
validators,
builders,
audits.
```

---

## Lectura Final

```text
000-012 cubren identidad,
calendario,
expectedness,
gobernanza,
contexto diario,
corporate actions,
halts,
event windows,
outcomes,
fundamentales,
noticias,
short context
y regimen.

013-018 siguen siendo necesarios para cubrir:
precio intradia quote-guarded,
tendencia intradia,
volatilidad intradia,
liquidez intradia,
participacion intradia,
microestructura,
contexto intradia,
Market State
y Event State.
```

