# Quotes Inspection Dossier

## Menu

- [Rol](#rol)
- [Estado Institucional](#estado-institucional)
- [Autoridad Documental](#autoridad-documental)
- [Fuentes Historicas](#fuentes-historicas)
- [Estructura](#estructura)
  - [`good_justification/`](#goodjustification)
  - [`flagged_case_evidence_packs/`](#flaggedcaseevidencepacks)
  - [`bad_case_evidence_packs/`](#badcaseevidencepacks)
  - [`coverage_case_evidence_packs/`](#coveragecaseevidencepacks)
  - [`evidence_assets/`](#evidenceassets)
- [Modelo De Imagenes](#modelo-de-imagenes)
  - [Imagenes Globales](#imagenes-globales)
    - [`01_taxonomy_distribution.png`](#01taxonomydistributionpng)
    - [`02_severity_and_root_mix.png`](#02severityandrootmixpng)
    - [`03_positive_cross_policy.png`](#03positivecrosspolicypng)
    - [`04_integer_and_timestamp_diagnostics.png`](#04integerandtimestampdiagnosticspng)
    - [`05_open_bucket_diagnostics.png`](#05openbucketdiagnosticspng)
  - [Imagenes Por Caso](#imagenes-por-caso)
    - [`00_event_month_context.png`](#00eventmonthcontextpng)
    - [`00a_event_month_adjusted_proxy.png`](#00aeventmonthadjustedproxypng)
    - [`00b_event_month_quotes_context.png`](#00beventmonthquotescontextpng)
    - [`01_raw_window.png`](#01rawwindowpng)
    - [`02_full_session_context.png`](#02fullsessioncontextpng)
    - [`03_structure_diagnostics.png`](#03structurediagnosticspng)
    - [`04_summary_card.png`](#04summarycardpng)
    - [`05_historical_context.png`](#05historicalcontextpng)
- [Taxonomia Y Consumo](#taxonomia-y-consumo)
  - [`good`](#good)
  - [`review`](#review)
  - [`bad`](#bad)
- [Price Views](#price-views)
- [Masa Poblacional Vs Casos Forenses](#masa-poblacional-vs-casos-forenses)
- [Reglas Para Futuros Agentes](#reglas-para-futuros-agentes)
- [Regla Final](#regla-final)


## Rol

Este dossier contiene la lectura humana e institucional del bloque `quotes` del modulo `01_TSIS_backtest_SmallCaps`.

Su funcion no es reemplazar el schema, el dataset contract, la consumption policy ni los validators. Su funcion es mostrar por que la politica vigente sobre `quotes` es defendible a partir de evidencia empirica, visual, tabular y trazable.

La unidad operativa natural del dossier es:

- `ticker`
- `date`
- `quotes.parquet`

Es decir: un `ticker-date-file`.

El eje central de inspeccion es la calidad local del libro observado:

- si existe `bid > ask`;
- si el crossed vive en `ask = 0` o en `ask > 0`;
- si la magnitud economica del crossed es leve, moderada o severa;
- si hay persistencia intradiaria o mensual;
- si hay timestamp drift, rollover UTC o integerization;
- y si existe contexto externo que explique el episodio.

La regla institucional mas importante es:

> El contexto externo puede explicar un episodio, pero no rehabilita automaticamente la calidad local del libro.

## Estado Institucional

El cierre principal del bloque vive en:

- `quotes_inspection_readout_v0_1.md`

Ese readout sintetiza la evidencia poblacional, la taxonomia, los casos forenses y la politica final de consumo.

La auditoria de trazabilidad de los casepacks abiertos vive en:

- `quotes_open_casepacks_audit_v0_1.md`

Ese documento comprueba que la frontera final `review` y `bad` no se construyo ad hoc: valida correspondencia entre `build_quotes_case_pool()`, manifests, documentos markdown, menus y assets fisicos.

La guia de construccion del pack vive en:

- `build_quotes_inspection_pack.md`

Ese documento describe como debia construirse el dossier, que fuentes historicas podian usarse y que no debia inventarse durante la traduccion institucional.

No hay notebooks dentro de esta carpeta raiz de `quotes`. Los notebooks relevantes viven fuera, principalmente en `01_research`, y esta carpeta encapsula sus conclusiones en markdown, manifests e imagenes persistidas.

## Autoridad Documental

Este dossier debe leerse junto con los documentos de autoridad de `01_foundations`.

Contratos especificos de `quotes`:

- `01_foundations/contract_registry/dataset_contracts/quotes_dataset_contract_v0_1.md`
- `01_foundations/contract_registry/dataset_contracts/quotes_label_taxonomy_and_cut_policy.md`
- `01_foundations/canonical_schemas/quotes/quotes_schema_contract.md`
- `01_foundations/data_consumption_policies/quotes_consumption_policy.md`
- `01_foundations/dataset_registry/quotes/quotes_registry_entry.yaml`
- `01_foundations/validators/quotes/quotes_validators.md`

Contratos transversales que gobiernan la lectura del dossier:

- `01_foundations/module_contracts/inspection_dossier_model.md`
- `01_foundations/module_contracts/evidence_model.md`
- `01_foundations/module_contracts/bad_evidence_and_rehabilitation.md`
- `01_foundations/module_contracts/policy_explanation_standard.md`
- `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`
- `01_foundations/module_contracts/external_price_comparison_caveats.md`
- `01_foundations/module_contracts/price_views_registry.md`
- `01_foundations/module_contracts/corporate_actions_adjustment_methodology.md`
- `01_foundations/module_contracts/event_families_and_reference_inventory.md`

Indices y explicaciones relacionados:

- `01_foundations/module_contracts/quotes_contracts_index.md`
- `01_foundations/module_contracts/quotes_acceptance_policy_explained.md`
- `01_foundations/module_contracts/quotes_rules_explained_line_by_line.md`

## Fuentes Historicas

El dossier actual traduce e institucionaliza trabajo historico de auditoria y certificacion.

Fuentes principales de auditoria `quotes/v2`:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/quotes/v2/04_quotes_full_C_D_methodology.ipynb`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/quotes/v2/04_quotes_full_C_D_methodology.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/quotes/v2/04_quotes_full_C_D_closeout.ipynb`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/quotes/v2/04_quotes_full_C_D_closeout.md`

Estas fuentes fijan:

- el alcance `quotes C+D <1B`;
- la taxonomia final refinada;
- la separacion entre `ask = 0` y `ask > 0`;
- la medicion economica del crossed en bps;
- los buckets abiertos;
- y la politica final `good / review / bad`.

Fuentes historicas de certificacion:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/03_quotes_quality_policy.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/04_quotes_usage_policy.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/12_quotes_open_buckets_synthesis.md`

Estas fuentes confirman la traduccion de buckets a consumo:

- `good`: apto para uso principal;
- `review`: uso condicionado y siempre identificado;
- `bad`: fuera del uso core.

Fuentes de lineage y task builder:

- `01_research/01_auditoria_RAW_DATA/00_data_quotes/quotes/01_universe_lineage_quotes.ipynb`
- `01_research/01_auditoria_RAW_DATA/00_data_quotes/quotes/02_task_builder_contract_quotes.ipynb`

Estas fuentes explican la genealogia del universo y el contrato esperado para construccion de tareas.

Fuentes de coverage historico:

- `01_research/01_auditoria_RAW_DATA/02_backtest/000_quotes_coverage_official_lifecycle.ipynb`
- `01_research/01_auditoria_RAW_DATA/02_backtest/00_quotes_coverage_radiography.ipynb`

Estas fuentes son contexto historico de cobertura. No son el eje principal del dossier visual actual, porque en `quotes` el cierre vigente se centra en calidad local del libro, crossed behavior y consumo por estado.

## Estructura

La carpeta sigue el modelo institucional de `inspection_dossiers/`.

```text
inspection_dossiers/quotes/
  README.md
  build_quotes_inspection_pack.md
  quotes_inspection_readout_v0_1.md
  quotes_open_casepacks_audit_v0_1.md
  good_justification/
  flagged_case_evidence_packs/
  bad_case_evidence_packs/
  coverage_case_evidence_packs/
  evidence_assets/
```

### `good_justification/`

Contiene la justificacion positiva de una muestra representativa de `good`.

El documento principal es:

- `good_justification/quotes_good_cases_v0_1.md`

No enumera todo el universo bueno. Selecciona ejemplos representativos para mostrar como se ve:

- un libro sano;
- un residuo `soft_crossed_micro_noise` aceptable;
- un `persistent_soft_crossed_low` compatible con consumo principal;
- y un caso de rollover UTC limpio.

### `flagged_case_evidence_packs/`

Contiene los casos `review`.

El documento principal es:

- `flagged_case_evidence_packs/quotes_review_cases_v0_1.md`

`review` significa que ya existe contradiccion economica real o fragilidad del libro, pero no necesariamente exclusion dura.

Un caso `review`:

- no debe tratarse como `good`;
- no debe usarse como ejecucion limpia;
- puede conservarse para analisis contextual, sensibilidad o investigacion;
- debe mantener su condicion de calidad cuando sea consumido.

### `bad_case_evidence_packs/`

Contiene los casos `bad`.

El documento principal es:

- `bad_case_evidence_packs/quotes_bad_cases_v0_1.md`

`bad` significa que el libro local queda fuera del consumo core.

Un caso `bad` no invalida al proveedor global ni al dataset completo. Invalida esa unidad o familia para usos que requieren libro economicamente creible.

### `coverage_case_evidence_packs/`

Carpeta reservada para casos donde el eje principal sea coverage, presencia esperada, missing data o completitud.

En el cierre actual de `quotes`, coverage no es el eje principal del dossier. La carpeta existe por homogeneidad con el modelo general de `inspection_dossiers/` y para futuras extensiones si la certificacion de quotes lo requiere.

### `evidence_assets/`

Contiene imagenes, manifests, tablas auxiliares y assets persistidos usados por los documentos institucionales.

Assets activos relevantes:

- `evidence_assets/global_policy/quotes_global_policy_manifest.csv`
- `evidence_assets/good_sample/quotes_good_case_packs_manifest.csv`
- `evidence_assets/review/quotes_review_case_packs_manifest.csv`
- `evidence_assets/bad/quotes_bad_case_packs_manifest.csv`
- `evidence_assets/open_casepacks_audit/quotes_open_casepacks_audit_summary.csv`
- `evidence_assets/open_casepacks_audit/quotes_open_casepacks_audit_summary.parquet`

La regla local de `evidence_assets/README.md` aplica siempre:

- no deben coexistir assets viejos y nuevos cumpliendo el mismo rol activo;
- si un asset deja de estar en uso y no conserva valor historico, debe eliminarse;
- si conserva valor historico, debe archivarse y anotarse explicitamente.

## Modelo De Imagenes

Las imagenes de este dossier no son decoracion. Cada imagen debe responder una pregunta concreta, declarar que prueba, que no prueba y que consecuencia tiene para la decision.

La regla contractual viene de:

- `01_foundations/module_contracts/inspection_dossier_model.md`
- `01_foundations/module_contracts/policy_explanation_standard.md`

La forma minima esperada es:

- que muestra;
- que responde;
- que no responde;
- consecuencia institucional.

### Imagenes Globales

Las imagenes globales viven en:

- `evidence_assets/global_policy/`

#### `01_taxonomy_distribution.png`

Muestra la distribucion poblacional de taxonomias.

Sirve para separar masa global de casos forenses. La conclusion clave es que el universo no esta dominado por corrupcion masiva: las familias limpias o de micro-ruido concentran la mayor parte.

#### `02_severity_and_root_mix.png`

Muestra la mezcla `PASS / SOFT_FAIL / HARD_FAIL` y el reparto por root.

Sirve para evitar que `severity` se lea como veredicto final sin contexto. `HARD_FAIL` es una alarma tecnica; la decision institucional requiere taxonomia, severidad economica y lectura forense.

#### `03_positive_cross_policy.png`

Separa el crossed positivo por regimen economico:

- `mild <5 bps`;
- `moderate 5-25 bps`;
- `severe >=25 bps`;
- `ask = 0`;
- `ask > 0`.

Sirve para no tratar todo crossed igual.

#### `04_integer_and_timestamp_diagnostics.png`

Muestra integerization y timestamp/UTC rollover.

Sirve para separar problemas estructurales o temporales de crossed economicamente material.

#### `05_open_bucket_diagnostics.png`

Muestra los buckets abiertos que requieren decision final.

Conecta poblacion, taxonomia y casos forenses para las familias `review` y `bad`.

### Imagenes Por Caso

Cada casepack puede contener una secuencia de paneles.

#### `00_event_month_context.png`

Pregunta: el episodio es local o forma parte de un contexto temporal mas amplio.

Muestra el evento frente a la serie diaria real del mes y compara el dia con vecinos mediante `crossed_ratio_pct` y `max_gap_bps_pos`.

#### `00a_event_month_adjusted_proxy.png`

Pregunta: una discrepancia de precios es fallo de datos o diferencia de price view.

Compara:

- `daily raw`;
- `daily adjusted_proxy`;
- `quote mid raw`;
- `quote mid split_normalized`;
- cadena de dividendos;
- cadena de splits.

Este panel existe para evitar falsas incidencias por mezclar `raw`, `split_normalized`, `adjusted` y `adjusted_proxy`.

#### `00b_event_month_quotes_context.png`

Pregunta: el problema reaparece dentro de `quotes` durante el mes o se concentra en una sola sesion.

Muestra sesiones disponibles de quotes, cobertura diaria, `crossed_ratio_pct` y `max_gap_bps_pos`.

#### `01_raw_window.png`

Pregunta: cual es la geometria local del crossed.

Muestra el tramo del libro donde aparece la contradiccion `bid > ask > 0` y convierte el gap a bps contra cortes economicos.

Este panel suele ser decisivo para separar:

- residuo leve;
- `review`;
- exclusion dura.

#### `02_full_session_context.png`

Pregunta: el crossed es un evento puntual o contamina la sesion completa.

Muestra el comportamiento intradiario extendido dentro del rango de sesion usado por el proyecto.

#### `03_structure_diagnostics.png`

Pregunta: el fallo es contradiccion economica genuina, degeneracion estructural o mezcla.

Separa:

- crossed total;
- `ask = 0`;
- `ask > 0`;
- distribucion de `gap_bps`;
- integerization;
- patrones estructurales.

#### `04_summary_card.png`

Pregunta: que variables sostienen la decision.

Resume, como minimo:

- `severity`;
- `root`;
- `crossed_ratio_pct`;
- `ask_integer_pct`;
- `median_bps_ask_positive`;
- `p90_bps_ask_positive`;
- filas crossed por composicion.

Este panel convierte la lectura visual en decision auditable.

#### `05_historical_context.png`

Pregunta: existe contexto externo historico que explique el episodio.

Puede incorporar contexto de halts, eventos conocidos, referencia o certificacion historica.

Su uso no rehabilita automaticamente el caso.

## Taxonomia Y Consumo

La taxonomia final debe leerse segun:

- `quotes_label_taxonomy_and_cut_policy.md`
- `quotes_consumption_policy.md`
- `quotes_validators.md`

### `good`

Familias tipicas:

- `clean_pass_or_other`
- `soft_crossed_micro_noise`
- `persistent_soft_crossed_low`
- `utc_rollover_large_day_clean`

Uso:

- consumo principal permitido;
- apto para baseline limpio;
- no requiere bandera dura;
- puede conservar notas si hay residuo leve.

### `review`

Familias tipicas:

- `persistent_soft_crossed_mid_large_scale`
- `large_file_threshold_edge_hard_many_crosses`

Uso:

- consumo condicionado;
- sensibilidad;
- analisis contextual;
- investigacion forense;
- no ejecucion limpia;
- no debe presentarse como equivalente a `good`.

### `bad`

Familias tipicas:

- `medium_file_threshold_edge_hard_many_crosses`
- `high_hard_crossed_10_to_20`

Uso:

- fuera del consumo core;
- `forensic_only`;
- no train principal de ML;
- no simulacion de ejecucion como si el libro fuera normal;
- no mark-to-market intradiario como libro creible.

## Price Views

`quotes` es una vista raw del libro observado.

No debe asumirse que `quotes_raw`, `daily_raw`, `split_normalized`, `adjusted` y `adjusted_proxy` vivan en la misma escala.

Cuando un casepack compare precios, debe declarar la vista usada.

La jerarquia y reglas viven en:

- `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`
- `01_foundations/module_contracts/price_views_registry.md`
- `01_foundations/module_contracts/corporate_actions_adjustment_methodology.md`
- `01_foundations/module_contracts/external_price_comparison_caveats.md`

Regla practica:

- `quotes_raw` y `trades_raw` sirven para microestructura y ejecucion observada;
- `daily_raw` sirve para observacion diaria raw;
- `split_normalized` sirve para reconciliar escalas de split;
- `adjusted` sirve para retornos economicamente comparables;
- `adjusted_proxy` es una capa de inspeccion o contraste, no la vista final.

Para backtest y ML, mezclar vistas sin declararlas introduce labels espurios, leakage conceptual y falsas incidencias de calidad.

## Masa Poblacional Vs Casos Forenses

Este dossier distingue siempre:

- masa poblacional;
- taxonomia;
- casos forenses;
- consumo operativo.

La masa poblacional dice cuanto pesa cada familia.

La taxonomia dice que tipo de anomalia representa.

El caso forense muestra si la decision es visual, economica y contextualmente defendible.

La consumption policy dice como puede usarse.

No debe inferirse una decision de consumo solo desde una imagen aislada ni solo desde un porcentaje agregado.

## Reglas Para Futuros Agentes

Antes de interpretar, ampliar o modificar este dossier, el agente debe leer:

- este `README.md`;
- `good_justification/README.md`;
- `flagged_case_evidence_packs/README.md`;
- `bad_case_evidence_packs/README.md`;
- `coverage_case_evidence_packs/README.md`;
- `evidence_assets/README.md`.

Los README locales no son decoracion. Son la capa que explica el rol de cada carpeta y evita mezclar `good`, `review`, `bad`, coverage y assets como si fueran equivalentes.

Reglas obligatorias:

- no anadir imagenes sin manifest;
- no anadir imagenes sin interpretacion textual;
- no usar una imagen como decoracion muda;
- no decidir solo por nombre de bucket;
- no confundir masa poblacional con caso forense;
- no usar contexto externo como rehabilitacion automatica;
- no mezclar `raw`, `split_normalized`, `adjusted` y `adjusted_proxy` sin declararlo;
- no convertir `review` en `good` por conveniencia de consumo;
- no consumir `bad` en pipelines core;
- no borrar evidencia historica util sin archivarla y documentarlo;
- no modificar la frontera `good / review / bad` sin revisar contratos, policies, validators, manifests y readout.

Si se cambia una decision operativa, deben revisarse como minimo:

- `quotes_inspection_readout_v0_1.md`;
- `quotes_open_casepacks_audit_v0_1.md`;
- manifests bajo `evidence_assets/`;
- `quotes_dataset_contract_v0_1.md`;
- `quotes_label_taxonomy_and_cut_policy.md`;
- `quotes_consumption_policy.md`;
- `quotes_validators.md`;
- y el `CHANGELOG.md` del modulo si el cambio altera estado institucional.

## Regla Final

Este dossier existe para que `quotes` pueda usarse con rigor, no con memoria conversacional.

La lectura correcta de `quotes` es:

```text
libro observado + taxonomia + severidad economica + lectura visual real + contexto separado + consumo declarado
```

Un caso explicado no es automaticamente un caso limpio.

Un crossed leve no es automaticamente corrupcion.

Un `bad` local no invalida todo el dataset.

La decision defendible sale de la combinacion trazable de evidencia, contratos y lectura visual real.
