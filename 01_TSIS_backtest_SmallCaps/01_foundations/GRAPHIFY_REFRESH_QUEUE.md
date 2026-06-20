# Graphify Refresh Queue for 01_foundations

Fecha de creacion: 2026-06-19
Estado: cola operativa versionada para refrescos Graphify de `01_foundations`.

## Rol

Este archivo evita tratar Graphify como si fuera Git.

Git registra cambios continuamente. Graphify se refresca por hitos semanticos,
por severidad o por lote.

Regla:

```text
No actualizar Graphify por cada commit.
Actualizar Graphify cuando el cambio altere el mapa semantico que un agente
necesita consultar.
```

El protocolo autoritativo vive en:

```text
GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
```

La definicion metodologica de slices vive en:

```text
module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md
```

## Severidad de refresco

### LOW

No requiere Graphify.

Ejemplos:

- typo;
- README menor;
- limpieza textual;
- nota privada o no promovida;
- cambio que no altera contratos, schemas, registries, policies ni validators.

Accion:

```text
No hacer nada en Graphify.
```

### MEDIUM

Se anota en esta cola, pero no se refresca inmediatamente.

Ejemplos:

- nuevo documento explicativo;
- nuevo README funcional;
- ampliacion documental sin cambio contractual;
- evidencia ligera no promovida;
- ajuste de navegacion que afecta como un agente encuentra documentos.

Accion:

```text
Anotar entrada pending.
Refrescar cuando haya lote suficiente o una consulta lo necesite.
```

### HIGH

Requiere rebuild del leaf afectado en una ventana dedicada.

Ejemplos:

- nuevo dataset contract;
- nuevo schema canonico;
- nueva data consumption policy;
- validator que cambia aceptacion;
- closeout que cambia interpretacion;
- nuevo protocolo transversal de tablas;
- nuevo graph slice.

Accion:

```text
Construir o actualizar leaf oficial.
No actualizar root si no es necesario para la tarea inmediata.
```

### CRITICAL

Requiere decision explicita antes de tocar el root.

Ejemplos:

- renombrar carpetas ya indexadas;
- eliminar o migrar rutas indexadas;
- cambiar semantica de dataset;
- cambiar price semantics;
- cambiar certification/recovery state;
- promocionar master table;
- cambiar consumo downstream.

Accion:

```text
Construir leaf si aporta valor inmediato.
No hacer merge aditivo si el root conserva nodos antiguos.
Integrar root solo mediante rebuild controlado o reemplazo oficial de slice.
```

## Cadencia recomendada

```text
Diario:
  Git normal.
  Documentar cambios relevantes.
  Anotar pending refresh si aplica.

Por hito:
  Rebuild de leaves afectados.

Por ventana dedicada:
  Integracion limpia del root si hace falta.
```

## Entradas activas

### GFQ-20260619-001 - Initial Data Foundation Graphify governance

Status: `leaf_built`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
```

Reason:

- Se creo la gobernanza inicial para Graphify de CAPA 1.
- Existen nuevos documentos que deben entrar en el mapa semantico cuando se
  construya el primer leaf oficial:
  - `GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md`
  - `GRAPHIFY_REFRESH_QUEUE.md`
  - `module_contracts/graphify/README.md`
  - `module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md`

Changed paths:

```text
01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_foundations/.graphifyignore
01_foundations/README.md
01_foundations/module_contracts/graphify/
01_foundations/module_contracts/README.md
```

Recommended action:

```text
Built foundations_authority_graph as the first official leaf.
Do not build a monolithic 01_foundations graph yet.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation governance
```

Notes:

The first useful Graphify build for CAPA 1 should map authority, not evidence.
Evidence-heavy dossiers and parquet/CSV profiling come later and must stay
separate.

`foundations_authority_graph` is not a physical folder. It is the first official
leaf graph name. The full `01_foundations` map is expected to emerge from
separate leaves and, if useful, a later `data_foundation_root_graph`.

Build result:

```text
Output:
01_foundations/graphify-out/leaf_slices/foundations_authority_20260619/

Stats:
- detected_files: 246
- detected_words: 411452
- nodes: 696
- edges: 854
- communities: 75

Validation:
- graphify diagnose multigraph passed with 0 dangling endpoints, 0 duplicate
  edges, and 0 endpoint-collapsed edge groups.
- root graph intentionally not created:
  01_foundations/graphify-out/graph.json = absent
```

### GFQ-20260619-002 - README cross-graph and graph-first lookup rule

Status: `leaf_built`

Severity: `MEDIUM`

Slice:

```text
foundations_authority_graph
```

Reason:

- `01_foundations/README.md` now records that the official
  `certification_decisions_graph` exists outside `01_foundations`.
- Future agents must consult the certification leaf when a question depends on
  historical audit/certification, closeouts, historical policies, global
  metrics or decisions expressed as `expected/present/healthy/usable`.
- `01_foundations/README.md` now distinguishes `graph_only`,
  `graph_first_source_verified` and `source_only_exception` answers.
- Future agents must query Graphify first for architecture, relationships,
  institutional quality, maturity or coverage questions, then verify material
  claims against source documents, scripts, dossiers and `evidence_assets`.
- The historical research graph is explicitly documented as context that can
  enrich, constrain or qualify interpretation of `01_foundations`, without
  promoting historical claims by itself.

Changed paths:

```text
01_foundations/README.md
```

Recommended action:

```text
Do not rebuild immediately.
Include this README change in the next foundations_authority_graph refresh.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation governance
```

Notes:

This change is a navigation and agent-usage update. It does not alter dataset
contracts, schemas, validators or consumption policies. It made the prior
`foundations_authority_graph` semantically stale for the new query protocol and
was included in the 20260620 leaf refresh.

Satisfied by:

```text
foundations_authority_graph leaf build:
01_foundations/graphify-out/leaf_slices/foundations_authority_20260620/
```

### GFQ-20260619-003 - RAW authority and derivation map

Status: `leaf_built`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
```

Reason:

- A new transversal module contract now separates RAW vendor provenance from
  functional role: raw market data, raw reference/context data, derived ETL
  views, feature layers, label/target layers, audit evidence and runtime/cache
  artifacts.
- `01_foundations/README.md` now points agents to that contract before reading
  maturity percentages as proof of raw data quality.
- `module_contracts/README.md` now includes the contract in the mandatory
  market-data reading path.
- This changes the semantic map agents need when answering raw-vs-derived
  questions, even though no dataset files, schemas or validators changed.

Changed paths:

```text
01_foundations/module_contracts/raw_data_authority_and_derivation_map.md
01_foundations/module_contracts/README.md
01_foundations/module_contracts/transversal_contracts_index.md
01_foundations/README.md
```

Recommended action:

```text
Do not rebuild immediately unless a raw/derived architecture query requires it.
Include this contract in the next foundations_authority_graph refresh.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation governance
```

Notes:

This is a semantic-governance update. It does not promote or demote any dataset
by itself. It fixes the transversal interpretation layer so derived datasets,
features, labels, evidence assets and Graphify outputs cannot be mistaken for
primary RAW audit authority.

Satisfied by:

```text
foundations_authority_graph leaf build:
01_foundations/graphify-out/leaf_slices/foundations_authority_20260620/
```

### GFQ-20260619-004 - Additional context quality and master-table readiness

Status: `leaf_built`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
```

Reason:

- `additional_v0_1` now has a validator contract, domain index, master-table
  readiness policy, generated inspection package and evidence assets.
- The README maturity changes from accepted auxiliary (`78%`) to governed RAW
  vendor context (`92%`) with explicit unresolved limits.
- The new package changes the semantic map future agents need when deciding how
  Additional can feed `data_quality_report`, `master_daily_table`,
  `symbol_master`, `corporate_actions_table`, `calendar_table` and indirect
  `master_intraday_table` context.

Changed paths:

```text
01_foundations/README.md
01_foundations/validators/README.md
01_foundations/validators/additional/additional_validators.md
01_foundations/module_contracts/README.md
01_foundations/module_contracts/transversal_contracts_index.md
01_foundations/module_contracts/additional_contracts_index.md
01_foundations/module_contracts/additional_to_master_tables_policy_v0_1.md
01_foundations/contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/additional_consumption_policy.md
01_foundations/dataset_registry/additional/additional_registry_entry.yaml
01_foundations/inspection_dossiers/README.md
01_foundations/inspection_dossiers/additional/
scripts/inspection/additional/build_additional_inspection_pack.py
```

Recommended action:

```text
Do not rebuild immediately unless an Additional/master-table architecture query
requires it. Include this package in the next foundations_authority_graph
refresh.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation governance
```

Notes:

This is a CAPA 1 governance and evidence update. It does not materialize a
master table and does not authorize downstream feature, execution, RL or live
consumers.

Satisfied by:

```text
foundations_authority_graph leaf build:
01_foundations/graphify-out/leaf_slices/foundations_authority_20260620/
```

### GFQ-20260620-001 - Visual inspection completion gate and family visual packs

Status: `leaf_built`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
```

Reason:

- The foundation completion standard now separates data-quality verdict,
  foundations completion status and visual inspection status.
- Families cannot be called `human_inspector_ready` unless they have a formal
  `visual_inspector_pack/` or an explicit waiver.
- New and updated visual inspector packs close the previous visual debt for:
  `financial`, `regime_indicators`, `short_review`, `additional`,
  `intraday_regime_features`, `Halts`, `reference` and
  `ohlcv_daily_adjusted`.
- The family status matrix now shows no active `visual_casepack_required`
  family in the current matrix.
- This changes the semantic map agents need when answering whether a data
  family is institutionalized for human inspection.

Changed paths:

```text
01_foundations/FOUNDATIONS_FAMILY_COMPLETION_STANDARD.md
01_foundations/DATA_AUDIT_QUALITY_STANDARD.md
01_foundations/VISUAL_INSPECTION_PACK_REQUIREMENTS.md
01_foundations/README.md
01_foundations/data_quality_report/
01_foundations/data_quality_report/family_status_matrix_v0_1.md
01_foundations/data_quality_report/families/additional_quality_report_v0_1.md
01_foundations/data_quality_report/families/daily_adjusted_quality_report_v0_1.md
01_foundations/data_quality_report/families/financial_quality_report_v0_1.md
01_foundations/data_quality_report/families/halts_quality_report_v0_1.md
01_foundations/data_quality_report/families/intraday_regime_features_quality_report_v0_1.md
01_foundations/data_quality_report/families/reference_quality_report_v0_1.md
01_foundations/data_quality_report/families/regime_indicators_quality_report_v0_1.md
01_foundations/data_quality_report/families/short_review_quality_report_v0_1.md
01_foundations/inspection_dossiers/additional/
01_foundations/inspection_dossiers/daily_adjusted/
01_foundations/inspection_dossiers/financial/
01_foundations/inspection_dossiers/halts/
01_foundations/inspection_dossiers/intraday_regime_features/
01_foundations/inspection_dossiers/reference/
01_foundations/inspection_dossiers/regime_indicators/
01_foundations/inspection_dossiers/short_review/
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Refresh the `foundations_authority_graph` leaf in a dedicated Graphify run.
Do not build a monolithic 01_foundations graph.
Respect .graphifyignore: graph CSV/PNG assets are evidence, not semantic graph
corpus, unless a future explicit visual-evidence slice is defined.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation visual inspection governance
```

Notes:

The refresh should capture the new completion semantics and the human-inspector
readiness state, not the binary visual evidence itself. The visual assets remain
auditable through manifests and dossiers; Graphify should index the markdown
contracts/readouts and keep heavy evidence excluded.

Satisfied by:

```text
foundations_authority_graph leaf build:
01_foundations/graphify-out/leaf_slices/foundations_authority_20260620/
```

### GFQ-20260620-002 - Data-family institutionalization contracts and audit navigation

Status: `leaf_built`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
```

Reason:

- The foundation authority layer now contains new and updated family contracts,
  dataset registries, data-consumption policies, validators and transversal
  module contracts for the data-family institutionalization work.
- This is broader than the visual-inspection gate: it defines where the
  technical data analysis, physical integrity checks, auditor navigation,
  readiness matrix and raw/derived data authority must live.
- Human and agent queries about whether a family is inspection-ready,
  production-usable, technically audited, contract-covered or source-of-truth
  governed must resolve through these documents.
- The affected docs are semantic authority inputs for the same
  `foundations_authority_graph` leaf and therefore must be refreshed together
  with the visual-gate update.

Changed paths:

```text
01_foundations/DATA_AUDIT_TOPIC_NAVIGATION.md
01_foundations/contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/financial_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/regime_indicators_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/additional_consumption_policy.md
01_foundations/data_consumption_policies/daily_adjusted_consumption_policy.md
01_foundations/data_consumption_policies/financial_consumption_policy.md
01_foundations/data_consumption_policies/ohlcv_1m_split_normalized_consumption_policy.md
01_foundations/data_consumption_policies/regime_indicators_consumption_policy.md
01_foundations/data_consumption_policies/short_review_consumption_policy.md
01_foundations/dataset_registry/additional/
01_foundations/dataset_registry/financial/
01_foundations/dataset_registry/regime_indicators/
01_foundations/dataset_registry/short_review/
01_foundations/inspection_dossiers/README.md
01_foundations/inspection_dossiers/halts/integration_notes.md
01_foundations/module_contracts/README.md
01_foundations/module_contracts/transversal_contracts_index.md
01_foundations/module_contracts/additional_contracts_index.md
01_foundations/module_contracts/additional_to_master_tables_policy_v0_1.md
01_foundations/module_contracts/data_engineering_physical_audit_standard_v0_1.md
01_foundations/module_contracts/data_folder_audit_readiness_matrix_v0_1.md
01_foundations/module_contracts/raw_data_authority_and_derivation_map.md
01_foundations/validators/README.md
01_foundations/validators/additional/
01_foundations/validators/financial/
01_foundations/validators/intraday_regime_features/
01_foundations/validators/regime_indicators/
01_foundations/validators/short_review/
```

Recommended action:

```text
Refresh the `foundations_authority_graph` leaf in the same dedicated Graphify
run as GFQ-20260620-001.
Do not build a monolithic 01_foundations graph.
Do not include physical data, CSV manifests, PNG evidence or parquet outputs in
the semantic corpus unless a future explicit evidence slice is approved.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation institutionalization governance
```

Notes:

This entry closes Graphify queue coverage for Markdown/YAML semantic authority
changes introduced by the family institutionalization work. It intentionally
does not claim that runtime evidence assets, generated CSVs, PNGs, parquet data
or scripts outside `01_foundations/` are part of this leaf.

Build result:

```text
Output:
01_foundations/graphify-out/leaf_slices/foundations_authority_20260620/

Stats:
- detected_files: 341
- detected_words: 476827
- nodes: 1002
- edges: 1381
- communities: 93
- semantic_chunks: 16
- semantic_nodes_before_build: 944
- semantic_edges_before_build: 1168
- hyperedges_before_build: 48

Validation:
- graphify diagnose multigraph passed with 0 dangling endpoints, 0 duplicate
  edges, and 0 endpoint-collapsed edge groups.
- root graph intentionally not created:
  01_foundations/graphify-out/graph.json = absent

Operational note:
- chunks 01-12 were Codex worker semantic extraction.
- chunks 13-16 were deterministic bounded structural extraction after worker
  subagents failed to write chunk files within the operational window.
- this limitation is recorded in the leaf BUILD_MANIFEST.md.
```

## Entry template

```text
### GFQ-YYYYMMDD-NNN - <title>

Status: pending | pending_leaf_build | leaf_built | pending_root_integration | closed | cancelled
Severity: LOW | MEDIUM | HIGH | CRITICAL
Slice:
Reason:
Changed paths:
Recommended action:
Root action:
Owner:
Notes:
```
