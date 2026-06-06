# Daily Adjusted Pilot Results `v0_2`

## Rol

Este documento registra el resultado del piloto semantico refinado de `daily_adjusted`.

Su trabajo es responder a una pregunta concreta:

- la capa ajustada activa de verdad donde hay eventos materiales en rango real `daily`, y permanece neutra donde no hay eventos

## Corrida ejecutada

Salida temporal usada:

- `C:\tmp\daily_adjusted_pilot_v0_2`

Tickers corridos:

- `SGC`
- `ABEO`
- `SELF`
- `BBW`
- `ABIO`
- `CASS`
- `CVLY`
- `AAME`
- `ABTX`
- `A`

## Resultado ticker por ticker

### `A`

- `split_non1_rows = 0`
- `div_non1_rows = 0`
- `adjusted_diff_rows = 0`

Lectura:

- control correcto
- no hay ajuste espurio
- la capa permanece neutra como debe

### `AAME`

- `split_non1_rows = 0`
- `div_non1_rows = 4721`

Lectura:

- caso `dividends_only` correcto
- la cadena de dividendos se activa de forma masiva
- la cadena de split permanece neutra

### `ABEO`

- `split_non1_rows = 1771`
- `div_non1_rows = 0`

Lectura:

- caso `reverse_split_only` correcto
- el factor de split actua
- la cadena de dividendos permanece neutra

### `ABIO`

- `split_non1_rows = 3925`
- `div_non1_rows = 3923`

Lectura:

- caso mixto duro correcto
- hay activacion muy fuerte de la cadena de split
- y tambien activacion de dividendo

### `ABTX`

- `split_non1_rows = 0`
- `div_non1_rows = 1735`

Lectura:

- caso `dividends_only_controlled` correcto

### `BBW`

- `split_non1_rows = 0`
- `div_non1_rows = 5327`

Lectura:

- caso `dividends_only` fuerte
- activacion completa de la cadena de dividendos sobre toda la historia materializada

### `CASS`

- `split_non1_rows = 3418`
- `div_non1_rows = 5237`

Lectura:

- caso mixto correcto
- reemplazo bueno para un candidato mixto mas debil
- la historia disponible activa ambas cadenas de forma clara

### `CVLY`

- `split_non1_rows = 3241`
- `div_non1_rows = 4382`

Lectura:

- caso mixto correcto
- split y dividendos activos en rango real

### `SELF`

- `split_non1_rows = 0`
- `div_non1_rows = 2548`

Lectura:

- caso `dividends_only` correcto

### `SGC`

- `split_non1_rows = 2412`
- `div_non1_rows = 5184`

Lectura:

- caso mixto correcto
- split y dividendos activos de forma clara

## Resumen cuantitativo

### Casos correctamente neutros

- `A`

### Casos split-only correctos

- `ABEO`

### Casos dividend-only correctos

- `AAME`
- `ABTX`
- `BBW`
- `SELF`

### Casos mixtos correctos

- `ABIO`
- `CASS`
- `CVLY`
- `SGC`

## Lectura institucional

El piloto `v0_2` ya no tiene el problema principal de `v0_1`.

Ahora la cesta:

- no solo aparece en las fuentes de corporate actions
- sino que activa realmente esas cadenas dentro de la ventana `daily` materializada

Eso significa que el piloto ya sirve para validar:

- la logica de split
- la logica de dividendos
- la composicion de ambas
- y la neutralidad del control sin eventos

## Veredicto final

El piloto semantico `v0_2` debe considerarse:

- **validado**

No es un full-universe.
No demuestra aun coste operacional masivo.

Pero si demuestra lo que necesitabamos demostrar en esta fase:

- que `daily_adjusted` actua cuando debe
- y no actua cuando no debe

## Consecuencia

La siguiente fase correcta ya no es seguir refinando el piloto.

La siguiente fase correcta es:

- conectar el primer consumidor real

El consumidor recomendado sigue siendo:

- labels diarios de retorno sobre `c_adjusted`
