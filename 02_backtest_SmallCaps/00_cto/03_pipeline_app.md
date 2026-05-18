# Tsis

Lo que quieres montar ya no es “un backtest”, sino **un motor de investigación sistemática** parecido a lo que TradeStation te da hecho, pero controlado por ti de extremo a extremo y optimizado para la microestructura de las Micro Caps.

La forma correcta de pensarlo es esta: **TradeStation = editor de estrategia + motor de simulación + optimizador + reporting**. Ahora, con tu data de Polygon/Massive, tú tienes solo la materia prima. Te faltan las otras cuatro capas. Además, para microcaps y small caps “muertas” que despiertan con news/pump, hay un detalle crítico: los agregados OHLC no bastan para todo, porque Massive/Polygon construye barras solo con trades “cualificados”, no genera barra si no hubo trades elegibles, y además dispone también de trades tick-by-tick, NBBO quotes, splits, dividends, ticker events y condition codes. Para este tipo de setups, eso es importantísimo. ([Massive][1])

Mi recomendación práctica es que no intentes replicar TradeStation al 100% desde el día 1. Empieza con un stack simple pero serio: **Python + Parquet + DuckDB/Polars + vectorbt o backtesting.py**. DuckDB consulta Parquet directamente y empuja filtros al escaneo; Polars con `scan_parquet` también trabaja en modo lazy y optimiza lectura; `backtesting.py` tiene `Backtest.run()` y `Backtest.optimize()`; y `vectorbt` está pensado para backtests vectorizados sobre pandas/NumPy y carteras desde señales. ([DuckDB][2])

Para ti, la mejor división de trabajo sería esta: **backtesting.py para depurar una estrategia individual** como si estuvieras en TradeStation, y **vectorbt para barrer miles de combinaciones y cestas de tickers**. Si luego quieres un motor totalmente propio, ya lo construyes encima de tus datasets. El concepto de **walk-forward analysis** sigue siendo el mismo que en plataformas clásicas: optimizas en una ventana in-sample, congelas parámetros, y validas en la siguiente ventana out-of-sample; Interactive Brokers lo describe justo así. ([kernc.github.io][3])

## Qué debes hacer, de principio a fin (Refinado con Capas Institucionales)

### 1) Congelar una base de datos “research-grade”

No empieces programando la estrategia. Primero deja cerrada la capa de datos. Guarda la data original en **Parquet** por fecha y, si puedes, por tipo: `minute_bars/`, `daily_bars/`, `trades/`, `quotes/`, `splits/`, `dividends/`, `ticker_events/`. No sobrescribas el raw. Toda limpieza o enriquecimiento debe ir en capas nuevas. Parquet + DuckDB/Polars te permite leer solo columnas y filas necesarias, que es justo lo que necesitas cuando acabas trabajando con 2005–2026 y miles de tickers. ([DuckDB][2])

* Integra obligatoriamente tus archivos de exclusión de auditoría (ej. daily_lt1b_hard_invalid_exclusion.parquet). Cualquier ticker/día marcado como bad (por errores de parseo o precios inválidos) debe quedar fuera del motor antes de empezar el proceso para no contaminar los resultados.

### 2) Resolver bien el universo histórico

En microcaps el mayor error no es la lógica de entrada; es el **survivorship bias**. No puedes testear hoy solo contra las compañías que siguen vivas. Tienes que reconstruir el universo “tal como existía” en cada fecha, incluyendo delistadas, cambios de ticker, fusiones y renombrados. Massive/Polygon expone `All Tickers`, `Ticker Overview` y `Ticker Events`, y marca si un activo está activo o delistado. Si no controlas esto, tus resultados saldrán artificialmente mejores. ([Massive][4]). Usa tu data auditada para asegurar que el universo <1B es consistente a lo largo del tiempo.

### 3) Elegir tu “verdad” de precios: La Microestructura

Tienes que decidir si tus setups se evalúan con:

* **barras de 1 minuto**,
* **trades tick-by-tick**,
* **quotes NBBO**,
* o combinación de varios.

Para Microcaps, yo usaría:

* Barras minuto para detección gruesa (Capa 1: Screener).
* Quotes NBBO (Capa 2: Data Broker) para reconstruir el Inside Quote (mejor Bid/Ask) y modelar ejecuciones realistas. No te fíes del precio de cierre de la vela de 1m; usa el lado correcto del spread para calcular el slippage real.

Para “primer día verde”, “primer día rojo”, “gap and go” y setups de squeeze/pump, yo no usaría solo OHLC minuto. Usaría:

* **barras minuto** para detección gruesa del patrón,
* **quotes NBBO** para modelar spread y ejecuciones realistas,
* **trades** para confirmar prints y volumen real,
* y **condition codes** para filtrar prints raros. ([Massive][1])

### 4) Normalizar corporate actions

Diferencia entre series ajustadas (continuidad) y no ajustadas (lo que veía el trader). En small caps, ignorar esto destruye señales de gaps y comparaciones de volumen.

Debes decidir dos series:

* una **ajustada** para indicadores de continuidad histórica,
* y otra **no ajustada** para reproducir mejor lo que veía el trader en tiempo real.

Massive/Polygon permite pedir agregados ajustados por splits o no ajustados; además tiene endpoints específicos de splits y dividends. En small caps, si no separas estas dos realidades, te cargas señales, gaps y comparaciones de volumen/precio. ([Massive][1])

### 5) Definir sesiones de mercado
Fija reglas para premarket, regular session y after-hours. Muchas microcaps hacen el movimiento decisivo fuera de mercado regular.  
Antes de programar una sola entrada, fija reglas de sesión:

* premarket,
* regular session,
* after-hours,
* holidays,
* media days,
* early close.

Massive/Polygon documenta market holidays y market status, y las barras cubren premarket, regular y after-hours. Esto importa mucho porque muchas microcaps hacen el movimiento decisivo fuera de mercado regular. ([Massive][1])

### 6) Construir una tabla maestra diaria por ticker

Tu primera tabla útil es una tabla de screening diario (Capa 1). Usa DuckDB para filtrar terabytes de datos y encontrar solo los días donde el precio "despertó" (RVOL > 5, Gap > 20%, etc.). Esto evita que el simulador pierda tiempo procesando el 99% de los días en los que el precio está muerto.

Tu primera tabla útil no es la intradía: es una **tabla diaria de screening**, una fila por ticker por día, con columnas como:

* fecha,
* ticker,
* activo/inactivo,
* close,
* dollar volume,
* market cap si la tienes,
* float si la tienes,
* gap vs close anterior,
* volumen relativo,
* número de barras premarket,
* high of day,
* low of day,
* rango intradía,
* news flag si luego lo añades,
* reverse split reciente,
* días desde IPO/cambio de ticker.
* etc

Esto te permite responder: “¿qué compañías estaban muertas y de repente despertaron?” y crear cestas históricas coherentes. Massive tiene endpoints de float, IPOs, short interest, short volume y ticker events que luego puedes unir. ([Massive][4])

### 7) Formalizar cada setup como una definición mecánica

Cada setup (ej. "Gap and Go") debe ser una función pura. Define reglas exactas de entrada y salida desconectadas de la ejecución técnica.  
Aquí es donde la mayoría falla. “Primer día verde” no es una idea; tiene que convertirse en reglas exactas. Por ejemplo:

**Primer día verde**

* Hoy cierra verde.
* Las `N` sesiones anteriores cerraron rojas o laterales.
* Gap máximo permitido.
* Volumen relativo mínimo.
* Market cap/float dentro de rango.
* Sin reverse split en los últimos `X` días o, si lo aceptas, marcado aparte.

**Gap and go / Cap and Go**

* Gap premarket entre `a` y `b`.
* PM volume > `x`.
* Open above PM high / reclaim de VWAP / primer pullback EMA.
* Entrada solo si el spread o slippage estimado es tolerable.

No intentes programar diez setups a la vez. Haz uno, ciérralo, y luego duplicas el pipeline. El objetivo es que cada setup sea una **función pura** que genere señales a partir de datos ya preparados.

### 8) Separar “selector” de “ejecutor”

Esto en TradeStation suele venir mezclado. Tú debes separarlo en dos módulos:  

**Selector (Capa 1):** decide qué tickers entran en la cesta ese día."In-Play"  
**Ejecutor(Capa 4: Execution Engine):** decide exactamente cómo se entra, sale y gestiona el riesgo. cómo gestionar la orden (Stop loss, trailing, etc.) basándose en la microestructura.  

Ejemplo:

* Selector: “microcaps entre 5M y 300M, con RVOL > 5 y gap > 20%”.
* Ejecutor: “entrada en rompimiento de PM high, stop bajo ORB 1m, salida parcial en 1R y resto al close”.

Esa separación te permite reutilizar el mismo ejecutor sobre distintas cestas y viceversa.

### 9) Crear un motor de simulación realista (Capa 4)

Tu simulador debe decidir el llenado real. Con NBBO quotes puedes modelar el spread; con trades puedes aproximar la liquidez.

* **Añadido Institucional**: El simulador debe incluir lógica de Short Borrow (¿había acciones para cortos? a qué precio?) y detección de Halts para no simular salidas imposibles durante una parada de mercado.

Tu simulador tiene que decidir:

* cuándo entra la orden,
* a qué precio se rellena,
* si puede haber fill parcial,
* cuánto deslizamiento hay,
* y cuánto tamaño puedes meter sin deformar el resultado.

Aquí es donde más se alejan TradeStation y la realidad de microcaps. En estas acciones, el problema no es solo la señal; es la **ejecución**. Con NBBO quotes puedes modelar spread; con trades puedes aproximar liquidez; con barras solas, no. ([Massive][5])

Yo te recomendaría empezar con **tres modelos de fill**:

1. **Idealista:** fill al precio de señal.
2. **Conservador:** fill en bid/ask o en peor extremo del spread.
3. **Muy conservador:** fill con slippage adicional dependiente de spread, rango y participación sobre volumen.

Si una estrategia solo funciona en el modelo idealista, no vale.

### 10) Definir tus costes “de verdad”
Modelar comisión, SEC/FINRA, spread y slippage dinámico. Limita tu participación al volumen real de la barra para evitar resultados basados en tamaños de posición que el mercado no podría absorber.

No uses una comisión plana y ya. Para microcaps, como mínimo modela:

* comisión,
* SEC/FINRA si aplica a tu broker/mercado,
* spread,
* slippage,
* y restricción por liquidez.

Regla sana: limita tu participación, por ejemplo, a un % pequeño del volumen de la barra o del minuto. Si tu estrategia gana solo metiendo un tamaño irreal en acciones ilíquidas, el edge es falso.

### 11) Elegir el framework adecuado para la fase inicial

Si vienes de TradeStation, la ruta más amigable es:

* **Fase A (Research):** `backtesting.py` para codificar 1 setup y optimizar parámetros con algo parecido a TS.
* **Fase B (Certificación):** 
    * `vectorbt` para lanzar grids masivos sobre miles de días, tickers y parámetros. lanzamientos masivos y encontrar el Alpha rápido (Filtro grueso
    * motor propio si necesitas reglas de fill muy específicas, múltiples entradas, parciales, SSR, halts, etc. Un Motor de Eventos propio que procese tick-a-tick con tus datos de Quotes C+D para validar la ejecución real antes de dar por buena una estrategia.

`backtesting.py` documenta explícitamente `Backtest.optimize()`, y `vectorbt` está centrado en portafolios desde señales con mucha velocidad por Numba. ([kernc.github.io][3])

### 12) Reproducir tu flujo mental de TradeStation

Tu flujo actual en TS es:

1. parametrizas,
2. generas resultados,
3. exportas,
4. buscas estabilidad,
5. eliges parámetros robustos.

Eso mismo en Python debe quedar así:

1. defines una malla de parámetros,
2. ejecutas un grid search,
3. guardas todos los resultados por combinación,
4. rankeas no por mejor PnL, sino por robustez,
5. haces walk-forward,
6. haces tests de sensibilidad y degradación.

No busques el “best Sharpe” absoluto. Busca **mesetas estables**. Si mover un parámetro de 9 a 10 destruye la curva, no hay robustez.

### 13) Optimizar por bloques, no sobre toda la historia

No optimices 2005–2026 entero de una vez. Hazlo por ventanas.

Una estructura razonable para tu estilo sería:

* **in-sample:** 2–4 años,
* **out-of-sample:** 6–12 meses,
* roll forward,
* reoptimizas,
* concatenas todos los OOS.

Eso es walk-forward analysis, y precisamente se usa para reducir el sobreajuste de optimizar una sola vez sobre toda la historia. ([Interactive Brokers][6])

### 14) Medir robustez de verdad

No te quedes con el PnL. Implementa CPCV (Combinatorial Purged Cross-Validation) para validar la estrategia en múltiples combinaciones de tiempo sin fugas de información. Añade pruebas de "Ruido" (Perturbation) retrasando artificialmente las entradas para ver si la estrategia sobrevive a la latencia real.

Cuando termines una optimización, no te quedes con “ha ganado dinero”. Haz estas pruebas:

* **Sensitivity map**: heatmap de parámetros.
* **IS vs OOS decay**: cuánto se degrada del in-sample al out-of-sample.
* **Subperiod analysis**: bull, bear, 2020, 2021 meme era, 2022–2023 sequía, 2024–2026.
* **By regime**: low float, higher float, biotech, China, reverse split, ex-news, no-news.
* **By time-of-day**: open, post-open, midday, power hour.
* **By liquidity**: spread estrecho vs ancho, PM volume alto vs bajo.
* **Perturbation**: añadir slippage extra, retrasar una barra la entrada, empeorar el fill.

Si la estrategia se rompe al mínimo cambio, no la promociones.

### 15) Construir un reporting estándar

Genera siempre analíticas detalladas:

* MAE/MFE: ¿Cuánto sufrió el trade antes de ganar?
* Análisis de Capacidad: ¿A partir de qué capital (ej. 500k) el slippage destruye el edge?
* Decaimiento de Alpha: ¿Funciona igual la estrategia a las 10:00 que a las 15:00?

Debes generar siempre el mismo pack de resultados:

* equity curve,
* drawdown curve,
* distribución de retornos por trade,
* % win,
* payoff ratio,
* expectancy,
* max adverse excursion,
* max favorable excursion,
* profit factor,
* Sharpe/Sortino si quieres,
* trades por año,
* resultados por ticker,
* resultados por setup,
* resultados por régimen.

Y, sobre todo, una tabla por combinación de parámetros con:

* IS metric,
* OOS metric,
* número de trades,
* estabilidad local,
* degradación,
* score final de robustez.

### 16) Hacer una capa de “event labeling”
Identifica "eventos de despertar" (Gap, RVOL, noticias). Esto te permite segmentar el comportamiento de las Micro Caps por regímenes (Low float vs High float).

Dado tu nicho, una de las piezas más potentes será una tabla de **eventos de despertar**:

* gap > x,
* RVOL > y,
* primer día con > z dollar volume tras 20 días muertos,
* close near HOD,
* reclaim de niveles,
* SSR day,
* reverse split reciente,
* news filing reciente.

Eso te permite filtrar el universo por “compañías normalmente muertas que activan comportamiento de atención/volumen”.

### 17) Añadir noticias y filings solo cuando el motor básico ya funcione

Usa los flags de news/8-K una vez que el motor básico funcione. Esto refinará tu Screener de la Capa 1.

Massive también ofrece noticias y textos de 8-K/10-K indexados. Úsalo después, no antes. Primero prueba si el edge existe solo con precio/volumen/liquidez. Si luego añades `news_flag`, `offering_flag`, `8k_flag`, `reverse_split_flag`, ya estarás haciendo una versión mucho más potente del screener discrecional. ([Massive][4])

### 18) Validar contra el “chart reality check”

Comprueba manualmente 30 trades. Si el gráfico no coincide con la lógica de tu código o el fill es irreal, el sistema tiene un bug conceptual.

Antes de creer cualquier resultado:

* coge 30 trades aleatorios,
* abre el gráfico,
* comprueba que la señal que tu código detectó es realmente el patrón que tú operas,
* revisa si el fill asumido es creíble.

Este paso parece “manual”, pero te ahorra meses de basura.

### 19) Crear una versión paper/live-ready

Compara el paper trading contra el backtest. No busques si gana; busca si los fills y el deslizamiento se parecen a lo simulado.

Cuando el backtest sea robusto, no pases a real directamente. Haz:

* **paper forward test**,
* mismas reglas,
* mismo selector,
* mismo sizing,
* mismo modelo horario,
* compara paper vs backtest.

La pregunta no es si gana; es si **se parece** a lo que el backtest prometía.

### 20) Mantener versionado

Versiona el dataset (ej. v2_audit_passed), el selector y el motor de ejecución. Sin esto, no podrás replicar científicamente tus éxitos pasados.

Cada estrategia debe tener:

* versión del dataset,
* versión del selector,
* versión del ejecutor,
* versión del modelo de costes,
* versión del grid,
* y fecha del último walk-forward.

Si no versionas, luego no sabrás por qué una curva cambió.

# La arquitectura institucional resumida

Tu trabajo real es construir este embudo de 6 capas:

* **Capa 1 (Screener)**: DuckDB filtra terabytes de Parquet usando tu auditoría.
* **Capa 2 (Broker)**: Inyecta datos de NBBO reconstruidos de Quotes C+D.
* **Capa 3 (Alpha)**: Lógica pura de la estrategia (como en TradeStation).
* **Capa 4 (Execution)**: Simulador de eventos con Halts, Slippage y Short Borrow.
* **Capa 5 (Robustez)**: Validación CPCV y Walk-Forward avanzada.
* **Capa 6 (Reporting)**: Informes MAE/MFE y análisis de capacidad de capital.

**El mayor peligro en tu nicho es hacer backtests preciosos pero falsos**. Integrando la auditoría de datos y la microestructura del spread, estarás construyendo un sistema de nivel Hedge Fund.

## Qué debes leer / mirar primero

Para construir bien la parte metodológica, yo empezaría por estos tres textos:

* **Robert Carver, *Systematic Trading***: muy bueno para pensar en sistema, proceso, riesgo y robustez. ([harriman-house.com][7]) https://github.com/pst-group/pysystemtrade 
* **Ernest Chan, *Quantitative Trading* / *Algorithmic Trading***: muy útil para el paso de idea a investigación sistemática y para trampas prácticas de backtesting. ([wiley.com][8])
* **Marcos López de Prado, *Advances in Financial Machine Learning***: especialmente por la parte de backtesting, overfitting y validación fuera de muestra. ([wiley.com][9])

Y para la parte operativa:

* Docs de **Massive/Polygon** para datos y corporate actions. ([Massive][4])
* Docs de **backtesting.py** para una primera réplica “tipo TradeStation”. ([kernc.github.io][3])
* Docs de **vectorbt** para barridos grandes de parámetros y cestas. ([vectorbt.dev][10])
* **IBKR Campus** para encajar bien el walk-forward. ([Interactive Brokers][6])

## La idea clave

Tu trabajo real no es “programar una estrategia”. Es construir este embudo:

**raw market data → universo histórico correcto → eventos/labels → señales → simulación realista → optimización → walk-forward → robustez → paper/live**

Si montas bien ese embudo una vez, luego podrás enchufar dentro cualquier setup de small caps.

El mayor peligro en tu nicho no es el código: es **hacer backtests preciosos pero falsos** por survivorship bias, splits mal tratados, ticker changes, spreads ignorados y fills irreales. Ahí es donde se gana o se pierde el proyecto. ([Massive][11])

Puedo convertirte todo esto en un **plan técnico ejecutable de 30 días**, con stack exacto, estructura de carpetas, tablas, y qué programar primero cada semana.

[1]: https://massive.com/docs/rest/stocks/aggregates/custom-bars?utm_source=chatgpt.com "Custom Bars (OHLC) | Stocks REST API"
[2]: https://duckdb.org/docs/stable/guides/file_formats/query_parquet.html?utm_source=chatgpt.com "Querying Parquet Files"
[3]: https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html?utm_source=chatgpt.com "backtesting.backtesting API documentation"
[4]: https://massive.com/docs/rest/stocks/llms.txt?ref=massive.com "massive.com"
[5]: https://massive.com/docs/rest/stocks/trades-quotes/quotes?utm_source=chatgpt.com "Quotes | Stocks REST API"
[6]: https://www.interactivebrokers.com/campus/ibkr-quant-news/the-future-of-backtesting-a-deep-dive-into-walk-forward-analysis/?utm_source=chatgpt.com "The Future of Backtesting: A Deep Dive into Walk Forward ..."
[7]: https://harriman-house.com/authors/robert-carver/systematic-trading/9780857194459?utm_source=chatgpt.com "Systematic Trading by Robert Carver"
[8]: https://www.wiley.com/en-us/Quantitative%2BTrading%3A%2BHow%2Bto%2BBuild%2BYour%2BOwn%2BAlgorithmic%2BTrading%2BBusiness%2C%2B2nd%2BEdition-p-9781119800064?utm_source=chatgpt.com "Quantitative Trading: How to Build Your Own Algorithmic ..."
[9]: https://www.wiley.com/en-us/Advances%2Bin%2BFinancial%2BMachine%2BLearning-p-9781119482086?utm_source=chatgpt.com "Advances in Financial Machine Learning"
[10]: https://vectorbt.dev/api/portfolio/base/?utm_source=chatgpt.com "base"
[11]: https://massive.com/docs/rest/stocks/corporate-actions/ticker-events?utm_source=chatgpt.com "Ticker Events | Stocks REST API"


