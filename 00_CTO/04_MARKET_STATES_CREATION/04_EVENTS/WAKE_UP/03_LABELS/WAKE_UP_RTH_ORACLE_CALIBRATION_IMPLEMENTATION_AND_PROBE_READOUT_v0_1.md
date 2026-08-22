# Wake-up RTH oracle calibration - implementation and probe readout v0.1

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `wake_up_rth_oracle_calibration_implementation_and_probe_readout` |
| `document_version` | `v0_1` |
| `document_status` | `SUPERSEDED_FOR_FULL_PANEL_STATUS_BY_STRATIFICATION_REPAIR_READOUT` |
| `experiment_id` | `EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001` |
| `scope` | `DEVELOPMENT_ONLY_LEGACY_RTH` |
| `issued_at` | `2026-08-17` |

## 1. Resultado

La preparación ejecutable del oracle retrospectivo Wake-up RTH está completa.
El código, tests, preflight, probe equivalente a producción por los cuatro
shards y certificador terminal han pasado.

```text
FULL 2,400 TARGET RUN
=
READY_FOR_HUMAN_LAUNCH

FULL RUN EXECUTED
=
NO

WUL-D01..D08
=
NOT_FROZEN

A/B COMPARISON
=
NOT_AUTHORIZED
```

El agente no lanza la operación larga. El humano ejecuta el comando congelado
y el proceso se detiene en `WAITING_HUMAN_BLIND_REVIEW`.

## 2. Pregunta científica y frontera

El experimento busca candidatos donde una acción:

```text
estaba dormida después de las 09:30 America/New_York
-> presenta la primera transición observable de actividad negociada realizada
-> recibe corroboración retrospectiva tipada
```

La búsqueda:

- es neutral respecto de Binding A y Binding B;
- usa solamente desarrollo TA-3 congelado, 2011-2022;
- no lee temporal validation 2023-2024 ni final OOS 2025-2026;
- no usa trayectoria intradía de precio, dirección, retorno ni outcomes;
- usa `trade_price * trade_size` exclusivamente para notional negociado;
- usa el precio presesión exclusivamente para estratificar el panel ciego.

## 3. Autoridades exactas

### Targets

```text
G:\TSIS\data\DATA_FOUNDATION_OUTPUTS\trading_activity_ta3_stratified_sample\
trading_activity_ta3_stratified_sample_v0_1_20260807T175808Z\
selected_target_contexts_v0_1.parquet

SHA-256
=
55890736132080098114ac356ab5bce66adf3c26a9a4b92915788594d06b2220
```

### Calendario

```text
G:\TSIS\data\data_foundation_outputs\market_calendar\
market_calendar_v0_1.parquet

SHA-256
=
cbf1879261866d980c5a8542fadf683dbc91f96b80b7865055417a16d1e6e87c
```

### Trades y elegibilidad

```text
raw trades
=
G:\TSIS\data\trades_ticks_prod_2005_2026

policy matrix
=
C:\TSIS_Data\tests\third_party_evidence\massive\market_operations\
snapshot_20260806T220504Z\policy_matrix_candidate_v0_1\
trading_activity_trade_condition_policy_matrix_candidate_v0_1.csv

policy SHA-256
=
b2f208496809cb970437d04024d93bfb98780b54b5d790091362aa145eb9635f
```

El evaluador de elegibilidad se importa desde:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\
evaluate_trading_activity_trade_eligibility.py
```

## 4. Implementación

La implementación vive en:

```text
C:\TSIS_Data\03_TSIS_Lab\04_experiments\
EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001
```

Componentes:

```text
scripts/wake_up_rth_core.py
scripts/build_wake_up_rth_candidate_pool.py
scripts/build_wake_up_blind_panel.py
scripts/render_wake_up_blind_gallery.py
scripts/aggregate_wake_up_blind_reviews.py
scripts/derive_wul_decision_evidence.py
scripts/validate_wake_up_rth_run.py
scripts/run_wake_up_rth_oracle_calibration.ps1
scripts/monitor_wake_up_rth_oracle_calibration.ps1
configs/wake_up_rth_calibration_v0_1.json
configs/wul_decisions_template_v0_1.json
tests/test_wake_up_rth_core.py
```

## 5. Panel ciego

El panel contiene candidatos y controles estratificados por:

```text
cohorte temporal;
franja RTH;
banda de precio presesión;
banda de market-cap proxy;
actividad previa;
calidad de fuente.
```

Roles de muestreo:

```text
CANDIDATE_ACTIVITY_TRANSITION
CONTROL_DORMANT
CONTROL_ONE_CLUSTER
CONTROL_CONTEXT_NORMAL_ACTIVITY
CONTROL_QUALITY_OR_ARTIFACT
CONTROL_RANDOM_ELIGIBLE
```

La galería no muestra ticker, fecha, trayectoria de precio, Binding A/B ni
outcomes. Su manifest público solo expone:

```text
blind_case_id
case_id
chart_file
review_order
```

Dos revisores independientes asignan una de estas clases:

```text
POSITIVE_WAKE_UP
NEGATIVE_ONE_PRINT
NEGATIVE_INSUFFICIENT_CORROBORATION
NEGATIVE_CONTEXT_NORMAL_HIGH_ACTIVITY
NEGATIVE_DATA_ARTIFACT
AMBIGUOUS
UNAVAILABLE
```

Los desacuerdos requieren adjudicador separado. `AMBIGUOUS` y `UNAVAILABLE`
no se convierten silenciosamente en negativos.

## 6. Incidentes detectados y controles permanentes

### 6.1 Cardinalidad legacy

El manifest TA-3 declara `23,400` segundos por sesión completa. La autoridad
corregida de Binding A es:

```text
open + 1 second
through
close - 1 second
=
23,399 symbol-seconds
```

Las 2,400 filas presentan exactamente la discrepancia legacy conocida de
`+1`. El runner solo admite ese caso exacto y falla ante cualquier otra
diferencia.

### 6.2 Identidad de target

`target_ordinal` no es global: se repite de `1..10` dentro de cada uno de
los 240 bloques. El probe inicial procesó 240 targets y colisionó al persistir
por ordinal.

La identidad de runtime corregida es:

```text
target_file_key
=
block_id
+
target_ordinal
+
instrument_id
+
session_date
```

Runner, resume, panel, renderer y certifier consumen la misma identidad
compuesta.

### 6.3 Compatibilidad PowerShell

Se eliminó el uso de `utf8NoBOM`, no soportado por Windows PowerShell 5.1.
Los writes gobernados del wrapper utilizan una codificación compatible.

### 6.4 Resume

`-Resume` rechaza:

- config SHA distinto;
- mode distinto;
- runner SHA distinto;
- core SHA distinto;
- partición existente con cardinalidad o identidad incorrecta.

Una carpeta de panel incompleta se preserva con sufijo
`.incomplete.<timestamp>` y se reconstruye. Resume nunca mezcla versiones,
schemas ni identidades.

## 7. Tests y probe equivalente a producción

```text
pytest
=
5 passed
```

Probe autoritativo:

```text
G:\TSIS\data\research_experiments\
EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\runs\
wake_up_rth_probe_v0_5_20260817
```

Resultado:

```text
shards                       = D1, D2, D3, D4
targets                      = 4/4
candidates                   = 11
failures                     = 0
probe blind-panel rows       = 150
probe gallery charts         = 8
terminal validation checks   = 20/20 PASS
final stage                  = WAITING_HUMAN_BLIND_REVIEW
```

Certificador:

```text
SHA-256
=
172843422bd02ab1ca5cc346a9d197796d8f1e0f2e8c86b413c99fcf267efbe9
```

La menor diversidad del panel del probe es esperada: contiene cuatro sesiones.
El full renderiza el panel completo.

## 8. Preflight final congelado

```text
run_root
=
G:\TSIS\data\research_experiments\
EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\runs\
wake_up_rth_preflight_v0_3_20260817

status                    = COMPLETE_PREFLIGHT_ONLY
governed targets          = 2,400
projected metric storage  = 0.457 GiB
G free                    = approximately 178.66 GiB
```

Hashes ligados al lanzamiento:

```text
config SHA-256
=
ca2d224fc66520c6f0260e62fa6e97abcf614dd1992fff6bb8f021b458ed5ac6

candidate-pool script SHA-256
=
78e2393d6bca661f2ed015996a32619132e0de92d341b8137d9d005068bed8ba

core SHA-256
=
f874496451997180da2fdb96119e6e7d11dd6c96c287852f3e43652bbd933a9b
```

Si código o config cambian, estos hashes quedan invalidados y deben repetirse
tests, probe D1..D4 y preflight.

## 9. Comandos humanos

### Lanzamiento full

```powershell
& "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\scripts\run_wake_up_rth_oracle_calibration.ps1" -RunId "wake_up_rth_full_v0_1_20260817" -Mode full
```

### Monitor

```powershell
& "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\scripts\monitor_wake_up_rth_oracle_calibration.ps1" -RunRoot "G:\TSIS\data\research_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\runs\wake_up_rth_full_v0_1_20260817" -IntervalSeconds 10 -Compact -Watch
```

### Resume del mismo run

```powershell
& "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001\scripts\run_wake_up_rth_oracle_calibration.ps1" -RunId "wake_up_rth_full_v0_1_20260817" -Mode full -Resume
```

No crear otro `RunId` para continuar el mismo run.

## 10. Secuencia posterior

```text
human full launch
-> terminal validator PASS
-> blind gallery and two independent reviews
-> separate adjudication
-> WUL-D01..D08 evidence readout
-> explicit human freeze of D07
-> development labels and eligible denominator
-> D12 exact validation/final-OOS custody
-> Binding B B-02 freeze
-> B implementation/probes/materialization
-> A/B comparison
```

La finalización computacional del full no congela D07 ni autoriza A/B.

## 11. Addendum posterior al full

El full candidate run terminó `2,400/2,400`, produjo `4,447` candidatos y
cero fallos. La auditoría posterior invalidó únicamente su panel/galería:
`240/240` casos pertenecían a `CLOSE_240M_PLUS` por prioridad lexical en el
sampler. El candidate pool permanece válido.

El estado vigente, root cause, controles permanentes, probe reparado `25/25
PASS` y comandos del rebuild full viven en:

```text
WAKE_UP_RTH_BLIND_PANEL_STRATIFICATION_INCIDENT_AND_REPAIR_READOUT_v0_1.md
```
