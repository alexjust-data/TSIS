# Short Seller Trap Layers Factor - Duxinator Advance Concepts Draft v0.1

Fecha: 2026-06-27
Estado: source_note / factor draft.
Fuente primaria:

```text
Steven Dux - Duxinator - 4 - Advance Concepts
7 - Layers of Short Seller Trap
```

## 1. Proposito

Este documento define la lectura inicial de TSIS para `Layers of Short Seller
Trap`.

No es una estrategia direccional.
No valida edge.
No autoriza operativa.

Es un factor que identifica cuando un short nuevo queda demasiado cerca de capas
de shorts previos que pueden cubrir y crear presion compradora.

La pregunta central es:

```text
estoy shorteando contra una zona donde otros shorts previos necesitan cubrir?
```

## 2. Idea central

Dux describe una situacion donde muchos short sellers entran en distintos
niveles durante un runner o microfloat squeeze.

Cuando el precio vuelve cerca de sus precios promedio, esos shorts pueden cubrir
para salir flat o reducir perdida.

Esa cobertura crea compra.

Si el nuevo short esta demasiado cerca de esas capas, la cobertura de una capa
puede empujar el precio hacia la siguiente, generando reaccion en cadena.

```text
short layer A covers
-> price lifts
-> short layer B gets nervous and covers
-> price lifts again
-> new short is trapped
```

## 3. Secuencia fuente

La secuencia conceptual descrita:

```text
1. massive spike / gap up;
2. pullback que invita shorts;
3. squeeze que fuerza cobertura;
4. nuevo pullback que vuelve a atraer shorts;
5. consolidacion donde se acumulan short sellers;
6. afternoon squeeze;
7. siguiente dia gap down o red attempt;
8. nuevos shorts entran cerca de capas previas;
9. shorts antiguos cubren cerca de break-even;
10. cobertura crea buy pressure y puede disparar squeeze.
```

## 4. Por que el porcentaje no basta

Dux advierte que en microfloat no basta mirar:

```text
stock up 500%
there must be downside
```

La lectura correcta es:

```text
el porcentaje solo cumple criterio inicial;
despues manda el chart y la localizacion de capas.
```

Para TSIS:

```text
runup_pct no puede ser el unico filtro de un short.
```

Debe combinarse con:

```text
consolidation_layers
average_short_layer_price
distance_to_layer
float
float_rotation
volume_in_layer
gap_down_location
```

## 5. Capa de short sellers

Una capa es una zona donde probablemente entraron shorts.

Origenes:

- pullback despues de squeeze;
- bounce into resistance;
- failed push aparente;
- consolidation after massive spike;
- red/green-to-red attempt;
- prior afternoon short attempt.

Campos:

```text
short_layer_low
short_layer_high
short_layer_mid
short_layer_start_ts
short_layer_end_ts
short_layer_volume
short_layer_context
```

## 6. Distancia peligrosa

La fuente menciona un ejemplo conceptual:

```text
prior short layer around 5
new short around 5.5
```

Si ambas zonas estan cerca, la cobertura en la primera capa puede empujar el
precio contra la segunda.

Formula candidata:

```text
distance_to_nearest_short_layer_pct =
  abs(current_short_area_price - nearest_short_layer_mid) /
  current_short_area_price * 100
```

Estado:

```text
short_layer_too_close
```

## 7. Chain reaction risk

Cuando hay varias capas cercanas:

```text
layer_1 cover
-> layer_2 cover
-> layer_3 cover
```

Estado:

```text
short_covering_chain_risk
```

Campos:

```text
short_layer_count
nearest_layer_distance_pct
layer_stack_width_pct
layer_volume_sum
```

## 8. Overextended gap-down danger

El transcript usa este factor para decidir cuando no usar una estrategia tipo
gap-down/green-to-red sobre un ticker muy extendido.

Lectura:

```text
si el gap down abre demasiado cerca de capas previas de shorts,
esas capas pueden cubrir y convertir el gap down en squeeze.
```

Estado:

```text
gap_down_into_short_layer_trap
```

## 9. Estados del factor

```text
short_trap_unknown
short_layer_detected
short_layer_too_close
short_layer_far_enough
stacked_short_layers
short_covering_chain_risk
gap_down_into_short_layer_trap
microfloat_short_trap_risk
invalid_short_due_to_layer_pressure
```

| Estado | Significado |
|---|---|
| `short_trap_unknown` | No hay capas identificadas. |
| `short_layer_detected` | Existe al menos una zona probable de shorts previos. |
| `short_layer_too_close` | La entrada/caso conceptual esta cerca de una capa. |
| `short_layer_far_enough` | La capa queda suficientemente lejos. |
| `stacked_short_layers` | Varias capas cercanas pueden activar cobertura encadenada. |
| `short_covering_chain_risk` | La cobertura de una capa puede empujar hacia otra. |
| `gap_down_into_short_layer_trap` | Gap down/red attempt cae sobre capas de shorts. |
| `microfloat_short_trap_risk` | Microfloat amplifica el riesgo de squeeze. |
| `invalid_short_due_to_layer_pressure` | La presion de cobertura invalida el caso short. |

## 10. Formulas candidatas

### 10.1. Nearest layer distance

```text
nearest_short_layer_distance_pct =
  abs(current_reference_price - nearest_short_layer_mid) /
  current_reference_price * 100
```

### 10.2. Layer stack width

```text
layer_stack_width_pct =
  (max(short_layer_high) - min(short_layer_low)) /
  current_reference_price * 100
```

### 10.3. Layer volume sum

```text
short_layer_volume_sum =
  sum(volume_inside_detected_short_layers)
```

### 10.4. Trap pressure score

Formula exploratoria:

```text
short_trap_pressure_score =
  short_layer_volume_sum /
  max(nearest_short_layer_distance_pct, 1)
```

Interpretacion:

```text
mas volumen de capa y menor distancia = mas riesgo de cobertura contra el short.
```

## 11. Campos minimos para factor_table

```text
factor_id
ticker
exchange
company_name
session_date
strategy_context
float
market_cap
current_reference_price
runup_pct
gap_down_pct
short_layer_count
nearest_short_layer_low
nearest_short_layer_high
nearest_short_layer_mid
nearest_short_layer_distance_pct
short_layer_volume_sum
layer_stack_width_pct
short_trap_pressure_score
short_trap_state
microfloat_flag
review_required
```

## 12. Aplicacion por estrategia

### 12.1. First Red Day / Multi-day Top

Usar para:

- evitar shortear sobre capas de shorts previos;
- distinguir downside real de squeeze-prone red attempt;
- detectar si el first red day abre demasiado cerca de covering zones.

### 12.2. Gap Down / Green-to-Red Short

Usar para:

- invalidar gaps down que abren sobre capas de shorts atrapados;
- medir si el short nuevo empuja contra covering pressure.

### 12.3. Bounce Short

Usar con cautela:

- una zona de resistencia puede ser buena;
- pero si tambien es zona de shorts previos muy cercanos, puede actuar como
  fuente de cobertura.

## 13. Chart requirements

Un notebook que use este factor debe mostrar:

- capas de short sellers como bandas horizontales;
- precio medio de cada capa;
- distancia desde precio actual;
- volumen aproximado dentro de cada capa;
- zona de gap down o red attempt;
- bandera si el precio actual esta demasiado cerca de capas previas.

## 14. Imagenes deseadas del propio video

No se deben insertar imagenes de otros videos.

Capturas deseadas:

```text
7 - Layers of Short Seller Trap:
00:00-01:00  spike/pull/squeeze sequence
01:00-02:30  shorts holding because ticker is up huge
02:30-04:00  consolidation layers and breakout gaining equity
04:00-05:40  next-day gap down near previous short layer
05:40-07:00  chain reaction of short sellers covering
07:00-07:35  rule: cannot short too close to consolidation/average short layers
```

## 15. Regla final

Short Seller Trap Layers no responde:

```text
el ticker esta muy extendido?
```

Responde:

```text
hay capas de shorts previos tan cerca que su cobertura puede convertirse en
buy pressure contra el nuevo short?
```

Si un notebook short solo mira porcentaje de extension y no calcula distancia a
capas de shorts previos, puede clasificar como buena una trampa evidente.
