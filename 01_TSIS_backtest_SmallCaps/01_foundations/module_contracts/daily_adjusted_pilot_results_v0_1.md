# Daily Adjusted Pilot Results `v0_1`

## Rol

Este documento registra el resultado del primer piloto semantico de `daily_adjusted` y la razon por la que el lote original se refino a una version `v0_2`.

## Corrida ejecutada

Salida temporal usada:

- `C:\tmp\daily_adjusted_pilot_v0_1`

Tickers corridos:

- `SGC`
- `AAIC`
- `ABEO`
- `SELF`
- `BBW`
- `ABIO`
- `ABVC`
- `AAME`
- `ABTX`
- `A`

## Resultado resumido

### Casos que respondieron bien

- `A`
  - control correcto
  - sin cambios espurios
- `AAME`
  - dividendos activos
- `ABEO`
  - split activo, dividendos neutros
- `ABIO`
  - split y dividendos activos
- `ABTX`
  - dividendos activos
- `BBW`
  - dividendos activos
- `SELF`
  - dividendos activos
- `SGC`
  - split y dividendos activos

### Casos que no activaron la senal esperada

- `AAIC`
  - `split_non1_rows = 0`
  - `div_non1_rows = 0`
- `ABVC`
  - `split_non1_rows = 496`
  - `div_non1_rows = 0`

## Lectura critica

El problema de `AAIC` no fue del materializador.

El problema fue de seleccion semantica del piloto:

- el ticker tiene corporate actions en fuentes institucionales
- pero la ventana real disponible en `daily` no activa esos eventos en la capa materializada

Consecuencia:

- `AAIC` era un ticker correcto “sobre el papel”
- pero no un buen ticker para validar la activacion real de la cadena dentro del rango observado

`ABVC` fue mejor:

- si activo la cadena de split
- pero no la cadena de dividendos dentro del rango materializado

Consecuencia:

- sirve como caso split-heavy
- pero no como caso mixto fuerte

## Decision

El piloto `v0_1` fue util y correcto como exploracion.

Pero no debe tratarse como lote final recomendado.

La decision correcta es:

- conservar `v0_1` como memoria de aprendizaje
- y promover un lote refinado `v0_2`

## Reemplazos recomendados

Para casos mixtos `split + dividends` realmente activos en la ventana `daily`, se recomiendan:

- `CASS`
- `CVLY`

Ambos activan:

- `future_split_factor != 1.0`
- `future_dividend_factor != 1.0`

dentro del rango real materializado.

## Manifest recomendado a partir de ahora

La version recomendada del lote piloto pasa a ser:

- [daily_adjusted_pilot_manifest_v0_2.csv](../dataset_registry/daily/daily_adjusted_pilot_manifest_v0_2.csv)

## Veredicto final

El piloto `v0_1` fue un exito tecnico y un exito metodologico parcial.

Exito tecnico:

- el materializador funciona
- escribe bien
- y activa los factores correctamente en la mayoria de casos

Exito metodologico parcial:

- demostro que la seleccion del lote no debe depender solo de aparecer en `splits` o `dividends`
- tambien debe comprobarse que el evento cae dentro de la ventana real disponible de `daily`
