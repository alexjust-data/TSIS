# Daily Adjusted Pilot Manifest `v0_1`

## Objetivo

Este documento fija el primer lote semantico de tickers para validar `daily_adjusted` antes de cualquier promocion mas amplia.

No es una muestra aleatoria.

Es una muestra deliberada para responder a una pregunta muy concreta:

- la cadena `split_normalized + dividend adjustment` se comporta correctamente cuando hay corporate actions reales, y permanece neutra cuando no los hay

## Regla de construccion

El piloto no debe formarse solo con tickers de `splits`.

Debe mezclar:

- casos de split real
- casos de reverse split
- casos con dividendos
- casos mixtos
- y controles sin eventos

Porque hay que validar dos cosas distintas:

1. que la capa ajustada actua cuando debe
2. que no inventa cambios donde no debe

## Lote piloto inicial

El manifest csv vive en:

- [daily_adjusted_pilot_manifest_v0_1.csv](../dataset_registry/daily/daily_adjusted_pilot_manifest_v0_1.csv)

Resultado posterior:

- este lote ya fue ejecutado como piloto real;
- sus resultados y limites quedaron registrados en:
  - [daily_adjusted_pilot_results_v0_1.md](./daily_adjusted_pilot_results_v0_1.md)

La version refinada actualmente recomendada del piloto es:

- [daily_adjusted_pilot_manifest_v0_2.csv](../dataset_registry/daily/daily_adjusted_pilot_manifest_v0_2.csv)

Composicion:

- `SGC`
  - `reverse_split_plus_dividends`
- `AAIC`
  - `reverse_split_plus_dividends`
- `ABEO`
  - `reverse_split_only`
- `SELF`
  - `dividends_only`
- `BBW`
  - `dividends_only`
- `ABIO`
  - `multi_reverse_split_plus_special_dividend`
- `ABVC`
  - `mixed_forward_reverse_split_plus_dividends`
- `AAME`
  - `dividends_only_controlled`
- `ABTX`
  - `dividends_only_controlled`
- `A`
  - `no_events_control`

## Por que esta composicion es buena

### Casos mixtos fuertes

- `SGC`
- `AAIC`
- `ABIO`
- `ABVC`

Sirven para comprobar que la cadena:

- no solo escribe columnas
- sino que compone correctamente varios eventos y no pierde trazabilidad

### Casos split-only

- `ABEO`

Sirve para comprobar que:

- el factor de split actua
- y el factor de dividendos se mantiene neutro

### Casos dividend-only

- `SELF`
- `BBW`
- `AAME`
- `ABTX`

Sirven para comprobar que:

- la capa no depende de splits para hacer algo util
- y que el ajuste por dividendos no contamina tickers sin necesidad de reescalar

### Caso control sin eventos

- `A`

Sirve para comprobar que:

- `future_split_factor = 1.0`
- `future_dividend_factor = 1.0`
- y que `*_adjusted` no diverge de `*_raw` salvo ruido numerico trivial

## Validaciones esperadas por subgrupo

### Reverse split

En:

- `SGC`
- `AAIC`
- `ABEO`
- `ABIO`

Debe observarse:

- `future_split_factor != 1.0` en historia anterior al evento

### Dividendos

En:

- `SGC`
- `AAIC`
- `SELF`
- `BBW`
- `ABIO`
- `ABVC`
- `AAME`
- `ABTX`

Debe observarse:

- `future_dividend_factor != 1.0` donde haya ex-dates futuras relevantes

### Control

En:

- `A`

Debe observarse:

- neutralidad completa de factores

## Para que sirve este piloto

Responde a:

- si la capa ajustada realmente funciona en casos no triviales
- si la provenance minima basta
- y si ya existe base suficiente para conectar el primer consumidor real

No responde todavia a:

- rendimiento full-universe
- coste operativo total
- o estabilidad de una corrida masiva de produccion

## Veredicto

Este lote es suficientemente rico para validar la semantica de `daily_adjusted`.

Si este piloto sale bien, el siguiente paso correcto es:

- conectar el primer consumidor real

no saltar directamente a una rematerializacion full-universe ciega.
