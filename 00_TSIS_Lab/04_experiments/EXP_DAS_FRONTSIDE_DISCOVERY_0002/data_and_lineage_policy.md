# Data And Lineage Policy - EXP_DAS_FRONTSIDE_DISCOVERY_0002

Fecha: 2026-07-06
Estado: draft_operativo

## Regla Base

`ohlcv_1m` raw no es suficiente para validar eventos, estados, charts ni outcomes.

Debe declararse la vista:

```text
official/candidate quote-guarded
raw + repair manifest
visual bridge raw + quotes
raw emergency only
```

## Fuente 1m Preferida

Cuando exista cobertura:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_2_candidate_quote_guarded/data.parquet
```

Si no cubre el ticker/sesion:

```text
E:/TSIS/data/ohlcv_1m
+
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
```

Para inspeccion visual provisional:

```text
E:/TSIS/data/ohlcv_1m
+
D:/quotes
+
visual quote guard q01/q99
+
scale guard
```



## Fuente Materializada Vigente Para Scanner 2026

Desde la materializacion full-universe quote-guarded, el scanner 2026 de este experimento debe leer preferentemente:

```text
C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_1
```

Esta base ya incorpora:

```text
raw ohlcv_1m
+ repair shards/manifests quote-guarded disponibles
+ checkpoints por ticker/anio
+ lineage de reparacion aplicado en materializacion
```

Por tanto, para `EXP_DAS_FRONTSIDE_DISCOVERY_0002`, `build_2026_scanner_from_qg_full_universe_1m_v0_2.py` es la ruta vigente. El flujo `raw 1m + repair shards durante el scanner` queda como referencia pre-materializacion o fallback declarado, no como ejecucion preferida.
## Fuente Exacta Del Scanner 2026

Para `EXP_DAS_FRONTSIDE_DISCOVERY_0002`, el denominador nuevo debe construirse desde:

```text
raw_root = E:/TSIS/data/ohlcv_1m
repair_manifest = E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
repair_shards = C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/*/repair_shards
master_daily = E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1
reference_overview = E:/TSIS/data/reference/overview
```

Regla operacional:

```text
raw 1m + quote-guarded repair shards = vista scanner research
```

El manifest consolidado `repair_manifest_lt1b_v0_1.parquet` es la prueba institucional de la reparacion, pero para ejecucion se prefieren shards por ticker/mes porque el parquet consolidado es demasiado grande para consultas interactivas por caso.

`candidate_events.parquet` de runs antiguos no es fuente permitida para construir el denominador de este experimento. Puede usarse solo como comparativa historica si se declara como `legacy_reference_only`.

## Market Cap Y Legalidad As-Of

`market_cap < 100M` es un filtro duro de la hipotesis DAS/frontside.

La fuente disponible hoy para este experimento es:

```text
E:/TSIS/data/reference/overview
```

Si `overview.request_date <= session_date`, el valor puede marcarse como `asof`.

Si solo existe un snapshot posterior a la sesion, el valor debe marcarse como:

```text
market_cap_source_state = future_snapshot_review
```

Ese caso puede servir para screening research si se declara, pero no puede entrar como observable legal de una tabla de estado as-of. Para promocion cientifica fuerte se necesita fuente point-in-time o politica explicita de exclusion/flag.

## Scale Guard

Antes de usar quotes para corregir visualmente OHLC:

```text
scale_ratio = median(raw_close / quote_mid)
```

Si hay mismatch:

```text
visual_price_source = raw_1m_quote_guard_skipped_scale_mismatch
```

El caso no puede usarse como evidencia limpia de anchor hasta auditoria.

## Trades

Si se estudia ejecucion intraminuto, las trades deben declararse aparte.

Si no hay trades premarket disponibles:

```text
execution_truth = unavailable
```

No se debe inferir fill real desde OHLC 1m.

## Campos De Lineage Minimos

```text
raw_root
raw_file_path
repair_manifest_path
repair_manifest_row_id si existe
quotes_root si aplica
quotes_file_path si aplica
visual_price_source
scale_ratio
scale_guard_state
renderer_version
builder_version
created_utc
```

## Casos Bloqueados

Bloquear para estadistica principal si:

```text
no hay vista 1m legal suficiente
raw/quotes scale mismatch sin resolucion
missing bars destruyen el anchor
first_push/dip/rebreak dependen de mecha raw no validada
coverage insuficiente en ventana clave
```

Se pueden conservar en un bucket separado:

```text
data_quality_blocked
```
