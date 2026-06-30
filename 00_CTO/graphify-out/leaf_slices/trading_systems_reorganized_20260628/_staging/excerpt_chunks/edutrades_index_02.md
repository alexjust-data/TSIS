## 8. Red_Base_Volume_Ramp_Event

### Que ocurre

Antes del Red to Green, el precio deja de caer, construye una base en rojo y el
volumen comprador empieza a aumentar. Es la transicion entre venta inicial y
reclaim.

### Imagenes fuente

<img src="source_assets/edu_trades/005_redtogreen.png" width="760" alt="005 - Base roja, soporte clave y volumen creciente">

<img src="source_assets/edu_trades/006_redtogreen.png" width="760" alt="006 - Reclaim intradia con volumen">

<img src="source_assets/edu_trades/007_reftogreen.png" width="760" alt="007 - Reversal intradia con expansion posterior">

### Texto del trader

El documento advierte que no se debe anticipar el reversal mientras el precio
sigue cayendo. Debe existir base, soporte y recuperacion con volumen. Las
imagenes muestran perdida progresiva de presion vendedora, soporte en nivel
clave y aumento de volumen durante la recuperacion.

### Definicion observable v0

Unidad de busqueda:

```text
intraday_window antes de Red_To_Green_Level_Reclaim_Event
```

Secuencia minima:

```text
1. open red o selloff inicial
2. se forma un low intradia
3. varios lows posteriores no rompen ese low de forma material
4. el volumen bajista deja de expandirse
5. aparece rampa de volumen comprador hacia prior_close o VWAP
```

Inicio conceptual:

```text
low inicial de la base roja
```

Fin conceptual:

```text
primera recuperacion relevante hacia prior_close o VWAP
```

### Busqueda historica v0

Features candidatas:

```text
base_low
base_duration_minutes
lower_low_count_after_base
sell_volume_decay_ratio
green_volume_ramp_ratio
distance_to_prior_close_pct
distance_to_vwap_pct
```

Thresholds semilla:

```text
base_duration_minutes >= 10
lower_low_count_after_base <= 1
green_volume_ramp_ratio >= 1.5
```

Excluir si:

```text
precio sigue haciendo lower lows con volumen creciente
no hay intento de reclaim
spread o liquidez impiden lectura
```

### Composicion observable no operativa

Puede aparecer como pieza observable dentro de:

- `Red to Green`;
- `Gap and Grab Reversal`;
- `VWAP Reclaim`;
- `Dip Buying Panics`.

### No es estrategia

No dice actuar sobre la base. Describe que la venta inicial dejo de dominar y el
precio comenzo una recuperacion medible.

## 9. VWAP_Bounce_After_Extension_Event

### Que ocurre

Una accion verde y extendida retrocede hacia VWAP. En vez de perderlo con
volumen, VWAP actua como soporte y el precio rebota.

### Imagenes fuente

<img src="source_assets/edu_trades/008_vwapbpunce.png" width="760" alt="008 - VWAP coincide con soporte diario y rebote">

<img src="source_assets/edu_trades/009vwapbounce.png" width="760" alt="009 - Tendencia frontside y VWAP como zona de soporte">

### Texto del trader

El documento fuente describe VWAP Bounce como un pullback hacia VWAP dentro de
una accion verde y sobreextendida. El rebote debe venir despues de que VWAP
funcione como soporte, idealmente con vela verde y volumen creciente.

### Definicion observable v0

Unidad de busqueda:

```text
ticker_session intraday
```

Secuencia minima:

```text
1. accion verde en el dia
2. high se aleja de VWAP
3. precio retrocede hacia VWAP
4. low toca o se aproxima a VWAP
5. cierra por encima o recupera VWAP
6. aparece rebote posterior
```

Inicio conceptual:

```text
primera vela que toca o aproxima VWAP despues de extension
```

Fin conceptual:

```text
vela de recuperacion o perdida confirmada de VWAP
```

### Busqueda historica v0

Features candidatas:

```text
day_gain_pct
high_to_vwap_distance_pct
pullback_low_to_vwap_pct
vwap_hold_close_flag
bounce_volume_ratio
post_bounce_5m_return
lower_high_failure_flag
```

Thresholds semilla:

```text
day_gain_pct > 0
high_to_vwap_distance_pct >= 10
abs(pullback_low_to_vwap_pct) <= 2
vwap_hold_close_flag = true
```

Excluir si:

```text
VWAP no tuvo tiempo de estabilizarse
precio rompe VWAP con volumen bajista alto
accion esta roja en el dia
```

### Composicion observable no operativa

Puede aparecer como pieza observable dentro de:

- `VWAP Bounce`;
- `First_Day_Runner_Frontside_Dip_Event`;
- `Gap and Go Pullback`.

### No es estrategia

No define actuar sobre VWAP. Marca que VWAP funciono como soporte observable tras
extension.

## 10. VWAP_Reclaim_Control_Event

### Que ocurre

El precio pierde VWAP, deja de aceptar precios por debajo y lo recupera con una
vela o secuencia de volumen superior. El evento es el cambio de VWAP de
resistencia a zona de control comprador.

### Imagenes fuente

<img src="source_assets/edu_trades/010_vwapreclaim.png" width="760" alt="010 - Recuperacion de VWAP con incremento de volumen">

### Texto del trader

El documento fuente define VWAP Reclaim como recuperacion de VWAP con volumen.
La barra de reclaim debe tener mas volumen que las anteriores del retroceso. Si
la accion esta roja en el dia, la lectura long deja de ser valida para este
play.

### Definicion observable v0

Unidad de busqueda:

```text
intraday_window
```

Secuencia minima:

```text
1. precio opera por debajo de VWAP
2. se estabiliza o reduce pendiente bajista
3. vela cierra por encima de VWAP
4. volumen de reclaim > volumen de barras previas del retroceso
5. al menos una vela posterior no destruye VWAP inmediatamente
```

Inicio conceptual:

```text
vela que cierra sobre VWAP despues de estar debajo
```

Fin conceptual:

```text
confirmacion de hold sobre VWAP o perdida inmediata
```

### Busqueda historica v0

Features candidatas:

```text
below_vwap_duration
reclaim_ts
reclaim_close_above_vwap_pct
reclaim_volume_vs_pullback_max
post_reclaim_hold_minutes
day_color_at_reclaim
prior_close_relation
```

Thresholds semilla:

```text
below_vwap_duration >= 5 minutes
reclaim_close_above_vwap_pct > 0
reclaim_volume_vs_pullback_max >= 1.0
post_reclaim_hold_minutes >= 3
```

Excluir si:

```text
accion sigue roja y no recupera prior_close
reclaim es solo wick
overhead resistance inmediata bloquea el movimiento
```

### Composicion observable no operativa

Puede aparecer como pieza observable dentro de:

- `VWAP Reclaim`;
- `Red to Green`;
- `Gap and Grab Reversal`.

### No es estrategia

No define accion sobre el dip posterior. Solo detecta recuperacion de VWAP y
aceptacion inicial.

## 11. Panic_Dip_Reversal_Event

### Que ocurre

El precio cae de forma violenta en pocos minutos, deja de acelerar a la baja y
aparece una vela/secuencia de reversa con volumen comprador. El evento busca el
cambio de flujo tras panico, no la caida en si.

### Imagenes fuente

No hay imagen dedicada de panic dip en `source_assets/edu_trades/`. Este evento
queda como candidato textual hasta incorporar ejemplos visuales.

### Texto del trader

El documento describe Dip Buying Panics como caidas de 15-20% en pocos minutos
sin catalizador negativo. Advierte que no debe tratarse la caida libre como
evento completo; debe
aparecer confirmacion de reversa con volumen comprador.

### Definicion observable v0

Unidad de busqueda:

```text
intraday_window
```

Secuencia minima:

```text
1. drop rapido desde high/local high
2. drop_pct supera umbral en pocos minutos
3. aparece desaceleracion de nuevos lows
4. vela verde o reclaim local con volumen comprador
5. el low de panico no se rompe inmediatamente
```

Inicio conceptual:

```text
low de panico o primera vela de reversa tras el low
```

Fin conceptual:

```text
confirmacion de rebound o ruptura del low de panico
```

### Busqueda historica v0

Features candidatas:

```text
drop_pct
drop_duration_minutes
panic_low
reversal_volume_ratio
green_reversal_close_location
no_negative_news_flag
post_reversal_5m_return
```

Thresholds semilla:

```text
drop_pct <= -15
drop_duration_minutes <= 20
reversal_volume_ratio >= 1.5
panic_low_not_breached_next_3_bars = true
```

Excluir si:

```text
hay financing/delisting/bad news
spread extremo
no hay reversal candle
```

### Composicion observable no operativa

Puede aparecer como pieza observable dentro de:

- `Dip Buying Panics`;
- `Gap and Grab Reversal`;
- `First Green Day Bounce`.

### No es estrategia

No dice actuar sobre panicos. Detecta una reversa medible despues de panico.

## 12. First_Green_Day_High_Close_Event

### Que ocurre

Despues de una fase previa de debilidad o dormancia, aparece un dia verde con
volumen excepcional y cierre cerca del maximo del dia. El evento es diario, no
intradía puro.

### Imagenes fuente

<img src="source_assets/edu_trades/011_primerdiaverde.png" width="760" alt="011 - Primer dia verde con volumen historico">

<img src="source_assets/edu_trades/012_primerdiaverde.png" width="760" alt="012 - Close cerca del HOD y sobre VWAP">

### Texto del trader

El documento fuente define First Green Day como un patron donde la accion hace
un breakout de volumen historico y cierra fuerte. Las imagenes remarcan:
volumen historico, cierre cerca del HOD y precio sobre VWAP.

### Definicion observable v0

Unidad de busqueda:

```text
ticker_day
```

Secuencia minima:

```text
1. periodo previo sin momentum o con caida
2. dia actual cierra verde
3. volumen actual es historicamente alto
4. cierre queda cerca del high del dia
5. intradia no pierde VWAP de forma destructiva
```

Inicio conceptual:

```text
session close del primer dia verde
```

Fin conceptual:

```text
cierre de sesion regular / afterhours context si existe
```

### Busqueda historica v0

Features candidatas:

```text
daily_return_pct
volume_rank_60d
float_rotation_proxy
close_location_pct
close_above_vwap_flag
prior_down_or_dormant_days
next_premarket_gap_pct
```

Thresholds semilla:

```text
daily_return_pct > 0
volume_rank_60d >= 95th percentile
close_location_pct >= 0.75
prior_down_or_dormant_days >= 3
```

Excluir si:

```text
close lejos del HOD
volumen no es anomalo
dia verde aparece despues de extension parabolica tardia
```

### Composicion observable no operativa

Puede aparecer como pieza observable dentro de:

- `First Green Day`;
- `Multi-Day Runner`;
- `First Green Day Bounce`.

### No es estrategia

No define mantener overnight. Solo identifica el primer dia verde fuerte.

