# Market State Representation Source File Map v0.1

Fecha: 2026-06-25
Estado: reference_map
Scope: TSIS Market Science, Data Foundation, Event Engine, ML/RL, AlphaEvolve

## Rol

Este documento clona y versiona el mapa de archivos fuente localizado durante la
revision de `Market State Representation` en TSIS.

La conclusion operativa es:

```text
TSIS no esta construyendo tablas de comodidad.
TSIS esta construyendo representaciones defendibles del estado de mercado por evento.
```

Estas representaciones deben alimentar:

- Event Engine;
- Outcome Research;
- Machine Learning;
- Decision Models;
- Offline RL;
- Execution Models;
- Evolution Systems / AlphaEvolve;
- sistemas live que actualizan estado en tiempo real.

## Lista Nuclear

- `C:/TSIS_Data/00_CTO/TSIS_LAB_ARCHITECTURE.md`
  - Arquitectura completa.
  - Define Capa 1 Data Foundation, Event Engine, `event_table`, ML, Decision
    Models, Offline RL y Evolution Systems.

- `C:/TSIS_Data/00_CTO/00_private/arquitectura.md`
  - Version privada original del pipeline por capas.
  - Usa eventos como unidad central.
  - No gobierna directamente; gobierna solo cuando se promueve.

- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/README.md`
  - El modulo SmallCaps existe para certificacion de datos, formalizacion de
    estados de mercado y backtesting.

- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/AGENTS.md`
  - Contrato local.
  - Exige formalizar estados de mercado y objetos de research.

- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/README.md`
  - Secuencia vigente:

```text
event_discovery
-> event_definition
-> event_engine
-> event_table
```

## Estado / Evento

- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/04_feature_engine/04_feature_engine.md`
  - Dice explicitamente que convierte el mercado en una secuencia de
    estados/eventos.
  - Declara que eso es compatible con ML/RL.
  - Establece que el Feature Engine no toma decisiones, solo representa estado
    observable del mercado.

- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/05_event_engine/05_event_engine.md`
  - El Event Engine convierte mercado en secuencia interpretable de
    estados/eventos.
  - Introduce state machines como parte del modelo conceptual.

- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/00_cto/roadmap/module_roadmap_initial_vision.md`
  - Roadmap antiguo con la misma idea:

```text
mercado -> secuencia de estados/eventos -> ML/RL
```

## ML / RL

- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/11_ml_preparation/11_ml_offline_rl.md`
  - Menciona `event states`, `state representations` y politicas condicionadas
    al estado del mercado.

- `C:/TSIS_Data/03_TSIS_Offline_RL/00_CTO/00_notas_RL.md`
  - Desarrolla estado, accion, reward, embeddings, estado latente y Offline RL
    sobre estados ricos.

- `C:/TSIS_Data/00_CTO/08_MACHINE_LEARNING/README.md`
  - ML pregunta que representa el estado del mercado.
  - Incluye Feature Engineering, Market State Representation y Causal Features.

- `C:/TSIS_Data/00_CTO/09_REINFORCEMENT_LEARNING/README.md`
  - RL depende de estado, accion, reward y policy.
  - Propone una carpeta especifica para `MARKET_STATE_REPRESENTATION`.

## Market Science

- `C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/README.md`
  - Documento central sobre `Market State Representation`.
  - Conecta microestructura, causalidad, ML, RL y AlphaEvolve.
  - Formula la pregunta central:

```text
Como represento el estado real de una microcap?
```

- `C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/01_Microstructure/README.md`
  - Microstructure features y order flow como parte del estado.

- `C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/03_Causality/README.md`
  - Causalidad aplicada a TSIS.
  - Distingue mecanismo causal de correlacion estadistica.

- `C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/07_Liquidity_Provider_Stress/README.md`
  - Liquidity stress e inventory stress como componentes de estado de mercado.

## AlphaEvolve / Evaluadores

- `C:/TSIS_Data/00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/00_CTO/AlphaEnvolve_en_Tsis.md`
  - AlphaEvolve requiere codigo modificable, evaluator automatico y fitness.
  - Traduce AlphaEvolve a TSIS como:

```text
Strategy / Feature / Policy Candidate
-> TSIS Backtester + Validator
-> Scientific Fitness
-> Candidate Archive
-> Evolution Engine
```

- `C:/TSIS_Data/00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/RESEARCH_AND_DEVELOPMENT/GAME_THEORETIC_PRESSURE_FOR_EVENT_SEARCH_ALPHAEVOLVE_v0_1.md`
  - AlphaEvolve debe evolucionar definiciones de eventos sin contaminar con
    PnL o estrategia.

- `C:/TSIS_Data/00_CTO/05_EVALUATION_SYSTEMS/README.md`
  - Ubicacion conceptual de fitness functions y evaluation systems.

## Data Foundation Outputs

- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md`
  - Documento clave actual.
  - Dice que Data Foundation no produce el evento.
  - Data Foundation produce el estado defendible que permite detectar el evento.
  - Incluye dependencias de evento:

```text
instrument_master
market_calendar
corporate_actions_table
master_daily_table
master_intraday_bar_table
microstructure_features_table
halts_table
real_time_corporate_event_alerts_table
dataset_certification_matrix
data_quality_report
```

- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/microstructure_features_table_dataset_contract_v0_1.md`
  - Microstructure features por ventana explicita de evento.
  - v0.1 es `seed_event_window_smoke`, no full-universe.

- `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/microstructure_features_table_consumption_policy.md`
  - Aclara que v0.1 no es feature store productivo.
  - No debe usarse como entrenamiento ML/RL full-universe.

## Estado Del Hueco Detectado

Existe:

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/
```

pero estaba vacia antes de esta promocion documental.

Debe convertirse en la sede CTO de la pregunta cientifica:

```text
Cual es la representacion minima, causalmente defendible y temporalmente
legal del estado de mercado que permite inferir evento, resultado, decision y
riesgo sin leakage?
```

## Regla De Uso

Este mapa no sustituye ningun contrato operativo.

Sirve para que un humano o agente encuentre rapidamente donde se explica:

- por que TSIS es event-first;
- por que las tablas son componentes de estado;
- por que ML/RL dependen de representacion de estado;
- por que AlphaEvolve no debe empezar por estrategias;
- por que microestructura y causalidad son parte del estado.

