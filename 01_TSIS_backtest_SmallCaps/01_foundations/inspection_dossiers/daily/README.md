# Daily Inspection Dossier

## Menu

- [Rol](#rol)
- [Estado Institucional](#estado-institucional)
- [Autoridad Documental](#autoridad-documental)
- [Fuentes Historicas](#fuentes-historicas)
- [Frontera Conceptual](#frontera-conceptual)
- [Estructura](#estructura)
  - [`daily_inspection_readout_v0_1.md`](#dailyinspectionreadoutv01md)
  - [`build_daily_inspection_pack.md`](#builddailyinspectionpackmd)
  - [`daily_adjusted_full_universe_audit_v0_1.md`](#dailyadjustedfulluniverseauditv01md)
  - [`daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md`](#dailyadjustedcomplexcorporateactionstailauditv01md)
- [Subcarpetas](#subcarpetas)
  - [`good_justification/`](#goodjustification)
  - [`flagged_case_evidence_packs/`](#flaggedcaseevidencepacks)
  - [`bad_case_evidence_packs/`](#badcaseevidencepacks)
  - [`coverage_case_evidence_packs/`](#coveragecaseevidencepacks)
  - [`evidence_assets/`](#evidenceassets)
- [Semantica De Calidad](#semantica-de-calidad)
  - [Calidad del bar](#calidad-del-bar)
  - [Coverage](#coverage)
- [Price Views](#price-views)
- [Consumo](#consumo)
  - [Permitido para `daily_core_v0_1`](#permitido-para-dailycorev01)
  - [No habilitado automaticamente](#no-habilitado-automaticamente)
  - [`daily_adjusted_v0_1`](#dailyadjustedv01)
- [Reglas Para Futuros Agentes](#reglas-para-futuros-agentes)
- [Regla Final](#regla-final)


## Rol

Este dossier contiene la lectura humana e institucional del bloque `daily` del modulo `01_TSIS_backtest_SmallCaps`.

Su funcion no es reemplazar el schema, el dataset contract, la consumption policy ni los validators. Su funcion es mostrar por que `daily_core_v0_1` y la capa derivada `daily_adjusted_v0_1` son defendibles a partir de evidencia historica, visual, tabular, contractual y reproducible.

La unidad operativa de inspeccion para `daily_core_v0_1` es:

- `ticker`
- `year`
- `ticker-year file`

Ejemplo:

- `D:\ohlcv_daily\ticker=HMNY\year=2025\day_aggs_HMNY_2025.parquet`

La unidad logica interna es:

- `ticker-day bar`

La regla central del bloque es:

> `daily` no se decide en un solo eje. Deben separarse siempre `quality axis` y `coverage axis`.

Un file puede estar sano como barra diaria y seguir abierto en coverage. Tambien puede tener una anomalia de calidad recuperable con flag sin convertirse en `bad`.

## Estado Institucional

`daily_core_v0_1` esta institucionalizado como dataset operativo del modulo 01.

Estado resumido:

- dataset base: `daily_core_v0_1`
- dominio: `daily`
- promotion state: `institutional`
- unidad de decision de calidad: `ticker-year file`
- unidad logica: `ticker-day bar`
- universo auditado historico: `<1B>`
- coverage temporal global de inspeccion: `2005-2026`

El cierre institucional principal vive en:

- `daily_inspection_readout_v0_1.md`

La guia de construccion del pack vive en:

- `build_daily_inspection_pack.md`

La capa derivada `daily_adjusted_v0_1` tambien esta institucionalizada como price view derivada promovida:

- canonical root: `E:\TSIS\data\ohlcv_daily_adjusted`
- source root: `D:\ohlcv_daily`
- promotion state: `full_universe_promoted`
- maturity: `Nivel 6 - Promovida`

La auditoria que sostiene esa promocion vive en:

- `daily_adjusted_full_universe_audit_v0_1.md`

## Autoridad Documental

Este dossier debe leerse junto con los documentos de autoridad de `01_foundations`.

Contratos especificos de `daily`:

- `01_foundations/contract_registry/dataset_contracts/daily_dataset_contract_v0_1.md`
- `01_foundations/contract_registry/dataset_contracts/daily_label_taxonomy_and_cut_policy.md`
- `01_foundations/canonical_schemas/daily/daily_schema_contract.md`
- `01_foundations/canonical_schemas/daily/daily_adjusted_schema_contract.md`
- `01_foundations/data_consumption_policies/daily_consumption_policy.md`
- `01_foundations/dataset_registry/daily/daily_registry_entry.yaml`
- `01_foundations/dataset_registry/daily/daily_adjusted_registry_entry.yaml`
- `01_foundations/validators/daily/daily_validators.md`

Contratos transversales que gobiernan la lectura:

- `01_foundations/module_contracts/inspection_dossier_model.md`
- `01_foundations/module_contracts/evidence_model.md`
- `01_foundations/module_contracts/bad_evidence_and_rehabilitation.md`
- `01_foundations/module_contracts/policy_explanation_standard.md`
- `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`
- `01_foundations/module_contracts/pipeline_price_view_policy.md`
- `01_foundations/module_contracts/price_views_registry.md`
- `01_foundations/module_contracts/layer_validation_standard_v0_1.md`
- `01_foundations/module_contracts/external_price_comparison_caveats.md`

Companions explicativos relacionados:

- `01_foundations/module_contracts/daily_acceptance_policy_explained.md`
- `01_foundations/module_contracts/daily_rules_explained_line_by_line.md`

## Fuentes Historicas

El dossier preserva y encapsula trabajo historico de auditoria y certificacion. No lo reescribe.

Fuentes historicas principales:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/daily/03_daily_root_cause_audit_notebook.ipynb`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/daily/04_daily_closeout.ipynb`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/daily/04_daily_closeout.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/00_daily_current_state.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/01_daily_recovery_and_coverage.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/02_daily_quality_policy.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/03_daily_closeout.md`

Coverage historico visual promovido:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/daily/02_diseno_implementacion_daily_v2.md`
- imagenes historicas `001.png` a `007.png`

Estas imagenes ya fueron reincorporadas en:

- `coverage_case_evidence_packs/daily_coverage_cases_v0_1.md`

## Frontera Conceptual

En `daily` nunca deben mezclarse estos planos:

1. schema logico de barras `daily`;
2. calidad primaria del bar;
3. diagnostico secundario de `vw`;
4. coverage y recovery;
5. estado final de certificacion;
6. price view raw, adjusted o adjusted proxy;
7. capa derivada `daily_adjusted`;
8. consumidores permitidos por policy.

La triparticion visual:

- `good`
- `non_good_quality`
- `bad`

solo organiza la inspeccion humana de calidad del bar.

La decision operativa completa combina:

- `quality axis`
- `coverage axis`

Estados finales relevantes:

- `good`
- `recoverable_without_penalty`
- `recoverable_with_flag`
- `review_not_rehabilitated`
- `bad`

## Estructura

```text
inspection_dossiers/daily/
  README.md
  build_daily_inspection_pack.md
  daily_inspection_readout_v0_1.md
  daily_adjusted_full_universe_audit_v0_1.md
  daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md
  good_justification/
  flagged_case_evidence_packs/
  bad_case_evidence_packs/
  coverage_case_evidence_packs/
  evidence_assets/
```

### `daily_inspection_readout_v0_1.md`

Es el documento principal de lectura humana para `daily_core_v0_1`.

Responde:

- cual es el veredicto institucional de `daily`;
- que diferencia hay entre inspeccion visual y certificacion final;
- que significa `bad`, `non_good_quality` y `good`;
- como se combinan quality y coverage;
- que consumidores pueden usar cada estado;
- donde estan los casepacks visuales;
- y por que `daily` queda ampliamente utilizable pese a una cola dura pequena.

Conteos clave de inspeccion visual:

- `bad = 102`
- `non_good_quality = 48`
- `good = 24` casos de muestra representativa

Conteos clave de coverage:

- `653` tickers sin `complete_daily`
- `374` recuperables sin penalizacion
- `222` recuperables con flag
- `57` abiertos como frontera de coverage

### `build_daily_inspection_pack.md`

Es la guia metodologica del dossier.

No ejecuta nada. Define como debe construirse o regenerarse el pack.

Regla principal:

- el builder no puede limitarse a `good / flagged / bad`;
- tambien debe evidenciar coverage y recovery;
- las imagenes historicas promovidas no deben volver a quedar fuera del cierre institucional.

Estado actual:

- el dossier historico de coverage ya esta promovido a `01_foundations`;
- la fase madura deseable es un script reproducible que regenere tambien la capa de coverage sin depender de rutas historicas.

### `daily_adjusted_full_universe_audit_v0_1.md`

Audita `daily_adjusted` frente al objetivo full-universe `2005-2026`.

Fuentes comparadas:

- raw: `D:\ohlcv_daily`
- adjusted: `E:\TSIS\data\ohlcv_daily_adjusted`

Resultado agregado clave:

- `raw_tickers = 12494`
- `adjusted_tickers = 12230`
- `raw_tickers_with_files = 12230`
- `adjusted_tickers_with_files = 12230`
- `raw_year_files = 125438`
- `adjusted_year_files = 125438`
- `ticker_with_files_coverage_pct = 100.0000%`
- `year_file_coverage_pct = 100.0000%`
- `missing_outputs = 0`
- `extra_adjusted_outputs = 0`
- `read_error_files = 0`
- `files_missing_required_columns = 0`
- `nonpositive_factor_rows = 0`
- `bad_price_view_rows = 0`
- `adjusted_rows_total = 27418158`

Perfil de activacion:

- `neutral_control = 9816`
- `split_only = 1210`
- `dividend_only = 861`
- `split_and_dividend = 343`

Veredicto:

- `daily_adjusted` esta correctamente definido, consumido y materializado fisicamente a cobertura full-universe frente al daily raw observado;
- la deuda de expansion fisica queda cerrada por coverage;
- la capa queda defendible como `Nivel 6 - Promovida`.

### `daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md`

Audita la cola de corporate actions complejas frente a la semantica actual de `daily_adjusted`.

Fuentes auditadas:

- `C:\TSIS_Data\data\additional\corporate_actions\splits`
- `C:\TSIS_Data\data\additional\corporate_actions\dividends`
- `C:\TSIS_Data\data\additional\corporate_actions\ticker_events`
- `D:\ohlcv_daily`

Hallazgo central:

- la deuda compleja real visible no es una masa estructurada rica de spin-offs o reorganizaciones;
- la deuda material medible es sobre todo `ticker_change`;
- existe una cola pequena de dividendos no `CD`, observada como `SC`.

Numeros clave:

- `ticker_event_rows_total = 3037`
- `ticker_event_ticker_change_rows = 3037`
- `ticker_change_rows_within_daily_window = 2142`
- `ticker_change_tickers_within_daily_window = 2072`
- `dividend_non_cd_rows = 361`
- `non_cd_dividend_rows_within_daily_window = 331`
- `non_cd_dividend_tickers_within_daily_window = 184`
- tipo observado no `CD`: `SC = 361`

Consecuencia institucional:

- no reabrir splits ni cash dividends base como si estuvieran sin resolver;
- decidir si `ticker_change` requiere politica explicita de continuidad/remap;
- declarar formalmente si `SC` se trata igual que `CD` o requiere matiz;
- distinguir deuda estructurada presente en fuente de deuda teorica futura.

## Subcarpetas

### `good_justification/`

Documento principal:

- `good_justification/daily_good_cases_v0_1.md`

Contiene una muestra representativa de `24` casos `good`.

Familias principales:

- `schema_only_or_other`
- `vw_edge_absmax_only`

Regla de lectura:

- `good` no significa ausencia literal de cualquier warning;
- significa que no hay una patologia diaria dominante que rompa la utilidad de la barra;
- `vw_edge_absmax_only` admite extremos puntuales si la proporcion y persistencia son bajas;
- `schema_only_or_other` significa ausencia de mecanismo de dano consistente, no riqueza estadistica garantizada.

Uso:

- apto para `backtest_core` en eje de calidad;
- apto para `ml_primary` si coverage y price view lo permiten;
- no autoriza ignorar coverage.

### `flagged_case_evidence_packs/`

Documento principal:

- `flagged_case_evidence_packs/daily_non_good_quality_cases_v0_1.md`

Contiene `48` casos `non_good_quality`.

Equivalencia contractual:

- `review` historico de daily = `recoverable_with_flag` contractual.

Buckets principales:

- `vw_low_ratio_limited_days`
- `vw_mid_ratio_illiquid_regime`
- `vw_high_ratio_illiquid_regime`
- `vw_warn_minor_or_material`

Regla de lectura:

- no son `good`;
- tampoco son `bad`;
- conservan estructura suficiente para no ser exclusion dura;
- exigen flag, sensibilidad, investigacion restringida o modelos de calidad.

No deben entrar en:

- `backtest_core` sin policy futura mas fuerte;
- `ml_primary` como observaciones limpias.

### `bad_case_evidence_packs/`

Documento principal:

- `bad_case_evidence_packs/daily_hard_invalid_cases_v0_1.md`

Contiene los `102` casos `hard_invalid_parse_or_price`.

Firmas principales:

- `all_rows_invalid_after_parse`
- `negative_or_zero_ohlc_rows`
- combinaciones con `vw_outside_range_severe`
- `OHLC = 0`
- campos criticos en cero
- contradicciones internas de precio

Regla de lectura:

- aqui la pregunta no es si el caso merece flag;
- la pregunta es si la barra sigue siendo interpretable como hecho de mercado;
- si no hay defendibilidad, queda fuera de consumo principal.

Uso permitido:

- `forensic_only`

Uso no permitido:

- `backtest_core`
- `backtest_extended`
- `ml_primary`
- `ml_flagged`

### `coverage_case_evidence_packs/`

Documento principal:

- `coverage_case_evidence_packs/daily_coverage_cases_v0_1.md`

Este dossier cierra la deuda visual de coverage.

Taxonomia de coverage:

- `LIKELY_VALID_GAP_ONLY = 374`
- `AMBIGUOUS_REVIEW = 222`
- `REALLY_PROBLEMATIC_UNEXPECTED = 57`

Familias visuales:

- familia A: gaps alineados entre `daily`, `1m`, `quotes` y `trades`;
- familia B: desalineacion moderada, normalmente con `quotes` y `trades` mas ricos que `daily`, pero sin ruptura grotesca de `daily`.

Regla de lectura:

- un gap no es automaticamente fallo duro;
- coverage no debe colapsarse a `good / bad`;
- `LIKELY_VALID_GAP_ONLY` apoya `recoverable_without_penalty`;
- `AMBIGUOUS_REVIEW` apoya `recoverable_with_flag`;
- `REALLY_PROBLEMATIC_UNEXPECTED` sigue siendo cola abierta, no prueba global contra daily.

### `evidence_assets/`

Contiene imagenes, manifests, tablas y parquets que sostienen la lectura.

Estructura activa:

- `good_sample/`
- `hard_invalid/`
- `non_good_quality/`
- `daily_adjusted_full_universe_audit/`
- `daily_adjusted_complex_actions_tail_audit/`

Resumen de artefactos:

- `good_sample`: `24` imagenes y manifests asociados;
- `hard_invalid`: `102` imagenes y tablas por caso;
- `non_good_quality`: `48` imagenes y tablas por caso;
- `daily_adjusted_full_universe_audit`: `7` CSV y `7` parquet;
- `daily_adjusted_complex_actions_tail_audit`: `4` CSV.

Regla:

- ningun asset debe leerse aislado;
- un CSV o PNG solo tiene autoridad si esta consumido por readout, casepack, audit o contrato;
- assets generados pero no consumidos deben archivarse o eliminarse segun `inspection_dossier_model.md`.

## Semantica De Calidad

### Calidad del bar

Buckets `good`:

- `schema_only_or_other`
- `vw_edge_absmax_only`

Buckets `recoverable_with_flag`:

- `vw_low_ratio_limited_days`
- `vw_mid_ratio_illiquid_regime`
- `vw_high_ratio_illiquid_regime`
- `vw_warn_minor_or_material`

Bucket `bad`:

- `hard_invalid_parse_or_price`

Regla de precedencia:

- `all_rows_invalid_after_parse` o `negative_or_zero_ohlc_rows` disparan `hard_invalid_parse_or_price`;
- los problemas `vw` se leen despues;
- `vw` es diagnostico y flag, no autoridad unica de salud global del dataset.

### Coverage

Estados:

- `recoverable_without_penalty`
- `recoverable_with_flag`
- `review_not_rehabilitated`

Mapeo:

- `LIKELY_VALID_GAP_ONLY` -> `recoverable_without_penalty`
- `AMBIGUOUS_REVIEW` -> `recoverable_with_flag`
- `REALLY_PROBLEMATIC_UNEXPECTED` -> `review_not_rehabilitated`

Regla:

- una coverage abierta no convierte por si sola un bar sano en `bad`;
- una calidad `bad` no se salva por coverage razonable;
- cuando calidad y coverage entren en conflicto, debe prevalecer la lectura mas restrictiva.

## Price Views

`daily` no debe interpretarse como automaticamente equivalente a charts externos ni a una serie ajustada.

Vistas relevantes:

- `daily_raw`
- `split_normalized`
- `adjusted_proxy`
- `adjusted`

Reglas:

- `ohlcv_daily` es la fuente raw diaria;
- `ohlcv_daily_adjusted` es la capa derivada promovida;
- `daily_raw` no debe usarse por defecto como vista principal de retorno economico multi-dia cuando el pipeline requiere comparabilidad a traves de corporate actions;
- `daily_adjusted` aporta `o_adjusted`, `h_adjusted`, `l_adjusted`, `c_adjusted` como columnas canonicas de retorno economico diario;
- las columnas raw `o`, `h`, `l`, `c` preservadas dentro de `daily_adjusted` siguen siendo precio observado bruto.

## Consumo

### Permitido para `daily_core_v0_1`

`good`:

- `backtest_core`
- `backtest_extended`
- `ml_primary`
- `ml_flagged`
- `research_only`

`recoverable_with_flag`:

- `backtest_extended`
- `ml_flagged`
- `research_only`

`bad`:

- `forensic_only`

Coverage `recoverable_without_penalty`:

- compatible con consumo principal si la calidad tambien lo permite.

Coverage `recoverable_with_flag`:

- requiere flag explicita.

Coverage `review_not_rehabilitated`:

- `research_only`
- `forensic_only`

### No habilitado automaticamente

- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

### `daily_adjusted_v0_1`

Permitido segun registry:

- `ml_primary`
- `ml_flagged`
- `research_only`
- `backtest_core`
- `backtest_extended`
- `forensic_only`

Restringido:

- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

## Reglas Para Futuros Agentes

Antes de tocar o interpretar `daily`, leer en este orden:

1. Este `README.md`.
2. `daily_inspection_readout_v0_1.md`.
3. `daily_adjusted_full_universe_audit_v0_1.md`.
4. `daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md`.
5. `build_daily_inspection_pack.md`.
6. Los cuatro casepacks:
   - `good_justification/daily_good_cases_v0_1.md`
   - `flagged_case_evidence_packs/daily_non_good_quality_cases_v0_1.md`
   - `bad_case_evidence_packs/daily_hard_invalid_cases_v0_1.md`
   - `coverage_case_evidence_packs/daily_coverage_cases_v0_1.md`
7. Los contratos, policy, schema, registry y validators listados en `Autoridad Documental`.
8. `inspection_dossiers/README.md`, especialmente `Madurez relativa de dossiers`.

Reglas obligatorias:

- no tratar `good / non_good_quality / bad` como semantica final completa;
- no olvidar el eje de coverage;
- no dejar que `vw` domine la salud global de `daily`;
- no usar `daily_raw` como retorno economico multi-dia si el pipeline exige continuidad ajustada;
- no presentar `daily_adjusted` como piloto: esta full-universe auditado y promovido;
- no decir que `ticker_change` esta resuelto por `daily_adjusted`;
- no decir que spin-offs o reorganizaciones complejas estan soportadas si no existen como fuente estructurada consumible;
- no consumir `bad` fuera de `forensic_only`;
- no consumir `recoverable_with_flag` como si fuera `good`.

Cada avance material en este dossier debe actualizar:

- este README;
- `inspection_dossiers/README.md`, seccion `Madurez relativa de dossiers`;
- y `CHANGELOG.md` si el avance cambia madurez, consumo, estructura documental o evidencia institucional.

## Regla Final

La lectura correcta de `daily` es:

```text
daily_core = barras raw auditadas + quality axis + coverage axis + policy de consumo
daily_adjusted = price view derivada + corporate actions soportadas + full-universe audit + consumer gobernado
```

El error que este dossier debe evitar es triple:

- convertir cualquier warning `vw` en corrupcion dura;
- convertir cualquier gap de coverage en fallo terminal;
- o mezclar raw, adjusted y adjusted proxy sin declarar price view.

`daily` esta ampliamente sano y es central para backtesting, ML diario y research, pero solo bajo consumo gobernado por sus contratos y policies.
