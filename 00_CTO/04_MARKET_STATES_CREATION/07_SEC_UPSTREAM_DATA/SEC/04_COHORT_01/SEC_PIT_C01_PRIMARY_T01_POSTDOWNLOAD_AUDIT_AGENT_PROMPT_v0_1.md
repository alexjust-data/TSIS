# SEC PIT C01 Primary T01 post-download audit agent prompt v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `EXECUTABLE_AGENT_HANDOFF_PROMPT` |
| `document_status` | `READY_WAITING_FOR_TERMINAL_MANIFEST` |
| `created_at` | `2026-08-15` |
| `authorized_scope` | `C01_T01_FIRST_250_TICKER_ROWS_ONLY` |
| `run_id` | `sec_pit_c01_primary_t01_0250_v0_1_20260814` |
| `run_root` | `D:/TSIS/fundamental_context/sec_pit_v0_1/runs/sec_pit_c01_primary_t01_0250_v0_1_20260814` |

## 1. Copy/paste prompt

```text
Trabajas en C:\TSIS_Data, en la rama activa existente. Tu tarea es auditar y
certificar, sin ampliar el alcance ni iniciar nuevas descargas, el run SEC PIT:

run_id
= sec_pit_c01_primary_t01_0250_v0_1_20260814

run_root
= D:\TSIS\fundamental_context\sec_pit_v0_1\runs\sec_pit_c01_primary_t01_0250_v0_1_20260814

object_root
= D:\TSIS\fundamental_context\sec_pit_v0_1\objects

IMPORTANTE: no confundas este run con el replay de percentiles de Trading
Activity Binding A. El mensaje `240/240 blocks`, `2,400/2,400 sessions` y
`3,351,960,000 percentile cells, mismatches=0` pertenece a Binding A y no
certifica ninguna descarga SEC.

Antes de actuar, cumple AGENTS.md, el orden de lectura raíz, las reglas locales
de 00_CTO y 01_TSIS_DATA_FOUNDATION y LONG_RUNNING_OPERATIONS_CONTRACT.md.
Trabaja solo en la rama existente; preserva cambios ajenos y no escribas en
main. Graphify es un mapa, no la autoridad terminal.

OBJETIVO Y MOTIVO DE LA DESCARGA

Este run descarga los documentos SEC primarios seleccionados por
sec_pit_predownload_control_v0_2 para las primeras 250 filas autorizadas y
elegibles de la cohorte C01, ordenada desde las observaciones más recientes del
universo de 4.824 ticker rows. Su propósito es:

1. obtener evidencia primaria SEC content-addressed y SHA-256 para resolver
   posteriormente shares outstanding y owner-exclusion float de forma PIT;
2. comprobar a escala real integridad, reanudación, fallbacks, latencia,
   retries, 404/HTTP y consumo físico de almacenamiento;
3. sustituir proyecciones teóricas por bytes y distribuciones observados;
4. medir blockers y riesgos antes de decidir si se autoriza otra tranche de
   C01 o cualquier cohorte posterior.

No es una descarga de 2.400 tickers. La autorización exacta es 250 ticker rows
y 127.946 documentos planificados. No autoriza las otras 499 filas elegibles de
C01, las 75 filas detenidas por lifecycle/security, las cohortes C02-C05, la
resolución downstream de O/S/float ni promoción institucional.

LECTURA MÍNIMA OBLIGATORIA

1. C:\TSIS_Data\00_CTO\04_MARKET_STATES_CREATION\_DESCAGRA_DATOS_NECESARIA_\SEC_PIT_4824_DESCENDING_ACQUISITION_EXECUTION_PLAN_v0_1.md
2. C:\TSIS_Data\00_CTO\04_MARKET_STATES_CREATION\_DESCAGRA_DATOS_NECESARIA_\SEC_PIT_4824_PRELAUNCH_AUDIT_CORRECTIONS_READOUT_v0_1.md
3. C:\TSIS_Data\00_CTO\04_MARKET_STATES_CREATION\_DESCAGRA_DATOS_NECESARIA_\SEC_PIT_C01_PRIMARY_TRANCHE_01_AUTHORIZATION_AND_LAUNCH_READOUT_v0_1.md
4. C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\inspection_dossiers\sec_pit\SEC_PIT_4824_DESCENDING_PREFLIGHT_READOUT_v0_1.md
5. C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\inspection_dossiers\sec_pit\SEC_PIT_PREDOWNLOAD_CONTROL_SEVEN_CASE_READOUT_v0_1.md
6. C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\sec_pit\sec_pit_storage_root_and_legacy_pilot_decision_v0_1.md
7. C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\sec_pit_primary_download_authorization_c01_t01_0250_v0_1_20260814.json
8. C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\authorization.py
9. C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\predownload_control.py
10. C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\run_authorized_primary_acquisition_v0_2.py
11. C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\tests\test_sec_pit_authorization.py
12. C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\tests\test_sec_pit_authorized_acquisition_scope.py

EVIDENCIA RUNTIME OBLIGATORIA

- D:\TSIS\fundamental_context\sec_pit_v0_1\runs\sec_pit_c01_primary_t01_0250_v0_1_20260814\pre_manifest.json
- D:\TSIS\fundamental_context\sec_pit_v0_1\runs\sec_pit_c01_primary_t01_0250_v0_1_20260814\pid_manifest.json
- D:\TSIS\fundamental_context\sec_pit_v0_1\runs\sec_pit_c01_primary_t01_0250_v0_1_20260814\heartbeat_latest.json
- D:\TSIS\fundamental_context\sec_pit_v0_1\runs\sec_pit_c01_primary_t01_0250_v0_1_20260814\heartbeat.jsonl
- D:\TSIS\fundamental_context\sec_pit_v0_1\runs\sec_pit_c01_primary_t01_0250_v0_1_20260814\acquisition.jsonl
- D:\TSIS\fundamental_context\sec_pit_v0_1\runs\sec_pit_c01_primary_t01_0250_v0_1_20260814\document_performance.jsonl
- D:\TSIS\fundamental_context\sec_pit_v0_1\runs\sec_pit_c01_primary_t01_0250_v0_1_20260814\run.log
- D:\TSIS\fundamental_context\sec_pit_v0_1\runs\sec_pit_c01_primary_t01_0250_v0_1_20260814\final_manifest.json
- C:\TSIS_Data\runtime\sec_pit_4824_descending_acquisition_v0_1\metadata_gate\cohort_01_v0_2\final_manifest.json
- C:\TSIS_Data\runtime\sec_pit_4824_descending_acquisition_v0_1\metadata_gate\cohort_01_v0_2\document_selection_plan_v0_2.parquet
- C:\TSIS_Data\runtime\sec_pit_4824_descending_acquisition_v0_1\metadata_gate\cohort_01_v0_2\gate_matrix.parquet

HARD STOP INICIAL

No declares COMPLETE ni empieces la certificación terminal si falta
final_manifest.json, si el wrapper sigue vivo o si el manifest no presenta un
estado terminal. En ese caso emite únicamente:

AUDIT_NOT_STARTED_RUN_NOT_TERMINAL

con la evidencia exacta y no modifiques el run. No mates, relances ni reanudes
el proceso. No uses el heartbeat como sustituto del final manifest.

AUDITORÍA REQUERIDA CUANDO EL RUN SEA TERMINAL

1. Verifica por hash que autorización, premanifest, metadata gate, selection
   plan, código y object root coinciden con el alcance congelado.
2. Reconstruye la lista autorizada exacta: primeros 250 ticker rows elegibles y
   127.946 documentos. Prueba que ninguna de las otras 574 filas C01 entró.
3. Reconcilia acquisition.jsonl contra el plan por identidad y URL; detecta
   faltantes, extras, duplicados, estados no terminales y conflictos.
4. Recalcula fetched, skipped_complete, failed, retries, HTTP 429, 404/fallbacks,
   bytes y ticker completion; no aceptes únicamente los totales del manifest.
5. Verifica que cada objeto FETCHED exista bajo el CAS, que tamaño y SHA-256
   coincidan y que no haya colisiones. Haz verificación completa si es viable;
   si no lo es, no llames a la muestra certificación integral y declara la
   cobertura exacta de muestreo.
6. Comprueba atomicidad y semántica de resume: no overwrite del CAS, no segundo
   writer, input hashes estables y ausencia de mezcla de versiones.
7. Calcula distribuciones observadas P50/P95/MAX de bytes/documento,
   documentos/ticker, bytes/ticker, latencia y retries; reporta throughput,
   tiempo total, disco inicial/final y peak RSS si la evidencia lo permite.
8. Clasifica fallos y fallbacks por tipo, formulario, año, ticker y accession.
   Todo unresolved debe conservar blocker y retry action explícitos.
9. Ejecuta los tests dirigidos SEC sin red. No hagas requests a SEC durante la
   auditoría.
10. Determina separadamente:

   ACQUISITION_INTEGRITY_GATE
   SCOPE_MEMBERSHIP_GATE
   CAS_HASH_GATE
   RESUME_LINEAGE_GATE
   PERFORMANCE_AND_STORAGE_READOUT
   DOWNSTREAM_READINESS_GATE

El veredicto global solo puede ser PASS si todos los hard gates pasan. Un PASS
autoriza como máximo preparar un gate humano para el siguiente paso; nunca
autoriza automáticamente otra tranche, O/S/float resolution o promoción.

ARTEFACTOS QUE DEBES CREAR

En Data Foundation, crea un auditor reproducible y tests si aún no existen.
Emite un readout versionado en:

C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\inspection_dossiers\sec_pit\

y actualiza, cuando corresponda:

- el readout de lanzamiento C01 T01;
- el plan descendente 4.824;
- README y CHANGELOG de Data Foundation y del dossier SEC;
- CURRENT_STATUS_AND_HANDOFF vigente de Market States solo para el estado del
  lane SEC, sin alterar el gate Trading Activity;
- la cola Graphify más cercana o el leaf oficial, conforme a AGENTS.md.

El readout debe registrar paths, SHA-256, commit/dirty state, comandos, versión
de Python/DuckDB, métricas recalculadas, limitaciones y la decisión exacta sobre
qué sigue permitido y qué continúa prohibido.

SALIDA FINAL AL HUMANO

Explica primero el resultado, luego la evidencia. Distingue claramente:

- descarga SEC T01 de 250 ticker rows / 127.946 documentos;
- replay Binding A de 2.400 sesiones / 240 bloques;
- estado de autorización del resto de C01 y C02-C05.

No afirmes que “la descarga SEC de 2.400 terminó” salvo que exista otro run
independiente, autorizado y con manifest terminal que lo demuestre.
```

## 2. State when this prompt was written

At `2026-08-15T08:39:50Z` the SEC run was still alive and had no
`final_manifest.json`:

```text
status              = RUNNING
progress            = 124,834 / 127,946
remaining           = 3,112 documents
failed              = 0
retry_count          = 729
http_429_count       = 0
wrapper_pid          = 31868 alive
```

This state is informational only. The future auditor must read the terminal
artifacts anew and must not treat these interim values as final evidence.
