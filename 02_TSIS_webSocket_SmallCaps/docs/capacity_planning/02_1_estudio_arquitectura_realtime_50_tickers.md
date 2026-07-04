# Estudio de arquitectura realtime para 50 tickers small y microcaps

[Escenario 50](./02_1_estudio_arquitectura_realtime_50_tickers.md) | [Escenario 200](./02_2_estudio_arquitectura_realtime_200_tickers.md) | [Escenario 500](./02_3_estudio_arquitectura_realtime_500_tickers.md)

[Objetivo](#objetivo) | [Supuestos](#supuestos) | [Arquitectura](#arquitectura) | [Presupuesto](#presupuesto) | [Latencia](#latencia) | [Riesgos](#riesgos) | [Fuentes](#fuentes)

## Objetivo

Disenar una infraestructura de baja latencia y coste contenido para consumir `Polygon WebSocket`, filtrar un universo dinamico de small y microcaps con `market_cap < 200M`, calcular features e inferencia ML en tiempo real, exponer datos a una web interna o privada y ejecutar ordenes via `IB`, `DAS` o `TradeStation`.

El principio de diseno es estricto: la base de datos no debe estar en el camino critico de ejecucion. El camino caliente debe vivir en memoria y escribir de forma asincrona al almacenamiento analitico.

## Supuestos

- Universo simultaneo: `50` tickers.
- Mercado: acciones US small y microcaps, con concentracion de actividad en aperturas, halts, resumptions y rompimientos de premarket.
- Feed consumido: `trades + quotes + per-second aggregates`.
- Modelo de carga de ingenieria:
  - `18 eventos/s` medios por ticker durante sesion regular.
  - `900 eventos/s` medios agregados.
  - `7,200 eventos/s` en rafagas `p95` usando factor de burst `8x`.
- Formula de almacenamiento mensual para sesion regular:
  - `storage_GB = eventos/s * bytes_por_evento * 6.5h * 3600 * 21d / 1024^3`
- Huella por evento:
  - `300 B` si se conserva el evento normalizado en formato tipo JSON/raw.
  - `70 B` efectivos en columna comprimida para historico analitico.

Resultado del modelo:

- Raw mensual estimado: `123.6 GB/mes`
- Columnar comprimido estimado: `28.8 GB/mes`

Estas cifras son estimaciones de ingenieria, no promesas del proveedor. Polygon publica para el universo completo US equities promedios cercanos a `~2,000 msg/s` en trades y `~8,000 msg/s` en quotes, con latencia media `<20 ms`; el escenario aqui modelado es un subconjunto suscrito por ticker y por tanto muy inferior al universo completo. Polygon tambien indica que no limita el numero de tickers suscritos si el cliente puede consumir el flujo lo bastante rapido.

## Arquitectura

**Topologia recomendada**

- `1` nodo de ejecucion y datos en `US East`
- `1` object storage para historico
- `1` frontend estatico detras de CDN

**Plano caliente**

1. `Universe Service`
   - Actualiza el universo elegible cada `30-60 s`.
   - Construye la suscripcion WebSocket a partir de una lista local de simbolos, nunca con `*`.
   - Usa `shares_outstanding * last_price` como market cap dinamico operativo.
2. `Market Data Gateway`
   - Una unica conexion WebSocket a Polygon.
   - Normaliza `T`, `Q` y `A/AM`.
   - Publica a una cola in-process o bus local de muy baja sobrecarga.
3. `Feature Engine`
   - Estado en memoria por ticker.
   - Ventanas deslizantes `1 s`, `5 s`, `15 s`, `1 m`.
   - Features recomendadas: spread, microprice, NBBO imbalance, relative volume, volatility burst, halt state, breakout distance, price velocity, trade-to-quote ratio.
4. `Inference + Strategy Engine`
   - Infiere en CPU.
   - Produce `signal intents`, nunca ordenes finales.
5. `Risk + Execution Adapter`
   - Enforcea hard limits por simbolo, notional, spread maximo, reject cooldown, halt prohibition y slippage.
   - Adaptadores dedicados para `IB`, `DAS` o `TradeStation`.

**Plano frio**

- `ClickHouse` local para consultas analiticas y serving de la web.
- `Backblaze B2` o `Cloudflare R2` para parquet y snapshots.
- Exportacion asincrona por lotes cada `1-5 s` o cada `N` eventos.

**Decision de ingenieria**

Para `50` tickers no conviene introducir `Kafka`, `Redis Cluster`, `Kubernetes` ni bases gestionadas. El coste operacional sube mas que la mejora real de latencia. Un unico nodo bien afinado es suficiente si el proceso de ejecucion queda aislado por prioridad de CPU y memoria.

## Presupuesto

**Configuracion recomendada**

- Computo principal: `DigitalOcean Basic Droplet 2 vCPU / 4 GiB` a `24 USD/mes`
- Historico analitico:
  - `Backblaze B2`: `0.006 USD/GB-mes`
  - Coste estimado sobre `28.8 GB/mes`: `0.17 USD/mes`
- Alternativa para datos web y objetos de baja salida:
  - `Cloudflare R2 Standard`: `0.015 USD/GB-mes`
  - Coste estimado sobre `28.8 GB/mes`: `0.43 USD/mes`

**Presupuesto mensual de infraestructura**

| Componente | Coste estimado |
| --- | ---: |
| VM principal | `24.00 USD` |
| B2 historico comprimido | `0.17 USD` |
| R2 opcional para serving de objetos | `0.43 USD` |
| Total infra minimo razonable | `24.17-24.60 USD` |

**Presupuesto mensual incluyendo datos de mercado para uso comercial**

Si el sistema va a alimentar una web, una aplicacion de terceros o un negocio, el coste dominante no es la nube sino el licenciamiento de mercado:

- `Polygon Stocks Business`: `1,999 USD/mes`
- `Polygon Full Market` expansion: `1,999 USD/mes`
- `Polygon Nasdaq Basic` expansion: `1,999 USD/mes`

Por tanto:

- Infra-only: `~24-25 USD/mes`
- Infra + `Polygon Stocks Business`: `~2,023 USD/mes`
- Infra + business + expansion real-time de mercado completo o Nasdaq: `~4,022 USD/mes`

Si el uso es estrictamente personal y no hay redistribucion, la lectura juridica cambia, pero para web y producto distribuido no debe asumirse esa excepcion.

## Latencia

**Presupuesto de latencia interno**

| Etapa | Objetivo p99 |
| --- | ---: |
| Parseo y normalizacion WebSocket | `<1.5 ms` |
| Actualizacion de estado y features | `<2.0 ms` |
| Inferencia ML en CPU | `<2.0 ms` |
| Risk checks + generacion de orden | `<1.0 ms` |
| Persistencia asincrona | fuera de camino critico |

Objetivo de software extremo a extremo, excluyendo broker y exchange: `<7 ms p99`.

**Observacion critica**

Para esta escala, el cuello de botella real sera el broker:

- `IB`: comodo y ampliamente documentado, pero no es el camino de menor latencia.
- `TradeStation`: usable para automatizacion, con coste operativo moderado.
- `DAS`: mejor candidato si la prioridad es ejecucion mas directa y menor latencia operativa.

## Riesgos

**Riesgo de diseno**

- Es un error usar la base de datos como bus de mensajeria del camino caliente.
- Es un error guardar cada quote cruda si luego la estrategia consume agregados y estado derivado.
- Es un error exponer el feed directamente a la web. La web debe leer una vista reducida, no el stream bruto.

**Riesgo regulatorio y contractual**

- La redistribucion publica o uso comercial del market data requiere revisar licencias y terminos.
- El presupuesto de mercado puede superar en dos ordenes de magnitud al presupuesto cloud.

**Recomendacion final**

Para `50` tickers, la mejor relacion `calidad / latencia / precio` es:

- `1` VM en `US East`
- hot path completamente en memoria
- `ClickHouse` local como almacen analitico
- `B2` para parquet
- web desacoplada del feed bruto

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
