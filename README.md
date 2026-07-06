# TSIS (Trading Scientific Intelligence System)

TSIS es un `Scientific Discovery Engine` para microcaps y small caps.

No es solo un backtester, una coleccion de estrategias, una tabla de estado o AlphaEvolve. El proyecto convierte datos gobernados en experimentos reproducibles, evidencia, conocimiento validado y componentes operativos.

## Lectura Inicial Obligatoria

Primero leer:

```text
C:/TSIS_Data/START_HERE.md
C:/TSIS_Data/PROJECT_OPERATING_SYSTEM.md
C:/TSIS_Data/PROJECT_RULES.md
C:/TSIS_Data/VERSIONING_STANDARDS.md
C:/TSIS_Data/RESEARCH_PHILOSOPHY.md
C:/TSIS_Data/00_CTO/TSIS_LAB_ARCHITECTURE_v3.md
C:/TSIS_Data/00_TSIS_Lab/README.md
E:/TSIS/data/README.md
```

Lectura correcta de arquitectura:

```text
TSIS = Scientific Discovery Engine
research_experiment = unidad cientifica central
AlphaEvolve = generador posible de candidate research experiments, no autoridad
Scientific Validation Pipeline = capa de aceptacion de conocimiento
```

## Arranque Recomendado De Codex

```powershell
powershell -ExecutionPolicy Bypass -File C:\TSIS_Data\START_CODEX_TSIS_AUTONOMOUS.ps1
```

## Mapa De Responsabilidades

```text
C:/TSIS_Data/00_CTO
= autoridad, filosofia, arquitectura, mapas y reglas

C:/TSIS_Data/00_TSIS_Lab
= contratos, registros, templates y experimentos cientificos reproducibles

C:/TSIS_Data/01_TSIS_backtest_SmallCaps
= Data Foundation, event discovery, feature engine, backtest clasico y strategy research SmallCaps

C:/TSIS_Data/02_TSIS_webSocket_SmallCaps
= live/shadow operation y procesamiento event-driven

C:/TSIS_Data/03_TSIS_Offline_RL
= aprendizaje secuencial sobre estados/outcomes gobernados

E:/TSIS/data
= outputs pesados, materializaciones y roots fisicos
```

## Flujo Conceptual Vigente

```text
Data Foundation
-> Canonical State / Event State / Outcomes
-> Research Experiment
-> Execution
-> Evidence
-> Scientific Validation Pipeline
-> Knowledge Object
-> Validated Knowledge
-> Operational Component
-> Backtest / Live / ML / RL / AlphaEvolve, segun corresponda
```

## Nota Obligatoria Sobre Datos Fisicos Y Minutos

Todo agente debe leer `E:/TSIS/data/README.md` como parte del contexto base del proyecto. Ese README gobierna el plano fisico de datos.

Para trabajos con minutos/1m, la raiz fisica canonica es:

```text
E:/TSIS/data/ohlcv_1m
```

Motivo: TSIS ya tuvo un incidente real de velas 1m imposibles y reparacion quote-guarded. La regla evita que agentes futuros usen rutas historicas, asuman que el raw esta corregido, o ignoren overlays/manifests oficiales.

