# Trading Systems and Methods, 5th Edition + Website - Concept Index

## Menu

- [Conceptos principales](#conceptos-principales)
- [Activos TSIS sugeridos](#activos-tsis-sugeridos)
- [Prioridad](#prioridad)

## Conceptos principales

| Concepto | Paginas | Encaje TSIS | Accion agente |
|---|---:|---|---|
| Research guidelines | 38-43 | `ResearchGovernance` | Cuestionar costes/risk/resultados buenos |
| System profile | 40-43 | `BacktestExpectationSpec` | Definir objetivo, data, risk, costs, monitoring |
| Market noise | 30-35, 138 | `MarketState`, `RegimeFeature` | Distinguir trend vs mean reversion |
| Strategy family taxonomy | 99-922 | `StrategyPatternLibrary` | Extraer patrones por familia |
| Transaction costs | 42, 737-744, 962-969 | `CostModel`, `CostSensitivityReport` | Validar fast systems con costes reales |
| Parameter identification | 928-930 | `ParameterSchema` | Declarar rangos/tipos antes de optimizar |
| Data selection/adjustment | 930-936 | `DataFoundationPolicy` | Split, rolls, adjusted data, synthetic data |
| In-sample / out-of-sample | 47, 936-939 | `ValidationProtocol` | Separar desarrollo y validacion |
| Step-forward/walk-forward | 938-939 | `WalkForwardRunner` | Simular realidad con ventanas |
| Robustness surface | 942-965, 996-1001 | `RobustnessAnalyzer` | Buscar mesetas, no maximos aislados |
| Sensitivity in n-space | 963-965 | `SensitivityNSpaceReport` | Analizar parametros multiples |
| Price shocks | 990-995, 1012-1017 | `PriceShockAudit` | Auditar shocks y riesgo infraestimado |
| Liquidity | 887, 1053-1054 | `SmallCapLiquidityGate` | Gate de ejecucion para small caps |
| Risk metrics | 1054-1062 | `RiskMetricCatalog` | Sharpe, IR, AMR, Calmar, Sortino, UI, VaR |
| Position sizing/stops | 1070-1081 | `PositionSizingPolicy`, `StopPolicy` | Controlar riesgo individual |
| Portfolio allocation | 1099+ | `PortfolioAllocationExperiment` | Diversificacion/correlation/allocation |

## Activos TSIS sugeridos

```text
StrategyPatternLibrary
ParameterCatalog
BacktestExpectationSpec
RobustnessSurface
SensitivityNSpaceReport
PriceShockAudit
RiskMetricCatalog
SmallCapLiquidityGate
```

## Prioridad

```text
v0.1: expectations, costs, parameter schema, basic robustness
v0.2: walk-forward, sensitivity surfaces, price shock audit
v0.3: portfolio/risk allocation and strategy library expansion
```
