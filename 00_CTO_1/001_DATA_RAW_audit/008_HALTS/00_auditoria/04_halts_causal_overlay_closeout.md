# 04_halts_causal_overlay_closeout

## Objetivo

Cerrar la fase causal visual de `halts` sobre el universo canonico `<1B>`, ya cruzado con `quotes` y `trades`.

Esta fase ya no responde si `halts` esta estructuralmente bien construido. Eso quedo cerrado en `03_halts_root_cause_audit_phase1_closeout.md`.

Aqui la pregunta es otra:

- si el evento oficial de `halts` se puede ver fisicamente sobre `quotes` y `trades`
- si el cruce causal es coherente
- que buckets visuales dominan
- que limitaciones siguen abiertas

## Universo y artefactos

Universo operativo:

- `<1B>` via `market_cap_cutoff_lt_1b_active_inactive.parquet`

Artefacto canonico de viewer:

- `halts_quotes_trades_visual_cases.parquet`

Regla de grano:

- una fila por `visual_key`
- una vista fisica `ticker-day`
- puede agregar multiples halts del mismo dia en una sola figura

Consecuencia:

- no se muestran vistas duplicadas por `halt_day` y `resume_day`
- el viewer final trabaja sobre evidencia fisica deduplicada

## Snapshot del overlay causal

| metrica | valor |
| --- | ---: |
| filas visuales | `25,301` |
| `visual_key` unicos | `25,301` |
| media `events_in_visual` | `2.13` |
| mediana `events_in_visual` | `1` |
| max `events_in_visual` | `90` |

Lectura:

- la deduplicacion visual esta cerrada
- la mayoria de vistas contienen `1` solo evento
- existe una cola real de nombres con secuencias de halts repetidos en el mismo dia

## Buckets visuales finales

| bucket | visual_rows |
| --- | ---: |
| `confirmed_halt_microstructure_coherent` | `18,591` |
| `halt_with_trades_signal_only` | `3,914` |
| `halt_with_quotes_signal_only` | `1,896` |
| `halt_present_but_market_clean` | `516` |
| `market_signal_without_clear_halt_window` | `384` |

Bucket ausente en la build actual:

- `review_timestamp_alignment`

Lectura:

- el bucket dominante es claramente `confirmed_halt_microstructure_coherent`
- el segundo bloque importante ya no es conflicto puro, sino asimetria entre `quotes` y `trades`
- el residuo sin evidencia raw enlazada queda acotado

## 1. `confirmed_halt_microstructure_coherent`

Definicion operativa:

- el halt oficial existe
- `quotes` y `trades` dejan senal consistente alrededor del halt o del reopen
- la lectura causal es fuerte

Ejemplo representativo:

- `BLVD | 2014-06-04`
- `events_in_visual = 4`
- `rank_score = 42`

Resumen del caso:

- `quotes_rows_window = 63`
- `trades_rows_window = 20`
- cuatro ventanas oficiales de `5` minutos
- `quotes_link_strength = problem`
- `trades_link_strength = problem`

Lectura:

- es exactamente el tipo de caso para el que se construyo esta fase
- el evento oficial no solo existe, sino que organiza visualmente la anomalia
- en estos casos `halts` refuerza la lectura de `quotes` y `trades`

Consecuencia operativa:

- este bucket valida el uso de `halts` como capa causal real

## 2. `halt_with_trades_signal_only`

Definicion operativa:

- el halt oficial existe
- `trades` muestran senal util
- `quotes` enlazan, pero quedan `linked_clean` o sin ruptura comparable

Ejemplo representativo:

- `BOXL | 2018-02-20`
- `events_in_visual = 1`
- `rank_score = 17`

Resumen del caso:

- `quotes_rows_window = 5`
- `trades_rows_window = 8`
- `quotes_link_strength = linked_clean`
- `trades_link_strength = problem`

Lectura:

- la asimetria aqui no sugiere que `halts` este mal
- sugiere que el libro disponible para esa ventana es demasiado fino o poco expresivo
- el tape si deja senal de evento

Consecuencia operativa:

- no debe interpretarse como conflicto contra `halts`
- debe interpretarse como evidencia causal sostenida por `trades` con apoyo debil de `quotes`

## 3. `halt_with_quotes_signal_only`

Definicion operativa:

- el halt oficial existe
- `quotes` dejan senal fuerte
- `trades` no enlazan o enlazan limpios

Ejemplo representativo:

- `OFED | 2016-04-13`
- `events_in_visual = 1`
- `rank_score = 16`

Resumen del caso:

- `quotes_rows_window = 24`
- `trades_rows_window = 0`
- `quotes_link_strength = problem`
- `trades_file_visual = null`

Lectura:

- aqui no hay contradiccion con `halts`
- hay carencia o silencio del tape visible
- el libro si refleja el evento

Consecuencia operativa:

- este bucket es coherente con usar `halts + quotes` sin exigir confirmacion simetrica de `trades`

## 4. `halt_present_but_market_clean`

Definicion operativa:

- existe halt oficial
- `quotes` y `trades` enlazan
- ninguno de los dos lados entra en bucket de problema

Ejemplo representativo:

- `DGICB | 2016-06-27`
- `events_in_visual = 25`
- `rank_score = 2`

Resumen del caso:

- `quotes_rows_window = 1183`
- `trades_rows_window = 18`
- secuencia repetida de halts y resumes de `5` minutos
- ambos lados quedan `linked_clean`

Lectura:

- este bucket no invalida `halts`
- muestra que puede existir evento oficial sin una dislocacion microestructural fuerte o sin una ruptura que el detector actual marque como problema
- tambien puede reflejar casos de regimen repetitivo y estabilizado

Consecuencia operativa:

- no debe forzarse una lectura de anomalia solo porque haya halt oficial
- este bucket es importante para no sobreinterpretar el overlay

## 5. `market_signal_without_clear_halt_window`

Definicion operativa:

- el evento oficial existe
- el viewer no consigue enlazar raw util de `quotes` ni de `trades`
- o la fecha efectiva cae fuera de la cobertura actualmente materializada

Ejemplo representativo:

- `TOPS | 2026-03-10`
- `events_in_visual = 10`
- `rank_score = 0`

Resumen del caso:

- `quotes_file_visual = null`
- `trades_file_visual = null`
- hay halts y resumes oficiales, pero no raw enlazado en esta capa

Lectura:

- en la build actual este bucket esta dominado por ausencia de enlace raw, no por contradiccion visual fuerte
- por tanto el nombre del bucket debe leerse con cuidado
- hoy significa mas "sin evidencia visual enlazada" que "evidencia de mercado opuesta al halt"

Consecuencia operativa:

- este bucket sigue siendo residual
- pero no debe venderse como fallo economico demostrado
- es sobre todo un bucket de cobertura visual pendiente o de fecha fuera del alcance materializado

## 6. Sobre `review_timestamp_alignment`

Estado actual:

- no aparecen filas en este bucket

Lectura:

- eso no prueba que no existan problemas temporales
- solo indica que la taxonomia actual no los esta aislando como bucket dominante dentro del universo visual materializado

Consecuencia:

- si aparecen contradicciones puntuales en el viewer, siguen pudiendo abrirse como casos manuales de alineacion temporal
- pero no constituyen hoy una familia relevante del overlay

## Hallazgos globales

### 1. `halts` si explica visualmente una parte grande del universo

El hecho clave es la masa de `confirmed_halt_microstructure_coherent`.

Eso significa:

- el evento oficial no esta "flotando" aislado del mercado
- en muchas vistas el halt se ve fisicamente sobre el comportamiento intradia

### 2. El residuo principal es asimetrico, no contradictorio

Los buckets grandes residuales son:

- `halt_with_trades_signal_only`
- `halt_with_quotes_signal_only`

Eso apunta mas a:

- granularidad desigual del libro y del tape
- huecos de enlace parcial
- distinta sensibilidad de los detectores

que a falsedad del evento `halts`

### 3. El bucket `market_signal_without_clear_halt_window` no debe sobreleerse

En la build actual, gran parte de ese bucket entra por:

- `quotes_file_visual = null`
- `trades_file_visual = null`
- `rank_score = 0`

Por tanto:

- no es la prueba principal de conflicto causal
- es antes un bucket de no-enlace visual

## Limitaciones actuales

1. El viewer trabaja sobre raw enlazado, no sobre cobertura universal garantizada por fecha.
2. El diagnostico visual es fuerte, pero sigue apoyandose en taxonomias previas de `quotes` y `trades`.
3. El bucket `market_signal_without_clear_halt_window` mezcla ausencia de raw enlazado con posible conflicto temporal real.
4. La fase visual ya es util, pero todavia no materializa una politica `good / review / bad` propia de `halts` a nivel de overlay.

## Decision operativa

`halts` queda aceptado para uso causal visual dentro del universo `<1B>`.

Eso significa:

- puede usarse para explicar eventos observados en `quotes`
- puede usarse para explicar eventos observados en `trades`
- puede usarse para priorizar drilldown intradia por `visual_key`

Con dos salvedades explicitas:

- no todos los halts dejan una ruptura microestructural fuerte
- el bucket sin enlace visual no debe venderse como contradiccion economica confirmada

## Politica explicita `good / review / bad`

La calibracion manual del viewer deja una politica simple y defendible.

### `good`

- `confirmed_halt_microstructure_coherent`

Motivo:

- el halt oficial queda alineado visualmente con `quotes` y `trades`
- el overlay explica la microestructura y no solo la acompana

Caso de referencia:

- `BBGI | 2025-12-10`

Lectura del caso:

- secuencia larga de halts visibles
- libro y tape reaccionan en la misma narrativa temporal
- este es el patron que justifica aceptar `halts` como capa causal

### `review`

- `halt_with_quotes_signal_only`
- `halt_with_trades_signal_only`
- `halt_present_but_market_clean`
- `market_signal_without_clear_halt_window`

Motivo:

- no son familias malas por defecto
- pero tampoco conviene cerrarlas como `good` sin matiz
- mezclan asimetria entre libro y tape, cobertura parcial o eventos sin ruptura microestructural fuerte

Casos de referencia revisados:

- `FCCO | 2016-04-19`
- `PRGN | 2016-04-28`
- `DGICB | 2016-04-26`
- `LGPS | 2025-03-26`
- `BGFV | 2025-10-01`
- `CJET | 2025-07-17`

Lectura consolidada:

- `halt_with_quotes_signal_only`
  - queda bien como `review`
  - la senal dominante esta en `quotes`
  - `trades` faltan o no cuentan la misma historia con fuerza comparable
- `halt_with_trades_signal_only`
  - tambien queda bien como `review`
  - el tape sostiene la lectura causal
  - el libro enlaza limpio o poco expresivo
- `halt_present_but_market_clean`
  - debe quedarse en `review`
  - no porque se vea malo, sino porque es un bucket mixto
  - algunos casos se ven realmente limpios como `BGFV`
  - otros se ven mas ambiguos o con cierto reajuste como `CJET`
- `market_signal_without_clear_halt_window`
  - se mantiene en `review`
  - hoy esta dominado mas por no-enlace visual que por contradiccion economica dura

### `bad`

Estado actual:

- no queda ningun bucket agregado que merezca `bad` como familia estable

Lectura:

- pueden existir casos individuales malos o mal alineados
- pero no aparece hoy un bloque visual de tamano material que obligue a etiquetar una familia completa como `bad`

Consecuencia operativa:

- `halts` cierra esta fase con una politica `good / review / no_bad_family_detected`
- si en fases futuras aparece un subconjunto consistente de contradiccion real, podria abrirse una familia `bad`

## Siguiente paso correcto

Con esta fase cerrada, el siguiente trabajo util ya no es infraestructura de `halts`.

Es uno de estos dos:

1. muestreo manual disciplinado por bucket para fijar politica `good / review / bad` del overlay
2. pasar a `short`, `reference` o `additional` replicando este mismo patron de cierre
