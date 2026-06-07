# Minute Inspection Dossier

## Menu

- [Rol](#rol)
- [Estado Institucional](#estado-institucional)
- [Autoridad Documental](#autoridad-documental)
- [Fuentes Historicas](#fuentes-historicas)
- [Frontera Conceptual](#frontera-conceptual)
- [Estructura](#estructura)
- [Documentos Principales](#documentos-principales)
  - [`raw_1m_lt1b_closeout_recalculation_v0_1.md`](#raw1mlt1bcloseoutrecalculationv01md)
  - [`raw_1m_schema_only_lt1b_inspection_readout_v0_1.md`](#raw1mschemaonlylt1binspectionreadoutv01md)
  - [`raw_1m_schema_only_lt1b_inspection_notebook_v0_1.ipynb`](#raw1mschemaonlylt1binspectionnotebookv01ipynb)
- [Notebooks Modernos Core/Vw](#notebooks-modernos-corevw)
- [Evidence Assets](#evidence-assets)
- [Semantica De Calidad](#semantica-de-calidad)
  - [Estados finales](#estados-finales)
  - [Familias `vw_*`](#familias-vw)
  - [`RESCUE_SCHEMA_ONLY`](#rescueschemaonly)
- [Consumo](#consumo)
- [Relacion Con `1m_split_normalized`](#relacion-con-1msplitnormalized)
- [Reglas Para Futuros Agentes](#reglas-para-futuros-agentes)
- [Regla Final](#regla-final)


## Rol

Este dossier contiene la lectura humana e institucional del bloque `minute` del modulo `01_TSIS_backtest_SmallCaps`.

En esta carpeta, `minute` significa especificamente:

- `ohlcv_1m_raw_v0_1`
- barras intradia raw de un minuto
- escala observada no ajustada
- alcance institucional recalculado sobre universo `<1B>`

No significa:

- `ohlcv_1m_split_normalized`
- capa ajustada por splits
- feature layer productiva
- feed limpio para backtest intradia sin flags

La unidad logica de `ohlcv_1m_raw` es:

- `ticker-minute bar`

La unidad operativa de los closeouts historicos/recalculados es:

- `ticker-month file` o `task key` mensual

Ejemplo fisico representativo del schema raw:

- `D:\ohlcv_1m\ticker=HSLV\year=2026\month=03\minute_aggs_HSLV_2026_03.parquet`

La regla central del bloque es:

> `ohlcv_1m_raw` esta institucionalmente entendido y documentado, pero no esta certificado como capa globalmente limpia para consumo productivo sin flags.

## Estado Institucional

Estado actual:

- dataset: `ohlcv_1m_raw_v0_1`
- family: `ohlcv_1m`
- layer: `raw_market_bars`
- registry status: `institutional_raw_closeout_reconciled_lt1b`
- active: `true`
- raw root: `D:\ohlcv_1m`
- universo de referencia: `lt1b_universe_v0_1`

El dossier contiene:

- un recalculo cuantitativo del closeout raw historico sobre `<1B>`;
- un readout inspector para el bloque `RESCUE_SCHEMA_ONLY`;
- un notebook ejecutado para navegar los casos schema-only;
- un dossier visual fijo con `7` mapas poblacionales y `60` imagenes de caso para core/vw y coverage;
- assets tabulares persistidos.

No contiene:

- auditoria completa de `vw_*` caso por caso;
- promocion de raw 1m a capa productiva limpia.

## Autoridad Documental

Documentos especificos de `ohlcv_1m_raw`:

- `01_foundations/contract_registry/dataset_contracts/ohlcv_1m_raw_dataset_contract_v0_1.md`
- `01_foundations/canonical_schemas/ohlcv_1m/ohlcv_1m_schema_contract.md`
- `01_foundations/data_consumption_policies/ohlcv_1m_raw_consumption_policy.md`
- `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_raw_registry_entry.yaml`
- `01_foundations/validators/ohlcv_1m/ohlcv_1m_raw_validators.md`

Documentos transversales y relacionados:

- `01_foundations/module_contracts/inspection_dossier_model.md`
- `01_foundations/module_contracts/evidence_model.md`
- `01_foundations/module_contracts/layer_validation_standard_v0_1.md`
- `01_foundations/module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md`
- `01_foundations/dataset_registry/universes/lt1b_universe_registry_entry.yaml`
- `01_foundations/contract_registry/dataset_contracts/ohlcv_1m_split_normalized_dataset_contract_v0_1.md`

Regla de autoridad:

- este dossier gobierna la lectura raw de `ohlcv_1m`;
- `1m_split_normalized/` gobierna la vista derivada split-normalized;
- ningun agente debe mezclar ambas como si fueran el mismo objeto.

## Fuentes Historicas

El dossier no reaudita `ohlcv_1m` desde cero.

Encapsula y reconcilia:

- auditoria historica raw `1m`;
- certificacion historica `1m`;
- global metrics historicos;
- universo moderno `<1B>`;
- cierre moderno de `ohlcv_1m_split_normalized`.

Fuentes historicas principales citadas por la reconciliacion:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/ohlcv_1m/00_auditoria_ohlcv_1m.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/ohlcv_1m/04_ohlcv_1m_closeout.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/1m/00_1m_current_state.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/1m/02_1m_quality_policy.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/1m/03_1m_closeout.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/global_metrics/01_global_metrics_tables_traceable.md`

La conclusion historica valida que se conserva es:

- la policy causal raw de `1m` sigue siendo util;
- los problemas dominantes viven en schema, `vw`, parse invalid y price invalid;
- los porcentajes historicos `full-scope` no deben citarse como `<1B>` sin recalculo explicito.

Ese recalculo explicito ya existe en este dossier.

## Frontera Conceptual

En `minute` nunca deben mezclarse estos planos:

1. `ohlcv_1m_raw`;
2. `ohlcv_1m_split_normalized`;
3. closeout historico `full-scope`;
4. recalculo moderno `<1B>`;
5. ticker membership `<1B>`;
6. interseccion temporal PTI;
7. estado `good/review/bad`;
8. familias `vw_*`;
9. bloque `RESCUE_SCHEMA_ONLY`;
10. consumo permitido por policy.

La lectura correcta actual es:

- el proyecto institucional vive en marco `<1B>`;
- el closeout raw historico sigue siendo valido en policy y causalidad;
- sus porcentajes antiguos eran `full-scope`;
- este dossier fija los porcentajes raw `1m` estrictamente `<1B>`;
- `ohlcv_1m_split_normalized` resuelve otra deuda: comparabilidad cross-session frente a splits.

## Estructura

```text
inspection_dossiers/minute/
  README.md
  raw_1m_lt1b_closeout_recalculation_v0_1.md
  raw_1m_schema_only_lt1b_inspection_readout_v0_1.md
  raw_1m_schema_only_lt1b_inspection_notebook_v0_1.ipynb
  minute_00_universe_quality_overview_v0_1.ipynb
  minute_01_core_quality_model_v0_1.ipynb
  minute_02_core_quality_population_readout_v0_1.ipynb
  minute_03_casepack_builder_v0_1.ipynb
  minute_04_ticker_month_inspector_v0_1.ipynb
  minute_05_final_readout_v0_1.ipynb
  core_quality_case_evidence_packs/
    minute_core_quality_visual_cases_v0_1.md
    minute_core_quality_visual_case_manifest_v0_1.csv
    population_visual_overview/
      minute_population_visual_manifest_v0_1.csv
      *.png
    images/
      *.png
    contact_sheets/
      *.png
  evidence_assets/
    raw_1m_lt1b_closeout/
      raw_1m_lt1b_exec_summary.csv
      raw_1m_lt1b_bucket_summary.csv
      raw_1m_lt1b_ticker_bucket_counts.csv
      raw_1m_lt1b_filtered_closeout.parquet
    core_quality/
      minute_core_quality_manifest_v0_1.parquet
      minute_core_quality_family_counts_v0_1.csv
      minute_core_quality_summary_v0_1.csv
```

## Documentos Principales

### `raw_1m_lt1b_closeout_recalculation_v0_1.md`

Recalcula el cierre raw historico de `1m` sobre el universo `<1B>` explicito.

Inputs:

- cierre raw historico:
  - `runs/backtest/ohlcv_1m_v2_materialized/ohlcv_1m_current_full/root_cause_operational_outputs/*.parquet`
- corte canonico:
  - `runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active_inactive.parquet`

Script:

- `scripts/inspection/minute/audit_1m_raw_lt1b_closeout.py`

Regla de filtrado:

- ticker presente en `lt1b`;
- interseccion temporal entre ventana del file `1m` y ventana PTI del ticker;
- no basta filtrar solo por ticker.

Resultado agregado:

- `lt1b_tickers_reference = 4824`
- `lt1b_current_1m_rows = 334660`
- `lt1b_current_1m_unique_tickers = 4822`
- `lt1b_current_1m_unique_task_keys = 334660`
- `lt1b_current_1m_unique_good_tickers = 1526`
- `lt1b_current_1m_unique_review_tickers = 3792`
- `lt1b_current_1m_unique_bad_tickers = 4224`

Buckets operativos heredados:

- `RESCUE_SCHEMA_ONLY = 19713` (`5.890456%`)
- `RESCUE_SCHEMA_PLUS_VW = 314947` (`94.109544%`)

Estado final `<1B>`:

- `good = 46652` (`13.940118%`)
- `review = 75245` (`22.484014%`)
- `bad = 212763` (`63.575868%`)

Taxonomia `vw_*`:

- `vw_mild_low_ratio = 26939` (`8.049662%`)
- `vw_moderate_ratio = 23933` (`7.151437%`)
- `vw_severe_tiny_base = 12035` (`3.596187%`)
- `vw_severe_small_mass = 39277` (`11.736389%`)
- `vw_severe_large_mass_diffuse = 90159` (`26.940477%`)
- `vw_severe_large_mass_persistent = 122604` (`36.635391%`)

Veredicto:

- el recalculo cierra el matiz de alcance;
- `1m raw <1B>` sigue dominado por deuda `vw`;
- el bloque `bad` sigue siendo dominante incluso con el filtro correcto.

### `raw_1m_schema_only_lt1b_inspection_readout_v0_1.md`

Cierra visualmente y de forma inspeccionable el `5.890456%` no-`vw`.

No reabre:

- taxonomia `vw_*`;
- auditoria de `ohlcv_1m_split_normalized`;
- policy historica raw.

Pregunta precisa:

- que significa `RESCUE_SCHEMA_ONLY` dentro del recalculo `<1B>`.

Hallazgo:

- `schema_only = 19713`;
- la firma dominante concentra `18266` filas-mes;
- esa firma representa `92.66%` del bloque `schema_only`;
- corresponde a:
  - `dataset_read_incompatible_schema`;
  - `schema_merge_conflict_ticker_encoding`.

Lectura:

- `schema_only` no significa limpio productivo;
- significa que la anomalia dominante es estructural, homogenea y no economica de `vw`;
- los problemas son sobre todo lectura, compatibilidad de schema, ticker encoding y merge de columnas.

### `raw_1m_schema_only_lt1b_inspection_notebook_v0_1.ipynb`

Notebook inspector del bloque `RESCUE_SCHEMA_ONLY`.

Estado inspeccionado:

- `8` celdas;
- `5` markdown;
- `3` code;
- `3` celdas de codigo ejecutadas;
- `10` outputs `display_data`;
- `6` tablas HTML;
- `1` imagen;
- `0` errores.

Permite seleccionar:

- firma de warning;
- ticker;
- `year-month`.

Muestra para cada caso:

- metadatos del file-month;
- `rows_after_parse`;
- `active_days`;
- `coverage_ratio`;
- `vw_rows`;
- mensaje de error de lectura agregado;
- firma exacta de warning.

Uso correcto:

- inspeccion humana y navegacion de la cola schema-only;
- no sustituye el closeout cuantitativo;
- no prueba que raw 1m sea globalmente limpio.

## Notebooks Modernos Core/Vw

Fecha de referencia: 2026-06-07.

Se ha creado una segunda generacion de notebooks para elevar `minute` al modelo de inspeccion usado en `daily`, `quotes` y `trades`, pero respetando la naturaleza propia de `ohlcv_1m_raw`.

Estos notebooks son lanzaderas/lectores ligeros. La logica pesada y estable vive en scripts:

- `scripts/inspection/minute/export_minute_core_quality_casepacks.py`
- `scripts/inspection/minute/export_minute_population_visuals.py`
- `scripts/inspection/minute/build_minute_core_quality_visual_readout.py`
- `scripts/inspection/minute/build_minute_launcher_notebooks.py`

El punto clave de esta generacion es separar explicitamente:

- calidad core OHLCV;
- calidad `vw_*`;
- estado combinado;
- consumo permitido.

Esta separacion existe porque `vw` es importante, pero no debe eclipsar la pregunta principal de calidad raw de barra:

```text
si no uso vw, puedo confiar razonablemente en open/high/low/close/volume/window/coverage para investigacion controlada?
```

### Notebooks activos

`minute_00_universe_quality_overview_v0_1.ipynb`

- Estado: notebook lanzadera/lector.
- Rol: mapa ligero del universo `ohlcv_1m_raw <1B>` desde manifest persistido.
- Muestra distribuciones, estados heredados, familias `vw_*`, coverage, tickers y meses.
- No redefine la policy; prepara la lectura poblacional.

`minute_01_core_quality_model_v0_1.ipynb`

- Estado: notebook lanzadera/lector.
- Rol: documenta y apunta al manifest moderno core/vw ya persistido.
- Lee:
  - `evidence_assets/core_quality/minute_core_quality_manifest_v0_1.parquet`
  - `evidence_assets/core_quality/minute_core_quality_family_counts_v0_1.csv`
  - `evidence_assets/core_quality/minute_core_quality_summary_v0_1.csv`
- Es el notebook que fija la lectura actual `core_quality_state`, `vw_quality_state`, `combined_quality_state` y `allowed_consumption`.

`minute_02_core_quality_population_readout_v0_1.ipynb`

- Estado: notebook lanzadera/lector.
- Rol: lectura agregada ligera del manifest moderno.
- Explica la poblacion por estado core, estado `vw`, estado combinado, consumo permitido, familias y cobertura temporal.

`minute_03_casepack_builder_v0_1.ipynb`

- Estado: notebook lanzadera.
- Rol: muestra el comando del script que exporta casepacks visuales fijos y lee el manifest visual resultante.
- No contiene logica pesada de plotting en celdas.

`minute_04_ticker_month_inspector_v0_1.ipynb`

- Estado: notebook inspector ligero con widgets.
- Rol: visor de PNGs ya exportados.
- Permite escoger ticker/mes/problema desde menus interactivos y ver la imagen fija con metadata.
- No recalcula paneles dentro de celdas.

`minute_05_final_readout_v0_1.ipynb`

- Estado: notebook lanzadera/lector.
- Rol: entrada ligera al cierre operativo moderno.
- Resume el estado final de consumo y deja visible que la capa raw queda mucho mas defendible si se separa `core OHLCV` de `vw`.

### Resultado moderno actual

Manifest:

- filas: `334660`
- tickers: `4822`
- rango temporal: `2005` a `2026`

Estado core OHLCV:

- `core_good = 331511`
- `core_review = 3149`
- `core_bad = 0`

Estado `vw`:

- `vw_good = 46652`
- `vw_review = 75245`
- `vw_bad = 212763`

Estado combinado:

- `core_good = 118818`
- `core_good_vw_bad = 212693`
- `core_review = 3079`
- `core_review_vw_bad = 70`

Consumo permitido:

- `controlled_ohlcv_research = 118818`
- `ohlcv_without_vw_only = 212693`
- `flagged_research_or_sensitivity = 3149`

Lectura institucional:

- la mayoria del universo raw `1m <1B>` es razonablemente usable para investigacion controlada de OHLCV si no se consume `vw`;
- una masa muy grande debe excluir `vw` o tratarlo como no fiable;
- la cola `core_review` requiere investigacion o sensibilidad;
- no existe promocion productiva sin flags para backtesting/ML intradia;
- el consumo debe declarar si usa `vw` o no.

### Regla sobre `schema_readability_known_warning`

El manifest moderno conserva la familia:

- `schema_readability_known_warning`

pero no la usa por si sola para degradar `core_quality_state`.

Motivo:

- el warning procede de compatibilidad/lectura agregada conocida;
- no demuestra por si mismo fallo economico de OHLCV;
- degradarlo automaticamente convertiria casi todo el universo en `review` aunque el problema operativo dominante real sea `vw`.

Consecuencia:

- el warning queda trazado;
- los problemas core reales siguen separados;
- cualquier consumidor puede filtrar por esa familia si su engine de lectura es sensible al schema;
- pero la calidad economica core no queda confundida con una advertencia tecnica de lectura.

### Regla de uso de widgets

Los notebooks `minute_03` y `minute_04` existen para inspeccion humana interactiva.

Futuros agentes no deben eliminar los widgets ni convertirlos en tablas estaticas si la tarea pide investigacion caso a caso.

Los widgets son necesarios porque el inspector debe poder escoger:

- ticker;
- mes;
- familia de problema;
- estado core;
- estado `vw`;
- y caso concreto.

La evidencia fija inicial ya existe en:

- `core_quality_case_evidence_packs/minute_core_quality_visual_cases_v0_1.md`

Ese dossier contiene:

- `7` visuales poblacionales;
- `60` imagenes individuales de caso;
- `67` imagenes incrustadas en total;
- `1` seccion poblacional general;
- `6` secciones de casos;
- `10` casos por seccion;
- analisis independiente por imagen con `Que muestra / Responde / No responde / Consecuencia`;
- manifest poblacional reproducible en `population_visual_overview/minute_population_visual_manifest_v0_1.csv`;
- manifest visual reproducible en `minute_core_quality_visual_case_manifest_v0_1.csv`.

Los notebooks interactivos siguen siendo utiles para drilldown adicional. Si se necesita ampliar la evidencia fija, debe exportarse como nuevo casepack versionado mediante script/builder, no dejar la conclusion solo dentro del widget.

## Dossier Visual Core/Vw

Fecha de referencia: 2026-06-07.

Documento principal:

- `core_quality_case_evidence_packs/minute_core_quality_visual_cases_v0_1.md`

Scripts:

- `scripts/inspection/minute/export_minute_population_visuals.py`
- `scripts/inspection/minute/export_minute_core_quality_casepacks.py`
- `scripts/inspection/minute/build_minute_core_quality_visual_readout.py`

Assets:

- `core_quality_case_evidence_packs/population_visual_overview/`
- `core_quality_case_evidence_packs/population_visual_overview/minute_population_visual_manifest_v0_1.csv`
- `core_quality_case_evidence_packs/minute_core_quality_visual_case_manifest_v0_1.csv`
- `core_quality_case_evidence_packs/images/`
- `core_quality_case_evidence_packs/contact_sheets/`

Cobertura visual:

- mapa poblacional core/vw/state/consumption: `1` imagen.
- matriz poblacional core vs `vw`: `1` imagen.
- distribuciones poblacionales de familias core y `vw`: `1` imagen.
- coverage y footprint temporal poblacional: `1` imagen.
- anatomia poblacional schema-only: `1` imagen.
- delta visual de `vw_not_flagged` vs recalculo: `1` imagen.
- consumo permitido por ano: `1` imagen.
- `core_good_vw_not_flagged`: `10` imagenes.
- `core_good_vw_mild_or_moderate`: `10` imagenes.
- `core_good_vw_bad_persistent`: `10` imagenes.
- `core_good_vw_bad_diffuse`: `10` imagenes.
- `core_review_large_gap`: `10` imagenes.
- `core_review_sparse`: `10` imagenes.

Lecturas visuales clave:

- la vision poblacional demuestra que el eje core OHLCV es mayoritariamente `good`, mientras la deuda masiva vive en `vw`;
- la celda dominante es `core good / vw bad`, por lo que no se debe expulsar OHLCV automaticamente ni consumir `vw` sin declararlo;
- `schema_only` es principalmente una deuda estructural de lectura/schema/ticker encoding, no una familia economica de precio rota;
- desde 2017 la restriccion `ohlcv_without_vw_only` domina la masa anual, especialmente en los anos modernos con mas cobertura;
- `vw_not_flagged` no es visualmente uniforme: algunos casos son limpios, pero `MULN` muestra residuo `vw` recalculado que el bucket heredado no capturaba.
- `vw_bad_persistent` muestra dano `vw` repetido y visualmente claro; el consumo correcto es `ohlcv_without_vw_only`.
- `vw_bad_diffuse` muestra dano frecuente pero menos uniforme; tampoco habilita consumidores `vw`.
- `core_review_large_gap` esta gobernado por continuidad y gaps, no por precio roto.
- `core_review_sparse` esta gobernado por cobertura mensual parcial, no por invalidez automatica de los minutos presentes.

Regla:

- este dossier visual es obligatorio para cualquier inspector que quiera entender `minute` al nivel de `daily`, `quotes` o `trades`;
- el inspector debe leer primero los `7` mapas poblacionales y despues las `60` imagenes de caso;
- no basta abrir los notebooks modernos;
- no basta citar el manifest core/vw;
- cada imagen debe leerse individualmente.

## Evidence Assets

Carpeta activa:

- `evidence_assets/raw_1m_lt1b_closeout/`
- `evidence_assets/core_quality/`

Assets:

- `raw_1m_lt1b_exec_summary.csv`
- `raw_1m_lt1b_bucket_summary.csv`
- `raw_1m_lt1b_ticker_bucket_counts.csv`
- `raw_1m_lt1b_filtered_closeout.parquet`
- `minute_core_quality_manifest_v0_1.parquet`
- `minute_core_quality_family_counts_v0_1.csv`
- `minute_core_quality_summary_v0_1.csv`

Rol de cada asset:

- `raw_1m_lt1b_exec_summary.csv`: contadores ejecutivos del universo filtrado.
- `raw_1m_lt1b_bucket_summary.csv`: distribucion de buckets operativos, estado final y familias `vw_*`.
- `raw_1m_lt1b_ticker_bucket_counts.csv`: conteos por ticker y estado final.
- `raw_1m_lt1b_filtered_closeout.parquet`: base filtrada completa para inspeccion y reproduccion.
- `minute_core_quality_manifest_v0_1.parquet`: manifest moderno file-month con lectura separada core/vw.
- `minute_core_quality_family_counts_v0_1.csv`: conteos de familias core y `vw`.
- `minute_core_quality_summary_v0_1.csv`: resumen ejecutivo del modelo moderno.

Regla:

- estos assets gobiernan porcentajes `<1B>`;
- no deben sustituirse por porcentajes historicos `full-scope`;
- cualquier cita numerica raw `1m <1B>` debe salir de aqui o de un recalculo versionado posterior.

## Semantica De Calidad

### Estados finales

`good`:

- elegible para diagnostico raw intradia controlado;
- util para validaciones baseline de barra raw;
- requiere declarar que la escala es raw observada.

`review`:

- solo investigacion exploratoria con flag;
- sensibilidad;
- comparacion forense;
- candidate rescue analysis.

`bad`:

- solo forense;
- no productivo;
- no baseline backtest;
- no ML training;
- no target generation.

### Familias `vw_*`

El campo `vw` requiere taxonomia especifica:

- `vw_mild_low_ratio`
- `vw_moderate_ratio`
- `vw_severe_tiny_base`
- `vw_severe_small_mass`
- `vw_severe_large_mass_diffuse`
- `vw_severe_large_mass_persistent`

Regla:

- cualquier consumidor que use `vw` debe declarar que familias incluye o excluye;
- cualquier consumidor que no use `vw` debe conservar igualmente el quality state file-level.

### `RESCUE_SCHEMA_ONLY`

No equivale a production-good.

Debe leerse como:

- conflicto de lectura agregada;
- incompatibilidad de schema;
- ticker encoding / schema merge conflict;
- anomalia estructural homogenea;
- bloque no dominado por `vw`.

## Consumo

Permitido con `good`:

- raw minute-bar diagnostics;
- controlled intraday research;
- construction checks for `ohlcv_1m_split_normalized`;
- baseline raw-bar sanity checks.

Permitido con `review`:

- flagged exploratory research;
- sensitivity analysis;
- forensic comparison;
- candidate rescue analysis.

Permitido con `bad`:

- forensic analysis;
- root-cause investigation;
- exclusion manifests;
- validator development.

Prohibido salvo contrato posterior:

- unflagged production backtesting;
- unflagged ML training;
- cross-session return engineering;
- split-sensitive regime features;
- execution/fill simulation que asuma tradability quote-level;
- evidencia de que el universo full `<1B>` minute es production-clean.

## Relacion Con `1m_split_normalized`

`minute/` y `1m_split_normalized/` son complementarios, no redundantes.

`minute/` responde:

- que calidad tiene el raw `ohlcv_1m`;
- que problemas dominan;
- como se recalcula el cierre historico sobre `<1B>`;
- como debe leerse `RESCUE_SCHEMA_ONLY`.

`1m_split_normalized/` responde:

- si la comparabilidad cross-session queda protegida frente a splits;
- si una vista derivada puede usarse para features cross-session;
- si la capa derivada supero piloto, auditoria full-universe y readout final.

Regla:

- trabajo split-sensitive y features cross-session deben usar `ohlcv_1m_split_normalized`;
- raw 1m puede servir para features intrasesion locales solo con scope y flags declarados;
- no debe usarse raw 1m como sustituto de la vista split-normalized.

## Reglas Para Futuros Agentes

Antes de tocar o interpretar `minute`, leer en este orden:

1. Este `README.md`.
2. `raw_1m_lt1b_closeout_recalculation_v0_1.md`.
3. `raw_1m_schema_only_lt1b_inspection_readout_v0_1.md`.
4. `raw_1m_schema_only_lt1b_inspection_notebook_v0_1.ipynb`, incluyendo celdas y outputs.
5. `minute_00_universe_quality_overview_v0_1.ipynb`, incluyendo celdas y outputs.
6. `minute_01_core_quality_model_v0_1.ipynb`, incluyendo celdas y outputs.
7. `minute_02_core_quality_population_readout_v0_1.ipynb`, incluyendo celdas y outputs.
8. `core_quality_case_evidence_packs/minute_core_quality_visual_cases_v0_1.md`, viendo cada imagen y su lectura individual.
9. `minute_03_casepack_builder_v0_1.ipynb`, preservando widgets.
10. `minute_04_ticker_month_inspector_v0_1.ipynb`, preservando widgets.
11. `minute_05_final_readout_v0_1.ipynb`, incluyendo celdas y outputs.
12. Los assets tabulares en `evidence_assets/raw_1m_lt1b_closeout/`.
13. Los assets tabulares en `evidence_assets/core_quality/`.
14. Los assets visuales en `core_quality_case_evidence_packs/images/`.
15. `01_foundations/module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md`.
16. Contract, schema, policy, registry y validators de `ohlcv_1m_raw`.
17. `inspection_dossiers/README.md`, seccion `Madurez relativa de dossiers`.

Reglas obligatorias:

- no llamar `minute` a `1m_split_normalized`;
- no usar porcentajes historicos `full-scope` si la afirmacion exige `<1B>`;
- no filtrar `<1B>` solo por ticker: aplicar tambien interseccion PTI;
- no presentar raw 1m como production-clean;
- no meter `review` o `bad` en consumo productivo silencioso;
- no ignorar `vw` aunque el consumidor no use la columna directamente;
- no convertir `RESCUE_SCHEMA_ONLY` en `good`;
- no usar raw 1m para features cross-session split-sensitive.
- no colapsar `core_quality_state` y `vw_quality_state` en un unico veredicto si la pregunta de consumo no usa `vw`.
- no borrar ni simplificar los widgets de inspeccion interactiva de `minute_03` y `minute_04`.
- no cerrar `minute` solo con notebooks o manifests: el dossier visual fijo debe mantenerse y ampliarse si cambia la politica.

Cada avance material en este dossier debe actualizar:

- este README;
- `inspection_dossiers/README.md`, seccion `Madurez relativa de dossiers`;
- y `CHANGELOG.md` si cambia madurez, consumo, estructura documental o evidencia institucional.

## Regla Final

La lectura correcta de `minute` es:

```text
ohlcv_1m_raw = barras intradia raw + closeout historico reconciliado <1B> + quality-state gobernado
```

No es:

```text
ohlcv_1m_raw = capa limpia productiva para backtest/ML intradia sin flags
```

El error que este dossier debe evitar es confundir:

- raw con split-normalized;
- full-scope historico con `<1B>` recalculado;
- schema-only con good;
- y closeout entendido con promocion productiva limpia.
