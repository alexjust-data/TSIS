# LOCAL_RULES - 03_TSIS_Lab

Fecha: 2026-07-06
Estado: regla local activa

## Regla Obligatoria Para Velas 1m

Ningun agente debe asumir que `G:/TSIS/data/ohlcv_1m` es una fuente limpia para investigacion, charts, eventos, estados o validacion visual.

La lectura correcta es:

```text
raw 1m = fuente primaria historica
no = verdad visual ni verdad oficial de estado
```

Para cualquier trabajo con velas 1m dentro de `03_TSIS_Lab`, el agente debe declarar explicitamente que vista esta usando.

## Orden De Preferencia

### 1. Vista oficial/candidate materializada

Usar una tabla intradia quote-guarded materializada cuando exista cobertura para el ticker/sesion:

```text
master_intraday_bar_table_v0_2_candidate_quote_guarded
```

Esta es la ruta preferida para estado, eventos, outcomes y estadistica reproducible.

### 2. Vista reconstruida raw + repair manifest

Si la tabla materializada no cubre el caso, usar la combinacion documentada:

```text
G:/TSIS/data/ohlcv_1m
+
G:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
```

El agente debe conservar lineage de raw, manifest, run id, repair state y policy.

### 3. Puente visual provisional raw + quotes

Para inspeccion visual DAS/frontside cuando todavia no hay cobertura materializada, se permite un puente visual provisional:

```text
raw 1m
+
quotes por minuto
+
clip visual contra envelope q01/q99
+
scale guard raw/quotes
```

Este puente sirve para auditoria visual humana. No promociona data oficial y no sustituye a la tabla quote-guarded materializada.

## Guard De Escala Obligatorio

Antes de recortar OHLC raw contra quotes, el agente debe comprobar que raw y quotes estan en la misma escala de precio.

Regla practica actual:

```text
scale_ratio = median(raw_close / quote_mid)
```

Si `scale_ratio` es claramente incompatible, por ejemplo mayor que `3.0` o menor que `1/3`, el agente debe:

```text
1. no aplicar quote clipping
2. marcar el caso como scale_mismatch
3. conservar raw solo como vista de emergencia
4. enviar el caso a auditoria de data foundation
```

Ejemplo real:

```text
INM 2024-08-20
raw 1m y quotes estan en escalas distintas
visual_price_source = raw_1m_quote_guard_skipped_scale_mismatch
```

## Prohibiciones

No esta permitido:

```text
usar mechas raw 1m como verdad de first push, dip, rebreak o breakout
validar eventos con raw 1m sin declarar repair/guard state
recortar raw contra quotes sin scale guard
ocultar si quotes/trades no estan disponibles
presentar un chart visual provisional como tabla oficial
usar una vela corregida visualmente sin dejar manifest de fuente
```

## Obligaciones De Todo Chart 1m

Todo chart 1m usado para inspeccion o validacion debe dejar trazabilidad minima:

```text
visual_price_source
raw_root
quotes_root si aplica
repair_manifest si aplica
quote_guarded_changed_rows si aplica
scale_guard_state
scale_ratio si aplica
label_id por cada metrica pintada
anchor timestamp y precio de cada label
regla de calculo de cada metrica
```

Las marcas visuales deben pintarse desde las mismas coordenadas/precios que alimentan el calculo. No se permite colocar puntos, cruces o labels "a ojo".

## Lectura Para Agentes

Antes de modificar builders, charts, experiments o validators que consuman 1m, leer tambien:

```text
C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/research_design.md
C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/execution_protocol.md
C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0002/research_design.md
C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0002/data_and_lineage_policy.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md
```
