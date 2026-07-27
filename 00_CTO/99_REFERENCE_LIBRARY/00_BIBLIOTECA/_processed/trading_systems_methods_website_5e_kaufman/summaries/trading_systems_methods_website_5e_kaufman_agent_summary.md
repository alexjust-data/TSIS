# Trading Systems and Methods, 5th Edition + Website - Perry J. Kaufman

Resumen operativo para agentes TSIS.

## Menu

- [Resumen ejecutivo](#resumen-ejecutivo)
- [Rol dentro de TSIS](#rol-dentro-de-tsis)
- [Mapa rapido de capitulos](#mapa-rapido-de-capitulos)
- [Bloque A - Filosofia de sistema](#bloque-a---filosofia-de-sistema)
- [Bloque B - Familias de estrategias](#bloque-b---familias-de-estrategias)
- [Bloque C - Testing y robustez](#bloque-c---testing-y-robustez)
- [Bloque D - Practical considerations](#bloque-d---practical-considerations)
- [Bloque E - Risk control](#bloque-e---risk-control)
- [Blueprint TSIS derivado](#blueprint-tsis-derivado)
- [Quality gates para agentes](#quality-gates-para-agentes)
- [Relacion con entrada Kaufman anterior](#relacion-con-entrada-kaufman-anterior)

## Resumen ejecutivo

Esta fuente es una edicion completa y trazable de Kaufman. La entrada antigua `trading_systems_methods_kaufman` se conserva, pero esta version tiene PDF real, 1232 paginas, TOC amplio y texto extraido sin OCR.

Kaufman es la enciclopedia practica de familias de sistemas, parametros, test design, robustness, transaction costs, price shocks, risk control y portfolio. No es el manual del event loop, pero es una fuente fuerte para:

```text
StrategyPatternLibrary + ParameterSchema + RobustnessAnalyzer + RiskControl
```

## Rol dentro de TSIS

Encaja en:

```text
StrategyPatternLibrary
ParameterCatalog
BacktestExpectationSpec
RobustnessAnalyzer
SystemTestingProtocol
TransactionCostAssumption
LiquidityGate
RiskMetricCatalog
PositionSizingPolicy
PortfolioAllocationResearch
```

## Mapa rapido de capitulos

| Capitulo | Uso TSIS |
|---|---|
| 1 Introduction | Research guidelines, system profile, testing, costs, risk |
| 2 Basic concepts | Returns, volatility, performance, probability |
| 3-5 Chart/swing/event-driven trends | Pattern taxonomy |
| 6-12 Trend, momentum, seasonality, cycles, volume | Strategy families |
| 13 Spreads/arbitrage | Spread/pairs research |
| 14 Behavioral techniques | News/crowd pattern context |
| 15 Pattern recognition | Computer-based pattern detection |
| 16 Day trading | Intraday systems and transaction costs |
| 17 Adaptive techniques | Adaptive parameters |
| 18 Price distribution | Market profile/support/resistance |
| 19 Multiple time frames | Multi-timeframe setup design |
| 20 Advanced techniques | Volatility, liquidity, fuzzy, neural, GA |
| 21 System Testing | Principal fuente para testing/robustez |
| 22 Practical Considerations | Hindsight, price shocks, paper trading, trade-offs |
| 23 Risk Control | Liquidity, metrics, leverage, stops, sizing |
| 24 Portfolio Allocation | Diversification/correlation/allocation |

## Bloque A - Filosofia De Sistema

Paginas 38-43 son fundamentales para governance: vigilar errores de omision, cuestionar resultados demasiado buenos, no tomar atajos, definir perfil del sistema, costes, risk control y monitoring.

Decision TSIS:

```text
cada estrategia debe tener BacktestExpectationSpec antes de optimizar.
```

## Bloque B - Familias De Estrategias

El libro cataloga trendlines, channels, swing, point-and-figure, trend systems, momentum, oscillators, seasonality, cycles, spreads, intraday, adaptive techniques, volatility systems y multi-timeframe. Para TSIS no conviene copiarlas todas; conviene extraer una taxonomia y seleccionar 2-3 estrategias benchmark para probar el motor.

## Bloque C - Testing Y Robustez

Capitulo 21 es central. Paginas 925-944 cubren expectativas, parametros, tipo de variables, data selection, adjusted data y testing integrity. Paginas 958-1001 cubren valid test results, sensitivity, OOS, transaction costs, price shocks y resumen de robustness.

Ideas clave para TSIS:

- testing valida una hipotesis, no debe descubrir por fuerza bruta;
- los parametros deben tener rangos razonables definidos antes;
- no espaciar periodos largos/cortos de forma ingenua;
- usar OOS y step-forward con cautela;
- elegir zonas robustas, no picos;
- resultados excelentes son sospechosos hasta auditar costes, reglas y datos.

## Bloque D - Practical Considerations

Capitulo 22 advierte contra abuso del ordenador, hindsight, paper trading mal usado, price shocks, trade-offs y similitud de senales sistematicas. Esto encaja con `ResearchGovernance` y `BacktestVsPaperReconciler`.

## Bloque E - Risk Control

Capitulo 23 cubre liquidity, Sharpe/information ratio, drawdowns, Calmar, Sortino, Ulcer Index, potential risk, VaR, leverage, individual trade risk, stops, entering/compounding positions y optimal f.

Especialmente relevante para small caps:

```text
inactive markets/small caps -> poor execution;
liquidity is a gate, not a metric cosmetica.
```

## Blueprint TSIS Derivado

```text
StrategyPatternLibrary
ParameterSchema
BacktestExpectationSpec
RobustnessSurface
SensitivityNSpaceReport
PriceShockAudit
TransactionCostSensitivityReport
LiquidityGate
RiskMetricCatalog
PositionSizingPolicy
PortfolioAllocationExperiment
```

## Quality Gates Para Agentes

- Definir expectativas antes de testear.
- No aceptar "surprisingly good" sin auditoria.
- No usar costes irreales.
- No elegir picos aislados de optimizacion.
- Probar mercados/simbolos comparables si se afirma robustez.
- Incluir price-shock audit cuando haya historico suficiente.
- Separar reglas de entrada/salida/sizing/risk.

## Relacion Con Entrada Kaufman Anterior

La entrada antigua `trading_systems_methods_kaufman` se mantiene para no romper referencias. Esta entrada nueva debe preferirse cuando el agente necesite paginas exactas, TOC amplio o trazabilidad directa al PDF indicado por el usuario.
