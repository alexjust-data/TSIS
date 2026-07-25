# Scanner Candidate Selection

Fecha: 2026-06-30
Estado: candidate_policy
Owner layer: `00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION`
Authority type: CTO architecture and navigation

## Rol

Esta carpeta explica, a nivel CTO, como TSIS debe seleccionar candidatos
in-play antes de construir `market_state` o `event_state`.

No es la autoridad operativa de schemas, builders, validators o registries.

La autoridad operativa vive en:

```text
01_TSIS_DATA_FOUNDATION/01_foundations
```

Esta carpeta existe para que un humano o agente entienda:

- por que existe una capa de scanner;
- que problema resuelve;
- que tablas y contratos ya existen;
- que no debe confundirse con estado, evento, estrategia, label o reward;
- como conecta con DAS, Market State, Event State, ML/RL y AlphaEvolve.

## Regla central

```text
El denominador base decide a quien se puede mirar.
Los perfiles genericos deciden como ordenar o inspeccionar.
Los overlays de estrategia aplican hipotesis especificas despues.
El market_state decide que sabia TSIS en ese momento.
La estrategia decide si ese estado encaja con una hipotesis.
ML/RL no entrena directamente sobre scanner rows.
```

## Orden de lectura

1. `intraday_scanner_candidates_contract_v0_1.md`
2. `scanner_base_and_in_play_momentum_contract_v0_3.md`
3. `scanner_base_universe_and_profiles_contract_v0_2.md`
4. `scanner_candidate_selection_architecture_v0_1.md`
5. `scanner_definitions_trade_station_vs_broad_discovery_v0_1.md`
6. `scanner_table_and_contract_map_v0_1.md`
7. `scanner_to_market_state_promotion_path_v0_1.md`
8. `strategy_scanner_overlay_policy_v0_1.md`

Notebook de inspeccion:

```text
notebook/daily_scanner_candidates_v0_3_run_inspection.ipynb
notebook/intraday_scanner_candidates_v0_1_run_inspection.ipynb
```

Uso:

- abrir manifests y summaries del run;
- ver tablas creadas;
- analizar KPIs, solapes y razones de inclusion;
- graficar movimiento, volumen, tradability, market cap y calidad;
- revisar casos frontera antes de usar el run como denominador de research.

Policy transversal para estrategias:

```text
strategy_scanner_overlay_policy_v0_1.md
```

Aplica a toda estrategia nueva en `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/`.
Define como consumir `daily_scanner_candidates_table`, declarar denominadores,
crear overlays y evitar sesgo de solo casos positivos.

Primera implementacion especifica:

```text
C:/TSIS_Data/00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/DAS_SCANNER_USAGE_AND_OVERLAY_RUNBOOK_v0_1.md
```

Ese documento no reemplaza los contratos de Data Foundation. Explica como una
estrategia debe consumir el denominador scanner, declarar filtros y construir
un overlay sin sesgo de solo casos positivos.

## Decision activa 2026-06-30

La lectura activa ya no es:

```text
dos scanners independientes
```

Tampoco es:

```text
base elegible = in-play
```

La lectura activa `v0.3` es:

```text
base_eligible_smallcap_denominator
-> in_play_momentum_candidate_denominator
-> strategy overlays
```

Contratos activos:

```text
intraday_scanner_candidates_contract_v0_1.md
01_foundations/module_contracts/outputs/intraday_scanner_framework_and_definitions_contract_v0_1.md
01_foundations/module_contracts/outputs/intraday_scanner_candidates_table_target_contract_v0_1.md
scanner_base_and_in_play_momentum_contract_v0_3.md
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_3.md
01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_3.md
```

Denominador base:

```text
common_stock = true
market_cap_usd < 100000000
0.5 < last_price <= 20
data_quality in usable/review
```

Denominador in-play momentum:

```text
base_eligible_smallcap_denominator
+ movement >= 50%
+ volume_today >= 500000 OR dollar_volume_today >= 250000
```

Reglas:

- `base_eligible` dice a quien mirar, no quien esta in-play;
- `in_play_momentum` decide que ticker tuvo movimiento explotable;
- el replay diario usa `daily_high_vs_prev_close_pct`, `pct_chg_1d` y `gap_pct`;
- el scanner intradia v0.1 segmenta 04:00-20:00 New York desde `ohlcv_1m`;
- para estrategias intradia, el daily scanner v0.3 es proxy coarse, no detector oficial de primer push;
- `float` es columna contextual futura, no filtro global;
- DAS y cualquier estrategia viven como overlays posteriores.

## Decision intradia 2026-06-30

El scanner diario v0.3 no puede certificar:

```text
first_cross_ts
premarket vs regular vs afterhours
volume_to_time_at_first_cross
dollar_volume_to_time_at_first_cross
```

Por tanto, para research intradia, DAS/frontside, event-state y futuros estados
ML/RL, la pieza activa es:

```text
intraday_scanner_candidates_table_v0_1
```

Implementacion:

```text
01_TSIS_DATA_FOUNDATION/scripts/materialize_intraday_scanner_candidates_table_v0_1.py
01_TSIS_DATA_FOUNDATION/scripts/run_intraday_scanner_candidates_materialization_v0_1.ps1
01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_intraday_scanner_candidates_table_builder_v0_1.py
```

Replay controlado inicial:

```text
C:/TSIS_Data/tests/test_runs/2026-06-30/intraday_scanner_candidates_replay_20250102_20250110_v0_1/
rows = 33413
selected_intraday_in_play_candidate_rows = 102
first_cross_premarket_rows = 114
first_cross_regular_rows = 82
first_cross_afterhours_rows = 39
full_universe_claim = false
```

Pendiente explicito:

```text
float_context_table
```

Debe crearse antes de usar float en scanner u overlays. Campos minimos:

```text
ticker
instrument_id
as_of_date
float_shares
shares_outstanding
free_float_pct
source
source_document
source_field
point_in_time_valid
quality_state
is_estimated
```

Hasta entonces, `overview_weighted_shares_outstanding` puede auditarse como
contexto de shares outstanding, pero no es float institucional y no puede
poblar `float_shares`.

Los replays `v0.1` y `v0.2` quedan como evidencia historica de forma, lineage y
aprendizaje semantico, no como arquitectura final para materializacion amplia.

## Cadena conceptual

```text
raw / audited foundation tables
-> scanner_candidate_selection
-> intraday_scanner_candidates_table for intraday strategy denominators
-> daily_scanner_candidates_table only for coarse daily/EOD context
-> strategy overlays when needed
-> strategy-specific experimental state tables
-> event_state_candidate / market_state_candidate
-> institutional_market_state
-> ML/RL / backtest / decision / AlphaEvolve evaluators
```

## No-goals

Esta carpeta no debe:

- redefinir schemas canonicos;
- duplicar dataset registry;
- reemplazar validators;
- guardar outputs de runs;
- contener parquets;
- convertirse en una estrategia;
- esconder thresholds ejecutables no versionados;
- promocionar un scanner como feature store ML/RL.

## Fuentes operativas relacionadas

```text
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_3.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/intraday_scanner_framework_and_definitions_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/intraday_scanner_candidates_table_target_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_3.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/daily_scanner_candidates_table_schema_contract.md
01_TSIS_DATA_FOUNDATION/01_foundations/contract_registry/dataset_contracts/daily_scanner_candidates_table_dataset_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/data_consumption_policies/daily_scanner_candidates_table_consumption_policy.md
01_TSIS_DATA_FOUNDATION/01_foundations/dataset_registry/outputs/daily_scanner_candidates_table_registry_entry.yaml
01_TSIS_DATA_FOUNDATION/01_foundations/validators/outputs/daily_scanner_candidates_table_validators.md
01_TSIS_DATA_FOUNDATION/configs/data_foundation_outputs/scanner_definitions/
01_TSIS_DATA_FOUNDATION/scripts/materialize_daily_scanner_candidates_table.py
01_TSIS_DATA_FOUNDATION/scripts/materialize_daily_scanner_candidates_table_v0_2.py
01_TSIS_DATA_FOUNDATION/scripts/materialize_daily_scanner_candidates_table_v0_3.py
01_TSIS_DATA_FOUNDATION/scripts/run_daily_scanner_candidates_materialization_v0_3.ps1
01_TSIS_DATA_FOUNDATION/scripts/materialize_intraday_scanner_candidates_table_v0_1.py
01_TSIS_DATA_FOUNDATION/scripts/run_intraday_scanner_candidates_materialization_v0_1.ps1
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/strategy_scanner_overlay_policy_v0_1.md
C:/TSIS_Data/00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/DAS_SCANNER_USAGE_AND_OVERLAY_RUNBOOK_v0_1.md
```
