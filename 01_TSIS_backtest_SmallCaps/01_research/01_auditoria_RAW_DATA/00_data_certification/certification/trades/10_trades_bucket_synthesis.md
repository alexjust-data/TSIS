# Trades | Síntesis de buckets

Con lo revisado hasta ahora, la lectura certificadora provisional de `trades` queda así.

## Buckets cerrados

- `reference_scale_mismatch`
  - `review`
  - el conflicto dominante es de comparabilidad por escala, no `bad_data`
- `review_microstructure`
  - `review`
  - residuo de comparabilidad/microestructura, no bucket limpio
- `review_1m_reference_alignment`
  - `review`
  - conflicto específico contra `1m`, no suficientemente limpio para `good`
- `review_no_1m_reference`
  - `review`
  - falta referencia `1m`, no deterioro claro del raw
- `bad_data`
  - `bad`
  - bucket real, con fuga residual pequeña de escala extrema, pero no redefinible en bloque como `scale mismatch`

## Lectura del bucket `review`

`review` genérico sigue siendo demasiado ancho para tratarlo ya como categoría final cerrada.

Hoy la lectura prudente es:

- mantenerlo como `review`
- no promoverlo a `good`
- no usarlo como bucket final fino sin una segmentación adicional

## Qué queda abierto de verdad

Ya no queda abierto el significado de los buckets específicos principales. Lo que sigue abierto es:

- la frontera `good / review`
- si una parte del `review` genérico puede escalar a `good`
- y cómo cerrar formalmente la convivencia entre:
  - universo full indexado `9,429,112`
  - residuo `D full` de `390,475`
  - y `file_acceptance` como política fina final

## Estado práctico

Para certificación operativa, `trades` puede leerse ya así:

- `good`
  - solo `good`, cuando exista de forma defendible
- `review`
  - `reference_scale_mismatch`
  - `review_microstructure`
  - `review_1m_reference_alignment`
  - `review_no_1m_reference`
  - `review`
- `bad`
  - `bad_data`

La siguiente pieza de trabajo ya no es otro bucket específico. Es decidir si el `review` genérico admite una partición adicional o si se deja así en el cierre final.
