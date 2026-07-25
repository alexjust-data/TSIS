# Building Winning Algorithmic Trading Systems - Kevin J. Davey

Resumen operativo para agentes TSIS.

## Menu

- [Resumen ejecutivo](#resumen-ejecutivo)
- [Rol dentro de TSIS](#rol-dentro-de-tsis)
- [Mapa rapido](#mapa-rapido)
- [Testing y desarrollo](#testing-y-desarrollo)
- [Walk-forward, Monte Carlo e incubacion](#walk-forward-monte-carlo-e-incubacion)
- [Position sizing y live monitoring](#position-sizing-y-live-monitoring)
- [Blueprint TSIS derivado](#blueprint-tsis-derivado)
- [Quality gates](#quality-gates)
- [Limitaciones](#limitaciones)

## Resumen ejecutivo

Davey es una fuente practica sobre el proceso completo de crear estrategias mecanicas: idea, datos, pruebas limitadas, walk-forward, Monte Carlo, incubacion, position sizing, documentacion y monitorizacion live.

No es una referencia institucional de microestructura ni de arquitectura. Su valor para TSIS es operacional:

```text
strategy idea -> limited test -> walk-forward -> Monte Carlo -> incubation -> live monitoring
```

Es especialmente util para evitar el ciclo de "optimizo una curva bonita y la lanzo".

## Rol dentro de TSIS

Encaja en:

```text
StrategyFactory
IdeaIntake
LimitedFeasibilityTest
WalkForwardTest
MonteCarloRobustness
IncubationHarness
StrategyDocumentation
LiveMonitoring
```

## Mapa rapido

| Parte | Contenido | Uso TSIS |
|---|---|---|
| Part I | trayectoria y errores reales | `CautionaryCases` |
| Part II | evaluar, analizar y disenar sistemas | `StrategyDevelopmentProcess` |
| Part III | desarrollar estrategia: data, limited test, WFA, MC, incubation, sizing, docs | `StrategyFactory` |
| Part IV | ejemplo de sistema completo | `BenchmarkProcessExample` |
| Part V | antes de live: account, psychology, operations | `GoLiveChecklist` |
| Part VI | monitorizacion live | `LivePerformanceMonitor` |
| Part VII | cautionary tales | `FailureModeLibrary` |

## Testing y desarrollo

Davey insiste en que el objetivo no es crear el mejor backtest, sino un backtest que tenga alguna probabilidad razonable de reflejar el futuro. Un punto practico fuerte es la secuencia progresiva de filtros: muchas ideas deben morir pronto.

Para TSIS:

```text
100-200 ideas -> 1 estrategia candidata
```

Esto implica que la infraestructura debe registrar ideas rechazadas, no solo ganadoras.

## Walk-forward, Monte Carlo e incubacion

El libro da mucho peso a:

- walk-forward analysis;
- Monte Carlo;
- incubation;
- real-time verification.

Para TSIS, esto se convierte en:

```text
backtest_candidate
    -> walk_forward_candidate
    -> monte_carlo_pass
    -> incubation_shadow_run
    -> live_small_size
```

La incubacion es importante: una estrategia puede tener buen backtest y aun asi debe observarse en condiciones reales antes de usar capital significativo.

## Position sizing y live monitoring

Davey advierte que una mala estrategia puede parecer mejor por position sizing agresivo. Primero se debe evaluar con sizing simple, luego aplicar money management.

Live monitoring debe comparar:

```text
expected_profile vs actual_profile
```

No solo P&L. Tambien:

- drawdown;
- trade frequency;
- win/loss profile;
- slippage;
- missed trades;
- broker/execution differences;
- degradation.

## Blueprint TSIS derivado

```text
IdeaRecord
    -> FeasibilityTest
    -> DetailedBacktest
    -> WalkForwardRun
    -> MonteCarloRun
    -> IncubationRun
    -> GoLiveApproval
    -> LiveMonitoringProfile
```

## Quality gates

- Toda idea debe tener `idea_id`.
- Registrar datos usados y reglas exactas.
- Hacer limited testing antes de investigacion profunda.
- No seleccionar solo por net profit.
- Exigir walk-forward para candidatos.
- Exigir Monte Carlo o perturbacion de trades.
- Exigir incubacion/shadow antes de live real.
- Documentar reglas, parametros y decision go/no-go.
- Comparar live contra perfil esperado.

## Limitaciones

Es retail/practico y centrado en futuros/sistemas mecanicos. No cubre microestructura small caps, order book, DAS, ni engine architecture. Es complemento operativo de Pardo.

