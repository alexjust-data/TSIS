# Auditoria And Certification Source Hierarchy

## Objetivo

Este documento fija la jerarquia correcta entre `auditoria` y `certification` dentro de:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/`

La regla operativa del modulo es:

- `auditoria` descubre, segmenta, explica y prueba tecnicamente los problemas;
- `certification` decide el cierre operativo, los estados de recuperacion y el uso permitido por pipeline;
- `01_foundations` debe promover ambas capas, no solo una.

## Regla general

No es correcto trabajar un bloque solo desde:

- `auditoria/`

ni solo desde:

- `certification/`

La lectura minima correcta por bloque es:

1. `auditoria/` para entender el origen tecnico del problema, la taxonomia y la evidencia cruda;
2. `certification/` para entender la decision final de uso, recovery y closeout;
3. `01_foundations/` para comprobar que esa semantica ya quedo promovida o detectar huecos.

## Diferencia funcional entre carpetas

### `auditoria`

Es la capa fuerte para:

- notebooks ejecutados;
- diagnostico de root cause;
- taxonomia tecnica;
- comparativas baseline vs versiones nuevas;
- ejemplos crudos y drill-down forense.

Senales tipicas:

- notebooks `.ipynb` con celdas y salidas ya ejecutadas;
- markdown exportado desde notebooks;
- exploracion de granularidad, residuals y anatomia de fallos.

### `certification`

Es la capa fuerte para:

- contrato final de certificacion;
- expected / present / healthy / usable;
- recovery semantics;
- usage policy por pipeline;
- artifact mapping;
- tablas globales cross-block;
- closeout final mas cercano a decision institucional.

Senales tipicas:

- markdown de politica y closeout;
- scripts que renderizan ejemplos ya seleccionados;
- tablas agregadas y `global_metrics`.

## Daily

### `auditoria/daily`

Notebooks relevantes:

- `03_daily_root_cause_audit_notebook.ipynb`
- `04_daily_closeout.ipynb`

Lo que aportan:

- `03` descompone `HARD_FAIL` y `SOFT_FAIL`, compara baseline vs `v020` y estudia la anatomia de `vw_outside_range_rows`.
- `04` traduce el residual tecnico a una primera politica `good / review / bad` y deja el inspector final.

Outputs ya presentes:

- `03_daily_root_cause_audit_notebook.ipynb`: `13` salidas con imagen.
- `04_daily_closeout.ipynb`: `2` salidas con imagen.

### `certification/daily`

Archivos relevantes:

- `00_daily_current_state.md`
- `01_daily_recovery_and_coverage.md`
- `02_daily_quality_policy.md`
- `03_daily_closeout.md`

Lo que aportan:

- refinan la semantica de recovery y coverage;
- distinguen `LIKELY_VALID_GAP_ONLY`, `AMBIGUOUS_REVIEW` y `REALLY_PROBLEMATIC_UNEXPECTED`;
- cierran el bloque con estados mas ricos que el trio simple `good / review / bad`.

Diferencia importante frente a foundations actual:

- `certification/daily` usa una semantica mas fina:
  - `good`
  - `recoverable_without_penalty`
  - `recoverable_with_flag`
  - `review_not_rehabilitated`
  - `bad`

Consecuencia:

- `01_foundations/daily` sigue siendo util, pero simplifica demasiado si no absorbe esta capa de recovery.

## Quotes

### `auditoria/quotes/v2`

Notebooks relevantes:

- `04_quotes_full_C_D_methodology.ipynb`
- `04_quotes_full_C_D_closeout.ipynb`

Lo que aportan:

- taxonomia refinada;
- severidad economica del crossed;
- regimenes `mild / moderate / severe`;
- ejemplos representativos;
- cierre tecnico de los buckets abiertos.

Outputs ya presentes:

- `04_quotes_full_C_D_methodology.ipynb`: `6` salidas con imagen.
- `04_quotes_full_C_D_closeout.ipynb`: `9` salidas con imagen.

### `certification/quotes`

Archivos relevantes:

- `00_quotes_certification_guide.md`
- `01_quotes_certification_contract.md`
- `02_quotes_expected_presence_logic.md`
- `03_quotes_quality_policy.md`
- `04_quotes_usage_policy.md`
- `05_quotes_artifact_mapping.md`
- `06_quotes_cert_table_spec.md`
- `07_quotes_local_certification_build_plan.md`
- `08` a `11` bucket docs con `img/*.png`
- `12_quotes_open_buckets_synthesis.md`

Lo que aportan:

- confirman que la fuente maestra de closeout vive en `auditoria/quotes/v2`;
- formalizan mejor la capa `expected / present / healthy / usable`;
- fijan artifact mapping;
- dan una capa de imagenes de bucket ya seleccionadas y explicadas.

Evidencia visual ya materializada:

- `16` imagenes en `certification/quotes/img/` para los cuatro buckets abiertos.

Conclusion de alineacion:

- `01_foundations/quotes` ya esta bastante alineado con `certification`;
- la principal ganancia de `certification/quotes` es gobernanza, artifact mapping y framing poblacional, no una taxonomia distinta.

## Trades

### `auditoria/trades/v2`

Notebooks relevantes:

- `04_trades_full_C_D_audit.ipynb`
- `05_trades_file_acceptance_audit.ipynb`
- `06_trades_file_acceptance_full_lt1b_closeout.ipynb`

Lo que aportan:

- `04` ense?a el universo masivo y la raiz de `HARD_FAIL` y warnings;
- `05` explica metodologicamente por que muchos casos duros son comparabilidad, escala o microestructura;
- `06` intenta cerrar el full acceptance `<1B>`.

Outputs ya presentes:

- `04_trades_full_C_D_audit.ipynb`: `20` salidas con imagen.
- `05_trades_file_acceptance_audit.ipynb`: `8` salidas con imagen.
- `06_trades_file_acceptance_full_lt1b_closeout.ipynb`: `0` salidas guardadas actualmente.

Importante:

- `06` no conserva outputs ejecutados en el notebook actual, por lo que para el cierre institucional hay que apoyarse tambien en:
  - `certification/trades/*.md`
  - caches finales del run
  - `certification/global_metrics`

### `certification/trades`

Archivos relevantes:

- `00_trades_current_state.md`
- `01_trades_label_assessment.md`
- `02_trades_base_certification_decision.md`
- `03_trades_old_vs_new_bucket_bridge.md`
- `04_trades_provisional_cert_policy.md`
- `05` a `12` docs por bucket y casos visuales
- `13` a `18` docs de recovery por bucket
- `19_trades_final_recovery_policy.md`
- `20_trades_closeout.md`
- `00_render_trades_label_examples.py`

Lo que aportan:

- no solo etiquetan buckets;
- convierten labels tecnicos en estados finales de uso;
- separan `review` recuperable de `review` no rehabilitado;
- fijan el cierre institucional del bloque.

Diferencia importante frente a foundations actual:

- `certification/trades` es mas avanzado que `01_foundations/trades` en semantica final de recovery.
- La capa relevante que foundations debe absorber es:
  - `good`
  - `recoverable_with_flag`
  - `review_not_rehabilitated`
  - `bad`

## Global Metrics

Archivos relevantes:

- `00_final_certification_process.md`
- `03_build_global_metrics_artifacts.py`
- `global_metrics/manifest.json`
- tablas CSV generadas por bloque.

Lo que aportan:

- una lectura transversal de universo, presencia, salud y uso;
- tablas cross-block ya listas para consumo institucional.

Importante:

- `global_metrics` puede usar caches o rutas algo anteriores a las mas nuevas que foundations ya esta leyendo.
- Eso obliga a documentar cualquier drift de counts o path antes de promover tablas como verdad final del modulo.

## Jerarquia operativa por bloque

### Daily

1. `auditoria/daily` para root cause y anatomia.
2. `certification/daily` para recovery y closeout final.
3. `01_foundations/daily` debe reflejar ambas.

### Quotes

1. `auditoria/quotes/v2` como fuente tecnica maestra.
2. `certification/quotes` como contrato de certificacion, artifact mapping y usage layer.
3. `01_foundations/quotes` debe reflejar ambas.

### Trades

1. `auditoria/trades/v2` para descubrir la logica del problema.
2. `certification/trades` para la politica final de recovery y uso.
3. `01_foundations/trades` no debe cerrarse solo con la muestra metodologica de `380` files.

## Regla para agentes y para trabajo futuro

Antes de tocar `daily`, `quotes` o `trades`, es lectura minima obligatoria:

- la carpeta `auditoria/` del bloque;
- la carpeta `certification/` del bloque;
- y la capa ya promovida en `01_foundations/`.

Si `certification/` contiene una semantica final mas rica que `01_foundations/`, debe abrirse una nota de alineacion y corregirse foundations antes de seguir expandiendo documentos derivados.
