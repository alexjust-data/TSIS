# Trading Systems, 2nd Edition - Urban Jaekle and Emilio Tomasini

Resumen operativo para agentes TSIS.

## Menu

- [Resumen ejecutivo](#resumen-ejecutivo)
- [Rol dentro de TSIS](#rol-dentro-de-tsis)
- [Mapa rapido de capitulos](#mapa-rapido-de-capitulos)
- [Bloque A - Desarrollo y evaluacion de sistemas](#bloque-a---desarrollo-y-evaluacion-de-sistemas)
- [Bloque B - Caso LUXOR](#bloque-b---caso-luxor)
- [Bloque C - Robustez, Monte Carlo y WFA](#bloque-c---robustez-monte-carlo-y-wfa)
- [Bloque D - Position sizing y portfolio](#bloque-d---position-sizing-y-portfolio)
- [Bloque E - Portfolio de acciones y survivorship](#bloque-e---portfolio-de-acciones-y-survivorship)
- [Blueprint TSIS derivado](#blueprint-tsis-derivado)
- [Quality gates para agentes](#quality-gates-para-agentes)
- [Limitaciones](#limitaciones)

## Resumen ejecutivo

Este libro es una referencia practica de desarrollo de sistemas: idea, codigo, datos, costes, optimizacion, estabilidad de parametros, exits, MAE/MFE, Monte Carlo, walk-forward, position sizing y portfolio.

Para TSIS es especialmente util porque ensena un flujo de construccion real:

```text
idea -> reglas -> backtest con costes -> estabilidad parametrica -> exits -> MAE/MFE -> Monte Carlo -> WFA -> sizing -> portfolio
```

No es un manual de arquitectura event-driven en Python. Su valor esta en el proceso de investigacion y evaluacion de estrategias, no en el diseno de `EventLoop`, `OMS` o `BrokerAdapter`.

## Rol dentro de TSIS

Encaja en:

```text
ResearchGovernance
StrategyDevelopmentWorkflow
OptimizationAudit
RobustnessAnalyzer
MAE_MFE_Analyzer
WalkForwardRunner
PositionSizing
PortfolioConstruction
DataQualityGate
SurvivorshipBiasGuard
```

Usarlo cuando un agente necesite:

- definir un proceso paso a paso para convertir una idea en sistema;
- evaluar estabilidad de parametros por mapas;
- decidir si una optimizacion es una meseta o un pico;
- analizar exits con MAE/MFE;
- comparar resultados antes/despues de costes;
- revisar sample size y estructura de mercado para WFA;
- construir portfolio dinamico y tratar correlaciones entre equity lines;
- recordar que universo, datos y survivorship cambian totalmente el resultado.

## Mapa rapido de capitulos

| Capitulo | Uso TSIS |
|---|---|
| 1. What is a Trading System? | Definicion de sistema como reglas sin discrecionalidad |
| 2. Design, Test, Optimisation and Evaluation | Datos, complejidad, walk-forward, robustez, metricas |
| 3. Step-by-step LUXOR | Caso practico: costes, parametros, exits, MAE/MFE |
| 4. Predictive Power | Timescale analysis y Monte Carlo |
| 5. Factors Around Your System | Long/short bias, OOS deterioration, data bias, over-fitting |
| 6. Periodic Reoptimisation and WFA | Anchored/rolling WFA, sample size, market structure |
| 7. Position Sizing Example | Max drawdown MM, fixed fractional, fixed ratio, Monte Carlo |
| 8. Dynamic Portfolio Construction | Correlaciones, equity-line crossover, dynamic composition |
| 9. Trading a Portfolio of Stocks | Survivorship, S&P 500/Nasdaq universes, ranking, execution |
| Appendices | Bollinger, Triangle, LUXOR, EasyLanguage/AmiBroker code |

## Bloque A - Desarrollo y evaluacion de sistemas

El libro insiste en que un sistema comienza con una idea y debe convertirse en reglas programables. La estructura minima del sistema es:

```text
entry formula
exit formula
money management formula
```

Para TSIS esto se traduce en separar:

```text
EntryRule
ExitPolicy
RiskModel
SizingModel
CostModel
ExperimentConfig
```

El capitulo 2 dedica bastante peso a datos: cierres inconsistentes, aperturas de subasta, sesiones raras, contratos continuos y splits/delistings. Para small caps esto refuerza que `DataFoundation` no puede ser un detalle posterior.

## Bloque B - Caso LUXOR

El caso LUXOR es una vertical slice pedagogica completa.

Secuencia:

```text
moving-average entry
backtest sin costes
backtest con slippage/commissions
optimization/stability diagrams
intraday time filter
MAE para stop
MFE para trailing/profit target
scatter de trades
preparacion para money management
```

La idea mas valiosa para TSIS es que un backtest profesional debe permitir ver como cada cambio transforma la distribucion de trades. No basta con comparar net profit final.

Artifacts TSIS derivados:

```text
TradeDistributionReport
MAE_MFE_Report
ExitImpactReport
CostImpactReport
ParameterStabilityMap
```

## Bloque C - Robustez, Monte Carlo y WFA

El libro trata tres pruebas practicas:

```text
timescale analysis
Monte Carlo
walk-forward analysis
```

Timescale analysis no es una validacion cientifica perfecta, pero sirve como stress de la logica de una estrategia: si una regla solo vive en una compresion exacta de barras, probablemente es fragil.

Monte Carlo se usa para alterar la secuencia de trades y estimar distribuciones posibles de drawdown y resultados. Es una capa de riesgo, no una prueba de edge.

WFA se presenta en forma anchored y rolling. La idea clave para TSIS:

```text
La ventana IS/OOS debe depender de sample size, estructura de mercado, numero de parametros y frecuencia del sistema.
```

## Bloque D - Position sizing y portfolio

El libro separa risk management y money management:

```text
risk management = cuanto se puede perder y como se controla
money management = cuanto se invierte en cada trade
```

El caso de position sizing compara:

- trading con un lote;
- maximum drawdown money management;
- fixed fractional;
- fixed ratio;
- Monte Carlo aplicado al sistema position-sized.

Para TSIS, esta capa debe vivir despues de tener una distribucion de trades creible. No debe usarse para maquillar una estrategia sin edge.

## Bloque E - Portfolio de acciones y survivorship

El capitulo 9 es muy relevante para TSIS porque trata:

- modificaciones al aplicar sistemas a acciones;
- survivorship bias;
- portfolio S&P 500;
- market filter;
- optimizacion conjunta de filtro y longitud de Bollinger;
- ranking cuando hay mas senales que capital;
- Monte Carlo y WFA del portfolio;
- position management con numero maximo de stocks;
- ejecucion diaria.

Para small caps, la leccion es directa:

```text
universe definition + survivorship-free data + liquidity filters + ranking policy + capacity
```

deben ser parte del backtest, no notas manuales.

## Blueprint TSIS derivado

```text
StrategyDevelopmentWorkflow
    -> IdeaSpec
    -> StrategyRules
    -> CostedBacktest
    -> ParameterStabilityMap
    -> ExitDiagnostics
    -> RobustnessSuite
    -> WalkForwardSuite
    -> PositionSizingSuite
    -> PortfolioSuite
    -> LiveExecutionPlan
```

## Quality gates para agentes

- No aceptar un resultado sin costes.
- No aceptar una optimizacion con pico aislado si no hay meseta estable.
- Registrar numero de parametros y grados de libertad.
- Separar entry logic, exits, risk y sizing.
- Revisar MAE/MFE antes de elegir stops o targets.
- Ejecutar Monte Carlo sobre trades ya generados correctamente.
- Documentar si WFA es anchored o rolling.
- Para acciones, exigir universo historico y control de survivorship.
- No usar ranking de senales sin declarar la politica de desempate.

## Limitaciones

- No define una arquitectura event-driven moderna.
- No cubre Python, Parquet, DuckDB o Polars.
- No resuelve order lifecycle profesional ni partial fills.
- No modela small caps con halts, quotes, borrow o DAS.
- La validacion estadistica no reemplaza Pardo, Lopez de Prado, PBO o DSR.
