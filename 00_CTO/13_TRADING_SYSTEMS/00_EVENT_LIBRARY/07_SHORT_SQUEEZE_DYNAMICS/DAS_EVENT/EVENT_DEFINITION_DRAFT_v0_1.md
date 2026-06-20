# DAS_Event

Fecha: 2026-06-20  
Estado: `draft_definition`  
Familia principal: `SHORT_SQUEEZE_DYNAMICS`  
Familia secundaria conceptual: `MOMENTUM_EXPANSION`  
Ruta: `00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/07_SHORT_SQUEEZE_DYNAMICS/DAS_EVENT/`  

Este documento define una primera version conceptual, didactica y revisable del evento:

```text
DAS_Event
```

`DAS` significa:

```text
Dips After Squeeze
```

No es una estrategia.
No es una entrada.
No es un detector productivo.
No es un backtest.
No es una prueba de edge.

Es una definicion inicial de un fenomeno observable que TSIS quiere estudiar:

```text
push/squeeze previo -> retroceso no destructivo -> reactivacion alcista
```

## Menu

- [1. Proposito](#1-proposito)
- [2. Nombre del evento](#2-nombre-del-evento)
- [3. Definicion corta](#3-definicion-corta)
- [4. Definicion didactica](#4-definicion-didactica)
- [5. Mecanica conductual propuesta](#5-mecanica-conductual-propuesta)
- [6. Fases del evento](#6-fases-del-evento)
- [7. Variantes principales](#7-variantes-principales)
- [8. DAS como evento recurrente](#8-das-como-evento-recurrente)
- [9. Timestamp oficial del evento](#9-timestamp-oficial-del-evento)
- [10. Condiciones observables minimas](#10-condiciones-observables-minimas)
- [11. Features candidatas](#11-features-candidatas)
- [12. Calidad y flags esperadas](#12-calidad-y-flags-esperadas)
- [13. Exclusiones](#13-exclusiones)
- [14. Ambiguedades abiertas](#14-ambiguedades-abiertas)
- [15. Review visual humana](#15-review-visual-humana)
- [16. Frontera con estrategia](#16-frontera-con-estrategia)
- [17. Estado actual](#17-estado-actual)
- [18. Proximos pasos recomendados](#18-proximos-pasos-recomendados)
- [19. Regla final](#19-regla-final)

---

## 1. Proposito

Este evento nace de una observacion discrecional sobre small caps en fase activa
de momentum/squeeze.

La secuencia humana observada es:

1. Una accion despierta con un primer push expansivo.
2. El movimiento atrae atencion y posiblemente presion sobre vendedores/shorts.
3. El precio retrocede.
4. Ese retroceso no destruye la estructura.
5. El precio se reactiva al alza.
6. La reactivacion puede forzar cobertura short o persecucion de momentum.

El objetivo de la definicion es capturar un fenomeno recurrente:

```text
despues de un squeeze, algunos dips no son fallo;
son puntos de reactivacion del squeeze.
```

TSIS debe estudiar este fenomeno como evento antes de convertirlo en estrategia.

## 2. Nombre del evento

Nombre preferido:

```text
DAS_Event
```

Nombre expandido:

```text
Dips_After_Squeeze_Event
```

Subtitulo descriptivo:

```text
Dips After Squeeze Reactivation Event
```

Descomposicion del nombre:

| Parte | Significado |
| --- | --- |
| `Dips` | Retrocesos posteriores a un movimiento expansivo. |
| `After` | El dip no aparece desde mercado muerto; aparece despues de squeeze/push. |
| `Squeeze` | Contexto de presion alcista, posible atrapamiento short y momentum. |
| `Event` | Fenomeno observable, no accion operativa. |

Decision provisional:

```text
Usar DAS_Event como nombre canonico corto.
```

## 3. Definicion corta

Evento donde una small cap en fase activa de squeeze o push expansivo hace un
retroceso no destructivo y posteriormente reactiva la subida, ya sea por rechazo
rapido del dip o por ruptura de una compresion/flag posterior.

La hipotesis mecanica es que parte de esa reactivacion puede venir de:

```text
shorts presionados
forced covering
momentum traders persiguiendo
feedback loop de precio-atencion-volumen
```

Esa hipotesis no se trata como hecho probado hasta que Outcome Research y datos
microestructurales la apoyen.

## 4. Definicion didactica

DAS no es simplemente un dip.

Un dip normal puede ser:

- agotamiento;
- pausa;
- pullback;
- fallo;
- ruido;
- toma de beneficios;
- inicio de reversa.

DAS requiere que el dip ocurra despues de un contexto especifico:

```text
push/squeeze previo
```

y que el retroceso no destruya la tesis de momentum.

La estructura conceptual es:

```text
1. squeeze_context
2. dip_attempt
3. structure_not_destroyed
4. bullish_reactivation
5. renewed_impulse_or_rebreak
```

La pregunta del evento es:

```text
El retroceso posterior al squeeze fue absorbido/rechazado y reactivo el
momentum?
```

No pregunta:

```text
Compro el dip?
Compro la vela que rompe?
Donde pongo stop?
Cuanto riesgo uso?
```

## 5. Mecanica conductual propuesta

La hipotesis humana inicial es:

```text
El squeeze/push inicial pone bajo presion a traders que estan short o que
intentan vender el movimiento. Cuando aparece el dip, algunos participantes
interpretan que el squeeze fallo. Si el dip no destruye estructura y el precio
se reactiva, esos shorts pueden quedar asustados o atrapados. Al cubrir,
contribuyen a acelerar el nuevo impulso.
```

Esta lectura pertenece a la capa de mecanismo, no a la capa de estrategia.

Debe documentarse como:

```yaml
behavioral_mechanics:
  status: human_hypothesis
  mechanism:
    - short_side_pressure
    - forced_covering_possible
    - momentum_feedback_loop
    - crowd_attention_reactivation
```

### 5.1. Participantes posibles

| Participante | Posible rol |
| --- | --- |
| Shorts tempranos | Pueden quedar en perdida tras el push inicial. |
| Shorts del dip | Pueden vender el retroceso pensando que el squeeze fallo. |
| Longs de momentum | Pueden perseguir la reactivacion. |
| Longs tempranos | Pueden defender estructura si el dip no destruye. |
| Sellers oportunistas | Pueden fallar si el mercado absorbe el retroceso. |
| Liquidity providers | Pueden retirar liquidez si aumenta la violencia del movimiento. |

### 5.2. Incentivo de teoria de juegos

El evento puede entenderse como un conflicto entre tesis:

```text
short thesis: el push fallo y el dip inicia reversa
long/momentum thesis: el dip fue absorbido y el squeeze continua
```

El nivel critico cambia cuando el precio:

- rechaza rapido el dip;
- recupera la zona de ruptura;
- rompe el high local anterior;
- imprime nuevo impulso con volumen.

En ese punto, los shorts pueden tener menos margen para esperar.

### 5.3. Alternativas plausibles

La hipotesis short-covering no debe asumirse como unica explicacion.

Alternativas:

- repricing por noticia;
- iliquidez extrema;
- momentum retail;
- continuacion mecanica por volumen;
- error o hueco de datos;
- spread demasiado ancho;
- baja calidad del ticker;
- rebote tecnico sin participacion short relevante.

## 6. Fases del evento

### 6.1. Fase A - `squeeze_context`

Fenomeno:

```text
El ticker ya esta activo y muestra expansion de precio/volumen.
```

Condiciones conceptuales:

- push previo visible;
- volumen superior al estado previo;
- rango expansivo;
- atencion creciente;
- el precio no esta en estado muerto;
- puede ocurrir en premarket o regular market.

Features candidatas:

```text
prior_push_pct
prior_push_duration_bars
prior_push_volume
prior_push_volume_ratio
prior_high
prior_push_start_ts
prior_push_end_ts
```

### 6.2. Fase B - `dip_attempt`

Fenomeno:

```text
El precio retrocede despues del squeeze/push.
```

El dip puede ser:

- inmediato;
- de una sola vela;
- dentro de una vela expansiva;
- de varias velas;
- en forma de flag/banderin.

El punto importante no es que dure mucho.
El punto importante es que no destruya la estructura.

Features candidatas:

```text
dip_start_ts
dip_low_ts
dip_depth_pct
dip_duration_bars
dip_volume
dip_speed
dip_low_relative_to_push
```

### 6.3. Fase C - `structure_not_destroyed`

Fenomeno:

```text
El retroceso no invalida el momentum previo.
```

Condiciones conceptuales:

- no devuelve todo el push;
- no pierde niveles estructurales relevantes;
- no convierte el movimiento en downtrend claro;
- no se seca completamente la atencion;
- el precio queda en posicion de poder reactivar.

Features candidatas:

```text
push_retained_pct
giveback_pct
held_above_key_level
held_above_vwap_if_relevant
dip_recovery_speed
```

### 6.4. Fase D - `bullish_reactivation`

Fenomeno:

```text
El precio rechaza el dip o rompe la compresion posterior.
```

Esta fase define el corazon del evento.

La reactivacion puede ser:

- vela con mecha inferior y cierre fuerte;
- recuperacion inmediata tras barrida;
- ruptura de flag;
- rebreak de high local;
- nuevo impulso con volumen.

Features candidatas:

```text
reactivation_start_ts
reactivation_type
reactivation_volume
reactivation_speed
lower_wick_pct
close_position_in_bar
rebreak_high
rebreak_volume_ratio
```

### 6.5. Fase E - `renewed_impulse`

Fenomeno:

```text
La reactivacion genera continuidad o nuevo impulso.
```

Esta fase puede medirse como outcome inicial del evento, no como requisito
operativo de entrada.

Features candidatas:

```text
post_reactivation_push_pct
post_reactivation_high_ts
time_to_new_high
continuation_bars
failure_after_reactivation
```

## 7. Variantes principales

### 7.1. `DAS_Wick_Reactivation`

La version ideal rapida.

Secuencia:

```text
squeeze/push inicial
-> retroceso inmediato
-> mecha inferior visible
-> recuperacion rapida
-> reactivacion vertical
```

Lectura:

El precio intenta retroceder, pero la demanda aparece de forma inmediata. El
dip queda rechazado dentro de una vela o en la vela siguiente.

Condiciones conceptuales:

- dip muy rapido;
- mecha inferior relevante;
- cierre fuerte;
- recuperacion de gran parte del rango;
- poca duracion del retroceso;
- verticalidad recuperada.

Campos esperados:

```text
das_variant = wick_reactivation
dip_duration_bars = 1 or 2
lower_wick_pct
close_position_in_bar
reactivation_speed
```

### 7.2. `DAS_Flag_Rebreak`

La version estructurada.

Secuencia:

```text
squeeze/push inicial
-> retroceso de varias velas
-> flag/banderin no destructivo
-> ruptura de la compresion
-> nuevo impulso
```

Lectura:

El precio no rechaza el dip de forma instantanea. Construye una microestructura
de pausa o compresion y posteriormente rompe.

Condiciones conceptuales:

- retroceso controlado;
- compresion o flag;
- highs/lows relativamente ordenados;
- no destruccion del push;
- rebreak de la parte alta de la estructura;
- volumen o velocidad en la rotura.

Campos esperados:

```text
das_variant = flag_rebreak
flag_duration_bars
flag_high
flag_low
flag_slope
flag_range_pct
rebreak_ts
rebreak_push_pct
```

## 8. DAS como evento recurrente

DAS puede ocurrir varias veces en una misma secuencia de squeeze.

Ejemplo conceptual:

```text
push inicial
-> DAS #1
-> nuevo impulso
-> DAS #2
-> nuevo impulso
-> DAS #3
```

Por tanto, cada instancia debe tener un indice ordinal:

```text
das_sequence_index:
  1
  2
  3
  ...
```

Tambien debe registrarse:

```text
sequence_maturity:
  early
  mid
  late
```

La hipotesis humana inicial es que DAS posteriores pueden tener peor calidad
estructural que el primer DAS.

Pero esta idea no pertenece a la regla de evento como sizing ni como accion.

Debe pasar a Outcome Research como pregunta:

```text
Como cambia la continuacion, fallo, volatilidad y riesgo segun
das_sequence_index?
```

## 9. Timestamp oficial del evento

El `event_start_ts` depende de la variante.

### 9.1. Para `DAS_Wick_Reactivation`

Timestamp preferido:

```text
primera vela que muestra rechazo claro del dip y recuperacion alcista
```

Campos relacionados:

```text
dip_start_ts
dip_low_ts
reactivation_start_ts
event_start_ts
```

### 9.2. Para `DAS_Flag_Rebreak`

Timestamp preferido:

```text
primera vela que rompe la parte alta del flag/banderin
```

Campos relacionados:

```text
flag_start_ts
flag_end_ts
rebreak_ts
event_start_ts
```

Regla:

```text
event_start_ts marca la reactivacion observable, no la entrada operativa.
```

## 10. Condiciones observables minimas

Una primera version de contrato podria exigir:

```yaml
event_name: DAS_Event
family: SHORT_SQUEEZE_DYNAMICS
secondary_family: MOMENTUM_EXPANSION
status: draft_definition

observable_conditions:
  required:
    - prior_squeeze_or_push_present
    - dip_after_push_present
    - dip_is_not_destructive
    - bullish_reactivation_present

  variant_required:
    wick_reactivation:
      - lower_wick_or_fast_rejection_present
      - recovery_within_short_window
    flag_rebreak:
      - flag_or_compression_present
      - rebreak_of_flag_high_present

  optional:
    - volume_expansion_on_reactivation
    - prior_high_rebreak
    - tape_shift_if_available
    - spread_acceptable_if_available
    - news_or_catalyst_context
    - halt_context
```

## 11. Features candidatas

### 11.1. Identidad y tiempo

```text
ticker
tradingview_symbol
primary_exchange
event_date
session_segment
event_start_ts
event_end_ts
das_sequence_index
sequence_maturity
das_variant
```

### 11.2. Contexto de squeeze/push

```text
prior_push_start_ts
prior_push_end_ts
prior_push_low
prior_push_high
prior_push_pct
prior_push_duration_bars
prior_push_volume
prior_push_volume_ratio
prior_high_before_dip
```

### 11.3. Dip

```text
dip_start_ts
dip_low_ts
dip_end_ts
dip_depth_pct
dip_duration_bars
dip_speed
dip_volume
giveback_pct
push_retained_pct
```

### 11.4. Reactivacion

```text
reactivation_start_ts
reactivation_high_ts
reactivation_push_pct
reactivation_volume
reactivation_volume_ratio
reactivation_speed
rebreak_high
rebreak_ts
```

### 11.5. Wick variant

```text
lower_wick_pct
upper_wick_pct
close_position_in_bar
bar_recovery_pct
same_bar_reactivation
next_bar_reactivation
```

### 11.6. Flag variant

```text
flag_start_ts
flag_end_ts
flag_duration_bars
flag_high
flag_low
flag_range_pct
flag_slope
flag_break_ts
flag_break_volume_ratio
```

### 11.7. Mecanica conductual

```text
behavioral_mechanism_status
short_pressure_hypothesis
forced_covering_hypothesis
momentum_feedback_hypothesis
alternative_explanation_flags
```

## 12. Calidad y flags esperadas

Estados de calidad:

```text
good_candidate
review_candidate
degraded_candidate
blocked_candidate
invalid_candidate
```

Flags conceptuales:

| Flag | Significado |
| --- | --- |
| `prior_push_clear` | El push/squeeze previo es visible y medible. |
| `dip_clear` | El retroceso posterior esta claramente identificado. |
| `dip_non_destructive` | El dip no invalida la estructura previa. |
| `reactivation_clear` | La recuperacion alcista es clara. |
| `wick_reactivation_clear` | Hay rechazo rapido con mecha/recuperacion. |
| `flag_rebreak_clear` | Hay flag/banderin y rotura clara. |
| `sequence_index_clear` | Puede distinguirse si es DAS #1, #2, etc. |
| `behavioral_mechanism_hypothesis_only` | El mecanismo short/crowd aun no esta probado. |
| `manual_review_required` | El caso necesita revision visual humana. |
| `spread_or_liquidity_concern` | Spread/liquidez podria distorsionar lectura. |
| `halt_overlap` | Existe halt cerca de la secuencia. |
| `data_gap_concern` | Hay huecos de data que afectan la lectura. |

Regla:

```text
Si no hay push/squeeze previo, no es DAS.
```

Otra regla:

```text
Si el dip destruye por completo la estructura previa, no es good_candidate.
```

## 13. Exclusiones

No deberian clasificarse como DAS:

1. Dip aislado sin squeeze/push previo.
2. Pullback normal en tendencia lenta sin expansion previa.
3. Spike que falla y no reactiva.
4. Retroceso que devuelve completamente el push.
5. Rotura bajista o inicio claro de backside.
6. Movimiento con data incompleta que impide ver el push previo.
7. Movimiento causado por split/corporate action o error de datos.
8. Caso donde la unica razon para llamarlo DAS sea una entrada humana.

## 14. Ambiguedades abiertas

### 14.1. Que cuenta como squeeze/push previo?

Pendiente definir:

```text
prior_push_pct minimo
prior_push_volume minimo
prior_push_duration_bars
```

### 14.2. Cuanto puede retroceder el dip?

Pendiente definir:

```text
max_giveback_pct
min_push_retained_pct
key_level_policy
```

### 14.3. Cuando un wick es suficiente?

Pendiente definir:

```text
lower_wick_pct minimo
close_position_in_bar minima
recovery_time maximo
```

### 14.4. Cuando una flag es real?

Pendiente definir:

```text
flag_duration_bars minimo/maximo
flag_range_pct maximo
flag_slope permitido
break_threshold
```

### 14.5. Como separar DAS de simple continuation?

Pregunta:

```text
Si el precio apenas retrocede y continua, es DAS o continuation?
```

Decision provisional:

```text
DAS requiere intento visible de dip o compresion.
```

### 14.6. Como probar la hipotesis short-covering?

La presion short no siempre es observable directamente.

Proxies posibles:

- SSR;
- short volume context si esta gobernado;
- tape/agresion si existe dato adecuado;
- velocidad de rebreak;
- volumen de reactivacion;
- fallo rapido de vendedores;
- outcomes de aceleracion posterior.

## 15. Review visual humana

Para revisar un candidato, el humano debe mirar:

1. Hubo squeeze/push previo claro?
2. El retroceso aparece despues del push?
3. El dip destruye o preserva la estructura?
4. La reactivacion es rapida o estructurada?
5. Es wick reactivation o flag rebreak?
6. Hay nuevo impulso o rebreak local?
7. El volumen acompana la reactivacion?
8. Hay indicios de shorts atrapados o solo es una narracion?
9. Hay problemas de spread, liquidez, halt o data?
10. Estamos metiendo una entrada de estrategia dentro del evento?

Checklist visual:

```text
[ ] prior squeeze/push visible
[ ] dip appears after push
[ ] dip does not fully destroy prior push
[ ] bullish reactivation visible
[ ] variant classified
[ ] sequence index assigned
[ ] volume reviewed
[ ] behavioral mechanism marked as hypothesis
[ ] no entry rule included
[ ] no stop rule included
[ ] no target rule included
[ ] no sizing rule included
```

## 16. Frontera con estrategia

Este documento puede decir:

```text
El dip fue rechazado.
El precio reactivo.
El high local se rompio.
El evento podria presionar shorts.
```

No puede decir:

```text
comprar el dip
comprar la vela de rotura
poner stop bajo la mecha
arriesgar menos en DAS #2
mantener core position
salir en X porcentaje
```

Estas frases pertenecen a Strategy Library, Execution Models o Decision Models.

Regla:

```text
El evento describe la reactivacion.
La estrategia decide si actuar sobre ella.
```

## 17. Estado actual

Estado del evento:

```text
draft_definition
```

No puede pasar aun a `detector_candidate` porque faltan:

- thresholds iniciales;
- ejemplos visuales buenos/malos;
- politica de variantes;
- reglas para `das_sequence_index`;
- definicion cuantitativa de dip no destructivo;
- definicion cuantitativa de wick reactivation;
- definicion cuantitativa de flag rebreak;
- tests exploratorios en `01_research/04_event_discovery`;
- validacion de false positives.

## 18. Proximos pasos recomendados

1. Reunir ejemplos visuales de DAS claros y dudosos.
2. Separar `wick_reactivation` de `flag_rebreak`.
3. Marcar `DAS #1`, `DAS #2`, `DAS #3` en cada secuencia.
4. Definir thresholds iniciales para:
   - `prior_push_pct`;
   - `dip_depth_pct`;
   - `push_retained_pct`;
   - `reactivation_speed`;
   - `flag_duration_bars`;
   - `lower_wick_pct`.
5. Crear busqueda exploratoria en `01_research/04_event_discovery`.
6. Revisar candidatos con chart interactivo.
7. Medir outcomes por variante y por `das_sequence_index`.
8. Solo despues considerar estrategias.

## 19. Regla final

DAS existe para capturar esta estructura:

```text
el precio hizo squeeze,
retrocedio sin destruir la estructura,
y reactivo el momentum.
```

La hipotesis es que esa reactivacion puede estar alimentada por:

```text
shorts presionados
forced covering
persecucion de momentum
feedback loop de masas
```

Pero mientras no incluya entrada, stop, target, sizing ni instruccion de
ejecucion, sigue siendo un evento.

Si empieza a decir que hacer frente a esa estructura, deja de pertenecer a
Event Library.
