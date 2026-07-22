# Plan De Prioridad Para Integracion Real De `price views`

## Objetivo

Este documento fija cual debe ser el primer aterrizaje productivo real de:

- `adjusted`
- `split_normalized`

y en que orden conviene promover consumidores posteriores.

## Veredicto corto

El primer consumidor real que debe promoverse no es:

- `quotes`
- `trades`
- ni un `execution_simulator`

El primer aterrizaje correcto es:

- **materializacion disciplinada de `daily_adjusted`**

para estos consumidores institucionales:

- `backtest_core`
- `backtest_extended`
- `benchmark interno`
- `ml_primary` diario
- `labels diarios de retorno`

Matiz estrategico:

- esto no convierte `daily_adjusted` en el nucleo alpha del proyecto;
- el nucleo alpha sigue siendo intradia y observado en `quotes_raw`, `trades_raw` y `1m raw`;
- `daily_adjusted` cierra primero la verdad economica lenta y de evaluacion.

## Por que esta es la primera prioridad correcta

### 1. Es el consumidor con mayor valor transversal

Si `daily_adjusted` queda bien promovido, resuelve de una vez la base economica para:

- retornos multi-dia comparables;
- benchmarking interno;
- equity curves;
- labels de ML diario;
- y research de senal disciplinado.

Es decir:

- no arregla un bloque local;
- arregla la base economica de varios consumidores a la vez.

### 2. Tiene menor ambiguedad que `quotes` o `trades`

`quotes` y `trades` siguen siendo capas de:

- microestructura;
- ejecucion;
- reconciliacion;
- y diagnostico de escala.

Su promocion productiva exige mas decisiones de sesion, disponibilidad, matching y arbitraje fino.

`daily_adjusted` es mas limpio como primer aterrizaje porque:

- su semantica ya esta mas cerrada;
- la implementacion reusable ya existe;
- y el uso economico diario ya esta doctrinalmente fijado en las policies.

### 3. Evita el error mas peligroso para backtest y ML

Hoy el mayor riesgo metodologico no es:

- un pequeño mismatch de `quotes`;
- ni una cola dura de `trades`.

El mayor riesgo transversal es:

- seguir construyendo retornos o labels diarios sobre `raw`
- y aprender corporate actions como si fueran alpha.

Promover `daily_adjusted` corta ese riesgo en la raiz.

### 4. No contradice el caracter intradia del proyecto

El proyecto opera sobre:

- activos dormidos que despiertan abruptamente
- scalping / hyperscalping
- y una capa ML que debe adaptarse al regimen intradia

Precisamente por eso hace falta separar:

- verdad economica lenta para evaluacion
- de verdad operativa observada para decision intradia

La primera la cierra `daily_adjusted`.
La segunda sigue viviendo en `quotes_raw`, `trades_raw` y `1m raw`.

## Donde no conviene empezar

### No empezar por `execution_simulator`

Motivo:

- exige una semantica microestructural mas estricta;
- y depende mas de `quotes_raw`, `trades_raw`, session scope, halts y calidad de tape.

Si se abre antes de cerrar `daily_adjusted`, se estaria abriendo un consumidor de umbral alto sin haber consolidado aun la base economica diaria mas simple y transversal.

### No empezar por `quotes` o `trades` como series economicas

Motivo:

- su rol primario no es producir retorno economico multi-dia;
- su rol primario es microestructura, ejecucion y reconciliacion.

Promoverlos primero como capa economica introduciria mas complejidad que valor.

## Secuencia recomendada

### Paso 1 - `daily_adjusted` materializado

Objetivo:

- producir una capa materializada y trazable de `daily_adjusted`

Base:

- `ohlcv_daily`
- `splits`
- `dividends`
- `src/data/price_views.py`

Salida minima recomendada:

- `o_adjusted`
- `h_adjusted`
- `l_adjusted`
- `c_adjusted`
- `future_split_factor`
- `future_adjustment_factor`
- metadatos de provenance

Consumidores que deberian quedar oficialmente conectados despues de este paso:

- `backtest_core`
- `backtest_extended`
- `benchmark interno`
- `labels diarios`
- `ml_primary` diario

Estado actual:

- ya existe un primer materializador en:
  - `scripts/materialize_daily_adjusted.py`
- ya existen contrato y schema minimos para esta capa;
- ya existe propuesta de landing operativo en:
  - `daily_adjusted_operational_landing_v0_1.md`
- y ya existe registry scaffolding en:
  - `01_foundations/dataset_registry/daily/daily_adjusted_registry_entry.yaml`
- y ya se verifico un smoke test real sobre `ticker=A` con salida temporal.

Lo que aun falta para considerar este paso plenamente promovido es:

- fijar una ruta canonica de materializacion persistente;
- decidir si la promocion sera full-universe o incremental;
- y conectar explicitamente al menos un consumidor real de `backtest` o labels a esta capa.

### Paso 2 - capa masiva de reconciliacion con `split_normalized`

Objetivo:

- crear una ruta utilitaria de reconciliacion visible y masiva entre:
  - `quotes_raw`
  - `trades_raw`
  - `daily_raw`
  - `split_normalized`
  - y opcionalmente `adjusted_proxy`

Motivo:

- hoy esta semantica ya vive muy bien en notebooks y paneles;
- falta promoverla como herramienta reutilizable fuera de inspeccion manual.

Consumidores naturales despues de este paso:

- vendor audit
- forensic reconciliation
- comparacion externa disciplinada

En este proyecto, aqui aparece ademas una necesidad explicita:

- una disciplina institucional de `1m_split_normalized`

porque cualquier modelo o backtest intradia que cruce una frontera de split o reverse split no debe aprender esa discontinuidad mecanica como si fuera movimiento economico real.

### Paso 3 - consumidores complejos de umbral alto

Solo despues deberian abrirse de forma contractual y operativa:

- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

Motivo:

- ya requieren una base previa estable;
- y no deben ser el lugar donde se descubra por primera vez una ambiguedad de semantica de precio.

## Relacion entre `adjusted` y `split_normalized`

No son prioridades rivales.

La lectura correcta es:

- `adjusted` debe aterrizar primero como base economica diaria de research, benchmark y labels;
- `split_normalized` debe aterrizar despues como base reutilizable de reconciliacion de escala en capas intradiarias y forenses.
- y en la familia intradia el primer derivado con mayor sentido practico es `1m_split_normalized`, no `quotes_adjusted` ni `trades_adjusted`.

Artefactos iniciales de esta fase:

- `01_foundations/contract_registry/dataset_contracts/ohlcv_1m_split_normalized_dataset_contract_v0_1.md`
- `01_foundations/module_contracts/ohlcv_1m_split_normalized_operational_landing_v0_1.md`
- `01_foundations/module_contracts/ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md`
- `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_registry_entry.yaml`
- `01_foundations/module_contracts/ohlcv_1m_split_normalized_semantic_pilot_v0_1.md`
- `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_pilot_manifest_v0_1.md`
- `01_foundations/module_contracts/ohlcv_1m_split_normalized_pilot_manifest_v0_2.md`
- `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_pilot_manifest_v0_2.csv`

Eso evita un error comun:

- intentar usar `split_normalized` como si fuera sustituto suficiente de `adjusted`

No lo es.

`split_normalized` corrige escala mecanica.
`adjusted` corrige continuidad economica.

## Estado actual frente a este plan

### Ya cerrado

- doctrine institucional
- implementacion reusable base
- uso fuerte en inspeccion y evidence packs

### Pendiente real

- materializacion estable de `daily_adjusted`
- conexion visible de esa vista a consumidores reales
- promocion utilitaria de reconciliacion masiva con `split_normalized`

## Veredicto final

La primera integracion productiva real debe ser:

- **`daily_adjusted` como capa canonica para retornos, benchmark y labels diarios**

Estado recomendado desde aqui:

- `daily_adjusted` ya puede planear cobertura full-universe `2005-2026`

Despues:

- **`split_normalized` como capa operativa de reconciliacion reutilizable**
- y en intradia:
  - `1m_split_normalized` primero como piloto semantico, no como full-universe inmediato
  - y su primer consumidor recomendado:
    - `intraday_regime_features`

Y solo despues:

- consumidores complejos de ejecucion, RL o live.
