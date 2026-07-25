# Trading Systems and Methods - Perry J. Kaufman

Resumen operativo para agentes TSIS.

## Menu

- [Resumen ejecutivo](#resumen-ejecutivo)
- [Rol dentro de TSIS](#rol-dentro-de-tsis)
- [Mapa rapido de capitulos](#mapa-rapido-de-capitulos)
- [Bloque A - Fundamentos cuantitativos](#bloque-a---fundamentos-cuantitativos)
- [Bloque B - Familias clasicas de sistemas](#bloque-b---familias-clasicas-de-sistemas)
- [Bloque C - Patrones, eventos e intradia](#bloque-c---patrones-eventos-e-intradia)
- [Bloque D - Adaptacion, volatilidad y multiples timeframes](#bloque-d---adaptacion-volatilidad-y-multiples-timeframes)
- [Bloque E - Testing, optimizacion y robustez](#bloque-e---testing-optimizacion-y-robustez)
- [Bloque F - Consideraciones practicas y riesgo](#bloque-f---consideraciones-practicas-y-riesgo)
- [Blueprint TSIS derivado](#blueprint-tsis-derivado)
- [Quality gates para agentes](#quality-gates-para-agentes)
- [Limitaciones](#limitaciones)

## Resumen ejecutivo

Kaufman es una enciclopedia de sistemas de trading. No es el primer manual para implementar un motor event-driven, pero si es una referencia muy fuerte para responder:

```text
Que familias de reglas existen?
Que supuestos hacen?
Como se parametrizan?
Como se prueban?
Como se rompen por costes, liquidez, shocks y sobreoptimizacion?
```

Para TSIS, el valor no esta en copiar todas las tecnicas, sino en usar el libro como catalogo de modelos y como fuente de criterios de validacion. Su parte mas importante para backtesting profesional son los capitulos 21, 22 y 23: testing, practical considerations y risk control.

El archivo local tiene extension `.pdf`, pero internamente es DjVu. Fue procesado con `djvutxt` de DjVuLibre extraido localmente; el texto OCR tiene ruido, pero es suficiente para mapa, resumen e indice conceptual.

## Rol dentro de TSIS

Encaja en estas capas:

```text
Strategy Library
    -> Indicator definitions
    -> Rule templates
    -> Parameter spaces
    -> Testing protocol
    -> Robustness review
    -> Cost/liquidity/risk assumptions
```

No debe usarse para:

- definir el contrato event-driven del motor;
- disenar el OMS;
- modelar fills de small caps;
- sustituir NautilusTrader, LEAN o QuantStart en arquitectura;
- sustituir Lopez de Prado, PBO o DSR en validacion estadistica moderna.

Si un agente trabaja en `TSIS_BACKTEST_ENGINE_ARCHITECTURE_V0_1`, Kaufman debe entrar como fuente de reglas, parametros, testing y riesgo, no como esqueleto del motor.

## Mapa rapido de capitulos

| Capitulo | Pagina impresa aprox. | Uso TSIS |
|---|---:|---|
| 1. Introduction | 1 | Premisa: primero idea, despues herramienta |
| 2. Basic Concepts | 9 | Datos, distribucion, dispersion, probabilidad, supply/demand |
| 3. Regression Analysis | 30 | Regresion, correlacion, modelos explicativos |
| 4. Trend Calculations | 62 | Moving averages, smoothing, lag/lead, ruido |
| 5. Trend Systems | 89 | Reglas de tendencia, breakouts, sistemas comparables |
| 6. Momentum and Oscillators | 126 | ROC, osciladores, divergencias, volumen |
| 7. Seasonality | 160 | Patrones estacionales y filtros |
| 8. Cycle Analysis | 189 | Ciclos, detrending, spectral/Fourier |
| 9. Charting | 213 | Patrones visuales, gaps, reversals, objetivos |
| 10. Volume, Open Interest, and Breadth | 237 | Confirmacion por volumen, amplitud, patrones intradia |
| 11. Point-and-Figure Charting | 256 | Box size, reversals, sensibilidad, riesgo |
| 12. Charting Systems | 281 | Sistemas basados en charting, breakouts, canales |
| 13. Spreads and Arbitrage | 305 | Spreads, arbitraje, carrying charges, leverage |
| 14. Behavioral Techniques | 334 | News, event trading, COT, opinion, comportamiento |
| 15. Pattern Recognition | 382 | Gaps, hora del dia, patrones semanales, IA |
| 16. Day Trading | 419 | Costes, liquidez, opening range, intradia |
| 17. Adaptive Techniques | 436 | Parametros que cambian con condiciones de mercado |
| 18. Price Distribution Systems | 449 | Desviacion estandar, distribucion, Market Profile |
| 19. Multiple Time Frames | 465 | Confirmacion entre marcos temporales |
| 20. Advanced Techniques | 471 | Volatilidad, fuzzy logic, fractals, NN, GA |
| 21. Testing | 503 | Objetivos, parametros, in/out-of-sample, robustez |
| 22. Practical Considerations | 555 | Computer use, price shocks, runs, trade-offs |
| 23. Risk Control | 587 | Liquidez, leverage, diversificacion, trade risk, ruin |

## Bloque A - Fundamentos cuantitativos

Capitulos 1-4.

La idea mas importante es metodologica: no se empieza por elegir indicador. Se empieza por saber que fenomeno se quiere extraer del mercado y despues se elige la herramienta.

Para TSIS esto se traduce en:

```text
hypothesis_id
    -> observable phenomenon
    -> feature definition
    -> decision rule
    -> expected trading profile
```

Los capitulos iniciales cubren medias, distribuciones, desviacion, skewness, probabilidad, supply/demand, regresion y trend calculations. Son utiles para agentes que tengan que implementar indicadores o features, porque obligan a entender que mide cada transformacion.

Regla practica para agentes:

```text
No implementar un indicador si no queda claro que propiedad del mercado pretende medir.
```

## Bloque B - Familias clasicas de sistemas

Capitulos 5-13.

Kaufman organiza muchas familias clasicas:

- trend following;
- moving-average systems;
- breakouts;
- momentum;
- oscillators;
- seasonality;
- cycles;
- charting systems;
- point-and-figure;
- spreads;
- arbitrage.

Para TSIS, este bloque sirve como catalogo de `StrategyTemplate`, no como lista de estrategias listas para operar.

Ejemplo de contrato para una plantilla:

```text
strategy_family
indicator_set
entry_rule
exit_rule
position_state
parameter_space
expected_profile
failure_modes
cost_sensitivity
liquidity_sensitivity
```

La leccion constante es que sistemas distintos tienen perfiles distintos. Un trend follower suele tener muchas perdidas pequenas y pocas ganancias grandes; un countertrend puede tener muchas ganancias pequenas y pocas perdidas grandes. TSIS debe medir ese perfil, no solo P&L final.

## Bloque C - Patrones, eventos e intradia

Capitulos 14-16.

Estos capitulos son relevantes para small caps porque conectan mercado, eventos y comportamiento:

- measuring the news;
- event trading;
- commitment of traders;
- opinion/contrary opinion;
- gaps;
- time-of-day patterns;
- opening gaps;
- intraday patterns;
- day trading;
- opening range breakout.

Para TSIS esto refuerza:

```text
EventStateSnapshot
MarketStateSnapshot
DecisionRecord
market replay
intraday liquidity checks
```

Un gap, una noticia, una aparicion en scanner o una ruptura de rango no deben ser solo columnas finales. Deben convertirse en eventos con:

```text
detected_at
observable_inputs
event_state
decision_time
order_time
fill_time
```

Day trading tiene una advertencia crucial: los costes y la liquidez pesan mucho mas cuando el objetivo por trade es pequeno. Para small caps, esto debe ser obligatorio desde v0.1 de cualquier simulacion intradia.

## Bloque D - Adaptacion, volatilidad y multiples timeframes

Capitulos 17-20.

Kaufman trata sistemas adaptativos, distribuciones de precios, multiples time frames, volatilidad y tecnicas avanzadas como neural networks y genetic algorithms.

La leccion practica no es "usa metodos complejos", sino:

- el mercado cambia de volatilidad y regimen;
- un parametro fijo puede funcionar en una zona y fallar en otra;
- adaptar parametros puede mejorar robustez, pero tambien aumenta el riesgo de sobreajuste;
- multiples timeframes no son equivalentes a medias de diferente longitud sobre el mismo timeframe;
- feedback entre entrenamiento y tuning puede contaminar el verdadero out-of-sample.

Para TSIS:

```text
adaptive_parameter = model output
```

no debe ser tratado como constante oculta. Debe quedar registrado en snapshots y ledgers.

## Bloque E - Testing, optimizacion y robustez

Capitulo 21.

Este es el bloque mas importante para arquitectura de backtesting.

Kaufman insiste en que los ordenadores hicieron muy facil probar miles de variantes y muy facil enganarse. La optimizacion no debe sustituir la seleccion logica. Antes de probar hay que definir:

```text
objective
expected profile
parameters
parameter ranges
test data
cost assumptions
success criteria
```

Ideas clave:

- Testing valida una idea definida previamente.
- Sin expectativas previas no hay confirmacion; solo busqueda retrospectiva.
- El criterio de optimizacion no puede ser solo max net profit.
- Los parametros deben clasificarse: continuos, discretos o codificados.
- En grids, los valores deben espaciarse con criterio; probar 1, 2, 3 dias no equivale a probar 48, 49, 50 dias.
- Hay que visualizar mapas de resultados, no solo el mejor punto.
- La robustez se ve en mesetas, no en picos aislados.
- In-sample y out-of-sample deben separarse.
- Step-forward testing es mas realista que seleccionar una vez y extrapolar.
- Cambiar reglas tras ver resultados convierte validacion en entrenamiento.
- Un solo caso famoso no prueba un sistema.
- Price shocks pueden inflar o falsear resultados.
- Data mining y overoptimization son riesgos centrales.

Traduccion directa a TSIS:

```text
variant_count
parameter_grid_id
objective_function_id
in_sample_range
out_of_sample_range
walk_forward_scheme_id
selected_variant_id
selection_reason
robustness_surface_path
```

Este capitulo conecta con Pardo y con Lopez de Prado, aunque con lenguaje menos moderno.

## Bloque F - Consideraciones practicas y riesgo

Capitulos 22-23.

Kaufman baja la teoria a restricciones reales:

- uso y abuso del ordenador;
- calidad y disponibilidad de datos;
- price shocks;
- teoria de runs;
- selective trading;
- trade-offs entre sistemas;
- trading limits;
- similitud entre sistemas;
- liquidez;
- leverage;
- diversificacion;
- riesgo por trade;
- probabilidad de ruina;
- compounding;
- equity cycles.

Para small caps, el punto mas importante es liquidez:

```text
un mercado liquido no garantiza buenos fills;
un mercado iliquido casi garantiza malos fills.
```

Esto implica que TSIS no debe aceptar un backtest intradia sin:

```text
spread
volume filter
participation cap
slippage model
commission model
halt/limit/stale data checks
```

En riesgo, Kaufman insiste en que el sistema por si solo no asegura supervivencia. La cuenta, el tamano de posicion, la diversificacion y la secuencia de perdidas importan tanto como la regla de entrada.

## Blueprint TSIS derivado

Kaufman aporta sobre todo a estas piezas:

```text
StrategyTemplateRegistry
    -> trend
    -> breakout
    -> momentum
    -> oscillator
    -> seasonality
    -> pattern/event
    -> spread/arbitrage

ParameterSpaceRegistry
    -> continuous parameters
    -> discrete parameters
    -> coded/regime parameters
    -> spacing policy

BacktestExperimentControl
    -> objective
    -> expected profile
    -> train/validation/test ranges
    -> variant count
    -> optimization surface

ExecutionRealismGate
    -> costs
    -> slippage
    -> liquidity
    -> day-trading feasibility

RiskControl
    -> trade risk
    -> leverage
    -> diversification
    -> ruin probability
    -> equity cycle monitoring
```

## Quality gates para agentes

Antes de aceptar un modulo inspirado en Kaufman:

- Debe declarar la familia de sistema.
- Debe declarar el fenomeno que intenta capturar.
- Debe separar indicador, regla, sizing y ejecucion.
- Debe declarar parametros y rangos antes del test.
- Debe registrar el numero de variantes.
- Debe usar costes y slippage si hay P&L operativo.
- Debe mostrar superficie o estabilidad de parametros, no solo el maximo.
- Debe tener out-of-sample real o walk-forward.
- Debe medir trade profile: win rate, avg win/loss, drawdown, streaks, turnover, exposure.
- Debe revisar sensibilidad a price shocks.
- Debe revisar liquidez si el horizonte es intradia o el universo es small caps.
- Debe registrar si una regla fue cambiada despues de ver resultados.

## Limitaciones

Kaufman es amplio, pero no moderno en todas sus herramientas. Muchas secciones preceden a la infraestructura actual de datos, Python, Parquet, event sourcing, APIs de brokers, ML moderno y validacion tipo PBO/DSR.

Su uso correcto en TSIS es como fuente de:

- taxonomia de sistemas;
- diseno de pruebas;
- riesgos de optimizacion;
- perfiles de performance;
- consideraciones practicas;
- riesgo y liquidez.

No debe ser la fuente principal para construir el motor event-driven.

