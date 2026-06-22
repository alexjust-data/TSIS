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

### GFQ-20260622-008 - Master daily table v0.1 initial materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
daily_price_views_graph
event_state_reconstruction_graph
module_test_governance_graph
```

Reason:

- Added `master_daily_table_v0_1` as the sixth CAPA 1 output table.
- Added contract, schema, registry entry, consumption policy, validators,
  materializer and pytest contract coverage.
- Materialized a partitioned parquet dataset under:

```text
E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1
```

- The table preserves explicit `daily_raw`, `split_normalized` and `adjusted`
  price views and links expected coverage, corporate actions and family-level
  certification gates.

### GFQ-20260622-007 - Dataset certification matrix v0.1 initial materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
data_quality_report_graph
module_test_governance_graph
```

Reason:

- Added `dataset_certification_matrix_v0_1` as the fifth CAPA 1 output table.
- Added contract, schema, registry entry, consumption policy, validators,
  materializer and pytest contract coverage.
- Added dedicated validators for `ohlcv_daily_adjusted` and
  `ohlcv_1m_split_normalized` to satisfy the family status matrix evidence
  surface.
- Materialized a compact parquet table under:

```text
E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix/dataset_certification_matrix_v0_1.parquet
```

- The table normalizes `family_status_matrix_v0_1.md` into a family-level
  gate and verifies linked evidence surfaces.

### GFQ-20260622-006 - Corporate actions table v0.1 initial materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
corporate_actions_adjustment_graph
module_test_governance_graph
```

Reason:

- Added `corporate_actions_table_v0_1` as the fourth CAPA 1 output table.
- Added contract, schema, registry entry, consumption policy, validators,
  materializer and pytest contract coverage.
- Materialized a compact parquet table under:

```text
E:/TSIS/data/data_foundation_outputs/corporate_actions_table/corporate_actions_table_v0_1.parquet
```

- The table preserves `reference` as primary source and `additional` as
  secondary/reconciliation source.

Materialized:

```text
rows = 104757
tickers = 3621
instrument_ids = 3497
action_type_counts = dividend: 92033, split: 6630, ticker_change: 6094
source_system_counts = additional: 52490, reference: 52267
first_action_date = 1969-12-31
last_action_date = 2027-06-15
build_run_id = corporate_actions_table_v0_1_20260622T144845Z
output_sha256 = 01989eb301a2cdd83e297fbf6384e0bd4d5b4fb300bdccee6b1adbde87d5e4ce
hard_fail_count = 0
```

Test evidence:

```text
C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_four_tables_v0_1/
tests = 16
passed = 16
failed = 0
skipped = 0
```

Changed paths:

```text
01_foundations/canonical_schemas/outputs/corporate_actions_table_schema_contract.md
01_foundations/contract_registry/dataset_contracts/corporate_actions_table_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/corporate_actions_table_consumption_policy.md
01_foundations/dataset_registry/outputs/corporate_actions_table_registry_entry.yaml
01_foundations/validators/outputs/corporate_actions_table_validators.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
scripts/materialize_corporate_actions_table.py
tests/data_foundation_outputs/test_corporate_actions_table_contract.py
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include in the next Data Foundation outputs/corporate-actions leaf refresh.
Link this node to daily_adjusted, master_daily_table, event_engine and
data_quality_report.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

- This table is context and adjustment lineage, not final adjusted price output.

### GFQ-20260622-005 - Expected data calendar v0.1 initial materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
module_test_governance_graph
```

Reason:

- Added `expected_data_calendar_v0_1` as the third CAPA 1 output table.
- Added contract, schema, registry entry, consumption policy, validators,
  materializer and pytest contract coverage.
- Materialized a partitioned parquet dataset under:

```text
E:/TSIS/data/data_foundation_outputs/expected_data_calendar/expected_data_calendar_v0_1
```

- The table is a coverage expectation denominator, not proof of physical
  presence or quality.

Materialized:

```text
rows = 29029152
dataset_families = daily_raw, ohlcv_1m_raw, quotes_raw, trades_raw
rows_per_family = 7257288
tickers = 4824
first_session = 2005-01-03
last_session = 2025-12-31
parquet_file_count = 84
tree_sha256 = 1c7571cdcefc1ffd3f0f6cda921d32d64dee33cc41c3676809686c1bc575a57f
build_run_id = expected_data_calendar_v0_1_20260622T141019Z
hard_fail_count = 0
```

Test evidence:

```text
C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_instrument_master_market_calendar_expected_data_calendar_v0_1/
tests = 12
passed = 12
failed = 0
skipped = 0
```

Changed paths:

```text
01_foundations/canonical_schemas/outputs/expected_data_calendar_schema_contract.md
01_foundations/contract_registry/dataset_contracts/expected_data_calendar_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/expected_data_calendar_consumption_policy.md
01_foundations/dataset_registry/outputs/expected_data_calendar_registry_entry.yaml
01_foundations/validators/outputs/expected_data_calendar_validators.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
scripts/materialize_expected_data_calendar.py
tests/data_foundation_outputs/test_expected_data_calendar_contract.py
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include in the next Data Foundation outputs leaf refresh. Link this node to
instrument_master, market_calendar, dataset_certification_matrix and
data_quality_report.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

- Future data_quality_report work must join expected rows against actual
  family presence/quality evidence.

### GFQ-20260622-004 - Data Foundation output contract tests

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
module_test_governance_graph
```

Reason:

- Added executable pytest contract tests for `instrument_master_v0_1` and
  `market_calendar_v0_1`.
- Added a pytest harness that writes dated institutional evidence under
  `C:/TSIS_Data/tests/test_runs/`.
- The tests validate manifest/hash integrity, contract links, schema/lineage,
  hard contractual gates and source reconciliation.
- Executed the first two table tests successfully.

Changed paths:

```text
01_TSIS_backtest_SmallCaps/tests/conftest.py
01_TSIS_backtest_SmallCaps/tests/_helpers/__init__.py
01_TSIS_backtest_SmallCaps/tests/_helpers/data_foundation.py
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_instrument_master_contract.py
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_market_calendar_contract.py
01_TSIS_backtest_SmallCaps/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md
C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_instrument_master_market_calendar_v0_1/
```

Test evidence:

```text
C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_instrument_master_market_calendar_v0_1/
```

Result:

```text
tests = 8
passed = 8
failed = 0
skipped = 0
```

Recommended action:

```text
Include in the next foundations/test-governance leaf refresh. Link the test
harness to future Data Foundation output tables before they are promoted.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
Modulo 01 / Data Foundation test governance
```

Notes:

- These are offline tests. Third-party live checks remain a future opt-in layer.

### GFQ-20260622-003 - Data root and test artifact topology clarification

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_storage_topology_graph
module_test_governance_graph
```

Reason:

- Clarified that `E:/TSIS/data/` is the active preferred data plane.
- Clarified that `E:/TSIS/data/data_foundation_outputs/` is for governed CAPA 1
  table outputs, not test execution artifacts.
- Clarified that `C:/TSIS_Data/tests/test_runs/`, `fixtures/` and
  `third_party_evidence/` are the roots for test outputs, small test data and
  cached external evidence.
- Reclassified `C:/TSIS_Data/data/` as legacy/quarantine until a migration audit
  proves which families can be removed.
- No deletion of legacy data was performed.

Changed paths:

```text
tests/README.md
tests/test_runs/README.md
tests/fixtures/README.md
tests/third_party_evidence/README.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/data_storage_topology_and_target_state.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Include in the next foundations/storage/test-governance leaf refresh. Link this
entry to the future migration audit for C:/TSIS_Data/data.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
Modulo 01 / Data storage and test governance
```

Notes:

- A lightweight path check showed counterparts in `E:/TSIS/data` for
  `additional`, `quotes`, `short`, `short_review` and
  `trades_ticks_prod_2005_2026`.
- `trades_ticks_2019_2025` was present in `C:/TSIS_Data/data` and did not have
  an immediate same-name counterpart in `E:/TSIS/data` during the check.
- Many existing docs/scripts still reference `C:/TSIS_Data/data`; deletion must
  wait for a migration audit.

### GFQ-20260622-002 - SmallCaps test topology scaffold

Status: `pending_leaf_build`

Severity: `MEDIUM`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
module_test_governance_graph
```

Reason:

- Added module-level test documentation under `01_TSIS_backtest_SmallCaps/tests/`.
- The scaffold defines where executable tests should live for Data Foundation
  outputs, foundations governance, pipelines, research, event engine, strategy
  engine, execution and offline RL preparation.
- The Data Foundation output test README formalizes the five minimum validation
  layers for institutional tables: schema contract, manifest/hash,
  source reconciliation, third-party evidence and adversarial/mutation checks.
- No executable validators were added in this entry.

Changed paths:

```text
01_TSIS_backtest_SmallCaps/tests/README.md
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/README.md
01_TSIS_backtest_SmallCaps/tests/foundations/README.md
01_TSIS_backtest_SmallCaps/tests/pipelines/README.md
01_TSIS_backtest_SmallCaps/tests/research/README.md
01_TSIS_backtest_SmallCaps/tests/event_engine/README.md
01_TSIS_backtest_SmallCaps/tests/strategy_engine/README.md
01_TSIS_backtest_SmallCaps/tests/execution/README.md
01_TSIS_backtest_SmallCaps/tests/rl_preparation/README.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Include in the next foundations/test-governance leaf refresh. Link the
`data_foundation_outputs/` tests to the CAPA 1 output contracts and table
materialization manifests.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
Modulo 01 / Data Foundation test governance
```

Notes:

- Existing `tests/test_price_views.py` remains in place and was not moved.
- This entry should be followed by executable pytest contracts for
  `instrument_master_v0_1` and `market_calendar_v0_1`.

### GFQ-20260622-001 - Market calendar v0.1 initial materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
data_foundation_outputs_graph
daily_intraday_calendar_graph
```

Reason:

- `market_calendar_v0_1` was defined as the second compact CAPA 1 output
  table.
- Contract, schema, registry entry, consumption policy, validator and
  materializer were added.
- The first materialized parquet was written under:

```text
E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet
```

- The output reconciles to the local official calendar candidate:

```text
rows = 5283
calendar = XNYS
timezone = America/New_York
first_session = 2005-01-03
last_session = 2025-12-31
early_close_sessions = 45
source_parquet_sha256 = 8aac3ea4f7fbcaf6c394320f53acc1524bf5e5e3addbcd48ef31718bc0214228
output_sha256 = 96bd60c124e6552d269f8846205ed28bf6e58881453a5bbb4f73ced0657b56d5
hard_fail_count = 0
```

- The output is an XNYS session calendar. It does not encode halts, liquidity,
  venue outages or dates after `2025-12-31`.

Changed paths:

```text
01_foundations/canonical_schemas/outputs/market_calendar_schema_contract.md
01_foundations/contract_registry/dataset_contracts/market_calendar_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/market_calendar_consumption_policy.md
01_foundations/dataset_registry/outputs/market_calendar_registry_entry.yaml
01_foundations/validators/outputs/market_calendar_validators.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
scripts/materialize_market_calendar.py
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include in the next foundations/calendar/output leaf refresh. Link it to
instrument_master, expected_data_calendar, master_daily_table and
master_intraday_bar_table.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

### GFQ-20260621-003 - Instrument master v0.1 initial materialization

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
reference_identity_graph
data_foundation_outputs_graph
```

Reason:

- `instrument_master_v0_1` was defined as the first compact CAPA 1 output
  table.
- Contract, schema, registry entry, consumption policy, validator and
  materializer were added.
- The first materialized parquet was written under:

```text
E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet
```

- The output reconciles exactly to `lt1b_universe_v0_1`:

```text
rows = 4824
tickers = 4824
hard_fail_count = 0
duplicate_ticker_count = 0
sha256 = 69104387d2607306c3fa1740573d130db5e7c30b1d1527d3ee8a8d2b4d53c2d2
```

- The table is ticker-grain for the `<1B>` operational universe. It does not
  resolve final economic continuity or daily fully point-in-time market-cap
  membership.

Changed paths:

```text
01_foundations/canonical_schemas/outputs/instrument_master_schema_contract.md
01_foundations/contract_registry/dataset_contracts/instrument_master_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/instrument_master_consumption_policy.md
01_foundations/dataset_registry/outputs/instrument_master_registry_entry.yaml
01_foundations/validators/outputs/instrument_master_validators.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
scripts/materialize_instrument_master.py
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include in the next foundations/reference identity leaf refresh. Keep linked
to the outputs target contract and the data storage topology decision.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

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

### GFQ-20260621-001 - Homogeneous Graphify semantic extraction remediation

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
```

Reason:

- `foundations_authority_20260620` is materialized, valid, consultable and
  diagnostically clean, but it is not a fully homogeneous semantic extraction.
- Chunks `01-12` were produced by Codex worker semantic extraction.
- Chunks `13-16` were produced by deterministic bounded structural extraction
  after worker subagents failed to write chunk files within the operational
  window.
- That fallback was intentionally documented, but it means the current leaf
  must not be represented as final institutional Graphify parity.

Changed paths:

```text
01_foundations/graphify-out/leaf_slices/foundations_authority_20260620/BUILD_MANIFEST.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_foundations/README.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Reopen the Graphify build work.
Re-extract chunks 13-16 using the same worker semantic-extraction standard as
chunks 01-12, splitting them into smaller chunks if needed.
Regenerate foundations_authority_graph as a new dated leaf.
Update BUILD_MANIFEST.md, GRAPHIFY_REFRESH_QUEUE.md, README.md and CHANGELOG.md.
Remove the limitation only after all chunks have homogeneous semantic extraction
evidence.
```

Root action:

```text
No root graph yet.
Do not integrate this leaf into a root graph until the homogeneous extraction
remediation is complete or an explicit waiver is documented.
```

Owner:

```text
Modulo 01 / Data Foundation Graphify governance
```

Notes:

Current state:

```text
graph materialized = yes
graph valid JSON / consultable = yes
root graph = no, by protocol
fully homogeneous Graphify semantic extraction = no
institutional final without caveat = no
```

This entry exists so the remediation is not left only in conversation memory.

### GFQ-20260621-002 - Data Foundation outputs target contract

Status: `pending_leaf_build`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
daily_ohlcv_graph
reference_identity_graph
microstructure_quotes_trades_graph
additional_fundamentals_news_graph
```

Reason:

- A new CAPA 1 output target contract was added under `module_contracts/outputs/`.
- The contract defines how Data Foundation outputs work together when an event
  is evaluated.
- It affects master table design, reference identity, market calendar,
  corporate actions, daily/intraday bars, microstructure sidecars, context
  sidecars and quality gates.
- It now fixes the common physical landing root for governed CAPA 1 outputs:
  `E:/TSIS/data/data_foundation_outputs/`.
- It distinguishes clean Data Foundation output tables from append-only live
  ingestion logs such as `E:/TSIS/data/live_ingestion/raw_alert_log/`.
- It now also records the missing governed live table for low-latency corporate
  event alerts: offerings, private placements, warrants, SEC 8-K/6-K/424B
  filings, reverse splits and comparable smallcap catalysts.
- It includes a DAS Trader / NewsWare investigation note: DAS/NewsWare is a
  candidate live alert source, but public DAS API documentation is not enough
  evidence to assume governed API ingestion through DAS Trader Pro API.
- The alert-table semantics distinguish historical/contextual news from
  `received_utc`-tracked live alerts and should be visible in downstream Event
  Engine and Strategy Research graph slices.
- The Graphify table-design protocol classifies a new master table contract as
  `HIGH`.

Changed paths:

```text
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/data_storage_topology_and_target_state.md
01_foundations/module_contracts/README.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Include the new outputs contract in the next foundations_authority_graph rebuild.
When the specialized graph slices are materialized, include the contract as a
cross-slice anchor for daily/intraday, reference identity, microstructure and
additional/context table design.
Do not create a monolithic 01_foundations graph.
```

Root action:

```text
No root graph yet.
Do not integrate into a root graph until GFQ-20260621-001 is remediated or an
explicit waiver is documented.
```

Owner:

```text
Modulo 01 / Data Foundation output governance
```

Notes:

The contract records that `market_calendar_official_XNYS_20050101_20251231`
is locally reproducible byte-for-byte from
`scripts/agent05_build_market_calendar_official.py` with
`exchange_calendars 4.13.1`, but also states that the artifact is not a raw
download from NYSE.

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
