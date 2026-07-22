# Quotes Certification Contract

## Uso de estos terminos

En `quotes`, estos terminos no se vuelven a definir desde cero.
Se usan como capa de ensamblado sobre lo ya fijado en `auditoria`.

## `expected`

Para `quotes`, `expected` no esta cerrado todavia como artefacto final.
Solo debe usarse con prudencia para la futura certificacion global.

Regla minima:

- no asumir que todo `ticker x day` entre `2005` y `2026` era exigible
- no generar faltantes sinteticamente sin antes fijar el expected set global

## `present`

`present` significa presencia observada en la materializacion auditada:

- `quotes_current_cd_merged\quotes_current.parquet`

Aqui no hay interpretacion de calidad.
Solo presencia.

## `healthy`

En `quotes`, la salud local ya esta resuelta en `auditoria\quotes\v2`.

La politica vigente es:

- `good`
- `review`
- `bad`

Y su lectura debe respetar el `closeout` y el `crosswalk`, no reescribirse aqui.

## `usable`

La usabilidad no se cerrara aqui con una taxonomia nueva.
Se apoyara en lo ya dicho en el `closeout`:

- `good` entra en el uso mas estricto
- `review` queda para uso condicionado
- `bad` queda fuera del uso core

## Regla importante

Si un caso `quotes` necesita explicacion por `halts`, `reference`, `news` o `ipos`, eso se resolvera en la capa de ensamblado final, usando `05_crosswalk_multidataset.md` como marco, no creando aqui una semantica paralela.
