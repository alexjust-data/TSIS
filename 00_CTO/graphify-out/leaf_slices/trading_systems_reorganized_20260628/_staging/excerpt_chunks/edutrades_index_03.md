## 13. First_Day_Runner_Frontside_Dip_Event

### Que ocurre

Durante el primer dia de un runner, el precio hace un pullback mientras la
tendencia sigue en frontside. El evento existe solo si el dip no rompe VWAP ni
la estructura alcista.

### Imagenes fuente

<img src="source_assets/edu_trades/009vwapbounce.png" width="760" alt="009 - Runner frontside con VWAP como referencia">

<img src="source_assets/edu_trades/013_gapandgo.png" width="760" alt="013 - Gap up, consolidacion y dip posterior al breakout">

### Texto del trader

El documento fuente usa lenguaje operativo de buying dips dentro del primer dia
de un runner, en el frontside de la tendencia, mientras VWAP actua como soporte.
En TSIS no copiamos la accion operativa; detectamos el dip que ocurre dentro de
una estructura alcista viva.

### Definicion observable v0

Unidad de busqueda:

```text
ticker_session
```

Secuencia minima:

```text
1. ticker esta en primer dia de momentum/runner
2. precio esta verde y por encima de VWAP
3. se forma pullback desde high local
4. VWAP o higher low sostiene la estructura
5. precio intenta recuperar desde el dip
```

Inicio conceptual:

```text
low del dip frontside
```

Fin conceptual:

```text
reclaim del micro high anterior o perdida de VWAP
```

### Busqueda historica v0

Features candidatas:

```text
first_runner_day_flag
day_gain_pct
pullback_depth_pct
pullback_low_to_vwap_pct
higher_low_flag
volume_on_pullback_ratio
reclaim_after_dip_flag
```

Thresholds semilla:

```text
day_gain_pct >= 10
pullback_depth_pct between 3 and 20
pullback_low >= vwap * 0.98
higher_low_flag = true
```

Excluir si:

```text
VWAP se pierde con volumen alto
pullback rompe low estructural
evento ocurre en backside
```

### Composicion observable no operativa

Puede aparecer como pieza observable dentro de:

- `Comprar dips en el primer dia del runner`;
- `VWAP Bounce`;
- `Gap and Go`.

### No es estrategia

No dice actuar sobre debilidad. Detecta un dip dentro de frontside vivo.

## 14. First_Green_Day_Bounce_Event

### Que ocurre

Tras una caida grande desde un runner, el ticker deja de destruirse y marca el
primer rebote verde. Debe haber caida previa suficiente y despues reversal con
volumen.

### Imagenes fuente

<img src="source_assets/edu_trades/011_primerdiaverde.png" width="760" alt="011 - Primer dia verde como base de rebote">

### Texto del trader

El documento distingue First Green Day Bounce: despues de una caida de 30-50%
de un runner, aparece el primer rebote verde tecnico. Debe mantener parte de
las ganancias previas y no tener catalizador negativo activo.

### Definicion observable v0

Unidad de busqueda:

```text
ticker_day
```

Secuencia minima:

```text
1. existe runner previo
2. precio cae 30-50% desde high del runner
3. no vuelve completamente a base inicial
4. aparece primer dia verde/reversal
5. volumen confirma rebote
```

Inicio conceptual:

```text
cierre del primer dia verde tras destruccion parcial
```

Fin conceptual:

```text
cierre de ese dia o siguiente confirmacion
```

### Busqueda historica v0

Features candidatas:

```text
runner_high
drawdown_from_runner_high_pct
retained_gain_pct
first_green_after_drawdown_flag
reversal_volume_ratio
close_location_pct
negative_catalyst_absent_flag
```

Thresholds semilla:

```text
drawdown_from_runner_high_pct between -30 and -60
retained_gain_pct > 0
daily_return_pct > 0
reversal_volume_ratio >= 1.5
```

Excluir si:

```text
caida fue causada por noticia negativa
ticker volvio completamente a base
rebote sin volumen
```

### Composicion observable no operativa

Puede aparecer como pieza observable dentro de:

- `First Green Day Bounce`;
- `Panic Bounce`;
- `Former Runner Reversal`.

### No es estrategia

No define swing ni overnight. Solo marca que el primer rebote verde existe.

## 15. Gap_And_Grab_Reversal_Event

### Que ocurre

El ticker abre rojo con gap bajo el cierre anterior, deja de caer, forma una V
o base y recupera niveles de resistencia con volumen. Es un reversal agresivo
que puede preceder a Red to Green.

### Imagenes fuente

<img src="source_assets/edu_trades/005_redtogreen.png" width="760" alt="005 - Apertura roja, soporte y recuperacion progresiva">

<img src="source_assets/edu_trades/006_redtogreen.png" width="760" alt="006 - Recuperacion con volumen superior al open">

### Texto del trader

El documento define Gap and Grab Reversal como una accion que abre roja, forma
una V y recupera resistencias. El volumen debe decrecer en la caida y aumentar
durante el pickup del reversal. El texto lo describe como arriesgado y
explosivo.

### Definicion observable v0

Unidad de busqueda:

```text
ticker_session
```

Secuencia minima:

```text
1. open < prior_close
2. precio cae o extiende rojo despues del open
3. se forma low y base/V
4. volumen bajista decrece
5. volumen comprador aparece en pickup
6. precio recupera resistencia local o prior_close/VWAP
```

Inicio conceptual:

```text
low de la V o primera vela de pickup
```

Fin conceptual:

```text
reclaim de resistencia o fallo bajo low reciente
```

### Busqueda historica v0

Features candidatas:

```text
gap_down_pct
v_low_ts
v_depth_pct
sell_volume_decay
pickup_volume_ratio
resistance_reclaim_flag
r2g_followthrough_flag
```

Thresholds semilla:

```text
gap_down_pct < 0
v_depth_pct <= -5
pickup_volume_ratio >= 1.5
resistance_reclaim_flag = true
```

Excluir si:

```text
no hay base/V
caida sigue acelerando
hay catalizador negativo
```

### Composicion observable no operativa

Puede aparecer como pieza observable dentro de:

- `Gap and Grab Reversal`;
- `Red to Green`;
- `VWAP Reclaim`;
- `Dip Buying Panic`.

### No es estrategia

No define anticipar reversal. Detecta que la V y el pickup ya son observables.

## 16. Gap_And_Go_Premarket_High_Breakout_Event

### Que ocurre

El ticker abre con gap/momentum, define un premarket high y durante la apertura
rompe ese nivel con volumen. El evento es la ruptura del PMH y continuacion
inicial, no la decision de perseguirla.

### Imagenes fuente

<img src="source_assets/edu_trades/013_gapandgo.png" width="760" alt="013 - Gap up, consolidacion, breakout y volumen">

### Texto del trader

El documento fuente define Gap and Go como el patron clasico de apertura en
momentum. Ocurre cuando la accion rompe el premarket high y continua al alza en
la apertura. Se recalca que solo aplica en primer dia de corrida y que puede
fallar en segundos si el breakout no es real.

### Definicion observable v0

Unidad de busqueda:

```text
ticker_session with premarket + regular open
```

Secuencia minima:

```text
1. gap up o green premarket
2. existe premarket_high definido
3. precio consolida o opera bajo PMH antes del open/early session
4. vela regular rompe PMH con volumen
5. precio sostiene al menos brevemente por encima
```

Inicio conceptual:

```text
primera vela regular que rompe/cierra sobre premarket_high
```

Fin conceptual:

```text
primer hold/retest o fallo bajo PMH
```

### Busqueda historica v0

Features candidatas:

```text
premarket_high
gap_pct
pm_volume
breakout_ts
breakout_volume_ratio
post_breakout_hold_minutes
fail_seconds_after_breakout
first_day_run_flag
```

Thresholds semilla:

```text
gap_pct > 0
pm_volume > threshold_config
breakout_close >= premarket_high * 1.001
breakout_volume_ratio >= 1.5
post_breakout_hold_minutes >= 3
```

Excluir si:

```text
no hay premarket data
breakout ocurre en afterhours, no open/regular
precio falla bajo PMH inmediatamente
evento es fase tardia despues de parabolic run
```

### Composicion observable no operativa

Puede aparecer como pieza observable dentro de:

- `Gap and Go`;
- `Opening Drive`;
- `Premarket High Breakout`;
- `First Day Runner`.

### No es estrategia

No define actuar sobre el PMH. Solo marca que el PMH fue roto con volumen durante la
apertura.

## 17. Filtros transversales de contexto

Estos no son eventos principales del menu. Son filtros o flags de contexto que
pueden acompanar la busqueda historica y degradar, revisar o excluir candidatos.

No deben tratarse como eventos por si solos.

### Catalyst_No_Dilution_Context_Filter

Uso:

```text
marcar si el evento tiene catalyst compatible y si existe riesgo de dilucion
que degrade la lectura del candidato
```

Campos futuros:

```text
catalyst_flag
catalyst_type
active_s3_flag
atm_or_424b_flag
warrant_risk_flag
no_dilution_context_state
```

### Event_Candidate_Failure_Risk_Filter

Uso:

```text
marcar candidatos como review/degraded/blocked si hay condiciones contrarias
```

Flags futuros:

```text
vwap_loss_with_volume
breakout_fakeout
overhead_resistance_too_close
repeated_failed_level
missing_volume_confirmation
negative_catalyst
```

### First_Day_Run_Context_Filter

Uso:

```text
limitar Gap and Go, Frontside Dip y First Green Day a fases tempranas del run
```

Campos futuros:

```text
run_day_index
days_since_first_volume_spike
prior_extension_pct
late_parabolic_risk_flag
```

## 18. Prioridad para futuras definiciones

Orden recomendado para convertir a draft formal:

1. `Red_To_Green_Level_Reclaim_Event`
2. `VWAP_Bounce_After_Extension_Event`
3. `VWAP_Reclaim_Control_Event`
4. `Gap_And_Go_Premarket_High_Breakout_Event`
5. `Daily_Resistance_Volume_Breakout_Event`
6. `First_Green_Day_High_Close_Event`
7. `Gap_And_Grab_Reversal_Event`
8. `Panic_Dip_Reversal_Event`

La prioridad favorece eventos que pueden buscarse con OHLCV 1m/daily antes de
depender de tape, filings o contexto fundamental.

## 19. Regla final

Este documento debe permitir que un agente futuro escriba una busqueda
historica preliminar en Python sin reinterpretar la idea desde cero.

Si una seccion no permite derivar:

```text
inputs
features
thresholds iniciales
inicio/fin del evento
exclusiones
```

entonces la seccion aun no esta lista para Event Research operativo.
