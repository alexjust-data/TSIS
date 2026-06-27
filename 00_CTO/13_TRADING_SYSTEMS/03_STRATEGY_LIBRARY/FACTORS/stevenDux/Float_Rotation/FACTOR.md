# Float Rotation Factor - Duxinator Source Draft v0.1

Fecha: 2026-06-27
Estado: source_note / factor draft.
Fuente primaria: Steven Dux - Duxinator - `9 - Introduction to Float Rotation`.

## 1. Proposito

Este documento define la lectura inicial de TSIS para `Float Rotation` segun el
material Duxinator.

No es una estrategia direccional por si misma.

Es un factor transversal que modifica:

```text
long setups
short setups
avoid decisions
volume projection
crowding interpretation
```

## 2. Definicion

Float rotation mide cuantas veces el volumen negociado equivale al float.

```text
float_rotation = traded_volume / float
```

Ejemplo fuente:

```text
float = 3M
traded_volume = 20M
float_rotation ~= 6.7x
```

## 3. Lectura conductual

Cuando el float rota:

- compradores antiguos salen;
- compradores nuevos entran mas arriba;
- vendedores nuevos aparecen mas arriba;
- la base de holders cambia;
- la presion long/short cambia.

Dux lo usa para distinguir volumen sano, volumen insuficiente y volumen
demasiado crowded.

## 4. Buckets fuente

### 4.1. 0x-1x rotation

Si no rota el float:

```text
good for shorting
```

Segun fuente, especialmente si el setup short necesita que no entren nuevos
compradores suficientes.

### 4.2. 3x-5x rotation

Fuente:

```text
best bet for long first green day
```

Para longs, puede indicar suficiente renovacion de compradores.

### 4.3. 10x-15x rotation

Fuente:

```text
very crowded rotation
look for afternoon action / buyer insufficiency
```

Funciona mejor como contexto de consolidacion y posible fallo, no como
parabolico sin estructura.

### 4.4. 20x+ rotation

Fuente:

```text
avoid if not in consolidation zone
avoid parabolic extremes
```

## 5. Aplicacion a shorts

Para `Bounce Short` y `Bounce Plus Gap`, Dux no quiere ver float rotation fuerte
en low floats.

Motivo:

```text
si el float es 1M y entran 5M shares,
pueden absorber a los bagholders y aun quedar demanda para romper resistencia.
```

Estados:

```text
short_rotation_absent_good
short_rotation_present_danger
low_float_rotation_squeeze_risk
```

## 6. Aplicacion a longs

Para longs en first green day o premarket breakout, Dux busca:

```text
market cap aprox 50M-200M
float <= 10M
good catalyst
no resistance
no consistent resistance
no warrants
3x-5x float rotation
```

## 7. Aplicacion a buyer insufficiency

En 10x-15x rotation, si el ticker consolida en un rango estrecho, mucha gente
queda intercambiando acciones al mismo precio.

Cuando el rango crackea:

```text
todos quieren vender primero
```

Esto puede generar panic/chain reaction.

## 8. Formulas candidatas

### 8.1. Observed rotation

```text
observed_float_rotation =
  session_volume_to_time / float
```

### 8.2. Estimated day rotation from premarket

```text
estimated_day_volume =
  premarket_volume * 10

estimated_float_rotation =
  estimated_day_volume / float
```

### 8.3. Estimated day rotation from first hour

Para premarket breakout, Dux prefiere usar la primera hora:

```text
estimated_day_volume =
  first_hour_volume * 4

estimated_float_rotation =
  estimated_day_volume / float
```

### 8.4. Consolidation range tightness

```text
consolidation_range_pct =
  (consolidation_high - consolidation_low) /
  consolidation_mid * 100
```

Fuente:

```text
10%-15% range preferred for buyer insufficiency context
```

## 9. Campos minimos para factor_table

```text
factor_id
ticker
exchange
company_name
session_date
float
premarket_volume
first_hour_volume
session_volume_to_time
estimated_day_volume_from_premarket
estimated_day_volume_from_first_hour
observed_float_rotation
estimated_float_rotation
rotation_bucket
market_cap
catalyst_flag
warrants_flag
resistance_above_flag
consolidation_zone_flag
consolidation_range_pct
factor_state
review_bucket
```

## 10. Imagenes deseadas del propio video

Solo se deben usar capturas de `9 - Introduction to Float Rotation`.

Capturas deseadas:

```text
00:31-01:35  definicion de float rotation
02:30-03:07  premarket volume * 10 y ejemplo 20M/3M
03:44-05:30  buckets 3x-5x, 10x-15x, 20x+
06:13-08:34  por que float rotation arruina bounce short en low float
08:40-10:00  bounce plus gap con premarket rotation peligrosa
10:17-13:36  uso long de 3x-5x con catalyst/no resistance/no warrants
13:55-18:06  10x-15x consolidation y buyer insufficiency
```

## 11. Advance Concepts: The Danger of Float Rotation

Fuente primaria adicional:

```text
Steven Dux - Duxinator - Advance Concepts
9 - The Danger of Float Rotation
```

Esta ampliacion documenta un riesgo especifico: interpretar una zona de
consolidacion como resistencia fuerte sin ajustar por float.

La idea fuente es:

```text
no todo el volumen negociado en una zona crea la misma cantidad de bagholders
si el float es pequeno y rota muchas veces.
```

### 11.1. Caso high float / resistencia mas fiable

Si el float es grande y el volumen negociado en una zona es comparable al
float, la lectura de resistencia puede ser mas directa.

Ejemplo conceptual:

```text
float = 20M
volume_in_consolidation = 20M
future_retest_volume = 5M
```

Lectura:

```text
5M shares de demanda futura pueden no ser suficientes para absorber
20M shares de resistencia potencial.
```

En este caso, una estrategia tipo bounce short o resistance retest puede tener
mas sentido estructural, siempre que el resto de condiciones lo permita.

### 11.2. Caso microfloat / resistencia degradada por rotacion

Si el float es muy pequeno y la zona negocia muchas veces el float, la
conclusion cambia.

Ejemplo conceptual:

```text
float = 1M
volume_in_consolidation = 20M
```

Aunque se hayan negociado 20M shares, no significa que existan 20M shares
distintas atrapadas en ese nivel.

La razon mecanica es:

```text
si el float real disponible es 1M, las shares pueden estar cambiando de manos
una y otra vez.
```

Por tanto, el maximo bloque de holders simultaneos atrapados en ese nivel puede
estar mas cerca del float que del volumen total negociado.

Lectura fuente:

```text
el siguiente spike no necesita absorber 20M shares;
puede necesitar absorber solo una fraccion limitada por el float.
```

Despues de absorber esa presion, el resto del volumen puede volver a
reintercambiarse y alimentar otro spike.

### 11.3. Regla conductual

La resistencia individual pierde fiabilidad cuando:

```text
float muy bajo
+ volumen extremo en consolidacion
+ multiples rotaciones del float
+ nuevo spike con capacidad de absorber el float completo
```

En ese contexto, shortear una consolidacion aleatoria de microfloat puede ser
peligroso, porque la zona aparentemente crowded puede no contener tanta oferta
efectiva como parece.

### 11.4. Variables candidatas

```text
float
resistance_zone_volume
resistance_zone_dollar_volume
resistance_volume_to_float
future_retest_volume
future_retest_volume_to_float
estimated_bagholder_capacity
effective_resistance_volume
rotation_danger_ratio
retest_absorption_ratio
individual_resistance_degraded_by_rotation
random_consolidation_short_danger
```

### 11.5. Formulas exploratorias

Estas formulas no son institucionales. Son una primera forma de convertir la
idea en variables medibles para notebooks.

```text
resistance_volume_to_float =
  resistance_zone_volume / float
```

```text
estimated_bagholder_capacity =
  min(resistance_zone_volume, float)
```

```text
effective_resistance_volume =
  min(resistance_zone_volume, float)
```

```text
retest_absorption_ratio =
  future_retest_volume / effective_resistance_volume
```

```text
rotation_danger_ratio =
  resistance_zone_volume / float
```

Interpretacion inicial:

```text
high rotation_danger_ratio
+ low float
= resistance may be less reliable than raw traded volume implies
```

### 11.6. Estados candidatos

```text
resistance_volume_supported
microfloat_resistance_degraded
individual_resistance_unreliable
random_consolidation_short_danger
float_rotation_breakthrough_risk
reexchange_spike_risk
```

### 11.7. Implicacion para Strategy Library

Este factor puede degradar:

```text
Bounce Short
Double Layer Resistance
Gap Up Short
random consolidation short
```

especialmente cuando el ticker tiene microfloat y volumen suficiente para rotar
el float multiples veces.

No convierte el evento en long.
No prohibe todos los shorts.

Solo dice:

```text
la resistencia historica o intradia debe ajustarse por float rotation antes de
tratarla como oferta real.
```

### 11.8. Imagenes deseadas del propio video

Solo se deben usar capturas de `9 - The Danger of Float Rotation`.

Capturas deseadas:

```text
00:00-01:00  introduccion a la psicologia del float rotation danger
01:00-02:00  ejemplo high float: 20M float / 20M consolidation volume
02:00-03:00  ejemplo microfloat: 1M float / 20M consolidation volume
03:00-04:00  por que solo 1M holders pueden quedar en ese nivel
04:00-05:00  advertencia contra random consolidation shorts en microfloat
```

## 12. Regla final

Float Rotation no responde:

```text
compro o vendo?
```

Responde:

```text
el volumen actual esta renovando la base de holders, saturando el float,
eliminando bagholders o creando una zona crowded vulnerable?
```
