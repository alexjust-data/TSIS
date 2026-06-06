# Contrato Agent02 / Agent03 para `halts`

## Objetivo

Fijar el contrato analitico de `halts` como dataset oficial de eventos de mercado y regulacion, para que su uso en auditoria sea consistente con `quotes` y `trades`.

## Principio funcional

- `halts` es la fuente de verdad del evento.
- `quotes` y `trades` son la evidencia del comportamiento de mercado alrededor del evento.
- La auditoria de `halts` debe validar si el dataset es defendible como verdad regulatoria y si alinea correctamente con la microestructura observada.

## Unidad logica auditada

- Unidad principal: `halt_event`
- Unidad fisica de entrada: `source_row`
- Unidad consolidada: `canonical_halt_event`

## Rol de cada fuente

### Nasdaq

- Fuente venue para trading halts publicados por Nasdaq Trader.
- Debe tratarse como fuente primaria de evento venue.

### NYSE

- Fuente venue para trading halts publicados por NYSE.
- Debe tratarse como fuente primaria de evento venue.

### SEC

- Fuente regulatoria para suspensiones formales.
- Debe tratarse como fuente primaria de suspension regulatoria.
- No siempre aporta ticker o granularidad intradia suficiente.

## Claves candidatas por source

### Nasdaq

- `ticker`
- `halt_date`
- `halt_code`
- `halt_start_et`

### NYSE

- `ticker`
- `halt_date`
- `halt_type`
- `halt_start_et`

### SEC

- `ticker` si existe
- `issuer_name`
- `halt_date` o `publish_date`
- `release_no`

## Unidad consolidada

- `event_id_canonical`

Debe construirse como clave canonica reproducible que preserve:

- identidad del evento
- procedencia del source
- capacidad de agrupar duplicados exactos o semanticos

## Semantica de cobertura

- Ausencia de halt no significa ausencia de cobertura.
- Un ticker sin eventos puede estar perfectamente cubierto.
- La pregunta correcta es si el sistema detecta y caracteriza bien los eventos cuando existen.

## Preguntas que debe responder la auditoria

1. Si la descarga es reconstruible y versionada.
2. Si la normalizacion conserva la semantica del evento.
3. Si el evento tiene calidad suficiente para uso causal.
4. Si la consolidacion multisource deduplica sin fusionar mal.
5. Si el cruce con `quotes` y `trades` alinea en tiempo y sentido economico.

## Salidas operativas esperadas

La auditoria debe permitir clasificar cada evento en buckets de uso:

- `good_full_intraday_event`
- `good_date_level_event`
- `review_cross_source_conflict`
- `review_partial_identity`
- `review_missing_resume_time`
- `bad_unusable_event`

Y tambien clasificar el dataset a nivel agregado:

- `good_for_event_overlay`
- `good_for_daily_causal_context`
- `review_for_intraday_halt_window_analysis`
- `not_defensible_as_regulatory_truth`

## Relacion con `quotes` y `trades`

Para cada `canonical_halt_event` deben derivarse ventanas:

- `pre_halt`
- `halt_core`
- `reopen`
- `post_reopen`

Estas ventanas deben cruzarse con artefactos de `quotes` y `trades` para medir:

- crossed market
- spread anomalo
- ausencia o caida de quotes
- ausencia o rareza de trades
- prints de reapertura
- outside range tras reanudacion

## Regla de interpretacion

- Si `halts` confirma evento y `quotes/trades` muestran patron coherente, el caso refuerza la validez de ambos lados.
- Si `halts` confirma evento pero `quotes/trades` no muestran señal, el caso entra en revision de alineacion temporal o granularidad.
- Si `quotes/trades` muestran patron claro y `halts` no tiene evento, el caso entra en revision de cobertura o de fenomeno no-halt.
