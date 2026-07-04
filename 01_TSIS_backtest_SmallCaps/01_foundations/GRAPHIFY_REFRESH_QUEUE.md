# Graphify Refresh Queue for 01_foundations

Fecha de creacion: 2026-06-19
Estado: cola operativa versionada para refrescos Graphify de `01_foundations`.

## Rol

Este archivo evita tratar Graphify como si fuera Git.

Git registra cambios continuamente. Graphify se refresca por hitos semanticos,
por severidad o por lote.

Regla:

```text
No actualizar Graphify por cada commit.
Actualizar Graphify cuando el cambio altere el mapa semantico que un agente
necesita consultar.
```

El protocolo autoritativo vive en:

```text
GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
```

La definicion metodologica de slices vive en:

```text
module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md
```

## Severidad de refresco

### LOW

No requiere Graphify.

Ejemplos:

- typo;
- README menor;
- limpieza textual;
- nota privada o no promovida;
- cambio que no altera contratos, schemas, registries, policies ni validators.

Accion:

```text
No hacer nada en Graphify.
```

### MEDIUM

Se anota en esta cola, pero no se refresca inmediatamente.

Ejemplos:

- nuevo documento explicativo;
- nuevo README funcional;
- ampliacion documental sin cambio contractual;
- evidencia ligera no promovida;
- ajuste de navegacion que afecta como un agente encuentra documentos.

Accion:

```text
Anotar entrada pending.
Refrescar cuando haya lote suficiente o una consulta lo necesite.
```

### HIGH

Requiere rebuild del leaf afectado en una ventana dedicada.

Ejemplos:

- nuevo dataset contract;
- nuevo schema canonico;
- nueva data consumption policy;
- validator que cambia aceptacion;
- closeout que cambia interpretacion;
- nuevo protocolo transversal de tablas;
- nuevo graph slice.

Accion:

```text
Construir o actualizar leaf oficial.
No actualizar root si no es necesario para la tarea inmediata.
```

### CRITICAL

Requiere decision explicita antes de tocar el root.

Ejemplos:

- renombrar carpetas ya indexadas;
- eliminar o migrar rutas indexadas;
- cambiar semantica de dataset;
- cambiar price semantics;
- cambiar certification/recovery state;
- promocionar master table;
- cambiar consumo downstream.

Accion:

```text
Construir leaf si aporta valor inmediato.
No hacer merge aditivo si el root conserva nodos antiguos.
Integrar root solo mediante rebuild controlado o reemplazo oficial de slice.
```

## Cadencia recomendada

```text
Diario:
  Git normal.
  Documentar cambios relevantes.
  Anotar pending refresh si aplica.

Por hito:
  Rebuild de leaves afectados.

Por ventana dedicada:
  Integracion limpia del root si hace falta.
```

## Entradas activas

### GFQ-20260704-minute-data-plane-reading

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
01_foundations/data_plane_physical_authority
01_foundations/price_views_and_intraday_consumption
01_TSIS_backtest_SmallCaps/agent_bootstrap
```

Reason:

```text
The project now requires all agents to read E:/TSIS/data/README.md as base
context, and Module 01 agents must read it before data/price work. For
minute/OHLCV 1m, E:/TSIS/data/ohlcv_1m is the canonical physical root. This must
be visible in Graphify because it governs scanners, intraday backtests,
quote-guarded overlays, feature/state builders and any future minute-consuming
agent workflow.
```

Changed paths:

```text
E:/TSIS/data/README.md
C:/TSIS_Data/README.md
C:/TSIS_Data/AGENTS.md
C:/TSIS_Data/START_HERE.md
C:/TSIS_Data/CHANGELOG.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/AGENTS.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Refresh the foundations outputs/data-plane leaf so graph queries route minute
work through E:/TSIS/data/README.md and E:/TSIS/data/ohlcv_1m before downstream
contracts or scripts are interpreted.
```

Root action:

```text
No immediate root rebuild. Include in the next official foundations leaf refresh.
```
### GFQ-20260701-001 - Market calendar expected calendar master daily 2026 governed range

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
data_foundation_outputs_graph
market_calendar_governance_graph
master_daily_table_governance_graph
event_discovery_graph
market_state_representation_graph
```

Why:

- Extended active `market_calendar_v0_1`, `expected_data_calendar_v0_1` and
  `master_daily_table_v0_1` materializations from the previous `2025-12-31`
  endpoint to the current governed source limit `2026-03-09`.
- Updated active build lineage:
  - `market_calendar_v0_1_20260630T193931Z`
  - `expected_data_calendar_v0_1_20260630T194807Z`
  - `master_daily_table_v0_1_20260630T201044Z`
- Updated row counts:
  - `market_calendar_v0_1`: 5,328 rows
  - `expected_data_calendar_v0_1`: 29,478,796 rows
  - `master_daily_table_v0_1`: 22,109,097 rows
- Added DuckDB spill/temp-directory execution support to expected-calendar and
  master-daily materializers so the wider output can complete without OOM.
- Updated the market-calendar builder/materializer defaults away from the old
  `20251231` source.
- Preserved the explicit limitation: this is not coverage through
  `2026-06-30`; later dates require a new governed source extension.

Changed paths:

```text
01_TSIS_backtest_SmallCaps/scripts/agent05_build_market_calendar_official.py
01_TSIS_backtest_SmallCaps/scripts/materialize_market_calendar.py
01_TSIS_backtest_SmallCaps/scripts/materialize_expected_data_calendar.py
01_TSIS_backtest_SmallCaps/scripts/materialize_master_daily_table.py
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_market_calendar_contract.py
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_expected_data_calendar_contract.py
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_master_daily_table_contract.py
01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/market_calendar_registry_entry.yaml
01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/expected_data_calendar_registry_entry.yaml
01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/master_daily_table_registry_entry.yaml
01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/market_calendar_dataset_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/master_daily_table_dataset_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/market_calendar_schema_contract.md
01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/expected_data_calendar_schema_contract.md
01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/market_calendar_consumption_policy.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md
```

External/output artifacts:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/data/reference/market_calendar_official_XNYS_20050101_20260309.parquet
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/data/reference/market_calendar_official_XNYS_20050101_20260309.meta.json
E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet
E:/TSIS/data/data_foundation_outputs/expected_data_calendar/expected_data_calendar_v0_1/
E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1/
E:/TSIS/data/data_foundation_outputs/_backups/20260630_extend_calendar_daily_to_20260309/
```

Validation:

```text
python -m pytest C:/TSIS_Data/01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_market_calendar_contract.py C:/TSIS_Data/01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_expected_data_calendar_contract.py C:/TSIS_Data/01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_master_daily_table_contract.py -q
result = 12 passed
```

Recommended action:

```text
Refresh the Data Foundation outputs leaf so graph users no longer infer the
older 2025-12-31 endpoint for calendar, expected coverage or master daily.
```

Root action:

```text
No immediate root rebuild. Include in the next official foundations leaf refresh
or root integration batch.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

### GFQ-20260630-daily-scanner-v0-3-in-play-momentum

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
data_foundation_outputs_graph
event_discovery_graph
market_state_representation_graph
strategy_research_graph
ml_feature_governance_graph
offline_rl_governance_graph
```

Why:

- Implemented the active `daily_scanner_candidates_table_v0_3` controlled
  builder model.
- Replaced the ambiguous v0.2 profile model with two explicit denominators:
  `base_eligible_smallcap_denominator_v0_3` and
  `in_play_momentum_candidate_denominator_v0_3`.
- Clarified that base eligible rows are only observable smallcap rows, not
  in-play candidates.
- Clarified that in-play momentum candidates require strong movement and
  tradability.
- Set the initial strong-move threshold to `50%`.
- Kept `trade_station_like_profile_v0_3` as operator visibility only.
- Removed DAS from the global scanner; DAS and future strategies must consume
  the scanner output through strategy overlays.
- Marked the controlled replay as `daily_eod_proxy`; it cannot certify
  premarket/regular/after-hours first-push timing until an intraday segment
  builder exists.
- Ran controlled replay
  `daily_scanner_candidates_replay_20250102_20250110_v0_3_0_in_play_momentum`
  under `C:/TSIS_Data/tests/test_runs/2026-06-30/`, producing 15,323 rows,
  6,184 base eligible rows, 69 selected in-play momentum candidates, 150
  TradeStation-like profile rows, zero DAS rows, zero selected rows without
  50% movement and zero selected rows without tradability.

Changed paths:

```text
01_TSIS_backtest_SmallCaps/scripts/materialize_daily_scanner_candidates_table_v0_3.py
01_TSIS_backtest_SmallCaps/scripts/run_daily_scanner_candidates_materialization_v0_3.ps1
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder_v0_3.py
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/README.md
01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/scanner_definitions/base_eligible_smallcap_denominator_v0_3.yaml
01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/scanner_definitions/in_play_momentum_candidate_denominator_v0_3.yaml
01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/scanner_definitions/trade_station_like_profile_v0_3.yaml
01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/scanner_definitions/README.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_3.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_3.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/daily_scanner_candidates_table_schema_contract.md
01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/daily_scanner_candidates_table_dataset_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/daily_scanner_candidates_table_consumption_policy.md
01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/daily_scanner_candidates_table_registry_entry.yaml
01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/daily_scanner_candidates_table_validators.md
01_TSIS_backtest_SmallCaps/01_research/README.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Refresh the Data Foundation outputs/scanner leaf so graph queries distinguish
v0.3 active scanner semantics from historical v0.1/v0.2 evidence.
```

Root action:

```text
No immediate root rebuild. Include in the next official foundations leaf refresh
or root integration batch.
```

Owner:

```text
Modulo 01 / Data Foundation outputs scanner governance
```

Notes:

```text
Validation: python -m pytest C:/TSIS_Data/01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder_v0_3.py -q
Result: 1 passed.
Runner smoke: C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_v0_3_runner_smoke_20250102_20250110_d/
Runner status: completed.
```

### GFQ-20260630-daily-scanner-v0-2-base-universe-profiles

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
data_foundation_outputs_graph
event_discovery_graph
market_state_representation_graph
strategy_research_graph
ml_feature_governance_graph
offline_rl_governance_graph
```

Why:

- Implemented the forward `daily_scanner_candidates_table_v0_2` controlled
  builder model.
- Replaced the v0.1 "two scanner universes" interpretation with one governed
  base eligible denominator plus parallel profile flags:
  `base_in_play_universe_scanner_v0_2` and profiles for TradeStation-like
  visibility, relative volume, percent change, dollar-volume tradability and
  DAS research.
- Clarified that `base_in_play_universe_scanner_v0_2` is the stable identifier,
  while the precise meaning is `base_eligible_smallcap_denominator`.
- Clarified that profile counts are not a sequential funnel.
- Clarified that `relative_volume_profile_v0_2` requires intraday/as-of volume
  acceleration before promotion, not only a daily RVOL proxy.
- Clarified that `percent_change_profile_v0_2` requires a declared minimum
  percent-change threshold before top-N ranking.
- Clarified that `dollar_volume_tradability_profile_v0_2` is tradability, not
  alpha.
- Clarified that `das_research_profile_v0_2` is provisional strategy-overlay
  lineage, not a final DAS scanner.
- Preserved `market_cap_usd < 100M` as the common hard filter.
- Preserved `volume_today >= 500k` only as the TradeStation-like profile hard
  filter, not as a universal research filter.
- Blocked float as a hard filter until a point-in-time float source passes
  source/coverage/as-of validation.
- Added a deterministic fixture test proving one base denominator row per
  instrument/session/as-of, profile flags, alias deduplication, no ML/RL/live
  authority and no official E-root promotion.
- Ran controlled replay
  `daily_scanner_candidates_replay_20250102_20250110_v0_2` under
  `C:/TSIS_Data/tests/test_runs/2026-06-30/`, producing 15,323 rows, 4,023
  selected-any-profile rows, 150 TradeStation-like profile rows, 2,472 DAS
  research profile rows, 3,177 selected rows below 500k volume, zero duplicate
  logical keys and zero ML/RL/live-authority rows.

Changed paths:

```text
scripts/materialize_daily_scanner_candidates_table_v0_2.py
tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder_v0_2.py
configs/data_foundation_outputs/scanner_definitions/base_in_play_universe_scanner_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/trade_station_like_profile_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/relative_volume_profile_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/percent_change_profile_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/dollar_volume_tradability_profile_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/das_research_profile_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/README.md
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_2.md
01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_2.md
01_foundations/canonical_schemas/outputs/daily_scanner_candidates_table_schema_contract.md
01_foundations/contract_registry/dataset_contracts/daily_scanner_candidates_table_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/daily_scanner_candidates_table_consumption_policy.md
01_foundations/dataset_registry/outputs/daily_scanner_candidates_table_registry_entry.yaml
01_foundations/validators/outputs/daily_scanner_candidates_table_validators.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/README.md
tests/data_foundation_outputs/README.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Evidence paths:

```text
C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_replay_20250102_20250110_v0_2/_daily_scanner_candidates_table_manifest_v0_2_candidate_replay.json
C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_replay_20250102_20250110_v0_2/_daily_scanner_candidates_table_summary_v0_2_candidate_replay.csv
```

Recommended action:

```text
Refresh the Data Foundation outputs and market-state/event-discovery related
leaves so graph users know that v0.2 is the forward scanner model, while v0.1
remains preserved historical controlled replay evidence. The leaf must include
the revised base-denominator/profile/strategy-overlay semantics. Do not mark
official E-root materialization as complete.
```

Root action:

```text
Do not rebuild root graph in this implementation turn. Include this entry in
the next planned Graphify maintenance window.
```

Owner:

```text
Modulo 01 / Data Foundation scanner and candidate-generation governance
```

### GFQ-20260629-master-intraday-quote-guarded-candidate

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
data_foundation_outputs_graph
ohlcv_1m_governance_graph
price_view_governance_graph
market_state_representation_graph
```

Why:

- Added the candidate contract for
  `master_intraday_bar_table_v0_2_candidate_quote_guarded`.
- Added a machine-readable candidate config under
  `configs/data_foundation_outputs/`.
- Updated the master intraday schema, validator, registry, consumption policy,
  dataset contract, target contract, status matrix and module-contract index.
- The semantic map must preserve the distinction between:
  - `master_intraday_bar_table_v0_1` as a scoped pilot;
  - quote-guarded v0.2 candidate route defined but not materialized;
  - current bridge run root under `runs/.../ohlcv_1m_quote_guarded/`;
  - future official source under
    `E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/`;
  - provisional `D:/quotes` lineage that must not be promoted as final.

Required corpus delta for next official build:

```text
configs/data_foundation_outputs/master_intraday_bar_table_quote_guarded_candidate_v0_2.json
tests/data_foundation_outputs/test_master_intraday_quote_guarded_candidate_contract.py
01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
01_foundations/module_contracts/outputs/master_intraday_bar_table_wider_scope_materialization_plan_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/canonical_schemas/outputs/master_intraday_bar_table_schema_contract.md
01_foundations/contract_registry/dataset_contracts/master_intraday_bar_table_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/master_intraday_bar_table_consumption_policy.md
01_foundations/dataset_registry/outputs/master_intraday_bar_table_registry_entry.yaml
01_foundations/validators/outputs/master_intraday_bar_table_validators.md
01_foundations/module_contracts/README.md
```


2026-07-03 update:

```text
quote_guarded_repair_manifest = E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
quote_guarded_repair_manifest_state = PASS
manifest_rows = 301278342
```

The semantic map must now distinguish between "upstream quote-guarded manifest
promoted" and "downstream master intraday/scanner candidate not yet
materialized".

### GFQ-20260629-market-event-state-controlled-candidates

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
data_foundation_outputs_graph
market_state_representation_graph
event_state_governance_graph
ml_feature_governance_graph
offline_rl_governance_graph
```

Why:

- Added controlled candidate builder mode to:
  - `scripts/materialize_market_state_table.py --materialize-candidate`
  - `scripts/materialize_event_state_table.py --materialize-candidate`
- Materialized controlled candidates under governed E-root output paths:
  - `E:/TSIS/data/data_foundation_outputs/market_state_table/market_state_table_v0_1_candidate_microstructure_halt_controlled/`
  - `E:/TSIS/data/data_foundation_outputs/event_state_table/event_state_table_v0_1_candidate_microstructure_halt_controlled/`
- Updated schemas, registry entries, validators, status matrix, output target
  contract, composition contract and build-loop runbook.
- The semantic map must preserve the distinction between:
  - official `market_state_table_v0_1` / `event_state_table_v0_1` not
    materialized/promoted;
  - controlled candidates materialized but `controlled_candidate_not_promoted`;
  - inherited provisional `D:/quotes` lineage requiring rebuild after
    `E:/TSIS/data/quotes_` parity/audit.

Required corpus delta for next official build:

```text
scripts/materialize_market_state_table.py
scripts/materialize_event_state_table.py
tests/data_foundation_outputs/test_market_state_table_contract.py
tests/data_foundation_outputs/test_event_state_table_contract.py
01_foundations/canonical_schemas/outputs/market_state_table_schema_contract.md
01_foundations/canonical_schemas/outputs/event_state_table_schema_contract.md
01_foundations/dataset_registry/outputs/market_state_table_registry_entry.yaml
01_foundations/dataset_registry/outputs/event_state_table_registry_entry.yaml
01_foundations/validators/outputs/market_state_table_validators.md
01_foundations/validators/outputs/event_state_table_validators.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md
01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md
```

### GFQ-20260629-scanner-framework-das-discovery

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
data_foundation_outputs_graph
event_discovery_graph
market_state_representation_graph
strategy_research_graph
ml_feature_governance_graph
offline_rl_governance_graph
```

Why:

- Added `scanner_framework_and_definitions_contract_v0_1.md` to formalize the
  initial scanner framework for `daily_scanner_candidates_table_v0_1`.
- Added two governed scanner configs:
  `trade_station_like_scanner_v0_1` and
  `broad_in_play_discovery_scanner_v0_1`.
- The change prevents future agents from treating `volume_today > 500000` and
  `% change 1D` ranking as the only general scanner for DAS research.
- Future controlled scanner replay must compare operational visibility against
  broad discovery, preserving candidate reasons, independent ranks and evidence
  of late/missed DAS candidates.

Affected files:

```text
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
configs/data_foundation_outputs/scanner_definitions/README.md
configs/data_foundation_outputs/scanner_definitions/trade_station_like_scanner_v0_1.yaml
configs/data_foundation_outputs/scanner_definitions/broad_in_play_discovery_scanner_v0_1.yaml
01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md
01_foundations/canonical_schemas/outputs/daily_scanner_candidates_table_schema_contract.md
01_foundations/contract_registry/dataset_contracts/daily_scanner_candidates_table_dataset_contract_v0_1.md
01_foundations/dataset_registry/outputs/daily_scanner_candidates_table_registry_entry.yaml
01_foundations/data_consumption_policies/daily_scanner_candidates_table_consumption_policy.md
01_foundations/validators/outputs/daily_scanner_candidates_table_validators.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/README.md
CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Required next Graphify action:

```text
Rebuild or update the data_foundation_outputs_graph leaf and related
event-discovery / strategy-research / market-state slices in the next Graphify
maintenance window. Root merge not required immediately.
```

### GFQ-20260629-daily-scanner-builder-replay

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
data_foundation_outputs_graph
event_discovery_graph
market_state_representation_graph
strategy_research_graph
ml_feature_governance_graph
offline_rl_governance_graph
```

Why:

- Implemented `daily_scanner_candidates_table_v0_1` controlled historical
  replay builder.
- Added deterministic fixture test proving scanner separation,
  broad-discovery candidates below 500k volume, alias deduplication, duplicate
  logical key prevention and ML/RL/live prohibition flags.
- Ran first controlled replay:
  `C:/TSIS_Data/tests/test_runs/2026-06-29/daily_scanner_candidates_replay_20250102_20250110_v0_1/`.
- The replay produced 30,646 evaluated rows, 150 TradeStation-like top-25 rows,
  3,196 broad-discovery rows, 2,383 broad-discovery rows below 500k volume,
  zero duplicate logical keys and no ML/RL/live-authority rows.
- Added the output-root policy: small samples/tests/demos stay under
  `C:/TSIS_Data/tests/test_runs/`, while long-range candidate replays must live
  under
  `E:/TSIS/data/data_foundation_outputs/daily_scanner_candidates_table/candidate_replays/`;
  the official promoted root remains reserved.
- This is evidence for builder shape and scanner comparison only. It is not an
  official E-root materialization and must not be treated as final
  `market_state_table` input without downstream validation/promotion gates.

Affected files:

```text
scripts/materialize_daily_scanner_candidates_table.py
tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder.py
01_research/README.md
01_research/notebooks/data_foundation_outputs/daily_scanner_candidates_replay_view_v0_1.ipynb
01_research/notebooks/data_foundation_outputs/README.md
01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md
01_foundations/canonical_schemas/outputs/daily_scanner_candidates_table_schema_contract.md
01_foundations/contract_registry/dataset_contracts/daily_scanner_candidates_table_dataset_contract_v0_1.md
01_foundations/dataset_registry/outputs/daily_scanner_candidates_table_registry_entry.yaml
01_foundations/validators/outputs/daily_scanner_candidates_table_validators.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Evidence paths:

```text
C:/TSIS_Data/tests/test_runs/2026-06-29/daily_scanner_candidates_replay_20250102_20250110_v0_1/_daily_scanner_candidates_table_manifest_v0_1_candidate_replay.json
C:/TSIS_Data/tests/test_runs/2026-06-29/daily_scanner_candidates_replay_20250102_20250110_v0_1/_daily_scanner_candidates_table_summary_v0_1_candidate_replay.csv
```

Required next Graphify action:

```text
Rebuild or update the data_foundation_outputs_graph leaf and event-discovery /
market-state representation slices so graph users know that scanner builder
and controlled replay evidence exist, but official E-root materialization is
still pending.
```

### GFQ-20260629-daily-scanner-candidates-contract-stack

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
data_foundation_outputs_graph
market_state_representation_graph
event_discovery_graph
ml_feature_governance_graph
offline_rl_governance_graph
```

Why:

- Added the `daily_scanner_candidates_table_v0_1` target stack as the governed
  candidate-generation/in-play discovery layer.
- The new stack defines scanner rows as candidate-set lineage, not as complete
  market state, full universe, direct ML/RL feature table, strategy signal or
  execution truth.
- Future state builders must use scanner candidates only as seeds, then compose
  full-history context, lookbacks, quality gates and event-window data.
- This changes the immediate Data Foundation output work order: controlled
  historical scanner replay precedes broad `market_state_table` samples that
  depend on daily in-play discovery.

Affected files:

```text
01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md
01_foundations/canonical_schemas/outputs/daily_scanner_candidates_table_schema_contract.md
01_foundations/contract_registry/dataset_contracts/daily_scanner_candidates_table_dataset_contract_v0_1.md
01_foundations/dataset_registry/outputs/daily_scanner_candidates_table_registry_entry.yaml
01_foundations/data_consumption_policies/daily_scanner_candidates_table_consumption_policy.md
01_foundations/validators/outputs/daily_scanner_candidates_table_validators.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md
01_foundations/canonical_schemas/outputs/market_state_table_schema_contract.md
01_foundations/canonical_schemas/outputs/event_state_table_schema_contract.md
01_foundations/contract_registry/dataset_contracts/market_state_table_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/event_state_table_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/market_state_table_consumption_policy.md
01_foundations/data_consumption_policies/event_state_table_consumption_policy.md
01_foundations/data_consumption_policies/README.md
01_foundations/canonical_schemas/README.md
01_foundations/contract_registry/dataset_contracts/README.md
01_foundations/dataset_registry/README.md
01_foundations/validators/README.md
01_foundations/module_contracts/README.md
```

Required next Graphify action:

```text
Rebuild or update the data_foundation_outputs_graph leaf and event-discovery /
market-state representation slices in the next Graphify maintenance window;
root merge not required immediately.
```

### GFQ-20260629-market-state-coverage-lookback-policy

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
data_foundation_outputs_graph
market_state_representation_graph
ml_feature_governance_graph
offline_rl_governance_graph
```

Why:

- Added `market_state_coverage_and_lookback_policy_v0_1.md` as the
  authoritative policy for daily scanner candidates, full-history context and
  event-window microstructure in market-state construction.
- The policy prevents a common semantic failure: treating a daily
  `in-play`/scanner ticker-day as a complete market state.
- Future `market_state_table` / `event_state_table` candidates must declare
  `state_population_scope`, `state_population_denominator`,
  `full_universe_claim`, `scanner_definition_id`, `strategy_family_id`,
  `event_window_source`, `lookback_policy_id`, price-view policy, as-of policy,
  leakage guard and quote-root lineage.
- Strategies that require historical memory, such as `Short Into Resistance`,
  must receive explicit lookback features instead of relying only on the
  current ticker-day.

Affected files:

```text
01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md
01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/README.md
```

Required next Graphify action:

```text
Rebuild or update the data_foundation_outputs_graph leaf and the affected
market-state representation/governance slices in the next Graphify maintenance
window; root merge not required immediately.
```

### GFQ-20260629-state-tables-provisional-d-quotes-lineage

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
data_foundation_outputs_graph
```

Why:

- The `market_state_table` / `event_state_table` build loop now explicitly
  accepts `D:/quotes` as provisional candidate-only quote lineage for controlled
  state samples while target official `E:/TSIS/data/quotes_` parity/audit
  remains incomplete.
- Updated contracts and policies require visible lineage:
  `quotes_root_used`, `quotes_root_state`, `target_official_quotes_root`,
  `legacy_incomplete_e_quotes_root` and
  `requires_rebuild_after_e_quotes_parity`.
- The change alters downstream interpretation: candidates inheriting this
  root state remain blocked for ML/RL primary training, backtest core and
  execution simulation until E-root parity/rebuild gates pass.
- Correction applied after human clarification: `E:/TSIS/data/quotes_` is the
  E-root target of the active `D:/quotes` clone; `E:/TSIS/data/quotes` is not
  the official target for this recovery decision and must be treated as
  incomplete/legacy.

Affected files:

```text
01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md
01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/data_consumption_policies/market_state_table_consumption_policy.md
01_foundations/data_consumption_policies/event_state_table_consumption_policy.md
```

Required next Graphify action:

```text
Rebuild or update data_foundation_outputs_graph leaf in the next Graphify
maintenance window; root merge not required immediately.
```

### GFQ-20260629-data-foundation-outputs-topology-leaf

Status: `leaf_built_root_not_merged`

Severity: `HIGH`

Slice:

```text
data_foundation_outputs_graph
```

Why:

- Built a deterministic Graphify topology leaf for CAPA 1 Data Foundation
  output tables.
- The leaf maps each output table to its schema contract, dataset contract,
  registry entry, consumption policy, validator and governed output path when
  those components exist.
- The build is useful for agents inspecting generated tables and contracts
  without scanning the entire `01_foundations` corpus.
- The leaf explicitly does not claim full semantic extraction of every field,
  rule or validator body.

Build result:

```text
Output:
01_foundations/graphify-out/leaf_slices/data_foundation_outputs_topology_20260629/

Graphify package: graphifyy 0.9.1
Semantic mode: deterministic_file_topology_extraction
Corpus files: 96
Nodes: 130
Edges: 200
Communities: 16
Diagnostic: clean
Root graph merge: not performed
```

Detected debt:

```text
short_sale_constraints_table / schema
short_sale_constraints_table / dataset_contract
short_sale_constraints_table / registry
short_sale_constraints_table / consumption_policy
short_sale_constraints_table / validator
```

Required follow-up:

```text
Create the missing short_sale_constraints_table contract stack before treating
SSR/borrow/locate/availability constraints as a governed table output.
Run full semantic extraction leaf later if agents need field-level or
validator-rule-level graph reasoning.
```

### GFQ-20260628-Graphify-no-api-version-alignment

Status: `cross_project_governance_leaf_built_foundations_authority_leaf_pending`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
certification_decisions_graph
graphify_governance_slice
```

Why:

- Graphify governance now explicitly follows upstream `safishamsi/graphify`
  branch `v8`, `graphifyy 0.9.1`, for no-API Codex behavior.
- The observed installed package was `graphifyy 0.8.40`; future builds must
  record whether the installed package was aligned, upstream was used, or the
  result is provisional by version limitation.
- Without Gemini/Google API keys, agents must use Graphify skill
  host-agent/subagent semantic extraction for markdown/contracts/papers/images.
- CLI `graphify update` alone is not semantic coverage for CAPA 1 documents.

Changed paths:

```text
PROJECT_RULES.md
CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/graphify/README.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md
01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_REFRESH_QUEUE.md
```

Required Graphify action:

```text
Include these files in the next official Graphify governance leaf. This queue
entry is not graph content and does not prove graph refresh completion.
```

Build result:

```text
Covered by cross-project governance leaf:
C:/TSIS_Data/00_CTO/graphify-out/leaf_slices/graphify_governance_20260629/

Graphify package: graphifyy 0.9.1
Semantic mode: Codex host inline extraction, no external API required
Nodes: 37
Edges: 60
Communities: 9
Diagnostic: clean

Important limitation:
This satisfies the graphify_governance_slice coverage for the protocol change,
but it does not rebuild foundations_authority_graph, data_foundation_outputs
or any full root graph. Those remain pending by slice.
```

### GFQ-20260626-001 - Event windows table CAPA 1 output materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
event_state_reconstruction_graph
halts_graph
module_test_governance_graph
```

Reason:

- Added `event_windows_table_v0_1` as a governed CAPA 1 output table.
- Added schema, dataset contract, registry entry, consumption policy,
  validators, materializer and pytest contract coverage.
- Materialized the governed parquet output under:

```text
E:/TSIS/data/data_foundation_outputs/event_windows_table/event_windows_table_v0_1.parquet
```

- The table derives event windows from halt events that are intraday-valid,
  temporally matched to `instrument_master_v0_1` and covered by
  `market_calendar_v0_1`.
- It separates pre-event feature windows from event-response and outcome
  windows to prevent leakage.
- It is not a general event table, not all event families, not execution truth
  and not a primary ML/RL dataset.
- Tests passed in:

```text
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_event_windows_table_v0_1/
```

Changed paths:

```text
01_foundations/canonical_schemas/outputs/event_windows_table_schema_contract.md
01_foundations/canonical_schemas/README.md
01_foundations/contract_registry/dataset_contracts/event_windows_table_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/README.md
01_foundations/data_consumption_policies/event_windows_table_consumption_policy.md
01_foundations/data_consumption_policies/README.md
01_foundations/dataset_registry/outputs/event_windows_table_registry_entry.yaml
01_foundations/dataset_registry/README.md
01_foundations/validators/outputs/event_windows_table_validators.md
01_foundations/validators/README.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
scripts/materialize_event_windows_table.py
tests/data_foundation_outputs/test_event_windows_table_contract.py
tests/data_foundation_outputs/README.md
C:/TSIS_Data/tests/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

External/output artifacts:

```text
E:/TSIS/data/data_foundation_outputs/event_windows_table/event_windows_table_v0_1.parquet
E:/TSIS/data/data_foundation_outputs/event_windows_table/_event_windows_table_manifest_v0_1.json
E:/TSIS/data/data_foundation_outputs/event_windows_table/_event_windows_table_summary_v0_1.csv
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_event_windows_table_v0_1/
```

Recommended action:

```text
Include this output in the next foundations_authority_graph rebuild and in the
specialized data_foundation_outputs, event_state_reconstruction and halts
leaves. Preserve the halts-only scope and anti-leakage gates as graph facts.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

Do not consume the partial timeout folder:

```text
E:/TSIS/data/data_foundation_outputs/event_windows_table/event_windows_table_v0_1_partial_timeout_do_not_use/
```

### GFQ-20260626-002 - Outcomes table CAPA 1 output materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
event_state_reconstruction_graph
outcome_research_graph
module_test_governance_graph
```

Reason:

- Added `outcomes_table_v0_1` as a governed CAPA 1 output table.
- Added schema, dataset contract, registry entry, consumption policy,
  validators, materializer and pytest contract coverage.
- Materialized the governed parquet output under:

```text
E:/TSIS/data/data_foundation_outputs/outcomes_table/outcomes_table_v0_1.parquet
```

- The table derives next-session daily labels/outcomes from
  `event_windows_table_v0_1` and `master_daily_table_v0_1`.
- It explicitly separates post-event labels/outcomes from pre-event features and
  blocks RL reward/execution interpretations in v0.1.
- It preserves review rows for missing daily event/outcome coverage instead of
  fabricating labels.
- Tests passed in:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_outcomes_table_v0_1/
```

Changed paths:

```text
01_foundations/canonical_schemas/outputs/outcomes_table_schema_contract.md
01_foundations/canonical_schemas/README.md
01_foundations/contract_registry/dataset_contracts/outcomes_table_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/README.md
01_foundations/data_consumption_policies/outcomes_table_consumption_policy.md
01_foundations/data_consumption_policies/README.md
01_foundations/dataset_registry/outputs/outcomes_table_registry_entry.yaml
01_foundations/dataset_registry/README.md
01_foundations/validators/outputs/outcomes_table_validators.md
01_foundations/validators/README.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
scripts/materialize_outcomes_table.py
tests/data_foundation_outputs/test_outcomes_table_contract.py
tests/data_foundation_outputs/README.md
C:/TSIS_Data/tests/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

External/output artifacts:

```text
E:/TSIS/data/data_foundation_outputs/outcomes_table/outcomes_table_v0_1.parquet
E:/TSIS/data/data_foundation_outputs/outcomes_table/_outcomes_table_manifest_v0_1.json
E:/TSIS/data/data_foundation_outputs/outcomes_table/_outcomes_table_summary_v0_1.csv
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_outcomes_table_v0_1/
```

Recommended action:

```text
Include this output in the next foundations_authority_graph rebuild and in the
specialized data_foundation_outputs, event_state_reconstruction and
outcome_research leaves. Preserve the label/feature separation, daily-only
scope and non-RL-reward limitation as graph facts.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

The official materialization is the `.parquet` file.

### GFQ-20260626-003 - Fundamentals as-of table CAPA 1 output materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
event_state_reconstruction_graph
ml_feature_governance_graph
module_test_governance_graph
```

Reason:

- Added `fundamentals_asof_table_v0_1` as a governed CAPA 1 output table.
- Added schema, dataset contract, registry entry, consumption policy,
  validators, materializer and pytest contract coverage.
- Materialized the governed partitioned parquet output under:

```text
E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/fundamentals_asof_table_v0_1/
```

- The table derives filing-date-aware statement context from
  `E:/TSIS/data/additional/financials`.
- It includes `income_statements`, `balance_sheets` and
  `cash_flow_statements`.
- It explicitly excludes `additional/financials/ratios` and standalone
  `E:/TSIS/data/financial` from v0.1 core because ratios remain sparse/review
  and `financial_v0_1` remains blocked by audit status `FAIL`.
- It fixes `as_of_date = filing_date` and blocks `period_end` as availability
  date.
- It is a state component, not direct ML/RL table, not latest-before-event
  snapshot and not market-cap/float authority.
- Tests passed in:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_fundamentals_asof_table_v0_1/
```

Changed paths:

```text
01_foundations/canonical_schemas/outputs/fundamentals_asof_table_schema_contract.md
01_foundations/canonical_schemas/README.md
01_foundations/contract_registry/dataset_contracts/fundamentals_asof_table_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/README.md
01_foundations/data_consumption_policies/fundamentals_asof_table_consumption_policy.md
01_foundations/data_consumption_policies/README.md
01_foundations/dataset_registry/outputs/fundamentals_asof_table_registry_entry.yaml
01_foundations/dataset_registry/README.md
01_foundations/validators/outputs/fundamentals_asof_table_validators.md
01_foundations/validators/README.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
scripts/materialize_fundamentals_asof_table.py
tests/data_foundation_outputs/test_fundamentals_asof_table_contract.py
tests/data_foundation_outputs/README.md
C:/TSIS_Data/tests/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

External/output artifacts:

```text
E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/fundamentals_asof_table_v0_1/
E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/_fundamentals_asof_table_manifest_v0_1.json
E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/_fundamentals_asof_table_summary_v0_1.csv
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_fundamentals_asof_table_v0_1/
```

Recommended action:

```text
Include this output in the next foundations_authority_graph rebuild and in the
specialized data_foundation_outputs, event_state_reconstruction and
ml_feature_governance leaves. Preserve the filing-date as-of rule, ratios/
standalone-financial exclusions, and direct-RL prohibition as graph facts.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

### GFQ-20260625-002 - Halts table CAPA 1 output materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
halts_graph
event_state_reconstruction_graph
module_test_governance_graph
```

Reason:

- Added `halts_table_v0_1` as a governed CAPA 1 output table.
- Added schema, dataset contract, registry entry, consumption policy,
  validators, materializer and pytest contract coverage.
- Materialized the governed parquet output under:

```text
E:/TSIS/data/data_foundation_outputs/halts_table/halts_table_v0_1.parquet
```

- The table preserves halt-source anomalies as explicit `good` / `review` /
  `bad` quality states instead of repairing them silently.
- The output is valid for event context, halt masks and outcome/backtest
  restrictions under quality gates, but it is not execution truth, not a live
  latency contract and not a primary ML/RL dataset.
- Tests passed in:

```text
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_halts_table_v0_1/
```

Changed paths:

```text
01_foundations/canonical_schemas/outputs/halts_table_schema_contract.md
01_foundations/canonical_schemas/README.md
01_foundations/contract_registry/dataset_contracts/halts_table_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/README.md
01_foundations/data_consumption_policies/halts_table_consumption_policy.md
01_foundations/data_consumption_policies/README.md
01_foundations/dataset_registry/outputs/halts_table_registry_entry.yaml
01_foundations/dataset_registry/README.md
01_foundations/validators/outputs/halts_table_validators.md
01_foundations/validators/README.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
scripts/materialize_halts_table.py
tests/data_foundation_outputs/test_halts_table_contract.py
tests/data_foundation_outputs/README.md
C:/TSIS_Data/tests/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

External/output artifacts:

```text
E:/TSIS/data/data_foundation_outputs/halts_table/halts_table_v0_1.parquet
E:/TSIS/data/data_foundation_outputs/halts_table/_halts_table_manifest_v0_1.json
E:/TSIS/data/data_foundation_outputs/halts_table/_halts_table_summary_v0_1.csv
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_halts_table_v0_1/
```

Recommended action:

```text
Include this output in the next foundations_authority_graph rebuild and in the
specialized data_foundation_outputs, halts and event_state_reconstruction
leaves. Preserve the context-only and non-live-latency limitations as graph
facts.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

Do not treat `halts_table_v0_1` as a live feed or execution source. It is a
historical halt/suspension context table with explicit quality gates.

### GFQ-20260623-002 - 1m split-normalized full-universe materialization runbook

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
intraday_price_views_graph
module_test_governance_graph
```

Reason:

- Added an operational runbook for official backtest/ML use of 1m
  split-normalized data.
- Added a manifest builder script for broad materialization scopes.
- Added a PowerShell runner for smoke tests, split-affected overnight
  materialization, optional audit, and physical full-copy mode.
- The runbook records that official intraday backtests/ML must use a split-safe
  1m strategy for the exact consumed scope.
- It distinguishes logical full-universe split-safe materialization from
  physical full-copy materialization.
- It includes PowerShell commands intended for long overnight runs by a human.

Changed paths:

```text
01_foundations/module_contracts/ohlcv_1m_split_normalized_full_universe_materialization_runbook_v0_1.md
01_foundations/module_contracts/ohlcv_1m_split_normalized_operational_landing_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/README.md
scripts/build_1m_split_normalized_materialization_manifest.py
scripts/run_1m_split_normalized_materialization.ps1
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include this runbook and manifest builder in the next intraday_price_views and
foundations_authority graph refresh.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

Do not treat the runbook commands as completed materialization evidence. They
are an execution protocol for future long runs.

### GFQ-20260623-001 - Master intraday bar table v0.1 scoped materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
intraday_price_views_graph
event_state_reconstruction_graph
module_test_governance_graph
```

Reason:

- Added `master_intraday_bar_table_v0_1` as the seventh CAPA 1 output table.
- Added contract, schema, registry entry, consumption policy, validators,
  materializer and pytest contract coverage.
- Materialized a scoped partitioned parquet dataset under:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_1
```

- The table intentionally carries `materialization_scope =
  scoped_split_normalized_event_cases` and `full_universe_claim = false`.
- The table exposes two price views, `1m_raw` and `1m_split_normalized`, over
  the 10 ticker-months currently present in `ohlcv_1m_split_normalized`.
- `backtest_core_bar_candidate` is false in v0.1; Event Engine and research
  graph slices must preserve the scoped flags and not treat this as a universal
  1m feed.
- Follow-up clarification on 2026-06-23: `ohlcv_1m_split_normalized` is a
  validated proof/pilot of the 1m split-normalization code and semantics. It is
  not a precomputed normalized copy of all raw 1m ticker-months. Future
  split-sensitive event/backtest scopes must rerun the audited normalization
  pipeline on the required ticker-months and register that scope.
- Contract tests passed in:

```text
C:/TSIS_Data/tests/test_runs/2026-06-23/data_foundation_outputs_seven_tables_v0_1_rerun/
```

Changed paths:

```text
01_foundations/canonical_schemas/outputs/master_intraday_bar_table_schema_contract.md
01_foundations/contract_registry/dataset_contracts/master_intraday_bar_table_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/master_intraday_bar_table_consumption_policy.md
01_foundations/dataset_registry/outputs/master_intraday_bar_table_registry_entry.yaml
01_foundations/validators/outputs/master_intraday_bar_table_validators.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
scripts/materialize_master_intraday_bar_table.py
tests/data_foundation_outputs/test_master_intraday_bar_table_contract.py
tests/data_foundation_outputs/README.md
tests/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include this output in the next foundations_authority_graph rebuild and in the
specialized data_foundation_outputs / intraday_price_views leaves. Preserve the
scoped warning as a graph fact.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until active Graphify remediation entries are
resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

This entry exists to prevent future agents from treating the 8-ticker scoped
surface as the full raw 1m universe.

### GFQ-20260622-008 - Master daily table v0.1 initial materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
daily_price_views_graph
event_state_reconstruction_graph
module_test_governance_graph
```

Reason:

- Added `master_daily_table_v0_1` as the sixth CAPA 1 output table.
- Added contract, schema, registry entry, consumption policy, validators,
  materializer and pytest contract coverage.
- Materialized a partitioned parquet dataset under:

```text
E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1
```

- The table preserves explicit `daily_raw`, `split_normalized` and `adjusted`
  price views and links expected coverage, corporate actions and family-level
  certification gates.

### GFQ-20260622-007 - Dataset certification matrix v0.1 initial materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
data_quality_report_graph
module_test_governance_graph
```

Reason:

- Added `dataset_certification_matrix_v0_1` as the fifth CAPA 1 output table.
- Added contract, schema, registry entry, consumption policy, validators,
  materializer and pytest contract coverage.
- Added dedicated validators for `ohlcv_daily_adjusted` and
  `ohlcv_1m_split_normalized` to satisfy the family status matrix evidence
  surface.
- Materialized a compact parquet table under:

```text
E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix/dataset_certification_matrix_v0_1.parquet
```

- The table normalizes `family_status_matrix_v0_1.md` into a family-level
  gate and verifies linked evidence surfaces.

### GFQ-20260622-006 - Corporate actions table v0.1 initial materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
corporate_actions_adjustment_graph
module_test_governance_graph
```

Reason:

- Added `corporate_actions_table_v0_1` as the fourth CAPA 1 output table.
- Added contract, schema, registry entry, consumption policy, validators,
  materializer and pytest contract coverage.
- Materialized a compact parquet table under:

```text
E:/TSIS/data/data_foundation_outputs/corporate_actions_table/corporate_actions_table_v0_1.parquet
```

- The table preserves `reference` as primary source and `additional` as
  secondary/reconciliation source.

Materialized:

```text
rows = 104757
tickers = 3621
instrument_ids = 3497
action_type_counts = dividend: 92033, split: 6630, ticker_change: 6094
source_system_counts = additional: 52490, reference: 52267
first_action_date = 1969-12-31
last_action_date = 2027-06-15
build_run_id = corporate_actions_table_v0_1_20260622T144845Z
output_sha256 = 01989eb301a2cdd83e297fbf6384e0bd4d5b4fb300bdccee6b1adbde87d5e4ce
hard_fail_count = 0
```

Test evidence:

```text
C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_four_tables_v0_1/
tests = 16
passed = 16
failed = 0
skipped = 0
```

Changed paths:

```text
01_foundations/canonical_schemas/outputs/corporate_actions_table_schema_contract.md
01_foundations/contract_registry/dataset_contracts/corporate_actions_table_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/corporate_actions_table_consumption_policy.md
01_foundations/dataset_registry/outputs/corporate_actions_table_registry_entry.yaml
01_foundations/validators/outputs/corporate_actions_table_validators.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
scripts/materialize_corporate_actions_table.py
tests/data_foundation_outputs/test_corporate_actions_table_contract.py
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include in the next Data Foundation outputs/corporate-actions leaf refresh.
Link this node to daily_adjusted, master_daily_table, event_engine and
data_quality_report.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

- This table is context and adjustment lineage, not final adjusted price output.

### GFQ-20260622-005 - Expected data calendar v0.1 initial materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
module_test_governance_graph
```

Reason:

- Added `expected_data_calendar_v0_1` as the third CAPA 1 output table.
- Added contract, schema, registry entry, consumption policy, validators,
  materializer and pytest contract coverage.
- Materialized a partitioned parquet dataset under:

```text
E:/TSIS/data/data_foundation_outputs/expected_data_calendar/expected_data_calendar_v0_1
```

- The table is a coverage expectation denominator, not proof of physical
  presence or quality.

Materialized:

```text
rows = 29029152
dataset_families = daily_raw, ohlcv_1m_raw, quotes_raw, trades_raw
rows_per_family = 7257288
tickers = 4824
first_session = 2005-01-03
last_session = 2025-12-31
parquet_file_count = 84
tree_sha256 = 1c7571cdcefc1ffd3f0f6cda921d32d64dee33cc41c3676809686c1bc575a57f
build_run_id = expected_data_calendar_v0_1_20260622T141019Z
hard_fail_count = 0
```

Test evidence:

```text
C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_instrument_master_market_calendar_expected_data_calendar_v0_1/
tests = 12
passed = 12
failed = 0
skipped = 0
```

Changed paths:

```text
01_foundations/canonical_schemas/outputs/expected_data_calendar_schema_contract.md
01_foundations/contract_registry/dataset_contracts/expected_data_calendar_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/expected_data_calendar_consumption_policy.md
01_foundations/dataset_registry/outputs/expected_data_calendar_registry_entry.yaml
01_foundations/validators/outputs/expected_data_calendar_validators.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
scripts/materialize_expected_data_calendar.py
tests/data_foundation_outputs/test_expected_data_calendar_contract.py
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include in the next Data Foundation outputs leaf refresh. Link this node to
instrument_master, market_calendar, dataset_certification_matrix and
data_quality_report.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

- Future data_quality_report work must join expected rows against actual
  family presence/quality evidence.

### GFQ-20260622-004 - Data Foundation output contract tests

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
module_test_governance_graph
```

Reason:

- Added executable pytest contract tests for `instrument_master_v0_1` and
  `market_calendar_v0_1`.
- Added a pytest harness that writes dated institutional evidence under
  `C:/TSIS_Data/tests/test_runs/`.
- The tests validate manifest/hash integrity, contract links, schema/lineage,
  hard contractual gates and source reconciliation.
- Executed the first two table tests successfully.

Changed paths:

```text
01_TSIS_backtest_SmallCaps/tests/conftest.py
01_TSIS_backtest_SmallCaps/tests/_helpers/__init__.py
01_TSIS_backtest_SmallCaps/tests/_helpers/data_foundation.py
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_instrument_master_contract.py
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_market_calendar_contract.py
01_TSIS_backtest_SmallCaps/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md
C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_instrument_master_market_calendar_v0_1/
```

Test evidence:

```text
C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_instrument_master_market_calendar_v0_1/
```

Result:

```text
tests = 8
passed = 8
failed = 0
skipped = 0
```

Recommended action:

```text
Include in the next foundations/test-governance leaf refresh. Link the test
harness to future Data Foundation output tables before they are promoted.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
Modulo 01 / Data Foundation test governance
```

Notes:

- These are offline tests. Third-party live checks remain a future opt-in layer.

### GFQ-20260622-003 - Data root and test artifact topology clarification

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_storage_topology_graph
module_test_governance_graph
```

Reason:

- Clarified that `E:/TSIS/data/` is the active preferred data plane.
- Clarified that `E:/TSIS/data/data_foundation_outputs/` is for governed CAPA 1
  table outputs, not test execution artifacts.
- Clarified that `C:/TSIS_Data/tests/test_runs/`, `fixtures/` and
  `third_party_evidence/` are the roots for test outputs, small test data and
  cached external evidence.
- Reclassified `C:/TSIS_Data/data/` as legacy/quarantine until a migration audit
  proves which families can be removed.
- No deletion of legacy data was performed.

Changed paths:

```text
tests/README.md
tests/test_runs/README.md
tests/fixtures/README.md
tests/third_party_evidence/README.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/data_storage_topology_and_target_state.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Include in the next foundations/storage/test-governance leaf refresh. Link this
entry to the future migration audit for C:/TSIS_Data/data.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
Modulo 01 / Data storage and test governance
```

Notes:

- A lightweight path check showed counterparts in `E:/TSIS/data` for
  `additional`, `quotes`, `short`, `short_review` and
  `trades_ticks_prod_2005_2026`.
- `trades_ticks_2019_2025` was present in `C:/TSIS_Data/data` and did not have
  an immediate same-name counterpart in `E:/TSIS/data` during the check.
- Many existing docs/scripts still reference `C:/TSIS_Data/data`; deletion must
  wait for a migration audit.

### GFQ-20260622-002 - SmallCaps test topology scaffold

Status: `pending_leaf_build`

Severity: `MEDIUM`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
module_test_governance_graph
```

Reason:

- Added module-level test documentation under `01_TSIS_backtest_SmallCaps/tests/`.
- The scaffold defines where executable tests should live for Data Foundation
  outputs, foundations governance, pipelines, research, event engine, strategy
  engine, execution and offline RL preparation.
- The Data Foundation output test README formalizes the five minimum validation
  layers for institutional tables: schema contract, manifest/hash,
  source reconciliation, third-party evidence and adversarial/mutation checks.
- No executable validators were added in this entry.

Changed paths:

```text
01_TSIS_backtest_SmallCaps/tests/README.md
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/README.md
01_TSIS_backtest_SmallCaps/tests/foundations/README.md
01_TSIS_backtest_SmallCaps/tests/pipelines/README.md
01_TSIS_backtest_SmallCaps/tests/research/README.md
01_TSIS_backtest_SmallCaps/tests/event_engine/README.md
01_TSIS_backtest_SmallCaps/tests/strategy_engine/README.md
01_TSIS_backtest_SmallCaps/tests/execution/README.md
01_TSIS_backtest_SmallCaps/tests/rl_preparation/README.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Include in the next foundations/test-governance leaf refresh. Link the
`data_foundation_outputs/` tests to the CAPA 1 output contracts and table
materialization manifests.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
Modulo 01 / Data Foundation test governance
```

Notes:

- Existing `tests/test_price_views.py` remains in place and was not moved.
- This entry should be followed by executable pytest contracts for
  `instrument_master_v0_1` and `market_calendar_v0_1`.

### GFQ-20260622-001 - Market calendar v0.1 initial materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
daily_intraday_calendar_graph
```

Reason:

- `market_calendar_v0_1` was defined as the second compact CAPA 1 output
  table.
- Contract, schema, registry entry, consumption policy, validator and
  materializer were added.
- The first materialized parquet was written under:

```text
E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet
```

- The output reconciles to the local official calendar candidate:

```text
rows = 5283
calendar = XNYS
timezone = America/New_York
first_session = 2005-01-03
last_session = 2025-12-31
early_close_sessions = 45
source_parquet_sha256 = 8aac3ea4f7fbcaf6c394320f53acc1524bf5e5e3addbcd48ef31718bc0214228
output_sha256 = 96bd60c124e6552d269f8846205ed28bf6e58881453a5bbb4f73ced0657b56d5
hard_fail_count = 0
```

- The output is an XNYS session calendar. It does not encode halts, liquidity,
  venue outages or dates after `2025-12-31`.

Changed paths:

```text
01_foundations/canonical_schemas/outputs/market_calendar_schema_contract.md
01_foundations/contract_registry/dataset_contracts/market_calendar_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/market_calendar_consumption_policy.md
01_foundations/dataset_registry/outputs/market_calendar_registry_entry.yaml
01_foundations/validators/outputs/market_calendar_validators.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
scripts/materialize_market_calendar.py
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include in the next foundations/calendar/output leaf refresh. Link it to
instrument_master, expected_data_calendar, master_daily_table and
master_intraday_bar_table.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

### GFQ-20260621-003 - Instrument master v0.1 initial materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
reference_identity_graph
data_foundation_outputs_graph
```

Reason:

- `instrument_master_v0_1` was defined as the first compact CAPA 1 output
  table.
- Contract, schema, registry entry, consumption policy, validator and
  materializer were added.
- The first materialized parquet was written under:

```text
E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet
```

- The output reconciles exactly to `lt1b_universe_v0_1`:

```text
rows = 4824
tickers = 4824
hard_fail_count = 0
duplicate_ticker_count = 0
sha256 = 69104387d2607306c3fa1740573d130db5e7c30b1d1527d3ee8a8d2b4d53c2d2
```

- The table is ticker-grain for the `<1B>` operational universe. It does not
  resolve final economic continuity or daily fully point-in-time market-cap
  membership.

Changed paths:

```text
01_foundations/canonical_schemas/outputs/instrument_master_schema_contract.md
01_foundations/contract_registry/dataset_contracts/instrument_master_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/instrument_master_consumption_policy.md
01_foundations/dataset_registry/outputs/instrument_master_registry_entry.yaml
01_foundations/validators/outputs/instrument_master_validators.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
scripts/materialize_instrument_master.py
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include in the next foundations/reference identity leaf refresh. Keep linked
to the outputs target contract and the data storage topology decision.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

### GFQ-20260619-001 - Initial Data Foundation Graphify governance

Status: `leaf_built`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
```

Reason:

- Se creo la gobernanza inicial para Graphify de CAPA 1.
- Existen nuevos documentos que deben entrar en el mapa semantico cuando se
  construya el primer leaf oficial:
  - `GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md`
  - `GRAPHIFY_REFRESH_QUEUE.md`
  - `module_contracts/graphify/README.md`
  - `module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md`

Changed paths:

```text
01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_foundations/.graphifyignore
01_foundations/README.md
01_foundations/module_contracts/graphify/
01_foundations/module_contracts/README.md
```

Recommended action:

```text
Built foundations_authority_graph as the first official leaf.
Do not build a monolithic 01_foundations graph yet.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation governance
```

Notes:

The first useful Graphify build for CAPA 1 should map authority, not evidence.
Evidence-heavy dossiers and parquet/CSV profiling come later and must stay
separate.

`foundations_authority_graph` is not a physical folder. It is the first official
leaf graph name. The full `01_foundations` map is expected to emerge from
separate leaves and, if useful, a later `data_foundation_root_graph`.

Build result:

```text
Output:
01_foundations/graphify-out/leaf_slices/foundations_authority_20260619/

Stats:
- detected_files: 246
- detected_words: 411452
- nodes: 696
- edges: 854
- communities: 75

Validation:
- graphify diagnose multigraph passed with 0 dangling endpoints, 0 duplicate
  edges, and 0 endpoint-collapsed edge groups.
- root graph intentionally not created:
  01_foundations/graphify-out/graph.json = absent
```

### GFQ-20260619-002 - README cross-graph and graph-first lookup rule

Status: `leaf_built`

Severity: `MEDIUM`

Slice:

```text
foundations_authority_graph
```

Reason:

- `01_foundations/README.md` now records that the official
  `certification_decisions_graph` exists outside `01_foundations`.
- Future agents must consult the certification leaf when a question depends on
  historical audit/certification, closeouts, historical policies, global
  metrics or decisions expressed as `expected/present/healthy/usable`.
- `01_foundations/README.md` now distinguishes `graph_only`,
  `graph_first_source_verified` and `source_only_exception` answers.
- Future agents must query Graphify first for architecture, relationships,
  institutional quality, maturity or coverage questions, then verify material
  claims against source documents, scripts, dossiers and `evidence_assets`.
- The historical research graph is explicitly documented as context that can
  enrich, constrain or qualify interpretation of `01_foundations`, without
  promoting historical claims by itself.

Changed paths:

```text
01_foundations/README.md
```

Recommended action:

```text
Do not rebuild immediately.
Include this README change in the next foundations_authority_graph refresh.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation governance
```

Notes:

This change is a navigation and agent-usage update. It does not alter dataset
contracts, schemas, validators or consumption policies. It made the prior
`foundations_authority_graph` semantically stale for the new query protocol and
was included in the 20260620 leaf refresh.

Satisfied by:

```text
foundations_authority_graph leaf build:
01_foundations/graphify-out/leaf_slices/foundations_authority_20260620/
```

### GFQ-20260619-003 - RAW authority and derivation map

Status: `leaf_built`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
```

Reason:

- A new transversal module contract now separates RAW vendor provenance from
  functional role: raw market data, raw reference/context data, derived ETL
  views, feature layers, label/target layers, audit evidence and runtime/cache
  artifacts.
- `01_foundations/README.md` now points agents to that contract before reading
  maturity percentages as proof of raw data quality.
- `module_contracts/README.md` now includes the contract in the mandatory
  market-data reading path.
- This changes the semantic map agents need when answering raw-vs-derived
  questions, even though no dataset files, schemas or validators changed.

Changed paths:

```text
01_foundations/module_contracts/raw_data_authority_and_derivation_map.md
01_foundations/module_contracts/README.md
01_foundations/module_contracts/transversal_contracts_index.md
01_foundations/README.md
```

Recommended action:

```text
Do not rebuild immediately unless a raw/derived architecture query requires it.
Include this contract in the next foundations_authority_graph refresh.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation governance
```

Notes:

This is a semantic-governance update. It does not promote or demote any dataset
by itself. It fixes the transversal interpretation layer so derived datasets,
features, labels, evidence assets and Graphify outputs cannot be mistaken for
primary RAW audit authority.

Satisfied by:

```text
foundations_authority_graph leaf build:
01_foundations/graphify-out/leaf_slices/foundations_authority_20260620/
```

### GFQ-20260619-004 - Additional context quality and master-table readiness

Status: `leaf_built`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
```

Reason:

- `additional_v0_1` now has a validator contract, domain index, master-table
  readiness policy, generated inspection package and evidence assets.
- The README maturity changes from accepted auxiliary (`78%`) to governed RAW
  vendor context (`92%`) with explicit unresolved limits.
- The new package changes the semantic map future agents need when deciding how
  Additional can feed `data_quality_report`, `master_daily_table`,
  `symbol_master`, `corporate_actions_table`, `calendar_table` and indirect
  `master_intraday_table` context.

Changed paths:

```text
01_foundations/README.md
01_foundations/validators/README.md
01_foundations/validators/additional/additional_validators.md
01_foundations/module_contracts/README.md
01_foundations/module_contracts/transversal_contracts_index.md
01_foundations/module_contracts/additional_contracts_index.md
01_foundations/module_contracts/additional_to_master_tables_policy_v0_1.md
01_foundations/contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/additional_consumption_policy.md
01_foundations/dataset_registry/additional/additional_registry_entry.yaml
01_foundations/inspection_dossiers/README.md
01_foundations/inspection_dossiers/additional/
scripts/inspection/additional/build_additional_inspection_pack.py
```

Recommended action:

```text
Do not rebuild immediately unless an Additional/master-table architecture query
requires it. Include this package in the next foundations_authority_graph
refresh.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation governance
```

Notes:

This is a CAPA 1 governance and evidence update. It does not materialize a
master table and does not authorize downstream feature, execution, RL or live
consumers.

Satisfied by:

```text
foundations_authority_graph leaf build:
01_foundations/graphify-out/leaf_slices/foundations_authority_20260620/
```

### GFQ-20260620-001 - Visual inspection completion gate and family visual packs

Status: `leaf_built`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
```

Reason:

- The foundation completion standard now separates data-quality verdict,
  foundations completion status and visual inspection status.
- Families cannot be called `human_inspector_ready` unless they have a formal
  `visual_inspector_pack/` or an explicit waiver.
- New and updated visual inspector packs close the previous visual debt for:
  `financial`, `regime_indicators`, `short_review`, `additional`,
  `intraday_regime_features`, `Halts`, `reference` and
  `ohlcv_daily_adjusted`.
- The family status matrix now shows no active `visual_casepack_required`
  family in the current matrix.
- This changes the semantic map agents need when answering whether a data
  family is institutionalized for human inspection.

Changed paths:

```text
01_foundations/FOUNDATIONS_FAMILY_COMPLETION_STANDARD.md
01_foundations/DATA_AUDIT_QUALITY_STANDARD.md
01_foundations/VISUAL_INSPECTION_PACK_REQUIREMENTS.md
01_foundations/README.md
01_foundations/data_quality_report/
01_foundations/data_quality_report/family_status_matrix_v0_1.md
01_foundations/data_quality_report/families/additional_quality_report_v0_1.md
01_foundations/data_quality_report/families/daily_adjusted_quality_report_v0_1.md
01_foundations/data_quality_report/families/financial_quality_report_v0_1.md
01_foundations/data_quality_report/families/halts_quality_report_v0_1.md
01_foundations/data_quality_report/families/intraday_regime_features_quality_report_v0_1.md
01_foundations/data_quality_report/families/reference_quality_report_v0_1.md
01_foundations/data_quality_report/families/regime_indicators_quality_report_v0_1.md
01_foundations/data_quality_report/families/short_review_quality_report_v0_1.md
01_foundations/inspection_dossiers/additional/
01_foundations/inspection_dossiers/daily_adjusted/
01_foundations/inspection_dossiers/financial/
01_foundations/inspection_dossiers/halts/
01_foundations/inspection_dossiers/intraday_regime_features/
01_foundations/inspection_dossiers/reference/
01_foundations/inspection_dossiers/regime_indicators/
01_foundations/inspection_dossiers/short_review/
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Refresh the `foundations_authority_graph` leaf in a dedicated Graphify run.
Do not build a monolithic 01_foundations graph.
Respect .graphifyignore: graph CSV/PNG assets are evidence, not semantic graph
corpus, unless a future explicit visual-evidence slice is defined.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation visual inspection governance
```

Notes:

The refresh should capture the new completion semantics and the human-inspector
readiness state, not the binary visual evidence itself. The visual assets remain
auditable through manifests and dossiers; Graphify should index the markdown
contracts/readouts and keep heavy evidence excluded.

Satisfied by:

```text
foundations_authority_graph leaf build:
01_foundations/graphify-out/leaf_slices/foundations_authority_20260620/
```

### GFQ-20260620-002 - Data-family institutionalization contracts and audit navigation

Status: `leaf_built`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
```

Reason:

- The foundation authority layer now contains new and updated family contracts,
  dataset registries, data-consumption policies, validators and transversal
  module contracts for the data-family institutionalization work.
- This is broader than the visual-inspection gate: it defines where the
  technical data analysis, physical integrity checks, auditor navigation,
  readiness matrix and raw/derived data authority must live.
- Human and agent queries about whether a family is inspection-ready,
  production-usable, technically audited, contract-covered or source-of-truth
  governed must resolve through these documents.
- The affected docs are semantic authority inputs for the same
  `foundations_authority_graph` leaf and therefore must be refreshed together
  with the visual-gate update.

Changed paths:

```text
01_foundations/DATA_AUDIT_TOPIC_NAVIGATION.md
01_foundations/contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/financial_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/regime_indicators_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/additional_consumption_policy.md
01_foundations/data_consumption_policies/daily_adjusted_consumption_policy.md
01_foundations/data_consumption_policies/financial_consumption_policy.md
01_foundations/data_consumption_policies/ohlcv_1m_split_normalized_consumption_policy.md
01_foundations/data_consumption_policies/regime_indicators_consumption_policy.md
01_foundations/data_consumption_policies/short_review_consumption_policy.md
01_foundations/dataset_registry/additional/
01_foundations/dataset_registry/financial/
01_foundations/dataset_registry/regime_indicators/
01_foundations/dataset_registry/short_review/
01_foundations/inspection_dossiers/README.md
01_foundations/inspection_dossiers/halts/integration_notes.md
01_foundations/module_contracts/README.md
01_foundations/module_contracts/transversal_contracts_index.md
01_foundations/module_contracts/additional_contracts_index.md
01_foundations/module_contracts/additional_to_master_tables_policy_v0_1.md
01_foundations/module_contracts/data_engineering_physical_audit_standard_v0_1.md
01_foundations/module_contracts/data_folder_audit_readiness_matrix_v0_1.md
01_foundations/module_contracts/raw_data_authority_and_derivation_map.md
01_foundations/validators/README.md
01_foundations/validators/additional/
01_foundations/validators/financial/
01_foundations/validators/intraday_regime_features/
01_foundations/validators/regime_indicators/
01_foundations/validators/short_review/
```

Recommended action:

```text
Refresh the `foundations_authority_graph` leaf in the same dedicated Graphify
run as GFQ-20260620-001.
Do not build a monolithic 01_foundations graph.
Do not include physical data, CSV manifests, PNG evidence or parquet outputs in
the semantic corpus unless a future explicit evidence slice is approved.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation institutionalization governance
```

Notes:

This entry closes Graphify queue coverage for Markdown/YAML semantic authority
changes introduced by the family institutionalization work. It intentionally
does not claim that runtime evidence assets, generated CSVs, PNGs, parquet data
or scripts outside `01_foundations/` are part of this leaf.

Build result:

```text
Output:
01_foundations/graphify-out/leaf_slices/foundations_authority_20260620/

Stats:
- detected_files: 341
- detected_words: 476827
- nodes: 1002
- edges: 1381
- communities: 93
- semantic_chunks: 16
- semantic_nodes_before_build: 944
- semantic_edges_before_build: 1168
- hyperedges_before_build: 48

Validation:
- graphify diagnose multigraph passed with 0 dangling endpoints, 0 duplicate
  edges, and 0 endpoint-collapsed edge groups.
- root graph intentionally not created:
  01_foundations/graphify-out/graph.json = absent

Operational note:
- chunks 01-12 were Codex worker semantic extraction.
- chunks 13-16 were deterministic bounded structural extraction after worker
  subagents failed to write chunk files within the operational window.
- this limitation is recorded in the leaf BUILD_MANIFEST.md.
```

### GFQ-20260621-001 - Homogeneous Graphify semantic extraction remediation

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
```

Reason:

- `foundations_authority_20260620` is materialized, valid, consultable and
  diagnostically clean, but it is not a fully homogeneous semantic extraction.
- Chunks `01-12` were produced by Codex worker semantic extraction.
- Chunks `13-16` were produced by deterministic bounded structural extraction
  after worker subagents failed to write chunk files within the operational
  window.
- That fallback was intentionally documented, but it means the current leaf
  must not be represented as final institutional Graphify parity.

Changed paths:

```text
01_foundations/graphify-out/leaf_slices/foundations_authority_20260620/BUILD_MANIFEST.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_foundations/README.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Reopen the Graphify build work.
Re-extract chunks 13-16 using the same worker semantic-extraction standard as
chunks 01-12, splitting them into smaller chunks if needed.
Regenerate foundations_authority_graph as a new dated leaf.
Update BUILD_MANIFEST.md, GRAPHIFY_REFRESH_QUEUE.md, README.md and CHANGELOG.md.
Remove the limitation only after all chunks have homogeneous semantic extraction
evidence.
```

Root action:

```text
No root graph yet.
Do not integrate this leaf into a root graph until the homogeneous extraction
remediation is complete or an explicit waiver is documented.
```

Owner:

```text
Modulo 01 / Data Foundation Graphify governance
```

Notes:

Current state:

```text
graph materialized = yes
graph valid JSON / consultable = yes
root graph = no, by protocol
fully homogeneous Graphify semantic extraction = no
institutional final without caveat = no
```

This entry exists so the remediation is not left only in conversation memory.

### GFQ-20260621-002 - Data Foundation outputs target contract

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
daily_ohlcv_graph
reference_identity_graph
microstructure_quotes_trades_graph
additional_fundamentals_news_graph
```

Reason:

- A new CAPA 1 output target contract was added under `module_contracts/outputs/`.
- The contract defines how Data Foundation outputs work together when an event
  is evaluated.
- It affects master table design, reference identity, market calendar,
  corporate actions, daily/intraday bars, microstructure sidecars, context
  sidecars and quality gates.
- It now fixes the common physical landing root for governed CAPA 1 outputs:
  `E:/TSIS/data/data_foundation_outputs/`.
- It distinguishes clean Data Foundation output tables from append-only live
  ingestion logs such as `E:/TSIS/data/live_ingestion/raw_alert_log/`.
- It now also records the missing governed live table for low-latency corporate
  event alerts: offerings, private placements, warrants, SEC 8-K/6-K/424B
  filings, reverse splits and comparable smallcap catalysts.
- It includes a DAS Trader / NewsWare investigation note: DAS/NewsWare is a
  candidate live alert source, but public DAS API documentation is not enough
  evidence to assume governed API ingestion through DAS Trader Pro API.
- The alert-table semantics distinguish historical/contextual news from
  `received_utc`-tracked live alerts and should be visible in downstream Event
  Engine and Strategy Research graph slices.
- The Graphify table-design protocol classifies a new master table contract as
  `HIGH`.

Changed paths:

```text
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/data_storage_topology_and_target_state.md
01_foundations/module_contracts/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include the new outputs contract in the next foundations_authority_graph rebuild.
When the specialized graph slices are materialized, include the contract as a
cross-slice anchor for daily/intraday, reference identity, microstructure and
additional/context table design.
Do not create a monolithic 01_foundations graph.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until GFQ-20260621-001 is remediated or an
explicit waiver is documented.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

The contract records that `market_calendar_official_XNYS_20050101_20251231`
is locally reproducible byte-for-byte from
`scripts/agent05_build_market_calendar_official.py` with
`exchange_calendars 4.13.1`, but also states that the artifact is not a raw
download from NYSE.

### GFQ-20260624-001 - Quotes recovery clone runbook

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
microstructure_quotes_trades_graph
```

Reason:

- A new operational runbook and PowerShell entry point define how to stage
  `D:/quotes` into `E:/TSIS/data/quotes_`.
- The change records a source-root mismatch discovered while preparing
  `microstructure_features_table`: several audited quotes case files exist in
  `D:/quotes` but not in `E:/TSIS/data/quotes`.
- The staging folder is explicitly not source of truth until a post-copy audit
  and promotion decision exist.
- The copy script supports `-SubPath` scoped smoke tests so operators do not
  need to run a full-tree dry-run over millions of files before the real clone.
- A new transversal contract records the final RAW storage parity requirement:
  every relevant raw/source-preserved folder under `D:/` must have equivalent
  governed landing evidence under `E:/TSIS/data`.
- The raw storage parity requirement is physical/lineage evidence and does not
  replace per-family data quality certification.
- The script materially affects how agents should reason about quotes physical
  roots and therefore belongs in both foundations authority and
  microstructure quotes/trades graph slices.

Changed paths:

```text
01_foundations/module_contracts/quotes/quotes_staging_clone_runbook_v0_1.md
01_foundations/module_contracts/transversal/raw_storage_parity_audit_requirement_v0_1.md
01_foundations/module_contracts/data_storage_topology_and_target_state.md
01_foundations/module_contracts/raw_data_authority_and_derivation_map.md
01_foundations/module_contracts/README.md
01_foundations/module_contracts/quotes_contracts_index.md
01_foundations/module_contracts/transversal_contracts_index.md
scripts/data_ops/clone_quotes_to_staging.ps1
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include the runbook and script entry point in the next foundations authority
leaf rebuild and the next microstructure quotes/trades graph slice.
Downstream official consumption remains blocked until post-copy audit and
promotion note exist, but E:/TSIS/data/quotes_ is now the target official
E-root for the active D:/quotes clone.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until the foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

Historical correction recorded on `2026-06-29`: the target
`E:/TSIS/data/quotes_` is no longer described as disposable staging. It is the
intended E-root produced by the active `D:/quotes` clone, pending final
post-copy audit/promotion. `E:/TSIS/data/quotes` is treated as incomplete/
legacy E-root for this recovery decision.

### GFQ-20260625-001 - Microstructure features table seed output

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
data_foundation_outputs_graph
microstructure_quotes_trades_graph
foundations_authority_graph
```

Reason:

- Added `microstructure_features_table_v0_1` as a scoped CAPA 1 output table.
- The table is intentionally `seed_event_window_smoke`, not full-universe.
- The Data Foundation outputs contract now includes a direct scientific
  decision-evidence matrix for state components, covering sequential decision
  states, Offline RL datasets, distribution shift, LOB modeling, LOB
  simulation, evaluator-driven program search and causal ML.
- Added a Data Foundation outputs status matrix that separates target design
  from actual materialization state, test evidence, consumer readiness and
  remaining blockers.
- Current v0.1 materializes one ZYXI 2025-12-01 event window from raw files:
  `D:/quotes` for quotes and
  `E:/TSIS/data/trades_ticks_prod_2005_2026` for trades.
- The table records row-level source paths and SHA-256 hashes, plus identity and
  family gate lineage.
- The contract explicitly states that `D:/quotes` is provisional legacy/recovery
  lineage and that a rebuild/compare from a governed E-root is required before
  any promotion.
- The test recomputes source metrics from raw files and validates that the seed
  table is not eligible for execution simulation or core backtesting.

Changed paths:

```text
configs/data_foundation_outputs/microstructure_features_seed_windows_v0_1.csv
scripts/materialize_microstructure_features_table.py
01_foundations/canonical_schemas/outputs/microstructure_features_table_schema_contract.md
01_foundations/contract_registry/dataset_contracts/microstructure_features_table_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/microstructure_features_table_consumption_policy.md
01_foundations/dataset_registry/outputs/microstructure_features_table_registry_entry.yaml
01_foundations/validators/outputs/microstructure_features_table_validators.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
tests/data_foundation_outputs/test_microstructure_features_table_contract.py
tests/data_foundation_outputs/README.md
01_foundations/canonical_schemas/README.md
01_foundations/contract_registry/dataset_contracts/README.md
01_foundations/data_consumption_policies/README.md
01_foundations/dataset_registry/README.md
01_foundations/validators/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

External/output artifacts:

```text
E:/TSIS/data/data_foundation_outputs/microstructure_features_table/microstructure_features_table_v0_1
E:/TSIS/data/data_foundation_outputs/microstructure_features_table/_microstructure_features_table_manifest_v0_1.json
E:/TSIS/data/data_foundation_outputs/microstructure_features_table/_microstructure_features_table_summary_v0_1.csv
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_microstructure_features_table_v0_1_rerun/
```

Recommended action:

```text
Rebuild the data_foundation_outputs leaf and the microstructure quotes/trades
slice so future agents can query the table lineage, provisional D-root rule,
source-file hashes, tests and promotion barrier.
Do not collapse this seed into a full-universe claim.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until the foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

`D:/quotes` is an input only for the current seed materialization. The target
future source remains a governed E-root after raw storage parity.

### GFQ-20260626-004 - News context table CAPA 1 output materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
event_state_reconstruction_graph
ml_feature_governance_graph
module_test_governance_graph
```

Reason:

- Added `news_context_table_v0_1` as a governed CAPA 1 output table.
- Added schema, dataset contract, registry entry, consumption policy,
  validators, materializer and pytest contract coverage.
- Materialized the governed partitioned parquet output under:

```text
E:/TSIS/data/data_foundation_outputs/news_context_table/news_context_table_v0_1/
```

- The table derives historical news context from
  `E:/TSIS/data/additional/news`.
- It fixes `as_of_utc = published_utc`, preserves requested ticker separately
  from article `payload_tickers`, and keeps multi-ticker articles as
  attribution-review rows.
- It is catalyst/news context, not proof of causality, not a live `received_utc`
  alert stream, not direct ML/RL table and not execution truth.
- Tests passed in:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_news_context_table_v0_1/
```

Changed paths:

```text
01_foundations/canonical_schemas/outputs/news_context_table_schema_contract.md
01_foundations/canonical_schemas/README.md
01_foundations/contract_registry/dataset_contracts/news_context_table_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/README.md
01_foundations/data_consumption_policies/news_context_table_consumption_policy.md
01_foundations/data_consumption_policies/README.md
01_foundations/dataset_registry/outputs/news_context_table_registry_entry.yaml
01_foundations/dataset_registry/README.md
01_foundations/validators/outputs/news_context_table_validators.md
01_foundations/validators/README.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
scripts/materialize_news_context_table.py
tests/data_foundation_outputs/test_news_context_table_contract.py
tests/data_foundation_outputs/README.md
C:/TSIS_Data/tests/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

External/output artifacts:

```text
E:/TSIS/data/data_foundation_outputs/news_context_table/news_context_table_v0_1/
E:/TSIS/data/data_foundation_outputs/news_context_table/_news_context_table_manifest_v0_1.json
E:/TSIS/data/data_foundation_outputs/news_context_table/_news_context_table_summary_v0_1.csv
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_news_context_table_v0_1/
```

Recommended action:

```text
Include this output in the next foundations_authority_graph rebuild and in the
specialized data_foundation_outputs, event_state_reconstruction and
ml_feature_governance leaves. Preserve the published_utc as-of rule,
requested-vs-payload ticker distinction, multi-ticker attribution-review
state, live received_utc limitation and direct-RL prohibition as graph facts.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until the foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

The official materialization is historical/contextual. Real-time offering/news
alerts still require `real_time_corporate_event_alerts_table` with feed/source
lineage, `received_utc` and latency measurement.

### GFQ-20260626-005 - Short context table CAPA 1 output materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
event_state_reconstruction_graph
ml_feature_governance_graph
module_test_governance_graph
```

Reason:

- Added `short_context_table_v0_1` as a governed CAPA 1 output table.
- Added schema, dataset contract, registry entry, consumption policy,
  validators, materializer and pytest contract coverage.
- Materialized the governed partitioned parquet output under:

```text
E:/TSIS/data/data_foundation_outputs/short_context_table/short_context_table_v0_1/
```

- The table derives short interest and short volume context from two explicitly
  separated source planes:

```text
E:/TSIS/data/short/
E:/TSIS/data/short_review/finra_short/
```

- `short_review`/FINRA is preserved as official/free baseline and provenance;
  `short` is preserved as the local operational plane.
- The output does not silently select one source of truth, does not collapse
  source duplicates, and requires consumer-side source selection plus
  as-of/availability lag.
- The output is short pressure/crowding context, not SSR, not borrow/locate/
  availability, not intraday tape, not execution truth, not direct ML/RL table
  and not a final market-state dataset.
- Tests passed in:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_short_context_table_v0_1/
```

Changed paths:

```text
01_foundations/canonical_schemas/outputs/short_context_table_schema_contract.md
01_foundations/canonical_schemas/README.md
01_foundations/contract_registry/dataset_contracts/short_context_table_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/README.md
01_foundations/data_consumption_policies/short_context_table_consumption_policy.md
01_foundations/data_consumption_policies/README.md
01_foundations/dataset_registry/outputs/short_context_table_registry_entry.yaml
01_foundations/dataset_registry/README.md
01_foundations/validators/outputs/short_context_table_validators.md
01_foundations/validators/README.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
scripts/materialize_short_context_table.py
tests/data_foundation_outputs/test_short_context_table_contract.py
tests/data_foundation_outputs/README.md
C:/TSIS_Data/tests/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

External/output artifacts:

```text
E:/TSIS/data/data_foundation_outputs/short_context_table/short_context_table_v0_1/
E:/TSIS/data/data_foundation_outputs/short_context_table/_short_context_table_manifest_v0_1.json
E:/TSIS/data/data_foundation_outputs/short_context_table/_short_context_table_summary_v0_1.csv
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_short_context_table_v0_1/
```

Recommended action:

```text
Include this output in the next foundations_authority_graph rebuild and in the
specialized data_foundation_outputs, event_state_reconstruction and
ml_feature_governance leaves. Preserve the FINRA/local source-plane separation,
duplicate-key flags, as-of/lag requirement, no-borrow/no-SSR limitation and
direct-RL prohibition as graph facts.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until the foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

`regime_context_table` has since been materialized as
`regime_context_table_v0_1`. Live offering or filing alerts remain a separate
`real_time_corporate_event_alerts_table` workstream requiring source/feed,
`received_utc` and latency semantics.

### GFQ-20260627-001 - Short sale constraints target contract

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
event_state_reconstruction_graph
short_strategy_governance_graph
execution_simulation_governance_graph
ml_feature_governance_graph
```

Reason:

- Added a dedicated target contract for `short_sale_constraints_table`.
- The contract separates SSR, borrow, locate and short availability from
  `short_context_table_v0_1`.
- It records that `short_context_table_v0_1` is valid for short pressure and
  crowding context, but cannot prove short execution feasibility.
- It defines required SSR, borrow, locate, availability, hard-to-borrow and
  borrow-fee fields before TSIS can claim institutional short-strategy
  execution realism.
- It records that no governed physical source for SSR/borrow/locate/
  availability currently exists under `E:/TSIS/data`.
- It blocks any future agent from inferring borrow or locate from FINRA short
  interest/short volume.

Changed paths:

```text
01_foundations/module_contracts/outputs/short_sale_constraints_table_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include this contract in the next foundations_authority_graph rebuild and in
specialized data_foundation_outputs, event_state_reconstruction, short-strategy
and execution-simulation governance leaves. Preserve the hard boundary:
short pressure != short execution feasibility.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until the foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

This is a target contract only. No `short_sale_constraints_table_v0_1` output
has been materialized. Regime context remains the next historical table
candidate, while SSR/borrow/locate requires source acquisition or explicit
derived-proxy validation first.

### GFQ-20260627-002 - Short sale constraints acquisition runbook

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
short_strategy_governance_graph
execution_simulation_governance_graph
live_ingestion_governance_graph
ml_feature_governance_graph
```

Reason:

- Added the acquisition runbook for `short_sale_constraints_table`.
- The runbook records that 20 years of market data is not 20 years of
  broker-specific borrow/locate/availability data.
- It separates SSR historical derived proxy, DAS/SageTrader live capture and
  broker/vendor historical intake as distinct acquisition tracks.
- It defines raw append-only capture requirements for future DAS integration.
- It defines metadata and frequency gates for any future historical
  broker/vendor borrow/locate/availability source.
- It blocks future agents from treating DAS live capture as retroactive history
  unless the broker/vendor provides point-in-time historical backfill.

Changed paths:

```text
01_foundations/module_contracts/outputs/short_sale_constraints_data_acquisition_runbook_v0_1.md
01_foundations/module_contracts/outputs/short_sale_constraints_table_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include this runbook in the next foundations_authority_graph rebuild and in
specialized data_foundation_outputs, short-strategy, execution-simulation,
live-ingestion and ML feature governance leaves. Preserve the boundary:
market data history != broker borrow/locate history.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until the foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

No DAS API connection or historical vendor source has been declared acquired.
This is a preparation runbook only. Materialization remains blocked until a
source exists, a manifest is written, validators pass and promotion evidence is
available.

### GFQ-20260627-003 - Regime context table CAPA 1 output materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
event_state_reconstruction_graph
market_state_representation_graph
ml_feature_governance_graph
module_test_governance_graph
```

Reason:

- Added `regime_context_table_v0_1` as a governed CAPA 1 output table.
- Added schema, dataset contract, registry entry, consumption policy,
  validators, materializer and pytest contract coverage.
- Materialized the governed partitioned parquet output under:

```text
E:/TSIS/data/data_foundation_outputs/regime_context_table/regime_context_table_v0_1/
```

- The table derives session-level regime context from:

```text
E:/TSIS/data/regime_indicators/**/minute.parquet
```

- It explicitly blocks `regime_indicators/**/day.parquet` because the daily
  files remain invalid under the audited 1970 date semantics.
- It explicitly excludes `E:/TSIS/data/intraday_regime_features` because that
  is a separate pilot feature layer, not the v0.1 global regime source.
- The output is a session-close context component, not same-session intraday
  causal state, not execution truth, not direct ML/RL table and not a final
  market-state dataset.
- Tests passed in:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_regime_context_table_v0_1/
```

Changed paths:

```text
01_foundations/canonical_schemas/outputs/regime_context_table_schema_contract.md
01_foundations/canonical_schemas/README.md
01_foundations/contract_registry/dataset_contracts/regime_context_table_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/README.md
01_foundations/data_consumption_policies/regime_context_table_consumption_policy.md
01_foundations/data_consumption_policies/README.md
01_foundations/dataset_registry/outputs/regime_context_table_registry_entry.yaml
01_foundations/dataset_registry/README.md
01_foundations/validators/outputs/regime_context_table_validators.md
01_foundations/validators/README.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
scripts/materialize_regime_context_table.py
tests/data_foundation_outputs/test_regime_context_table_contract.py
tests/data_foundation_outputs/README.md
C:/TSIS_Data/tests/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

External/output artifacts:

```text
E:/TSIS/data/data_foundation_outputs/regime_context_table/regime_context_table_v0_1/
E:/TSIS/data/data_foundation_outputs/regime_context_table/_regime_context_table_manifest_v0_1.json
E:/TSIS/data/data_foundation_outputs/regime_context_table/_regime_context_table_summary_v0_1.csv
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_regime_context_table_v0_1/
```

Recommended action:

```text
Include this output in the next foundations_authority_graph rebuild and in the
specialized data_foundation_outputs, event_state_reconstruction,
market_state_representation and ML feature governance leaves. Preserve the
minute-source decision, blocked day.parquet boundary, intraday-feature
exclusion, as-of requirement, same-session intraday prohibition and direct-RL
prohibition as graph facts.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until the foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

`regime_context_table_v0_1` closes the current historical context table
materialization step for regime proxies. It does not replace the future
`market_state_table` / `event_state_table` composition contract.

### GFQ-20260627-004 - Market/event state composition contract skeleton

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
event_state_reconstruction_graph
market_state_representation_graph
ml_feature_governance_graph
offline_rl_governance_graph
execution_simulation_governance_graph
```

Reason:

- Added the skeleton composition contract for `market_state_table_v0_1` and
  `event_state_table_v0_1`.
- The contract records that current CAPA 1 context outputs are state
  components only after a legal decision-time/as-of builder composes them.
- It defines the boundary between state, signal, strategy, outcome, reward and
  execution fill.
- It blocks inline labels/outcomes/rewards in future state tables.
- It defines required state namespaces, lineage bundles, quality states,
  as-of gates and hard leakage failures.
- It records that no `market_state_table_v0_1` or `event_state_table_v0_1`
  output is materialized yet.

Changed paths:

```text
01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include this contract in the next foundations_authority_graph rebuild and in
specialized data_foundation_outputs, event_state_reconstruction,
market_state_representation, ML feature, offline RL and execution-simulation
governance leaves. Preserve the hard boundary: context table != final state,
feature table != label table, state != reward.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until the foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

The next implementation step is not another conceptual definition. It is the
schema/builder/validator/test skeleton for `market_state_table_v0_1` and
`event_state_table_v0_1` based on this contract.

### GFQ-20260627-005 - Market/event state contract stack skeletons

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
event_state_reconstruction_graph
market_state_representation_graph
ml_feature_governance_graph
offline_rl_governance_graph
module_test_governance_graph
```

Reason:

- Added the recoverable build-loop runbook for market/event state work.
- Added schema contracts for `market_state_table_v0_1` and
  `event_state_table_v0_1`.
- Added dataset contracts, consumption policies, validator contracts and
  registry target entries with `contract_defined_not_materialized` status.
- Added non-writing builder skeletons that support `--contract-check-only` and
  fail explicitly if invoked as materializers.
- Added executable contract-skeleton tests and passed them.
- Preserved the hard boundary that no official parquet/manifest/summary exists
  yet for either table.

Changed paths:

```text
01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md
01_foundations/canonical_schemas/outputs/market_state_table_schema_contract.md
01_foundations/canonical_schemas/outputs/event_state_table_schema_contract.md
01_foundations/contract_registry/dataset_contracts/market_state_table_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/event_state_table_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/market_state_table_consumption_policy.md
01_foundations/data_consumption_policies/event_state_table_consumption_policy.md
01_foundations/validators/outputs/market_state_table_validators.md
01_foundations/validators/outputs/event_state_table_validators.md
01_foundations/dataset_registry/outputs/market_state_table_registry_entry.yaml
01_foundations/dataset_registry/outputs/event_state_table_registry_entry.yaml
scripts/materialize_market_state_table.py
scripts/materialize_event_state_table.py
tests/data_foundation_outputs/test_market_state_table_contract.py
tests/data_foundation_outputs/test_event_state_table_contract.py
01_foundations/canonical_schemas/README.md
01_foundations/contract_registry/dataset_contracts/README.md
01_foundations/data_consumption_policies/README.md
01_foundations/dataset_registry/README.md
01_foundations/validators/README.md
01_foundations/module_contracts/README.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
tests/data_foundation_outputs/README.md
C:/TSIS_Data/tests/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

External/test artifacts:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_market_state_table_contract_skeleton_v0_1/
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_event_state_table_contract_skeleton_v0_1/
```

Recommended action:

```text
Include this stack in the next foundations_authority_graph rebuild and in the
specialized data_foundation_outputs, event_state_reconstruction,
market_state_representation, ML feature and offline RL governance leaves.
Preserve that both registry entries are target skeleton entries, not
materialized dataset entries.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until the foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

The next implementation step is deterministic fixture design and real builder
configs. Do not materialize full state tables until adversarial leakage tests
exist and pass.

### GFQ-20260627-006 - Market/event state deterministic fixture loop

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
event_state_reconstruction_graph
market_state_representation_graph
ml_feature_governance_graph
offline_rl_governance_graph
module_test_governance_graph
```

Reason:

- Added deterministic fixture set for market/event state contract tests.
- Added fixture-only builder configs for `market_state_table_v0_1` and
  `event_state_table_v0_1`.
- Added shared fixture builder helper enforcing test-run-only outputs,
  official-output prohibition, required flags, prohibited prefixes and as-of
  gates.
- Extended both materializer scripts with `--config --output-dir` fixture mode
  while preserving `official_builder_implemented = false`.
- Extended tests to execute good fixture samples and reject adversarial leakage
  fixtures.
- Added explicit Data Foundation priority rule: expand governed intraday and
  microstructure coverage before official market/event state materialization.
- Preserved the hard boundary that no official parquet/manifest/summary exists
  for either table.

Changed paths:

```text
tests/fixtures/data_foundation_outputs/market_event_state_v0_1/README.md
tests/fixtures/data_foundation_outputs/market_event_state_v0_1/market_state_components_good_v0_1.json
tests/fixtures/data_foundation_outputs/market_event_state_v0_1/market_state_components_future_asof_bad_v0_1.json
tests/fixtures/data_foundation_outputs/market_event_state_v0_1/market_state_components_prohibited_feature_bad_v0_1.json
tests/fixtures/data_foundation_outputs/market_event_state_v0_1/event_state_events_good_v0_1.json
tests/fixtures/data_foundation_outputs/market_event_state_v0_1/event_state_events_inline_label_bad_v0_1.json
tests/fixtures/data_foundation_outputs/market_event_state_v0_1/event_state_events_post_review_bad_ml_v0_1.json
01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/market_state_builder_fixture_v0_1.json
01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/event_state_builder_fixture_v0_1.json
01_TSIS_backtest_SmallCaps/scripts/_state_fixture_builder.py
01_TSIS_backtest_SmallCaps/scripts/materialize_market_state_table.py
01_TSIS_backtest_SmallCaps/scripts/materialize_event_state_table.py
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_market_state_table_contract.py
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_event_state_table_contract.py
01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/README.md
C:/TSIS_Data/tests/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

External/test artifacts:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_market_event_state_fixture_loop_v0_1/
```

Recommended action:

```text
Include this fixture-loop change in the next foundations_authority_graph rebuild
and in specialized data_foundation_outputs, event_state_reconstruction,
market_state_representation, ML feature and offline RL governance leaves.
Preserve that this is fixture-only evidence, not official table
materialization.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until the foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

The next implementation step is a richer controlled multi-component sample and
stricter adversarial gates. Do not materialize full state tables until manifest,
recomputation and coverage gates exist and pass.

### GFQ-20260627-007 - Master intraday wider-scope materialization plan

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
market_state_representation_graph
event_state_reconstruction_graph
ml_feature_governance_graph
offline_rl_governance_graph
module_test_governance_graph
```

Reason:

- Added a dedicated plan for expanding `master_intraday_bar_table` beyond the
  current scoped v0.1 pilot.
- Preserved that `master_intraday_bar_table_v0_1` remains
  `scoped_split_normalized_event_cases` with `full_universe_claim=false`.
- Documented that broad intraday expansion must start from split-safe 1m
  smoke/manifest work, not by reinterpreting the existing v0.1 output.
- Defined required builder changes before any `v0_2_candidate`: config-driven
  dataset id, source root, output root, materialization scope, denominator
  manifest, row-level claims and no overwrite of v0.1.
- Defined promotion gates: denominator reconciliation, split formula tests,
  factor-1 logical equivalence, raw quality inheritance, manifest/tree hashes,
  changelog, registry, validators and Graphify updates.

Changed paths:

```text
01_foundations/module_contracts/outputs/master_intraday_bar_table_wider_scope_materialization_plan_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include this governance contract in the next foundations_authority_graph rebuild
and in specialized data_foundation_outputs, market_state_representation,
event_state_reconstruction, ML feature and offline RL governance leaves.
Preserve that this is a plan-only change: no new parquet dataset has been
created or promoted.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until the foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

The next executable action is the 1m split-safe smoke manifest from
`ohlcv_1m_split_normalized_full_universe_materialization_runbook_v0_1.md`.
Do not launch physical full-copy materialization or claim full-universe
coverage until denominator, manifest, audit and tests pass.

### GFQ-20260627-008 - Microstructure multi-window materialization plan

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
microstructure_quotes_trades_graph
event_state_reconstruction_graph
market_state_representation_graph
ml_feature_governance_graph
offline_rl_governance_graph
module_test_governance_graph
```

Reason:

- Added a dedicated plan for expanding `microstructure_features_table` beyond
  the current one-window v0.1 seed.
- Preserved that `microstructure_features_table_v0_1` remains
  `seed_event_window_smoke` with `full_universe_claim=false`.
- Documented that broad microstructure expansion must use governed event
  windows, not a blind scan of every quotes/trades file.
- Defined `event_windows_table_v0_1` as the first governed denominator for a
  halt-only multi-window candidate.
- Preserved the quotes-root boundary: `D:/quotes` is provisional candidate
  lineage until `E:/TSIS/data/quotes_` parity/authority is resolved. The
  pre-existing `E:/TSIS/data/quotes` tree is explicitly legacy/incomplete and
  must not be treated as the official E-root.
- Defined required builder changes before any `v0_2_candidate`: config-driven
  dataset id, scope, output root, source root state, event-window input,
  denominator manifest, missingness states and no overwrite of v0.1.
- Defined promotion gates: source hash validation, recomputation from raw
  quotes/trades, leakage tests, visual/forensic evidence, changelog, registry,
  validators and Graphify updates.

Changed paths:

```text
01_foundations/module_contracts/outputs/microstructure_features_table_multi_window_materialization_plan_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include this governance contract in the next foundations_authority_graph rebuild
and in specialized data_foundation_outputs, microstructure_quotes_trades,
event_state_reconstruction, market_state_representation, ML feature and offline
RL governance leaves. Preserve that this is a plan-only change: no new
microstructure parquet dataset has been created or promoted.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until the foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

The next executable action is a governed multi-window candidate manifest derived
from `event_windows_table_v0_1` rows where
`valid_for_microstructure_feature_candidate=true`. Do not claim all event
families or ML/RL readiness from the v0.1 seed.

### GFQ-20260627-009 - Microstructure candidate window manifest builder

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
microstructure_quotes_trades_graph
event_state_reconstruction_graph
market_state_representation_graph
ml_feature_governance_graph
offline_rl_governance_graph
module_test_governance_graph
```

Reason:

- Added `scripts/build_microstructure_candidate_window_manifest.py`.
- Added tests for the governed microstructure v0.2 candidate window manifest.
- Parameterized `scripts/materialize_microstructure_features_table.py` so it
  can write a candidate dataset id/scope/output path while preserving v0.1
  defaults.
- The builder derives candidate windows from `event_windows_table_v0_1` and
  preserves the distinction between:
  - `source_window_dataset_id = event_windows_table_v0_1`;
  - `source_event_dataset_id = halts_table_v0_1`.
- The builder writes only CSV/JSON manifest artifacts to the requested output
  directory; the materializer candidate writes only to test/candidate paths.
- Tests verify denominator counts, selected role counts, leakage semantics, no
  full-universe claim, raw quote/trade source reconciliation and no writes to
  official `microstructure_features_table_v0_1`.
- Updated docs and changelog with evidence.

Changed paths:

```text
scripts/build_microstructure_candidate_window_manifest.py
scripts/materialize_microstructure_features_table.py
tests/data_foundation_outputs/test_microstructure_candidate_window_manifest.py
tests/data_foundation_outputs/README.md
01_foundations/module_contracts/outputs/microstructure_features_table_multi_window_materialization_plan_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

External/test artifacts:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_candidate_window_manifest_v0_1/
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_features_table_v0_1_default_guard/
```

Recommended action:

```text
Include this code/test/doc change in the next foundations_authority_graph
rebuild and in specialized data_foundation_outputs, microstructure_quotes_trades,
event_state_reconstruction, market_state_representation, ML feature and offline
RL governance leaves. Preserve that this is candidate/test evidence only:
no microstructure feature parquet candidate has been promoted under
`E:/TSIS/data`.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until the foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

The next executable action is visual/forensic evidence for the 6-row candidate
windows, then a larger declared candidate only after quotes-root state and
denominator policy are confirmed.

### GFQ-20260627-010 - Microstructure candidate visual evidence notebook and dossier

Status: `pending_leaf_build`

Severity: `MEDIUM`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
microstructure_quotes_trades_graph
event_state_reconstruction_graph
market_state_representation_graph
ml_feature_governance_graph
offline_rl_governance_graph
module_test_governance_graph
```

Reason:

- Added a human-viewable notebook for the 6-row
  `microstructure_features_table_v0_2_candidate` smoke artifact.
- Added a governed inspection dossier with six PNG panels, a visual manifest
  and a markdown readout for human auditors.
- The notebook is a convenience inspection surface; the institutional evidence
  lives in the inspection dossier and generated manifest/readout.
- This closes the previous "visual/forensic evidence missing" step for the
  6-row candidate smoke only. It does not promote a new official dataset.

Changed paths:

```text
scripts/inspection/microstructure/build_microstructure_candidate_visual_evidence.py
01_foundations/inspection_dossiers/microstructure_features/README.md
01_foundations/inspection_dossiers/microstructure_features/microstructure_candidate_visual_readout_v0_1.md
01_foundations/inspection_dossiers/microstructure_features/visual_evidence_v0_1/microstructure_candidate_visual_manifest_v0_1.json
01_foundations/inspection_dossiers/microstructure_features/visual_evidence_v0_1/images/
01_research/notebooks/data_foundation_outputs/microstructure_candidate_visual_evidence_v0_1.ipynb
01_foundations/module_contracts/outputs/microstructure_features_table_multi_window_materialization_plan_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

External/test artifacts:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_candidate_window_manifest_v0_1/
```

Recommended action:

```text
Include the notebook/readout/script/dossier in the next specialized
data_foundation_outputs and microstructure_quotes_trades leaf rebuild. Preserve
that this is visual evidence for a candidate smoke artifact only and not a
full-universe or E-root promotion.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until the foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

The next executable action is to decide the quotes-root state and materialize a
larger declared candidate only after source-root, denominator and recomputation
policy are explicit.

### GFQ-20260627-011 - Optimized 1m split-normalized manifest smoke

Status: `pending_leaf_build`

Severity: `MEDIUM`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
daily_ohlcv_graph
event_state_reconstruction_graph
market_state_representation_graph
ml_feature_governance_graph
offline_rl_governance_graph
module_test_governance_graph
```

Reason:

- Reworked `scripts/build_1m_split_normalized_materialization_manifest.py` so
  `split-affected` mode no longer uses a global `Path.rglob()` over
  `E:/TSIS/data/ohlcv_1m`.
- The optimized strategy starts from split files and checks expected
  `ticker/year/month` minute paths directly.
- Added regression tests that monkeypatch `Path.rglob()` to fail if this path
  regresses.
- Ran the official smoke wrapper successfully and recorded the smoke manifest
  evidence for the next `master_intraday_bar_table` wider-scope loop.

Changed paths:

```text
scripts/build_1m_split_normalized_materialization_manifest.py
tests/data_foundation_outputs/test_1m_split_normalized_manifest_builder.py
tests/data_foundation_outputs/README.md
01_foundations/module_contracts/ohlcv_1m_split_normalized_full_universe_materialization_runbook_v0_1.md
01_foundations/module_contracts/outputs/master_intraday_bar_table_wider_scope_materialization_plan_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

External/test artifacts:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/1m_split_normalized_full_universe_candidate/split_affected_20260627_153012/
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_1m_split_manifest_builder_v0_1/
```

Recommended action:

```text
Include the optimized builder/test/runbook evidence in the next Data Foundation
outputs and daily_ohlcv graph leaf rebuild. Preserve that this is manifest
smoke/test evidence only: no split-normalized full-universe parquet candidate
or master_intraday v0.2 candidate has been promoted.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until the foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

The next executable action is to decide whether to launch
`run_1m_split_normalized_materialization.ps1 -Mode split-affected -RunAudit`
or provide the command for manual overnight execution.

### GFQ-20260627-012 - Long-running operation telemetry contract

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
module_test_governance_graph
data_foundation_outputs_graph
daily_ohlcv_graph
quotes_graph
graphify_governance_graph
```

Reason:

- Added the root-level `LONG_RUNNING_OPERATIONS_CONTRACT.md`.
- The contract makes pre-manifest, PID manifest, heartbeat JSON/JSONL,
  timestamps, live log, monitor command and final manifest/summary mandatory
  for long-running operations across TSIS.
- Instrumented the 1m split-normalized materialization runner and quotes
  staging clone runner so new runs expose telemetry from startup.
- Added generic monitor script for humans/agents to inspect long-running runs
  from a separate terminal, including compact append-only progress lines.
- Updated quotes and 1m split-normalized runbooks with the new telemetry
  expectation and monitor command shape.

Changed paths:

```text
LONG_RUNNING_OPERATIONS_CONTRACT.md
PROJECT_OPERATING_SYSTEM.md
PROJECT_RULES.md
AGENTS.md
01_TSIS_backtest_SmallCaps/README.md
01_TSIS_backtest_SmallCaps/scripts/monitor_long_running_operation.ps1
01_TSIS_backtest_SmallCaps/scripts/run_1m_split_normalized_materialization.ps1
01_TSIS_backtest_SmallCaps/scripts/data_ops/clone_quotes_to_staging.ps1
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/quotes/quotes_staging_clone_runbook_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/ohlcv_1m_split_normalized_full_universe_materialization_runbook_v0_1.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md
```

External/runtime validation artifacts:

```text
E:/TSIS/data/data_ops_manifests/quotes_clone/quotes_clone_to_staging_20260627T170447Z.*
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/1m_split_normalized_full_universe_candidate/telemetry_smoke_20260627_1912/
```

Recommended action:

```text
Include the new root long-running operations contract and the two instrumented
runners in the next foundations governance leaf build. Preserve that the
currently alive legacy robocopy run predates this contract and is not evidence
of the new telemetry standard.
```

Root action:

```text
Do not rebuild root graph until foundations Graphify remediation state is
resolved or explicitly waived.
```

Owner:

```text
TSIS root governance / Modulo 01 Data Foundation operations
```

### GFQ-20260627-013 - Microstructure v0.2 controlled candidate validation

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
microstructure_quotes_trades_graph
event_state_reconstruction_graph
market_state_representation_graph
ml_feature_governance_graph
offline_rl_governance_graph
module_test_governance_graph
```

Reason:

- Added executable validation for the physically materialized controlled
  `microstructure_features_table_v0_2_candidate` dataset.
- The candidate has 50 halt-derived event windows, 9 tickers and 1 parquet
  partition under the governed Data Foundation output root.
- Tests validate manifest, summary, output-tree hash, contract paths,
  source-window semantics, no-promotion flags, partial trade-source missingness
  sampled raw quote/trade recomputation and the 50-case visual/forensic pack.
- Added a controlled visual evidence pack with 50 PNG panels and per-image
  explanatory markdown. The builder reads the declared candidate partition and
  caches raw quote/trade files, so the run read 9 quote files and 5 trade files
  instead of reloading per window.
- The test deliberately avoids broad filesystem scans over million-file roots:
  it reads the declared candidate partition and exact raw sample paths.
- The candidate remains not promoted: `full_universe_claim=false`,
  `execution_sim_candidate_rows=0`,
  `backtest_core_microstructure_candidate_rows=0`.
- Quotes lineage remains provisional through
  `quotes_root_state=provisional_d_legacy_recovery_root_pending_e_parity`.
- Trades are present for 24/50 rows; 26 rows are explicit
  `review_partial_source` rows and cannot be treated as clean execution/ML
  state.

Changed paths:

```text
tests/data_foundation_outputs/test_microstructure_features_controlled_candidate.py
tests/data_foundation_outputs/README.md
scripts/inspection/microstructure/build_microstructure_candidate_visual_evidence.py
01_foundations/inspection_dossiers/microstructure_features/README.md
01_foundations/inspection_dossiers/microstructure_features/microstructure_candidate_controlled_visual_readout_v0_2.md
01_foundations/inspection_dossiers/microstructure_features/visual_evidence_v0_2_controlled_25_per_role/microstructure_candidate_controlled_visual_manifest_v0_2.json
01_foundations/inspection_dossiers/microstructure_features/visual_evidence_v0_2_controlled_25_per_role/images/
01_foundations/module_contracts/outputs/microstructure_features_table_multi_window_materialization_plan_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

External/output artifacts:

```text
E:/TSIS/data/data_foundation_outputs/microstructure_features_table/microstructure_features_table_v0_2_candidate_controlled_25_per_role
E:/TSIS/data/data_foundation_outputs/microstructure_features_table/_microstructure_features_table_manifest_v0_2_candidate_controlled_25_per_role.json
E:/TSIS/data/data_foundation_outputs/microstructure_features_table/_microstructure_features_table_summary_v0_2_candidate_controlled_25_per_role.csv
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/microstructure_features_table_v0_2_candidate_controlled_25_per_role/microstructure_features_table_v0_2_candidate_window_manifest_v0_1.csv
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_v0_2_controlled_candidate/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/microstructure_features/microstructure_candidate_controlled_visual_readout_v0_2.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/microstructure_features/visual_evidence_v0_2_controlled_25_per_role/
```

Recommended action:

```text
Include this candidate validation in the next foundations_authority_graph
rebuild and in specialized data_foundation_outputs, microstructure_quotes_trades,
event_state_reconstruction, market_state_representation, ML feature and offline
RL governance leaves. Preserve the candidate-only status, provisional quotes
root and partial trades-source coverage as graph facts.
```

Root action:

```text
Do not rebuild root graph until foundations Graphify remediation state is
resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

The next executable work is visual/forensic evidence for the 50-window
controlled candidate and quotes E-root parity resolution before any broader
candidate or promotion claim.

### GFQ-20260627-014 - Quotes recovery clone ticker-chunk telemetry

Status: pending
Severity: HIGH
Slice:

```text
01_foundations/module_contracts/quotes
data_ops_long_running_operations
raw_storage_parity
quotes_recovery_to_target_e_root
```

Reason:

```text
The quotes recovery command for D:/quotes -> E:/TSIS/data/quotes_ was extended
with ticker-chunked telemetry so million-file copy operations are no longer
launched as opaque one-unit robocopy jobs. This changes operational guidance for
a raw data recovery workflow and affects how future agents should resume,
monitor and audit the clone into the target official E-root.
```

Changed paths:

```text
scripts/data_ops/clone_quotes_to_staging.ps1
01_foundations/module_contracts/quotes/quotes_staging_clone_runbook_v0_1.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Include this operation in the next foundations leaf refresh. Preserve that
quotes_ is the target official E-root pending post-copy parity audit and
promotion, that ticker-chunked clone mode is the preferred observable recovery
path, and that official downstream consumption is blocked until audit/promotion.
Also preserve that E:/TSIS/data/quotes is legacy/incomplete for this decision.
```

Root action:

```text
Do not rebuild root graph until the broader foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation raw storage recovery governance
```

Notes:

```text
The legacy blind clone started on 2026-06-24 may still expose only process-level
evidence. Future clones/resumes should use -ChunkByTicker when human progress
observability is required.
```

### GFQ-20260628-001 - 1m split-normalized split-affected candidate completed

Status: pending
Severity: HIGH
Slice:

```text
01_foundations/module_contracts
01_foundations/dataset_registry/ohlcv_1m
01_foundations/data_consumption_policies
price_views
ohlcv_1m_split_normalized
```

Reason:

```text
The split-affected full-universe logical candidate for ohlcv_1m_split_normalized
completed materialization and post-run audit. The repository now contains a
results contract with the completed run id, manifest/output counts, audit
counts and pending promotion gate. Future agents must not treat this as still
unexecuted, nor as a promoted production root.
```

Changed paths:

```text
01_foundations/module_contracts/ohlcv_1m_split_normalized_split_affected_materialization_results_v0_1.md
01_foundations/module_contracts/ohlcv_1m_split_normalized_full_universe_materialization_runbook_v0_1.md
01_foundations/module_contracts/ohlcv_1m_split_normalized_operational_landing_v0_1.md
01_foundations/module_contracts/README.md
01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_registry_entry.yaml
01_foundations/data_consumption_policies/ohlcv_1m_split_normalized_consumption_policy.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Refresh the affected foundations price-view leaf so graph users can discover
that run split_affected_20260627_192314 completed, produced 115667 candidate
outputs, had 0 audit FAIL cases, and remains pending promotion.
```

Root action:

```text
Do not rebuild root graph until the broader foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / Data Foundation price-view governance
```

Notes:

```text
The candidate root is E:/TSIS/data/ohlcv_1m_split_normalized_full_universe_candidate.
It is a split-affected logical full-universe candidate, not a physical full copy
and not yet an official production root.
```

### GFQ-20260628-002 - Long-running monitor stale process detection

Status: pending
Severity: HIGH
Slice:

```text
root_long_running_operations_contract
module01_long_running_monitor
data_ops_quotes_clone
```

Reason:

```text
The generic long-running monitor now derives stale_no_process when a heartbeat
still says running but the wrapper/worker processes are dead and the heartbeat
is old. This prevents stale heartbeat files from being misread as active work,
which directly affected the quotes clone run quotes_clone_to_staging_20260627T185359Z.
```

Changed paths:

```text
LONG_RUNNING_OPERATIONS_CONTRACT.md
01_TSIS_backtest_SmallCaps/scripts/monitor_long_running_operation.ps1
01_TSIS_backtest_SmallCaps/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Refresh the affected operations-governance leaf so future graph users know that
running heartbeats are not sufficient evidence of a live process. The monitor
must expose wrapper liveness and stale_no_process derived state.
```

Root action:

```text
Do not rebuild root graph until the broader foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / transversal long-running operation governance
```

Notes:

```text
This does not resume the quotes clone. It only fixes operator visibility. The
clone remains resumable by rerunning the ticker-chunk command with
-AllowNonEmptyTarget.
```

### GFQ-20260628-003 - Windows-safe telemetry JSON replacement

Status: pending
Severity: HIGH
Slice:

```text
root_long_running_operations_contract
module01_long_running_runners
data_ops_quotes_clone
one_minute_split_normalized_materialization
```

Reason:

```text
The quotes clone runner stopped after APEN because Move-Item -Force failed while
rewriting an existing heartbeat JSON file. The telemetry writer was replaced
with a Windows-safe temporary-file plus File.Replace strategy in both affected
long-running runners. The quotes clone runner also gained -StartAtTicker so the
stopped clone can resume from APEX instead of rechecking the completed prefix.
Future agents must treat the stopped clone as resumable, not as data
corruption.
```

Changed paths:

```text
LONG_RUNNING_OPERATIONS_CONTRACT.md
01_TSIS_backtest_SmallCaps/scripts/data_ops/clone_quotes_to_staging.ps1
01_TSIS_backtest_SmallCaps/scripts/run_1m_split_normalized_materialization.ps1
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/quotes/quotes_staging_clone_runbook_v0_1.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Refresh the affected long-running operations leaf so graph users know heartbeat
JSON replacement must be Windows-safe and that quotes clone runs stopped by this
telemetry failure can be resumed with -AllowNonEmptyTarget and, when supported
by log evidence, -StartAtTicker.
```

Root action:

```text
Do not rebuild root graph until the broader foundations Graphify remediation
state is resolved or explicitly waived.
```

Owner:

```text
Modulo 01 / long-running operation telemetry governance
```

Notes:

```text
Validation dry-run after fix: quotes_clone_to_staging_20260628T063552Z.
```

### GFQ-20260628-004 - Graphify build baseline provenance rule

Status: pending
Severity: HIGH
Slice:

```text
root_project_rules
foundations_graphify_governance
certification_graphify_governance
module01_changelog
```

Reason:

```text
Future Graphify builds must expose an exact Git/corpus baseline. Every new
BUILD_MANIFEST.md must record commit, dirty state, dirty/untracked paths, exact
corpus manifest, queue entries covered, queue entries left pending, diagnostics
and next-delta commands. This prevents future agents from guessing whether
git diff is measured from HEAD or from the last graph build.
```

Changed paths:

```text
PROJECT_RULES.md
00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
CHANGELOG.md
00_CTO/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
00_data_certification/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Include this governance change in the next foundations authority refresh and in
any leaf build that will become the next delta baseline.
```

Root action:

```text
No root graph yet. Do not treat this queue entry as corpus replacement; the
actual changed protocol files must be included in the leaf corpus.
```

Owner:

```text
Modulo 01 / Graphify governance
```

### GFQ-20260630-002 - Daily scanner v0.2 contract-aligned controlled replay

Status: pending
Severity: HIGH
Slice:

```text
01_foundations/module_contracts/outputs/
01_foundations/canonical_schemas/outputs/
01_foundations/validators/outputs/
01_foundations/dataset_registry/outputs/
configs/data_foundation_outputs/scanner_definitions/
tests/data_foundation_outputs/
scripts/
```

Reason:

```text
The daily scanner v0.2 builder and controlled replay were aligned with the
corrected contract semantics. The replay now disables relative-volume selection
without intraday/as-of acceleration, enforces percent-change minimum threshold
before top-N selection, treats dollar-volume as tradability not alpha, and keeps
DAS as provisional strategy-overlay seed lineage. A new controlled replay was
materialized under tests/test_runs/2026-06-30 with run_id
daily_scanner_candidates_replay_20250102_20250110_v0_2_1_contract_aligned.
```

Changed paths:

```text
01_TSIS_backtest_SmallCaps/scripts/materialize_daily_scanner_candidates_table_v0_2.py
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder_v0_2.py
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/README.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_2.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/daily_scanner_candidates_table_schema_contract.md
01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/daily_scanner_candidates_table_validators.md
01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/daily_scanner_candidates_table_registry_entry.yaml
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Refresh the Data Foundation outputs/scanner leaf so graph queries distinguish
the older v0.2 replay from the v0_2_1 contract-aligned replay and do not infer
relative-volume semantics from daily RVOL proxy.
```

Root action:

```text
No immediate root rebuild. Include in the next official foundations leaf refresh
or root integration batch.
```

Owner:

```text
Modulo 01 / Data Foundation outputs scanner governance
```

Notes:

```text
Validation: python -m pytest C:/TSIS_Data/01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder_v0_2.py -q
Result: 1 passed.
```

### GFQ-20260630-003 - Intraday scanner v0.1 first-push denominator

Status: pending
Severity: HIGH
Slice:

```text
01_foundations/module_contracts/outputs/
configs/data_foundation_outputs/scanner_definitions/
scripts/
tests/data_foundation_outputs/
```

Reason:

```text
The scanner stack now has an intraday 1m candidate detector. Daily scanner v0.3
remains a daily/EOD coarse proxy, while intraday_scanner_candidates_table_v0_1
detects first +50% crosses by premarket/regular/afterhours segment using
ohlcv_1m, volume-to-time and dollar-volume-to-time. This is semantically
important for DAS/frontside, event-state and future ML/RL state preparation.
```

Changed paths:

```text
01_TSIS_backtest_SmallCaps/scripts/materialize_intraday_scanner_candidates_table_v0_1.py
01_TSIS_backtest_SmallCaps/scripts/run_intraday_scanner_candidates_materialization_v0_1.ps1
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_intraday_scanner_candidates_table_builder_v0_1.py
01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/scanner_definitions/intraday_in_play_momentum_candidate_denominator_v0_1.yaml
01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/scanner_definitions/README.md
01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/intraday_scanner_candidates_table_schema_contract.md
01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/intraday_scanner_candidates_table_dataset_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/intraday_scanner_candidates_table_consumption_policy.md
01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/intraday_scanner_candidates_table_registry_entry.yaml
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/intraday_scanner_framework_and_definitions_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/intraday_scanner_candidates_table_target_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/intraday_scanner_candidates_table_validators.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Refresh the Data Foundation outputs/scanner leaf so graph queries distinguish
daily coarse scanner v0.3 from intraday first-push scanner v0.1.
```

Root action:

```text
No immediate root rebuild. Include in the next official foundations leaf refresh
or root integration batch.
```

Owner:

```text
Modulo 01 / Data Foundation outputs scanner governance
```

Notes:

```text
Validation: python -m pytest C:/TSIS_Data/01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_intraday_scanner_candidates_table_builder_v0_1.py -q
Result: 1 passed.
Controlled replay: C:/TSIS_Data/tests/test_runs/2026-06-30/intraday_scanner_candidates_replay_20250102_20250110_v0_1/
selected_intraday_in_play_candidate_rows = 102
full_universe_claim = false
Runner telemetry fix: run_intraday_scanner_candidates_materialization_v0_1.ps1
now avoids blocking stdout/stderr Peek()/ReadToEnd() while the Python worker is
alive, so long monthly windows can keep heartbeat updates flowing.
```

### GFQ-20260630-004 - Intraday scanner quote-guarded successor gate

Status: pending
Severity: HIGH
Slice:

```text
01_foundations/module_contracts/outputs/
01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
```

Reason:

```text
The intraday scanner now has an explicit quote-guarded successor gate.
intraday_scanner_candidates_table_v0_1 remains raw ohlcv_1m controlled replay
evidence only. The next institutional candidate must be
intraday_scanner_candidates_table_v0_2_quote_guarded_candidate and consume the
raw ohlcv_1m + repair_manifest_lt1b_v0_1.parquet overlay before any
20-year canonical scanner promotion.
```

Changed paths:

```text
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/intraday_scanner_framework_and_definitions_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/intraday_scanner_candidates_table_target_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Refresh the Data Foundation outputs/scanner leaf so graph queries show the
dependency between intraday scanner v0.2 and the ohlcv_1m_quote_guarded repair
manifest.
```

Root action:

```text
No immediate root rebuild. Include in the next official foundations leaf refresh
or root integration batch.
```

Owner:

```text
Modulo 01 / Data Foundation outputs scanner governance
```

Notes:

```text
The LT1B quote-guarded manifest is now promoted, but no scanner parquet has
been promoted. The entry now records that raw +50% spikes not confirmed by
quote-guarded bars must be preserved as evidence and rejected from selected
in-play candidates.
```

### GFQ-20260703-001 - Quotes post-copy parity audit protocol

Status: pending
Severity: HIGH
Slice:

```text
01_foundations/module_contracts/quotes/
scripts/data_ops/
data_ops_manifests/quotes_parity_audit
```

Reason:

```text
The completed D:/quotes -> E:/TSIS/data/quotes_ recovery clone now has a
documented post-copy parity audit protocol before any downstream promotion.
The protocol defines Phase A structural path/size parity and Phase B full
SHA256 parity, both sharded across the top-level ticker roster with independent
manifests, heartbeat, PID files, summary CSVs and mismatch evidence.
```

Changed paths:

```text
01_TSIS_backtest_SmallCaps/scripts/data_ops/audit_quotes_clone_parity.py
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/quotes/quotes_staging_clone_runbook_v0_1.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Refresh the quotes/data-ops recovery leaf so graph queries know that
E:/TSIS/data/quotes_ is still blocked pending parity audit, and that promotion
requires the structural audit at minimum plus optional full SHA256 evidence for
the strongest byte-level parity claim.
```

Root action:

```text
No immediate root rebuild. Include in the next official foundations leaf refresh
or root integration batch after the overnight audit evidence exists.
```

Owner:

```text
Modulo 01 / Data Foundation quotes recovery governance
```

Notes:

```text
No audit run was launched by this documentation change. The audit is intended
for overnight terminal execution. Syntax of audit_quotes_clone_parity.py was
checked with Python AST parsing before documenting the commands.
```


### GFQ-20260704-002 - State observable eligibility contract

Status: pending
Severity: HIGH
Slice:

```text
01_foundations/module_contracts/outputs/
01_foundations/canonical_schemas/outputs/
```

Reason:

```text
A cross-output contract defines which source columns or column groups may feed future market_state/event_state builders, with cutoff, quality gate, allowed usage and status. Formula governance is now also closed for declared derived observables.
```

Changed paths:

```text
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
00_CTO/CHANGELOG.md
```

Recommended action:

```text
Refresh the Data Foundation outputs/state-composition leaf so future graph queries route agents to state_observable_eligibility_contract_v0_1.md and state_derived_observables_formula_contract_v0_1.md before state builder, ML/RL or AlphaEvolve work.
```

Root action:

```text
No immediate root rebuild. Include in the next official foundations leaf refresh or root integration batch.
```

Owner:

```text
Modulo 01 / Data Foundation market state governance
```

Notes:

```text
Eligibility, formula, timestamp policy and snapshot role gates are complete for declared scope. State builder contract, validators and controlled fixtures remain next gates.
```

### GFQ-20260704-003 - State derived observable formulas contract

Status: pending
Severity: HIGH
Slice: 01_foundations / module_contracts / outputs

Summary:

A new contract closes formula/window/cutoff governance for derived observables feeding future market_state/event_state builders. It complements state_observable_eligibility_contract_v0_1.md and keeps state materialization, ML/RL datasets and AlphaEvolve evaluators disabled until later gates exist.

Changed paths:

```text
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Expected graph update:

- link derived formula contract to eligibility contract, market_state/event_state composition, coverage/lookback policy and state builder route;
- mark formula gate complete for declared scope;
- leave state builder contract and validators as next steps.

### GFQ-20260704-004 - State decision timestamp policy contract

Status: pending
Severity: HIGH
Slice: 01_foundations / module_contracts / outputs

Summary:

A new contract closes legal timestamp governance for future market_state/event_state builders. It complements observable eligibility and derived formula contracts by defining decision_timestamp_utc, state_cutoff_utc, availability time, received time, observation time, window legality and temporal leakage gates.

Changed paths:

```text
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_decision_timestamp_policy_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Expected graph update:

- link timestamp policy to eligibility, formula, market_state/event_state composition and coverage/lookback policy;
- mark timestamp policy complete for declared scope;
- leave state builder contract and validators as next steps.

### GFQ-20260704-005 - State snapshot roles contract

Status: pending
Severity: HIGH
Slice: 01_foundations / module_contracts / outputs

Summary:

A new contract closes state_role governance for future market_state/event_state builders. It defines canonical snapshot roles, allowed timestamp types/windows, ML/RL/AlphaEvolve usage boundaries and role-specific leakage validators.

Changed paths:

```text
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_snapshot_roles_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_decision_timestamp_policy_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Expected graph update:

- link snapshot roles to timestamp policy, eligibility, formula and market_state/event_state composition;
- mark snapshot roles complete for declared scope;
- leave state builder contract and validators as next steps.
## Entry template

```text
### GFQ-YYYYMMDD-NNN - <title>

Status: pending | pending_leaf_build | leaf_built | pending_root_integration | closed | cancelled
Severity: LOW | MEDIUM | HIGH | CRITICAL
Slice:
Reason:
Changed paths:
Recommended action:
Root action:
Owner:
Notes:
```

### GFQ-20260704-006 - State builder contract

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
01_foundations/module_contracts/outputs
01_foundations/data_foundation_outputs_state_composition
01_foundations/market_state_event_state_builder_route
```

Reason:

```text
A new contract closes the state builder assembly gate for future market_state/event_state builders. Eligibility, formula, timestamp, role and builder-contract gates are now complete for declared scope. Validators and controlled fixtures are the next gates before candidate materialization.
```

Changed paths:

```text
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_builder_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Expected graph action:

```text
- add state_builder_contract_v0_1.md as completed gate after snapshot roles;
- link it to eligibility, formula, timestamp and roles contracts;
- link it to existing fixture/candidate builder evidence without promoting official tables;
- route next work to leakage/formula/timestamp/role/builder validators and controlled fixtures.
```
### GFQ-20260704-007 - Event candidate tables contract

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
01_foundations/module_contracts/outputs
01_foundations/data_foundation_outputs_state_composition
01_foundations/event_candidate_tables_route
```

Reason:

```text
A new contract defines daily/1m candidate event tables as the missing layer between scanner candidates and event_state. It introduces daily_strategy_candidate_events_table_v0_1 and intraday_1m_strategy_candidate_events_table_v0_1 as not-materialized targets.
```

Changed paths:

```text
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Expected graph action:

```text
- add event_candidate_tables_contract_v0_1.md as completed route contract;
- link scanners to daily/1m candidate event targets;
- link candidate events to future event_windows expansion and event_state fixtures;
- keep event/state/outcome/ML/RL/AlphaEvolve boundaries explicit.
```
### GFQ-20260704-008 - Event candidate table schema contracts

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
01_foundations/canonical_schemas/outputs
01_foundations/event_candidate_tables_route
01_foundations/data_foundation_outputs_state_composition
```

Reason:

```text
Nuevos schema contracts canonicos definen la forma requerida de daily_strategy_candidate_events_table_v0_1 e intraday_1m_strategy_candidate_events_table_v0_1. Cierran el paso de schema, pero no materializan tablas de eventos.
```

Changed paths:

```text
01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/daily_strategy_candidate_events_table_schema_contract.md
01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/intraday_1m_strategy_candidate_events_table_schema_contract.md
01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/README.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Expected graph action:

```text
- anadir nodos de schema para eventos candidatos daily/intradia;
- conectarlos con event_candidate_tables_contract_v0_1.md y futuros validators/builders;
- preservar las fronteras scanner/event/event_window/event_state/outcome;
- mantener materializacion oficial, ML/RL y AlphaEvolve deshabilitados.
```
### GFQ-20260704-009 - Event candidate table validators contract

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
01_foundations/module_contracts/outputs
01_foundations/event_candidate_tables_route
01_foundations/data_foundation_outputs_state_composition
```

Reason:

```text
Nuevo contrato de validators define que debe fallar antes de construir o consumir daily_strategy_candidate_events_table_v0_1 e intraday_1m_strategy_candidate_events_table_v0_1. Cierra el contrato de validators, pero no implementa validators ejecutables.
```

Changed paths:

```text
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_table_validators_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Expected graph action:

```text
- anadir nodo event_candidate_table_validators_contract_v0_1;
- conectarlo a schemas daily/intradia y event_candidate_tables_contract_v0_1;
- enrutar siguiente trabajo a validators ejecutables, fixtures y builders candidate;
- preservar que no hay materializacion oficial ni ML/RL/AlphaEvolve habilitado.
```
### GFQ-20260704-010 - Canonical State vs Representation Layer contract

Status: `pending_next_outputs_leaf_refresh`

Severity: `HIGH`

Slice:

```text
01_foundations/module_contracts/outputs
01_foundations/data_foundation_outputs_state_composition
01_foundations/representation_layer_boundary
```

Reason:

```text
Nuevo contrato separa Canonical State de Representation Layer. Cierra la frontera conceptual para evitar que scores, embeddings, parameter grids, semantic states o thresholds optimizados entren como verdad base de market_state/event_state.
```

Changed paths:

```text
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_canonical_vs_representation_layer_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Expected graph action:

```text
- anadir nodo state_canonical_vs_representation_layer_contract_v0_1;
- conectarlo despues de state_builder/event_candidate validators y antes de semantic_state_representation_contract futuro;
- distinguir Canonical State de Representation Candidate;
- mantener schemas oficiales, materializacion y ML/RL/AlphaEvolve production deshabilitados.
```

