# Trades Inspection Dossier

## Menu

- [Rol](#rol)
- [Estado Institucional](#estado-institucional)
- [Autoridad Documental](#autoridad-documental)
- [Fuentes Historicas](#fuentes-historicas)
- [Frontera Conceptual](#frontera-conceptual)
- [Estructura](#estructura)
  - [`population_evidence_packs/`](#populationevidencepacks)
  - [`file_acceptance_evidence_packs/`](#fileacceptanceevidencepacks)
  - [`good_justification/`](#goodjustification)
  - [`flagged_case_evidence_packs/`](#flaggedcaseevidencepacks)
  - [`bad_case_evidence_packs/`](#badcaseevidencepacks)
  - [`family_case_evidence_packs/`](#familycaseevidencepacks)
  - [`evidence_assets/`](#evidenceassets)
- [Universo Global `57f`](#universo-global-57f)
- [Rehabilitacion](#rehabilitacion)
- [Familias Semanticas](#familias-semanticas)
  - [`good`](#good)
  - [`review`](#review)
  - [`reference_scale_mismatch`](#referencescalemismatch)
  - [`review_microstructure`](#reviewmicrostructure)
  - [`review_no_1m_reference`](#reviewno1mreference)
  - [`review_1m_reference_alignment`](#review1mreferencealignment)
  - [`bad_data`](#baddata)
- [Modelo De Imagenes](#modelo-de-imagenes)
  - [Imagenes Globales](#imagenes-globales)
  - [Imagenes Historicas](#imagenes-historicas)
  - [Imagenes De Casepacks Amplios](#imagenes-de-casepacks-amplios)
- [Scripts Relevantes](#scripts-relevantes)
- [Price Views Y Arbitros](#price-views-y-arbitros)
- [Consumo](#consumo)
- [Reglas Para Futuros Agentes](#reglas-para-futuros-agentes)
- [Regla Final](#regla-final)


## Rol

Este dossier contiene la lectura humana e institucional del bloque `trades` del modulo `01_TSIS_backtest_SmallCaps`.

Su funcion no es reemplazar el schema, el dataset contract, la consumption policy ni los validators. Su funcion es explicar por que la politica vigente sobre `trades` es defendible a partir de evidencia poblacional, notebooks ejecutables, manifests reproducibles, casepacks visuales y contratos de consumo.

La unidad auditada practica es el file raw de trades por ticker-dia:

- `ticker`
- `date`
- `market.parquet`
- fila file-level correspondiente en la tabla de auditoria/materializacion

Dentro del file raw, la unidad elemental es el trade ejecutado:

- timestamp;
- price;
- size;
- exchange;
- conditions.

La regla central del bloque es:

> En `trades` no debe confundirse desacuerdo contra un arbitro (`daily` o `1m`) con corrupcion intrinseca del tape.

`outside_daily`, `outside_1m`, duplicados, odd-lots, off-session activity o scale mismatch son senales. No son, por si solas, una sentencia completa de consumo.

## Estado Institucional

El dossier actual ya contiene varias capas institucionales.

Readouts principales:

- `trades_inspection_readout_v0_1.md`
- `trades_global_universe_readout_v0_1.md`
- `build_trades_inspection_pack.md`
- `trades_sampling_strategy_v0_1.md`

Notebooks dentro del dossier:

- `trades_inspection_notebook_v0_1.ipynb`
- `trades_universe_inspection_notebook_v0_1.ipynb`

El notebook `trades_inspection_notebook_v0_1.ipynb` es un punto de entrada manual file-level. No contiene outputs persistidos; carga el selector y permite explorar libremente por capa, bucket y caso.

El notebook `trades_universe_inspection_notebook_v0_1.ipynb` si esta ejecutado. Es la capa poblacional moderna sobre `57f/full_clean_fast_same_schema`; produce y muestra las imagenes globales de universo.

Estado resumido:

- hay readout poblacional;
- hay readout file-acceptance;
- hay readout global-universe;
- hay manifests estratificados reproducibles;
- hay casepacks amplios por familia;
- hay selector interactivo;
- hay scripts reutilizables para regenerar muestras, casepacks y paneles.

Lo que no debe hacerse es presentar `trades` como cerrado por una sola capa. El cierre correcto depende de separar poblacion, muestra metodologica, full closeout y estados finales de certificacion.

## Autoridad Documental

Este dossier debe leerse junto con los documentos de autoridad de `01_foundations`.

Contratos especificos de `trades`:

- `01_foundations/contract_registry/dataset_contracts/trades_dataset_contract_v0_1.md`
- `01_foundations/contract_registry/dataset_contracts/trades_label_taxonomy_and_cut_policy.md`
- `01_foundations/canonical_schemas/trades/trades_schema_contract.md`
- `01_foundations/data_consumption_policies/trades_consumption_policy.md`
- `01_foundations/dataset_registry/trades/trades_registry_entry.yaml`
- `01_foundations/validators/trades/trades_validators.md`

Contratos transversales que gobiernan la lectura:

- `01_foundations/module_contracts/inspection_dossier_model.md`
- `01_foundations/module_contracts/evidence_model.md`
- `01_foundations/module_contracts/bad_evidence_and_rehabilitation.md`
- `01_foundations/module_contracts/policy_explanation_standard.md`
- `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`
- `01_foundations/module_contracts/external_price_comparison_caveats.md`
- `01_foundations/module_contracts/price_views_registry.md`
- `01_foundations/module_contracts/corporate_actions_adjustment_methodology.md`

Indices y explicaciones relacionados:

- `01_foundations/module_contracts/trades_contracts_index.md`
- `01_foundations/module_contracts/trades_acceptance_policy_explained.md`
- `01_foundations/module_contracts/trades_rules_explained_line_by_line.md`

## Fuentes Historicas

La jerarquia historica correcta viene de:

1. `auditoria/trades/v2`
2. `certification/trades`
3. `certification/global_metrics`, con chequeo de drift si cambian caches o rutas
4. contratos y policies promovidos a `01_foundations`

Fuentes principales de auditoria historica:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/trades/v2/03_diseno_implementacion_trades_CD.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/trades/v2/04_trades_full_C_D_audit.ipynb`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/trades/v2/04_trades_full_C_D_notebook.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/trades/v2/05_trades_file_acceptance_audit.ipynb`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/trades/v2/05_trades_file_acceptance_notebook.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/trades/v2/06_trades_file_acceptance_full_lt1b_closeout.ipynb`

Estas fuentes fijan tres capas distintas:

- `04`: snapshot poblacional de estres;
- `05`: muestra metodologica file-acceptance y rediseño taxonomico;
- `06`: cierre full final `lt1b` y etiquetas `57f`.

Fuentes de certificacion:

- `certification/trades`
- `certification/global_metrics`

Estas fuentes traducen labels file-level a estados finales:

- `good`
- `recoverable_with_flag`
- `review_not_rehabilitated`
- `bad`

## Frontera Conceptual

En `trades` nunca deben mezclarse estos niveles:

1. snapshot poblacional de estres;
2. muestra metodologica file-level;
3. labels file-level del cierre full `57f`;
4. estados finales de certificacion;
5. consumo operativo por pipeline.

Romper esta frontera produce el error principal detectado por la auditoria historica: leer como `bad tape` lo que puede ser comparabilidad de escala, microestructura, falta de arbitro fino o conflicto de price view.

## Estructura

```text
inspection_dossiers/trades/
  README.md
  build_trades_inspection_pack.md
  trades_inspection_readout_v0_1.md
  trades_global_universe_readout_v0_1.md
  trades_sampling_strategy_v0_1.md
  trades_inspection_notebook_v0_1.ipynb
  trades_universe_inspection_notebook_v0_1.ipynb
  population_evidence_packs/
  file_acceptance_evidence_packs/
  good_justification/
  flagged_case_evidence_packs/
  bad_case_evidence_packs/
  family_case_evidence_packs/
  evidence_assets/
```

### `population_evidence_packs/`

Documento principal:

- `population_evidence_packs/trades_population_readout_v0_1.md`

Esta capa explica masa poblacional, distribucion heredada, residuo D full y contaminacion de escala.

Responde:

- cuanta masa hay;
- que buckets dominan;
- por que `good` diminuto no equivale a "todo roto";
- por que el bloque necesita estados intermedios.

No responde:

- si un file concreto es recuperable;
- ni que caso individual representa toda una familia.

### `file_acceptance_evidence_packs/`

Documento principal:

- `file_acceptance_evidence_packs/trades_file_acceptance_readout_v0_1.md`

Esta capa explica la muestra metodologica `380` y por que cambio la lectura ingenua del bloque.

Responde:

- como se construyo la muestra;
- que hallazgos separaron `reference_scale_mismatch`, `review_microstructure`, `review_no_1m_reference`, `review_1m_reference_alignment` y `bad_data`;
- por que la taxonomia deja de ser solo contable y pasa a ser causal.

No responde:

- el tamaño final de cada bucket por si sola;
- ni la rehabilitacion completa sobre `57f`.

### `good_justification/`

Documento principal:

- `good_justification/trades_good_cases_v0_1.md`

Contiene casos historicos promovidos de la cola pristine `good`.

Regla de lectura:

- `good` no mide la masa util total;
- `good` mide pureza extrema;
- usar `good` como proxy de utilidad destruye cobertura.

### `flagged_case_evidence_packs/`

Documento principal:

- `flagged_case_evidence_packs/trades_review_cases_v0_1.md`

Contiene casos historicos de familias no limpias pero no necesariamente `bad`.

Incluye, entre otras:

- `reference_scale_mismatch`;
- `review_microstructure`;
- `review_1m_reference_alignment`;
- `review_no_1m_reference`;
- `review` generico.

### `bad_case_evidence_packs/`

Documento principal:

- `bad_case_evidence_packs/trades_bad_cases_v0_1.md`

Contiene casos historicos `bad_data`.

Regla de lectura:

- `bad_data` existe y es real;
- es una cola pequeña frente al universo completo;
- no es visualmente homogenea;
- no todo `bad_data` se demuestra con el mismo panel.

### `family_case_evidence_packs/`

Esta es la capa amplia por familia.

Documento indice:

- `family_case_evidence_packs/family_casepacks_index_v0_1.md`
- `family_case_evidence_packs/family_casepacks_index.csv`

Casepacks exportados:

- `family_case_evidence_packs/bad_data/bad_data_cases_v0_1.md`
- `family_case_evidence_packs/good/good_cases_v0_1.md`
- `family_case_evidence_packs/reference_scale_mismatch/reference_scale_mismatch_cases_v0_1.md`
- `family_case_evidence_packs/review/review_cases_v0_1.md`
- `family_case_evidence_packs/review_1m_reference_alignment/review_1m_reference_alignment_cases_v0_1.md`
- `family_case_evidence_packs/review_microstructure/review_microstructure_cases_v0_1.md`
- `family_case_evidence_packs/review_no_1m_reference/review_no_1m_reference_cases_v0_1.md`

Conteos exportados:

- `bad_data`: `60`
- `good`: `106`
- `reference_scale_mismatch`: `60`
- `review`: `60`
- `review_1m_reference_alignment`: `60`
- `review_microstructure`: `60`
- `review_no_1m_reference`: `60`

Esta capa no agota el universo completo. Es una muestra amplia, reproducible y estratificada, diseñada para que el inspector no dependa de dos ejemplos bonitos.

### `evidence_assets/`

Contiene assets persistidos.

Subcarpetas principales:

- `evidence_assets/global_universe/`
- `evidence_assets/historical_assets/`
- `evidence_assets/stratified_samples/`

`global_universe/` contiene el snapshot poblacional y las imagenes modernas del universo `57f`.

`historical_assets/` contiene imagenes historicas promovidas desde certification/auditoria.

`stratified_samples/` contiene manifests reproducibles por familia, en `.csv` y `.parquet`, mas el resumen de cuotas.

Documento principal de manifests:

- `evidence_assets/stratified_samples/trades_stratified_sample_manifests_v0_1.md`

## Universo Global `57f`

El readout global se apoya en:

- `trades_global_universe_readout_v0_1.md`
- `trades_universe_inspection_notebook_v0_1.ipynb`
- `evidence_assets/global_universe/trades_universe_snapshot_v0_1.json`

Conteos finales del universo:

- `review = 4,851,211`
- `reference_scale_mismatch = 2,418,062`
- `review_microstructure = 2,130,781`
- `bad_data = 15,869`
- `review_no_1m_reference = 8,091`
- `review_1m_reference_alignment = 4,992`
- `good = 106`

Lectura correcta:

- `bad_data` es real pero no domina;
- `good` es pristine pero demasiado pequeño para medir utilidad;
- `review` es la mayor frontera de rehabilitacion;
- `reference_scale_mismatch` requiere politica de reconciliacion, no rechazo automatico;
- `review_microstructure` requiere lectura de textura del tape, especialmente odd-lots.

Lectura incorrecta:

- "`good` es minimo, luego casi todo esta roto".

## Rehabilitacion

La regla estricta aplicada al bucket `review` exige:

- `scale_bucket_vw` en `{~1x, near_1x}`;
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 0.5`;
- `outside_daily_regular_pct <= 1`;
- `outside_1m_regular_pct <= 15`.

Resultado sobre `57f`:

- `review_total = 4,851,211`
- `review_recoverable_strict = 3,327,955`
- `review_recoverable_strict_pct = 68.6005%`
- `review_not_rehabilitated_strict = 1,523,256`

La regla extendida exige:

- `scale_bucket_vw` en `{~1x, near_1x}`;
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 1.0`;
- `outside_daily_regular_pct <= 2`;
- `outside_1m_regular_pct <= 20`.

Resultado sobre `57f`:

- `review_recoverable_extended = 3,505,290`
- `review_recoverable_extended_pct = 72.2560%`
- `review_not_rehabilitated_extended = 1,345,921`

Regla de lectura:

- la masa util real de `trades` no vive en `good`;
- vive sobre todo en `recoverable_with_flag`;
- pero no debe inflarse con el optimismo historico parcial de `57e`.

## Familias Semanticas

### `good`

Cola pristine.

Significa:

- tape limpio;
- comparabilidad fuerte con arbitros;
- sin caveats materiales.

No significa:

- masa util total;
- ni que todo lo no-good sea inservible.

### `review`

Residuo principal.

Significa:

- no es pristine;
- tampoco es automaticamente `bad`;
- parte importante puede pasar a `recoverable_with_flag` con regla explicita.

### `reference_scale_mismatch`

Familia de conflicto de comparabilidad/escala frente a arbitros.

Significa:

- desacople entre `trades_raw` y referencias;
- problema de escala o price view;
- necesidad de reconciliacion antes de consumo.

No significa:

- tape roto por defecto.

### `review_microstructure`

Familia de textura fina del tape.

El universo muestra dominancia extrema de odd-lots.

Significa:

- rareza microestructural;
- composicion de prints;
- posible utilidad si el pipeline declara semantica y flags.

No significa:

- corrupcion bruta;
- ni alpha limpia por defecto.

### `review_no_1m_reference`

Familia donde falta el arbitro fino `1m`.

Significa:

- limitacion epistemica;
- no se puede cerrar con la misma fuerza que cuando existe `1m`.

No significa:

- `bad_data` automatico.

### `review_1m_reference_alignment`

Familia donde el arbitro `1m` cambia la lectura.

Significa:

- `daily` puede parecer razonable;
- la tension aparece al abrir comparabilidad intradia fina.

No significa:

- discrepancia residual simple.

### `bad_data`

Cola dura real.

Subfamilias visuales principales:

- colapso de escala o rango;
- conflicto ralo o sparse;
- mixto estructural/rango;
- integridad estructural.

Regla:

- si la causalidad vive en integridad del tape, el panel de precio no basta;
- debe haber evidencia localizada de `size <= 0`, duplicados o filas invalidas.

## Modelo De Imagenes

Las imagenes de `trades` no son decoracion. Cada imagen debe decir que muestra, que pregunta responde, que no responde y que decision cambia.

### Imagenes Globales

Viven en:

- `evidence_assets/global_universe/`

Imagenes activas:

- `00_acceptance_distribution.png`
- `01_yearly_acceptance_mix.png`
- `02_scale_bucket_mix_by_label.png`
- `03_signature_mix_by_label.png`
- `04_outside_daily_severity_by_label.png`
- `05_outside_1m_severity_by_label.png`
- `06_duplicate_severity_by_label.png`
- `07_odd_lot_severity_by_label.png`
- `08_has_1m_reference_by_label.png`
- `09_review_rehabilitation_waterfall.png`
- `10_bad_data_visual_subfamilies.png`
- `11_review_microstructure_textures.png`
- `12_reference_scale_mismatch_buckets.png`
- `13_review_rehabilitation_categories.png`

Funciones:

- mapa de masa por label;
- persistencia temporal;
- estructura de escala;
- firmas duras;
- severidad frente a `daily`;
- severidad frente a `1m`;
- duplicacion;
- odd-lots;
- cobertura de arbitro `1m`;
- rehabilitacion de `review`;
- subfamilias visuales de `bad_data`;
- texturas dominantes de `review_microstructure`;
- buckets de escala en `reference_scale_mismatch`;
- estructura interna de `review`.

### Imagenes Historicas

Viven en:

- `evidence_assets/historical_assets/`

Incluyen imagenes promovidas desde certification/auditoria, por ejemplo:

- poblacion/agregado;
- `reference_scale_mismatch`;
- `review_microstructure`;
- `review_1m_reference_alignment`;
- `review_no_1m_reference`;
- `bad_data`;
- `good`.

Estas imagenes no deben tratarse como material accesorio. Son parte de la evidencia institucional historica.

### Imagenes De Casepacks Amplios

Viven dentro de:

- `family_case_evidence_packs/<familia>/images/`

Cada caso debe leerse contra su familia semantica y contra el mapa poblacional. Un caso no representa por si solo el universo completo.

## Scripts Relevantes

Scripts de inspeccion:

- `scripts/inspection/trades/trades_case_panel.py`
- `scripts/inspection/trades/trades_universe_panel.py`
- `scripts/inspection/trades/build_trades_stratified_sample_manifests.py`
- `scripts/inspection/trades/export_trades_family_casepacks.py`

Funciones institucionales:

- `trades_case_panel.py`
  - carga casos file-level;
  - dibuja panel raw vs `daily` vs `1m`;
  - muestra conflicto temporal;
  - muestra integridad del tape;
  - explica familia y decision.
- `trades_universe_panel.py`
  - computa snapshot global;
  - renderiza imagenes poblacionales;
  - expone secciones del notebook global.
- `build_trades_stratified_sample_manifests.py`
  - construye manifests reproducibles por familia;
  - evita cherry-picking;
  - estratifica por era, firma y severidad.
- `export_trades_family_casepacks.py`
  - exporta casepacks amplios por familia;
  - genera markdowns e imagenes;
  - añade evidencia estructural en `bad_data` cuando aplica.

## Price Views Y Arbitros

`trades` expone su vista nativa como:

- `trades_raw`

`trades_raw` sirve para:

- ejecucion observada;
- microestructura;
- analisis de prints;
- duplicates;
- odd-lots;
- session structure;
- comparacion contra arbitros declarados.

No sirve por si solo para:

- retorno economico ajustado;
- labels diarios ajustados;
- verdad universal de precio intertemporal.

Toda comparacion debe declarar:

- referencia usada: `daily`, `1m` o ninguna;
- price view: `raw`, `split_normalized`, `adjusted`, `adjusted_proxy`;
- session policy;
- regla de corporate actions si aplica;
- si el resultado es calidad del tape, comparabilidad o consumo operativo.

## Consumo

Estados finales correctos:

- `good`
- `recoverable_with_flag`
- `review_not_rehabilitated`
- `bad`

Uso recomendado:

- `good`
  - benchmark pristine;
  - no usar como proxy de masa util total.
- `recoverable_with_flag`
  - masa principal util para ejecucion/backtest/ML solo si el pipeline consume flags y declara semantica.
- `review_not_rehabilitated`
  - no consumo limpio;
  - investigacion, sensibilidad o futura rehabilitacion.
- `bad`
  - fuera de consumo productivo;
  - `forensic_only`.

Para backtest:

- no usar solo `good` como universo operativo;
- no consumir `reference_scale_mismatch` sin reconciliacion de escala;
- no tratar `review_microstructure` como ruido inocuo si el modelo no sabe que esta leyendo odd-lots/textura;
- no convertir `bad_data` en fills o marks normales.

Para ML:

- no mezclar familias semanticas distintas como una sola nocion de calidad;
- no aprender conflictos de escala como alpha;
- no aprender odd-lots o duplicacion como señal economica si no es el objetivo explicito;
- no usar `trades_raw` como label economico intertemporal.

## Reglas Para Futuros Agentes

Antes de interpretar, ampliar o modificar este dossier, el agente debe leer:

- este `README.md`;
- `build_trades_inspection_pack.md`;
- `trades_inspection_readout_v0_1.md`;
- `trades_global_universe_readout_v0_1.md`;
- `trades_sampling_strategy_v0_1.md`;
- los markdowns principales de cada subcarpeta;
- los manifests de `evidence_assets/stratified_samples/`;
- el indice de `family_case_evidence_packs/`;
- y los contratos de `trades` listados en la seccion de autoridad documental.

Como `trades` no tiene actualmente READMEs locales dentro de cada subfolder, los markdowns principales de cada carpeta actuan como autoridad local. Si en el futuro se añaden READMEs de subcarpeta, deben leerse antes que cualquier casepack individual.

Reglas obligatorias:

- no presentar `good` como masa util total;
- no presentar `outside_daily` u `outside_1m` como `bad tape` automatico;
- no mezclar poblacion, muestra `380`, full closeout `57f` y estados finales;
- no presentar casos file-level sin mapa poblacional;
- no presentar familias como taxonomia muda;
- no reducir `bad_data` a un solo tipo visual;
- no usar panel de precio para probar integridad estructural si el fallo vive en `size <= 0`, duplicados o filas invalidas;
- no usar `reference_scale_mismatch` sin declarar price view y arbitro;
- no consumir `review_microstructure` sin declarar odd-lot/textura;
- no ignorar la falta de arbitro `1m` en `review_no_1m_reference`;
- no reusar counts historicos de `57e` como si fueran cierre `57f`;
- no modificar frontera de consumo sin revisar contratos, policies, validators, manifests y readouts.

Si se cambia una decision operativa, deben revisarse como minimo:

- `trades_inspection_readout_v0_1.md`;
- `trades_global_universe_readout_v0_1.md`;
- `build_trades_inspection_pack.md`;
- `trades_sampling_strategy_v0_1.md`;
- manifests bajo `evidence_assets/stratified_samples/`;
- `family_case_evidence_packs/family_casepacks_index_v0_1.md`;
- `trades_dataset_contract_v0_1.md`;
- `trades_label_taxonomy_and_cut_policy.md`;
- `trades_consumption_policy.md`;
- `trades_validators.md`;
- y el `CHANGELOG.md` del modulo si el cambio altera estado institucional.

## Regla Final

La lectura correcta de `trades` es:

```text
tape raw + arbitro declarado + price view declarada + firma causal + mapa poblacional + estado de consumo
```

Un desacuerdo contra `daily` no es automaticamente corrupcion.

Un conflicto contra `1m` no es automaticamente exclusion dura.

Un `good` diminuto no significa que todo lo demas sea basura.

Un `bad_data` local no invalida todo el dataset.

La amenaza principal para backtest y ML no es la existencia de una cola `bad_data`; es colapsar familias semanticas distintas en una sola nocion de calidad.
