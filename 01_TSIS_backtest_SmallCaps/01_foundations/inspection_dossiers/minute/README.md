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
- assets tabulares persistidos.

No contiene:

- casepacks visuales por imagen como `quotes`, `trades` o `daily`;
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
  evidence_assets/
    raw_1m_lt1b_closeout/
      raw_1m_lt1b_exec_summary.csv
      raw_1m_lt1b_bucket_summary.csv
      raw_1m_lt1b_ticker_bucket_counts.csv
      raw_1m_lt1b_filtered_closeout.parquet
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

## Evidence Assets

Carpeta activa:

- `evidence_assets/raw_1m_lt1b_closeout/`

Assets:

- `raw_1m_lt1b_exec_summary.csv`
- `raw_1m_lt1b_bucket_summary.csv`
- `raw_1m_lt1b_ticker_bucket_counts.csv`
- `raw_1m_lt1b_filtered_closeout.parquet`

Rol de cada asset:

- `raw_1m_lt1b_exec_summary.csv`: contadores ejecutivos del universo filtrado.
- `raw_1m_lt1b_bucket_summary.csv`: distribucion de buckets operativos, estado final y familias `vw_*`.
- `raw_1m_lt1b_ticker_bucket_counts.csv`: conteos por ticker y estado final.
- `raw_1m_lt1b_filtered_closeout.parquet`: base filtrada completa para inspeccion y reproduccion.

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
5. Los assets tabulares en `evidence_assets/raw_1m_lt1b_closeout/`.
6. `01_foundations/module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md`.
7. Contract, schema, policy, registry y validators de `ohlcv_1m_raw`.
8. `inspection_dossiers/README.md`, seccion `Madurez relativa de dossiers`.

Reglas obligatorias:

- no llamar `minute` a `1m_split_normalized`;
- no usar porcentajes historicos `full-scope` si la afirmacion exige `<1B>`;
- no filtrar `<1B>` solo por ticker: aplicar tambien interseccion PTI;
- no presentar raw 1m como production-clean;
- no meter `review` o `bad` en consumo productivo silencioso;
- no ignorar `vw` aunque el consumidor no use la columna directamente;
- no convertir `RESCUE_SCHEMA_ONLY` en `good`;
- no usar raw 1m para features cross-session split-sensitive.

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
