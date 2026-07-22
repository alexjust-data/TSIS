# 1m | Closeout

`ohlcv_1m` queda cerrado como bloque con política operativa sólida, pero con una salvedad de alcance.

## Lo que sí queda cerrado

- la semántica `good / review / bad`
- la lógica de rescate frente a cuarentena
- la prioridad de `parse_invalid` y `price_invalid` sobre el simple ruido de schema
- la existencia de recuperación incluso dentro de `price_invalid`

## Lo que no voy a sobreactuar

No he encontrado un artefacto ya materializado con filtro explícito `<1B>` para este cierre.

Por tanto:

- la política del bloque sí puede consumirse ya
- las proporciones exactas por bucket deben declararse como `full-scope`

## Veredicto práctico

La lectura correcta no es:

- `1m` roto

La lectura correcta es:

- `1m` con política de rescate dominante
- cuarentena muy pequeña
- y un núcleo `vw` que sí necesita separar:
  - ruido leve
  - review utilizable con cautela
  - masa grande persistente fuera del core

## Uso en certificación global

Para la certificación final, `1m` puede entrar ya con esta regla:

- usar la política `good / review / bad` actual
- dejar constancia de que las cuentas observadas hoy son `full-scope`
- si más adelante hace falta cifra exacta `<1B>`, aplicar la misma política sobre universo filtrado, no reinventar la auditoría
