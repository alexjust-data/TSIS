# SERSAN Reverse Engineering: Book Evidence Matrix

Fecha de trabajo: 2026-07-23

Documento objetivo:
`C:\TSIS_Data\00_CTO\14_BACKTEST_ENGINE\01_SERSANS_SISTEMAS\SERSAN_REVERSE_ENGINEERING_EVIDENCE.md`

Biblioteca analizada:
`C:\TSIS_Data\00_CTO\99_REFERENCE_LIBRARY\BACKTEST_python`

Notas metodologicas:

- Se extrajeron 22 documentos: 19 PDF y 3 EPUB.
- Las paginas indicadas para PDF son paginas del archivo PDF extraidas por `pdftotext`.
- Los EPUB no tienen paginacion fija; se cita capitulo y se marca `pagina: n/a (EPUB)`.
- Dos PDFs tienen texto no extraible sin OCR local: `ALGO_TRADING\Algorithmic_Trading_and_DMA_-_Johnson.pdf` y `CLEAN ARCHITECTURE\_OceanofPDF.com_Clean_Architecture_-_Anderson_Rogerio.pdf`.
- No habia Tesseract/OCR Python instalado. Esos dos libros quedan como brecha de OCR, no como evidencia negativa.

## 1. Data Foundation / Historical Research

Que debe construirse:

Un subsistema historico con descarga, securities master, universo point-in-time, precios ajustados/no ajustados, corporate actions, control de delistings, calendarios, validacion de calidad y datasets reproducibles para backtesting.

Referencias:

- Stefan Jansen, `Machine_Learning_for_Algorithmic_Trading_2nd`, cap. "Getting the data right / Look-ahead bias / Survivorship bias", pp. 346-347. Explica que el backtest debe usar solo informacion disponible en ese momento y que debe rastrear el universo historico para evitar survivorship bias.
- Ernest P. Chan, `Quantitative_Trading`, cap. "Finding and Using Historical Databases", p. 61. Compara bases historicas para backtesting e identifica problemas como survivorship bias y ajustes split/dividend.
- `Successful Algorithmic Trading`, cap. "Data Accuracy Evaluation", p. 59. Enumera precios, corporate actions, holidays y errores de datos como elementos necesarios de una estructura historica fiable.
- `Successful Algorithmic Trading`, cap. "Data Quality", p. 83. Trata la limpieza de datos financieros posterior a vendor delivery como paso necesario, no accesorio.

Aplicacion a SERSAN:

El bloque no es solo "descargar data"; debe ser una fundacion reproducible con identidad de simbolos, calendario, acciones corporativas y validaciones. La salida minima deberia ser un dataset historico versionado y auditable para alimentar backtests y compararlo con live.

## 2. Market Data Runtime

Que debe construirse:

Un adaptador runtime para Massive REST/WebSocket que normalice snapshots, trades, quotes, barras y timestamps, publique eventos internos y mantenga estado de feed/subscripcion.

Referencias:

- Yves Hilpisch, `Python_for_Algorithmic_Trading`, cap. "Running a Simple Tick Data Server", p. 350. Presenta servidor tick, cliente tick, senales en tiempo real y visualizacion de streaming data como bloque operacional.
- Larry Harris, `Trading_and_Exchanges...`, cap. "Market Information Systems", p. 111. Describe que los sistemas de market data reportan trades y quotes al publico y distinguen servicios real-time vs delayed.
- `Successful Algorithmic Trading`, cap. "Why An Event-Driven Backtester?", p. 139. Justifica tratar la recepcion de market data como evento para aproximar el comportamiento live.
- Jason Strimpel, `Python_for_Algorithmic_Trading_Cookbook`, cap. "Streaming live market data / Storing live tick data", pp. 315-318. Muestra ticks como objetos, snapshot/streaming y almacenamiento local.

Aplicacion a SERSAN:

Massive debe quedar encapsulado como proveedor. Las estrategias no deberian leer Massive directamente; deberian consumir eventos normalizados y una interfaz estable que pueda cambiar entre historico, paper y live.

## 3. Premarket Universe Scanner

Que debe construirse:

Un proceso periodico que parta de un universo base, aplique filtros de tradeability, precio, volumen/liquidez, gaps/senales y clasifique simbolos como pendientes u operables con razones auditables.

Referencias:

- Stefan Jansen, `Machine_Learning_for_Algorithmic_Trading_2nd`, cap. "Built-in Quantopian factors", p. 204. Describe universos custom con filtros para limitar el backtest universe a acciones realistamente tradeables.
- Stefan Jansen, mismo libro, cap. "A single alpha factor from market data", p. 202. La Pipeline devuelve longs/shorts/ranking y usa un `screen` por dollar volume.
- Larry Harris, `Trading_and_Exchanges`, cap. "Liquidity", p. 75. Define liquidez como capacidad de operar tamanos grandes rapidamente y a bajo coste.
- Perry J. Kaufman, `A_Guide_to_Creating_a_Successful_Algorithmic_Trading_Strategy`, cap. 14 "Picking the Best Stocks (and Futures Markets) for Your Portfolio", pagina: n/a (EPUB). Trata la seleccion de instrumentos como parte explicita de la construccion de estrategia.

Aplicacion a SERSAN:

El scanner debe producir una tabla de candidatos con `symbol`, metricas, estado, tipo/razon, timestamps y snapshot usado. No basta con "buscar volumen"; hay que separar universo, filtros, ranking y registro operable.

## 4. Runtime Orchestrator

Que debe construirse:

Un componente principal que arranque, coordine, supervise y detenga scanner, feeds, estrategias, riesgo, ejecucion, persistencia y GUI. Debe tener loop/heartbeat, retry, timeout y estados de sesion.

Referencias:

- `Successful Algorithmic Trading`, cap. "Backtest", p. 161. El objeto Backtest encapsula la logica event-handling, une las clases y usa un loop event-driven con heartbeat.
- `Successful Algorithmic Trading`, cap. "Backtest", p. 162. Lista parametros como `heartbeat`, `data_handler`, `execution_handler`, `portfolio` y `strategy`.
- Robert C. Martin, `Clean_Architecture`, cap. 26 "The Main Component", pagina: n/a (EPUB). Define el componente Main como el que crea, coordina y supervisa los demas componentes.
- Martin Kleppmann, `Designing_Data_Intensive_Applications`, cap. "Timeouts and unbounded delays", p. 295. Explica retry, timeout y declaracion de nodo muerto cuando no hay respuesta.

Aplicacion a SERSAN:

El orquestador no debe ser solo botonera. Es la autoridad de lifecycle: premarket scan, trading, pausa, cierre, reconexion, cierre forzado y degradacion controlada.

## 5. Strategy Runtime

Que debe construirse:

Un runtime de estrategias con registry/loader, instancias configuradas, interfaz comun de datos, generacion de senales y conversion controlada a intenciones de orden.

Referencias:

- `Successful Algorithmic Trading`, cap. "Events", pp. 140-142. Define `MarketEvent`, `SignalEvent`, `OrderEvent` y `FillEvent` como contrato de flujo interno.
- `Successful Algorithmic Trading`, cap. "Data Handler", p. 144. Explica que historico y live deben compartir interfaz para que data handlers sean intercambiables.
- `Successful Algorithmic Trading`, cap. "Strategy", p. 149. Muestra que la estrategia consume market events/data handler y emite senales.
- Stefan Jansen, `Machine_Learning_for_Algorithmic_Trading_2nd`, cap. "From data and signals to trades - strategy", p. 360. Presenta data feeds como materia prima de la estrategia.

Aplicacion a SERSAN:

Cada estrategia debe ser un modulo con identidad, configuracion, estado y senales auditables. La salida de estrategia no debe saltarse riesgo, portfolio ni OMS.

## 6. Locate Management

Que debe construirse:

Una capa para shorts que controle disponibilidad, coste, aprobacion, expiracion y consumo de locates antes de permitir ordenes short.

Referencias:

- Larry Harris, `Trading_and_Exchanges...`, cap. "Short Interest Rebate", p. 168. Indica que antes de aceptar una venta short el broker debe determinar que los valores estaran disponibles para settlement.
- Larry Harris, mismo libro, cap. "Short Interest Rebate", pp. 169-170. Explica rebate, borrow fee y disponibilidad del security.
- Larry Harris, mismo libro, cap. "Security Lending Fees", p. 171. Senala que las fees dependen de demanda de shorts y disponibilidad de acciones.
- Larry Harris, mismo libro, cap. "Arbitrageurs", p. 383. Incluye borrowing fees y pagos de dividendos al lender como costes de posiciones short.

Aplicacion a SERSAN:

Para small caps short, "hay senal" no equivale a "hay trade". El sistema necesita estado de locate por simbolo, coste, cantidad disponible, vencimiento y bloqueo si no hay disponibilidad.

## 7. Risk and Operational Controls

Que debe construirse:

Un risk engine con limites de exposicion, position sizing, max daily loss/drawdown, stops, sector/ADV constraints, kill switch y controles de operacion degradada.

Referencias:

- `Successful Algorithmic Trading`, cap. "Sources of Risk", p. 128. Divide riesgo en estrategia, portfolio, contraparte, mercado y operacional.
- `Successful Algorithmic Trading`, cap. "Kelly Criterion", p. 130. Menciona max drawdowns, sector allocation y average daily volume limits como restricciones.
- `Successful Algorithmic Trading`, cap. "Why An Event-Driven Backtester?", p. 139. Situa risk management, sector exposure y position sizing en Portfolio, con posible clase RiskManagement separada.
- Robert Carver, `systematic_trading`, cap. "Why a modular framework?", p. 124. Explica que trading rules deben estar envueltas por un marco de position/risk management.

Aplicacion a SERSAN:

El bloque de riesgo debe estar entre estrategia y ejecucion. Debe poder rechazar, reducir, cerrar o pausar operaciones por condiciones de cuenta, simbolo, locate, feed o sesion.

## 8. Order Management and DAS Execution

Que debe construirse:

Un OMS/adaptador DAS con ciclo: intent/signal -> order event -> DAS command -> broker response/action order -> fill -> portfolio/account update -> traceability.

Referencias:

- `Successful Algorithmic Trading`, cap. "Events", p. 140. El `ExecutionHandler` toma `OrderEvents`, ejecuta via broker simulado/real y crea `FillEvents`.
- `Successful Algorithmic Trading`, cap. "Events", p. 142. `FillEvent` describe coste de compra/venta y costes de transaccion como fees/slippage.
- `Successful Algorithmic Trading`, cap. "Event-Driven Execution", p. 165. El handler de ejecucion conectado a broker recibe queue y `order_routing`.
- Larry Harris, `Trading_and_Exchanges...`, cap. "Order Routing Systems", p. 115. Explica que order-routing systems transmiten ordenes entre clientes, brokers, dealers y exchanges.
- Larry Harris, mismo libro, cap. "Brokers", p. 162. Presenta FIX como protocolo de intercambio para integrar sistemas de trading de distintos vendors.

Aplicacion a SERSAN:

DAS debe ser un adapter externo, no el modelo interno. El sistema debe persistir la orden interna, comando enviado, respuesta DAS, fill y errores para reconciliacion.

## 9. Position and Account Accounting

Que debe construirse:

Accounting interno que reconstruya posiciones, average/cost basis, realized PnL, unrealized PnL, cash/equity, fees y exposicion desde fills y eventos de cuenta.

Referencias:

- `Successful Algorithmic Trading`, cap. "Portfolio", p. 153. Distingue `all_positions` y `current_positions`; una posicion negativa indica short.
- `Successful Algorithmic Trading`, cap. "Portfolio", pp. 155-157. Actualiza posiciones y holdings a partir de market data y `FillEvent`.
- Jason Strimpel, `Python_for_Algorithmic_Trading_Cookbook`, cap. "Getting portfolio details", p. 336. Usa `position`, market value, average cost, unrealized PnL y realized PnL.
- Jason Strimpel, mismo libro, cap. "Getting PnL", p. 338. Solicita daily PnL, unrealized PnL y realized PnL para calcular retornos y metricas.

Aplicacion a SERSAN:

La GUI no debe calcular PnL desde tablas visibles. Debe leer una fuente accounting unica derivada de fills, snapshots de cuenta y reglas de matching/cost basis.

## 10. Execution Quality / Slippage

Que debe construirse:

Una capa de TCA/slippage que compare precio esperado, benchmark, midpoint/spread, fill real, route, liquidez, fees, market impact y oportunidad perdida.

Referencias:

- Larry Harris, `Trading_and_Exchanges`, cap. "Transaction Cost Components", p. 83. Relaciona execution quality, transaction costs, spreads, comisiones y fees.
- Larry Harris, `Trading_and_Exchanges...`, cap. "Liquidity and Transaction Cost Measurement", p. 437. Explica effective spread como diferencia firmada entre trade price y quote midpoint.
- Larry Harris, mismo libro, cap. "Liquidity and Transaction Cost Measurement", p. 449. Descompone implementation shortfall en timing, market impact, commission y missed trade opportunity.
- `Successful Algorithmic Trading`, cap. "Events", p. 142. Incluye fees/slippage como parte del `FillEvent`.

Aplicacion a SERSAN:

El modulo debe almacenar expected vs actual por orden/fill y agregarlo por estrategia, simbolo, route, liquidez y hora. Es clave para small caps, donde el backtest puede no reflejar fills reales.

## 11. Analytics and Reporting

Que debe construirse:

Un subsistema que reconstruya trades cerrados, series de equity/returns, metricas, drawdown, win/loss, profit factor, Sharpe/Sortino, informes HTML y export CSV.

Referencias:

- `Successful Algorithmic Trading`, cap. "Risk/Reward Analysis", pp. 122-124. Explica Sharpe ratio y calculo sobre returns.
- `Successful Algorithmic Trading`, cap. "Drawdown Analysis", p. 126. Trata max drawdown y duracion.
- `Successful Algorithmic Trading`, cap. "Portfolio", p. 158. Genera equity curve y returns stream para performance calculations.
- Kevin J. Davey, `Building_Winning_Algorithmic_Trading_Systems`, cap. "Prob > 0", p. 83. Resume performance report, equity curve, Monte Carlo y parametros como profit factor.
- Jason Strimpel, `Python_for_Algorithmic_Trading_Cookbook`, cap. "Portfolio risk metrics", p. 347. Calcula Sharpe, Sortino y drawdown desde portfolio returns.

Aplicacion a SERSAN:

El reporting debe salir de datos operativos persistidos, no de logs sueltos. Debe soportar rangos: hoy, mensual, total, por estrategia y portfolio agregado.

## 12. Observability and Recovery

Que debe construirse:

Logs estructurados, consola operador, health checks, watchdog, metricas de recursos, estado de feed/DAS, alertas, retry/backoff y procedimientos de recuperacion.

Referencias:

- Yves Hilpisch, `Python_for_Algorithmic_Trading`, cap. "Logging and Monitoring", p. 493. Describe logging en disco y monitoring en tiempo real para operaciones automatizadas.
- Yves Hilpisch, mismo libro, cap. "Capital Management / Infrastructure and Deployment", p. 446. Vincula cloud deployment robusto con logging, monitoring y observacion via sockets.
- Martin Kleppmann, `Designing_Data_Intensive_Applications`, cap. "How important is reliability?", p. 30. Define recuperacion rapida ante fallos humanos y errores como parte de sistemas fiables.
- Martin Kleppmann, mismo libro, cap. "Timeouts and unbounded delays", p. 295. Justifica retry, timeout y deteccion de fallos.
- Martin Kleppmann, mismo libro, cap. "Partitioned logs", p. 455. Explica logs durables como base para almacenamiento y notificacion low-latency.

Aplicacion a SERSAN:

El watchdog debe observar procesos, conexiones, heartbeats y latencia de datos. Los logs deben permitir reconstruir que paso antes de una pausa, cierre o fallo de ejecucion.

## 13. Configuration System

Que debe construirse:

Configuracion externa por dominio: estrategias, premarket, locates, orquestador, logs, notificaciones, GUI y calendario; con schema, validacion, defaults y perfiles.

Referencias:

- Leonardo Giordani, `Clean_Architectures_in_Python`, cap. "Orchestration management", pp. 132 y 137. Usa variables de entorno, archivos JSON y funciones de lectura de configuracion.
- Leonardo Giordani, mismo libro, cap. "Test and create an HTTP endpoint", p. 70. Muestra clases de configuracion para production, development y testing.
- Robert C. Martin, `Clean_Architecture`, cap. 26 "The Main Component", pagina: n/a (EPUB). Situa la creacion de factories, strategies y global facilities en el componente principal.
- `Successful Algorithmic Trading`, cap. "Parameter Adjustment", p. 202. Muestra estrategias parametrizadas inyectadas al crear instancias.

Aplicacion a SERSAN:

Los `json5` visibles encajan con una configuracion por bounded context. Debe validarse antes de guardar/aplicar, y el runtime debe poder explicar que version de configuracion produjo cada trade.

## 14. Desktop Control Panel

Que debe construirse:

Una GUI desktop como adapter de operador: control de lifecycle, estado, scanner, estrategias, ordenes, posiciones, logs, reporting y configuracion. La GUI no debe contener reglas de negocio.

Referencias:

- Robert C. Martin, `Clean_Architecture`, cap. 22 "The Clean Architecture", pagina: n/a (EPUB). Situa presenters, views y controllers dentro de interface adapters, separados de use cases/entities.
- Robert C. Martin, `Clean_Architecture`, cap. 23 "Presenters and Humble Objects", pagina: n/a (EPUB). Propone separar comportamientos dificiles de testear de la logica testable.
- Robert C. Martin, `The_Clean_Coder`, cap. "Acceptance Tests", pp. 142-143. Advierte que las GUIs cambian mucho y recomienda probar mediante abstracciones estables.
- Yves Hilpisch, `Python_for_Algorithmic_Trading`, cap. "The Basics / Visualizing Streaming Data with Plotly", p. 362. Trata visualizacion en tiempo real de streaming data.
- `Successful Algorithmic Trading`, cap. "PyQt, IPython and Matplotlib", p. 53. Menciona herramientas Python para visualizacion y desarrollo interactivo.

Aplicacion a SERSAN:

CustomTkinter o cualquier toolkit debe quedar como delivery mechanism. La GUI llama casos de uso: start, pause, restart, stop, edit config, export, inspect; no decide riesgo ni ejecucion.

## 15. Persistent Operational Storage

Que debe construirse:

Una capa persistente para orders, action orders, fills, positions, account snapshots, equity, trades reconstruidos, locates, slippage, logs y configuraciones/versiones.

Referencias:

- `Successful Algorithmic Trading`, cap. "Financial Data Storage / Securities Master Databases", pp. 56-58. Justifica securities master, storage formats y RDBMS para datos financieros.
- Jason Strimpel, `Python_for_Algorithmic_Trading_Cookbook`, cap. "Storing live tick data in a local SQL database", pp. 319-322. Crea tablas SQLite e inserta ticks streaming.
- Jason Strimpel, mismo libro, cap. "Getting portfolio details / Getting PnL", pp. 336-338. Persiste/estructura posiciones, market value, average cost, realized/unrealized PnL.
- Martin Kleppmann, `Designing_Data_Intensive_Applications`, cap. "Partitioned logs", p. 455. Define logs append-only como almacenamiento duradero y mecanismo de notificacion.
- Martin Kleppmann, mismo libro, cap. "State, streams, and immutability", p. 467. Explica que el estado puede derivarse de logs de transacciones/eventos.

Aplicacion a SERSAN:

El diseno mas robusto es event log + tablas/proyecciones: eventos crudos para auditoria y tablas derivadas para GUI/reporting. Esto permite replay, reconciliacion y analisis post-mortem.

## Brechas y siguientes pasos

1. OCR pendiente:
   - `Algorithmic_Trading_and_DMA_-_Johnson.pdf` probablemente contiene evidencia fuerte para DMA/OMS, pero no tiene capa de texto.
   - `_OceanofPDF.com_Clean_Architecture_-_Anderson_Rogerio.pdf` tampoco es extraible sin OCR.

2. EPUB sin pagina fija:
   - `Clean_Architecture_-_Robert_C_Marti.epub` es clave para Main Component, Interface Adapters, Presenters y Database as Detail, pero no ofrece pagina estable.
   - `A_Guide_to_Creating_a_Successful_Algorithmic_Trading_Strategy.epub` aporta seleccion de instrumentos y risk controls, pero sin pagina estable.

3. Recomendacion de implementacion:
   - Crear backlog de construccion con los 15 bloques como bounded contexts.
   - Para cada bloque, definir contratos de entrada/salida y eventos persistidos.
   - Empezar por datos, storage, event bus, orchestrator y accounting antes de GUI sofisticada.
