# Trading Activity Binding A independent percentile replay plan v0.1

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_role` | `INDEPENDENT_SCIENTIFIC_AUDIT_PLAN` |
| `document_status` | `PROBE_PREPARED_FULL_SCOPE_NOT_AUTHORIZED` |
| `snapshot_at` | `2026-08-14` |
| `binding` | `trading_activity_binding_a_candidate_v0_2` |
| `scope` | `legacy_rth_reconciled_event_time_research_only` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `binding_b_materialization` | `NOT_AUTHORIZED` |

## 1. Por qué existe este gate

La auditoría científica v0.1 comprobó dominio `[0,1]`, estados, cardinalidad,
fechas causales, ratios y compresión sobre una muestra estratificada. No
reconstruyó de forma independiente los cuatro rankings empíricos a partir de
las observaciones históricas `current_state`.

Esto es una laguna de evidencia, no evidencia de que los percentiles estén
mal. Además existe una comparación Python/C++ exacta anterior de 25 sesiones,
8.612.625 filas y cero diferencias. Esa equivalencia demuestra que ambos
motores coincidieron, pero no sustituye un tercer cálculo independiente de la
fórmula científica.

El nuevo gate responde exactamente:

```text
¿Coincide cada percentile materializado, fila por fila, con
count(reference_value <= current_value) / baseline_total_count
reconstruido desde las particiones current_state históricas?
```

No se permite interpolación ni midrank. Los empates son inclusivos por la
derecha (`<=`).

## 2. Independencia del oráculo

El oráculo nuevo:

- lee las particiones inmutables `current_state` conservadas en cada bloque;
- usa únicamente PyArrow, NumPy y Pandas para lectura, ordenación y tiempo ET;
- no importa ni llama al motor Python de baseline, al vectorizado, al adapter
  C++ ni al binario nativo;
- selecciona historia separadamente por `(clock_minute_et, window_seconds)`;
- excluye la sesión objetivo y cualquier fecha futura;
- aplica `B20/B60/B120` y mínimos `15/40/80`;
- compara valores exactos, máscaras `NULL`, estado, cardinalidad y primeras y
  últimas fechas de referencia;
- falla con una sola diferencia.

Variables auditadas:

```text
trade_count_percentile_pit
share_volume_percentile_pit
dollar_volume_percentile_pit
arrival_rate_percentile_pit
```

## 3. Secuencia obligatoria

```text
tests unitarios PASS
-> preflight hash-frozen PASS
-> PROBE: 1 bloque por shard, 2 sesiones por bloque
-> auditoría de 4 sesiones normales + 4 early-close
-> cero diferencias exactas
-> revisión humana
-> crear un NUEVO plan FULL autorizado desde el final PASS del probe
-> FULL: 240 bloques / 2.400 sesiones
-> actualizar el veredicto científico Binding A
```

El scope FULL preparado no es ejecutable. El autorizador exige el manifiesto
final PASS del probe, cobertura 4/4 shards, 8/8 sesiones, igualdad exacta y una
autorización humana cuyo identificador empiece por `AUTHORIZED_BY_`.

## 4. Scope físico medido

### Probe preparado

```text
bloques                              = 4
shards                               = 4/4
sesiones target                      = 8
sesiones normales                    = 4
early closes                         = 4
particiones current_state históricas = 521
filas históricas                     = 60.576.395
bytes históricos comprimidos         = 170.862.796
filas baseline comparadas            = 2.159.880
bytes baseline comprimidos           = 8.423.244
celdas percentile auditadas          = 8.639.520
```

### FULL preparado, todavía bloqueado

```text
bloques                              = 240
shards                               = 60/60/60/60
sesiones target                      = 2.400
particiones current_state históricas = 32.013
filas históricas                     = 3.729.376.935
bytes históricos comprimidos         = 13.742.743.270 (12,80 GiB)
filas baseline comparadas            = 837.990.000
bytes baseline comprimidos           = 4.472.744.880 (4,17 GiB)
celdas percentile auditadas          = 3.351.960.000
```

El auditor también verifica los SHA-256 de inputs. Por tanto, el FULL hará una
pasada de hash y otra lectura columnar de las variables necesarias. No escribe
3.351 millones de rankings nuevos: conserva solo checkpoints, contadores y
ejemplos de discrepancia, por lo que el output será pequeño.

## 5. Coste esperado y política de hardware

Sí, el FULL es una auditoría pesada por CPU y por ordenación, no por espacio de
salida. En la máquina Ryzen 7 5800X / 32 GB y con inputs en el HDD USB `D:`, v0.1
usa un único worker para evitar presión de RAM, paging y búsquedas concurrentes
en disco mecánico.

Antes del probe no se certifica una duración. La referencia anterior C++
recalculó 25 sesiones completas en 927,5 segundos, pero este oráculo tiene otro
algoritmo y solo reconstruye cuatro percentiles. Como presupuesto conservador,
el FULL debe tratarse inicialmente como un trabajo de aproximadamente 12-48
horas. El probe medirá por separado carga de historia y coste por sesión; solo
con esos tiempos se publicará una proyección seria del FULL y se decidirá si
mantener un worker u optimizar sin cambiar resultados.

## 6. Artefactos ejecutables

```text
01_TSIS_DATA_FOUNDATION/scripts/
trading_activity_binding_a_percentile_replay_oracle.py
build_trading_activity_binding_a_percentile_replay_plan.py
authorize_trading_activity_binding_a_percentile_replay_full.py
run_trading_activity_binding_a_percentile_replay.py
monitor_trading_activity_binding_a_percentile_replay.ps1

01_TSIS_DATA_FOUNDATION/tests/
test_trading_activity_binding_a_percentile_replay.py
```

Planes congelados:

```text
configs/trading_activity_binding_a_percentile_replay_probe_v0_1_20260814.json
configs/trading_activity_binding_a_percentile_replay_full_preparation_v0_1_20260814.json
```

SHA-256 del plan probe tras el preflight:

```text
57498fdd039c143215081fb8214c21debb0d817e31634854ae7108b155a6d904
```

## 7. Comandos operativos del probe

Lanzamiento humano, en una sola línea:

```powershell
python "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\run_trading_activity_binding_a_percentile_replay.py" --plan "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\trading_activity_binding_a_percentile_replay_probe_v0_1_20260814.json"
```

Monitor:

```powershell
& "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\monitor_trading_activity_binding_a_percentile_replay.ps1" -RunRoot "C:\TSIS_Data\runtime\trading_activity_binding_a_percentile_replay_probe_v0_1_20260814\runtime" -IntervalSeconds 10 -Compact -Watch
```

Reanudación, únicamente con los mismos hashes:

```powershell
python "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\run_trading_activity_binding_a_percentile_replay.py" --plan "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\trading_activity_binding_a_percentile_replay_probe_v0_1_20260814.json" --resume
```

Parada segura:

```powershell
@{requested_by=$env:USERNAME;reason='operator_safe_stop';requested_at_utc=(Get-Date).ToUniversalTime().ToString('o')} | ConvertTo-Json -Compress | Set-Content -LiteralPath "C:\TSIS_Data\runtime\trading_activity_binding_a_percentile_replay_probe_v0_1_20260814\runtime\stop_requested.json" -Encoding UTF8
```

La parada se atiende entre unidades de cálculo y conserva los bloques PASS. El
`--resume` reutiliza únicamente checkpoints ligados al mismo plan, runner y
oráculo.

## 8. Estado al cerrar esta preparación

```text
tests unitarios                 = 4 PASS
preflight plan/hash/index       = PASS
probe                           = PREPARED_NOT_LAUNCHED
FULL scope                      = PREPARED_NOT_AUTHORIZED
Binding A restriction           = OPEN_PENDING_REPLAY
Binding B materialization       = NOT_AUTHORIZED
OOS                             = NOT_AUTHORIZED
canonical promotion             = NOT_AUTHORIZED
```

