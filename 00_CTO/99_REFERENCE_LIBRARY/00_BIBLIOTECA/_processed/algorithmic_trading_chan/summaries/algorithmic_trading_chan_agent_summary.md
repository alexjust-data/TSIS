# Algorithmic Trading - Ernest P. Chan

Resumen operativo para agentes TSIS.

## Menu

- [Resumen ejecutivo](#resumen-ejecutivo)
- [Rol dentro de TSIS](#rol-dentro-de-tsis)
- [Mapa rapido de capitulos](#mapa-rapido-de-capitulos)
- [Capitulo 1 - Backtesting y ejecucion automatizada](#capitulo-1---backtesting-y-ejecucion-automatizada)
- [Capitulo 2 - Bases de mean reversion](#capitulo-2---bases-de-mean-reversion)
- [Capitulo 3 - Implementacion de mean reversion](#capitulo-3---implementacion-de-mean-reversion)
- [Capitulo 4 - Mean reversion en acciones y ETFs](#capitulo-4---mean-reversion-en-acciones-y-etfs)
- [Capitulo 5 - Mean reversion en divisas y futuros](#capitulo-5---mean-reversion-en-divisas-y-futuros)
- [Capitulo 6 - Momentum interday](#capitulo-6---momentum-interday)
- [Capitulo 7 - Momentum intraday](#capitulo-7---momentum-intraday)
- [Capitulo 8 - Gestion del riesgo](#capitulo-8---gestion-del-riesgo)
- [Blueprint TSIS derivado](#blueprint-tsis-derivado)
- [Quality gates para agentes](#quality-gates-para-agentes)
- [Limitaciones](#limitaciones)

## Resumen ejecutivo

Este libro es una fuente practica intermedia entre un manual introductorio de trading cuantitativo y una arquitectura profesional de backtesting. No entrega un motor event-driven institucional completo, pero si explica con claridad que un backtest util debe estar conectado semanticamente con la ejecucion real: los mismos detalles que se simulan deben ser implementables despues en trading automatizado.

Para TSIS, su valor principal esta en cuatro areas:

1. Traducir ideas de estrategia a modelos cuantitativos simples.
2. Identificar sesgos mecanicos comunes del backtest.
3. Aterrizar estrategias de mean reversion y momentum en reglas programables.
4. Separar resultado estadistico, realismo operativo y gestion del riesgo.

El libro debe usarse despues de `Quantitative Trading` y antes de `Machine Trading` cuando un agente necesite convertir hipotesis en prototipos comprobables. Para arquitectura de motor, debe complementarse con NautilusTrader, LEAN y QuantStart.

## Rol dentro de TSIS

Encaja especialmente en estas capas:

```text
Research hypothesis
    -> Strategy prototype
    -> Backtest assumptions
    -> Execution feasibility checks
    -> Risk model
    -> Live/automated execution readiness
```

No sustituye:

- el contrato event-driven del motor;
- un OMS completo;
- un modelo realista de fills para small caps;
- el protocolo cientifico de PBO/DSR de Lopez de Prado.

Si un agente esta trabajando en TSIS_BACKTEST_ENGINE, este libro debe leerse como fuente de criterios para que las estrategias y los backtests no sean ingenuos, no como especificacion unica del software.

## Mapa rapido de capitulos

| Capitulo | Paginas aprox. | Uso TSIS |
|---|---:|---|
| 1. Backtesting and Automated Execution | 19-56 | Sesgos, hipotesis, plataformas, equivalencia backtest/live |
| 2. The Basics of Mean Reversion | 57-80 | Estacionariedad, ADF, Hurst, variance ratio, cointegracion |
| 3. Implementing Mean Reversion Strategies | 81-104 | Spreads, ratios, Bollinger, scaling-in, Kalman, errores de datos |
| 4. Mean Reversion of Stocks and ETFs | 105-124 | Pares, ETFs, gaps, baskets, problemas especificos de acciones |
| 5. Mean Reversion of Currencies and Futures | 125-150 | Cross-rates, rollovers, calendar spreads, roll return |
| 6. Interday Momentum Strategies | 151-172 | Momentum time-series y cross-sectional, roll returns, filtros |
| 7. Intraday Momentum Strategies | 173-186 | Opening gaps, noticias, PEAD, leveraged ETFs, order book imbalance |
| 8. Risk Management | 187-204 | Kelly, CPPI, stops, indicadores de riesgo |

## Capitulo 1 - Backtesting y ejecucion automatizada

La tesis central del capitulo es que backtesting y ejecucion automatizada no deben ser mundos separados. Un backtest no es solo calcular retornos historicos: es reproducir decisiones que habrian sido posibles con la informacion disponible en cada momento y con precios ejecutables bajo reglas concretas.

Puntos clave para TSIS:

- El motor debe distinguir claramente entre datos observados, decision, orden, fill y posicion.
- Una estrategia que compra en la apertura no puede ser tratada igual que una estrategia que decide despues de observar la apertura.
- Usar maximos, minimos o cierres de la misma barra para tomar una decision intrabar introduce look-ahead si el evento de decision no esta definido.
- Si el mismo codigo de estrategia puede ejecutarse en historico y en vivo cambiando solo el data feed y el execution adapter, baja mucho el riesgo de divergencia semantica.
- La plataforma importa: no basta que calcule resultados; debe permitir automatizar exactamente la logica que se probo.

Sesgos y riesgos:

- `look-ahead bias`: la estrategia lee informacion futura.
- `data-snooping bias`: se prueban demasiadas variantes y se conserva la ganadora.
- `survivorship bias`: se eliminan del universo historico los activos que desaparecieron.
- `corporate-action error`: splits y dividendos mal ajustados alteran senales y P&L.
- `short-sale infeasibility`: las acciones no siempre pueden ser tomadas prestadas.
- `primary-vs-consolidated-price mismatch`: usar precios consolidados para una ejecucion que depende de una ruta real de mercado puede exagerar la ejecutabilidad.

Para TSIS, este capitulo justifica que desde v0.1 existan:

```text
run_manifest.json
dataset_id
universe_id
strategy_version
cost_model_version
fill_model_version
decision_timestamp
observable_state_snapshot
order_event_ledger
```

Tambien introduce una idea importante: no todas las estrategias merecen backtesting. Si una estrategia requiere datos de order book que no tienes, o supuestos de ejecucion HFT que no puedes simular, el resultado puede ser decorativo.

## Capitulo 2 - Bases de mean reversion

El capitulo diferencia entre una intuicion visual de mean reversion y una propiedad estadistica testeable. La mayor parte de las series de precios son cercanas a random walks; que los retornos tengan media cercana a cero no implica que el precio sea mean-reverting de forma explotable.

Conceptos utiles:

- `stationarity`: propiedad necesaria para muchos modelos de mean reversion.
- `ADF test`: prueba si una serie tiene tendencia a revertir.
- `Hurst exponent`: mide persistencia o antipersistencia.
- `variance ratio`: testea desviacion respecto a random walk.
- `half-life`: convierte la velocidad estimada de reversion en horizonte operativo.
- `cointegration`: permite construir carteras estacionarias a partir de activos no estacionarios.

Aplicacion TSIS:

- Antes de crear una estrategia de pares, el pipeline de research debe producir evidencia de estacionariedad o cointegracion.
- Los lookbacks no deberian elegirse solo por optimizacion; la vida media estimada puede dar un punto de partida defendible.
- La estrategia debe guardar el metodo que justifico el par, spread o basket usado.

Contrato minimo recomendado:

```text
mean_reversion_model_id
stationarity_test_type
test_window
estimated_half_life
entry_zscore
exit_zscore
formation_period
trading_period
```

## Capitulo 3 - Implementacion de mean reversion

Este capitulo baja la teoria a reglas. Compara spreads de precios, log spreads y ratios, y muestra que la forma de construir el spread cambia la interpretacion economica de la estrategia.

Ideas importantes:

- Un spread cointegrado puede operarse como desviacion respecto a una media.
- Un ratio de precios puede parecer intuitivo, pero no siempre respeta una relacion economica estable.
- Las Bollinger Bands convierten mean reversion en una regla de entrada/salida simple.
- El scaling-in puede reducir impacto y aprovechar desviaciones mas grandes, pero introduce mas parametros y mas riesgo.
- El Kalman filter permite estimar relaciones dinamicas entre activos.
- Los errores de datos son especialmente peligrosos en mean reversion porque un tick malo puede parecer una oportunidad extraordinaria.

Implicacion para TSIS:

El motor debe poder distinguir entre:

```text
feature calculation
signal generation
portfolio sizing
order generation
fill simulation
```

Un z-score no es una orden. Es una observacion que puede convertirse en una intencion, despues en un target, despues en una orden y finalmente en un fill.

Quality gate especifico:

```text
Ninguna estrategia de threshold puede operar sin filtros de calidad de datos.
```

## Capitulo 4 - Mean reversion en acciones y ETFs

Este es el capitulo mas relevante para small caps, aunque no sea un manual especifico de small caps.

Puntos clave:

- Los pares de acciones pueden parecer cointegrados en el pasado y romperse por cambios especificos de compania.
- La liquidez, el spread y la capacidad de short son restricciones reales, no detalles secundarios.
- El tamano disponible en NBBO puede ser pequeno incluso cuando el volumen diario parece suficiente.
- La decimalizacion redujo spreads y comprimio oportunidades de market making simple.
- Los ETFs pueden ofrecer relaciones mas estables que pares de acciones individuales, pero tambien pueden romperse cuando aparece una variable economica omitida.
- En estrategias de gaps, el momento exacto de decision y entrada es critico.

Para TSIS small caps:

- El universo debe ser point-in-time y survivorship-free.
- Las reglas deben registrar si se permite short y bajo que fuente de borrow.
- La simulacion debe tener como minimo spread, slippage y filtro de volumen.
- Para estrategias intraday, no se puede usar una barra OHLC como si todo su recorrido fuera conocido al decidir.

Campos recomendados en ledgers:

```text
is_shortable_at_decision
borrow_source
borrow_fee_assumption
spread_bps_at_decision
available_volume_proxy
primary_exchange
halt_status
corporate_action_state
```

## Capitulo 5 - Mean reversion en divisas y futuros

Aunque TSIS este centrado en small caps, este capitulo aporta lecciones de contabilidad y contratos:

- Una estrategia puede estar correctamente senalizada y aun asi tener P&L mal calculado si la moneda de denominacion no se trata bien.
- Los rollovers, intereses y vencimientos son parte de la rentabilidad real.
- En futuros, el roll return puede dominar el retorno spot.
- Calendar spreads e intermarket spreads exigen datos continuos construidos con reglas explicitas.

Transferencia a TSIS:

```text
El backtester no debe inferir P&L desde precios finales sin ledger.
```

Debe haber accounting incremental:

```text
fill -> cash -> position -> realized_pnl -> unrealized_pnl -> equity
```

La leccion general es que cada instrumento necesita su contrato economico. En small caps esto se traduce en acciones ajustadas, splits, dividendos, borrow, comisiones, ECN fees y reglas de sesion.

## Capitulo 6 - Momentum interday

El libro separa momentum time-series y cross-sectional. Tambien insiste en que las causas economicas importan: roll returns, informacion que se difunde lentamente, flujos forzados o efectos microestructurales.

Ideas utiles:

- Momentum no debe reducirse a "si subio, compro"; hay que definir horizonte, universo, rebalanceo y costes.
- Los tests deben evitar solapamientos que inflen significancia.
- Los filtros de mean reversion pueden mejorar o condicionar estrategias momentum.
- El comportamiento puede cambiar tras eventos estructurales de mercado.

Para TSIS:

- Una estrategia momentum debe declarar el horizonte de formacion y de tenencia.
- Las senales deben separarse de construccion de cartera y ejecucion.
- Si se prueban muchos horizontes, el experimento debe registrar el numero de variantes.

Contrato recomendado:

```text
formation_window
holding_window
rebalance_frequency
ranking_metric
selection_count
cost_assumption
variant_count
```

## Capitulo 7 - Momentum intraday

Este capitulo aporta ideas directamente conectadas con scanners de small caps:

- Opening gap strategy.
- News-driven momentum.
- Post-earnings announcement drift.
- Eventos como guidance, revisions, same-store sales, M&A, index changes y macro surprises.
- Leveraged ETF end-of-day rebalancing.
- Order book imbalance.

Lo importante no es copiar una estrategia, sino respetar la temporalidad:

```text
announcement_time
observable_time
decision_time
order_submission_time
fill_time
```

Para small caps, los eventos y el tape importan. Una noticia antes del open, un gap, un halt o una aparicion en scanner deben entrar como eventos con ciclo de vida, no solo como columnas en una tabla final.

Uso TSIS:

```text
EventStateSnapshot
MarketStateSnapshot
DecisionRecord
```

deben capturar que sabia el sistema cuando decidio. Este capitulo refuerza que el motor debe poder reproducir market replay, no solo calcular factores al cierre.

## Capitulo 8 - Gestion del riesgo

El capitulo define la gestion del riesgo como maximizacion del crecimiento de largo plazo, no como simple reduccion de volatilidad.

Conceptos:

- Kelly y half-Kelly.
- Kelly multiestrategia usando matriz de covarianzas.
- Monte Carlo con distribuciones no gaussianas.
- CPPI para controlar drawdown maximo asumido.
- Stop loss segun naturaleza de la estrategia.
- Indicadores de riesgo como VIX, TED spread, HYG, divisas u order flow.

Implicacion para TSIS:

- `risk` no es un reporte posterior; debe ser componente pre-trade y post-trade.
- Para mean reversion, un stop demasiado cercano puede destruir el edge; para momentum, un stop suele ser mas natural.
- Los indicadores de riesgo deben validarse con cuidado porque son terreno fertil para data snooping.

Contrato recomendado:

```text
max_risk_per_trade
max_daily_loss
max_symbol_exposure
portfolio_leverage_limit
stop_model_id
risk_indicator_set_id
kill_switch_rule_id
```

## Blueprint TSIS derivado

Arquitectura minima que este libro empuja indirectamente:

```text
Data Foundation
    -> HistoricalDataFeed / ReplayFeed / LiveFeed
    -> Clock + EventLoop
    -> MarketStateBuilder
    -> Strategy
    -> Signal
    -> PortfolioConstruction
    -> PreTradeRisk
    -> OrderManager
    -> ExecutionSimulator / BrokerAdapter
    -> FillLedger
    -> Accounting
    -> PostTradeRisk
    -> Metrics + Validation
```

El punto critico es que la estrategia no debe consultar el futuro ni saltarse capas. Debe observar estado, decidir, emitir intenciones y dejar que portfolio, risk, OMS y execution hagan su trabajo.

## Quality gates para agentes

Antes de aceptar una implementacion inspirada en este libro, comprobar:

- La decision tiene timestamp propio.
- La orden tiene timestamp propio.
- El fill tiene timestamp propio.
- El precio usado era observable o ejecutable bajo reglas documentadas.
- El backtest registra splits, dividendos y universo historico.
- Los costes no son cero salvo que el test este marcado como teorico.
- Short trades exigen estado de borrow o supuesto declarado.
- Los parametros optimizados quedan registrados.
- El numero de variantes probadas queda registrado.
- La misma estrategia puede correr en historical replay y live adapter sin reescribir la logica central.
- La estrategia tiene benchmark simple y pruebas de sensibilidad.

## Limitaciones

No es una guia completa para construir un motor event-driven profesional. Sus ejemplos estan orientados a explicar estrategias y riesgos practicos, no a definir un OMS, una cola de eventos, un message bus, un modelo de fill realista o un sistema de auditoria completo.

Para TSIS debe combinarse con:

- NautilusTrader para arquitectura profesional event-driven.
- LEAN para separacion de universo, alpha, portfolio, risk y execution.
- QuantStart para el primer esqueleto Python.
- Harris para ordenes, mercado, liquidez y ejecucion.
- Lopez de Prado para validacion cientifica avanzada.
