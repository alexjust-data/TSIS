# Changelog del Modulo 01

Este changelog registra cambios institucionales y semanticamente relevantes para:

- `01_TSIS_backtest_SmallCaps`

No duplica el historial de Git.
Existe para preservar memoria arquitectonica y metodologica del modulo.

## v0.4.30 - transversal layer validation standard

### Added

- `01_foundations/module_contracts/layer_validation_standard_v0_1.md`

### Notes

This standard closes a missing transversal governance piece:

- when a new layer may be considered semantically validated;
- what minimum checks it must pass before being called well-built;
- and how to avoid treating "the script ran" or "a few examples looked fine" as sufficient evidence.

The standard fixes seven required validation dimensions:

- semantic validation;
- implementation validation;
- negative controls;
- visual or inspective validation;
- real consumer validation;
- reproducibility;
- and documentary traceability.

It also introduces maturity levels so new layers can be described as:

- defined;
- implemented;
- piloted;
- audited;
- consumed;
- or promoted.

## v0.4.31 - first explicit maturity assessment for core derived layers

### Added

- `01_foundations/module_contracts/layer_maturity_assessment_v0_1.md`

### Notes

This document applies the new transversal validation standard to three active layers:

- `daily_adjusted`
- `ohlcv_1m_split_normalized`
- `intraday_regime_features`

The resulting classification is:

- `daily_adjusted` -> `Nivel 5 - Consumida`
- `ohlcv_1m_split_normalized` -> `Nivel 4 - Auditada`
- `intraday_regime_features` -> `Nivel 1 - Definida`

This makes the current architectural sequence explicit and removes the need to infer maturity from scattered pilots, readouts, and contracts.

## v0.4.32 - first executable landing of `intraday_regime_features`

### Added

- `scripts/materialize_intraday_regime_features.py`
- `01_foundations/module_contracts/intraday_regime_features_initial_materialization_results_v0_1.md`

### Notes

This is the first real executable landing of the first proposed consumer of `ohlcv_1m_split_normalized`.

The materializer now reads:

- `D:\\ohlcv_1m`
- `E:\\TSIS\\data\\ohlcv_1m_split_normalized`

and writes:

- `E:\\TSIS\\data\\intraday_regime_features`

at `ticker-day` grain.

Its first promoted feature families are now explicit in code:

- cross-session regime features computed from `1m_split_normalized`
- local intrasesion features computed from `1m raw`

This moves `intraday_regime_features` from:

- `Nivel 1 - Definida`

to:

- `Nivel 2 - Implementada`

while still leaving semantic pilot and downstream validation as the next required step before calling the layer fully piloted or consumed.

## v0.4.33 - semantic pilot and audit readout for `intraday_regime_features`

### Added

- `scripts/inspection/minute/export_intraday_regime_features_pilot_readout.py`
- `01_foundations/inspection_dossiers/intraday_regime_features/intraday_regime_features_semantic_pilot_readout_v0_1.md`
- `01_foundations/module_contracts/intraday_regime_features_semantic_pilot_results_v0_1.md`

### Notes

This closes the first semantic pilot of the first real consumer of `ohlcv_1m_split_normalized`.

The readout now compares, case by case, the same cross-session features computed:

- with `1m raw` as a counterfactual
- versus `1m_split_normalized` as the contractual view

The result is now explicit:

- strong reverse-split months show massive false-gap contamination under raw;
- several forward-split months also show materially wrong cross-session readings under raw;
- and controls remain neutral, including the important case where `future_split_factor != 1` but all compared days still live in the same relative scale regime.

This promotes:

- `intraday_regime_features` from `Nivel 2 - Implementada` to `Nivel 3 - Pilotada`
- `ohlcv_1m_split_normalized` from `Nivel 4 - Auditada` to `Nivel 5 - Consumida`

## v0.4.34 - explicit separation between data-audit consumer and deferred feature-engineering backlog

### Added

- `01_foundations/module_contracts/intraday_regime_features_deferred_families_v0_1.md`

### Notes

This update makes a critical phase boundary explicit:

- `intraday_regime_features v0_1` remains a minimal semantic-validation consumer for `1m_split_normalized`;
- it is not yet the start of broad strategy feature engineering or alpha research.

The richer families around:

- premarket context;
- opening/first-hour behavior;
- richer multi-session extension;
- intraday volume profile;
- session range position;
- and contextual compression/expansion

are now preserved as deferred backlog in the correct place, without polluting the current data-audit phase.

## v0.4.35 - navigation layer for `module_contracts` before any physical migration

### Added

- `01_foundations/module_contracts/README.md`
- `01_foundations/module_contracts/daily_contracts_index.md`
- `01_foundations/module_contracts/quotes_contracts_index.md`
- `01_foundations/module_contracts/trades_contracts_index.md`
- `01_foundations/module_contracts/1m_contracts_index.md`
- `01_foundations/module_contracts/transversal_contracts_index.md`

### Notes

This update does **not** move any contract yet.

It introduces a navigation layer first, while explicitly marking physical reorganization as pending work that must avoid:

- broken references;
- orphaned links in readouts and notebooks;
- and silent path drift for humans and agents.

## v0.4.36 - final inspector package for `ohlcv_1m_split_normalized`

### Added

- `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_final_readout_v0_1.md`
- `scripts/inspection/minute/build_1m_split_normalized_inspection_notebook.py`
- `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_inspection_notebook_v0_1.ipynb`

### Notes

This closes the inspector-facing package for `ohlcv_1m_split_normalized` by unifying:

- contractual semantics;
- the price-layer pilot;
- the downstream minimal consumer pilot;
- and a final inspector readout with an executed notebook saved with outputs.

The package now supports both:

- markdown-first institutional review;
- and notebook-first visual supervision without requiring the inspector to recompute the whole chain manually.

## v0.4.37 - exhaustive full-universe split audit for `1m`

### Added

- `scripts/inspection/minute/audit_1m_split_full_universe.py`
- `scripts/inspection/minute/build_1m_split_full_universe_audit_notebook.py`
- `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md`
- `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_notebook_v0_1.ipynb`

### Notes

This closes the open debt around "proving all split cases" at the strongest level allowed by the actual `1m` coverage.

The exhaustive audit now covers:

- `3335` split-event cases intersected with real `1m` availability

with results:

- `PASS = 2280`
- `FAIL = 0`
- `NO_PRE_COVERAGE = 164`
- `NO_POST_COVERAGE = 151`
- `NO_1M_COVERAGE = 740`

The key institutional conclusion is now explicit:

- **100% of fully auditable cases pass**
- and the remaining non-pass statuses are classified as coverage limits, not semantic failures.

The new notebook gives the inspector a live selector over the full audited universe instead of a fixed sample of PNGs.

## v0.4.15 - repaso transversal final de `01_foundations`

### Added

- `01_foundations/module_contracts/foundations_transversal_final_review_v0_1.md`

### Notes

This review consolidates the current institutional status of the module and separates three layers:

- what is already effectively closed;
- what remains as real methodological debt;
- and what is only cosmetic or asymmetry-of-finish debt.

The main open items left explicit are:

- full downstream integration of `split_normalized`;
- extension of `adjusted` to more complex corporate actions;
- and a final upgrade of `quotes` toward the same global analytic standard already reached by `trades`.

The review was also explicitly marked as a **state snapshot**, not a live primary policy.

It now includes review triggers so it does not silently become stale if:

- `price views` are promoted to real consumers;
- complex downstream consumers are contracted;
- or the module changes phase materially.

## v0.4.16 - transversal standard for institutional state snapshots

### Added

- `01_foundations/module_contracts/state_snapshot_standard.md`

### Notes

This standard fixes how state-review artifacts must be treated:

- as versioned state snapshots;
- not as live primary policies;
- and with explicit review/versioning triggers so they do not become silently stale.

## v0.4.17 - priority plan for real `price view` integration

### Added

- `01_foundations/module_contracts/price_view_consumer_integration_status.md`
- `01_foundations/module_contracts/price_view_integration_priority_plan_v0_1.md`

### Notes

This closes the architectural decision behind transversal priority 1:

- the first real downstream promotion should be `daily_adjusted`;
- then a reusable mass-reconciliation layer around `split_normalized`;
- and only after that should higher-threshold consumers like `execution_simulator`, `rl_allowed`, or `live_downstream_candidate` be opened.

## v0.4.18 - first `daily_adjusted` materializer scaffolded and smoke-tested

### Added

- `scripts/materialize_daily_adjusted.py`
- `01_foundations/contract_registry/dataset_contracts/daily_adjusted_dataset_contract_v0_1.md`
- `01_foundations/canonical_schemas/daily/daily_adjusted_schema_contract.md`

### Notes

This is the first executable landing of transversal priority 1.

It does not yet mean full production promotion.

It means:

- `daily_adjusted` now has a real materialization path;
- the layer has a first explicit contract and schema;
- and a smoke test over `ticker=A` succeeded with temporary output under `C:\\tmp\\daily_adjusted_smoke`.

## v0.4.19 - official landing proposal and pilot registry for `daily_adjusted`

### Added

- `01_foundations/module_contracts/daily_adjusted_operational_landing_v0_1.md`
- `01_foundations/dataset_registry/daily/daily_adjusted_registry_entry.yaml`

### Notes

This fixes the first concrete operational proposal for `daily_adjusted`:

- canonical root: `E:\\TSIS\\data\\ohlcv_daily_adjusted`
- mirrored physical layout from `D:\\ohlcv_daily`
- incremental materialization strategy with provenance
- first pilot consumer: daily return labels
- second target: `backtest_core`

The same update also makes explicit that:

- `daily_adjusted` closes the slow economic truth layer;
- the project core remains intraday and raw-observed;
- and a later `1m_split_normalized` discipline will be required so intraday ML/backtests do not learn split/reverse-split jumps as false alpha.

## v0.4.20 - exact incremental promotion plan for `daily_adjusted`

### Added

- `01_foundations/module_contracts/daily_adjusted_incremental_materialization_plan_v0_1.md`

### Notes

This fixes the concrete step order for promoting `daily_adjusted`:

- smoke test
- semantic pilot on real corporate-action tickers
- first real consumer
- incremental expansion
- and only after that, possible full-universe promotion

## v0.4.21 - first explicit semantic pilot manifest for `daily_adjusted`

### Added

- `01_foundations/dataset_registry/daily/daily_adjusted_pilot_manifest_v0_1.csv`
- `01_foundations/module_contracts/daily_adjusted_pilot_manifest_v0_1.md`

### Notes

The pilot is not random.

It explicitly mixes:

- reverse splits
- split-plus-dividend cases
- dividend-only cases
- and a no-event control

so the first semantic validation can check both:

- that the adjusted layer changes when it should;
- and that it stays neutral where no corporate action exists.

## v0.4.22 - refined pilot validated and first real consumer defined for `daily_adjusted`

### Added

- `01_foundations/module_contracts/daily_adjusted_pilot_results_v0_2.md`
- `01_foundations/module_contracts/daily_return_labels_consumer_contract_v0_1.md`
- `01_foundations/dataset_registry/daily/daily_adjusted_pilot_manifest_v0_2.csv`

### Notes

The refined semantic pilot `v0_2` is now explicitly recorded as validated.

This also fixes the first concrete downstream target for `daily_adjusted`:

- daily return labels built from `c_adjusted`

with initial horizons:

- `ret_1d`
- `ret_3d`
- `ret_5d`

## v0.4.12 - `bad_data` marks `size<=0` directly in the top panel

### Changed

- `scripts/inspection/trades/trades_case_panel.py`
- regenerated:
  - `01_foundations/inspection_dossiers/trades/family_case_evidence_packs/bad_data/bad_data_cases_v0_1.md`

### Notes

Cases with:

- `size <= 0`

are now marked directly in the top price panel with a red `X`.

This complements the structural-integrity panel and makes the invalid trade row visually locatable inside the tape.

## v0.4.13 - `bad_data` gains universe map and exact invalid-row evidence

### Changed

- `scripts/inspection/trades/export_trades_family_casepacks.py`
- `01_foundations/inspection_dossiers/trades/build_trades_inspection_pack.md`
- regenerated:
  - `01_foundations/inspection_dossiers/trades/family_case_evidence_packs/bad_data/bad_data_cases_v0_1.md`

### Notes

`bad_data` now starts with two universe-level layers:

- full `57f` acceptance distribution
- internal `bad_data` hard-signature distribution

and structural-integrity cases now expose exact evidence, not just aggregate warnings:

- invalid rows with:
  - `timestamp`
  - `price`
  - `size`
  - `exchange`
  - `conditions`
- duplicate groups with exact `timestamp/price/size`

This closes the gap identified in cases like `WSBF`, where price looked almost normal but the real rejection cause lived in tape integrity rather than visible price geometry.

## v0.4.14 - `trades` gets full-universe inspection notebook and global metrics module

### Added

- `scripts/inspection/trades/trades_universe_panel.py`
- `01_foundations/inspection_dossiers/trades/trades_universe_inspection_notebook_v0_1.ipynb`

### Notes

This adds a second interactive layer for `trades`, complementary to the existing case-level notebook.

The new layer is population-first and works over the full `57f/full_clean_fast_same_schema` universe.

It exports and displays, inline in the notebook:

- final acceptance distribution
- yearly acceptance mix
- scale-bucket mix by label
- hard-signature mix by label
- outside-daily severity by label
- outside-1m severity by label
- duplicate severity by label
- odd-lot severity by label
- 1m-reference coverage by label
- review rehabilitation waterfall

This closes a previous weakness: inspectors could see many cases, but they still lacked a modern, ambitious, executable map of the entire `trades` universe.

## v0.4.15 - `trades` global notebook executed and scope clarified

### Changed

- `01_foundations/inspection_dossiers/trades/trades_universe_inspection_notebook_v0_1.ipynb`

### Notes

The notebook was executed and saved with embedded outputs.

Its scope is now stated explicitly inside the notebook:

- it runs on the `lt1b` universe
- materialized in `57f/full_clean_fast_same_schema`

This avoids a dangerous ambiguity between:

- the audited `lt1b` production universe
- and a hypothetical all-cap universe outside this certification scope

## v0.4.16 - `trades` global readout and fine-grained universe cuts

### Added

- `01_foundations/inspection_dossiers/trades/trades_global_universe_readout_v0_1.md`

### Changed

- `scripts/inspection/trades/trades_universe_panel.py`
- `01_foundations/inspection_dossiers/trades/trades_universe_inspection_notebook_v0_1.ipynb`

### Notes

The global `trades` universe layer is no longer only a coarse summary.

It now includes fine-grained cuts for:

- `bad_data` by visual subfamily
- `review_microstructure` by dominant texture
- `reference_scale_mismatch` by scale bucket
- `review` by internal rehabilitation severity

The notebook was re-executed so these new sections remain embedded with outputs.

This closes another weakness:

- inspectors can now move from the full-universe map
- to fine-grained population structure
- before they drop into file-level casepacks.

## v0.4.9 - `trades` rules explained line by line

### Added

- companion compacto de reglas:
  - `01_foundations/module_contracts/trades_rules_explained_line_by_line.md`

### Notes

Este documento reescribe la policy de `trades` como:

- una regla por linea,
- agrupada por secciones,
- con formulas y cortes cuando existen.

Su funcion es ayudar a inspectores y agentes cuando necesiten:

- ver todas las reglas de `trades` de una vez,
- sin perder los cortes cuantitativos,
- y sin depender de una explicacion larga en prosa.

## v0.4.10 - `daily` and `quotes` explanatory companions

### Added

- `01_foundations/module_contracts/daily_acceptance_policy_explained.md`
- `01_foundations/module_contracts/daily_rules_explained_line_by_line.md`
- `01_foundations/module_contracts/quotes_acceptance_policy_explained.md`
- `01_foundations/module_contracts/quotes_rules_explained_line_by_line.md`

### Notes

This closes the symmetry with `trades`.

From now on, the three main audited families:

- `daily`
- `quotes`
- `trades`

have:

- a formal policy layer,
- an explanatory companion,
- and a compact line-by-line rule inventory.

## v0.4.11 - Transversal policy symmetry closed

### Added

- `01_foundations/module_contracts/pipeline_price_view_policy_explained.md`
- `01_foundations/module_contracts/pipeline_price_view_rules_line_by_line.md`
- `01_foundations/module_contracts/price_semantics_rules_line_by_line.md`
- `01_foundations/module_contracts/external_price_comparison_rules_line_by_line.md`

### Notes

This closes the institutional symmetry of the main transversal policies.

The module now has, across both dataset-level and transversal policies:

- a formal layer
- an explanatory layer where needed
- and a compact line-by-line rule inventory for fast inspection

## v0.4.8 - Policy explanation standard

### Added

- nuevo estandar transversal:
  - `01_foundations/module_contracts/policy_explanation_standard.md`
- primer companion explicativo especifico de politica de aceptacion:
  - `01_foundations/module_contracts/trades_acceptance_policy_explained.md`

### Notes

Este hito institucionaliza una regla general:

- una policy formal no basta por si sola;
- toda policy operativa importante debe tener una capa explicativa que diga:
  - que significa cada estado;
  - que pregunta responde;
  - que pregunta no responde;
  - que error metodologico evita;
  - y que consecuencia operativa tiene.

Tambien deja enlazada esa regla desde:

- `inspection_dossier_model.md`
- `trades_label_taxonomy_and_cut_policy.md`
- `trades_consumption_policy.md`
- `README.md`
- `AGENTS.md`

## v0.4.7 - Quotes cerrado con lectura poblacional y muestra good representativa

### Added

- cierre institucional de `quotes` mediante:
  - `01_foundations/inspection_dossiers/quotes/good_justification/quotes_good_cases_v0_1.md`
  - `01_foundations/inspection_dossiers/quotes/quotes_inspection_readout_v0_1.md`
- activacion completa del scope `good` en:
  - `scripts/inspection/quotes/quotes_case_panel.py`
- evidencia poblacional global regenerada en:
  - `01_foundations/inspection_dossiers/quotes/evidence_assets/global_policy/`

### Notes

Este hito deja `quotes` cerrado en dos planos separados y obligatorios:

- evidencia poblacional global del universo auditado;
- evidencia forense de las familias abiertas `review` y `bad`.

Tambien deja explicitamente declarado que:

- la bolsa `review + bad` traslada exactamente los `79` casos abiertos del historico `v2`;
- la franja `good` no se documenta como enumeracion exhaustiva del universo bueno;
- se documenta como muestra historica representativa para justificar las familias buenas principales.

## v0.4.6 - Policy transversal por pipeline para price views

### Added

- policy transversal de asignacion de vistas de precio por pipeline/departamento:
  - `01_foundations/module_contracts/pipeline_price_view_policy.md`

### Notes

Este hito aterriza la semantica de precio en reglas operativas concretas para:

- vendor audit y forensic reconciliation
- execution research
- signal research diario
- portfolio valuation
- ML microestructural
- ML daily / labels de retorno
- comparacion con plataformas externas

Ademas deja enlazada esa policy desde:

- `daily_dataset_contract_v0_1.md`
- `quotes_dataset_contract_v0_1.md`
- `daily_consumption_policy.md`
- `quotes_consumption_policy.md`

## v0.4.5 - Vista adjusted reusable institucionalizada

### Added

- primera implementacion reusable de la vista `adjusted` en:
  - `src/data/price_views.py`
- nuevo test de secuencia metodologica:
  - `tests/test_price_views.py`
- export publico de `apply_adjusted_view` en:
  - `src/data/__init__.py`

### Notes

Este hito cierra la primera version reusable de la secuencia institucional correcta:

- `raw`
- `split_normalized`
- `adjusted`

La implementacion actual de `adjusted`:

- primero normaliza por splits;
- despues aplica la cadena futura de dividendos sobre esa base ya split-normalized;
- y deja `adjusted_proxy` como capa diagnostica separada, no como sustituto de `adjusted`.

Queda explicitamente documentado que:

- la vista `adjusted` ya existe y es reusable;
- pero su alcance actual cubre la primera capa institucional seria del modulo, no una reproduccion total de todas las cadenas vendor-specific posibles;
- la extension futura a stock dividends, spin-offs u otros eventos complejos sigue pendiente.

## v0.4.4 - Primera implementacion reusable de price views

### Added

- primera capa reusable de price views en:
  - `src/data/price_views.py`
- tests iniciales de price views en:
  - `tests/test_price_views.py`

### Notes

Este hito no cierra aun la vista `adjusted` institucional final.

Si deja materializado por primera vez, fuera del dossier de `quotes`, una implementacion reusable de:

- `split_normalized`
- `adjusted_proxy`

La motivacion fue evitar que la semantica de corporate actions quedara atrapada dentro de scripts de inspeccion locales.

Ademas, se deja explicitamente anotado un matiz de lectura importante de `quotes`:

- los `15 bad` y `64 review` de los dossiers actuales no representan todos los `HARD_FAIL` del universo;
- representan solo los casos abiertos y representativos que el flujo historico `v2` llevo al inspector final;
- el universo total auditado sigue conteniendo una masa mucho mayor de `PASS`, `SOFT_FAIL` y `HARD_FAIL`, ya resumida en los artefactos historicos de severidad y taxonomia.

## v0.4.2 - Politica transversal de semantica de precio y ajustes

### Added

- politica transversal institucional de vistas de precio:
  - `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`
- refuerzo bibliografico e institucional de la politica transversal:
  - CRSP
  - Kenneth French Data Library
  - Lopez de Prado
  - Gu/Kelly/Xiu
  - AQR
  - Andrew Lo

### Notes

Este hito fija a nivel de modulo:

- la separacion entre `quotes_raw`, `trades_raw`, `daily_raw`, `split_normalized`, `adjusted` y `adjusted_proxy`;
- la diferencia entre precio de senal, precio de ejecucion y precio de valoracion;
- la regla de uso de series ajustadas en backtest y ML;
- y la forma correcta de reconciliar discrepancias con plataformas externas.

La politica queda enlazada desde:

- `external_price_comparison_caveats.md`
- `inspection_dossier_model.md`
- `daily_dataset_contract_v0_1.md`
- `quotes_dataset_contract_v0_1.md`

Ademas, deja fijada una norma metodologica adicional:

- toda decision operativa futura sobre semantica de precio, ajuste, comparacion externa, backtest o ML debe incluir respaldo cientifico o institucional suficiente dentro del documento que la establezca.

## v0.4.3 - Infraestructura general de datos y pausa metodologica explicita de quotes

### Added

- topologia general de almacenamiento y estado objetivo:
  - `01_foundations/module_contracts/data_storage_topology_and_target_state.md`
- inventario general de familias de evento y referencia con ejemplos reales:
  - `01_foundations/module_contracts/event_families_and_reference_inventory.md`
- registro institucional de vistas de precio:
  - `01_foundations/module_contracts/price_views_registry.md`
- metodologia general de corporate actions y ajustes:
  - `01_foundations/module_contracts/corporate_actions_adjustment_methodology.md`

### Notes

Este hito deja explicitamente anotado que:

- el stack ya contiene mucho mas que market data bruto;
- existen capas reales de `dividends`, `splits`, `reverse splits`, `ticker_change`, `halts`, `ipos`, `news`, `economic`, `financial`, `short_interest`, `short_volume`, `ticker_types`, `exchanges` e identidad temporalizada;
- y el modulo debe tratarlas como infraestructura general, no como detalles locales de `daily` o `quotes`.

Ademas se deja constancia de una pausa metodologica parcial en `quotes`:

- el bloque no se abandona;
- se aparta temporalmente parte del refinamiento local porque la semantica de precio y ajustes ya exige una solucion transversal reusable.

## v0.4.1 - Quotes inspection packs y dossiers review/bad activados

### Added

- exportador institucional de packs de evidencia de `quotes`:
  - `scripts/inspection/quotes/quotes_case_panel.py`
- capa global de policy visual para `quotes` en:
  - `01_foundations/inspection_dossiers/quotes/evidence_assets/global_policy/`
- exportacion de packs por caso para:
  - `01_foundations/inspection_dossiers/quotes/evidence_assets/review/`
  - `01_foundations/inspection_dossiers/quotes/evidence_assets/bad/`
- manifiestos generados:
  - `quotes_global_policy_manifest.csv`
  - `quotes_review_case_packs_manifest.csv`
  - `quotes_bad_case_packs_manifest.csv`
- primer dossier humano `review` de `quotes`:
  - `01_foundations/inspection_dossiers/quotes/flagged_case_evidence_packs/quotes_review_cases_v0_1.md`
- primer dossier humano `bad` de `quotes`:
  - `01_foundations/inspection_dossiers/quotes/bad_case_evidence_packs/quotes_bad_cases_v0_1.md`

### Notes

Este hito ya no solo fija contrato y policy de `quotes`; activa evidencia visual institucional reutilizable.

La exportacion actual de `quotes` cubre:

- capa global de distribucion/policy;
- packs por caso `review`;
- packs por caso `bad`;
- e incrusta, cuando existe, la imagen historica de certificacion junto al pack nuevo.

La franja `good` de `quotes` queda pendiente para la siguiente iteracion.

## v0.4.0 - Quotes contractual base y sesion de mercado institucionalizadas

### Added

- regla horizontal de alcance de sesion para market data:
  - `01_foundations/module_contracts/market_session_scope.md`
- taxonomia exacta y politica de corte de `quotes`:
  - `01_foundations/contract_registry/dataset_contracts/quotes_label_taxonomy_and_cut_policy.md`
- contrato alto nivel de `quotes`:
  - `01_foundations/contract_registry/dataset_contracts/quotes_dataset_contract_v0_1.md`
- policy de consumo de `quotes`:
  - `01_foundations/data_consumption_policies/quotes_consumption_policy.md`
- schema contract canonico de `quotes`:
  - `01_foundations/canonical_schemas/quotes/quotes_schema_contract.md`
- documento de validators de `quotes`:
  - `01_foundations/validators/quotes/quotes_validators.md`
- registry entry institucional de `quotes`:
  - `01_foundations/dataset_registry/quotes/quotes_registry_entry.yaml`

### Notes

Este hito no reaudita `quotes`.

Promueve a capa contractual institucional la evidencia historica ya cerrada del bloque y fija ademas una regla horizontal de sesion:

- `premarket -> regular -> afterhours`
- `04:00-20:00 America/New_York`

La lectura contractual de `quotes` queda cerrada sobre una regla clave:

- el contexto causal puede explicar el episodio;
- pero no rehabilita automaticamente la calidad local del libro.

## v0.2.0 - Primer dataset institucional real formalizado

### Added

- primer dataset contract institucional real del modulo:
  - `daily_dataset_contract_v0_1.md`
- primera policy de consumo institucional real para dataset:
  - `daily_consumption_policy.md`
- primer schema contract canonico real de dataset:
  - `daily_schema_contract.md`
- primer documento de validators institucionales reales para dataset:
  - `daily_validators.md`
- primera registry entry institucional real:
  - `daily_registry_entry.yaml`
- primera instancia completa del circuito:
  - `evidencia preservada -> contrato -> policy -> schema -> validators -> registry`

### Notes

Este hito no toca:

- `01_research/01_auditoria_RAW_DATA/`
- `data/`
- `run/`
- `runs/`

Formaliza `daily` como primer objeto institucional real construido sobre evidencia auditada y certificada ya existente.

## v0.3.0 - Modelo canonico de inspeccion institucional iniciado

### Added

- modelo canonico general de `inspection dossier` para el modulo:
  - `inspection_dossier_model.md`
- primera estructura de dossier de inspeccion especifica para `daily`
- primer `daily_inspection_readout_v0_1.md`
- documento inicial de construccion del inspection pack de `daily`
- arbol base para:
  - `good_justification`
  - `flagged_case_evidence_packs`
  - `bad_case_evidence_packs`
  - `coverage_case_evidence_packs`
  - `evidence_assets`

### Notes

Este hito fija el metodo general con el que `daily`, `quotes`, `trades`, `1m` y otros bloques deberan presentar evidencia a inspectores humanos y agentes.
No sustituye notebooks historicos ni closeouts.
Introduce la capa institucional de presentacion e inspeccion de evidencia.

## v0.1.0 - Fundacion local del modulo formalizada

### Added

- baseline de gobernanza local mediante `README.md`
- contrato local de agentes mediante `AGENTS.md`
- restricciones operativas locales mediante `LOCAL_RULES.md`
- regla explicita de preservacion de evidencia historica de auditoria y certificacion
- proteccion explicita de no tocar para:
  - `01_research/01_auditoria_RAW_DATA/`
  - `data/`
  - `run/`
  - `runs/`
- direccion explicita de consolidacion institucional para el modulo 01
- reconocimiento formal de `01_foundations/` como nueva capa operativa institucional que debe construirse al lado del arbol actual de research

### Notes

Este hito no reorganiza los arboles historicos de research ni de datos.
Establece la gobernanza necesaria para institucionalizar conocimiento auditado sin destruir lineage ni memoria cientifica.

## 2026-05-25 | trades foundations start

- created `01_foundations/contract_registry/dataset_contracts/trades_dataset_contract_v0_1.md`
- created `01_foundations/contract_registry/dataset_contracts/trades_label_taxonomy_and_cut_policy.md`
- created `01_foundations/data_consumption_policies/trades_consumption_policy.md`
- created `01_foundations/inspection_dossiers/trades/build_trades_inspection_pack.md`
- documented that `trades` must be interpreted through three layers: population snapshot, file-acceptance methodology sample, and full-closeout `57f`
- documented the crucial difference between the `380`-file methodological sample and the final full `<1B>` closure
- recorded full final `57f` label counts, including the residual `bad_data` tail and the extremely narrow `good` tail
- created `01_foundations/canonical_schemas/trades/trades_schema_contract.md`
- created `01_foundations/validators/trades/trades_validators.md`
- created `01_foundations/dataset_registry/trades/trades_registry_entry.yaml`
- anchored the trades registry and contracts to the real local `57f` full-closeout cache under `runs/backtest/trades_v2_materialized`
- documented that the methodological `380`-file sample is explanatory authority but not a replacement for the final `57f` full-closeout counts

## 2026-05-25 | Certification review promoted

- Added `01_foundations/module_contracts/auditoria_and_certification_source_hierarchy.md`.
- Documented the correct hierarchy between `auditoria/` and `certification/` for `daily`, `quotes`, and `trades`.
- Recorded that `certification/daily` and especially `certification/trades` contain more advanced recovery and usage semantics than current simplified foundations summaries.
- Recorded that `certification/quotes` complements the promoted foundations layer with stronger artifact mapping and certification framing.
- Recorded that `global_metrics` is a critical cross-block authority, but may need drift checks against newer local caches before counts are promoted as final truth.

## 2026-05-25 | Daily certification semantics aligned

- Refined `daily_inspection_readout_v0_1.md` to distinguish the visual inspection partition from the final certification state that combines quality and coverage.
- Updated `build_daily_inspection_pack.md` to require an explicit `coverage_case_evidence_packs` layer and to preserve the historical `001..007` coverage images as institutional evidence.
- Tightened `daily_dataset_contract_v0_1.md` and `daily_consumption_policy.md` so `daily` is no longer read as a simple `good / review / bad` block but as a two-axis final certification system.

## 2026-05-25 | Trades certification semantics aligned

- Refined `trades_dataset_contract_v0_1.md` so foundations now reflects the source hierarchy `auditoria -> certification -> foundations` explicitly.
- Elevated the final trades certification states `good / recoverable_with_flag / review_not_rehabilitated / bad` above the raw file-label vocabulary.
- Refined `trades_consumption_policy.md` to map file labels into final certification states instead of treating the label list as the final operational truth.
- Expanded `build_trades_inspection_pack.md` to record the existing certification images and to require a future trades inspection stack that separates population stress, file labels and final certification states.

## 2026-05-25 - Daily coverage visual closeout

- Promovida la evidencia historica `001.png` a `007.png` de `auditoria/daily/img` al cierre institucional de foundations.
- Creado `01_foundations/inspection_dossiers/daily/coverage_case_evidence_packs/daily_coverage_cases_v0_1.md`.
- Fijadas dos familias visuales de coverage en `daily`:
  - familia A alineada, compatible con `recoverable_without_penalty`;
  - familia B de desalineacion moderada, compatible con `recoverable_with_flag`.
- Actualizado `daily_inspection_readout_v0_1.md` para que `daily` deje de presentar la cobertura como deuda pendiente y pase a tratarla como evidencia ya integrada.

## 2026-05-25 - Trades inspection stack promoted

- Promoted `certification/trades/img/*.png` into `01_foundations/inspection_dossiers/trades/evidence_assets/historical_assets/`.
- Created `trades_population_readout_v0_1.md` to separate population stress from file-level decisions.
- Created `trades_file_acceptance_readout_v0_1.md` to document exactly what the `380`-file methodological sample proves and what it cannot prove.
- Created `trades_review_cases_v0_1.md`, `trades_bad_cases_v0_1.md` and `trades_good_cases_v0_1.md` using the strongest historical representative images.
- Created `trades_inspection_readout_v0_1.md` as the final institutional inspection synthesis for the block.
- Updated `build_trades_inspection_pack.md` to reflect that the initial foundations inspection stack now exists and future work is refinement, not greenfield scaffolding.
## 2026-05-25 - Trades `good` bucket interpretation clarified

- strengthened the `trades` readouts to explain that the tiny `good` share (`80` historical files in certification; `106` in current `57f` aggregate) must not be read as "almost all trades data is bad";
- documented explicitly that `good` measures only the pristine tail where `trades`, `daily`, and `1m` align almost perfectly;
- documented that the economically usable mass of `trades` is expected to live mainly in `recoverable_with_flag`, not in `good`;
- anchored that interpretation in `certification/trades/12_trades_good.md` and the final recovery policy.

## 2026-05-25 - Trades next-step handoff recorded

- recorded the next high-value operational step for `trades` in `build_trades_inspection_pack.md`;
- the pending task is to rematerialize the rehabilitation rule on `57f/full_clean_fast_same_schema`;
- the goal is to quantify how much of the current `review` mass would now pass into `recoverable_with_flag`;
- this was explicitly recorded because that number is more informative than the tiny `good` share when judging the real usable mass of the `trades` block.

## 2026-05-26 - Trades inspection notebook added in `01_foundations`

- created `01_foundations/inspection_dossiers/trades/trades_inspection_notebook_v0_1.ipynb` as a user-facing inspection notebook;
- added `scripts/inspection/trades/trades_case_panel.py` as the reusable widget selector for `trades`;
- the selector lets the user choose `capa`, `bucket` and `caso` over the promoted historical evidence;
- translated the `trades` build/inspection entry-point material to castellano so the new interactive layer does not drift in language from the rest of the module.

## 2026-05-26 - Trades family-semantics rule strengthened

- recorded explicitly in the `trades` inspection plan and readout that each case family must be explained as a semantic, causal and operational family;
- documented that future `trades` dossiers must not rely on bucket names, file names or raw attributes alone;
- required each family explanation to cover meaning, shared signature, methodological error avoided, pipeline impact and institutional decision consequence.

## 2026-05-26 - Trades stratified sampling policy recorded

- created `trades_sampling_strategy_v0_1.md` under `01_foundations/inspection_dossiers/trades/`;
- fixed the rule that future `trades` case packs must be built from enumeracion completa or muestra estratificada por familia, not from ad-hoc examples;
- documented per-family stratification variables for:
  - `reference_scale_mismatch`
  - `review_microstructure`
  - `review_no_1m_reference`
  - `review_1m_reference_alignment`
  - `review`
  - `bad_data`
  - `good`

## 2026-05-26 - General evidence-explanation rule formalized

- formalized in `inspection_dossier_model.md` the rule that every graph, table, example and evidence layer must explain:
  - `que muestra`
  - `responde`
  - `no responde`
  - `consecuencia`
- propagated the rule to the local `AGENTS.md` and `README.md` so future agents treat it as a general inspection norm, not a one-off preference from a single block.
### 2026-05-26 | trades | muestra_380 ya con panel rico comparable

- `scripts/inspection/trades/trades_case_panel.py` deja de mostrar `muestra_380` como preview tabular simple y pasa a renderizar un panel rico por caso.
- El panel ahora cruza:
  - `trades raw`,
  - referencia `daily`,
  - referencia `1m`,
  - y concentracion temporal del conflicto.
- El notebook `01_foundations/inspection_dossiers/trades/trades_inspection_notebook_v0_1.ipynb` queda actualizado para explicarlo en castellano.
- La distincion entre `population`, `case_pack` y `muestra_380` se mantiene por semantica de evidencia, pero `muestra_380` ya no debe sentirse como una capa visualmente inferior.
### 2026-05-27 | trades | rehabilitacion de review rematerializada sobre 57f real

- La politica historica de recuperacion de `trades` deja de apoyarse solo en el parcial `57e/full_clean`.
- Se recalcula la regla estricta y la extendida sobre el cache canonico real:
  - `root_cause_exports/file_acceptance_cache_lt1b_full_clean_fast_same_schema`
- Resultado sobre `review`:
  - `review_total = 4,851,211`
  - `strict_recoverable = 3,327,955` (`68.6005%`)
  - `strict_residual = 1,523,256`
  - `extended_recoverable = 3,505,290` (`72.2560%`)
  - `extended_residual = 1,345,921`
- Implicacion institucional:
  - la masa util real de `trades` es mucho mayor que `good`;
  - pero la vision optimista del parcial `57e` (`85.89%` rehabilitable estricto) ya no puede presentarse como cierre operativo del bloque.

### 2026-05-27 | trades | recuperacion por familia propagada a policy y readouts intermedios

- `trades_consumption_policy.md` ya no documenta solo la rehabilitacion de `review`, sino tambien la recuperacion operativa provisional de:
  - `review_microstructure`
  - `review_1m_reference_alignment`
- `trades_population_readout_v0_1.md` ahora explica que la masa util real del bloque vive sobre todo en la parte rehabilitable de `review` y familias vecinas, no en la cola `good`.
- `trades_file_acceptance_readout_v0_1.md` ahora conecta explicitamente la muestra metodologica `380` con los conteos reales de recuperacion sobre `57f`.
- Con esto, la lectura de `trades` ya no depende solo del readout final para entender:
  - cuanta masa es recuperable hoy;
  - que parte sigue como `review_not_rehabilitated`;
  - y por que la muestra metodologica y el cierre final cumplen funciones distintas.

### 2026-05-27 | trades | manifests estratificados materializados sobre 57f

- se creo `scripts/inspection/trades/build_trades_stratified_sample_manifests.py`;
- el script materializa manifests reproducibles por familia sobre `57f/full_clean_fast_same_schema`;
- se generaron en `01_foundations/inspection_dossiers/trades/evidence_assets/stratified_samples/`:
  - `review`: `60`
  - `reference_scale_mismatch`: `60`
  - `review_microstructure`: `60`
  - `bad_data`: `60`
  - `review_no_1m_reference`: `60`
  - `review_1m_reference_alignment`: `60`
  - `good`: `106` (enumeracion completa)
- se actualizo `trades_sampling_strategy_v0_1.md` para reflejar que `review_no_1m_reference` y `review_1m_reference_alignment` ya no deben tratarse como buckets diminutos en el cierre real;
- y se promovio esta muestra al plan y al readout final para que la siguiente etapa parta de manifests fijos y no de ejemplos elegidos a mano.

### 2026-05-27 | trades | casepacks amplios por familia ya exportados

- se creo `scripts/inspection/trades/export_trades_family_casepacks.py`;
- el exportador reutiliza el panel rico file-level del selector de `trades` y lo guarda como `.png` por caso;
- se generaron los dossiers amplios por familia en `01_foundations/inspection_dossiers/trades/family_case_evidence_packs/`:
  - `bad_data`: `60` imagenes
  - `good`: `106` imagenes
  - `reference_scale_mismatch`: `60` imagenes
  - `review`: `60` imagenes
  - `review_1m_reference_alignment`: `60` imagenes
  - `review_microstructure`: `60` imagenes
  - `review_no_1m_reference`: `60` imagenes
- se creo el indice:
  - `family_casepacks_index_v0_1.md`
- con esto, `trades` ya no depende solo de:
  - ejemplos historicos curados,
  - ni del notebook interactivo;
- tambien tiene una capa exportada amplia y reproducible por familia para lectura del inspector.

### 2026-05-27 | trades | `bad_data` dividido en subfamilias visuales y lectura por imagen endurecida

- se formaliza en `inspection_dossier_model.md` una regla mas fuerte:
  - la explicacion de una imagen no puede salir solo de bucket + metricas;
  - debe salir de la lectura visual real del panel;
  - y si el panel no demuestra la causalidad principal, el dossier debe decirlo y pedir una visualizacion complementaria.
- en `trades`, `bad_data` deja de tratarse como familia visual unica:
  - subfamilia de colapso de escala/rango;
  - subfamilia de integridad estructural del tape.
- cuantificacion sobre `57f`:
  - `trade_price_outside_daily_range`: `9,606` (`60.53%`)
  - `scale_bucket_vw = nan`: `4,247` (`26.76%`)
  - `negative_or_zero_size_rows`: `695` (`4.38%`)
  - `duplicate_excess_ratio_gt_hard_cap`: `1,329` (`8.37%`)
  - componente estructural sin conflicto diario fuerte: `204` (`1.29%`)
- se endurecio la lectura de:
  - `ASTI 2007-12-24`
  - `DCTH 2005-12-29`
  - `WSBF 2009-08-14`
- conclusion importante:
  - `ASTI` y `DCTH` ya quedan bien justificados por el panel actual como `bad_data` de colapso de escala/rango;
  - `WSBF` puede seguir siendo `bad_data`, pero el panel actual no demuestra bien su causalidad y exige un panel adicional de integridad (`size <= 0`, duplicados, filas invalidas).

### 2026-05-27 | trades | `bad_data` reexportado con panel de integridad y comentarios por subfamilia

- `trades_case_panel.py` ahora anade un tercer panel operativo de `Integridad estructural del tape` con:
  - `size <= 0`
  - `size NA`
  - `price NA`
  - `dup rows`
- la lectura file-level de `bad_data` ya no es generica:
  - clasifica cada caso en subfamilias visuales;
  - usa comentarios distintos para colapso de escala/rango, integridad estructural, dano mixto y conflictos ralos;
  - y documenta cuando el panel de precio no demuestra por si solo la causalidad del rechazo.
- se ha reexportado `bad_data_cases_v0_1.md` completo (`60` casos) con esta logica nueva.

### 2026-05-29 | price views | primer consumidor real de `daily_adjusted` ya materializado

- se ejecuto `scripts/materialize_daily_return_labels.py` sobre la fuente oficial piloto:
  - `E:\TSIS\data\ohlcv_daily_adjusted`
- se materializo la salida operativa en:
  - `E:\TSIS\data\daily_return_labels`
- layout confirmado por `ticker/year`, por ejemplo:
  - `E:\TSIS\data\daily_return_labels\ticker=A\year=2005\day_aggs_A_2005_labels.parquet`
- columnas verificadas en parquet real:
  - `c_adjusted`
  - `ret_1d`
  - `ret_3d`
  - `ret_5d`
  - `label_source_view`
  - `label_contract`
- resumen del piloto:
  - `A`: `22` files / `5327` rows
  - `AAME`: `22` / `4949`
  - `ABEO`: `12` / `2693`
  - `ABIO`: `16` / `3925`
  - `ABTX`: `8` / `1758`
  - `BBW`: `22` / `5327`
  - `CASS`: `22` / `5241`
  - `CVLY`: `20` / `4420`
  - `SELF`: `11` / `2548`
  - `SGC`: `22` / `5199`
- con esto, `daily_adjusted` deja de ser solo semantica documentada y queda conectado a un consumidor real reproducible de labels diarios de retorno.

### 2026-05-29 | price views | contrato minimo de `1m_split_normalized` ya fijado

- se formalizo la siguiente capa intradia prioritaria despues de `daily_adjusted`:
  - `ohlcv_1m_split_normalized`
- se anadieron:
  - `01_foundations/contract_registry/dataset_contracts/ohlcv_1m_split_normalized_dataset_contract_v0_1.md`
  - `01_foundations/module_contracts/ohlcv_1m_split_normalized_operational_landing_v0_1.md`
  - `01_foundations/module_contracts/ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md`
  - `01_foundations/dataset_registry/1m/ohlcv_1m_split_normalized_registry_entry.yaml`
- queda fijado que:
  - esta capa corrige escala mecanica por split entre sesiones;
  - no sustituye a `1m raw`;
  - no es todavia un `1m_adjusted` economico completo;
  - y debe promocionarse incrementalmente por `ticker-month` bajo demanda del consumidor real.

### 2026-05-29 | price views | `daily_adjusted` orientado ya a full-universe y piloto semantico de `1m_split_normalized` fijado

- se anadio:
  - `01_foundations/module_contracts/daily_adjusted_full_universe_promotion_plan_v0_1.md`
- queda fijado que `daily_adjusted` ya tiene madurez suficiente para apuntar a cobertura full-universe `2005-2026`;
- la deuda pendiente ya no es semantica sino promocion operativa disciplinada.
- se anadieron tambien:
  - `01_foundations/module_contracts/ohlcv_1m_split_normalized_semantic_pilot_v0_1.md`
  - `01_foundations/dataset_registry/1m/ohlcv_1m_split_normalized_pilot_manifest_v0_1.md`
- queda fijado que el siguiente paso de `1m_split_normalized` no es full-universe inmediato, sino:
  - piloto semantico con `forward split`, `reverse split` y controles;
  - seleccionado por cobertura real en `D:\ohlcv_1m`;
  - y con unidad `ticker-month`.

### 2026-05-29 | price views | lote real del piloto `1m_split_normalized` ya seleccionado

- se cruzo cobertura real de:
  - `D:\ohlcv_1m`
  - `D:\ohlcv_daily`
  - y fuentes maestras de `splits`
- se fijo un lote minimo de `10` casos, alineado con la escala del piloto de `daily_adjusted`:
  - `4` `reverse split`
  - `4` `forward split`
  - `2` `control`
- artefactos creados:
  - `01_foundations/module_contracts/ohlcv_1m_split_normalized_pilot_manifest_v0_2.md`
  - `01_foundations/dataset_registry/1m/ohlcv_1m_split_normalized_pilot_manifest_v0_2.csv`
- casos seleccionados:
  - `BXRX 2022-12`
  - `COSM 2022-12`
  - `CEI 2022-12`
  - `BNGO 2025-01`
  - `EFSH 2025-01`
  - `SAVA 2023-12`
  - `PD 2006-03`
  - `LIVE 2014-02`
  - `BXRX 2022-11` control
  - `BNGO 2025-02` control

### 2026-05-29 | price views | piloto `1m_split_normalized` ya materializado y leido semanticamente

- se creo:
  - `scripts/materialize_1m_split_normalized.py`
- se materializo el piloto en:
  - `E:\TSIS\data\ohlcv_1m_split_normalized`
- se genero el resumen:
  - `E:\TSIS\data\ohlcv_1m_split_normalized\_split_normalized_materialization_summary.csv`
- se documento la lectura semantica en:
  - `01_foundations/module_contracts/ohlcv_1m_split_normalized_pilot_results_v0_1.md`
- hallazgo importante fijado:
  - un control pre-evento puede y debe seguir teniendo `future_split_factor != 1`;
  - un control post-evento debe quedar neutro;
  - y la capa protege contra shocks mecanicos de split entre sesiones sin reemplazar `1m raw`.

### 2026-05-29 | price views | readout visual del piloto `1m_split_normalized` ya exportado

- se creo:
  - `scripts/inspection/minute/export_1m_split_normalized_pilot_readout.py`
- se exporto:
  - `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_pilot_readout_v0_1.md`
- se generaron `10` imagenes de auditoria visual en:
  - `01_foundations/inspection_dossiers/1m_split_normalized/images/`
- cada caso muestra:
  - `1m raw` del mes completo
  - `1m split_normalized` del mes completo
  - ventana focalizada alrededor del evento o ancla
  - trayectoria diaria de `future_split_factor`
- con esto, la validacion de `1m_split_normalized` ya no depende solo de tablas y texto contractual; tambien queda auditada visualmente caso por caso.

### 2026-05-29 | price views | primer consumidor recomendado de `1m_split_normalized` ya fijado

- se anadieron:
  - `01_foundations/module_contracts/intraday_regime_features_consumer_contract_v0_1.md`
  - `01_foundations/module_contracts/intraday_regime_features_variable_taxonomy_v0_1.md`
  - `01_foundations/module_contracts/intraday_regime_features_operational_landing_v0_1.md`
  - `01_foundations/dataset_registry/features/intraday_regime_features_registry_entry.yaml`
- queda fijado que el primer consumidor natural de `1m_split_normalized` no es:
  - `execution_simulator`
  - ni RL
  - ni una policy final de entrada/salida
- sino una capa de `intraday_regime_features` que:
  - use `1m_split_normalized` para comparaciones cross-session
  - use `1m raw` para estado local de la sesion
  - y deje la microestructura fina para una fase posterior con `quotes_raw` y `trades_raw`.

### 2026-06-02 | governance | `module_contracts` ya tiene indice maestro e indices por dominio

- se anadieron:
  - `01_foundations/module_contracts/README.md`
  - `01_foundations/module_contracts/daily_contracts_index.md`
  - `01_foundations/module_contracts/quotes_contracts_index.md`
  - `01_foundations/module_contracts/trades_contracts_index.md`
  - `01_foundations/module_contracts/1m_contracts_index.md`
  - `01_foundations/module_contracts/transversal_contracts_index.md`
- se crearon, todavia vacias, las carpetas destino de una futura migracion fisica:
  - `module_contracts/daily/`
  - `module_contracts/quotes/`
  - `module_contracts/trades/`
  - `module_contracts/minute/`
  - `module_contracts/transversal/`
  - `module_contracts/consumers/`
  - `module_contracts/governance/`
- queda fijado que la reorganizacion fisica no se hace todavia y que cualquier migracion futura debe priorizar no romper referencias desde markdowns, notebooks, readouts y agentes.

### 2026-06-02 | price views | cierre inspector final de `1m_split_normalized` ya consolidado

- se anadieron:
  - `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_final_readout_v0_1.md`
  - `scripts/inspection/minute/build_1m_split_normalized_inspection_notebook.py`
  - `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_inspection_notebook_v0_1.ipynb`
- el notebook queda ejecutado con outputs y enlaza:
  - contrato
  - formula
  - piloto semantico
  - consumidor minimo real
- con ello `1m_split_normalized` deja de estar solo defendido por contrato y tablas; tambien queda presentado como paquete inspector navegable.

### 2026-06-02 | price views | auditoria exhaustiva full-universe de splits en `1m` ya ejecutada

- se creo:
  - `scripts/inspection/minute/audit_1m_split_full_universe.py`
- se generaron:
  - `01_foundations/inspection_dossiers/1m_split_normalized/evidence_assets/full_universe_split_audit/full_universe_split_event_cases.csv`
  - `01_foundations/inspection_dossiers/1m_split_normalized/evidence_assets/full_universe_split_audit/full_universe_split_event_cases.parquet`
  - `01_foundations/inspection_dossiers/1m_split_normalized/evidence_assets/full_universe_split_audit/full_universe_split_event_status_summary.csv`
  - `01_foundations/inspection_dossiers/1m_split_normalized/evidence_assets/full_universe_split_audit/full_universe_split_event_audit_meta.csv`
- resultados:
  - `total_event_cases = 3335`
  - `PASS = 2280`
  - `FAIL = 0`
  - `NO_PRE_COVERAGE = 164`
  - `NO_POST_COVERAGE = 151`
  - `NO_1M_COVERAGE = 740`
- conclusion institucional fijada:
  - el `100%` de los casos plenamente auditables pasa;
  - los no-`PASS` observados son limites de cobertura y no fallos semanticos de la capa.

### 2026-06-02 | price views | notebook interactivo full-universe para auditoria de splits en `1m` ya disponible

- se creo:
  - `scripts/inspection/minute/build_1m_split_full_universe_audit_notebook.py`
- se genero:
  - `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_notebook_v0_1.ipynb`
  - `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md`
- el notebook no usa PNGs como interfaz principal; permite al inspector seleccionar cualquier caso del universo auditado por:
  - `status`
  - `ticker`
  - `evento`
- y visualizar inline:
  - metadata del caso
  - serie `raw`
  - serie `split_normalized`
  - trayectoria de `future_split_factor`
  - lectura tecnica del estado de auditoria

### 2026-06-02 | quotes | readout poblacional reescrito con lectura numerica grafico por grafico

- se reescribio:
  - `01_foundations/inspection_dossiers/quotes/quotes_inspection_readout_v0_1.md`
- la nueva version ya no solo explica intencion y semantica de cada panel; ahora cuantifica explicitamente:
  - peso de las familias dominantes
  - masa real de la cola dura
  - diferencia entre severidad, taxonomia y open buckets
  - y por que una familia visualmente extrema puede ser pequena mientras otra mas pequena puede ser economicamente mas peligrosa
- esto deja `quotes` mas cerca del estandar analitico ya usado en `trades`.

### 2026-06-02 | quotes | auditoria de integridad de la bolsa abierta `review/bad` ya ejecutada

- se creo:
  - `scripts/inspection/quotes/audit_quotes_open_casepacks.py`
- se generaron:
  - `01_foundations/inspection_dossiers/quotes/evidence_assets/open_casepacks_audit/quotes_open_casepacks_audit_summary.csv`
  - `01_foundations/inspection_dossiers/quotes/evidence_assets/open_casepacks_audit/quotes_open_casepacks_audit_summary.parquet`
  - `01_foundations/inspection_dossiers/quotes/quotes_open_casepacks_audit_v0_1.md`
- resultados:
  - `review`: `64` esperados, `64` en manifest, `64` en markdown, `64` con assets completos, `PASS`
  - `bad`: `15` esperados, `15` en manifest, `15` en markdown, `15` con assets completos, `PASS`
- conclusion institucional fijada:
  - la bolsa abierta de `quotes` no contiene casos perdidos ni casos anadidos ad hoc;
  - queda cerrada con integridad de coverage y de assets respecto al pool historico abierto.

### 2026-06-02 | governance | snapshot transversal `v0_2` ya refleja el nuevo estado de cierre

- se creo:
  - `01_foundations/module_contracts/foundations_transversal_final_review_v0_2.md`
- y `v0_1` queda enlazado hacia `v0_2` como snapshot historico previo.
- `v0_2` fija explicitamente:
  - que `quotes` ya no tiene solo buen cierre semantico, sino tambien auditada la integridad de su frontera abierta;
  - que `1m` ya tiene cerrada exhaustivamente la deuda de splits sobre el universo auditable;
  - y que las deudas restantes viven mas en promocion operacional, uniformidad final y alcance que en definicion base.

### 2026-06-02 | governance | compatibilidad futura de paths en `module_contracts` ya preparada

- se anadio al `README` de `module_contracts` una seccion explicita de:
  - compatibilidad de paths y referencias;
  - regla de resolucion de rutas antiguas;
  - y obligacion de usar mapa oficial en vez de heuristica.
- se creo:
  - `01_foundations/module_contracts/module_contracts_migration_map_v0_1.md`
- el mapa deja preparado:
  - origen -> destino previsto;
  - agrupacion por dominios futuros;
  - y la nota institucional de que cualquier documento futuro que cite paths antiguos debe resolverlos mediante este mapa si la migracion fisica ya se hubiera ejecutado.

### 2026-06-02 | governance | pre-auditoria real de referencias a `module_contracts` ya exportada

- se creo:
  - `scripts/inspection/governance/audit_module_contracts_references.py`
  - `01_foundations/module_contracts/module_contracts_reference_pre_audit_v0_1.md`
- se exportaron:
  - `01_foundations/module_contracts/evidence_assets/module_contracts_reference_audit/module_contracts_reference_hits.csv`
  - `01_foundations/module_contracts/evidence_assets/module_contracts_reference_audit/module_contracts_reference_summary.csv`
  - `01_foundations/module_contracts/evidence_assets/module_contracts_reference_audit/module_contracts_reference_sources.csv`
- resultados agregados:
  - `reference_hits_total = 188`
  - `unique_source_files = 41`
  - `unique_target_documents = 55`
- targets mas sensibles por volumen de referencias:
  - `policy_explanation_standard.md` -> `20` referencias en `20` archivos
  - `price_semantics_and_adjustment_policy.md` -> `13` referencias en `10` archivos
  - `external_price_comparison_caveats.md` -> `9` referencias en `7` archivos
  - `pipeline_price_view_policy.md` -> `8` referencias en `8` archivos
- con esto, la futura migracion de `module_contracts` ya no parte de intuicion: queda cuantificada su superficie de ruptura potencial.

### 2026-06-03 | governance | plan de ejecucion segura de migracion de `module_contracts` ya preparado para otro agente

- se creo:
  - `01_foundations/module_contracts/module_contracts_migration_execution_plan_v0_1.md`
- y se enlazo desde:
  - `01_foundations/module_contracts/README.md`
- el plan deja preparado:
  - orden por fases;
  - lotes de riesgo;
  - checklist de entrada, ejecucion y salida;
  - criterio de parada;
  - y reglas de handoff para que otro agente pueda ejecutar la migracion sin empezar desde cero ni mover todo de golpe.

### 2026-06-03 | daily | auditoria de estado full-universe de `daily_adjusted` ya ejecutada

- se creo:
  - `scripts/inspection/daily/audit_daily_adjusted_full_universe.py`
  - `01_foundations/inspection_dossiers/daily/daily_adjusted_full_universe_audit_v0_1.md`
- se exportaron:
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_full_universe_audit/daily_adjusted_full_universe_summary.csv`
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_full_universe_audit/daily_adjusted_ticker_activation_summary.csv`
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_full_universe_audit/daily_adjusted_file_activation_summary.csv`
- resultado clave:
  - `raw_tickers = 12494`
  - `adjusted_tickers = 10`
  - `raw_year_files = 125438`
  - `adjusted_year_files = 177`
  - `ticker_coverage_pct = 0.080038%`
  - `year_file_coverage_pct = 0.141106%`
- conclusion fijada:
  - la deuda abierta de `daily_adjusted` ya no es semantica de la capa, sino promocion operacional amplia y auditoria agregada posterior a esa expansion.

### 2026-06-03 | daily | cola compleja de corporate actions para `daily_adjusted` ya medida

- se creo:
  - `scripts/inspection/daily/audit_daily_adjusted_complex_actions_tail.py`
  - `01_foundations/inspection_dossiers/daily/daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md`
- se exportaron:
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_complex_actions_tail_audit/daily_adjusted_complex_actions_tail_summary.csv`
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_complex_actions_tail_audit/daily_adjusted_ticker_change_tail.csv`
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_complex_actions_tail_audit/daily_adjusted_non_cd_dividend_tail.csv`
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_complex_actions_tail_audit/daily_adjusted_complex_actions_type_summary.csv`
- resultado clave:
  - `ticker_event_rows_total = 3037`
  - `ticker_change_rows_within_daily_window = 2142`
  - `ticker_change_tickers_within_daily_window = 2072`
  - `dividend_non_cd_rows = 361`
  - `non_cd_dividend_rows_within_daily_window = 331`
  - `non_cd_dividend_tickers_within_daily_window = 184`
- conclusion fijada:
  - la frontera compleja visible hoy no es una masa estructurada de `spin-offs` o `stock dividends`;
  - la deuda material real es, sobre todo, `ticker_change` como problema de continuidad corporativa;
  - y la cola `dividend_type != CD` existe pero es pequena y aparece solo como `SC`.

### 2026-06-03 | 1m | reconciliacion explicita entre cierre raw historico, marco `lt1b` y cierre moderno de splits

- se creo:
  - `01_foundations/module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md`
- el documento fija explicitamente:
  - que el proyecto institucional moderno si vive en marco `lt1b`;
  - que el cierre historico raw de `1m` sigue siendo valido en policy y causalidad;
  - pero que sus porcentajes historicos deben declararse como `full-scope` salvo recalculo nominal `<1B>`;
  - y que el cierre nuevo de `ohlcv_1m_split_normalized` no contradice ese cierre raw, sino que resuelve la deuda especifica de splits.

### 2026-06-03 | 1m | arranque del recalculo raw `1m` sobre universo `<1B>` explicito

- se creo:
  - `scripts/inspection/minute/audit_1m_raw_lt1b_closeout.py`
  - `01_foundations/inspection_dossiers/minute/raw_1m_lt1b_closeout_recalculation_v0_1.md`
- el recalculo queda definido para:
  - reutilizar los buckets historicos raw de `1m`;
  - filtrarlos por ticker + ventana PTI del corte canonico `<1B>`;
  - y exportar conteos y porcentajes compatibles ya con el alcance moderno del proyecto.

### 2026-06-03 | 1m | cierre cuantitativo del recálculo raw `1m` sobre universo `<1B>` explicito

- se actualizan:
  - `scripts/inspection/minute/audit_1m_raw_lt1b_closeout.py`
  - `01_foundations/inspection_dossiers/minute/raw_1m_lt1b_closeout_recalculation_v0_1.md`
  - `01_foundations/module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md`
- el script ya reconstruye la taxonomia fina `vw_*` directamente desde las metricas historicas guardadas en `rescue_schema_plus_vw.parquet`
- el recalculo `<1B>` queda exportado con conteos finales reales:
  - `lt1b_current_1m_rows = 334660`
  - `good = 46652 (13.940118%)`
  - `review = 75245 (22.484014%)`
  - `bad = 212763 (63.575868%)`
- a partir de aqui:
  - los porcentajes `full-scope` del closeout raw historico de `1m` siguen siendo antecedente metodologico;
  - pero las afirmaciones cuantitativas raw `1m` estrictamente `<1B>` deben citar este recalculo.

### 2026-06-04 | 1m | paquete inspector especifico para `schema_only` en raw `<1B>`

- se crean:
  - `scripts/inspection/minute/build_1m_schema_only_lt1b_inspection_notebook.py`
  - `01_foundations/inspection_dossiers/minute/raw_1m_schema_only_lt1b_inspection_readout_v0_1.md`
  - `01_foundations/inspection_dossiers/minute/raw_1m_schema_only_lt1b_inspection_notebook_v0_1.ipynb`
- el notebook queda ejecutado con outputs y widgets para:
  - seleccionar firma de warning;
  - seleccionar ticker;
  - y seleccionar cualquier `year-month` del bloque `RESCUE_SCHEMA_ONLY`
- la lectura institucional que queda fijada es:
  - el `5.89%` no-`vw` no es una cola economica difusa;
  - esta dominado por `dataset_read_incompatible_schema` + `schema_merge_conflict_ticker_encoding`;
  - y debe leerse como problema de compatibilidad estructural / merge de schema.

### 2026-06-05 | daily | materializacion fisica full-universe de `daily_adjusted` completada

- se completo la materializacion fisica de `daily_adjusted` contra el universo diario raw:
  - raw input: `D:\ohlcv_daily`
  - adjusted output: `E:\TSIS\data\ohlcv_daily_adjusted`
- comprobacion fisica final:
  - `raw_files = 125438`
  - `adjusted_files = 125438`
  - `missing_outputs = 0`
  - `extra_adjusted_outputs = 0`
- la ejecucion final se cerro mediante runner seguro de reanudacion fisica:
  - no dependia de `_materialization_summary.csv` como checkpoint;
  - decidia completitud por presencia fisica de parquets por `ticker/year`;
  - y mantuvo `overwrite=False`, por lo que no reescribia parquets ya existentes.
- durante la ejecucion se detecto un bloqueo transitorio de escritura del volumen `E:` (`HFS Plus`); tras reabrir el volumen, el proceso retomo desde el primer ticker incompleto (`NKX`) y completo solo los anos faltantes.
- estado institucional fijado:
  - el computo full-universe de parquets `daily_adjusted` esta materialmente completo;
  - no queda proceso materializador activo;
  - la promocion semantica/contractual final todavia requiere ejecutar y registrar la auditoria full-universe correspondiente antes de llamar la capa `full-universe bueno`.

### 2026-06-05 | daily | `daily_adjusted` promovido full-universe tras auditoria contractual agregada

- se actualizo y ejecuto:
  - `scripts/inspection/daily/audit_daily_adjusted_full_universe.py`
  - `01_foundations/inspection_dossiers/daily/daily_adjusted_full_universe_audit_v0_1.md`
- se regeneraron evidence assets bajo:
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_full_universe_audit/`
- durante la auditoria se detecto un parquet ajustado invalido de `0` bytes:
  - `E:\TSIS\data\ohlcv_daily_adjusted\ticker=NHI\year=2007\day_aggs_NHI_2007_adjusted.parquet`
- el archivo invalido se preservo en cuarentena y se regenero solo el `ticker-year` afectado con `overwrite=False`:
  - `E:\TSIS\data\ohlcv_daily_adjusted\_quarantine_zero_byte_20260605\day_aggs_NHI_2007_adjusted.parquet.zero_bytes`
- resultado final de auditoria full-universe:
  - `raw_tickers_with_files = 12230`
  - `adjusted_tickers_with_files = 12230`
  - `raw_year_files = 125438`
  - `adjusted_year_files = 125438`
  - `missing_outputs = 0`
  - `extra_adjusted_outputs = 0`
  - `read_error_files = 0`
  - `files_missing_required_columns = 0`
  - `nonpositive_factor_rows = 0`
  - `null_factor_rows = 0`
  - `bad_price_view_rows = 0`
  - `missing_source_daily_file_rows = 0`
- se actualizo:
  - `01_foundations/dataset_registry/daily/daily_adjusted_registry_entry.yaml`
  - `01_foundations/module_contracts/layer_maturity_assessment_v0_1.md`
- estado institucional fijado:
  - `daily_adjusted` pasa de `Nivel 5 - Consumida` a `Nivel 6 - Promovida`;
  - queda activa como vista derivada diaria full-universe para verdad economica lenta;
  - no habilita automaticamente ejecucion, RL ni uso live.
