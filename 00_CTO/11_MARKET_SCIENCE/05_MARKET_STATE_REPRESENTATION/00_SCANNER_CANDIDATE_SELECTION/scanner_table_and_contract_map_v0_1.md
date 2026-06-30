# Scanner Table And Contract Map v0.1

Fecha: 2026-06-30
Estado: reference_map

## Rol

Este documento lista donde vive el trabajo real ya hecho sobre el scanner.

No reemplaza esos contratos. Sirve como mapa para humanos y agentes.

## Autoridad operativa

```text
01_TSIS_backtest_SmallCaps/01_foundations
```

## Contratos principales

| Tema | Ruta | Rol |
| --- | --- | --- |
| Framework de scanners | `01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md` | Define `trade_station_like` y `broad_discovery`. |
| Tabla objetivo | `01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md` | Define rol, replay, output roots y prohibiciones. |
| Schema canonico | `01_foundations/canonical_schemas/outputs/daily_scanner_candidates_table_schema_contract.md` | Define columnas, grain y flags. |
| Dataset contract | `01_foundations/contract_registry/dataset_contracts/daily_scanner_candidates_table_dataset_contract_v0_1.md` | Define identidad logica y estado del dataset. |
| Consumption policy | `01_foundations/data_consumption_policies/daily_scanner_candidates_table_consumption_policy.md` | Define usos permitidos/prohibidos downstream. |
| Registry entry | `01_foundations/dataset_registry/outputs/daily_scanner_candidates_table_registry_entry.yaml` | Registra estado y rutas del dataset. |
| Validators | `01_foundations/validators/outputs/daily_scanner_candidates_table_validators.md` | Define checks requeridos antes de promocion. |

## Configs versionadas

```text
01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/scanner_definitions/trade_station_like_scanner_v0_1.yaml
01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/scanner_definitions/broad_in_play_discovery_scanner_v0_1.yaml
```

Regla:

```text
Los thresholds de scanner no deben esconderse en notebooks ni en prompts.
```

## Implementacion

Builder:

```text
01_TSIS_backtest_SmallCaps/scripts/materialize_daily_scanner_candidates_table.py
```

Test:

```text
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder.py
```

Notebook de inspeccion:

```text
01_TSIS_backtest_SmallCaps/01_research/notebooks/data_foundation_outputs/daily_scanner_candidates_replay_view_v0_1.ipynb
```

## Primer replay controlado

Ruta:

```text
C:/TSIS_Data/tests/test_runs/2026-06-29/daily_scanner_candidates_replay_20250102_20250110_v0_1/
```

Scope:

```text
start_date: 2025-01-02
end_date: 2025-01-10
price_view: daily_raw
as_of_policy: session_close_utc_from_market_calendar
official_e_root_materialization: false
full_universe_claim: false
```

Validaciones registradas:

```text
rows: 30646
sessions: 6
instruments: 2590
selected_trade_station_like_top25_rows: 150
selected_broad_discovery_rows: 3196
broad_selected_below_500k_volume_rows: 2383
duplicate_key_groups: 0
full_universe_claim_true_rows: 0
ml_feature_candidate_rows: 0
rl_state_candidate_rows: 0
live_downstream_candidate_rows: 0
```

Interpretacion:

```text
El replay prueba forma, lineage y separacion operacional-vs-broad.
No prueba output oficial E:/ ni full universe institucional.
```

## Output roots

Samples pequenos, tests y notebooks:

```text
C:/TSIS_Data/tests/test_runs/<run_date>/<run_id>/
```

Replays largos candidatos:

```text
E:/TSIS/data/data_foundation_outputs/daily_scanner_candidates_table/candidate_replays/<run_id>/
```

Root oficial reservado:

```text
E:/TSIS/data/data_foundation_outputs/daily_scanner_candidates_table/daily_scanner_candidates_table_v0_1/
```

## Estado actual

```text
builder_implemented_controlled_replay_not_official
```

Significa:

- hay contrato;
- hay configs;
- hay builder;
- hay test;
- hay replay pequeno controlado;
- hay notebook de inspeccion;
- no hay promocion oficial full historical;
- no debe consumirse como estado ML/RL final.

## Pendiente antes de promocion

1. Ejecutar validator suite completa sobre replay candidato.
2. Decidir periodo y denominador de replay amplio.
3. Materializar candidate replay amplio en `E:/TSIS/data/.../candidate_replays/`.
4. Revisar evidencia visual/forense si se usa como seed de estados.
5. Promocionar solo con manifest, changelog, registry status y consumo downstream claro.

