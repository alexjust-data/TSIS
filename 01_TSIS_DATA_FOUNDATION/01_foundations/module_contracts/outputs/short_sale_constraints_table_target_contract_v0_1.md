# Short Sale Constraints Table Target Contract v0.1

## Estado

Tipo: target contract.

Modulo: `01_TSIS_DATA_FOUNDATION`.

Ambito: `CAPA 1 - DATA FOUNDATION`.

Status: `target_defined_not_materialized`.

Este contrato define la tabla objetivo para:

```text
SSR
borrow
locate
short availability
hard-to-borrow / easy-to-borrow state
borrow fee / rebate when available
```

No materializa datos.
No declara que TSIS tenga hoy estas fuentes.
No modifica `short_context_table_v0_1`.

Runbook de adquisicion/preparacion:

```text
01_foundations/module_contracts/outputs/short_sale_constraints_data_acquisition_runbook_v0_1.md
```

## Decision Central

`short_context_table` y `short_sale_constraints_table` son tablas distintas.

```text
short_context_table
  = short interest + short volume + FINRA/local provenance

short_sale_constraints_table
  = can this be shorted, when, under what regulatory/broker constraint,
    with what source, account/broker scope and timestamp?
```

Regla:

```text
short interest / short volume no prueban borrow, locate, SSR ni shortability.
```

Regla historica:

```text
20 years of market data
!=
20 years of broker-specific borrow inventory
```

TSIS puede tener historico amplio de precios, volumen, quotes, trades y short
context. Eso no equivale a tener historico point-in-time de shares available to
short, locate approval, borrow fee o HTB/ETB por broker/cuenta.

Por tanto ningun agente puede inferir:

- borrow availability;
- locate approval;
- hard-to-borrow state;
- borrow fee;
- SSR active state;
- o short execution eligibility;

desde `short_context_table_v0_1` salvo que exista un contrato derivado
separado y validado.

## Por Que Existe Esta Tabla

TSIS no puede hacer backtesting institucional de estrategias short ni simulacion
realista de ejecucion short si no sabe:

- si SSR estaba activo;
- si la orden short debia ejecutarse por encima del National Best Bid;
- si existian acciones disponibles para short;
- si se requeria locate;
- si el locate fue aprobado;
- cuanto costaba el borrow;
- que broker/vendor observo esa disponibilidad;
- y a que hora exacta estaba disponible esa informacion.

Sin esta tabla, un backtest short puede asumir fills imposibles.

## Componentes

La tabla tiene dos familias semanticas.

### 1. SSR Regulatory State

Describe restricciones regulatorias tipo Short Sale Restriction / Alternative
Uptick Rule.

Campos objetivo:

```text
constraint_family = ssr
ticker
instrument_id
trading_date
venue_or_listing_market
trigger_source
trigger_method
prior_regular_close
trigger_price_threshold
trigger_timestamp_utc
ssr_active_start_utc
ssr_active_end_utc
ssr_active_regular_session
ssr_active_premarket
ssr_active_afterhours
restriction_rule_id
restriction_description
derived_from_prices
confirmed_by_official_or_vendor_feed
quality_state
```

SSR historico puede tener dos niveles:

```text
official_or_vendor_confirmed
derived_regulatory_proxy
```

`derived_regulatory_proxy` solo es aceptable si el contrato declara:

- fuente de prior close;
- fuente intradia usada para detectar el 10% trigger;
- timezone/session;
- price view;
- limitaciones por ausencia de lista oficial;
- y validacion de casos muestrales contra fuente externa.

### 2. Borrow / Locate / Availability State

Describe disponibilidad real o reportada para poder shortear.

Campos objetivo:

```text
constraint_family = borrow_availability
ticker
instrument_id
as_of_utc
broker_or_vendor
account_scope
source_channel
shares_available_to_short
easy_to_borrow_flag
hard_to_borrow_flag
locate_required
locate_requested
locate_approved
locate_approved_shares
locate_request_id
borrow_fee_rate
rebate_rate
fee_currency
min_quantity
max_quantity
availability_status
raw_status_text
received_utc
ingested_utc
latency_ms
source_event_id
quality_state
```

Esta familia es broker/vendor-specific.

Regla:

```text
borrow availability at broker A/account X/time T
!=
borrow availability at broker B/account Y/time T
```

No puede promoverse como verdad universal del mercado.

## Fuentes Candidatas

### SSR

Fuentes candidatas:

```text
official exchange / listing-market short-sale restriction files
SEC / Regulation SHO rule reference
vendor market data SSR feeds
derived proxy from validated daily + intraday prices
broker/order-route reject logs
```

Fuentes regulatorias de referencia:

```text
SEC Regulation SHO / Rule 201:
https://www.sec.gov/rules/final/2010/34-61595.pdf

17 CFR 242.201 reference:
https://www.ecfr.gov/current/title-17/chapter-II/part-242/section-242.201
```

### Borrow / Locate / Availability

Fuentes candidatas:

```text
broker API or broker export
DAS/SageTrader-compatible broker records if available through the broker/API
Interactive Brokers / CenterPoint / TradeZero / Cobra / other broker borrow feeds
vendor securities-lending data
internal OMS/order logs for locate requests and approvals
execution reject logs
```

Fuentes regulatorias de referencia:

```text
Regulation SHO locate requirement reference:
https://www.ecfr.gov/current/title-17/chapter-II/part-242/section-242.203
```

## Fuentes Que No Bastan

Estas fuentes no bastan para construir esta tabla:

```text
E:/TSIS/data/short/
E:/TSIS/data/short_review/
short_context_table_v0_1
FINRA short volume
FINRA short interest
daily OHLCV alone
1m OHLCV alone
quotes/trades alone for borrow
```

Explicacion:

- `short_interest` mide posicion short reportada con lag;
- `short_volume` mide flujo reportado/agregado, no disponibilidad para short;
- OHLCV puede ayudar a derivar SSR proxy, pero no prueba borrow;
- quotes/trades no muestran inventario prestable ni locate approval.

## Grain Objetivo

La tabla puede materializarse como un dataset particionado con dos familias:

```text
constraint_family=ssr/
constraint_family=borrow_availability/
```

Grain SSR:

```text
source_system + ticker/instrument_id + trading_date + venue_or_listing_market
```

Grain borrow/locate:

```text
source_system + broker_or_vendor + account_scope + ticker/instrument_id +
as_of_utc + source_event_id
```

## Uso En Un Evento

Para un evento:

```text
ticker = ABCD
event_time = 2021-05-14 13:45:00 UTC
```

El consumidor debe preguntar:

```text
1. SSR:
   was SSR active at event_time?
   if yes, what rule and source?
   can a short order execute at/below NBB?

2. Borrow:
   did the relevant broker/account report shares available before event_time?
   was locate required?
   was locate approved?
   how many shares?
   what fee/rebate?
   how stale is the observation?
```

Uso permitido cuando este materializada:

- short strategy feasibility;
- execution simulation;
- short-entry filters;
- failed-short / no-locate labels;
- short squeeze state;
- risk controls;
- live trading pre-checks;
- ML/RL state component only after legal as-of and OOD gates.

Uso prohibido:

- usarlo como alpha por si solo;
- asumir borrow universal;
- usar availability de un broker para otro;
- usar availability posterior al evento;
- entrenar RL directo sin action/reward/execution simulator;
- deducir locate desde short volume/interest.

## Relacion Con Otras Tablas

```text
short_context_table
  -> crowding / short pressure context

short_sale_constraints_table
  -> execution feasibility and short-sale restrictions

microstructure_features_table
  -> book/tape liquidity and execution texture

event_windows_table
  -> legal event cutoffs and feature/outcome boundaries

market_calendar
  -> sessions, next trading day and early closes

master_daily_table / master_intraday_bar_table
  -> possible SSR derived proxy inputs
```

## Promotion Barrier

La tabla no puede materializarse como output gobernado hasta que exista al
menos uno de estos caminos:

### Camino A - SSR Proxy Historico

Requisitos:

- fuente diaria validada para prior close;
- fuente intradia validada para detectar trigger;
- calendario oficial;
- regla SSR versionada;
- casos muestrales comparados contra fuente oficial/vendor;
- campo `confirmed_by_official_or_vendor_feed=false` si no hay lista externa.

### Camino B - SSR Oficial/Vendor

Requisitos:

- feed/lista oficial o vendor con timestamps;
- lineage del proveedor;
- timezone;
- fecha de descarga/ingesta;
- hash de raw;
- comparacion contra proxy derivado.

### Camino C - Borrow/Locate Broker/Vendor

Requisitos:

- contrato de proveedor/broker;
- `received_utc`;
- `broker_or_vendor`;
- `account_scope`;
- raw log append-only;
- mapping de ticker/instrument;
- schema de locate request/approval/reject;
- politica de staleness;
- evidencia de replay o muestras forenses.

### Camino D - DAS / SageTrader Live Capture

Requisitos:

- documentacion oficial, entitlement activo o muestra raw capturada;
- raw payload append-only;
- `received_utc`;
- `broker_or_vendor`;
- `account_scope`;
- preservacion de `raw_status_text`;
- parser versionado;
- politica de staleness;
- mapping a `instrument_master`;
- evidencia de que la API/plataforma expone shortable, availability, locate,
  borrow fee o reject logs antes de poblar esos campos.

Regla:

```text
DAS/SageTrader captura hacia adelante desde el primer dia operativo.
No reconstruye historico pasado salvo que el broker/vendor entregue backfill
historico con semantica point-in-time.
```

## Estado Actual

```text
materialized = false
known_physical_source_under_E:/TSIS/data = false
short_context_table_replacement = false
backtest_short_execution_ready = false
live_trading_ready = false
```

Raices observadas actualmente bajo `E:/TSIS/data`:

```text
short
short_review
```

No existe en este momento una raiz gobernada equivalente a:

```text
E:/TSIS/data/ssr/
E:/TSIS/data/borrow/
E:/TSIS/data/locates/
E:/TSIS/data/short_availability/
```

## Tabla Objetivo

Root objetivo cuando se materialice:

```text
E:/TSIS/data/data_foundation_outputs/short_sale_constraints_table/
```

Dataset objetivo:

```text
short_sale_constraints_table_v0_1
```

Status esperado inicial:

```text
target_defined_not_materialized
```

## Regla Final

Hasta que esta tabla exista:

```text
TSIS puede estudiar short pressure.
TSIS no puede afirmar short execution feasibility institucional.
```
