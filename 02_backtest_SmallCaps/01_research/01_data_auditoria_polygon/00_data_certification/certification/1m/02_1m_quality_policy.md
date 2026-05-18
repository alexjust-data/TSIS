# 1m | Quality Policy

La política de `1m` ya viene bastante clara desde el `closeout`.

## Buckets

- `good`
  - `RESCUE_SCHEMA_ONLY`
  - `vw_mild_low_ratio`
- `review`
  - `vw_moderate_ratio`
  - `vw_severe_tiny_base`
  - `vw_severe_small_mass`
- `bad`
  - `vw_severe_large_mass_diffuse`
  - `vw_severe_large_mass_persistent`
  - `QUARANTINE_PARSE_INVALID`
  - `QUARANTINE_PRICE_INVALID`

## Matiz importante

He comprobado que no hay contradicción material en que algunos casos lleven `schema` y aun así acaben en cuarentena.

La razón es simple:

- `schema` no manda si además aparece `parse_invalid` o `price_invalid`

Eso es coherente con el `hard_quarantine` real:

- `3,049` parse invalid
- `51` price invalid

## Taxonomía `vw` full-scope

Dentro de `RESCUE_SCHEMA_PLUS_VW`, la taxonomía refinada queda así:

- `vw_mild_low_ratio`: `274,639`
- `vw_moderate_ratio`: `119,875`
- `vw_severe_tiny_base`: `22,661`
- `vw_severe_small_mass`: `81,272`
- `vw_severe_large_mass_diffuse`: `192,575`
- `vw_severe_large_mass_persistent`: `372,954`

Esto respalda la semántica del `closeout`:

- lo leve entra en `good`
- lo intermedio en `review`
- lo grande y persistente sí queda en `bad`

## Salvedad de alcance

Estas cuentas son `full-scope`.

No deben presentarse como proporciones finales `<1B>` sin hacer el filtro explícito.
