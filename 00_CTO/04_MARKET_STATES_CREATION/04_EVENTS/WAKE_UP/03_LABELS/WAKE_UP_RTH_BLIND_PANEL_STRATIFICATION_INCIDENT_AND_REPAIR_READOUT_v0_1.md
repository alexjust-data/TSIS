# Wake-up RTH blind-panel stratification incident and repair readout v0.1

## 0. Control

| Field | Value |
|---|---|
| `document_status` | `REPAIR_PROBE_PASS_FULL_REBUILD_PENDING_HUMAN_LAUNCH` |
| `experiment_id` | `EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001` |
| `incident_severity` | `HIGH` |
| `scope` | `BLIND_PANEL_AND_GALLERY_ONLY` |
| `candidate_pool_status` | `VALID_COMPLETE` |
| `D07_status` | `NOT_FROZEN` |

## 1. Resultado del full válido

El run development terminó correctamente:

```text
run_id                     = wake_up_rth_full_v0_1_20260817
targets                    = 2,400/2,400
candidates                 = 4,447
failures                   = 0
source-unavailable targets = 159, typed and preserved
Binding A consumed         = false
Binding B consumed         = false
intraday price path        = not consumed
```

El `final_manifest.json` del candidate run tiene SHA-256:

```text
f81830a86a656ec5fa34456f6d183492a9a4c49089145a4ea7376fa0b5b0e0ff
```

No se repiten el scan de 2.400 sesiones ni el candidate pool.

## 2. Finding posterior

La galería inicial no es apta para revisión humana. Sus 240 filas quedaron en:

```text
CLOSE_240M_PLUS = 240/240
OPEN_0_60M      = 0/240
MID_60_240M     = 0/240
```

La fuente no estaba colapsada. El candidate pool full contiene diversidad
temporal en D1..D4. El defecto estaba en `_deterministic_sample`: ordenaba
`sampling_stratum` lexicográficamente y después truncaba con `.head(count)`.
Los strata cuyo nombre comenzaba por `CLOSE_` quedaban seleccionados primero.

El certifier inicial solo verificaba que la columna de franja RTH existiera; no
verificaba cobertura de sus valores. Por ello su PASS no certificaba diversidad
temporal y queda revocado para el panel/galería. No se revoca el candidate run.

## 3. Corrección

La versión reparada:

1. balancea explícitamente `OPEN_0_60M`, `MID_60_240M` y
   `CLOSE_240M_PLUS`;
2. selecciona de forma determinista dentro de cada stratum;
3. redistribuye shortages sin reintroducir prioridad lexical;
4. hash-vincula panel a config y candidate final manifest;
5. hash-vincula galería a config y panel manifest;
6. exige IDs ciegos y casos únicos;
7. exige cardinalidad exacta por cohorte/rol en full;
8. exige las tres franjas RTH en full;
9. valida staging antes de promover;
10. mueve la galería inválida a cuarentena, sin borrarla.

Hashes del código reparado:

```text
panel builder = f6cab77ff76978d81bd6a09634b09f62ee61ccc52118411a92c7be2bb82cb8c3
gallery       = ee5d36c7166a27793d5b2d0371e91630c9c9a8c6f9e3ecd44da40a9fbb771141
validator     = 14a717234d9fd2e0d624631795abb0f6b0b30e75a7166b769b30882139fae7ba
repair runner = f66f93f57fac20aba2d957e9a05f7243eb7ec6c4375bf41ae703a2314a06b1ea
monitor       = b8a81584980a20b54828cd0710565885fccafb8971f794b8bfaa9fa39b4dee10
```

## 4. Probe del repair

```text
repair_id             = blind_panel_rth_stratification_probe_v0_4
targets               = 4/4, D1..D4
terminal checks       = 25/25 PASS
panel rows            = 150
OPEN_0_60M            = 44
MID_60_240M           = 43
CLOSE_240M_PLUS       = 63
gallery charts        = 8
network               = prohibited and not used
invalid prior panel   = preserved in quarantine
```

## 5. Full repair gobernado

El rebuild full es una operación larga y debe ser lanzado por el humano:

```powershell
& "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\scripts\rebuild_wake_up_rth_blind_panel.ps1" -RunRoot "G:\TSIS\data\research_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\runs\wake_up_rth_full_v0_1_20260817" -RepairId "blind_panel_rth_stratification_v0_2"
```

Monitor:

```powershell
& "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\scripts\monitor_wake_up_rth_blind_panel_repair.ps1" -RunRoot "G:\TSIS\data\research_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\runs\wake_up_rth_full_v0_1_20260817" -RepairId "blind_panel_rth_stratification_v0_2" -IntervalSeconds 10 -Compact -Watch
```

Resume, únicamente si los hashes siguen coincidiendo:

```powershell
& "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\scripts\rebuild_wake_up_rth_blind_panel.ps1" -RunRoot "G:\TSIS\data\research_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\runs\wake_up_rth_full_v0_1_20260817" -RepairId "blind_panel_rth_stratification_v0_2" -Resume
```

## 6. Gate

```text
candidate search                         = COMPLETE_VALID
initial blind panel/gallery              = INVALID_QUARANTINE_PENDING
repair probe                             = PASS
full blind-panel repair                  = PENDING_HUMAN_LAUNCH
human blind review                       = BLOCKED_UNTIL_FULL_REPAIR_PASS
WUL-D01..D08 / D07 freeze                = NOT_AUTHORIZED
Binding B B-03 / A-B comparison / OOS    = NOT_AUTHORIZED
```
