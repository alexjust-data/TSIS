# Daily Scanner Candidates Table Target Contract v0.2

## Estado

Tipo: output table target contract.

Modulo: `01_TSIS_backtest_SmallCaps`.

Ambito: `CAPA 1 - DATA FOUNDATION`.

Status:

```text
builder_implemented_controlled_replay_not_official
```

## Rol

`daily_scanner_candidates_table_v0_2` materializa candidatos diarios/in-play
como:

```text
one base denominator + multiple governed profiles
```

Responde:

```text
que tickers fueron evaluados en la base smallcap <100M, y por que perfiles quedaron seleccionados?
```

No responde:

```text
cual es el estado completo?
que estrategia operar?
que outcome ocurrio?
que reward asignar?
hubo fill?
```

## Grain

```text
scanner_run_id + scanner_definition_id + session_date + as_of_utc + instrument_id
```

En `v0.2`, `scanner_definition_id` debe ser:

```text
base_in_play_universe_scanner_v0_2
```

Los perfiles viven como flags/metadata en la misma fila.

## Required v0.2 Fields

Ademas de las columnas heredadas `v0.1`, el output candidato `v0.2` debe
preservar:

```text
base_universe_definition_id
base_universe_definition_version
scanner_profile_set_id
scanner_profile_ids
selected_trade_station_like_profile
selected_relative_volume_profile
selected_percent_change_profile
selected_dollar_volume_tradability_profile
selected_das_research_profile
selected_any_profile
float_filter_state
float_shares
float_asof_date
float_source
```

Columnas heredadas de compatibilidad:

```text
selected_trade_station_like_top25
selected_broad_discovery
selected_by_pct_chg_rank
selected_by_volume_acceleration_rank
selected_by_dollar_volume_rank
selected_by_composite_in_play_rank
```

Estas columnas heredadas no sustituyen los nuevos perfiles. En `v0.2`,
`selected_broad_discovery` es solo una compatibilidad para consumidores antiguos
y no debe reintroducir el modelo de dos scanners independientes.

## Builder And Test

```text
builder: scripts/materialize_daily_scanner_candidates_table_v0_2.py
test: tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder_v0_2.py
```

El builder:

- lee `master_daily_table_v0_1`;
- lee `instrument_master_v0_1`;
- lee `market_calendar_v0_1`;
- lee configs `scanner_definitions/*_v0_2.yaml`;
- no escanea raw quotes/trades ni millones de ficheros;
- escribe parquet, summary y manifest bajo el `output-root` declarado.

## Output Root Policy

Small controlled samples, smoke runs, notebook demos and test evidence:

```text
C:/TSIS_Data/tests/test_runs/<run_date>/<run_id>/
```

Long-range candidate replays:

```text
E:/TSIS/data/data_foundation_outputs/daily_scanner_candidates_table/candidate_replays/<run_id>/
```

Official promoted root remains reserved:

```text
E:/TSIS/data/data_foundation_outputs/daily_scanner_candidates_table/daily_scanner_candidates_table_v0_2/
```

Official promotion requires a separate promotion step, validator suite,
manifest review and status update.

## Current Controlled Evidence

Fixture test:

```text
python -m pytest C:/TSIS_Data/01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder_v0_2.py -q
```

Validated semantics:

```text
one scanner_definition_id
one row per deduplicated instrument/session/as_of
market_cap < 100M as base hard filter
volume >= 500k only for trade_station_like_profile
float_filter_state = not_used_until_point_in_time_float_source_exists
ML/RL/live flags remain false
```

Controlled replay evidence:

```text
run_id: daily_scanner_candidates_replay_20250102_20250110_v0_2
root: C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_replay_20250102_20250110_v0_2/
rows: 15323
sessions: 6
instruments: 2590
selected_any_profile_rows: 4023
selected_trade_station_like_profile_rows: 150
selected_relative_volume_profile_rows: 150
selected_percent_change_profile_rows: 150
selected_dollar_volume_tradability_profile_rows: 2930
selected_das_research_profile_rows: 2472
selected_below_500k_volume_rows: 3177
duplicate_key_groups: 0
full_universe_claim_true_rows: 0
float_filter_used_rows: 0
ml_feature_candidate_rows: 0
rl_state_candidate_rows: 0
live_downstream_candidate_rows: 0
```

This evidence is still `controlled_replay_candidate`, not official E-root
promotion.

## Required Separation

The table must distinguish:

```text
candidate discovery
state construction
event definition
outcome/label construction
strategy decision
execution simulation
```

No builder may collapse these into one output.

## Promotion Gate

Before official materialization:

1. run a wider controlled replay;
2. implement validator suite against the physical `v0.2` output;
3. verify denominator and duplicate-grain behavior;
4. preserve no-ML/no-RL/no-live flags;
5. decide whether long-range candidate replays remain non-promoted or are
   promoted into the official E-root;
6. update Graphify leaf in a maintenance window.

## Contract Stack

```text
scanner_framework: 01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_2.md
schema: 01_foundations/canonical_schemas/outputs/daily_scanner_candidates_table_schema_contract.md
dataset_contract: 01_foundations/contract_registry/dataset_contracts/daily_scanner_candidates_table_dataset_contract_v0_1.md
consumption_policy: 01_foundations/data_consumption_policies/daily_scanner_candidates_table_consumption_policy.md
registry: 01_foundations/dataset_registry/outputs/daily_scanner_candidates_table_registry_entry.yaml
validators: 01_foundations/validators/outputs/daily_scanner_candidates_table_validators.md
coverage_policy: 01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
```
