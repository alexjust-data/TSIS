# Secondary Mirror Note

Fecha: 2026-07-12
Scope: `data_foundation_outputs_topology_20260629`

## Relacion Con CTO_1

Existe una copia secundaria ligada en:

```text
C:/TSIS_Data/00_CTO_1/003_STADE_tables/
```

La autoridad primaria sigue viviendo en:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/graphify-out/leaf_slices/data_foundation_outputs_topology_20260629/
```

La carpeta `C:/TSIS_Data/00_CTO_1/003_STADE_tables/` no es una source of truth independiente. Si se modifica informacion material en los originales, la copia secundaria debe actualizarse en la misma operacion para mantener ambas superficies emparejadas.

No editar manualmente `graph.json`, `graph.html` ni `GRAPH_REPORT.md` para reflejar esta nota; esos archivos siguen siendo outputs Graphify generados.