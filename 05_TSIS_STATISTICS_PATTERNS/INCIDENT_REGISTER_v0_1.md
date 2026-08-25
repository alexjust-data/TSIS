# Daily Pattern Atlas Incident Register v0.1

Registro append-only de fallos de implementación y controles heredables.

## INC-20260824-001 — Hive partition type collision

- fase: production-equivalent probe, ocho shards;
- alcance observado: primeros tickers de los shards 0-7;
- síntoma: `ArrowTypeError`, `ticker string` incompatible con `ticker dictionary`;
- causa: `pyarrow.read_table(path)` activó inferencia de dataset Hive sobre una
  ruta `ticker=<TICKER>` y trató de combinar la partición con la columna física;
- impacto: cero filas materializadas; todos los fallos persistidos, sin salida
  parcial promocionada;
- corrección: leer cada fichero mediante `pyarrow.parquet.ParquetFile.read`;
- control heredable: los lectores de ficheros bajo particiones Hive no pueden
  inferir particiones cuando la misma clave existe físicamente;
- estado: corrected_pending_reprobe_all_shards.


## INC-20260824-002 — Nonpositive anchor produced infinite outcome

- fase: aggregation after eight shard-level PASS certifications;
- síntoma: DuckDB `STDDEV_SAMP is out of range`;
- causa: una sesión real con precio cero fue elegida como ancla y produjo una
  razón infinita en `horizon_peak_from_anchor_close_pct`;
- impacto: agregación abortada, sin manifest final ni autorización full-run;
- corrección: conservar todas las filas para reconciliación, añadir
  `analysis_eligible` y `quality_state`, y prohibir activaciones/anclas sobre
  OHLC no positivo o incoherente;
- control heredable: toda división de outcome exige ancla elegible y ningún
  infinito puede llegar a estadísticas agregadas;
- estado: corrected_pending_reprobe_all_shards.
## INC-20260825-003 — Invalid future rows contaminated retrospective outcomes

- fase: post-full independent audit of `20260824_full_v0_1`;
- evidencia: 747 filas inválidas con outcomes, 64 running highs contaminados,
  10 horizon peaks/eventos sobre `invalid_ohlcv`;
- causa: `argmax`, `cummax` y outcomes operaban sobre toda la ventana;
- impacto: el terminal estructural produjo un falso `PASS`;
- corrección: outcomes nulos en filas inválidas, running high y peak calculados
  solo sobre filas elegibles, gate terminal independiente y regresión sintética;
- control heredable: cero outcomes/eventos en filas inválidas y recomputación
  exacta del running high elegible;
- estado: corrected_pending_reprobe_all_shards.

## INC-20260825-004 — Physical volume schema varied by ticker

- fase: post-full scan of 24.120 Parquet parts;
- evidencia: 4.632 tickers con `v: double` y 192 con `v: int64` en sesiones y
  trayectorias;
- causa: dtype de origen propagado sin normalización contractual;
- impacto: incumplimiento del gate de schema estable aunque el union final
  coercionara a double;
- corrección: normalización float64 de OHLCV y precios normalizados, más
  fingerprint de cada part en certificación terminal;
- control heredable: exactamente una variante física por tabla en todos los
  shards;
- estado: corrected_pending_reprobe_all_shards.

## INC-20260825-005 — Cooldown cohorts did not represent all activations

- fase: semantic audit of full cohort statistics;
- evidencia: `gap_ge_30pct` tenía 13.488 activaciones pero solo 1.113 anclas con
  trayectoria; el rango por etiqueta era aproximadamente 6%-10%;
- causa: cooldown global aplicado entre cualquier familia de activación;
- impacto: las curvas no respondían qué ocurrió después de cada gap;
- corrección: conservar episodios cooldown como censo de ciclos y materializar
  por separado cohortes directas y case index sobre el 100% de activaciones;
- control heredable: D0 de cada cohorte directa debe reconciliar exactamente con
  el conteo de su etiqueta;
- estado: corrected_pending_reprobe_all_shards.

## INC-20260825-006 — Broken row lineage and incomplete run identity

- fase: post-full reproducibility audit;
- evidencia: `source_daily_file` apuntaba a `D:/ohlcv_daily`, root inexistente;
  manifest final sin commit, config hash, upstream identity o hashes de outputs;
- causa: lineage legacy propagado y `_git_commit` no usado por el orchestrator;
- impacto: el run ejecutado no podía reconstruirse desde el manifest final;
- corrección: canonicalización a `G:/TSIS/data/ohlcv_daily`, commit previo al
  run y lineage/hashes persistidos por pre/final manifest;
- control heredable: toda ruta distinta debe existir y todo run debe declarar
  commit/config/upstream antes de ejecutar;
- estado: corrected_pending_reprobe_all_shards.

## INC-20260825-007 — Future split factor leaked into observable table

- fase: contract-to-schema audit;
- evidencia: `future_split_factor` estaba físicamente presente en X-like output;
- causa: metadata de materialización se conservó a nivel de fila pese a ser
  declarada lineage-only;
- impacto: riesgo de consumo downstream como observable causal;
- corrección: eliminar la columna del output de sesiones y prohibirla en el
  certificador terminal;
- control heredable: `future_split_factor` puede existir en input ajustado pero
  nunca en outputs observables;
- estado: corrected_pending_reprobe_all_shards.

## Invalidación del run 20260824_full_v0_1

La auditoría posterior invalida su `PASS` estructural como cierre científico.
El run se conserva íntegro bajo `runs/invalidated/` y no puede alimentar la app,
un readout oficial ni una promoción.
## INC-20260825-008 — Upstream activity date column mismatch

- fase: terminal certification of `20260825_probe_v0_1`;
- evidencia: los 8 runners, certificadores de shard y agregador finalizaron, pero
  el gate de scope abortó con `Referenced column date not found`;
- causa: la autoridad upstream usa `session_date_et`, no `date`;
- impacto: probe terminal FAIL; no autorización full y ningún output promovido;
- corrección: proyectar explícitamente `session_date_et AS date` y exigir
  `family='ohlcv_daily'` en la reconciliación;
- control heredable: los schemas upstream se consumen por nombres canónicos
  auditados y el terminal certifica la familia esperada;
- estado: corrected_pending_reprobe_all_shards.
