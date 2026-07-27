# Testing and Tuning Market Trading Systems - Timothy Masters

Resumen operativo para agentes TSIS.

## Menu

- [Resumen ejecutivo](#resumen-ejecutivo)
- [Rol dentro de TSIS](#rol-dentro-de-tsis)
- [Mapa rapido de capitulos](#mapa-rapido-de-capitulos)
- [Bloque A - Pre-optimizacion](#bloque-a---pre-optimizacion)
- [Bloque B - Optimizacion](#bloque-b---optimizacion)
- [Bloque C - Bias, OOS y walkforward](#bloque-c---bias-oos-y-walkforward)
- [Bloque D - Trade analysis y retornos](#bloque-d---trade-analysis-y-retornos)
- [Bloque E - Bootstrap y permutation tests](#bloque-e---bootstrap-y-permutation-tests)
- [Blueprint TSIS derivado](#blueprint-tsis-derivado)
- [Quality gates para agentes](#quality-gates-para-agentes)
- [Limitaciones](#limitaciones)

## Resumen ejecutivo

Masters es una de las fuentes mas utiles de la biblioteca para la capa de validacion y optimizacion de TSIS. No ensena a construir el event loop, pero si ensena a no enganarse cuando el motor ya produce retornos.

Su tesis practica para TSIS:

```text
un resultado bueno no vale si no sabemos cuanto bias, leakage, selection bias, sample error y dependencia temporal contiene.
```

## Rol dentro de TSIS

Encaja en:

```text
OptimizationRunner
WalkForwardRunner
TemporalLeakageGate
SelectionBiasAudit
ReturnsGranularityPolicy
PermutationTestRunner
BootstrapBounds
DrawdownBounds
ParameterSensitivityAnalyzer
ValidationReport
```

Debe aplicarse despues del primer vertical slice del backtester, pero sus registros de experimento deben existir desde v0.1.

## Mapa rapido de capitulos

| Capitulo | Uso TSIS |
|---|---|
| 1 Introduction | Alcance: testing/rigor, no diseno de estrategias |
| 2 Pre-optimization Issues | Stationarity, entropy e indicadores antes de optimizar |
| 3 Optimization Issues | Regularizacion, lambda CV, differential evolution |
| 4 Post-optimization Issues | Bias barato, sensibilidad, relaciones de parametros |
| 5 Future Performance I | IS/OOS, training bias, selection bias, walkforward, CSCV |
| 6 Future Performance II | Bar-by-bar returns, trade analysis, confidence bounds, drawdown |
| 7 Permutation Tests | Tests de sistema, factory, selection bias y modelos predictivos |

## Bloque A - Pre-optimizacion

Paginas 21-24 tratan stationarity como problema practico: indicadores, retornos y propiedades de mercado cambian. Antes de optimizar, TSIS debe mirar si el indicador se desplaza, cambia de varianza o solo funciona en un regimen.

Decision TSIS:

```text
todo FeatureSet candidato debe tener StationarityProfile y RegimeCoverageReport.
```

## Bloque B - Optimizacion

Paginas 46-48 son clave: la calidad de los indicadores importa mas que la potencia del modelo. Masters favorece empezar simple y regularizar antes de usar modelos no lineales.

Paginas 88-110 cubren differential evolution como optimizador no lineal. En TSIS solo debe usarse si el espacio de busqueda esta previamente declarado y si se registra el numero de evaluaciones.

## Bloque C - Bias, OOS y Walkforward

Paginas 153-161 separan training bias y selection bias. Un OOS deja de ser imparcial si se usa para elegir al ganador entre muchas estrategias. La solucion conceptual es reservar otro tramo o mecanismo que evalue el sistema ya seleccionado.

Paginas 168-176 muestran detalles peligrosos de walkforward con lookahead: hay que usar buffers `OMIT` y `EXTRA` para evitar overlap IS/OOS y correlacion serial peligrosa.

Decision TSIS:

```text
WalkForwardRunner debe declarar lookback, lookahead, omit_buffer, extra_gap, train_window, test_window.
```

## Bloque D - Trade Analysis y Retornos

Paginas 235-240 explican por que analizar solo trades cerrados puede destruir informacion. Para estadistica, bar-by-bar OOS returns suelen ser superiores: conservan volatilidad interna y evitan profit factor/Sharpe inflados por trades agregados.

Decision TSIS:

```text
guardar trade-level returns y bar/event-level marked-to-market returns.
```

## Bloque E - Bootstrap y Permutation Tests

Paginas 254-283 cubren lower bounds, confidence intervals y bootstrap. Paginas 338-360 cubren permutation tests. La idea crucial: las permutaciones deben destruir la relacion predictiva sin crear historiales imposibles. En multi-mercado, preservar correlaciones y calendarios compartidos es obligatorio.

Decision TSIS:

```text
PermutationTestRunner no puede barajar datos de small caps sin respetar calendario, multi-symbol alignment y estructura realista de mercado.
```

## Blueprint TSIS derivado

```text
StationarityProfile
FeatureEntropyReport
OptimizationManifest
TrainingBiasEstimate
SelectionBiasAudit
WalkForwardWindowPolicy
LeakageBufferPolicy
ReturnGranularityPolicy
BootstrapConfidenceBounds
PermutationTestRun
DrawdownBoundReport
```

## Quality Gates Para Agentes

- No seleccionar estrategia por IS.
- No seleccionar entre muchas variantes usando el mismo OOS que se reporta como final.
- No usar completed-trade-only returns para tests estadisticos criticos.
- Declarar lookahead y buffers antes del walkforward.
- Registrar numero de variantes probadas.
- Tratar resultados extremadamente buenos como sospechosos hasta auditar data/rules/leakage.

## Limitaciones

Los ejemplos estan en C++ y con muchos casos de barras diarias. TSIS debe traducir la logica a Python/Parquet y adaptarla a small caps, intradia, costs, halts, liquidity y short constraints.
