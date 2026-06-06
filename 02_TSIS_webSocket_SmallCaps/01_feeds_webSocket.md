# WebSocket de Stocks

A fecha de 17 de marzo de 2026, en la documentación oficial de Polygon, los feeds WebSocket de stocks documentados son estos:

- Trades
https://polygon.io/docs/websocket/stocks/trades
- Quotes
https://polygon.io/docs/websocket/stocks/quotes
- Aggregates (Per Second)
https://polygon.io/docs/websocket/stocks/aggregates-per-second
- Aggregates (Per Minute)
https://polygon.io/docs/websocket/stocks/aggregates-per-minute
- Limit Up / Limit Down (LULD)
https://polygon.io/docs/websocket/stocks/luld
- NOI / Imbalances
https://polygon.io/docs/websocket/stocks/imbalances
- Fair Market Value (FMV)
https://polygon.io/docs/websocket/stocks/fair-market-value

La página Overview WS no es un feed adicional; es solo la vista general:

- https://polygon.io/docs/stocks/ws_getting-started

La propia overview enumera esos feeds: trades, quotes, aggregates por minuto, aggregates por segundo, LULD y FMV, además de NOI/
imbalances en su página específica.
Fuente: https://polygon.io/docs/stocks/ws_getting-started

Sobre “descargar absolutamente todo”:

- En streaming, eso significa suscribirte a * donde Polygon lo permite.
- En bulk histórico, lo importante son los Flat Files de stocks, que hoy veo como:
    - trades: https://polygon.io/docs/flat-files/stocks/trades
    - quotes: https://polygon.io/docs/flat-files/stocks/quotes
    - minute aggs: https://polygon.io/docs/flat-files/stocks/minute-aggregates
    - day aggs: https://polygon.io/docs/flat-files/stocks/day-aggregates
    - overview: https://polygon.io/docs/flat-files/stocks/overview

Resumen corto:

- WebSocket stocks: 7 feeds reales.
- Flat files stocks: 4 datasets bulk.
- Overview WS y Overview Flat Files no cuentan como feeds/datasets extra, son páginas índice.



---


La documentación oficial de Massive/Polygon a fecha de 17 de marzo de 2026 y la forma correcta de plantear una descarga en tiempo real es esta:

**1. Qué significa “descargar tiempo real” en Polygon/Massive**

No es una descarga tipo archivo. Es un pipeline de ingesta continua por WebSocket que:

- se conecta a un feed en vivo,
- autentica con API key,
- se suscribe a uno o varios canales,
- recibe eventos JSON en streaming,
- los normaliza,
- y los persiste localmente.

Para histórico masivo, Massive recomienda Flat Files/S3. Para tiempo real, la vía correcta es WebSocket.
Fuentes:
https://massive.com/sockets
https://massive.com/docs/websocket/quickstart
https://massive.com/knowledge-base/article/how-to-get-started-with-s3?_rsc=19iwh

**2. Cómo funciona técnicamente el WebSocket**

La mecánica oficial es:

- Endpoint delayed: wss://delayed.massive.com/stocks
- Endpoint realtime: wss://socket.massive.com/stocks

Autenticación: `{"action":"auth","params":"API_KEY"}`

Suscripción: `{"action":"subscribe","params":"AM.AAPL,T.AAPL,Q.AAPL"}`

También puedes usar * en varios feeds para todo el mercado, por ejemplo:

- AM.*
- A.*
- T.*
- Q.*

Massive documenta además que:

- los mensajes pueden llegar agrupados en arrays JSON;
- si procesas lento, el servidor puede desconectarte;
- por defecto la quickstart habla de 1 conexión concurrente por asset class;
- en pricing business aparece hasta 3 conexiones concurrentes, más una por expansión, así que esto es plan-dependent.

Fuentes:
https://massive.com/docs/websocket/quickstart
https://massive.com/blog/javascript-stock-market-data?_rsc=1ijya
https://massive.com/blog/go-stock-market-data
https://massive.com/delayed

**3. Qué feeds de stocks existen para tiempo real**

Los feeds oficiales de stocks que encontré son:

- AM = aggregates por minuto
https://massive.com/docs/websocket/stocks/aggregates-per-minute
- A = aggregates por segundo
https://massive.com/docs/websocket/stocks/aggregates-per-second
- T = trades tick a tick
https://massive.com/docs/stocks/ws_stocks_t
- Q = NBBO quotes
https://massive.com/docs/stocks/ws_stocks_q
- LULD = limit up / limit down
https://massive.com/docs/websocket/stocks/overview?assetClass=stocks&license=personal&name=stocks_starter
https://www.massive.com/changelog
- NOI / Imbalances = net order imbalance de NYSE
https://massive.com/docs/websocket/stocks/imbalances
https://www.massive.com/changelog
- FMV = fair market value
https://massive.com/docs/websocket/stocks/fair-market-value

Notas importantes:

- NOI no es un feed general de todo el mercado; el changelog dice que cubre NYSE-listed tickers.
- LULD está en planes selectos.
- FMV es un feed premium/business.

**4. Qué feed conviene usar según el prototipo**

Para un primer notebook:

- Si quieres algo ligero y útil: usa AM.
- Si quieres más detalle sin morir de volumen: usa A.
- Si quieres tape real: usa T.
- Si quieres libro top-of-book/NBBO: usa Q, pero es mucho más pesado.
- Si quieres eventos regulatorios: añade LULD.
- Si quieres auctions/open-close pressure: añade NOI.

Recomendación pragmática:

- primer notebook: AM + T para 5-20 tickers
- segunda fase: añadir Q
- tercera fase: añadir LULD y NOI
- FMV solo si tu plan lo incluye y realmente lo necesitas

**5. Campos y semántica importantes**

De la documentación oficial:

Trades (T) trae, entre otros:

- sym, p, s, x, c, t, q, z, trfi, trft

Quotes (Q) trae:

- sym, bx, bp, bs, ax, ap, as, c, i, t, q, z

Aggregates (A / AM) traen:

- sym, v, av, op, vw, o, c, h, l, a, z, s, e, otc

Dos detalles críticos:

- Massive dice que los sequence numbers son crecientes y únicos por ticker, pero no siempre contiguos.
- En diciembre de 2025 Massive anunció un cambio: los tamaños de quotes (bid_size, ask_size) pasan a reportarse en shares, mientras que parte de la documentación todavía describe round lots. Hay que programar con esa discrepancia en mente.

Fuentes:

https://massive.com/docs/stocks/ws_stocks_t  
https://massive.com/docs/stocks/ws_stocks_q  
https://massive.com/docs/websocket/stocks/aggregates-per-minute  
https://massive.com/docs/websocket/stocks/aggregates-per-second  
https://www.massive.com/changelog  

**6. Horarios y timestamps**

Massive documenta para stocks:

- premarket: 4:00 AM - 9:30 AM ET
- regular: 9:30 AM - 4:00 PM ET
- after-hours: 4:00 PM - 8:00 PM ET

Los timestamps vienen como Unix timestamps; en stocks overview dejan claro que debes tratarlos como UTC y convertir explícitamente a ET cuando quieras alinearlos a sesión/fecha de mercado.

Fuente:

https://massive.com/docs/stocks/getting-started  
https://massive.com/docs/websocket/stocks/overview?assetClass=stocks&license=personal&name=stocks_starter  

**7. Cómo debe construirse el prototipo en Jupyter**

Para notebook, la forma correcta no es “poner un while y hacer prints”. Debe tener esta arquitectura:

1. Ingesta
    - cliente oficial Python o websocket raw
    - suscripción limitada al principio
    - recepción de arrays de mensajes
2. Normalización
    - separar por ev
    - convertir timestamps
    - añadir received_at
    - guardar raw_json
3. Persistencia
    - append-only
    - ideal: Parquet particionado por date/feed/ticker
    - alternativa simple: DuckDB
4. Control de flujo
    - cola en memoria
    - parser rápido
    - escritura asíncrona o por batches
5. Recuperación
    - reconexión automática
    - resuscripción
    - backfill por REST si hay huecos
6. Observabilidad
    - contador por feed
    - lag de procesamiento
    - desconexiones
    - últimos timestamps por ticker

Esto está alineado con el tutorial oficial sobre patrón non-blocking en Python: no mezclar procesamiento pesado o REST síncrono dentro del handler del WebSocket.

Fuente:
https://massive.com/blog/pattern-for-non-blocking-websocket-and-rest-calls-in-python

**8. Qué no debes hacer**

Estas son las decisiones que te rompen un prototipo de tiempo real casi desde el principio:

- No empieces con Q.* para todo el mercado en un notebook.
Motivo: el caudal de NBBO quotes es muy alto y te va a saturar CPU, memoria, disco o parsing antes de validar la arquitectura.
- No hagas REST síncrono dentro del callback del stream.
Motivo: bloqueas el consumo del socket y aumentas mucho el riesgo de lag, backlog o desconexión.
- No asumas que 1 mensaje = 1 evento.
Motivo: Massive puede enviar arrays JSON con varios eventos en un mismo frame.
- No asumas continuidad perfecta de q o del orden absoluto entre todos los eventos.
Motivo: los sequence numbers sirven, pero no debes modelar el sistema como si fueran globalmente contiguos y perfectos.
- No mezcles delayed y realtime sin etiquetarlo explícitamente.
Motivo: luego no sabrás qué datos son aptos para validación operativa real y cuáles eran solo pruebas de conectividad.
- No uses solo memoria.
Motivo: si el proceso cae, pierdes datos y no puedes auditar huecos ni rehidratar la sesión.
- No empieces con demasiados tickers y demasiados feeds a la vez.
Motivo: si algo falla, no sabrás si el problema es red, parsing, persistencia o volumen.
- No transformes en exceso el raw stream en la primera versión.
Motivo: primero hay que preservar el evento original y luego derivar tablas limpias.

**9. Fases de construcción del prototipo**

Aquí va la parte que faltaba, ordenada como roadmap técnico.

Fase 1. Prototipo mínimo en notebook
Objetivo: validar conexión, autenticación, suscripción, parsing y persistencia básica.

Contenido:

- conectar a wss://socket.massive.com/stocks
- enviar auth
- suscribirse a un universo pequeño, por ejemplo:
    - AM.AAPL,AM.MSFT,T.AAPL,T.MSFT
- parsear cada payload por ev
- guardar cada evento raw en JSONL
- añadir captured_at
- generar un resumen básico por:
    - tipo de evento
    - ticker
    - número total de mensajes
    - número total de eventos

Resultado esperado:

- confirmar que el pipeline funciona extremo a extremo
- tener trazabilidad de lo recibido
- medir el volumen real de una sesión pequeña

Fase 2. Persistencia analítica y robustez inicial

Objetivo: pasar de “capturo cosas” a “capturo datos útiles y reutilizables”.

Contenido:

- transformar el raw a tablas normalizadas por feed:
    - trades
    - quotes
    - minute_aggs
    - second_aggs
- persistir a:
    - Parquet particionado por fecha/feed/ticker, o
    - DuckDB como capa de exploración rápida
- añadir:
    - reconexión automática
    - resuscripción automática
    - logs técnicos del proceso
- medir:
    - latencia de captura
    - tiempo de escritura
    - tamaño por feed
    - ratio de eventos por ticker

Resultado esperado:

- tener un dataset reproducible y consultable
- saber si la arquitectura aguanta varias decenas de tickers
- detectar los primeros cuellos de botella

Fase 3. Expansión funcional del stream
Objetivo: ampliar cobertura sin perder control operacional.

Contenido:

- ampliar universo de símbolos gradualmente
- añadir Q para algunos tickers, no para todo el mercado al principio
- añadir LULD si el plan lo permite
- añadir NOI si aplica a tu caso
- introducir control de calidad:
    - validación de timestamps
    - detección de gaps aparentes
    - validación de campos nulos o inesperados
- empezar a definir backfill:
    - si falta una ventana, reconstruir con REST cuando sea posible

Resultado esperado:

- un prototipo ya cercano a una ingesta seria
- cobertura de eventos más rica
- criterios claros para decidir qué feeds merecen producción

Fase 4. Migración a backend web
Objetivo: convertir la lógica del notebook en un servicio persistente.

Contenido:

- mover la lógica de conexión y captura a un proceso backend
- separar componentes:
    - stream_ingestor
    - normalizer
    - writer
    - monitoring
    - api
- exponer los datos al frontend desde tu backend:
    - vía API REST
    - o vía WebSocket interno tuyo
- el frontend no debe conectarse directo a Massive/Polygon
Motivo:
    - no expones API keys
    - controlas rate, buffering y formato
    - puedes reemitir datos ya limpios

Resultado esperado:

- arquitectura mantenible
- seguridad correcta
- posibilidad de dashboard en tiempo real sin acoplar la UI al proveedor

**10. Conclusión**

La forma correcta de organizarlo es:

1. Fase 1: AM + T, pocos tickers, raw capture, resumen básico.
2. Fase 2: persistencia seria, reconexión, métricas, tablas limpias.
3. Fase 3: añadir Q, luego LULD/NOI, ampliar universo con control.
4. Fase 4: mover todo a backend web y hacer que la UI consuma tu servicio.

La idea central es esta:

- primero validas el transporte;
- luego validas la persistencia;
- después amplías cobertura;
- y solo al final conviertes eso en producto web.

## Diseño notebook jupyter - fase :  

He dejado montado el prototipo base en realtime_polygon_prototype.ipynb y los scripts de apoyo en cell_code. Cada bloque del notebook tiene encima una explicación técnica con qué hace el script, por qué existe y qué resultado debes esperar.

La estructura que he creado es esta:

- `_ws_common.py`: utilidades compartidas, rutas, API key y construcción de suscripciones.
- `00_validate_runtime.py`: valida entorno, dependencias y clave.
- `01_prepare_capture_plan.py`: genera el plan reproducible de captura.
- `02_capture_stream.py`: abre el WebSocket, autentica, suscribe y persiste JSONL.
- `03_summarize_capture.py`: convierte la captura a tabla y la guarda en Parquet.

También verifiqué que funciona:

- El entorno está listo y detecta POLYGON_API_KEY.
- El notebook es JSON válido.
- Hice una prueba real de 5 segundos contra wss://socket.massive.com/stocks.
- La captura y el resumen se generaron correctamente en:
    - capture_meta.json
    - events.jsonl
    - events.parquet

Resultado de la smoke test:

- La autenticación y la suscripción funcionaron.
- En esa ventana solo entraron eventos status, no ticks de mercado. Eso es coherente con una ventana muy corta y el momento de ejecución; el pipeline sigue estando validado extremo a extremo.

Siguiente paso útil: ampliar el notebook con una celda de configuración editable y otra de reconexión/backfill para pasar del prototipo a una ingesta más robusta.