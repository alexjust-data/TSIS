# Estudio de arquitectura realtime para 200 tickers small y microcaps

[Escenario 50](./02_1_estudio_arquitectura_realtime_50_tickers.md) | [Escenario 200](./02_2_estudio_arquitectura_realtime_200_tickers.md) | [Escenario 500](./02_3_estudio_arquitectura_realtime_500_tickers.md)

[Objetivo](#objetivo) | [Supuestos](#supuestos) | [Arquitectura](#arquitectura) | [Presupuesto](#presupuesto) | [Latencia](#latencia) | [Riesgos](#riesgos) | [Fuentes](#fuentes)

## Objetivo

Disenar una plataforma realtime de ingenieria intermedia, orientada a `200` tickers small y microcaps `< 200M`, en la que el camino de decision algoritmica sea estable bajo rafagas de apertura y momentum, manteniendo una relacion agresiva de coste frente a latencia.

En esta escala ya no conviene mezclar ingestion, analitica y serving web en el mismo proceso. La separacion minima correcta es por nodos.

## Supuestos

- Universo simultaneo: `200` tickers.
- Feed consumido: `trades + quotes + per-second aggregates`.
- Modelo de carga de ingenieria:
  - `14.5 eventos/s` medios por ticker.
  - `2,900 eventos/s` medios agregados.
  - `23,200 eventos/s` en rafagas `p95` usando factor `8x`.
- Huella de almacenamiento mensual:
  - Raw: `398.2 GB/mes`
  - Columnar comprimido: `92.9 GB/mes`

La reduccion de eventos medios por ticker respecto al escenario de `50` no asume menos actividad intrinseca del mercado, sino una mezcla de nombres mas heterogenea. La cola alta sigue siendo severa: unas pocas microcaps activas concentran la mayor parte del burst budget.

## Arquitectura

**Topologia recomendada**

- `2` nodos en `US East`
- `1` object storage
- `1` frontend estatico detras de CDN

**Nodo A: ejecucion**

- `Universe Service`
- `Polygon Gateway`
- `Feature Engine`
- `Inference Engine`
- `Strategy Engine`
- `Risk Engine`
- `Broker Adapters`

**Nodo B: datos y serving**

- `ClickHouse`
- API interna para web
- jobs de compactacion, snapshots y retraining prep
- paneles operativos y auditoria

**Plano caliente**

1. Ingestion con una sola conexion WebSocket primaria.
2. Cola local ligera entre parser y feature engine.
3. Estado por ticker enteramente en RAM.
4. Snapshot del estado util para web cada `250-500 ms`.
5. Persistencia asincrona a `ClickHouse` por micro-batches temporales.

**Plano frio**

- Exportacion a parquet en `B2` o `R2`.
- Retencion dual:
  - tick y quote derivados de corto plazo en `ClickHouse`
  - parquet historico de mayor horizonte en object storage

**Decision de ingenieria**

Aqui sigue sin compensar `Kafka` salvo que el equipo necesite fan-out multiusuario o replays muy extensos. Si empieza a compensar separar el serving web de la ejecucion para evitar jitter de CPU, presion de memoria y lock contention en rafagas.

## Presupuesto

**Configuracion recomendada**

- Nodo A ejecucion: `DigitalOcean 2 vCPU / 4 GiB` a `24 USD/mes`
- Nodo B datos: `DigitalOcean 4 vCPU / 8 GiB` a `48 USD/mes`
- Historico analitico:
  - `Backblaze B2` a `0.006 USD/GB-mes`
  - Coste estimado sobre `92.9 GB/mes`: `0.56 USD/mes`
- Alternativa R2:
  - `0.015 USD/GB-mes`
  - Coste estimado: `1.39 USD/mes`

**Presupuesto mensual de infraestructura**

| Componente | Coste estimado |
| --- | ---: |
| Nodo A ejecucion | `24.00 USD` |
| Nodo B datos | `48.00 USD` |
| B2 historico comprimido | `0.56 USD` |
| R2 opcional | `1.39 USD` |
| Total infra minimo razonable | `72.56-73.95 USD` |

**Presupuesto mensual incluyendo datos de mercado para uso comercial**

- Infra-only: `~73-74 USD/mes`
- Infra + `Polygon Stocks Business`: `~2,072 USD/mes`
- Infra + business + expansion Nasdaq o full market: `~4,071 USD/mes`

La conclusion economica es la misma que en el escenario pequeno: el coste estructural dominante sera el entitlement de datos si el sistema soporta negocio o visualizacion publica.

## Latencia

**Presupuesto de latencia interno**

| Etapa | Objetivo p99 |
| --- | ---: |
| Parseo y normalizacion | `<2.0 ms` |
| Features y ventanas | `<3.0 ms` |
| Inferencia CPU | `<3.0 ms` |
| Risk + order intent | `<1.5 ms` |
| Hand-off a adaptador de broker | `<1.0 ms` |

Objetivo interno extremo a extremo: `<10.5 ms p99`, excluyendo broker y exchange.

**Recomendacion de ejecucion**

- Si el objetivo es robustez operativa y desarrollo agil: `IB` o `TradeStation`.
- Si el objetivo es minimizar la cola de salida y endurecer latencia operativa: `DAS`.

En esta escala todavia es posible operar con inferencia en CPU y sin GPU. La inferencia debe estar pre-cargada y evitar asignaciones dinamicas por tick.

## Riesgos

**Riesgo de arquitectura**

- El acoplamiento de web y ejecucion en un mismo nodo ya es tecnicamente incorrecto.
- Persistir cada evento sincronamente destruye el presupuesto de latencia.
- Un universo de `200` nombres requiere control de backpressure y dropless parsing.

**Riesgo de calidad de senal**

- Market cap estatico diario no es suficiente para entradas intradia en microcaps.
- Debe existir reconciliacion entre `reference data`, ultimo precio y estado de halts.

**Recomendacion final**

Para `200` tickers, la mejor relacion `calidad / latencia / precio` es:

- `2` nodos en `US East`
- ejecucion aislada de datos y web
- `ClickHouse` en nodo propio
- object storage barato para parquet
- broker adapter desacoplado del engine de senales

## Fuentes

- DigitalOcean pricing: https://www.digitalocean.com/pricing/droplets
- Backblaze B2 pricing: https://www.backblaze.com/cloud-storage/pricing
- Cloudflare R2 pricing: https://developers.cloudflare.com/r2/pricing/
- Polygon business pricing: https://polygon.io/business/
- Polygon market data terms: https://polygon.io/legal/market-data-terms-of-service
- Polygon WebSocket rates: https://polygon.io/knowledge-base/article/how-much-data-is-streamed-through-polygons-websockets
- Polygon WebSocket latency: https://polygon.io/knowledge-base/article/what-is-the-average-latency-for-polygons-websockets
- Polygon WebSocket subscriptions: https://polygon.io/knowledge-base/article/how-many-tickers-can-you-subscribe-to-on-a-single-polygon-websocket-connection
- Polygon WebSocket connections: https://polygon.io/knowledge-base/article/how-many-polygon-websocket-connections-can-i-use-at-one-time
- IBKR TWS API docs: https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/
- TradeStation API docs: https://api.tradestation.com/docs/
- DAS Trader API services: https://dastrader.com/das-api-services/
