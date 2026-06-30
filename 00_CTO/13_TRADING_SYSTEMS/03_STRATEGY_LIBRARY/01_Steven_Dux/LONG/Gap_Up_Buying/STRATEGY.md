# Gap Up Buying Strategy - Duxinator Source Draft v0.1

Fecha: 2026-06-27
Estado: source_note / strategy draft.
Fuente primaria: Steven Dux - Duxinator - `4 - Gap Up Buying`.

## 1. Proposito

Este documento define la lectura inicial de TSIS para `Gap Up Buying` segun el
material Duxinator.

No valida edge.
No crea parametros institucionales.
No autoriza operativa.

Su funcion es traducir la estrategia long de gap crowded controlado en reglas
medibles para busqueda historica.

## 2. Resumen tecnico

`Gap Up Buying` es una estrategia long para tickers crowded, pero no
excesivamente crowded.

Dux la plantea como compra de gap premarket donde:

1. el market cap sigue siendo pequeno;
2. el float es bajo;
3. el volumen premarket esta en un rango activo pero no saturado;
4. la accion puede consolidar y romper o ir parabolica al open;
5. se busca capturar el push estadistico medio.

La idea central:

```text
volumen premarket suficiente para empujar
pero no tan alto como para volver el ticker demasiado crowded
```

## 3. Condiciones minimas del setup

### 3.1. Market cap

Fuente:

```text
market_cap < 100M / 200M
```

La transcripcion menciona ambos niveles de forma imperfecta. TSIS debe medir
sensibilidad por bucket.

### 3.2. Float

Fuente:

```text
float < 10M
```

Cuanto menor el float, mayor puede ser el push medio, pero tambien mayor el
riesgo de warrants, spreads y movimientos violentos.

### 3.3. Volumen premarket

Fuente:

```text
premarket_volume < 1M       -> menos probable que empuje
premarket_volume 1M-3M      -> zona preferida
premarket_volume > 3M       -> demasiado crowded
```

### 3.4. Estructura premarket aceptable

Dux menciona dos escenarios preferidos:

```text
premarket consolidation breakout
premarket parabolic push
```

Escenarios a evitar:

```text
premarket weakness
gap que ya perdio 50% de su ganancia
distancia excesiva entre resistencia premarket y precio de apertura
```

## 4. Formulas candidatas

### 4.1. Push esperado por float

```text
expected_push_pct_bucket =
  20%-25% if float between 2M and 10M
  25%-50% if float below 2M
```

Estos porcentajes son fuente Dux, no parametros institucionales.

### 4.2. Damage del gap antes del open

```text
premarket_gap_damage_pct =
  (premarket_high - open_reference_price) /
  (premarket_high - prior_close) * 100
```

Interpretacion:

```text
damage >= 50% -> evitar long segun fuente
```

### 4.3. Distancia a resistencia premarket

```text
distance_open_to_premarket_resistance_pct =
  (premarket_high / open_reference_price - 1) * 100
```

Si esta distancia es demasiado grande, la estrategia long se degrada.

## 5. Estados candidatos

```text
gap_up_buying_candidate
premarket_volume_too_low
premarket_volume_preferred
premarket_volume_too_crowded
premarket_consolidation_breakout
premarket_parabolic_candidate
premarket_weakness_avoid
gap_damage_avoid
invalid_gap_up_buying
```

## 6. Campos minimos para candidate_table

```text
candidate_id
ticker
exchange
company_name
session_date
market_cap
float
prior_close
premarket_open
premarket_high
open_reference_price
premarket_volume
premarket_gap_pct
premarket_gap_damage_pct
distance_open_to_premarket_resistance_pct
expected_push_pct_bucket
actual_push_pct_after_open
premarket_structure_type
strategy_state
review_bucket
```

## 7. Charts requeridos para notebook

### 7.1. Premarket structure chart

Debe mostrar:

- prior close;
- premarket open;
- premarket high;
- consolidacion o parabola;
- volumen premarket;
- damage del gap.

### 7.2. Open push chart

Debe mostrar:

- open;
- push de apertura;
- % desde open;
- volumen 1m;
- VWAP;
- EMA8/Wilder8 overlay.

### 7.3. Avoid chart

Debe mostrar:

- premarket weakness;
- gap que ya perdio 50%;
- precio de apertura lejos del nivel util.

## 8. Diferencia con eventos

Este documento es Strategy Library porque contiene decision long.

Eventos futuros derivados:

```text
Premarket_Active_Not_Overcrowded_Event
Premarket_Consolidation_Breakout_Event
Gap_Damage_Above_50_Avoid_Context
Opening_Push_After_Gap_Event
```

## 9. Imagenes deseadas del propio video

Solo se deben usar capturas de `4 - Gap Up Buying`.

Capturas deseadas:

```text
00:34-01:17  criterios market cap, float y volumen premarket
02:08-02:44  escenarios aceptables: consolidation breakout y parabolic
02:44-03:04  pullback/consolidation como riesgo
03:22-04:22  push esperado por float y micro float
05:36-06:39  escenario de premarket weakness a evitar
06:43-07:50  gap que pierde 50% de su ganancia y pasa a sesgo short
```

## 10. Regla final

Gap Up Buying no busca cualquier gap alcista.

Busca:

```text
gap con volumen premarket suficiente, float bajo y estructura viva,
antes de que el gap este demasiado crowded o ya destruido.
```
