# Neutralized Area Factor - Duxinator Advance Concepts Draft v0.1

Fecha: 2026-06-27
Estado: source_note / factor draft.
Fuente primaria:

```text
Steven Dux - Duxinator - 4 - Advance Concepts
6 - Identifying Neutralized Area
```

## 1. Proposito

Este documento define la lectura inicial de TSIS para `Neutralized Area`.

No es una estrategia direccional.
No valida edge.
No autoriza operativa.

Es un factor que responde:

```text
donde deja de haber reward porque el precio entra en una zona aceptada,
soportada o neutralizada por volumen/participantes?
```

## 2. Definicion

Una `neutralized area` es una zona donde el mercado ha aceptado precio y deja de
moverse con facilidad.

Lectura fuente:

```text
buyer and seller agreed;
the stock does not really move anymore.
```

Interpretacion TSIS:

```text
zona donde el precio puede dejar de caer/subir porque ya existe acuerdo,
soporte, volumen previo o participantes que cubren/compran/venden.
```

## 3. Uso principal

Dux usa la zona neutralizada para medir:

```text
maximum reward
remaining reward
risk/reward quality
shortable vs not shortable multi-day runner
take-profit area for gap up short
avoid area for first red day / multi-day top shorts
```

TSIS debe modelarla como factor de reward restante, no como entrada.

## 4. Neutralized area simple

Caso simple:

```text
prior accepted price ~= 2
stock gaps/runs higher
if it drops back to 2, movement may stall
```

Lectura:

```text
la zona donde el precio estuvo aceptado sin volumen agresivo puede actuar como
limite natural del movimiento.
```

Formula conceptual:

```text
remaining_reward_to_neutralized_area_pct =
  (current_price - neutralized_area_price) / current_price * 100
```

## 5. Half-gain neutralized target

Dux menciona usar la zona neutralizada para medir una devolucion aproximada del
movimiento.

Lectura fuente:

```text
entire gain / 2 can approximate a neutralized/take-profit region
```

Formula candidata:

```text
half_gain_neutralized_price =
  run_start_price + 0.5 * (run_high_price - run_start_price)
```

Uso:

```text
gap up short reward estimate
```

No debe convertirse en target institucional sin estadistica.

## 6. Multi-day runner neutralizado

En multi-day runners, la zona neutralizada puede aparecer como capas de soporte
muy cercanas al precio actual.

Lectura fuente:

```text
si la zona neutralizada esta demasiado cerca del first red day/open,
el short tiene mal risk/reward y puede quedar squeezed.
```

Motivo:

```text
shorts previos cubren cerca de la zona,
longs ven soporte,
el precio deja de caer facilmente.
```

Estado:

```text
neutralized_multiday_runner
```

## 7. Soporte por volumen consolidado

Dux describe sumar volumen de consolidaciones para estimar soporte.

Ejemplo fuente conceptual:

```text
day A volume = 30M
day B volume = 30M
consolidation volume A = 20M
consolidation volume B = 25M
support_volume ~= 45M-50M
```

Lectura TSIS:

```text
una zona con mucho volumen consolidado puede neutralizar un short si el precio
llega alli con poco reward restante.
```

Campos:

```text
neutralized_support_volume
neutralized_support_dollar_volume
support_zone_low
support_zone_high
support_zone_mid
```

## 8. Shortable vs not shortable runner

### 8.1. Not shortable

Condicion conceptual:

```text
first_red_day_entry_area close to neutralized support area
```

Lectura:

```text
el short entra justo encima de soporte/covering zone.
```

Estado:

```text
neutralized_area_too_close
```

### 8.2. Shortable

Condicion conceptual:

```text
large clean air gap between current/entry area and neutralized area
```

Lectura:

```text
hay reward suficiente antes de chocar contra soporte neutralizante.
```

Estado:

```text
neutralized_area_far_enough
```

## 9. Gap without support

Dux describe que si en medio de la subida no hay soporte/volumen pesado, la zona
neutralizada puede estar mucho mas abajo.

Lectura:

```text
si el runner es parabolico y deja vacio entre precio actual y soporte,
hay mas reward teorico.
```

Estado:

```text
clean_air_to_neutralized_area
```

## 10. Estados del factor

```text
neutralized_area_unknown
neutralized_area_detected
neutralized_area_too_close
neutralized_area_far_enough
neutralized_multiday_runner
heavy_support_neutralization
clean_air_to_neutralized_area
half_gain_neutralized_target
short_reward_blocked_by_neutralized_area
short_reward_open_to_neutralized_area
```

| Estado | Significado |
|---|---|
| `neutralized_area_unknown` | No hay zona identificable. |
| `neutralized_area_detected` | Existe una zona aceptada/neutralizada. |
| `neutralized_area_too_close` | La zona esta demasiado cerca del punto operativo conceptual. |
| `neutralized_area_far_enough` | Hay distancia suficiente hasta la zona. |
| `neutralized_multiday_runner` | Runner con capas cercanas que dificultan short. |
| `heavy_support_neutralization` | Soporte creado por volumen consolidado material. |
| `clean_air_to_neutralized_area` | Poco soporte entre precio actual y zona inferior. |
| `half_gain_neutralized_target` | Zona aproximada por mitad del movimiento. |
| `short_reward_blocked_by_neutralized_area` | Reward short bloqueado por soporte cercano. |
| `short_reward_open_to_neutralized_area` | Reward short disponible hasta la zona. |

## 11. Formulas candidatas

### 11.1. Neutralized area midpoint

```text
neutralized_area_mid =
  (neutralized_area_low + neutralized_area_high) / 2
```

### 11.2. Distance to neutralized area

```text
distance_to_neutralized_area_pct =
  (current_price - neutralized_area_mid) / current_price * 100
```

Para long context:

```text
distance_up_to_neutralized_area_pct =
  (neutralized_area_mid - current_price) / current_price * 100
```

### 11.3. Support volume

```text
neutralized_support_volume =
  sum(volume_in_support_zone_windows)
```

### 11.4. Support dollar volume

```text
neutralized_support_dollar_volume =
  sum(volume_i * price_i for bars inside support zone)
```

### 11.5. Reward to neutralized area

```text
remaining_reward_to_neutralized_area_pct =
  abs(current_price - neutralized_area_mid) / current_price * 100
```

### 11.6. Clean air ratio

```text
clean_air_ratio =
  distance_to_neutralized_area_pct / current_risk_pct
```

## 12. Campos minimos para factor_table

```text
factor_id
ticker
exchange
company_name
session_date
strategy_context
current_price
run_start_price
run_high_price
neutralized_area_low
neutralized_area_high
neutralized_area_mid
neutralized_area_source
neutralized_area_start_date
neutralized_area_end_date
neutralized_support_volume
neutralized_support_dollar_volume
distance_to_neutralized_area_pct
remaining_reward_to_neutralized_area_pct
half_gain_neutralized_price
clean_air_ratio
neutralized_area_state
review_required
```

## 13. Aplicacion por estrategia

### 13.1. Gap Up Short

Usar para:

- estimar zona de profit/reward maximo;
- evitar esperar una caida mas alla de la zona donde el mercado ya esta
  neutralizado;
- comparar half-gain target contra soporte real.

### 13.2. First Red Day / Multi-day Top

Usar para:

- evitar shortear directamente contra soporte cercano;
- medir si hay clean air debajo del entry area;
- separar runners shorteables de runners neutralizados.

### 13.3. Bounce Short

Usar para:

- distinguir resistencia superior de soporte inferior;
- medir si el fade tiene espacio antes de zona neutralizada;
- evitar confundir rechazo real con simple retorno a zona aceptada.

## 14. Chart requirements

Un notebook que use este factor debe mostrar:

- zona neutralizada como banda horizontal;
- volumen acumulado dentro de esa zona;
- distancia desde precio actual;
- half-gain neutralized price si aplica;
- clean-air area entre precio actual y zona;
- soporte/resistencia cercano que degrada risk/reward.

## 15. Imagenes deseadas del propio video

No se deben insertar imagenes de otros videos.

Capturas deseadas:

```text
6 - Identifying Neutralized Area:
00:00-01:10  neutralized area simple / buyer-seller agreement
01:10-02:00  half-gain / take-profit neutralized area
02:00-04:00  neutralized multi-day runner no-trade example
04:00-05:20  support-volume layers too close to first red day
05:20-06:40  clean-air runner with lower neutralized area
06:40-07:05  shortable vs not shortable comparison
```

## 16. Regla final

Neutralized Area no responde:

```text
donde entro?
```

Responde:

```text
cuanto reward real queda antes de que el precio choque con una zona aceptada,
soportada o neutralizada por volumen/participantes?
```

Si un notebook short de multi-day runner no calcula distancia a zona
neutralizada, puede clasificar como buena una operacion con reward ya bloqueado.
