# Daily Validators - Modulo 01

## 1. Rol

Este documento define el conjunto base de validators para `daily_core_v0_1`.

Su funcion es traducir la semantica del contrato y de la policy a verificaciones reproducibles.

La taxonomia exacta de etiquetas y los thresholds literales de corte para `daily` viven en:

- `01_foundations/contract_registry/dataset_contracts/daily_label_taxonomy_and_cut_policy.md`

## 2. Principio rector

En `daily`, los validators no deben colapsar todo desvio en `corrupcion`.

Deben separar:

- invalidez dura;
- calidad primaria del bar;
- coverage;
- residuo recuperable;
- y condiciones de flag.

Cuando un caso termine en `bad`, los validators deben producir soporte suficiente para activar el protocolo definido en:

- `01_foundations/module_contracts/bad_evidence_and_rehabilitation.md`

La lectura institucional correcta de `daily` no debe quedar dominada por `vw`.

En este modulo:

- `OHLC`, `volume`, parse y fechas forman la validacion primaria;
- coverage forma la segunda capa estructural;
- `vw` o `vwap` forma una validacion secundaria de diagnostico y flag, no la autoridad principal del dataset.

Las verificaciones de este documento deben leerse siempre contra la politica de corte exacta fijada en:

- `01_foundations/contract_registry/dataset_contracts/daily_label_taxonomy_and_cut_policy.md`

## 3. Validators minimos requeridos

### schema_validator

Debe verificar:

- presencia de campos requeridos del schema logico;
- parseabilidad de `session_date`;
- parseabilidad numerica de OHLCV;
- coherencia basica de claves logicas.

### ohlc_integrity_validator

Debe verificar:

- `open`, `high`, `low`, `close` positivos en filas validas;
- `high >= max(open, low, close)`;
- `low <= min(open, high, close)`;
- `volume >= 0`.

Hallazgos como:

- `all_rows_invalid_after_parse`
- `negative_or_zero_ohlc_rows`

deben escalar como invalidez dura.

Este validator pertenece a la capa primaria de verdad del dataset.

Regla operativa adicional:

- la mera presencia de una fila en el archivo no autoriza su uso en `backtest_core`;
- si una barra presenta `OHLC = 0`, campos criticos en cero o contradicciones internas no defendibles, debe tratarse inicialmente como artefacto potencial y no como mercado confirmado;
- la inclusion solo seria valida si otra evidencia permite demostrar una semantica de mercado interpretable y no contaminante.

### temporal_and_uniqueness_validator

Debe verificar:

- parseabilidad de `date`;
- unicidad de fechas por file;
- coherencia del año;
- y consistencia minima entre file, particion y contenido.

Tambien pertenece a la capa primaria.

### coverage_validator

Debe verificar y clasificar estados de coverage como:

- `recoverable_without_penalty`
- `recoverable_with_flag`
- `review_not_rehabilitated`

Este validator debe leerse aparte de la calidad del bar.

Un caso puede estar sano en bar y seguir abierto en coverage.

### vw_regime_validator

Debe verificar:

- presencia y comportamiento de `vw` cuando exista;
- distancia de `vw` respecto de `high/low`;
- proporcion de dias afectados;
- y senales de iliquidez extrema.

No debe clasificar automaticamente todo `vw_outside_range` como `bad`.

Debe separar:

- borde de regla;
- residuo menor;
- regimen iliquido recuperable;
- y combinaciones con invalidez dura.

Este validator pertenece a la capa secundaria de `daily`.

Su funcion correcta es:

- detectar casos que exigen flag;
- abrir inspeccion fina;
- y evitar sobrerreaccion binaria.

No debe redefinir por si solo la salud global del dataset.

### exclusion_tail_validator

Debe materializar o verificar el exclusion set duro:

- `hard_invalid_parse_or_price`

Debe garantizar que esos objetos queden fuera de:

- `backtest_core`
- `backtest_extended`
- `ml_primary`
- `ml_flagged`

Tambien debe dejar disponible evidencia suficiente para:

- identificar el objeto afectado;
- explicar por que queda en `bad`;
- permitir cotejo humano cuando sea viable;
- y soportar una eventual evaluacion de rehabilitacion.

Cuando el caso se base en barras con:

- `OHLC = 0`
- `open = 0`
- `low = 0`
- `close = 0`
- `high < low`
- o incoherencia interna tipo `vw > high` con `high = 0`

el validator debe dejar explicito que el criterio de exclusion no es "dato raro".

Es:

- no defendibilidad actual como hecho de mercado apto para consumo principal.

## 4. Outputs minimos esperados

Los validators de `daily` deben poder producir, como minimo:

- clasificacion por estado de calidad primaria;
- clasificacion por estado de coverage;
- clasificacion secundaria de flags `vw` cuando aplique;
- exclusion tail duro consumible;
- resumen de contadores por bucket;
- y trazabilidad suficiente para auditoria posterior.

Para casos `bad`, cuando la unidad de analisis lo permita, tambien deben poder producir:

- evidencia inspeccionable por file, ticker o fecha;
- resumen del motivo causal de exclusion;
- y soporte para decidir entre `bad_confirmed`, `bad_recoverable_rejected`, `bad_rehabilitated_with_flag` o `bad_reclassified`.

## 5. Criterio de aprobacion

`daily_core_v0_1` pasa validacion institucional minima cuando:

- el schema logico requerido se satisface;
- la integridad primaria de OHLC y fechas se sostiene;
- el tail duro queda correctamente aislado;
- la coverage abierta queda etiquetada segun policy;
- y el residuo `vw` queda clasificado como capa secundaria sin sobrerreaccion binaria;
- la coverage abierta queda etiquetada segun policy;
- y los consumidores reciben solo los estados que les corresponden.

## 6. Regla final

Un validator de `daily` correcto no solo detecta errores.

Tambien preserva la interpretacion institucional de que:

- `daily` esta ampliamente sano;
- su verdad principal esta en OHLC, fechas, parse y coverage;
- su residuo mayoritario es recuperable;
- `vw` es una capa auxiliar de diagnostico y flag;
- y su exclusion dura es pequena, concreta y trazable.
