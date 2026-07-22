# EXP_DAS_FRONTSIDE_DISCOVERY_0001

Fecha: 2026-07-05
Estado: draft
Tipo: strategy_seeded_research_experiment

## Rol

Este experimento es el primer experimento declarativo del Lab para estudiar DAS/frontside.

No nace como busqueda generica de momentum intradia. Nace de una estrategia discrecional humana concreta:

```text
DAS = Dips After Squeeze
```

La idea original era usar un screener de small/micro caps en premarket para encontrar tickers visibles/in-play, cazar movimientos frontside fuertes, exportar imagenes y estudiar visualmente si aparecia la secuencia:

```text
scanner / ticker in-play
-> awakening / primer push
-> primer dip
-> rebreak del high estructural del primer push
-> frontside activo
-> continuacion, fallo o backside
```

## Pregunta Cientifica

Pregunta general:

```text
Dentro de small/micro caps que el screener humano podia ver en premarket,
que estructura observable diferencia un frontside/DAS sano de un push que se destruye?
```

Primera subpregunta:

```text
Donde empieza la zona minima de operabilidad del frontside para estudiar longs DAS?
```

## Lectura Correcta

Los valores historicos del notebook/script son semillas humanas, no verdades cientificas:

```text
market_cap < 100M        = frontera de dominio para esta linea de investigacion
session_volume >= 500k   = semilla humana de liquidez, investigable
0.5 <= price <= 20       = semilla/rango operativo, investigable dentro del rango
session_scope=premarket  = semilla principal, investigable despues
push_label_pct=20        = semilla humana de primer push, investigable
dip_label_pct=3          = semilla humana de primer dip, investigable
momentum_trigger_pct=50  = criba humana de operabilidad frontside, investigable
```

## Archivos

```text
experiment.yaml
research_design.md
parameter_space.yaml
execution_protocol.md
sweeps/SWEEP_001_frontside_operability_boundary.yaml
```

## No-Goals

Este experimento no valida DAS como edge.
No valida una estrategia.
No optimiza entradas, stops ni targets.
No convierte +50% en evento oficial.
No interpreta los thresholds bajo 50% como setups long DAS.
No trata +50% como entrada; lo trata como frontera humana a auditar.
No convierte los runs visuales DAS en denominador poblacional.
No permite AlphaEvolve todavia.

## Siguiente Paso

Construir el preflight/executor minimo que lea los YAML, genere `resolved_config.yaml` y `preflight_report` antes de materializar casos historicos. La ejecucion oficial debe seguir `execution_protocol.md`, no un notebook manual.



