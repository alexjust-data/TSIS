# TSIS Root Test Topology

Este directorio reserva los tests institucionales del monorepo completo.

No sustituye los tests locales de cada modulo. Su funcion es comprobar reglas que
cruzan fronteras entre `00_CTO`, `01_TSIS_DATA_FOUNDATION`,
`04_TSIS_webSocket_SmallCaps` y `05_TSIS_Offline_RL`.

## Si no recuerdas nada, empieza aqui

Esta es la ruta de recuperacion operativa para humanos y agentes futuros.

1. Leer este archivo completo:

```text
C:/TSIS_Data/tests/README.md
```

2. Si la pregunta es global del monorepo, ir a:

```text
C:/TSIS_Data/tests/institutional/README.md
```

Usar esta ruta para reglas TSIS globales: limites entre modulos, versionado,
Graphify, changelogs, contratos raiz y trazabilidad institucional.

3. Si la pregunta es de arquitectura CTO, ir a:

```text
C:/TSIS_Data/00_CTO/tests/README.md
```

Usar esta ruta para comprobar que los mapas CTO, documentos privados
promocionados, contratos publicos y referencias de arquitectura siguen
alineados.

4. Si la pregunta es del modulo SmallCaps, ir a:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/README.md
```

Usar esta ruta para tests ejecutables del modulo: Data Foundation, research,
eventos, estrategias, ejecucion y offline RL.

5. Si lo que quieres es iniciar los tests de las tablas de Data Foundation, ir
directamente a:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/README.md
```

Ese README define el estandar minimo para cada tabla: schema contract,
manifest/hash, source reconciliation, third-party evidence y
adversarial/mutation tests.

6. Si lo que quieres es entender el contrato de las tablas antes de testearlas,
leer:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
```

Ese contrato explica que tablas existen, para que sirven, de donde sale su
informacion y como deben ser consumidas.

7. Si lo que quieres es validar evidencia humana o auditoria visual, ir a:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/data_quality_report/
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/
```

Los tests ejecutables no sustituyen esta evidencia. Deben comprobar que existe,
que esta enlazada y que respeta el contrato de auditoria.

## Primer trabajo recomendado

La primera bateria ejecutable debe empezar por las dos primeras tablas ya
materializadas:

```text
instrument_master_v0_1
market_calendar_v0_1
expected_data_calendar_v0_1
corporate_actions_table_v0_1
dataset_certification_matrix_v0_1
master_daily_table_v0_1
master_intraday_bar_table_v0_1
microstructure_features_table_v0_1
halts_table_v0_1
event_windows_table_v0_1
outcomes_table_v0_1
fundamentals_asof_table_v0_1
news_context_table_v0_1
short_context_table_v0_1
regime_context_table_v0_1
```

Contract skeletons not materialized:

```text
market_state_table_v0_1
event_state_table_v0_1
```

These two state tables now also have deterministic fixture-only builders and
adversarial leakage tests. This is not an official materialization.

Ruta de tests:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/
```

Rutas de outputs:

```text
E:/TSIS/data/data_foundation_outputs/instrument_master/
E:/TSIS/data/data_foundation_outputs/market_calendar/
E:/TSIS/data/data_foundation_outputs/expected_data_calendar/
E:/TSIS/data/data_foundation_outputs/corporate_actions_table/
E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix/
E:/TSIS/data/data_foundation_outputs/master_daily_table/
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/
E:/TSIS/data/data_foundation_outputs/microstructure_features_table/
E:/TSIS/data/data_foundation_outputs/halts_table/
E:/TSIS/data/data_foundation_outputs/event_windows_table/
E:/TSIS/data/data_foundation_outputs/outcomes_table/
E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/
E:/TSIS/data/data_foundation_outputs/news_context_table/
E:/TSIS/data/data_foundation_outputs/short_context_table/
E:/TSIS/data/data_foundation_outputs/regime_context_table/
```

Future output roots reserved but not materialized:

```text
E:/TSIS/data/data_foundation_outputs/market_state_table/
E:/TSIS/data/data_foundation_outputs/event_state_table/
```

Evidencia reciente:

```text
C:/TSIS_Data/tests/test_runs/2026-06-23/data_foundation_outputs_seven_tables_v0_1_rerun/
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_microstructure_features_table_v0_1_rerun/
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_halts_table_v0_1/
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_event_windows_table_v0_1/
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_outcomes_table_v0_1/
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_fundamentals_asof_table_v0_1/
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_news_context_table_v0_1/
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_short_context_table_v0_1/
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_regime_context_table_v0_1/
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_market_state_table_contract_skeleton_v0_1/
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_event_state_table_contract_skeleton_v0_1/
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_market_event_state_fixture_loop_v0_1/
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_candidate_window_manifest_v0_1/
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_features_table_v0_1_default_guard/
```

Nota:

```text
data_foundation_outputs_microstructure_candidate_window_manifest_v0_1
```

valida solo el manifest candidato de ventanas para
`microstructure_features_table_v0_2_candidate` y un candidato pequeño de
features bajo `artifacts/`. No crea parquet oficial ni modifica
`E:/TSIS/data/data_foundation_outputs/microstructure_features_table/`.

Rutas de contratos relacionados:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/contract_registry/dataset_contracts/
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/dataset_registry/outputs/
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/data_consumption_policies/
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/validators/outputs/
```

Orden recomendado:

1. Mantener tests contractuales offline para las tablas CAPA 1 ya materializadas.
2. Ampliar tests contractuales cuando se materialice una tabla nueva.
3. Crear evidencia third-party cacheada para muestras deterministicas.
4. Crear tests opcionales con red solo bajo opt-in explicito.
5. Crear tests adversariales que demuestren que los validadores fallan cuando
   deben fallar.
6. Actualizar changelog y cola Graphify si cambia semantica operativa.

No empezar por tests de estrategias o RL hasta que las tablas base tengan gates
institucionales.

## Donde se guardan los outputs de tests

Los outputs de tests no deben guardarse en:

```text
E:/TSIS/data/data_foundation_outputs/
C:/TSIS_Data/data/
```

Esas rutas no son para resultados de ejecucion de tests.

La ruta canonica para resultados de tests del monorepo es:

```text
C:/TSIS_Data/tests/test_runs/
```

Cada ejecucion relevante debe crear una carpeta fechada con metadata:

```text
C:/TSIS_Data/tests/test_runs/YYYY-MM-DD/<run_id>/
  metadata.json
  summary.md
  pytest_output.txt
  junit.xml
  coverage.xml
  artifacts/
```

Regla:

- `metadata.json` debe indicar fecha, modulo, contrato validado, commit si
  existe, dataset version, paths de inputs, paths de outputs validados y persona
  o agente que ejecuto el test.
- `summary.md` debe explicar que se comprobo, que fallo y que queda pendiente.
- los artefactos grandes no deben duplicar raw data; deben ser muestras,
  reports, hashes, diffs, snapshots o evidencia minima reproducible.

## Donde se guardan fixtures y evidencia externa

Fixtures pequenas y deterministicas:

```text
C:/TSIS_Data/tests/fixtures/
```

Evidencia externa cacheada para evitar tests con internet por defecto:

```text
C:/TSIS_Data/tests/third_party_evidence/
```

Ejemplos:

- snapshot SEC EDGAR de una muestra deterministica;
- snapshot NYSE/Nasdaq de calendario;
- respuesta OpenFIGI cacheada;
- hash y timestamp de descarga;
- nota de fuente y licencia si aplica.

Los tests con red en vivo deben ser opt-in. Por defecto, los tests deben poder
ejecutarse offline contra evidencia cacheada.

## Principio de organizacion

TSIS debe tener dos niveles de tests:

- tests raiz del monorepo: reglas institucionales, limites entre modulos,
  versionado, trazabilidad, Graphify y coherencia de arquitectura global.
- tests locales de modulo: contratos ejecutables de la capa que produce,
  transforma o consume artefactos concretos.

Los tests raiz no deben validar el contenido granular de una tabla concreta.
Eso pertenece al modulo propietario de la tabla. Los tests raiz si deben
comprobar que cada modulo declara sus contratos, changelogs, manifests y rutas
de evidencia de forma compatible con el sistema TSIS.

## Subdirectorios

- `institutional/`: gates globales del monorepo.
- `test_runs/`: outputs fechados de ejecuciones de tests.
- `fixtures/`: fixtures pequenas, sinteticas o congeladas para tests.
- `third_party_evidence/`: snapshots externos cacheados para comprobaciones
  independientes.

## Relacion con otros arboles de tests

- `00_CTO/tests/`: tests de arquitectura, gobierno y consistencia CTO.
- `01_TSIS_DATA_FOUNDATION/tests/`: tests ejecutables del modulo SmallCaps.

Cuando se anada un nuevo modulo, debe crear su propio `tests/` local y este
directorio raiz solo debe validar que ese modulo cumple las reglas comunes.

## Regla contra trampas al solitario

Un test institucional no debe limitarse a confirmar que existe un fichero.
Debe validar al menos una propiedad semantica verificable:

- el documento correcto enlaza al contrato correcto;
- el manifest apunta al output correcto;
- el changelog describe el cambio semantico;
- la cola Graphify contiene la actualizacion pendiente cuando corresponde;
- una fuente externa o evidencia congelada permite reconstruir la afirmacion.

Si una prueba solo comprueba presencia superficial, debe considerarse incompleta.
