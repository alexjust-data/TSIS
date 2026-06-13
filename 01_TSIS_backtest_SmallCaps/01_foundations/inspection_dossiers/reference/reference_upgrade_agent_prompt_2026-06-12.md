# Prompt para agente - Upgrade moderno completo de Reference

Estado actualizado 2026-06-13:

Este prompt queda superseded para el alcance `foundation_promotion`.

El upgrade moderno de `reference` fue ejecutado mediante:

- `scripts/inspection/reference/build_reference_inspection_pack.py`
- `reference_inspection_readout_v0_2.md`
- `build_reference_inspection_pack.md`
- `reference_casepacks_traceability_audit_v0_1.md`
- `integration_notes.md`
- `evidence_assets/run_manifest.json`

No lanzar este prompt como tarea pendiente sin revisar primero el readout v0.2.

Copia este prompt en un agente Codex iniciado en `C:\TSIS_Data` con permisos autonomos.

```text
Tienes que ejecutar el upgrade moderno completo del dossier `reference` en TSIS.

DIRECTORIO DE TRABAJO:
C:\TSIS_Data

IMPORTANTE SOBRE PERMISOS:
- Si estas en modo YOLO dentro de C:\TSIS_Data, trabaja directamente.
- Si estas en una sesion sandboxed cuyo workspace principal no es C:\TSIS_Data, usa `sandbox_permissions: "require_escalated"` para toda lectura/escritura bajo C:\TSIS_Data y E:\TSIS\data.
- No intentes lecturas sandboxed normales de C:\TSIS_Data si el entorno no lo permite; en sesiones previas se quedaron colgadas.

OBJETIVO:
Elevar `reference` desde promocion foundation minima a dossier inspector moderno, con calidad comparable a `daily`, `quotes`, `trades`, `minute` y `1m_split_normalized`.

NO OBJETIVO:
- No mover, reordenar, borrar ni reescribir evidencia historica en `01_research`.
- No modificar los datos fisicos de `E:\TSIS\data\reference`.
- No declarar `reference` como alpha, feature productiva, remap continuity service, live, RL ni universe final.
- No usar `ticker_change` como continuidad economica cerrada.

LECTURA OBLIGATORIA:
Lee completos antes de editar:

1. C:\TSIS_Data\PROJECT_RULES.md
2. C:\TSIS_Data\AGENTS.md
3. C:\TSIS_Data\ARCHITECTURE_OVERVIEW.md
4. C:\TSIS_Data\CHANGELOG.md
5. C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md
6. C:\TSIS_Data\VERSIONING_STANDARDS.md
7. C:\TSIS_Data\RESEARCH_PHILOSOPHY.md
8. C:\TSIS_Data\README.md
9. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\README.md
10. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\AGENTS.md
11. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\LOCAL_RULES.md
12. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\CHANGELOG.md
13. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\inspection_dossier_model.md
14. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\auditoria_and_certification_source_hierarchy.md
15. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\evidence_model.md
16. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\bad_evidence_and_rehabilitation.md
17. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\policy_explanation_standard.md
18. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\README.md
19. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\reference\README.md
20. C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\reference\reference_modernization_gap_audit_2026-06-12.md

BENCHMARKS A LEER PARA IMITAR CALIDAD:
Lee como minimo:

- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\daily\README.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\quotes\README.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\quotes\quotes_inspection_readout_v0_1.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\quotes\quotes_open_casepacks_audit_v0_1.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\trades\README.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\minute\README.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\1m_split_normalized\README.md

REFERENCE ACTUAL A LEER:

- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\reference\reference_institutional_closeout_v0_1.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\reference_dataset_contract_v0_1.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\reference_consumption_policy.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\reference\reference_registry_entry.yaml
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\validators\reference\reference_validators.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\reference\*.md

FUENTES HISTORICAS OBLIGATORIAS:

Auditoria:
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\auditoria\reference\01_contrato_reference.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\auditoria\reference\02_diseno_implementacion_reference_v2.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\auditoria\reference\03_reference_root_cause_audit_phase1_closeout.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\auditoria\reference\04_reference_closeout.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\auditoria\reference\04_reference_causal_overlay_closeout.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\auditoria\reference\cache_v2\manifest.json

Certification:
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\certification\reference\00_reference_current_state.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\certification\reference\01_reference_causal_value.md
- C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\certification\reference\02_reference_closeout.md

DATOS FISICOS:
- Root actual: E:\TSIS\data\reference
- No modificar este root. Solo leer.

TAREAS:

1. Crear scripts residentes bajo:
   C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\inspection\reference\

   Minimo:
   - audit_reference_foundation_physical_root.py
   - export_reference_population_visuals.py
   - export_reference_casepacks.py
   - build_reference_visual_readout.py

2. Crear evidence assets bajo:
   C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\reference\evidence_assets\

   Minimo:
   - historical_cache_inventory/
   - physical_root_audit/
   - population_visual_overview/
   - identity/
   - corporate_actions/
   - causal_overlays/

3. Auditar root fisico actual `E:\TSIS\data\reference`:
   - presencia de subfamilias;
   - conteo de files/dirs;
   - schema por subfamilia;
   - filas por muestra o metadata;
   - claves logicas;
   - fechas parseables;
   - payload-empty vs payload-real;
   - errores hard/review.

4. Convertir caches historicos en evidence assets modernos:
   - no mover caches historicos;
   - crear summaries/exports bajo `01_foundations`;
   - mantener mapping claro entre path historico y output moderno.

5. Crear population visuals con manifests:
   - endpoint/download status;
   - identity quality;
   - listing presence/gaps;
   - instrument/exchange mix;
   - event payload/event type;
   - splits payload/ratios;
   - dividends payload/type;
   - causal alignment matrix;
   - events vs halts;
   - events vs quotes;
   - splits vs trades/daily/1m.

6. Crear casepacks versionados:
   - good_justification/reference_good_cases_v0_1.md
   - flagged_case_evidence_packs/reference_review_cases_v0_1.md
   - bad_case_evidence_packs/reference_bad_identity_cases_v0_1.md
   - causal_case_evidence_packs/reference_causal_overlay_cases_v0_1.md
   - coverage_case_evidence_packs/reference_presence_coverage_cases_v0_1.md

   Cada casepack debe tener manifest CSV y, cuando haya imagenes, deben estar embebidas con:
   - Que muestra
   - Responde
   - No responde
   - Consecuencia

7. Crear:
   - reference_inspection_readout_v0_2.md
   - build_reference_inspection_pack.md
   - reference_casepacks_traceability_audit_v0_1.md

8. Actualizar:
   - inspection_dossiers/reference/README.md
   - inspection_dossiers/README.md, seccion Reference y madurez relativa
   - reference_dataset_contract_v0_1.md si cambia semantica
   - reference_consumption_policy.md si cambia consumo
   - reference_registry_entry.yaml si cambia evidencia o estado
   - validators/reference/reference_validators.md si cambian outputs del runner
   - CHANGELOG.md del modulo 01

CRITERIOS DE ACEPTACION:

- No hay scripts ni outputs fuera de C:\TSIS_Data salvo datos leidos en E:\TSIS\data.
- No se modifica `01_research` ni `E:\TSIS\data\reference`.
- Todo asset activo esta consumido por algun markdown o manifest.
- Todo markdown nuevo enlaza sus fuentes.
- El readout v0.2 empieza general-a-particular.
- Cada visual/caso tiene `Que muestra / Responde / No responde / Consecuencia`.
- El estado final no sobrepromueve `reference`.
- Si queda deuda, queda declarada con nombre, razon y siguiente accion.
- Actualizas changelog.

RESULTADO FINAL QUE DEBES REPORTAR:

- archivos creados;
- scripts creados;
- assets creados;
- conteos principales;
- cambios de madurez;
- limitaciones;
- si reference queda o no a paridad con `quotes/trades/daily/1m`;
- siguiente bloque recomendado despues de reference.
```
