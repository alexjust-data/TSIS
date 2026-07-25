# Source Map - Trading Systems and Methods - Perry J. Kaufman

Mapa inverso para agentes: que extraer de Kaufman y donde encaja en TSIS.

## Menu

- [Ficha](#ficha)
- [Nota de extraccion](#nota-de-extraccion)
- [Fuente por bloque](#fuente-por-bloque)
- [Mapa arquitectura TSIS](#mapa-arquitectura-tsis)
- [Preguntas que esta fuente responde](#preguntas-que-esta-fuente-responde)
- [Preguntas que no responde](#preguntas-que-no-responde)
- [Prioridad de lectura](#prioridad-de-lectura)

## Ficha

| Campo | Valor |
|---|---|
| Book ID | `trading_systems_methods_kaufman` |
| Titulo | `Trading Systems and Methods` |
| Autor | `Perry J. Kaufman` |
| Formato local | DjVu con extension `.pdf` |
| Paginas DjVu | 621 |
| Chunks de texto extraidos | 600 |
| Palabras OCR aprox. | 271972 |
| Tipo de fuente | Enciclopedia de sistemas, testing y riesgo |
| Estado | Extraido e indexado |

## Nota de extraccion

El archivo:

```text
C:\TSIS_Data\00_CTO\99_REFERENCE_LIBRARY\00_BIBLIOTECA\Trading_Systems_and_Methods_-_Perry_J_Kaufman.pdf
```

no es un PDF real. La cabecera interna es DjVu (`AT&TFORM...DJVM`). Se uso `djvutxt.exe` de DjVuLibre extraido localmente desde el paquete Chocolatey para obtener texto OCR.

El OCR contiene ruido y errores menores en algunas palabras, por lo que los agentes deben usar este resumen e indice como mapa rapido, y acudir a la fuente local cuando necesiten verificar un detalle de formula o regla.

## Fuente por bloque

| Bloque del libro | Extraer | Encaje TSIS |
|---|---|---|
| Caps. 1-4 | Conceptos, datos, distribucion, regresion, tendencias | `ResearchFoundation`, `FeaturePipeline` |
| Caps. 5-13 | Familias clasicas de sistemas | `StrategyTemplateRegistry` |
| Caps. 14-16 | Eventos, comportamiento, patrones intradia, day trading | `EventState`, `MarketReplay`, `IntradayStrategyLibrary` |
| Caps. 17-20 | Adaptacion, volatilidad, multiples timeframes, advanced methods | `AdaptiveParameterPolicy`, `RegimeModel`, `VolatilityModel` |
| Cap. 21 | Testing, parametros, in/out-of-sample, robustez | `ExperimentControl`, `OptimizationAudit`, `WalkForwardValidation` |
| Cap. 22 | Price shocks, runs, trade-offs, computer use | `StressTesting`, `RobustnessReview`, `LiveReadiness` |
| Cap. 23 | Liquidez, leverage, diversification, trade risk, ruin | `RiskEngine`, `ExecutionRealismGate`, `PortfolioRisk` |

## Mapa arquitectura TSIS

```text
Kaufman
    |
    +-- Taxonomia de sistemas
    |       -> trend
    |       -> breakout
    |       -> momentum
    |       -> oscillator
    |       -> seasonality
    |       -> pattern/event
    |       -> spread/arbitrage
    |
    +-- Contrato de parametros
    |       -> continuous
    |       -> discrete
    |       -> coded/regime
    |       -> spacing policy
    |
    +-- Testing
    |       -> objective
    |       -> expected profile
    |       -> optimization map
    |       -> walk-forward
    |       -> out-of-sample
    |       -> overoptimization warning
    |
    +-- Realismo operativo
    |       -> costs
    |       -> slippage
    |       -> liquidity
    |       -> price shocks
    |
    +-- Riesgo
            -> leverage
            -> diversification
            -> trade risk
            -> ruin probability
            -> equity cycle monitoring
```

## Preguntas que esta fuente responde

- Que familias clasicas de sistemas existen y como se diferencian.
- Como convertir un indicador o patron en reglas testeables.
- Como definir parametros y espacios de busqueda.
- Por que el mejor resultado puntual de una optimizacion no es suficiente.
- Como mirar superficies de parametros y robustez.
- Como separar in-sample y out-of-sample.
- Por que price shocks distorsionan backtests.
- Como pensar en costes, liquidez, leverage y riesgo de ruina.
- Que perfiles de P&L esperar de trend following, countertrend o breakout.

## Preguntas que no responde

- Como implementar un motor event-driven profesional en Python.
- Como disenar message bus, event queue, OMS o broker adapter.
- Como persistir snapshots en Parquet.
- Como crear una arquitectura online/historical con la misma semantica.
- Como modelar small caps con quotes, halts, borrow y partial fills de forma moderna.
- Como aplicar PBO/DSR formalmente.

## Prioridad de lectura

Para TSIS, orden recomendado:

1. Capitulo 21 completo: testing, parametros, robustez y overoptimization.
2. Capitulo 23 completo: riesgo, liquidez, leverage y ruin.
3. Capitulo 22: practical considerations, price shocks y trade-offs.
4. Capitulo 16: day trading, costes y liquidez intradia.
5. Capitulos 5-6: trend/momentum como estrategias benchmark.
6. Capitulos 14-15: eventos, gaps y patrones si el agente trabaja con scanners.
7. Capitulos 17-20 solo cuando se trabaje adaptacion, volatilidad o modelos avanzados.

Kaufman debe vivir en TSIS como biblioteca de diseno de estrategias y validacion practica. La arquitectura del motor debe venir de NautilusTrader, LEAN y QuantStart.
