# Testing and Tuning Market Trading Systems - Concept Index

## Menu

- [Conceptos principales](#conceptos-principales)
- [Activos TSIS sugeridos](#activos-tsis-sugeridos)
- [Prioridad](#prioridad)

## Conceptos principales

| Concepto | Paginas | Encaje TSIS | Accion agente |
|---|---:|---|---|
| Stationarity | 21-24 | `StationarityProfile` | Auditar indicadores antes de optimizar |
| Entropy / indicator information | 25-45 | `FeatureInformationReport` | Medir informacion de indicadores |
| Regularization | 46-82 | `ModelComplexityBudget` | Preferir modelos simples/regularizados |
| Differential evolution | 88-110 | `OptimizationRunner` | Usar con manifest y limite de busqueda |
| Training bias estimate | 115-121 | `TrainingBiasEstimate` | Estimar bias preliminar durante optimizacion |
| Parameter sensitivity | 123-152 | `ParameterSensitivityAnalyzer` | Buscar zonas robustas, no picos |
| IS/OOS split | 153-161 | `ValidationProtocol` | Separar training, selection y final test |
| Selection bias | 157-161 | `SelectionBiasAudit` | OOS usado para elegir deja de ser final |
| Walkforward buffers | 168-176 | `TemporalLeakageGate` | Declarar omit/extra/lookahead |
| Cross-validation risk | 184-188 | `CrossValidationPolicy` | Usar con guard buffers y cautela |
| CSCV | 195-230 | `CSCVRunner` | Futuro PBO/overfit audit |
| Bar-by-bar returns | 235-240 | `ReturnGranularityPolicy` | Mantener retornos por barra/evento |
| Confidence lower bounds | 254-268 | `ConfidenceBounds` | Reportar lower bound, no solo media |
| Bootstrap | 269-283 | `BootstrapBounds` | Usar para distribuciones no normales |
| Drawdown bounds | 286-337 | `DrawdownBoundReport` | Estimar riesgo de drawdown futuro |
| Permutation tests | 338-360 | `PermutationTestRunner` | Test robusto contra random luck/selection |

## Activos TSIS sugeridos

```text
ValidationProtocol
OptimizationManifest
WalkForwardRunner
TemporalLeakageGate
ReturnGranularityPolicy
SelectionBiasAudit
PermutationTestRunner
BootstrapConfidenceBounds
DrawdownBounds
```

## Prioridad

```text
v0.1: manifest + train/validation/test + no leakage
v0.2: walkforward + sensitivity
v0.3: bootstrap/permutation/CSCV
```
