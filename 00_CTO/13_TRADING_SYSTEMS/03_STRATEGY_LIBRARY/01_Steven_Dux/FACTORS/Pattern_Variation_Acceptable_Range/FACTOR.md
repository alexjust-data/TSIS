# Pattern Variation Acceptable Range Factor - Duxinator Source Draft v0.1

Fecha: 2026-06-27
Estado: source_note / factor draft.
Fuente primaria: Steven Dux - Duxinator - `10 - Pattern Variation and its Acceptable Range`.

## 1. Proposito

Este documento define como TSIS debe leer la idea de `pattern variation` segun
la fuente Duxinator.

No es una estrategia direccional por si misma.

Es un factor de control que responde:

```text
Esta variacion del patron sigue siendo aceptable, o el contexto de volumen,
float, SSR y resistencia historica la vuelve estadisticamente debil?
```

La utilidad principal es evitar que un notebook clasifique dos graficos como el
mismo setup solo porque ambos rompen un nivel.

La pregunta correcta es:

```text
La ruptura esta soportada por suficiente volumen real y liquidez actual, o es
solo un spike temporal producido por cobertura de shorts?
```

## 2. Idea central

Dux separa dos familias de ruptura:

```text
thin / same-volume breakout
heavy-volume supported breakout
```

Ambas pueden verse visualmente como un breakout.

Pero no significan lo mismo.

La diferencia esta en si el volumen del dia actual tiene capacidad de superar la
presion historica del nivel que se esta rompiendo.

## 3. Unidad semantica

Este factor no etiqueta una entrada.

Etiqueta la calidad contextual de una ruptura o variacion de patron.

Puede aplicarse a:

- multi-day breakout;
- gap-up buying;
- low-float breakout;
- SSR squeeze;
- second-day breakout;
- first green day continuation;
- failed breakout short;
- avoid decision.

## 4. Variables minimas

### 4.1. prior_resistance_price

Nivel historico contra el que el precio esta intentando romper.

Puede venir de:

- high del primer green day;
- high de un dia previo de gran volumen;
- multi-day resistance;
- consolidation high;
- whole/half dollar level si coincide con resistencia visible.

### 4.2. prior_resistance_volume

Volumen negociado durante la sesion o tramo que construyo la resistencia.

Ejemplo fuente:

```text
prior_resistance_volume = 20M shares
```

Lectura:

```text
Ese volumen representa la cantidad aproximada de participacion historica que
puede actuar como supply, trapped longs, sellers o referencia de presion.
```

### 4.3. breakout_volume_to_time

Volumen del dia actual acumulado hasta el momento de la ruptura.

Ejemplo fuente:

```text
breakout_volume_to_time = 5M shares
```

Si rompe una resistencia creada con 20M shares usando solo 5M shares, la ruptura
puede ser visualmente fuerte pero estructuralmente debil.

### 4.4. projected_day_volume

Estimacion simple del volumen final del dia usando el ritmo actual.

Formula inicial:

```text
projected_day_volume =
    cumulative_volume_to_time / elapsed_regular_session_fraction
```

Ejemplo:

```text
elapsed_regular_session_fraction = 2h / 6.5h
cumulative_volume_to_time = 15M
projected_day_volume ~= 48.75M
```

Si `projected_day_volume` supera claramente `prior_resistance_volume`, la
ruptura tiene mas soporte estadistico que una ruptura con bajo volumen.

### 4.5. breakout_volume_ratio

```text
breakout_volume_ratio =
    breakout_volume_to_time / prior_resistance_volume
```

Interpretacion inicial:

```text
< 0.50  thin breakout / bajo soporte
0.50-1.00 comparable but not dominant
> 1.00  volume-supported breakout
```

Estos rangos no son institucionales. Son punto de partida para notebooks y
estadistica.

### 4.6. projected_volume_ratio

```text
projected_volume_ratio =
    projected_day_volume / prior_resistance_volume
```

Este ratio ayuda a distinguir:

```text
ruptura temprana con volumen bajo
ruptura temprana con ritmo de volumen suficiente para superar la resistencia
```

## 5. Thin / same-volume breakout

Nombre provisional:

```text
Thin_Volume_Breakout_Context
```

Definicion:

Ruptura de un nivel historico donde el volumen actual usado para romper es
materialmente inferior al volumen que creo la resistencia.

Forma conceptual:

```text
prior resistance volume alto
-> breakout actual con volumen menor
-> spike temporal posible
-> baja probabilidad de retencion si no entra volumen nuevo
```

Lectura Dux:

Cuando un micro/low float rompe una resistencia con poco volumen, puede hacerlo
porque el float es estrecho, porque hay SSR, o porque los shorts estan cubriendo.
Pero esa ruptura no necesariamente implica que existan compradores nuevos
suficientes para sostener el movimiento.

## 6. Caso SSR + micro float

La fuente insiste en que SSR cambia la mecanica.

Contexto:

```text
overextended gap down
-> SSR probable
-> shorts no pueden golpear bid con la misma libertad
-> green-to-red shorts quedan expuestos
-> push manipulado o squeeze puede romper resistencia con poco volumen
```

Problema:

La ruptura puede parecer fuerte porque el precio sube rapido.

Pero la causa puede ser:

```text
short covering
```

no:

```text
real buyer-supported accumulation
```

Por eso el factor debe separar:

```text
covering-driven breakout
buyer-supported breakout
```

## 7. Heavy-volume supported breakout

Nombre provisional:

```text
Heavy_Volume_Supported_Breakout_Context
```

Definicion:

Ruptura de resistencia donde el volumen acumulado actual, o su proyeccion al
cierre, supera de forma razonable el volumen historico que creo la resistencia.

Forma conceptual:

```text
first green day volume alto
-> pullback / consolidation
-> regreso a resistencia
-> el precio no cae
-> acumula liquidez cerca del nivel
-> projected_day_volume > prior_resistance_volume
-> breakout con soporte real
```

Lectura Dux:

Si en las primeras horas ya hay suficiente volumen para proyectar que el dia
superara el volumen de la resistencia previa, el breakout es mas predecible y
puede tener mejor rango aceptable.

## 8. Acceptable range

La variacion de patron es aceptable si la mecanica principal sigue intacta.

Para un breakout, la mecanica principal no es solo:

```text
price > resistance
```

Tambien debe existir:

```text
current participation >= historical resistance pressure
```

o al menos una razon explicita para aceptar una excepcion.

## 9. Estados del factor

### 9.1. volume_unsupported_breakout

Condiciones conceptuales:

- precio rompe resistencia;
- `breakout_volume_ratio` bajo;
- `projected_volume_ratio` bajo o incierto;
- no hay acumulacion suficiente cerca del nivel.

Lectura:

```text
breakout visualmente presente, pero fuera del rango aceptable para long limpio.
```

Uso posterior:

- avoid long chase;
- posible failed breakout study;
- revisar si el spike fue short covering.

### 9.2. ssr_covering_breakout

Condiciones conceptuales:

- SSR activo o probable;
- micro/low float;
- ruptura ocurre con volumen inferior al nivel historico;
- movimiento rapido compatible con short covering.

Lectura:

```text
ruptura posible, pero no debe tratarse como buyer-supported breakout.
```

### 9.3. volume_supported_breakout

Condiciones conceptuales:

- volumen actual alto;
- `projected_volume_ratio > 1`;
- precio consolida cerca de resistencia sin fallar;
- ruptura ocurre con participacion creciente.

Lectura:

```text
breakout dentro del rango aceptable.
```

### 9.4. wait_for_resolution

Condiciones conceptuales:

- el precio rompe, pero el volumen/contexto no permite clasificar;
- shorts pueden seguir cubriendo;
- compradores reales no estan claros;
- no hay edge estadistico aun.

Lectura:

```text
esperar al cierre o al siguiente dia antes de clasificar como continuation,
failure o multi-day top.
```

## 10. Candidate-table fields

Un notebook que aplique este factor deberia producir como minimo:

```text
ticker
session_date
strategy_context
float
float_bucket
is_micro_float
is_low_float
is_ssr_active_or_probable
prior_resistance_price
prior_resistance_date
prior_resistance_volume
breakout_ts
breakout_price
breakout_volume_to_time
breakout_volume_ratio
cumulative_volume_to_time
elapsed_regular_session_fraction
projected_day_volume
projected_volume_ratio
volume_support_state
breakout_acceptance_state
classification
manual_review_required
```

## 11. Formulas iniciales

```text
breakout_volume_ratio =
    breakout_volume_to_time / prior_resistance_volume

projected_day_volume =
    cumulative_volume_to_time / elapsed_regular_session_fraction

projected_volume_ratio =
    projected_day_volume / prior_resistance_volume

float_rotation_to_breakout =
    breakout_volume_to_time / float

projected_float_rotation =
    projected_day_volume / float
```

## 12. Relacion con Float Rotation

Este factor debe conectarse con:

```text
01_Steven_Dux/FACTORS/Float_Rotation/FACTOR.md
```

Porque una ruptura de bajo volumen en micro float puede desplazar precio con
poco volumen, pero eso no significa que haya suficiente soporte para mantener
el movimiento.

La pregunta conjunta es:

```text
Cuanto del float ha rotado, y ese volumen es suficiente frente a la resistencia
historica que se esta rompiendo?
```

## 13. Relacion con estrategias futuras

Este factor puede modificar:

- Gap Up Buying;
- Dip Buying Multi-Day Runner;
- Parabolic Breakout;
- Failed Breakout;
- Double Layer Resistance;
- First Red Day;
- Multi-Day Top.

Ejemplos:

```text
Gap Up Buying + volume_supported_breakout
-> long candidate con mejor soporte

Gap Up Buying + ssr_covering_breakout
-> evitar chase o marcar como review

Failed Breakout + volume_unsupported_breakout
-> short/fade research candidate

Multi-Day Top + projected_volume_ratio decreciente
-> posible agotamiento de continuation
```

## 14. Chart requirements

### 14.1. Daily chart

Debe mostrar:

- resistance day;
- resistance price;
- prior resistance volume;
- current day volume;
- projected day volume;
- float rotation;
- SSR marker si aplica.

### 14.2. Intraday chart

Debe mostrar:

- cumulative volume curve;
- resistance price line;
- breakout timestamp;
- breakout volume to time;
- projected volume at breakout;
- VWAP;
- EMA8/Wilder8 overlay si la estrategia usa 1m.

### 14.3. Review labels

Etiquetas necesarias:

```text
prior resistance volume = X
breakout volume to time = Y
breakout volume ratio = Y / X
projected day volume = Z
projected volume ratio = Z / X
classification = volume_supported | unsupported | ssr_covering | wait
```

## 15. Estadistica requerida

Para validar este factor, TSIS debe estudiar outcomes por bucket:

```text
breakout_volume_ratio_bucket
projected_volume_ratio_bucket
float_bucket
SSR state
day_index
gap_state
first_green_day_volume_bucket
```

Outcomes minimos:

```text
hold_above_resistance_30m
hold_above_resistance_close
max_favorable_excursion_after_break
max_adverse_excursion_after_break
panic_to_support_same_day
next_day_gap_direction
first_red_day_probability
```

## 16. Imagenes deseadas del propio video

No se deben insertar imagenes de otros videos.

Capturas utiles de este video:

```text
00:24 - 01:44  introduccion de same/thin-volume breakout como factor
01:45 - 04:27  ejemplo de low-float/SSR breakout con poco volumen
04:27 - 06:16  comparacion volumen breakout menor que volumen historico
07:08 - 09:07  heavy-volume breakout soportado por volumen proyectado
```

Cuando existan capturas propias, deben insertarse aqui y enlazarse con las
variables anteriores.

## 17. Regla final

Un breakout no es aceptable solo porque el precio haya roto.

En este factor, el rango aceptable depende de:

```text
volumen actual
volumen historico del nivel
proyeccion de volumen
float
SSR
calidad de acumulacion cerca de resistencia
```

El notebook no debe limitarse a encontrar rupturas.

Debe clasificar si la ruptura esta soportada por participacion suficiente o si
solo parece un breakout por mecanica de micro float / short covering.
