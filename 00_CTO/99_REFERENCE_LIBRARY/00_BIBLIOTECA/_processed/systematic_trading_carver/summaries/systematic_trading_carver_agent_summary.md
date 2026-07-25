# Systematic Trading - Robert Carver

Resumen operativo para agentes TSIS.

## Menu

- [Resumen ejecutivo](#resumen-ejecutivo)
- [Rol dentro de TSIS](#rol-dentro-de-tsis)
- [Mapa rapido](#mapa-rapido)
- [Theory](#theory)
- [Toolbox](#toolbox)
- [Framework](#framework)
- [Practice](#practice)
- [Blueprint TSIS derivado](#blueprint-tsis-derivado)
- [Quality gates](#quality-gates)
- [Limitaciones](#limitaciones)

## Resumen ejecutivo

Carver no es un libro de backtesting engine. Es un manual practico de diseno de sistemas robustos, especialmente fuerte en framework modular, forecasts, combinacion de reglas, volatility targeting, position sizing, portfolio construction y control de costes.

Para TSIS, su valor es convertir estrategias en un sistema de posicionamiento y riesgo coherente:

```text
forecast -> forecast scaling -> combined forecast -> volatility target -> position -> portfolio
```

La idea clave es que el edge no vive solo en la entrada. La robustez depende de sizing, diversificacion, costes, velocidad de trading y disciplina.

## Rol dentro de TSIS

Encaja en:

```text
ForecastModel
ForecastCombiner
VolatilityTargeting
PositionSizing
InstrumentWeights
DiversificationMultiplier
CostAwareSpeedPolicy
PortfolioConstruction
SemiAutomaticDecisionFramework
```

No sustituye a Pardo/Lopez de Prado para validacion cientifica ni a Nautilus/LEAN para arquitectura event-driven.

## Mapa rapido

| Parte | Contenido | Uso TSIS |
|---|---|---|
| Theory | sesgos humanos, reglas simples, estilos, Sharpe alcanzable | `StrategyGovernance`, `ExpectationSetting` |
| Toolbox | fitting y portfolio allocation | `OverfitGuard`, `PortfolioWeightPolicy` |
| Framework | instruments, forecasts, combined forecasts, vol target, position sizing, portfolios, costs | `PortfolioConstructionEngine` |
| Practice | semi-automatic, asset allocator, staunch systems trader | `OperatorMode`, `Runbook` |
| Appendices | EWMAC, carry, portfolio optimisation, forecast rescaling | `StrategyTemplate`, `ForecastScaling` |

## Theory

Carver parte de una tesis pragmaticamente importante: los humanos son malos ejecutando decisiones financieras bajo emocion. La solucion no tiene que ser automatizacion total; puede ser sistematizar decision, sizing y riesgo.

Para TSIS:

```text
discretionary_signal_allowed
systematic_risk_framework_required
```

Incluso si la senal viene de analisis humano, la posicion, riesgo y portfolio deben ser reglas reproducibles.

## Toolbox

La seccion de fitting advierte contra sistemas que funcionan demasiado bien en backtest. El problema no es usar datos, sino ajustar demasiado a ellos. La optimizacion de portfolio tambien puede fallar si se confia demasiado en estimaciones inestables.

Aplicacion:

- limitar complejidad;
- preferir reglas simples;
- usar pesos robustos;
- no confiar en parametros demasiado precisos;
- penalizar costes antes de seleccionar velocidad.

## Framework

Esta es la parte central para TSIS.

Componentes:

```text
instrument selection
forecast generation
forecast combination
forecast scaling/capping
volatility targeting
position sizing
instrument weights
diversification multiplier
trading cost policy
```

La idea de forecast normalizado es especialmente util: diferentes reglas pueden emitir senales comparables si se escalan a una unidad comun y se capan para evitar posiciones extremas.

Para TSIS small caps:

```text
raw_signal_score -> normalized_forecast -> capped_forecast -> risk_targeted_position
```

Esto separa alpha de sizing y evita que cada estrategia invente su propio mecanismo de riesgo.

## Practice

Carver define tres modos:

- asset allocating investor;
- semi-automatic trader;
- staunch systems trader.

Para TSIS, esto sugiere separar:

```text
decision_mode = discretionary | semi_automatic | systematic
execution_mode = manual | assisted | automated
```

La infraestructura debe permitir operar estrategias con distinto grado de automatizacion manteniendo el mismo ledger, manifest y risk framework.

## Blueprint TSIS derivado

```text
Signal/Decision
    -> RawForecast
    -> ForecastScaler
    -> ForecastCombiner
    -> ForecastCap
    -> VolatilityTarget
    -> PositionSizer
    -> InstrumentWeightPolicy
    -> CostAwareTradeFilter
    -> PortfolioTarget
    -> OrderRequest
```

## Quality gates

- La estrategia debe declarar forecast bruto y forecast normalizado.
- El sizing no debe estar mezclado con la regla de entrada.
- Debe existir volatility target o limite de riesgo equivalente.
- Debe registrarse coste esperado por velocidad de trading.
- Debe existir portfolio/instrument weight policy.
- No aceptar reglas altamente optimizadas sin simplicidad o robustez.

## Limitaciones

No cubre microestructura profunda, order book, DAS, OMS ni event loop. Su utilidad maxima esta en portfolio construction y risk sizing.

