# Market State / Event State Composition Contract v0.1

## 2026-07-07 Quotes Root Supersession

`D:/quotes -> E:/TSIS/data/quotes_` is closed and approved. The official quotes E-root for new downstream work is `E:/TSIS/data/quotes_`, backed by Phase A structural parity and Phase B SHA256 retry evidence. Historical artifacts built from `D:/quotes` remain pre-approval/provenance evidence and must be rebuilt against the approved E-root before promotion to an official downstream table. The legacy `E:/TSIS/data/quotes` tree remains incomplete for this decision.


## Estado

Tipo: composition contract skeleton.

Modulo: `01_TSIS_backtest_SmallCaps`.

Ambito: `CAPA 1 - DATA FOUNDATION`.

Status:

```text
composition_contract_defined
market_state_table_materialized = false
event_state_table_materialized = false
builder_implemented = false
```

Este contrato define como deben componerse:

```text
market_state_table_v0_1
event_state_table_v0_1
```

No materializa datos.
No crea un builder.
No habilita ML/RL directo.
No convierte context tables en estado por si solas.

Contrato companion obligatorio sobre cobertura, scanner diario y lookbacks:

```text
01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
```

## Decision Central

TSIS no debe tratar `OHLCV` como el estado completo del mercado.

La unidad cientifica que necesita TSIS es:

```text
State =
representacion legal, trazable y as-of de todo lo necesario para decidir,
sin labels, outcomes, acciones, rewards ni informacion futura.
```

Por tanto:

```text
market_state_table
  = snapshot as-of de componentes de mercado/instrumento/contexto

event_state_table
  = vista event-scoped de market_state para una decision concreta

outcomes_table
  = labels/y/resultados posteriores, separados de features/X
```

Regla:

```text
state != signal
state != strategy
state != outcome
state != reward
state != execution fill
```

Tambien queda fijado:

```text
daily_in_play != market_state completo
full_history_context != microstructure full-universe ciega
event_window_microstructure != universo completo
```

La politica de cobertura y lookback obliga a combinar:

- contexto full-history compacto;
- candidatos diarios/en-evento;
- microestructura pesada solo en ventanas gobernadas;
- lookback features as-of para estrategias que dependen de memoria historica.

## Por Que Existe Este Contrato

TSIS esta construyendo una maquina que aprende por estados.

Eso exige que cada evento pueda reconstruirse como:

```text
instrument identity
+ calendar/session
+ price context
+ intraday context when legal
+ microstructure context when legal
+ halt/interruption context
+ fundamentals as-of
+ news/catalyst as-of
+ short pressure as-of/lagged
+ short-sale constraints when sourced
+ regime context as-of
+ quality gates
= event/market state
```

Sin este contrato, futuros agentes podrian:

- mezclar features con labels;
- usar datos posteriores al evento;
- usar same-session daily aggregates como si fueran pre-evento;
- inferir borrow/locate desde short volume;
- usar outputs scoped/seed como full-universe;
- entrenar ML/RL sobre filas sin cutoff legal;
- o producir un dataset de estados imposible de auditar.

## Relacion Entre Tablas

### `market_state_table`

Unidad:

```text
instrument_id + decision_timestamp_utc + state_horizon + state_schema_version
```

Rol:

```text
snapshot reusable de estado de mercado/instrumento bajo un cutoff temporal
```

Debe contener:

- identificadores;
- decision timestamp;
- estado de componentes;
- features as-of;
- quality flags;
- lineage por componente;
- version de builder y schema;
- flags de consumo permitido/restringido.

No debe contener:

- labels;
- returns futuros;
- outcomes;
- rewards;
- acciones;
- fills;
- PnL;
- seniales de estrategia;
- decisiones de entrada/salida.

### `event_state_table`

Unidad:

```text
event_id or event_window_id + decision_timestamp_utc + state_role + state_schema_version
```

Rol:

```text
vista de market_state anclada a un evento y a un momento de decision
```

Debe contener:

- `event_id` / `event_window_id`;
- decision timestamp;
- role de estado, por ejemplo `pre_event`, `at_event`, `post_event_review`;
- foreign keys hacia `market_state_table`;
- event-window metadata legal;
- component availability;
- leakage gates;
- feature namespace version.

No debe contener:

- outcome values;
- label columns;
- reward columns;
- estrategia;
- accion;
- fill simulation.

Puede contener una llave de join hacia labels, pero no los valores de label:

```text
outcome_join_key_allowed = true
outcome_values_inline_allowed = false
```

## Componentes Actuales

Esta tabla define el estado actual de composicion. No todos los componentes
tienen el mismo nivel de readiness.

| Component | Current source | Current role | State use today |
| --- | --- | --- | --- |
| Identity | `instrument_master_v0_1` | ticker/instrument identity | allowed with flags |
| Calendar | `market_calendar_v0_1` | session boundaries | allowed |
| Expected coverage | `expected_data_calendar_v0_1` | denominator/absence context | allowed as quality context |
| Dataset gates | `dataset_certification_matrix_v0_1` | family-level quality gate | allowed as quality context |
| Corporate actions | `corporate_actions_table_v0_1` | split/dividend/ticker-change context | allowed |
| Scanner candidates | `daily_scanner_candidates_table_v0_1` target | in-play/candidate-set lineage | not materialized; seed only after validator gates |
| Daily price | `master_daily_table_v0_1` | daily context and price views | allowed with price-view policy |
| Intraday bars | `master_intraday_bar_table_v0_1` | scoped 1m pilot/event cases | scoped only, not full-universe |
| Microstructure | `microstructure_features_table_v0_1` | one seed window smoke proof | not trainable, not primary state |
| Halts | `halts_table_v0_1` | interruption/halt context | allowed with timestamp legality |
| Event windows | `event_windows_table_v0_1` | event boundaries | allowed as boundary, not feature label |
| Outcomes | `outcomes_table_v0_1` | labels/y | prohibited as feature |
| Fundamentals | `fundamentals_asof_table_v0_1` | filing-date-aware context | allowed only after as-of join |
| News | `news_context_table_v0_1` | published-utc catalyst context | allowed only after as-of join |
| Short context | `short_context_table_v0_1` | short interest/short volume context | allowed only after source/as-of/lag rules |
| Regime | `regime_context_table_v0_1` | session-close regime context | allowed only after as-of join |
| Short constraints | target/runbook only | SSR/borrow/locate/availability | blocked until source exists |
| Real-time alerts | not materialized | offerings/filings/newswire live alerts | blocked until source/feed/latency contract |

## Microstructure Source Root Policy

As of `2026-06-29`, the next controlled state-table loop may use
`D:/quotes` as a provisional quote source through the upstream
`microstructure_features_table` candidate path.

Required lineage:

```text
quotes_root_used = D:/quotes
quotes_root_state = pre_approval_d_recovery_lineage_requires_rebuild
target_official_quotes_root = E:/TSIS/data/quotes_
legacy_incomplete_e_quotes_root = E:/TSIS/data/quotes
requires_rebuild_after_quotes_root_approval = true
```

Allowed use:

```text
controlled candidate samples
market-state/event-state builder tests
forensic/debug readouts
component integration validation
```

Prohibited use while this root state remains provisional:

```text
institutional promotion
ML/RL primary training
backtest-core direct source
execution simulation truth
claiming official E-root parity
```

Any `market_state_table` or `event_state_table` candidate that consumes
microstructure derived from `D:/quotes` must preserve the upstream root state
in row-level lineage or in the manifest and must be recomputable after
`E:/TSIS/data/quotes_` parity/audit is complete. `E:/TSIS/data/quotes` is an
incomplete/legacy E-root for this recovery decision, not the official target.

## Mandatory As-Of Rules

Every component must be selected by:

```text
component_as_of_utc <= decision_timestamp_utc
```

Where the source uses dates instead of timestamps, the builder must apply the
component-specific availability rule from the source consumption policy.

Examples:

```text
fundamentals_asof_table: filing_date / as_of_date <= decision cutoff
news_context_table: published_utc <= decision cutoff
short_context_table: as_of_date plus required lag model <= decision cutoff
regime_context_table: as_of_utc <= decision cutoff
outcomes_table: never a feature source
```

Same-session completed aggregates are prohibited before they are legally
available:

```text
same_session_daily_close_as_pre_event_feature = false
same_session_regime_close_as_intraday_feature = false
```

## Required Output Roots

Future materialized outputs must live under:

```text
E:/TSIS/data/data_foundation_outputs/market_state_table/
E:/TSIS/data/data_foundation_outputs/event_state_table/
```

They must not live in:

```text
C:/TSIS_Data/data/
notebooks/
runtime caches
raw/source folders
```

## Minimum `market_state_table` Schema Skeleton

Required identity fields:

```text
market_state_id
instrument_id
ticker
decision_timestamp_utc
decision_date
state_horizon
state_scope
state_schema_version
state_builder_version
state_quality_state
```

Required lineage fields:

```text
build_run_id
created_at_utc
component_manifest_hash_bundle
component_build_run_id_bundle
component_quality_bundle
component_availability_bundle
source_cutoff_policy_version
leakage_policy_version
```

Required gate fields:

```text
valid_for_event_context_candidate
valid_for_ml_feature_candidate
valid_for_backtest_context_candidate
valid_for_rl_state_candidate
valid_for_execution_simulator_direct
contains_future_information_without_event_filter
requires_asof_filter
full_universe_claim
```

Feature namespaces must be explicit:

```text
identity__*
calendar__*
daily__*
intraday__*
microstructure__*
halt__*
fundamentals__*
news__*
short_context__*
short_constraints__*
regime__*
quality__*
```

No un-namespaced feature column is allowed.

## Minimum `event_state_table` Schema Skeleton

Required identity fields:

```text
event_state_id
event_id
event_window_id
market_state_id
instrument_id
ticker
event_family
event_timestamp_utc
decision_timestamp_utc
state_role
state_schema_version
state_builder_version
```

Required event anchoring fields:

```text
event_window_start_utc
event_window_end_utc
pre_event_window_start_utc
pre_event_window_end_utc
state_cutoff_utc
state_cutoff_reason
```

Required label-separation fields:

```text
outcome_join_key
outcome_values_inline_allowed = false
label_columns_inline_allowed = false
reward_columns_inline_allowed = false
```

Required consumer gates:

```text
valid_for_pattern_discovery
valid_for_ml_feature_candidate
valid_for_rl_state_candidate
valid_for_backtest_context_candidate
valid_for_execution_context_candidate
```

## State Quality States

Allowed initial quality states:

```text
state_good_for_declared_cutoff
state_review_missing_optional_component
state_review_scoped_intraday_component
state_review_microstructure_seed_only
state_review_short_constraints_missing
state_blocked_future_information_detected
state_blocked_required_component_missing
state_blocked_invalid_component_quality
state_bad_duplicate_state_id
state_bad_missing_decision_timestamp
```

Hard failures:

- duplicated `market_state_id` or `event_state_id`;
- missing decision timestamp;
- any component with as-of after decision timestamp;
- inline outcome/label/reward fields inside feature state;
- use of `microstructure_features_table_v0_1` as primary full-universe state;
- use of `master_intraday_bar_table_v0_1` as full-universe intraday state;
- use of `short_context_table_v0_1` as borrow/SSR/locate evidence;
- use of `regime_context_table_v0_1` same-session close aggregate before close.

## Builder Requirements

Future builder:

```text
scripts/materialize_market_state_table.py
scripts/materialize_event_state_table.py
```

must require a config such as:

```text
configs/data_foundation_outputs/market_state_builder_v0_1.yaml
configs/data_foundation_outputs/event_state_builder_v0_1.yaml
```

The config must declare:

- event families included;
- decision timestamps;
- state horizons;
- required components;
- optional components;
- as-of policies;
- lag policies;
- component quality masks;
- output partitioning;
- materialization scope;
- full-universe claim status.

No default builder may silently include all rows from every upstream table.

## Validation Requirements

Before materialization, future agents must create:

```text
01_foundations/canonical_schemas/outputs/market_state_table_schema_contract.md
01_foundations/canonical_schemas/outputs/event_state_table_schema_contract.md
01_foundations/contract_registry/dataset_contracts/market_state_table_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/event_state_table_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/market_state_table_consumption_policy.md
01_foundations/data_consumption_policies/event_state_table_consumption_policy.md
01_foundations/dataset_registry/outputs/market_state_table_registry_entry.yaml
01_foundations/dataset_registry/outputs/event_state_table_registry_entry.yaml
01_foundations/validators/outputs/market_state_table_validators.md
01_foundations/validators/outputs/event_state_table_validators.md
tests/data_foundation_outputs/test_market_state_table_contract.py
tests/data_foundation_outputs/test_event_state_table_contract.py
```

Validation must prove:

- schema and required namespaces;
- unique keys;
- no future component as-of;
- no label/outcome/reward columns inside feature state;
- manifest/tree hashes;
- component manifest hashes;
- row counts by state role/horizon/event family;
- quality-state distribution;
- consumer-gate counts;
- deterministic recomputation for a small fixture;
- adversarial leakage cases fail.

## ML Boundary

For supervised ML:

```text
X = event_state_table / market_state_table features under legal cutoff
y = outcomes_table or other label table joined separately
```

The training dataset builder must keep:

```text
feature_table != label_table
```

and must emit:

```text
feature_manifest
label_manifest
join_manifest
leakage_check_manifest
```

## RL Boundary

`event_state_table_v0_1` is not an RL dataset by itself.

RL requires a separate transition/evaluator layer:

```text
state_t
action_t
reward_t
state_t_plus_1
done
execution_simulation_context
policy_constraints
```

Therefore:

```text
valid_for_rl_state_candidate may become true only after state gates pass
valid_for_rl_training_direct remains false until transition/reward contracts exist
```

## Current Readiness

Current state:

```text
15 CAPA 1 outputs are materialized for declared v0.1 scopes.
market_state_table_v0_1 is not materialized.
event_state_table_v0_1 is not materialized.
market_state_table_v0_1_candidate_microstructure_halt_controlled is materialized as controlled_candidate_not_promoted.
event_state_table_v0_1_candidate_microstructure_halt_controlled is materialized as controlled_candidate_not_promoted.
short_sale_constraints_table_v0_1 is blocked by missing SSR/borrow/locate source.
real_time_corporate_event_alerts_table_v0_1 is blocked by live/vendor/feed semantics.
microstructure_features_table_v0_1 is seed-only.
master_intraday_bar_table_v0_1 is scoped-only.
```

Allowed next work:

```text
expand controlled candidates, strengthen as-of joins, add coverage gates,
rebuild after E:/TSIS/data/quotes_ parity, and only then evaluate promotion.
```

Blocked claim:

```text
TSIS has a final institutional market_state dataset
```

## Promotion Barrier

No future agent may mark either table as materialized or institutional until:

- schema contracts exist;
- dataset contracts exist;
- registry entries exist;
- consumption policies exist;
- validators exist;
- builders exist;
- manifests exist;
- tests pass;
- Graphify queue is updated;
- changelog is updated;
- all component source versions are declared;
- leakage/adversarial tests are recorded.

## Regla Final

The state layer exists to make event decisions scientifically auditable.

It must answer:

```text
At this exact decision time, for this instrument and event,
what was legally knowable, from which governed source,
with what quality, and under what restrictions?
```

If a future table cannot answer that, it is not a TSIS state table.
