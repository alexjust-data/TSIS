El 50% responde a:

¿Cuándo el scanner captura un ticker interesante?

Pero el breakout/rebreak responde a:

¿Cuándo la estrategia DAS entra realmente en juego?

Son dos niveles distintos.

En CJMB no se marca ese breakout temprano porque el script actual solo conoce estas fases:

scanner gate
first push high
first dip low
rebreak confirmed

No tiene todavía una fase explícita llamada:

initial_breakout_confirmed

o:

strategy_inplay_gate

Por eso la vela grande con volumen máximo puede ser obvia para ti como humano, pero el sistema no la etiqueta como “breakout”:
para el sistema ahora mismo esa vela pertenece al first push, no al rebreak.

Cómo Lo Plantearía En Los Docs

En C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/research_design.md añadiría una sección nueva:

## Scanner Gate Vs Strategy In-Play Gate

Este experimento separa dos preguntas:

1. Scanner gate:
    ¿cuándo un ticker queda capturado por el scanner como candidato observable?

2. Strategy in-play gate:
    ¿cuándo aparece una estructura DAS suficientemente clara para considerar
    que la estrategia entra en juego?

El scanner no valida la estrategia.
El scanner solo crea el denominador poblacional.

La estrategia DAS no empieza en el +50%.
La estrategia empieza cuando aparece una estructura de breakout/rebreak
observable, validable y auditable.

Luego definiría fases:

DAS Phase 0 - scanner_gate
Ticker capturado por market cap, precio, volumen y movimiento mínimo.

DAS Phase 1 - initial_breakout_attempt
Primera expansión/breakout visible después del despertar.

DAS Phase 2 - initial_breakout_confirmed
Breakout con confirmación de volumen/cierre/cuerpo/continuidad.

DAS Phase 3 - first_push_high
Máximo estructural del primer push.

DAS Phase 4 - first_dip_low
Primer pullback real después del push.

DAS Phase 5 - rebreak_attempt
Intento de romper de nuevo el nivel estructural.

DAS Phase 6 - fake_rebreak
Rompe por mecha o sin volumen/cierre suficiente.

DAS Phase 7 - rebreak_confirmed
Breakout/rebreak confirmado; aquí la estrategia puede pasar a in-play.

En C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/execution_protocol.md lo bajaría a datos:

Por cada ticker capturado por el scanner se debe construir una tabla de fases:

candidate_id
ticker
session_date
phase_type
phase_ts_utc
phase_price
reference_level
bars_from_scanner
bars_from_push_start
bars_from_dip
volume
prior_volume_avg
volume_ratio
green_candle
close_above_level
high_above_level
body_pct
wick_rejection
vwap_relation
ema_wilder_regime
phase_status
visual_label_id
state_snapshot_role

Y las reglas de volumen no las fijaría como verdad única. Las pondría como sweep:

volume_confirmation_rule:
- volume > mean(previous 3 bars)
- volume > mean(previous 5 bars)
- volume > median(previous 5 bars)
- volume > max(pullback volume)
- volume > dip candle volume
- volume_ratio >= 1.5
- volume_ratio >= 2.0

Así AlphaEvolve/humano no “adivinan” la regla correcta: la investigan.

Orden Que Seguiría

1. Actualizar research_design.md con esta separación:
    scanner gate vs strategy in-play gate.

2. Actualizar execution_protocol.md con la tabla de fases DAS.
3. Crear extractor de fases:
    no solo candidate_events, sino das_phase_events.

4. Generar PNGs con todas las fases:
    scanner, initial breakout, first push high, dip, fake rebreak, confirmed rebreak.

5. Ejecutar sobre los ~4800 tickers del scanner.
6. Medir estadísticas por fase:
    qué pasa si entra en scanner pero no rompe,
    qué pasa si rompe sin volumen,
    qué pasa si rompe con volumen,
    qué pasa si hay fake rebreak,
    qué pasa si confirma.

7. Solo después conectar tablas de estado:
    scanner_gate_state, initial_breakout_state, first_dip_state, rebreak_attempt_state, rebreak_confirmed_state.

Esta es la ruta correcta: primero convertir DAS en una secuencia auditable de fases, luego medir qué fase tiene valor real.