# Estudio de arquitectura realtime para 500 tickers small y microcaps

[Escenario 50](./02_1_estudio_arquitectura_realtime_50_tickers.md) | [Escenario 200](./02_2_estudio_arquitectura_realtime_200_tickers.md) | [Escenario 500](./02_3_estudio_arquitectura_realtime_500_tickers.md)

[Objetivo](#objetivo) | [Supuestos](#supuestos) | [Arquitectura](#arquitectura) | [Presupuesto](#presupuesto) | [Latencia](#latencia) | [Riesgos](#riesgos) | [Fuentes](#fuentes)

## Objetivo

Disenar una arquitectura para `500` tickers small y microcaps `< 200M` en la que el sistema siga siendo de coste contenido, pero ya con aislamiento suficiente para que una carga de mercado muy concentrada no degrade el pipeline de ejecucion ni el serving analitico.

En este nivel el problema deja de ser de "script rapido" y pasa a ser de ingenieria de sistemas. La simplicidad sigue siendo valiosa, pero ya no puede lograrse concentrando todo en una sola maquina.

## Supuestos

- Universo simultaneo: `500` tickers.
- Feed consumido: `trades + quotes + per-second aggregates`.
- Modelo de carga de ingenieria:
  - `12 eventos/s` medios por ticker.
  - `6,000 eventos/s` medios agregados.
  - `60,000 eventos/s` en rafagas `p95` usando factor `10x`.
- Huella de almacenamiento mensual:
  - Raw: `823.8 GB/mes`
  - Columnar comprimido: `192.2 GB/mes`

Este escenario no equivale al universo completo US equities, pero ya entra en una zona donde las rafagas locales se parecen mas a una infraestructura multi-servicio que a un monolito. Polygon indica que la conexion unica puede consumir el universo completo si el cliente tiene capacidad suficiente, pero esa afirmacion no implica que sea una arquitectura correcta para un motor de trading con ML y serving simultaneo.

## Arquitectura

**Topologia recomendada**

- `3` nodos en `US East`
- `1` object storage
- frontend estatico y API de lectura separados del motor de ejecucion

**Nodo A: ingestion y normalizacion**

- Conexion WebSocket principal a Polygon
- Parser de eventos y normalizacion
- micro-batching hacia cola local o `NATS` ligero

**Nodo B: decision y ejecucion**

- Estado en memoria por ticker
- features
- inferencia ML
- strategy engine
- risk engine
- adaptadores a `IB`, `DAS` o `TradeStation`

**Nodo C: datos y serving**

- `ClickHouse`
- API para web y research
- exportacion a parquet
- auditoria, replay y metricas

**Decision de ingenieria**

Aqui si conviene una separacion explicita entre ingestion y ejecucion. No porque la CPU media lo exija, sino porque la cola alta de eventos y la sensibilidad del algoritmo ante jitter hacen antieconomico seguir con un unico proceso principal.

`Kafka` todavia puede evitarse si el equipo es pequeno y el replay requerido no es masivo. Un bus liviano o cola local persistente basta. El criterio no es moda arquitectonica; es minimizar latencia variable y complejidad operativa.

## Presupuesto

**Configuracion recomendada**

- Nodo A ingestion: `DigitalOcean 2 vCPU / 4 GiB` a `24 USD/mes`
- Nodo B ejecucion: `DigitalOcean 4 vCPU / 8 GiB` a `48 USD/mes`
- Nodo C datos: `DigitalOcean 8 vCPU / 16 GiB` a `96 USD/mes`
- Historico analitico:
  - `Backblaze B2` a `0.006 USD/GB-mes`
  - Coste estimado sobre `192.2 GB/mes`: `1.15 USD/mes`
- Alternativa R2:
  - `0.015 USD/GB-mes`
  - Coste estimado: `2.88 USD/mes`

**Presupuesto mensual de infraestructura**

| Componente | Coste estimado |
| --- | ---: |
| Nodo A ingestion | `24.00 USD` |
| Nodo B ejecucion | `48.00 USD` |
| Nodo C datos | `96.00 USD` |
| B2 historico comprimido | `1.15 USD` |
| R2 opcional | `2.88 USD` |
| Total infra minimo razonable | `169.15-171.03 USD` |

**Presupuesto mensual incluyendo datos de mercado para uso comercial**

- Infra-only: `~169-171 USD/mes`
- Infra + `Polygon Stocks Business`: `~2,168 USD/mes`
- Infra + business + expansion Nasdaq o full market: `~4,167 USD/mes`

La lectura economica se mantiene: el market data para negocio o redistribucion domina el presupuesto incluso en un sistema tecnicamente mas serio.

## Latencia

**Presupuesto de latencia interno**

| Etapa | Objetivo p99 |
| --- | ---: |
| Ingestion y parseo | `<2.5 ms` |
| Fan-out interno | `<1.0 ms` |
| Features y estado | `<4.0 ms` |
| Inferencia ML CPU | `<4.0 ms` |
| Risk + order hand-off | `<1.5 ms` |

Objetivo interno extremo a extremo: `<13 ms p99`, excluyendo broker y exchange.

**Criterio tecnico**

En esta escala ya no debe suponerse que "sin latencia" significa "base de datos muy rapida". La unica forma racional de acercarse a baja latencia es:

- estado operativo en memoria
- persistencia asincrona
- procesos aislados
- broker adapter separado
- observabilidad sobre lag, backlog y jitter

## Riesgos

**Riesgo de infraestimar la distribucion de actividad**

- En microcaps, la media engana. El sistema colapsa por bursts, no por medias.
- Los peores minutos no coinciden con la media diaria, sino con aperturas, halts y news catalysts.

**Riesgo de broker**

- `IB` puede ser suficiente para research-to-production inicial, pero no debe modelarse como solucion de minima latencia.
- Si la ventaja competitiva depende de velocidad de salida, `DAS` es el candidato mas coherente.

**Riesgo de coste mal identificado**

- Optimizar `30-100 USD` de cloud carece de sentido si el despliegue real requiere licencias de mercado de varios miles al mes.

**Recomendacion final**

Para `500` tickers, la mejor relacion `calidad / latencia / precio` es:

- `3` nodos en `US East`
- separacion explicita entre ingestion, ejecucion y serving
- `ClickHouse` como almacen analitico, no como bus
- object storage barato para historico
- prioridad absoluta a la disciplina del camino caliente

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
