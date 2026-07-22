# Ohlcv 1m Split-Normalized - Operational Landing `v0_1`

## 1. Decision

La primera promocion operativa de `1m_split_normalized` debe vivir en:

- `E:\TSIS\data\ohlcv_1m_split_normalized`

## 2. Fuente obligatoria

La fuente obligatoria es:

- `D:\ohlcv_1m`

No debe construirse desde:

- `daily`
- `quotes`
- `trades`

## 3. Layout recomendado

La capa debe espejar el layout de `ohlcv_1m raw`.

Ejemplo:

- `E:\TSIS\data\ohlcv_1m_split_normalized\ticker=A\year=2005\month=01\minute_aggs_A_2005_01_split_normalized.parquet`

## 4. Estrategia de promocion

No se recomienda una materializacion full-universe inmediata.

La promocion correcta es:

- incremental
- por `ticker-month`
- y bajo demanda del consumidor intradia real

## 5. Consumidores esperados

Consumidores de mayor prioridad:

- feature pipelines intradia que crucen sesiones
- clasificadores de regimen intradia
- backtests intradia que acumulen contexto de varios dias

Consumidores de menor prioridad:

- ejecucion puramente local dentro de la sesion

## 6. Regla central

Si un pipeline no cruza ninguna frontera de split entre sesiones y solo necesita la verdad observada local del minuto:

- debe seguir usando `1m raw`

Si un pipeline compara sesiones historicas y necesita continuidad de escala:

- debe usar `1m_split_normalized`

## 7. Veredicto

Esta capa no reemplaza el intradia raw.

Lo protege cuando el problema dominante deja de ser la microestructura local y pasa a ser la comparabilidad historica entre sesiones.

## 7.1 Backtesting Oficial Y ML

Para backtesting intradia oficial y ML, la regla es:

```text
el scope exacto consumido debe tener estrategia split-safe declarada.
```

Si el experimento declara universo `<1B>` completo, entonces la vista 1m
split-normalized debe cubrir ese mismo universo/scope. Si el experimento usa
event windows o ticker-months concretos, basta con materializar y registrar ese
scope exacto.

Esto permite dos rutas:

- full-universe logico: materializar ticker-months afectados por splits y usar
  raw como fallback cuando `future_split_factor = 1`;
- full-universe fisico: copiar/materializar todo raw 1m en una raiz
  split-normalized completa.

Runbook operativo:

```text
01_foundations/module_contracts/ohlcv_1m_split_normalized_full_universe_materialization_runbook_v0_1.md
```

## 8. Estado actual

El piloto ya fue materializado en la ruta operativa propuesta:

- `E:\TSIS\data\ohlcv_1m_split_normalized`

Base usada:

- `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_pilot_manifest_v0_2.csv`

Resultados:

- `01_foundations/module_contracts/ohlcv_1m_split_normalized_pilot_results_v0_1.md`

## 8.1 Candidato Split-Affected Full-Universe Logico

La ruta candidata nueva es:

- `E:\TSIS\data\ohlcv_1m_split_normalized_full_universe_candidate`

Run completado:

- `split_affected_20260627_192314`

Resultado:

- `115667` filas de manifest;
- `24` chunks;
- `115667` outputs presentes;
- auditoria post-run ejecutada;
- `FAIL = 0` en los casos de split auditables.

Documento de resultados:

- `01_foundations/module_contracts/ohlcv_1m_split_normalized_split_affected_materialization_results_v0_1.md`

Estado:

```text
materialized_audited_candidate
```

Este root no sustituye todavia a:

- `E:\TSIS\data\ohlcv_1m_split_normalized`

ni a:

- `E:\TSIS\data\ohlcv_1m`

La promocion oficial queda pendiente de registry, policy, validators, tests y
decision explicita de consumo downstream.
