# Quantum Finance - Concept Index

## Menu

- [Conceptos principales](#conceptos-principales)
- [Activos TSIS sugeridos](#activos-tsis-sugeridos)
- [Prioridad](#prioridad)

## Conceptos principales

| Concepto | Paginas | Encaje TSIS | Accion agente |
|---|---:|---|---|
| Four-tier quantum finance model | 42-44 | `ExperimentalAlphaArchitecture` | Mapear como capas de feature/forecast/policy |
| Quantum Price Levels | 116-140 | `FeatureFamily`, `SupportResistanceAlternative` | Implementar solo como feature experimental |
| Trend/breakout/reversal/channel families | 146-181 | `StrategyPatternLibrary` | Usar como taxonomia de setups |
| Risk control reminder | 181-184 | `RiskPolicy` | Vincular a stops/sizing, no a forecast |
| Genetic algorithm | 207-213 | `GeneticSearchRunner` | Requiere manifest de espacio de busqueda |
| Fuzzy logic for trading | 214-229 | `FuzzyFeatureLayer` | Convertir reglas difusas en features trazables |
| Chaos/fractals | 236-256 | `ExperimentalFeatureLab` | Validar contra baselines simples |
| QPL/MQL implementation pipeline | 300-319 | `ForecastBatchRun` | Traducir MQL a Python solo si hay tarea concreta |
| TSCNON architecture | 325-353 | `ForecastModelRegistry` | Catalogar como forecast system, no motor de trading |
| Actor-critic RL trader | 398-417 | `OfflineRLPolicyLab` | Aplazar hasta backtester + costs + replay |

## Activos TSIS sugeridos

```text
QuantumPriceLevelFeature
ForecastBatchRunManifest
ForecastOutputLedger
SignalSelectionExperiment
RewardFunctionSpec
RLPolicyExperiment
ModelBenchmarkReport
```

## Prioridad

```text
v0.1 backtester: baja
alpha research clasico: baja/media
experimental ML/RL: media
post-core TSIS: alta como fuente de ideas, baja como autoridad
```
