# Liquidity Gain Loss Factor - Duxinator Advance Concepts Draft v0.1

Fecha: 2026-06-27
Estado: source_note / factor draft.
Fuente primaria:

```text
Steven Dux - Duxinator - 4 - Advance Concepts
4 - The Gain _ Loss of Liquidity
5 - Volume Range and Liquidity Collaboration
```

## 1. Proposito

Este documento define como TSIS debe leer la idea Dux de `gain/loss of
liquidity`.

No es una estrategia direccional.
No valida edge.
No autoriza operativa.

Es un factor que ajusta la prediccion de volumen segun lo que hace el chart
despues de abrir:

```text
el ticker esta ganando liquidez/equity,
perdiendo liquidez/equity,
o entrando en un estado crowded donde el rango esperado cambia?
```

## 2. Relacion con Volume Prediction

`Volume_Prediction` calcula una expectativa base:

```text
premarket_volume * 10
first_hour_volume * 4
```

`Liquidity_Gain_Loss` corrige esa expectativa mirando la accion del precio:

```text
consolidacion que aguanta -> puede ganar volumen
parabolico/uptrend -> puede ganar volumen
morning panic -> puede perder volumen
consolidation breakdown -> puede perder volumen
crowded heavy volume -> cambia el rango de bounce/retest
```

Regla:

```text
La prediccion de volumen no es estatica.
Debe actualizarse segun el comportamiento intradia.
```

## 3. Definicion operativa

### 3.1. Gaining liquidity / gaining equity

El ticker gana liquidez cuando mantiene interes y participacion.

Formas fuente:

```text
flat consolidation with volume
uptrend
parabolic spike
consolidation that holds gains
```

Lectura:

```text
si el precio no se destruye y sigue atrayendo compradores/vendedores,
el volumen final puede superar la prediccion base.
```

Estado:

```text
gaining_liquidity
```

### 3.2. Losing liquidity / losing equity

El ticker pierde liquidez cuando el chart destruye interes y reduce la
participacion esperada.

Formas fuente:

```text
morning panic
large opening dump
consolidation breakdown
failed holding range
```

Lectura:

```text
si el precio cae fuerte o rompe una consolidacion, muchos participantes se van
y el volumen final puede caer cerca de la mitad de la prediccion base.
```

Estado:

```text
losing_liquidity
```

## 4. Escenarios principales

### 4.1. Consolidation holding gains

El precio queda plano o en rango, pero no devuelve la subida.

Lectura fuente:

```text
people like to buy consolidations because the stock is not dropping.
```

Interpretacion TSIS:

```text
holding consolidation = liquidity retention / possible liquidity gain.
```

Estado:

```text
holding_consolidation_gaining_liquidity
```

### 4.2. Parabolic/uptrend

El precio acelera al alza.

Lectura:

```text
el movimiento atrae compradores, vendedores, shorts y chasers.
```

Estado:

```text
parabolic_gaining_liquidity
```

### 4.3. Morning panic

El ticker cae fuerte justo despues del open.

Lectura fuente:

```text
morning panic can reduce intraday volume by roughly half.
```

Formula candidata:

```text
adjusted_estimated_day_volume =
  base_estimated_day_volume * 0.5
```

Estado:

```text
morning_panic_losing_liquidity
```

### 4.4. Consolidation breakdown

El precio consolida durante un tramo y luego rompe a la baja.

Lectura:

```text
muchos participantes compraron/vendieron dentro del rango;
cuando el rango crackea, todos quieren vender primero.
```

Formula candidata:

```text
adjusted_estimated_day_volume =
  base_estimated_day_volume * 0.5
```

Estado:

```text
consolidation_breakdown_losing_liquidity
```

### 4.5. Gap through resistance is not a breakout

Dux distingue entre:

```text
gap through resistance
real breakout through resistance
```

Un gap que aparece por encima de una resistencia no negocia volumen en medio del
nivel.

Lectura TSIS:

```text
si no hubo volumen negociado atravesando el nivel, la resistencia no queda
automaticamente neutralizada.
```

Estado:

```text
gap_through_resistance_without_volume
```

## 5. Formula base y ajustes

### 5.1. Base estimate

```text
base_estimated_day_volume =
  max(
    premarket_volume * 10,
    first_hour_volume * 4
  )
```

### 5.2. Gaining liquidity adjustment

Fuente conceptual:

```text
premarket_volume = 1M
base estimate = 10M
if stock holds/spikes/consolidates, final volume may be 10M-15M
```

Formula candidata:

```text
adjusted_estimated_day_volume =
  base_estimated_day_volume * liquidity_gain_multiplier
```

Valores iniciales para research:

```text
liquidity_gain_multiplier = 1.0 to 1.5
```

### 5.3. Losing liquidity adjustment

Fuente conceptual:

```text
morning panic or consolidation crack can cut volume expectation roughly in half.
```

Formula candidata:

```text
adjusted_estimated_day_volume =
  base_estimated_day_volume * liquidity_loss_multiplier
```

Valor inicial para research:

```text
liquidity_loss_multiplier = 0.5
```

### 5.4. Final adjusted estimate

```text
liquidity_adjusted_day_volume =
  base_estimated_day_volume * state_multiplier
```

Donde:

```text
state_multiplier =
  1.0-1.5 if gaining_liquidity
  0.5     if losing_liquidity
  1.0     if neutral/unknown
```

Estos multiplicadores son etiquetas fuente para investigacion, no parametros
institucionales finales.

## 6. Volume range and liquidity collaboration

El transcript 5 conecta volumen total esperado con rango de rebote/fallo.

Buckets fuente:

| Expected day volume | Lectura fuente | Estado TSIS |
|---|---|---|
| `~10M` | light volume | `light_volume_range` |
| `~20M` | decent volume | `decent_volume_range` |
| `~30M` | decent / a little crowded | `crowded_leaning_volume_range` |
| `>=40M` | super crowded, often not tradable | `super_crowded_volume_range` |

Regla:

```text
El rango esperado de bounce/retest cambia con el volumen.
```

Lectura:

- volumen ligero: drops tienden a tener bounce mas pequeno;
- volumen pesado: drops pueden tener bounce mas grande;
- volumen super crowded: el rango puede alcanzar zonas de riesgo mas amplias.

## 7. Bounce range implications

Dux usa la relacion:

```text
harder drop + heavier volume -> larger bounce range
lighter volume -> lighter bounce range
```

Para TSIS esto no debe convertirse inmediatamente en entry/stop.

Debe convertirse en features:

```text
drop_pct_from_high
expected_bounce_range_pct
observed_bounce_pct
volume_bucket_at_drop
crowded_range_risk
```

## 8. Resistance comparison after liquidity adjustment

El volumen que debe compararse contra resistencia historica no debe ser solo la
prediccion base.

Debe ser:

```text
liquidity_adjusted_day_volume
```

Formula:

```text
adjusted_current_vs_resistance_volume_ratio =
  liquidity_adjusted_day_volume / resistance_volume
```

Lectura:

```text
si el ticker pierde liquidez, una resistencia historica puede volver a dominar;
si gana liquidez, esa resistencia puede ser neutralizada.
```

## 9. Estados del factor

```text
liquidity_state_unknown
holding_consolidation_gaining_liquidity
parabolic_gaining_liquidity
morning_panic_losing_liquidity
consolidation_breakdown_losing_liquidity
gap_through_resistance_without_volume
real_breakout_volume_confirmed
light_volume_range
decent_volume_range
crowded_leaning_volume_range
super_crowded_volume_range
microfloat_rotation_degrades_liquidity_read
```

## 10. Campos minimos para factor_table

```text
factor_id
ticker
exchange
company_name
session_date
strategy_context
market_cap
float
premarket_volume
first_hour_volume
base_estimated_day_volume
liquidity_state
liquidity_state_start_ts
liquidity_state_reason
state_multiplier
liquidity_adjusted_day_volume
estimated_float_rotation
resistance_volume
adjusted_current_vs_resistance_volume_ratio
volume_bucket
drop_pct_from_high
expected_bounce_range_pct
observed_bounce_pct
gap_through_resistance_flag
real_breakout_volume_confirmed
review_required
```

## 11. Chart requirements

Un notebook que use este factor debe mostrar:

- premarket volume;
- first hour volume;
- base estimated day volume;
- liquidity-adjusted estimate;
- estado de liquidez;
- zona donde se detecta morning panic o consolidation breakdown;
- si el precio gapeo por encima de resistencia sin negociar volumen en medio;
- comparacion contra resistencia historica cuando aplique;
- bucket de volumen esperado.

## 12. Aplicacion por estrategia

### 12.1. Gap Up Short

Usar para:

- esperar push si el premarket volume sugiere morning spike;
- reducir expectativa de volumen despues de panic;
- decidir si una resistencia todavia puede atraer precio tras gap through.

### 12.2. Bounce Short

Usar para:

- recalcular si el volumen actual puede competir con la resistencia historica;
- detectar cuando un crack hace que la resistencia vuelva a dominar;
- distinguir retest con volumen sano vs retest sin capacidad.

### 12.3. First Red Day

Usar para:

- detectar perdida de liquidez despues de la fase parabolica;
- ajustar expectativa de volumen si el ticker ya rompio estructura;
- comparar volumen actual contra dias previos.

### 12.4. DAS / long momentum

Usar para:

- no confundir consolidacion que gana liquidez con fallo;
- distinguir primer crack que destruye liquidez;
- medir si el frontside sigue vivo o pierde participacion.

## 13. Imagenes deseadas del propio video

No se deben insertar imagenes de otros videos.

Capturas deseadas:

```text
4 - The Gain _ Loss of Liquidity:
00:00-00:40  escenarios consolidation/uptrend/morning panic
00:58-01:25  morning panic reduces liquidity
01:25-02:15  consolidation breakdown reduces expected volume
03:15-04:25  gap through resistance is not real breakout
05:00-06:45  float rotation degrades resistance/volume logic
07:20-09:00  gaining equity vs losing equity diagrams
10:15-12:30  resistance ratio and bounce short example

5 - Volume Range and Liquidity Collaboration:
00:00-01:15  volume buckets 10M/20M/30M/40M+
01:15-02:40  heavier volume changes bounce range
02:40-04:00  crowded volume and wider risk range
```

## 14. Regla final

La prediccion de volumen no debe quedarse congelada al open.

Debe actualizarse con el estado del chart:

```text
si el ticker aguanta y consolida, puede ganar liquidez;
si paniquea o rompe consolidacion, puede perder liquidez;
si el volumen es demasiado crowded, el rango esperado cambia.
```

Si un notebook no ajusta la prediccion de volumen por `liquidity_state`, no esta
modelando correctamente este bloque de `Advance Concepts`.
