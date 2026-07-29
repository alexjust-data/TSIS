# TSIS_SCIENTIFIC_RESEARCH_LABORATORY_SYSTEM_MAP_V0_1

# 1. Propósito

TSIS es un laboratorio científico para:

```text
construir
auditar
validar
preservar
y evolucionar
```

conocimiento histórico sobre el mercado de small caps estadounidenses.

El sistema no se limita a ejecutar estrategias.

Debe permitir reconstruir completamente el recorrido:

```text
dato fuente
↓
representación del mercado
↓
fenómeno observado
↓
hipótesis
↓
experimento
↓
operaciones simuladas
↓
resultados
↓
validación
↓
evidencia
↓
conocimiento
```

---

# 2. Principio central

```text
TSIS construye la semántica científica propia.

Las librerías externas proporcionan infraestructura genérica.
```

TSIS no debe reconstruir:

```text
motores SQL
formatos columnares
álgebra numérica
frameworks de ML
sistemas de control de versiones
contenedores
```

TSIS sí debe construir:

```text
autoridad de datos
universos históricos
legalidad temporal
representaciones de mercado
eventos
hipótesis
experimentos
simulación
validación
evidencia
conocimiento
```

---

# 3. Mapa completo del sistema

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 TSIS SCIENTIFIC RESEARCH LABORATORY                         │
└─────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│ 01. RESEARCH GOVERNANCE                                                     │
│                                                                             │
│ Research Questions · Hypotheses · Experiment Authorization                  │
│ Versioning · Scope · Scientific Decisions · Limitations                     │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 02. DATA AUTHORITY                                                          │
│                                                                             │
│ RAW Vendor Data · Reference · News · Fundamentals · Short · Halts           │
│ Daily · 1m · Trades · Quotes · Corporate Actions                            │
│ Dataset Contracts · Schemas · Validators · Known Failures                   │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 03. DATASET AND PRICE-VIEW RESOLUTION                                       │
│                                                                             │
│ raw · adjusted · split_normalized · quote_guarded · governed derivatives    │
│ Dataset Version · Physical Paths · Repair Manifests · Lineage               │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 04. TEMPORAL AND MARKET AUTHORITY                                           │
│                                                                             │
│ Trading Calendar · Sessions · Timezones · DST · Early Closes                │
│ Security Lifecycle · Listings · Delistings · Ticker Changes · Splits        │
│ Information Availability · Publication Delays · Point-in-Time Legality      │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 05. POINT-IN-TIME UNIVERSE                                                  │
│                                                                             │
│ Historical Symbol Universe · In-Play Universe · Eligibility Rules           │
│ Membership Reasons · Exclusions · Universe Manifests                        │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 06. DATA QUALITY AND MARKET RECONSTRUCTION                                  │
│                                                                             │
│ Missing Bars · Bad Prints · Impossible Prices · Halts · Late Opens          │
│ Quote Guards · Repairs · Empty Minutes · Data Gaps · Exceptions             │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 07. FEATURE AND INFORMATION OBJECT LAYER                                    │
│                                                                             │
│ Price Movement · Trading Activity · Volatility · Liquidity                  │
│ Microstructure · Order Flow · News · Fundamentals · Short Context           │
│ Broad Market · Halts · Intraday Position                                    │
│                                                                             │
│ Feature Registry · Definitions · Dependencies · Availability                │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 08. MARKET REPRESENTATION                                                   │
│                                                                             │
│ Market State                                                               │
│ What was observable in market state at decision timestamp t?                │
│                                                                             │
│ Event State                                                                │
│ What was observable at t with respect to event E?                           │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 09. EVENT RESEARCH                                                          │
│                                                                             │
│ Event Definitions · Detection · Event Tables · Outcome Windows              │
│ Event Families · Event Instances · Event Transitions                        │
│ Clustering · Comparable Cases · Phenomenon Discovery                        │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 10. HYPOTHESIS AND STRATEGY RESEARCH                                        │
│                                                                             │
│ Research Question · Hypothesis · Expected Mechanism                         │
│ Entry Rules · Exit Rules · Stops · Sizing · Parameters                      │
│ Forbidden Information · Strategy Freeze · Strategy Version                  │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 11. EXPERIMENT DESIGN                                                       │
│                                                                             │
│ Dataset · Universe · Dates · Sessions · Costs · Execution Assumptions       │
│ Training · Validation · Holdout · Walk-Forward · Scenarios                  │
│ Experiment Manifest · Run Configuration · Reproducibility                   │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
┌───────────────────────────────────┐   ┌─────────────────────────────────────┐
│ 12A. VECTOR RESEARCH ENGINE       │   │ 12B. EVENT-DRIVEN BACKTEST ENGINE  │
│                                   │   │                                     │
│ Fast Exploration                  │   │ Chronological Event Processing      │
│ Parameter Sweeps                  │   │ Order Intents                       │
│ Sensitivity Matrices              │   │ Orders                              │
│ Cross-Sectional Analysis          │   │ Fills                               │
│ Scenario Grids                    │   │ Positions                           │
│ Fast Portfolio Evaluation         │   │ Portfolio                           │
│                                   │   │ Execution State                     │
└─────────────────┬─────────────────┘   └──────────────────┬──────────────────┘
                │                                        │
                └────────────────────┬───────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 13. EXECUTION SIMULATION                                                    │
│                                                                             │
│ Market · Limit · Stop · Same-Bar Ambiguity · Intrabar Paths                 │
│ Bid/Ask · Spread · Slippage · Latency · Participation                       │
│ Partial Fills · Queue Assumptions · Rejections · Halts                      │
│ Capacity · Locates · Borrow · Fees                                          │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 14. PORTFOLIO AND ACCOUNTING                                                │
│                                                                             │
│ Cash · Positions · Average Cost · Realized PnL · Unrealized PnL             │
│ Exposure · Equity · Leverage · Costs · Daily Returns                        │
│ Accounting Identities · Portfolio Constraints                              │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 15. CANONICAL OUTPUT LEDGERS                                                │
│                                                                             │
│ Universe Membership · Decisions · Order Intents · Orders · Fills            │
│ Positions · Closed Trades · Daily Portfolio · Equity Curve                  │
│ Cost Breakdown · Exceptions · State Snapshots                               │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 16. PERFORMANCE AND DIAGNOSTICS                                             │
│                                                                             │
│ Gross/Net PnL · Win Rate · Expectancy · Profit Factor                       │
│ Drawdown · Sharpe · Sortino · Exposure · Turnover · Capacity                │
│ MAE · MFE · Concentration by Ticker · Day · Regime · Event                  │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 17. ROBUSTNESS AND SCIENTIFIC VALIDATION                                    │
│                                                                             │
│ Chronological Holdout · Walk-Forward · Parameter Stability                  │
│ Cost Stress · Spread Stress · Slippage Stress · Fill Stress                 │
│ Universe Perturbation · Subperiods · Regimes · Bootstrap                    │
│ Multiple Testing · PBO · DSR · Independent Replication                      │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                        ┌────────────┴─────────────┐
                        │                          │
                        ▼                          ▼
┌───────────────────────────────────┐  ┌──────────────────────────────────────┐
│ 18. ML RESEARCH                   │  │ 19. EVOLUTION SYSTEMS                │
│                                   │  │                                      │
│ Logistic Regression               │  │ AlphaEvolve                          │
│ Random Forest                     │  │ OpenEvolve                           │
│ Gradient Boosting                 │  │ Feature Evolution                    │
│ Transformers                      │  │ Detector Evolution                   │
│ Representation Learning           │  │ Rule Evolution                       │
│ Clustering                        │  │ Strategy Evolution                   │
│ Supervised Learning               │  │ Controlled Search                    │
│ Offline RL / IRL                  │  │ Multiple-Testing Governance          │
└─────────────────┬─────────────────┘  └──────────────────┬───────────────────┘
                │                                       │
                └─────────────────────┬─────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 20. EXPERIMENT REGISTRY                                                     │
│                                                                             │
│ Experiment IDs · Run IDs · Parameters · Metrics · Artifacts                 │
│ Dataset Versions · Universe Versions · Strategy Versions                    │
│ Code Commit · Environment · Dependencies · Reproduction Status              │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 21. EVIDENCE REGISTRY                                                       │
│                                                                             │
│ Tables · Charts · Casepacks · Statistical Tests · Exceptions                │
│ Supporting Evidence · Contradictory Evidence · Limitations                  │
│ Source Lineage · Audit Trail                                                │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 22. KNOWLEDGE FORMATION                                                     │
│                                                                             │
│ Finding · Phenomenon · Validated Relationship · Conditional Edge            │
│ Rejected Hypothesis · Unresolved Question · Domain Limitation               │
│ Confidence · Scope · Conditions · Evidence Links                            │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 23. KNOWLEDGE REGISTRY                                                      │
│                                                                             │
│ Accepted Knowledge · Provisional Knowledge · Rejected Knowledge             │
│ Superseded Knowledge · Version History · Dependencies                       │
│ Evidence References · Replication Status                                    │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 24. REPRODUCIBLE RESEARCH DOSSIER                                           │
│                                                                             │
│ Hypothesis · Data · Universe · Strategy · Execution · Results               │
│ Robustness · Evidence · Limitations · Conclusions · Reproduction Guide      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 4. Flujo completo de investigación

```text
Research Question
    ↓
Hypothesis
    ↓
Experiment Authorization
    ↓
Dataset Resolution
    ↓
Point-in-Time Universe
    ↓
Temporal Legality
    ↓
Feature / State Construction
    ↓
Event Detection
    ↓
Strategy Decision
    ↓
Order Intent
    ↓
Execution Simulation
    ↓
Fill
    ↓
Position
    ↓
Portfolio
    ↓
PnL
    ↓
Metrics
    ↓
Robustness
    ↓
Evidence
    ↓
Scientific Decision
    ↓
Knowledge Registry
```

---

# 5. Flujo completo de una operación

```text
Historical session begins
    ↓
Resolve authorized dataset and price view
    ↓
Resolve valid securities for the date
    ↓
Construct point-in-time In-Play universe
    ↓
Load data available at decision timestamp
    ↓
Construct Market State / Event State
    ↓
Evaluate frozen strategy rules
    ↓
Create decision
    ↓
Create order intent
    ↓
Apply risk and portfolio constraints
    ↓
Create simulated order
    ↓
Evaluate venue, price, spread and liquidity
    ↓
Generate zero, one or multiple fills
    ↓
Update position
    ↓
Update cash, costs and exposure
    ↓
Evaluate exit conditions
    ↓
Create exit order intent
    ↓
Simulate exit fills
    ↓
Close or reduce position
    ↓
Calculate realized PnL
    ↓
Update daily portfolio and equity
    ↓
Persist every ledger and exception
```

---

# 6. Modos de ejecución

## 6.1 Modo tabular

Para estrategias donde no es necesario reconstruir toda la secuencia intradía.

```text
Universe Table
    ↓
Entry/Exit Price Resolution
    ↓
Trade Table
    ↓
Daily Portfolio
    ↓
Metrics
```

Ejemplos:

```text
open-to-close
close-to-open
daily gap studies
fixed-time entry and exit
cross-sectional ranking
event outcome research
```

---

## 6.2 Modo vectorizado

Para exploración masiva y sensibilidad.

```text
Research Matrix
    ↓
Signals / Parameters / Scenarios
    ↓
Vectorized Evaluation
    ↓
Candidate Results
```

No constituye por sí solo la autoridad final de evidencia.

Los resultados importantes deben pasar posteriormente al motor auditable.

---

## 6.3 Modo event-driven

Para estrategias donde el orden exacto de los eventos modifica el resultado.

```text
Clock
↓
Ordered Market Events
↓
Strategy
↓
Order Intent
↓
Execution
↓
Fill
↓
Portfolio
```

Ejemplos:

```text
stops
targets
partial fills
halts
multiple entries
multiple exits
quotes
trades
microstructure
latency
scalping
hyperscalping
```

---

# 7. Límites entre componentes

## Data Foundation

Responsable de:

```text
preservación
procedencia
esquemas
validación
versiones
fallos conocidos
```

No decide:

```text
qué estrategia operar
qué hipótesis aceptar
qué resultado es conocimiento
```

---

## Universe Builder

Responsable de:

```text
qué símbolos eran elegibles
en una fecha y timestamp determinados
```

No decide:

```text
si comprar
cuánto comprar
cómo ejecutar
```

---

## Representation Layer

Responsable de:

```text
representar lo observable
```

No decide:

```text
acciones operativas
labels futuros
resultados
```

---

## Event Research

Responsable de:

```text
detectar y estudiar fenómenos
```

No decide:

```text
entradas
salidas
posición
```

---

## Strategy Engine

Responsable de:

```text
tomar decisiones
según una estrategia congelada
```

No decide:

```text
si la orden realmente se ejecuta
a qué precio final
```

---

## Execution Simulator

Responsable de:

```text
convertir órdenes intentadas
en fills simulados
```

No decide:

```text
qué estrategia es buena
si existe conocimiento
```

---

## Portfolio and Accounting

Responsable de:

```text
posiciones
cash
costes
PnL
equity
```

No decide:

```text
validez estadística
robustez científica
```

---

## Validation Layer

Responsable de:

```text
determinar si el resultado
sobrevive a pruebas de robustez
```

No modifica:

```text
la estrategia original
los datos originales
los resultados históricos
```

---

## Knowledge Registry

Responsable de:

```text
preservar conclusiones científicas
y su evidencia
```

No debe contener:

```text
afirmaciones sin evidencia
resultados no reproducibles
hallazgos exploratorios presentados como confirmados
```

---

# 8. Componentes propios y componentes reutilizados

## TSIS construye

```text
Data Authority
Dataset Resolver
Price-View Resolver
Temporal Legality
Point-in-Time Universe
In-Play Universe
Event Engine
Information Objects
Market State
Event State
Strategy Specification
Order Intent Model
Execution Policies
Canonical Ledgers
Experiment Registry
Evidence Registry
Knowledge Registry
Research Governance
Scientific Dossiers
```

## TSIS utiliza

```text
Parquet / Arrow
DuckDB
Polars
NumPy
Numba
Pandas
SciPy
Statsmodels
Scikit-learn
PyTorch
MLflow
Optuna
Pytest
Pydantic
Git
Docker
Matplotlib
Plotly
```

Estas herramientas proporcionan infraestructura.

No son autoridad semántica de TSIS.

---

# 9. Estrategia de construcción

```text
V0 — Single-Experiment Vertical Slice
V1 — Tabular Backtest Foundation
V2 — Point-in-Time Universe Authority
V3 — Execution and Portfolio Realism
V4 — Experiment and Evidence Registry
V5 — Scientific Validation
V6 — Event Research
V7 — Market State and Event State
V8 — ML Research
V9 — Event-Driven Intraday Engine
V10 — Trades, Quotes and Microstructure
V11 — IRL, Offline RL and Evolution Systems
V12 — Independent Replication and Publication
```

---

# 10. Primer experimento autorizado

```text
Experiment:
Daily In-Play Open-to-Close

Universe:
Stocks classified as In Play
using only information available
before the official market open.

Entry:
First valid executable regular-session opening price.

Exit:
Last valid executable regular-session closing price.

Direction:
Long.

Output:
One auditable row per symbol and session.

Validation:
Manual reconstruction, costs, exclusions,
subperiods, sensitivity and holdout.
```

---

# 11. Árbol del proyecto

```text
TSIS_SCIENTIFIC_RESEARCH_LABORATORY/
│
├── README.md
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── .env.example
├── Makefile
│
├── configs/
│   ├── datasets/
│   ├── price_views/
│   ├── universes/
│   ├── strategies/
│   ├── execution/
│   ├── portfolios/
│   ├── experiments/
│   ├── validation/
│   └── environments/
│
├── docs/
│   ├── 00_system/
│   │   ├── TSIS_SCIENTIFIC_RESEARCH_LABORATORY_SYSTEM_MAP_V0_1.md
│   │   ├── TSIS_BACKTEST_ENGINE_SYSTEM_MAP_V0_1.md
│   │   ├── ARCHITECTURE_PRINCIPLES.md
│   │   ├── COMPONENT_BOUNDARIES.md
│   │   └── TERMINOLOGY.md
│   │
│   ├── 01_data/
│   ├── 02_universe/
│   ├── 03_representation/
│   ├── 04_events/
│   ├── 05_strategies/
│   ├── 06_execution/
│   ├── 07_portfolio/
│   ├── 08_validation/
│   ├── 09_evidence/
│   ├── 10_knowledge/
│   └── 11_research_dossiers/
│
├── src/
│   └── tsis/
│       │
│       ├── __init__.py
│       │
│       ├── common/
│       │   ├── ids.py
│       │   ├── enums.py
│       │   ├── exceptions.py
│       │   ├── hashing.py
│       │   ├── logging.py
│       │   ├── paths.py
│       │   ├── serialization.py
│       │   └── types.py
│       │
│       ├── governance/
│       │   ├── research_question.py
│       │   ├── hypothesis.py
│       │   ├── authorization.py
│       │   ├── decision_record.py
│       │   └── limitations.py
│       │
│       ├── data_authority/
│       │   ├── dataset_contract.py
│       │   ├── dataset_registry.py
│       │   ├── schema_registry.py
│       │   ├── source_registry.py
│       │   ├── lineage.py
│       │   ├── validators.py
│       │   └── known_failures.py
│       │
│       ├── dataset_resolution/
│       │   ├── dataset_resolver.py
│       │   ├── price_view_resolver.py
│       │   ├── partition_resolver.py
│       │   ├── repair_manifest.py
│       │   └── resolution_manifest.py
│       │
│       ├── temporal/
│       │   ├── trading_calendar.py
│       │   ├── sessions.py
│       │   ├── timestamps.py
│       │   ├── timezone.py
│       │   ├── availability.py
│       │   └── temporal_legality.py
│       │
│       ├── securities/
│       │   ├── security_master.py
│       │   ├── lifecycle.py
│       │   ├── ticker_history.py
│       │   ├── listings.py
│       │   ├── delistings.py
│       │   └── corporate_actions.py
│       │
│       ├── universe/
│       │   ├── specification.py
│       │   ├── point_in_time.py
│       │   ├── in_play.py
│       │   ├── eligibility.py
│       │   ├── exclusions.py
│       │   ├── membership.py
│       │   └── manifest.py
│       │
│       ├── data_quality/
│       │   ├── missing_data.py
│       │   ├── irregular_bars.py
│       │   ├── bad_prints.py
│       │   ├── quote_guard.py
│       │   ├── halts.py
│       │   ├── late_opens.py
│       │   ├── repairs.py
│       │   └── exceptions_ledger.py
│       │
│       ├── loaders/
│       │   ├── daily_loader.py
│       │   ├── bars_1m_loader.py
│       │   ├── trades_loader.py
│       │   ├── quotes_loader.py
│       │   ├── news_loader.py
│       │   ├── fundamentals_loader.py
│       │   ├── short_loader.py
│       │   ├── halts_loader.py
│       │   └── reference_loader.py
│       │
│       ├── features/
│       │   ├── feature_definition.py
│       │   ├── feature_registry.py
│       │   ├── feature_builder.py
│       │   ├── feature_availability.py
│       │   ├── daily/
│       │   ├── intraday/
│       │   ├── microstructure/
│       │   └── context/
│       │
│       ├── information_objects/
│       │   ├── registry.py
│       │   ├── price_movement.py
│       │   ├── trading_activity.py
│       │   ├── volatility_range_state.py
│       │   ├── liquidity.py
│       │   ├── market_microstructure_state.py
│       │   ├── order_flow_pressure.py
│       │   ├── news_catalyst_context.py
│       │   ├── fundamental_context.py
│       │   ├── short_side_context.py
│       │   ├── broad_market_context.py
│       │   ├── halt_context.py
│       │   └── intraday_position.py
│       │
│       ├── representation/
│       │   ├── market_state.py
│       │   ├── event_state.py
│       │   ├── state_builder.py
│       │   ├── state_snapshot.py
│       │   ├── observability.py
│       │   └── causality_guard.py
│       │
│       ├── events/
│       │   ├── event_definition.py
│       │   ├── event_registry.py
│       │   ├── event_detector.py
│       │   ├── event_instance.py
│       │   ├── event_table.py
│       │   ├── outcome_engine.py
│       │   ├── outcome_table.py
│       │   ├── transitions.py
│       │   └── clustering.py
│       │
│       ├── strategies/
│       │   ├── specification.py
│       │   ├── registry.py
│       │   ├── decision.py
│       │   ├── decision_engine.py
│       │   ├── parameters.py
│       │   ├── sizing.py
│       │   ├── rules/
│       │   └── open_to_close/
│       │
│       ├── orders/
│       │   ├── order_intent.py
│       │   ├── order.py
│       │   ├── order_state.py
│       │   ├── order_types.py
│       │   └── order_ledger.py
│       │
│       ├── execution/
│       │   ├── simulator.py
│       │   ├── fill_model.py
│       │   ├── fill.py
│       │   ├── spread_model.py
│       │   ├── slippage_model.py
│       │   ├── latency_model.py
│       │   ├── liquidity_model.py
│       │   ├── participation.py
│       │   ├── partial_fills.py
│       │   ├── intrabar_paths.py
│       │   ├── halt_policy.py
│       │   ├── locate_model.py
│       │   ├── borrow_model.py
│       │   ├── fee_model.py
│       │   └── execution_ledger.py
│       │
│       ├── portfolio/
│       │   ├── portfolio.py
│       │   ├── position.py
│       │   ├── cash.py
│       │   ├── accounting.py
│       │   ├── cost_basis.py
│       │   ├── exposure.py
│       │   ├── constraints.py
│       │   ├── equity.py
│       │   └── ledgers.py
│       │
│       ├── engines/
│       │   ├── tabular/
│       │   │   ├── engine.py
│       │   │   ├── entry_exit_resolver.py
│       │   │   └── trade_builder.py
│       │   │
│       │   ├── vectorized/
│       │   │   ├── engine.py
│       │   │   ├── matrices.py
│       │   │   ├── scenario_grid.py
│       │   │   └── sensitivity.py
│       │   │
│       │   └── event_driven/
│       │       ├── engine.py
│       │       ├── clock.py
│       │       ├── event_queue.py
│       │       ├── dispatcher.py
│       │       ├── market_events.py
│       │       └── state_machine.py
│       │
│       ├── metrics/
│       │   ├── performance.py
│       │   ├── drawdowns.py
│       │   ├── risk.py
│       │   ├── trade_statistics.py
│       │   ├── capacity.py
│       │   ├── concentration.py
│       │   ├── mae_mfe.py
│       │   └── diagnostics.py
│       │
│       ├── validation/
│       │   ├── chronological_holdout.py
│       │   ├── walk_forward.py
│       │   ├── parameter_stability.py
│       │   ├── cost_stress.py
│       │   ├── execution_stress.py
│       │   ├── universe_perturbation.py
│       │   ├── subperiods.py
│       │   ├── regimes.py
│       │   ├── bootstrap.py
│       │   ├── multiple_testing.py
│       │   ├── pbo.py
│       │   ├── dsr.py
│       │   └── replication.py
│       │
│       ├── experiments/
│       │   ├── experiment_spec.py
│       │   ├── run_spec.py
│       │   ├── runner.py
│       │   ├── run_manifest.py
│       │   ├── environment_manifest.py
│       │   ├── artifact_registry.py
│       │   └── reproducibility.py
│       │
│       ├── ml/
│       │   ├── datasets.py
│       │   ├── splits.py
│       │   ├── training.py
│       │   ├── predictions.py
│       │   ├── evaluation.py
│       │   ├── model_registry.py
│       │   ├── supervised/
│       │   ├── clustering/
│       │   ├── transformers/
│       │   ├── irl/
│       │   └── offline_rl/
│       │
│       ├── evolution/
│       │   ├── candidate.py
│       │   ├── evaluator.py
│       │   ├── search_space.py
│       │   ├── constraints.py
│       │   ├── alphaevolve_adapter.py
│       │   ├── openevolve_adapter.py
│       │   └── evolution_registry.py
│       │
│       ├── evidence/
│       │   ├── evidence_item.py
│       │   ├── evidence_registry.py
│       │   ├── casepack.py
│       │   ├── chart_evidence.py
│       │   ├── table_evidence.py
│       │   ├── contradictory_evidence.py
│       │   └── audit_trail.py
│       │
│       ├── knowledge/
│       │   ├── finding.py
│       │   ├── phenomenon.py
│       │   ├── knowledge_claim.py
│       │   ├── knowledge_registry.py
│       │   ├── confidence.py
│       │   ├── scope.py
│       │   ├── dependencies.py
│       │   └── lifecycle.py
│       │
│       ├── reports/
│       │   ├── run_report.py
│       │   ├── metrics_report.py
│       │   ├── robustness_report.py
│       │   ├── limitations_report.py
│       │   ├── research_dossier.py
│       │   └── publication_export.py
│       │
│       └── cli/
│           ├── main.py
│           ├── run_experiment.py
│           ├── validate_dataset.py
│           ├── build_universe.py
│           ├── run_backtest.py
│           └── build_dossier.py
│
├── notebooks/
│   ├── 00_sandbox/
│   ├── 01_data_inspection/
│   ├── 02_universe_research/
│   ├── 03_event_research/
│   ├── 04_strategy_prototypes/
│   ├── 05_case_reconstruction/
│   ├── 06_validation/
│   ├── 07_ml_research/
│   └── 08_publication/
│
├── experiments/
│   ├── EXP_0001_INPLAY_OPEN_TO_CLOSE/
│   │   ├── hypothesis.md
│   │   ├── experiment.yaml
│   │   ├── strategy.yaml
│   │   ├── universe.yaml
│   │   ├── execution.yaml
│   │   ├── validation.yaml
│   │   ├── notebooks/
│   │   ├── runs/
│   │   └── dossier/
│   │
│   └── templates/
│
├── outputs/
│   ├── datasets/
│   ├── universes/
│   ├── features/
│   ├── states/
│   ├── events/
│   ├── outcomes/
│   ├── experiments/
│   ├── evidence/
│   ├── knowledge/
│   └── reports/
│
├── registries/
│   ├── datasets/
│   ├── schemas/
│   ├── features/
│   ├── information_objects/
│   ├── events/
│   ├── strategies/
│   ├── experiments/
│   ├── models/
│   ├── evidence/
│   └── knowledge/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── temporal/
│   ├── accounting/
│   ├── execution/
│   ├── reproducibility/
│   ├── regression/
│   ├── property/
│   ├── fixtures/
│   └── hand_calculated_cases/
│
├── scripts/
│   ├── bootstrap_project.py
│   ├── validate_environment.py
│   ├── validate_datasets.py
│   ├── build_universe.py
│   ├── run_experiment.py
│   ├── run_validation.py
│   └── build_research_dossier.py
│
├── sql/
│   ├── data_quality/
│   ├── universes/
│   ├── features/
│   ├── events/
│   ├── experiments/
│   └── validation/
│
└── infrastructure/
├── docker/
├── environments/
├── mlflow/
├── orchestration/
├── profiling/
└── ci/
```

---

# 12. Árbol que debe existir al comenzar

El árbol anterior representa la arquitectura objetivo.

No debe crearse físicamente entero desde el primer día.

Para el primer experimento solo debe materializarse:

```text
TSIS_SCIENTIFIC_RESEARCH_LABORATORY/
│
├── README.md
├── pyproject.toml
├── configs/
│   ├── datasets/
│   ├── universes/
│   ├── strategies/
│   ├── execution/
│   └── experiments/
│
├── docs/
│   └── 00_system/
│
├── src/
│   └── tsis/
│       ├── common/
│       ├── data_authority/
│       ├── dataset_resolution/
│       ├── temporal/
│       ├── universe/
│       ├── loaders/
│       ├── strategies/
│       │   └── open_to_close/
│       ├── execution/
│       ├── portfolio/
│       ├── engines/
│       │   └── tabular/
│       ├── metrics/
│       ├── validation/
│       ├── experiments/
│       └── reports/
│
├── notebooks/
│   ├── 01_data_inspection/
│   ├── 02_universe_research/
│   ├── 04_strategy_prototypes/
│   ├── 05_case_reconstruction/
│   └── 06_validation/
│
├── experiments/
│   └── EXP_0001_INPLAY_OPEN_TO_CLOSE/
│
├── outputs/
│   ├── universes/
│   ├── experiments/
│   └── reports/
│
└── tests/
├── unit/
├── integration/
├── accounting/
├── reproducibility/
└── hand_calculated_cases/
```

---

# 13. Regla de crecimiento

```text
Una carpeta o componente solo se materializa
cuando existe una necesidad científica concreta,
un contrato definido
y una prueba que demuestre su comportamiento.
```

El mapa completo define el destino.

El árbol mínimo define el punto de partida.

---

# 14. Resultado esperado

TSIS debe poder responder para cualquier conclusión:

```text
¿Qué pregunta intentábamos responder?

¿Qué hipótesis se congeló?

¿Qué datos se utilizaron?

¿Qué universo existía?

¿Qué información era observable?

¿Qué transformaciones se aplicaron?

¿Qué operaciones se simularon?

¿Qué hipótesis de ejecución se utilizaron?

¿Qué resultado se obtuvo?

¿Qué pruebas de robustez superó?

¿Qué limitaciones conserva?

¿Qué evidencia sostiene la conclusión?

¿Puede reproducirse exactamente?
```

Cuando todas estas preguntas puedan responderse, TSIS no será únicamente un motor de backtesting.

Será un laboratorio científico de investigación histórica.
