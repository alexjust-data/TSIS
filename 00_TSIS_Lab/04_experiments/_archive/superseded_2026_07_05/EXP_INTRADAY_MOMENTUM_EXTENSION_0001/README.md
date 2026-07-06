# Estado Archivado

Fecha de archivo: 2026-07-05
Estado: archived_superseded
Superseded by: `EXP_DAS_FRONTSIDE_DISCOVERY_0001`

Este experimento fue la semilla generica inicial para pensar `intraday_momentum_extension`, pero no es la ruta operativa activa.

La ruta activa actual es:

```text
C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001
```

Motivo:

```text
El trabajo real nace de una estrategia humana concreta: DAS/frontside.
El +50% debe estudiarse como sampling probe dentro de esa genealogia,
no como evento generico aislado.
```

---
# EXP_INTRADAY_MOMENTUM_EXTENSION_0001

Fecha: 2026-07-05
Estado: draft

## Objetivo

Primer experimento semilla para estudiar `intraday_momentum_extension` en small caps usando 1m quote-guarded cuando este disponible para el scope declarado.

Este experimento no busca demostrar que `+50%` sea el evento correcto.

Busca medir como cambia el fenomeno de momentum intradia al variar:

```text
threshold_pct
reference_price
session_scope
pre_event_window
post_event_window
liquidity_gate
```

## Lectura Correcta

```text
+50% = sampling_probe_human_seed
30m = sampling_window_controlled_seed
```

No son evento/ventana validados.

## Relacion Con Tablas De Estado

Este experimento consumira:

```text
market_state/event_state = X legal as-of
outcomes = y separado
```

El experimento no modifica el estado base ni copia outcomes dentro de X.

## Siguiente Paso

Completar `experiment.yaml`, definir primer sweep minimo y conectar el bridge SmallCaps sin sustituir el flujo de investigacion/backtest clasico del modulo SmallCaps.


