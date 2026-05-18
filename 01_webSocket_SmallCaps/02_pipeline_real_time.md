pipeline de trading en tiempo real con dos caminos separados:

- Camino caliente: market data -> features -> señales -> risk checks -> orden al broker
- Camino frío: market data/eventos -> almacenamiento histórico -> entrenamiento ML -> research/backtests

Si tu objetivo es small/microcaps < $200M, con ejecución vía IB, DAS o TradeStation, la conclusión
importante es esta:

La menor latencia real no te la da la nube barata.
La latencia final la dominan:

- el feed que uses
- la cercanía de tu servidor al broker/router
- el broker/API
- el exchange route

Si ejecutas por IB, tu cuello de botella suele ser IB/TWS Gateway, no ClickHouse ni S3.
Si ejecutas por DAS/FIX, puedes bajar mucho más la latencia porque DAS anuncia infraestructura co-locada y
validación sub-milisegundo hacia venues US; pero eso ya es otro nivel operativo/comercial.
Fuentes: https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/ , https://dastrader.com/ ,
https://dastrader.com/das-api-services/ , https://api.tradestation.com/docs/ ,
https://api.tradestation.com/docs/fundamentals/http-streaming/

Arquitectura recomendada

1. Universe service
    - Calcula y actualiza la lista de tickers < $200M
    - Usa market cap dinámico: shares_outstanding * last_price
    - Rebalancea suscripciones del stream
2. Market data gateway
    - Una conexión estable a Polygon WebSocket
    - Se suscribe solo a tu universo
    - Normaliza trades, quotes y aggregates
    - Publica eventos internamente
3. Feature engine
    - Calcula en RAM features de 1s, 5s, 1m
    - VWAP, relative volume, breakout state, spread, imbalance, halt/resume, etc.
    - Aquí debe estar tu inferencia ML online
4. Strategy engine
    - Consume features
    - Evalúa reglas/ML
    - Genera intención de orden, no manda órdenes directas
5. Risk/Execution engine
    - Límites por símbolo, pérdida diaria, tamaño, spread, slippage
    - Traduce señales a órdenes concretas
    - Adaptadores separados para IB, DAS, TradeStation
6. Hot store
    - Para web y dashboards
    - Guarda estado actual, últimas barras, señales, posiciones, órdenes
    - Aquí priorizas latencia de lectura
7. Cold store / research store
    - Parquet en object storage
    - Histórico para backtest, retraining y auditoría
8. Observability
    - Logs de señales
    - Event sourcing mínimo
    - Métricas: lag del feed, tiempo señal->orden, rechazos, fills, drop rate

Qué base de datos usar

- Tiempo real / web: Redis o memoria local para estado vivo
- Series temporales / analytics: ClickHouse
- Histórico barato: Backblaze B2 o Cloudflare R2

Para tu caso, ClickHouse + Parquet + cache en memoria suele dar mejor relación calidad/latencia/precio que
montar Postgres/Timescale como núcleo.

Infraestructura que te conviene
Hay 3 niveles razonables:

Nivel 1: barato y suficiente para empezar

- 1 VM en EE. UU. Este
- DigitalOcean 4GB/2vCPU $24/mes o 8GB/4vCPU $48/mes
- ClickHouse en la misma VM
- B2 para histórico
- Cloudflare para frontend/API cache
Fuente: https://www.digitalocean.com/pricing/droplets , https://www.backblaze.com/cloud-storage/pricing ,
https://developers.cloudflare.com/r2/pricing/

Esto sirve si:

- universo pequeño/medio
- inferencia ligera CPU
- ejecución retail/semi-pro
- aceptas que no es HFT

Nivel 2: mejor equilibrio real

- 2 VMs en la misma región US East/NJ
- VM A: ingest + strategy + execution
- VM B: ClickHouse + APIs internas + web backend
- Object storage aparte para histórico

Esta es la opción que yo elegiría para ti.
Te da aislamiento: si la base o la web sufren, no te rompe ejecución.

Nivel 3: baja latencia seria

- servidor/VPS cerca de Nueva York/Nueva Jersey
- proceso de ejecución separado
- DAS/FIX o infraestructura broker más directa
- hot path casi todo en RAM
- DB solo asíncrona

Esto ya es para priorizar latencia por encima de simplicidad. Si usas IB, muchas mejoras de este nivel se
diluyen por la propia arquitectura de IB.

Mi recomendación concreta
Si tu prioridad es precio + buena calidad + latencia razonable:

- Región: EE. UU. Este
- Diseño: 2 nodos
- Nodo 1:
    - Polygon consumer
    - feature engine
    - ML inference
    - strategy engine
    - broker adapter
- Nodo 2:
    - ClickHouse
    - API web
    - dashboards
    - jobs batch
- Storage:
    - Backblaze B2 para parquet/raw
- Cache:
    - memoria local al inicio; Redis solo si de verdad lo necesitas

No haría esto al principio

- Kubernetes
- serverless para el hot path
- Redis serverless por evento
- GPUs permanentes
- una sola base de datos intentando servir realtime + training + web + auditoría

Broker por latencia

- DAS: mejor si tu prioridad es ejecución rápida y routing directo
- IB: mejor si quieres facilidad, cobertura y coste operativo menor, pero no es la opción de menor latencia
- TradeStation: intermedio, con API decente, pero no lo pondría por delante de DAS si tu obsesión es
ejecución rápida
Fuentes: https://dastrader.com/ , https://dastrader.com/das-api-services/ ,
https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/ , https://api.tradestation.com/docs/

Mi resumen corto:

- Barato y sólido: DigitalOcean + ClickHouse + B2 + Cloudflare + IB/DAS adapter
- Mejor equilibrio para ti: 2 VMs en US East, no una sola
- Si la latencia manda de verdad: DAS/infra cerca de NY/NJ, no arquitectura cloud genérica

Si quieres, el siguiente paso útil es que te dibuje una arquitectura exacta por procesos, con:

- servicios
- colas o sin colas
- qué corre en cada VM
- y coste mensual estimado para 50, 200 y 500 tickers.