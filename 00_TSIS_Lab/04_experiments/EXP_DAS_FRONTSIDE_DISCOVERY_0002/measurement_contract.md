# Measurement Contract - EXP_DAS_FRONTSIDE_DISCOVERY_0002

Fecha: 2026-07-06
Estado: draft_operativo

## Principio

Todas las metricas deben calcularse desde anchors declarados.

No se permite mover el punto de medicion para que el resultado mejore.

```text
anchor -> ventana -> metrica -> lineage
```

## Anchors Minimos

| Anchor | Que representa | Precio base inicial |
| --- | --- | --- |
| `scanner_gate` | momento en que el scanner captura el ticker | precio observable en scanner gate segun policy |
| `push_start` | inicio del primer tramo expansivo | open/close de barra de despertar segun policy |
| `first_push_high` | maximo del primer tramo antes del primer dip | high corregido/guarded del tramo |
| `first_dip_low` | minimo real del primer pullback despues del first push | low corregido/guarded del dip |
| `recovery_point` | punto donde empieza recuperacion del dip | regla candidata |
| `rebreak` | ruptura/recuperacion valida de first_push_high | executable price segun policy |
| `fake_rebreak` | ruptura no confirmada o fallo de ruptura | precio/timestamp de intento fallido |

## MFE Y MAE

Para long:

```text
MFE(anchor, horizon) = max(high entre anchor y horizon) / anchor_price - 1
```

```text
MAE(anchor, horizon) = min(low entre anchor y horizon) / anchor_price - 1
```

El resultado debe guardarse como porcentaje.

## Returns

```text
return_Nm(anchor) = close_Nm / anchor_price - 1
```

Si no hay barra exacta en `N`, aplicar policy declarada:

```text
next_available_bar
or
missing
```

No interpolar sin contrato.

## Recovery Metrics

```text
first_dip_recovered = precio posterior recupera first_push_high segun regla candidata
```

Metricas:

```text
time_to_recover_first_push_high
bars_to_recover_first_push_high
max_recovery_pct_from_dip
recovery_before_regular_open
recovery_without_new_low
```

## Destruction Metrics

Un ticker puede destruirse aunque haya hecho primer push.

Metricas iniciales:

```text
death_after_dip_flag
failure_below_first_dip_low_flag
failure_below_scanner_gate_flag
return_10m_from_dip
return_30m_from_dip
max_drawdown_from_dip
```

La definicion exacta de `death_after_dip` queda como candidata hasta sweep/validacion.

## Fake Rebreak Metrics

Un fake rebreak no es solo una vela que toca el nivel.

Debe registrar:

```text
attempt_ts
attempt_price
break_type = wick_only / close_break / body_break
volume_on_attempt
prior_volume_avg
close_above_level
hold_above_level_n_bars
failure_after_attempt
```

## Opportunity Decomposition

### scanner_to_first_push

```text
scanner_to_first_push_move_pct = first_push_high_price / scanner_gate_price - 1
```

### scanner_to_dip

```text
scanner_to_dip_mae_pct = first_dip_low_price / scanner_gate_price - 1
```

### dip_to_recovery

```text
dip_to_first_push_recovery_pct = first_push_high_price / first_dip_low_price - 1
```

### missed_move

Si `inplay_gate` se define despues:

```text
missed_move_pct = inplay_executable_price / scanner_gate_price - 1
```

En `0002`, si no hay inplay oficial, se calcula version candidata:

```text
missed_move_to_rebreak_candidate_pct = rebreak_executable_price / scanner_gate_price - 1
```

### tradable_after_rebreak_candidate

```text
tradable_after_rebreak_mfe_Nm = max(high despues de rebreak hasta N) / rebreak_executable_price - 1
```

## Threshold Sensitivity

Para cada `threshold_pct` medir:

```text
case_count
recovery_rate
rebreak_rate
fake_rebreak_rate
destruction_rate
median_mfe_from_scanner
median_mae_from_scanner
median_mfe_from_dip
median_mae_from_dip
median_missed_move_to_rebreak_candidate
```

La lectura debe buscar zonas, no un numero magico.

## Coste De Oportunidad

Para comparar filtros:

```text
lost_cases = cases_in_looser_filter - cases_in_stricter_filter
```

```text
lost_good_cases = casos perdidos que luego habrian tenido recovery/continuation segun definicion candidata
```

```text
noise_removed = casos eliminados que luego mueren/no recuperan/fallan
```

No se permite llamar "mejor filtro" a un filtro que solo reduce casos sin medir oportunidad perdida.

## Ejecucion Intraminuto

Si una oportunidad depende de una mecha dentro de vela 1m, la lectura inicial es:

```text
opportunity envelope
```

No es backtest ejecutable hasta validar con policy de ejecucion:

```text
next_bar_open
confirming_bar_close
quotes/trades intraminuto
slippage proxy
```

## Campos De Calidad Obligatorios

Cada fila de output debe incluir:

```text
visual_price_source
repair_manifest_state
scale_guard_state
coverage_ratio
missing_bar_ratio
anchor_quality_state
lineage_manifest
```
