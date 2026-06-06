# Estado De Integracion Real De `price views`

## Objetivo

Este documento separa dos cosas que ya no deben confundirse:

- **contrato institucional**: que vista deberia usar cada pipeline;
- **integracion real en codigo**: donde esa decision ya esta aterrizada de verdad.

La prioridad 1 del repaso transversal no era redefinir la politica.
Era localizar esta brecha.

## Veredicto corto

La situacion actual es:

- la semantica institucional de `raw`, `split_normalized`, `adjusted` y `adjusted_proxy` ya existe;
- la implementacion reusable ya existe en `src/data/price_views.py`;
- pero el aterrizaje en consumidores reales sigue siendo limitado y desigual.

La conclusion correcta es:

- el proyecto ya no tiene una deuda teorica fuerte sobre `price views`;
- tiene una deuda de integracion productiva.

## Que ya existe de forma reusable

La capa reusable vive en:

- [price_views.py](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/src/data/price_views.py>)

Funciones ya presentes:

- `canonicalize_split_table`
- `build_future_split_factor_series`
- `apply_split_normalized_view`
- `canonicalize_dividend_table`
- `build_future_dividend_adjustment_table`
- `apply_adjusted_proxy_view`
- `apply_adjusted_view`

Esto significa que:

- `split_normalized` ya no es una idea;
- `adjusted_proxy` ya no es solo un panel de inspeccion;
- `adjusted` ya existe como primera implementacion institucional reusable.

## Donde si estan aterrizadas hoy

### 1. Capa de inspeccion y evidencia

Aqui la integracion es fuerte.

Bloques claros:

- `scripts/inspection/quotes/quotes_case_panel.py`
- `scripts/inspection/trades/trades_case_panel.py`
- `scripts/inspection/trades/trades_universe_panel.py`

Lectura correcta:

- las `price views` ya se usan para diagnostico, reconciliacion y evidencia institucional;
- especialmente en `quotes`, donde `split_normalized` y `adjusted_proxy` ya aparecen de forma visible en paneles y markdowns.

Consecuencia:

- la capa de inspeccion ya esta semanticamente madura;
- no es ahi donde vive hoy la mayor deuda.

### 2. Documentacion contractual y de consumo

Aqui la integracion es tambien fuerte.

Bloques claros:

- `price_views_registry.md`
- `pipeline_price_view_policy.md`
- `daily_consumption_policy.md`
- `quotes_consumption_policy.md`
- `trades_consumption_policy.md`

Consecuencia:

- el proyecto ya tiene claro que vista deberia usar cada tipo de pipeline;
- el problema no es de ambiguedad doctrinal.

## Donde no estan aterrizadas todavia de forma fuerte

### 1. Consumidores reales de backtest / research ejecutable

El bloque mas visible inspeccionado hasta ahora es:

- `scripts/backtest03_v3/`

Lectura tecnica:

- `contracts.py` define eras, roots y thresholds de cobertura;
- `orchestrator.py` y `policy.py` trabajan sobre elegibilidad y solape;
- pero no aparece cableado explicito a `src.data.price_views`.

Esto significa:

- el pipeline real revisado no esta consumiendo todavia `adjusted` o `split_normalized` como capa ejecutable institucional;
- su foco actual es cobertura / elegibilidad, no semantica economica final del precio.

Consecuencia:

- la policy ya sabe que `backtest` y labels diarios deben vivir sobre `adjusted`;
- pero esa decision no esta todavia materializada de forma visible en este consumidor real.

Matiz importante:

- ya existe una primera ruta materializadora de `daily_adjusted` en `scripts/materialize_daily_adjusted.py`;
- pero todavia no esta conectada de forma oficial a un consumidor real del bloque `backtest03_v3` ni a otro pipeline ejecutable equivalente.

### 2. Consumidores complejos aun no promovidos

Siguen sin contrato productivo final fuerte:

- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

Lectura correcta:

- el proyecto no esta prometiendo todavia que esos consumidores esten semantica y operativamente cerrados;
- cualquier uso ahi seguiria siendo prematuro sin una promocion adicional.

### 3. Integracion institucional de `split_normalized` fuera de inspeccion

Hoy `split_normalized` ya existe y se usa bien para explicar casos.

Pero sigue faltando:

- una capa utilitaria mas clara para consumidores de reconciliacion masivos;
- su aterrizaje visible en pipelines que comparen `quotes/trades` contra `daily` sin pasar por notebooks o paneles.

Consecuencia:

- el riesgo no es que la vista no exista;
- el riesgo es que algun consumidor futuro rehaga mal la normalizacion o la ignore.

### 4. Integracion institucional de `adjusted` fuera de la capa reusable

`adjusted` ya esta implementado, pero su aterrizaje visible sigue siendo limitado.

No hemos localizado aun:

- un pipeline de labels diarios que lo consuma de forma explicita;
- un backtest real del modulo que declare de forma operativa `signal_price_view = adjusted`;
- una capa de materializacion productiva estable de `daily_adjusted`.

Consecuencia:

- doctrinalmente el proyecto ya cerro la decision;
- operacionalmente todavia falta una promocion clara a consumidores reales.

## Matriz de estado

### `daily`

- Vista nativa observada: `daily_raw`
- Vista economica contractual: `adjusted`
- Estado en politica: cerrado
- Estado en implementacion reusable: presente
- Estado en inspeccion: presente
- Estado en consumidor real visible: parcial / aun no claramente promovido

### `quotes`

- Vista nativa observada: `quotes_raw`
- Vista de reconciliacion contractual: `split_normalized`
- Vista diagnostica contractual: `adjusted_proxy`
- Estado en politica: cerrado
- Estado en implementacion reusable: presente
- Estado en inspeccion: fuerte
- Estado en consumidor real visible: fuerte para inspeccion, debil fuera de inspeccion

### `trades`

- Vista nativa observada: `trades_raw`
- Vista de reconciliacion contractual: `split_normalized`
- Vista diagnostica contractual: `adjusted_proxy`
- Vista economica eventual: `adjusted` diario como capa externa de labels / benchmark
- Estado en politica: cerrado
- Estado en implementacion reusable: presente
- Estado en inspeccion: fuerte
- Estado en consumidor real visible: debil fuera de inspeccion

## Lectura institucional correcta

La prioridad 1 no debe interpretarse como:

- “falta inventar otra policy”

La lectura correcta es:

- ya existe suficiente gobierno semantico;
- ahora hace falta decidir donde se materializan esas vistas en codigo y artefactos de uso real.

## Secuencia recomendada de integracion real

### Paso 1

Promover una materializacion disciplinada de `daily_adjusted`:

- sobre `ohlcv_daily`
- usando la cadena ya definida de `splits + dividends`

Esto resolveria la base para:

- retornos economicos;
- benchmark interno;
- labels diarios de ML;
- y comparacion coherente entre research y evaluacion.

### Paso 2

Crear una capa explicita de reconciliacion diaria / intradiaria que consuma:

- `quotes_raw`
- `trades_raw`
- `split_normalized`
- opcionalmente `adjusted_proxy`

Objetivo:

- que la comparacion de escalas no dependa solo de notebooks y paneles.

### Paso 3

Solo despues, promover consumidores complejos:

- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

Porque esos consumidores ya no toleran ambiguedad ni semantica implícita.

## Veredicto final

`price views` ya estan institucionalmente definidas y tecnicamente arrancadas.

La brecha actual no es:

- falta de teoria;
- ni falta de implementacion minima reusable.

La brecha actual es:

- falta de promotion clara a consumidores reales del modulo.

Por eso la prioridad 1 sigue siendo correcta:

- cerrar el aterrizaje productivo real de `split_normalized` y `adjusted`

no para volver a discutir su semantica,
sino para que dejen de vivir sobre todo en policies e inspeccion y empiecen a vivir tambien en pipelines ejecutables reales.

La priorizacion concreta de ese aterrizaje vive en:

- [price_view_integration_priority_plan_v0_1.md](./price_view_integration_priority_plan_v0_1.md)
