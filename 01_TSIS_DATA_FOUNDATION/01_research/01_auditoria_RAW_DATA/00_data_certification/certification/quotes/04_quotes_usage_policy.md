# Quotes Usage Policy

## Fuente canonica

La implicacion de `quotes` para uso operativo ya esta planteada en:

- `auditoria\quotes\v2\04_quotes_full_C_D_closeout.md`

## Regla minima

Hasta el cierre final de certificacion, la lectura util es esta:

- `good`
  - apto para el uso mas estricto
- `review`
  - uso condicionado y siempre identificado
- `bad`
  - fuera del uso core

## Backtest

Para `backtest` la lectura debe ser conservadora:

- baseline principal sobre `good`
- `review` solo para sensibilidad o analisis aparte

## ML / IA

Para `ML` o `IA`:

- `good` es la base limpia
- `review` solo tiene sentido si entra con flags de calidad
- `bad` no entra en el train principal

## Regla de esta carpeta

No cerrar aqui una politica mas fina de uso hasta que la certificacion global una `quotes` con el resto de capas.
