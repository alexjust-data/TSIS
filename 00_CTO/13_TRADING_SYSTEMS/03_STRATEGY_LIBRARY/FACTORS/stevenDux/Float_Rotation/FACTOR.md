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

## 11. Regla final

Float Rotation no responde:

```text
compro o vendo?
```

Responde:

```text
el volumen actual esta renovando la base de holders, saturando el float,
eliminando bagholders o creando una zona crowded vulnerable?
```
