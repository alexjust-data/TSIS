# 00_EVENT_LIBRARY

Estado: carpeta promovida de diseno conceptual.

La Event Library define fenomenos observables de mercado.

Responde:

```text
Que esta ocurriendo?
```

No responde:

```text
Que debo hacer?
```

Esa segunda pregunta pertenece a Strategy Library, Execution Models y Decision
Models.

## Inputs

- datos auditados de Data Foundation;
- conocimiento de microestructura;
- `00_private/eventos.md` como source note historica;
- material destilado desde `99_REFERENCE_LIBRARY/` cuando sea promovido;
- evidencia futura de Outcome Research, Pattern Discovery y Cluster Research.

## Outputs

- familias de eventos;
- definiciones de eventos;
- criterios observables;
- prerequisitos de datos;
- ambiguedades;
- exclusions;
- versionado de eventos.

## No-goals

La Event Library no contiene:

- entradas;
- stops;
- targets;
- sizing;
- portfolio rules;
- reglas de ejecucion;
- resultados de backtest.

Si una definicion incluye accion operativa, deja de ser evento y debe moverse a
Strategy Library, Execution Models o Decision Models.

## Familias activas

```text
01_MOMENTUM_EXPANSION
02_VWAP_CONTROL
03_INTRADAY_REVERSALS
04_MOMENTUM_EXHAUSTION
05_RUNNER_LIFECYCLE
06_RESISTANCE_AND_BREAKOUTS
07_SHORT_SQUEEZE_DYNAMICS
99_EXPERIMENTAL
```

Las familias son hipotesis organizativas. No son definitivas. Pattern Discovery
y Cluster Research podran proponer nuevas familias o cambios de frontera.

## Template minimo de evento

```yaml
event_name: VWAP_Reclaim_Event
family: VWAP_CONTROL
status: draft
description: >
  Price recovers VWAP after trading below it.
observable_conditions:
  - price_below_vwap_prior
  - cross_above_vwap
  - hold_above_vwap
required_inputs:
  - master_intraday_table
  - calendar_table
candidate_features:
  - gap_pct
  - float
  - reclaim_volume
  - reclaim_time
notes:
  - Not a strategy.
  - No entries.
  - No exits.
  - No stop loss.
```

## Lifecycle

```text
source_note
-> draft event definition
-> detector candidate
-> event_table version
-> outcome validation
-> promoted event
```

No event is institutional until it has explicit versioning, detector rules,
required inputs and reproducible outcome evidence.
