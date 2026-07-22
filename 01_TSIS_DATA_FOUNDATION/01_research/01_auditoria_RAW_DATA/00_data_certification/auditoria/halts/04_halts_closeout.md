# 04_halts_closeout

## Objetivo

Cerrar `halts` como bloque auditado dentro de `00_data_certification`, al mismo nivel de exigencia que `daily`, `ohlcv_1m`, `quotes` y `trades`.

Este cierre consolida dos fases:

- fase 1: estructura, completitud, taxonomia de evento y reconciliacion multisource
- fase 2: overlay causal visual sobre el universo canonico `<1B>` cruzado con `quotes` y `trades`

## Base del cierre

Documentos de apoyo ya cerrados:

- `03_halts_root_cause_audit_phase1_closeout.md`
- `04_halts_causal_overlay_closeout.md`

Artefactos canonicos:

- `source_quality_summary.parquet`
- `canonical_event_summary.parquet`
- `halts_lt1b_event_index.parquet`
- `halts_intraday_overlay_index.parquet`
- `halts_quotes_trades_visual_cases.parquet`

Notebook operativo:

- `03_halts_root_cause_audit_notebook.ipynb`

## Lectura final

### 1. `halts` queda aceptado como fuente de verdad del evento

La fase estructural deja cerrado que:

- `nasdaq` queda rescatado y utilizable para ventana intradia
- `nyse` queda estable como source venue
- `sec` queda aceptado como contexto regulatorio y fecha, no como reloj intradia fino
- el `multisource_row_mismatch` no refleja perdida de cobertura
- el residuo duro real queda reducido a raws vacios muy marginales

### 2. `halts` si alinea causalmente con mercado en una parte grande del universo

La fase visual `<1B>` deja cerrado que:

- domina `confirmed_halt_microstructure_coherent`
- el halt oficial se puede ver fisicamente sobre `quotes` y `trades`
- el overlay no es decorativo; es causalmente util

### 3. El residuo principal no es contradiccion dura

Los buckets `review` no apuntan a una familia mala dominante.

Apuntan sobre todo a:

- asimetria entre libro y tape
- cobertura visual parcial
- eventos oficiales sin ruptura microestructural fuerte

## Politica final `good / review / bad`

### `good`

- `confirmed_halt_microstructure_coherent`

Lectura:

- el halt oficial queda bien alineado con la microestructura observada

### `review`

- `halt_with_quotes_signal_only`
- `halt_with_trades_signal_only`
- `halt_present_but_market_clean`
- `market_signal_without_clear_halt_window`

Lectura:

- requieren contexto o muestreo puntual
- no bloquean el cierre del bloque
- no constituyen por si mismos evidencia de dataset malo

### `bad`

Estado actual:

- no se identifica una familia agregada `bad` en esta fase

Lectura:

- pueden existir casos individuales problematicos
- no aparece un bucket visual suficientemente coherente y material como para etiquetarlo como `bad` familiar

## Decision operativa final

`halts` puede darse por cerrado a nivel de auditoria.

Que significa "cerrado":

- existe contrato analitico
- existe builder reproducible
- existen artefactos reutilizables
- existe notebook metodologico y viewer visual
- existe lectura estructural defendible
- existe lectura causal visual defendible
- existe politica `good / review / bad`

Que no significa:

- no significa que todos los eventos sean igual de expresivos
- no significa que no queden casos de revision puntual
- no significa que `sec` deba usarse como timestamp intradia fino

## Uso recomendado

### Backtesting y analisis causal

Uso recomendado:

- si

Condicion:

- usar `halts` como capa de verdad del evento
- usar `quotes` y `trades` como evidencia alrededor del evento

### ML y features event-driven

Uso recomendado:

- si

Condicion:

- separar al menos `good` de `review`
- no tratar igual los casos sin evidencia visual enlazada que los casos causalmente coherentes

### Investigacion forense puntual

Uso recomendado:

- si, especialmente sobre `visual_key`

Condicion:

- abrir primero casos `good`
- despues muestrear `review` para no sobreinferir conflictos

## Siguiente paso

Con `halts` cerrado, el siguiente bloque natural a auditar con el mismo patron es `reference`.

Razon:

- esta mas cerca del nucleo de identidad, corporate actions y comparabilidad
- puede contaminar la interpretacion de `quotes`, `trades` y del propio overlay causal si queda sin cerrar
