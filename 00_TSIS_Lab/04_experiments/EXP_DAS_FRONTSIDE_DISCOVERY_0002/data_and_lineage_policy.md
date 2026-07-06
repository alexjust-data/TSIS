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
