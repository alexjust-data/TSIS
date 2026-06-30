# Parabolic Breakout and Failed Breakout Strategy - Duxinator Source Draft v0.1

Fecha: 2026-06-27
Estado: source_note / strategy draft.
Fuente primaria: Steven Dux - Duxinator - `6 - Parabolic Breakout and Failed Breakout`.

## 1. Proposito

Este documento define la lectura inicial de TSIS para `Parabolic Breakout and
Failed Breakout` segun el material Duxinator.

La fuente contiene contexto long y short. Se coloca bajo `01_Steven_Dux/SHORT`
porque el uso practico principal descrito es distinguir cuando el breakout no
debe sostener y puede fallar.

## 2. Resumen tecnico

Dux separa dos fuerzas:

```text
buying pressure
short-cover pressure
```

Un breakout parabolico sostiene cuando ambas fuerzas coinciden:

```text
compradores nuevos
+ shorts cubriendo al romper su riesgo
= doble presion compradora
```

Un failed breakout aparece cuando el breakout genera cobertura temporal, pero el
volumen/liquidez no es suficiente para sostener el movimiento.

## 3. Contexto psicologico

La pregunta clave es:

```text
donde esta la mayoria de los shorts?
```

Si los shorts estan concentrados en una consolidacion y el nivel rompe, el
breakout puede forzar cobertura.

Si el volumen posterior no supera la liquidez/volumen del dia previo, el
movimiento puede ser solo un spike temporal.

## 4. Condiciones para breakout que sostiene

### 4.1. Consolidacion correcta

Dux menciona que una consolidacion util no debe ser demasiado amplia.

Fuente:

```text
consolidation range <= 20%-25% of entire gain
```

### 4.2. Volumen suficiente

Para que un breakout multi-day sostenga, la liquidez/volumen del segundo dia
debe superar o al menos competir con el primer green day.

```text
second_day_volume >= first_green_day_volume
```

### 4.3. Sin gap down de debilidad

Si el ticker gapea down, la fuente interpreta que pierde liquidez y que el
segundo dia probablemente no supere el volumen del primero.

## 5. Condiciones para failed breakout

### 5.1. Break temporal por cobertura

El breakout puede ocurrir porque los shorts cubren su riesgo.

### 5.2. Volumen insuficiente

Si el breakout tradea mucho menos volumen que el primer green day, puede no
sostener.

Ejemplo fuente:

```text
first_green_day_volume = 60M
breakout_volume = 10M
```

### 5.3. Spike sin nuevos compradores

Cuando los shorts ya cubrieron y no hay compradores suficientes, el precio puede
fade back down.

## 6. Formulas candidatas

### 6.1. Consolidation range as percent of gain

```text
consolidation_range_pct_of_gain =
  (consolidation_high - consolidation_low) /
  (run_high - run_start_price) * 100
```

### 6.2. Breakout volume sufficiency

```text
breakout_volume_ratio =
  breakout_volume / first_green_day_volume
```

### 6.3. Premarket volume projection

Fuente:

```text
premarket_volume * 10 = estimated_day_volume
```

```text
estimated_day_volume_ratio =
  estimated_day_volume / prior_day_volume
```

## 7. Estados candidatos

```text
parabolic_breakout_context
short_cover_pressure_zone
buying_pressure_confirmed
consolidation_range_acceptable
breakout_volume_sufficient
breakout_volume_insufficient
temporary_short_cover_spike
failed_breakout_candidate
breakout_hold_candidate
```

## 8. Campos minimos para candidate_table

```text
candidate_id
ticker
exchange
company_name
session_date
run_start_price
run_high
first_green_day_volume
prior_day_volume
premarket_volume
estimated_day_volume
estimated_day_volume_ratio
consolidation_high
consolidation_low
consolidation_range_pct_of_gain
breakout_ts
breakout_price
breakout_volume
breakout_volume_ratio
gap_down_flag
red_to_green_flag
strategy_state
review_bucket
```

## 9. Charts requeridos para notebook

### 9.1. Short concentration map

Debe mostrar:

- consolidacion donde se acumulan shorts;
- nivel de riesgo de shorts;
- breakout;
- zona donde cubren.

### 9.2. Breakout hold/fail chart

Debe mostrar:

- volumen de breakout;
- volumen del first green day;
- VWAP;
- EMA8/Wilder8;
- si el precio acepta o falla encima del nivel.

## 10. Diferencia con eventos

Este documento es Strategy Library porque interpreta una respuesta operativa
short/avoid/long-context.

Eventos futuros:

```text
Short_Cover_Pressure_Zone_Event
Parabolic_Breakout_Event
Breakout_Volume_Insufficiency_Event
Failed_Breakout_Event
Breakout_Hold_Context_Event
```

## 11. Imagenes deseadas del propio video

Solo se deben usar capturas de `6 - Parabolic Breakout and Failed Breakout`.

Capturas deseadas:

```text
00:32-01:36  buying pressure + short-cover pressure
01:41-02:33  localizar donde estan la mayoria de shorts
02:36-05:00  parabolic second green day y doble presion compradora
05:20-06:05  consolidacion correcta menor al 20%-25% del gain
06:20-08:33  breakout con volumen insuficiente vs first green day
08:34-09:20  failed breakout y mejor entrada short
```

## 12. Regla final

La pregunta correcta no es:

```text
rompio el nivel?
```

La pregunta correcta es:

```text
el breakout tiene suficiente volumen/liquidez para sostener despues de que los
shorts cubran, o solo fue un spike temporal por cobertura?
```
