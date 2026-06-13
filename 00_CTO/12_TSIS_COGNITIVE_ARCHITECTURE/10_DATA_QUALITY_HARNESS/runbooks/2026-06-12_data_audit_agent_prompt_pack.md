# Data Audit Agent Prompt Pack - 2026-06-12

Uso: copiar el prompt `SINGLE_AGENT_DATA_AUDIT_COMPLETION` completo en una sesion Codex abierta desde `C:\TSIS_Data` con `START_CODEX_TSIS_AUTONOMOUS.ps1`.

Este prompt reemplaza el enfoque multi-agente para el siguiente run. La ejecucion inmediata debe ser un solo agente secuencial.

Correccion 2026-06-13: este prompt trabaja una sola carpeta/dataset por ejecucion y obliga a preservar la auditoria historica antes de crear artefactos nuevos.

## SINGLE_AGENT_DATA_AUDIT_COMPLETION

```text
Estas trabajando en TSIS.

DIRECTORIO:
C:\TSIS_Data

MODO DE EJECUCION:
Un solo agente autonomo, estilo SersanSistemas.
No lances ni simules varios agentes.
No paralelices escrituras de indices.
No inventes un supervisor multi-agente todavia.

OBJETIVO GENERAL:
Cerrar un dataset pendiente de la auditoria de data con calidad comparable a `daily`, `quotes`, `trades`, `minute` y `1m_split_normalized`, preservando primero la auditoria historica ya existente.

DATASET TARGET DE ESTE RUN:
1. reference

NO continues automaticamente con Halts, additional, short, financial ni regime_indicators.
Cuando termines `reference`, valida, reporta y para para revision humana.

ORDEN FUTURO DESPUES DE REVISION HUMANA:
1. reference
2. halts
3. additional
4. short
5. financial
6. regime_indicators
7. integracion final

FUERA DE ALCANCE:
E:\TSIS\data\images_Flash_Research

No inventaries, no muevas, no OCRices, no valides y no institucionalices `images_Flash_Research` en este run. No es parte del cierre de auditoria Polygon de este Harness.

RUTAS PROHIBIDAS, READ-ONLY:
- E:\TSIS\data
- C:\TSIS_Data\data
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\data
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\run
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA

No modifiques, no muevas, no renombres, no limpies, no normalices y no reorganices nada dentro de esas rutas.
Solo pueden leerse como evidencia/provenance.

AUDITORIA HISTORICA PROTEGIDA:
Antes de crear nada para el dataset target, lee y reconcilia lo que exista en:
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\auditoria\additional
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\auditoria\halts
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\auditoria\reference
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\auditoria\short
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\certification

Para `reference`, esto es obligatorio. No reaudites desde cero. Promociona y completa lo que falta en `01_foundations`.

DONDE SI PUEDE VIVIR TRABAJO NUEVO:
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\inspection\<dataset>

IMPORTANTE SOBRE ENTORNO:
Si estas en sesion autonoma YOLO desde C:\TSIS_Data, trabaja normal.
Si estas en sesion sandboxed desde fuera, usa `sandbox_permissions: "require_escalated"` para C:\TSIS_Data y E:\TSIS\data. Las lecturas sandboxed normales pueden quedarse colgadas.

LECTURA OBLIGATORIA RAIZ:
1. C:\TSIS_Data\START_HERE.md
2. C:\TSIS_Data\PROJECT_RULES.md
3. C:\TSIS_Data\AGENTS.md
4. C:\TSIS_Data\ARCHITECTURE_OVERVIEW.md
5. C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md
6. C:\TSIS_Data\VERSIONING_STANDARDS.md
7. C:\TSIS_Data\RESEARCH_PHILOSOPHY.md
8. C:\TSIS_Data\README.md
9. C:\TSIS_Data\CHANGELOG.md

LECTURA OBLIGATORIA MODULO 01:
1. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\README.md
2. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\AGENTS.md
3. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\LOCAL_RULES.md
4. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\CHANGELOG.md
5. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\inspection_dossier_model.md
6. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\auditoria_and_certification_source_hierarchy.md
7. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\data_storage_topology_and_target_state.md
8. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\event_families_and_reference_inventory.md
9. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\price_semantics_and_adjustment_policy.md
10. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\price_views_registry.md
11. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\corporate_actions_adjustment_methodology.md
12. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\external_price_comparison_caveats.md

LECTURA OBLIGATORIA CTO/HARNESS:
1. C:\TSIS_Data\00_CTO\README.md
2. C:\TSIS_Data\00_CTO\CHANGELOG.md
3. C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\README.md
4. C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\00_SHARED_HARNESS_KERNEL\agentic_harness_architecture_reference.md
5. C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\00_SHARED_HARNESS_KERNEL\harness_toolchain_traceability_contract.md
6. C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\00_SHARED_HARNESS_KERNEL\shared_run_manifest_contract.md
7. C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\00_SHARED_HARNESS_KERNEL\shared_validation_principles.md
8. C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\10_DATA_QUALITY_HARNESS\README.md
9. C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\10_DATA_QUALITY_HARNESS\historical_audit_preservation_and_promotion_contract.md
10. C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\10_DATA_QUALITY_HARNESS\data_audit_completion_artifact_contract.md
11. C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\10_DATA_QUALITY_HARNESS\runbooks\2026-06-12_overnight_data_audit_completion_harness_runbook.md

BENCHMARKS MADUROS QUE DEBES ENTENDER ANTES DE CREAR NADA:

1. daily
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\daily\README.md
- daily_inspection_readout_v0_1.md
- build_daily_inspection_pack.md
- daily_adjusted_full_universe_audit_v0_1.md
- daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md
- good_justification, flagged_case_evidence_packs, bad_case_evidence_packs, coverage_case_evidence_packs y evidence_assets.

2. quotes
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\quotes\README.md
- quotes_inspection_readout_v0_1.md
- quotes_open_casepacks_audit_v0_1.md
- build_quotes_inspection_pack.md
- READMEs locales de good_justification, flagged_case_evidence_packs, bad_case_evidence_packs, coverage_case_evidence_packs y evidence_assets.
- Manifests e imagenes globales/casepacks.

3. trades
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\trades\README.md
- build_trades_inspection_pack.md
- trades_inspection_readout_v0_1.md
- trades_global_universe_readout_v0_1.md
- trades_sampling_strategy_v0_1.md
- trades_inspection_notebook_v0_1.ipynb
- trades_universe_inspection_notebook_v0_1.ipynb
- population_evidence_packs, file_acceptance_evidence_packs, good_justification, flagged_case_evidence_packs, bad_case_evidence_packs, family_case_evidence_packs y evidence_assets.
- scripts/inspection/trades.

4. minute / ohlcv_1m_raw
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\minute\README.md
- raw_1m_lt1b_closeout_recalculation_v0_1.md
- raw_1m_schema_only_lt1b_inspection_readout_v0_1.md
- raw_1m_schema_only_lt1b_inspection_notebook_v0_1.ipynb, incluyendo celdas y outputs.
- minute_00_universe_quality_overview_v0_1.ipynb, incluyendo celdas y outputs.
- minute_01_core_quality_model_v0_1.ipynb, incluyendo celdas y outputs.
- minute_02_core_quality_population_readout_v0_1.ipynb, incluyendo celdas y outputs.
- minute_03_casepack_builder_v0_1.ipynb, preservando su rol de launcher/widget.
- minute_04_ticker_month_inspector_v0_1.ipynb, preservando widgets/selectores.
- minute_05_final_readout_v0_1.ipynb.
- core_quality_case_evidence_packs/minute_core_quality_visual_cases_v0_1.md: leer primero los 7 mapas poblacionales y despues las 60 imagenes de caso. Cada imagen debe entenderse individualmente.

5. 1m_split_normalized
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\1m_split_normalized\README.md
- ohlcv_1m_split_normalized_final_readout_v0_1.md
- ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md
- ohlcv_1m_split_normalized_pilot_readout_v0_1.md
- ohlcv_1m_split_normalized_inspection_notebook_v0_1.ipynb
- ohlcv_1m_split_normalized_full_universe_audit_notebook_v0_1.ipynb
- event_case_evidence_packs/ohlcv_1m_split_normalized_visual_inspector_pack_v0_1.md: leer mapas poblacionales y casepacks visuales.

ESTANDAR QUE DEBES COPIAR:
No basta con crear markdowns.
No basta con crear schemas.
No basta con crear un registry entry.
No basta con una tabla de conteos.

Cada dataset debe aproximarse al sistema inspector maduro:
- contratos;
- schemas;
- registry;
- consumption policy;
- validators;
- readout;
- evidence assets;
- manifests;
- scripts/builders residentes;
- notebooks inspectores si aportan navegacion humana;
- visuales/casepacks si la pregunta lo exige;
- interpretacion visual real;
- estado de consumo honesto.

REGLA SOBRE NOTEBOOKS:
Los notebooks no son almacenes de codigo.
Sirven como interfaces inspectoras, launchers, lectores, widgets y drilldown humano.
La logica pesada debe vivir en scripts residentes.
Si un notebook contiene una conclusion, esa conclusion debe quedar promovida a markdown/readout/manifest/asset.
No dejes una decision estable solo dentro de un notebook.

REGLA SOBRE IMAGENES:
Las imagenes no son decoracion.
Cada visual, panel o tabla relevante debe declarar:
- Que muestra
- Responde
- No responde
- Consecuencia

Ademas debes leer la imagen de verdad:
- donde se ve el fenomeno;
- si no se ve, decirlo;
- si el panel no prueba la causa, pedir o crear evidencia complementaria;
- no inferir solo por nombre de bucket;
- no reemplazar mapa poblacional por muestras bonitas;
- no reemplazar caso forense por conteos agregados.

TRABAJO POR DATASET:
Para el dataset target de este run:
1. Audita root fisico en modo read-only.
2. Lee auditoria historica y certification preservadas si existen.
3. Inventaria foundation existente.
4. Identifica schema real, unidad logica, unidad operacional, temporal availability y consumers.
5. Crea o actualiza scripts residentes bajo scripts/inspection/<dataset> si generas assets.
6. Crea evidence assets con manifests.
7. Crea notebooks inspectores si hacen falta para navegacion humana; si no hacen falta, justificalo.
8. Crea visuales/casepacks cuando la pregunta lo exija; si no puedes, crea gap audit visual honesto.
9. Interpreta visuales con Que muestra / Responde / No responde / Consecuencia.
10. Crea o actualiza README local, readout, build guide, contract, schema, registry, policy y validators.
11. Crea integration_notes.md.
12. No sobrepromuevas estado.
13. Para. No continues con el siguiente dataset sin revision humana.

OUTPUT MINIMO POR DATASET:
- canonical_schemas/<dataset>/...
- contract_registry/dataset_contracts/<dataset>_dataset_contract_v0_1.md
- dataset_registry/<dataset>/<dataset>_registry_entry.yaml
- data_consumption_policies/<dataset>_consumption_policy.md
- validators/<dataset>/<dataset>_validators.md
- inspection_dossiers/<dataset>/README.md
- inspection_dossiers/<dataset>/<dataset>_inspection_readout_v0_1.md
- inspection_dossiers/<dataset>/build_<dataset>_inspection_pack.md
- inspection_dossiers/<dataset>/evidence_assets/...
- inspection_dossiers/<dataset>/integration_notes.md
- scripts/inspection/<dataset>/... si hubo generador/builder.

ESTADOS PERMITIDOS:
- not_started
- inventory_only
- foundation_minimal
- modernization_gap_documented
- modern_dossier_partial
- modern_dossier_complete
- blocked_needs_human_decision
- not_consumable_no_active_consumer

PROHIBIDO:
Usar `done`, `clean`, `ok` o `closed` como estado final sin contrato, consumidor y evidencia.

INTEGRACION FINAL:
No hagas integracion final multi-dataset en este run.

Solo actualiza indices compartidos si son estrictamente necesarios para el dataset target y si no contradicen el gate de revision humana:
- inspection_dossiers/README.md
- contract_registry/dataset_contracts/README.md
- dataset_registry/README.md
- data_consumption_policies/README.md
- validators/README.md
- canonical_schemas/README.md si aplica.

Actualiza tambien:
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\CHANGELOG.md

No crees `data_audit_completion_final_report_2026-06-13.md` salvo que el humano pida explicitamente integracion final.

VALIDACIONES FINALES:
- YAML parsea.
- No hay referencias rotas evidentes.
- No hay TODO/TBD sin bloqueo formal.
- No hay C:\Users ni C:\tmp en artefactos finales aceptados.
- No hay outputs aceptados fuera del proyecto.
- No se ha modificado E:\TSIS\data ni C:\TSIS_Data\data.
- Los visuales no son mudos.
- Los notebooks no son unica fuente de verdad.
- git -C C:\TSIS_Data status -sb revisado al final.

REPORTE FINAL:
Entrega un resumen con:
- benchmark leido y estandar aplicado;
- datasets completados;
- datasets parciales;
- datasets bloqueados;
- archivos principales creados/modificados;
- visuales/notebooks generados o gaps visuales;
- verificaciones ejecutadas;
- rutas protegidas confirmadas como no tocadas;
- siguiente accion humana.
```
