# Data Quality Harness Shutdown Handoff Note

Fecha: 2026-06-13

## 1. Proposito

Esta nota existe para que otro agente pueda continuar si la sesion se corta, se apaga el equipo o se pierde contexto conversacional.

No sustituye los contratos del proyecto. Es una nota operativa de continuidad para el tramo actual del Data Quality Harness.

Debe leerse antes de continuar cualquier trabajo sobre:

- `01_TSIS_backtest_SmallCaps/01_foundations`;
- auditoria de data Polygon;
- modernizacion de dossiers;
- commits/pushes relacionados con este tramo.

## 2. Donde esta esta nota

Ruta:

- `C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\10_DATA_QUALITY_HARNESS\runbooks\2026-06-13_shutdown_handoff_note.md`

Razones:

- pertenece al Data Quality Harness;
- es operativa, no privada;
- debe vivir junto a los runbooks que gobiernan agentes de auditoria de data;
- no debe mezclarse con `00_private`;
- y debe quedar versionada en GitHub.

## 3. Estado Git al crear esta nota

Repositorio:

- `C:\TSIS_Data`

Remoto:

- `origin = https://github.com/alexjust-data/TSIS.git`

Estado remoto confirmado antes de esta nota:

- `origin/main` quedo actualizado en GitHub con commit:
  - `2aeb747 docs: promote data quality harness dossiers`

Rama local activa tras resolver el problema:

- `integrate/main-data-quality-dossiers-20260613`

Esta rama local estaba alineada con:

- `origin/main`

Problematica Git encontrada:

1. El trabajo original se commiteo primero en:
   - `docs/update-00-cto-readme-20260611`
   - commit local: `de76ecd docs: promote data quality harness dossiers`

2. Intentar empujar esa rama fallo dos veces con:
   - `HTTP 500`
   - `send-pack: unexpected disconnect while reading sideband packet`
   - `fatal: the remote end hung up unexpectedly`
   - y el mensaje ambiguo `Everything up-to-date`

3. Esa rama no aparecio en remoto al verificar con `ls-remote`.

4. No era correcto hacer simplemente:
   - `git push origin main`

   porque el commit nuevo no estaba en la rama local `main`, sino en `docs/update-00-cto-readme-20260611`.

5. Ademas, la rama local `main` estaba divergida:
   - `ahead 1`
   - `behind 4`

6. La solucion segura fue:

```powershell
git -C "C:\TSIS_Data" fetch origin
git -C "C:\TSIS_Data" switch -c integrate/main-data-quality-dossiers-20260613 origin/main
git -C "C:\TSIS_Data" cherry-pick de76ecd
git -C "C:\TSIS_Data" push origin HEAD:main
```

Resultado:

- GitHub acepto el push:
  - `0162702..2aeb747 HEAD -> main`

Regla para el siguiente agente:

- No usar la rama local `main` para nuevos pushes hasta sanearla explicitamente.
- No hacer `git reset`, `checkout --`, `clean` ni revert sin instruccion explicita del usuario.
- Para continuar, partir de `origin/main` o de la rama local alineada `integrate/main-data-quality-dossiers-20260613`.
- Antes de cualquier push:
  - comprobar procesos Git vivos;
  - comprobar `status -sb`;
  - comprobar `branch -vv`;
  - comprobar `log --oneline --decorate -3`;
  - y empujar solo un HEAD que sea descendiente de `origin/main`.

Comandos de diagnostico recomendados:

```powershell
Get-Process git -ErrorAction SilentlyContinue
git -C "C:\TSIS_Data" fetch origin
git -C "C:\TSIS_Data" status -sb
git -C "C:\TSIS_Data" branch -vv
git -C "C:\TSIS_Data" log --oneline --decorate --graph --max-count=12 --all
git -C "C:\TSIS_Data" ls-remote --heads origin main
```

## 4. Problema de entorno

`C:\TSIS_Data` puede quedar fuera del workspace principal de Codex cuando la sesion arranca en `C:\Users\AlexJ`.

En sesiones sandboxed normales, lecturas simples contra `C:\TSIS_Data` llegaron a quedarse colgadas.

Regla:

- si la sesion arranca en `C:\TSIS_Data` en modo YOLO/autonomo, trabajar normal;
- si la sesion arranca fuera de `C:\TSIS_Data` o esta sandboxed, usar comandos con permisos escalados para `C:\TSIS_Data` y `E:\TSIS\data`;
- no insistir con lecturas sandboxed largas si un probe minimo se cuelga.

Comando de arranque recomendado por el usuario:

```powershell
powershell -ExecutionPolicy Bypass -File C:\TSIS_Data\START_CODEX_TSIS_AUTONOMOUS.ps1
```

## 5. Lectura obligatoria para retomar

Primero leer:

- `C:\TSIS_Data\START_HERE.md`
- `C:\TSIS_Data\PROJECT_RULES.md`
- `C:\TSIS_Data\AGENTS.md`
- `C:\TSIS_Data\ARCHITECTURE_OVERVIEW.md`
- `C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md`
- `C:\TSIS_Data\VERSIONING_STANDARDS.md`
- `C:\TSIS_Data\RESEARCH_PHILOSOPHY.md`
- `C:\TSIS_Data\README.md`
- `C:\TSIS_Data\CHANGELOG.md`

Modulo 01:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\README.md`
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\AGENTS.md`
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\LOCAL_RULES.md`
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\CHANGELOG.md`

CTO / Data Quality Harness:

- `C:\TSIS_Data\00_CTO\README.md`
- `C:\TSIS_Data\00_CTO\CHANGELOG.md`
- `C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\README.md`
- `C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\00_SHARED_HARNESS_KERNEL\agentic_harness_architecture_reference.md`
- `C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\00_SHARED_HARNESS_KERNEL\harness_toolchain_traceability_contract.md`
- `C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\00_SHARED_HARNESS_KERNEL\shared_run_manifest_contract.md`
- `C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\00_SHARED_HARNESS_KERNEL\shared_validation_principles.md`
- `C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\10_DATA_QUALITY_HARNESS\README.md`
- `C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\10_DATA_QUALITY_HARNESS\data_audit_completion_artifact_contract.md`
- `C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\10_DATA_QUALITY_HARNESS\historical_audit_preservation_and_promotion_contract.md`
- `C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\10_DATA_QUALITY_HARNESS\runbooks\2026-06-12_overnight_data_audit_completion_harness_runbook.md`
- esta nota.

Foundation model:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\inspection_dossier_model.md`
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\auditoria_and_certification_source_hierarchy.md`
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\data_storage_topology_and_target_state.md`
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\event_families_and_reference_inventory.md`

## 6. Estado de trabajo cerrado

### Reference

`reference` quedo modernizado y promovido como foundation/reference layer.

Estado correcto:

```text
reference = historical_deep_audit_closed + modern_dossier_complete_for_foundation_promotion
```

Archivos clave:

- `01_TSIS_backtest_SmallCaps/scripts/inspection/reference/build_reference_inspection_pack.py`
- `01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/reference/reference_inspection_readout_v0_2.md`
- `01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/reference/build_reference_inspection_pack.md`
- `01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/reference/reference_casepacks_traceability_audit_v0_1.md`
- `01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/reference/integration_notes.md`
- `01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/reference/evidence_assets/run_manifest.json`
- `01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/reference/reference_registry_entry.yaml`
- `01_TSIS_backtest_SmallCaps/01_foundations/validators/reference/reference_validators.md`
- `01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/reference_dataset_contract_v0_1.md`

Importante:

- no habilita alpha, live, RL, continuidad corporativa completa ni universe membership final;
- los artefactos nuevos son ligeros;
- no se copiaron parquets historicos pesados a `01_foundations`.

### Halts

`halts` quedo modernizado y promovido como event/reference layer.

Estado correcto:

```text
halts = historical_deep_audit_closed + modern_dossier_complete_for_foundation_promotion
```

Archivos clave:

- `01_TSIS_backtest_SmallCaps/scripts/inspection/halts/build_halts_inspection_pack.py`
- `01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/halts/halts_inspection_readout_v0_1.md`
- `01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/halts/build_halts_inspection_pack.md`
- `01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/halts/halts_casepacks_traceability_audit_v0_1.md`
- `01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/halts/integration_notes.md`
- `01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/halts/evidence_assets/run_manifest.json`
- `01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/halts_dataset_contract_v0_1.md`
- `01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/halts/halts_registry_entry.yaml`
- `01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/halts_consumption_policy.md`
- `01_TSIS_backtest_SmallCaps/01_foundations/validators/halts/halts_validators.md`

Importante:

- root canonico: `E:\TSIS\data\Halts`;
- root historico observado: `D:\Halts`;
- `halts` no es precio, tape, alpha ni execution truth;
- SEC/context/date-level no debe usarse como ventana intradia;
- ausencia de halt no prueba mercado limpio ni missing data;
- los artefactos nuevos son ligeros;
- no se copiaron parquets historicos pesados a `01_foundations`.

## 7. Validaciones ya ejecutadas

Se valido:

- YAML parseable para `reference_registry_entry.yaml`;
- YAML parseable para `halts_registry_entry.yaml`;
- `py_compile` de builders `reference` y `halts`;
- existencia y tamano no nulo de PNGs poblacionales;
- ausencia de `TODO`, `TBD`, `C:\Users` y `C:\tmp` en artefactos aceptados de `halts`;
- ausencia de parquets/comprimidos en `inspection_dossiers/halts`;
- `git diff --check` sin errores de whitespace, solo avisos CRLF;
- working tree limpio antes del commit/push principal;
- push final a `origin/main` aceptado.

## 8. Rutas protegidas

No modificar, mover, normalizar ni reorganizar:

- `E:\TSIS\data`
- `C:\TSIS_Data\data`
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\data`
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\run`
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs`
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA`

Estas rutas solo pueden leerse como evidencia/provenance.

Los nuevos artefactos aceptados deben vivir en:

- `01_TSIS_backtest_SmallCaps/01_foundations`
- `01_TSIS_backtest_SmallCaps/scripts/inspection/<dataset>`

## 9. Que falta por hacer

No continuar con un harness en bucle sobre todo sin revisar dataset por dataset.

El usuario pidio que, tras cada carpeta/dataset, se pare y se revise.

Orden operativo pendiente, salvo nueva instruccion:

1. `financial`
2. `regime_indicators`
3. integracion final

Fuera de alcance:

- `E:\TSIS\data\images_Flash_Research`

No inventariar, mover, OCRizar, validar ni institucionalizar `images_Flash_Research` dentro del cierre Polygon del Data Quality Harness.

Punto importante:

- antes de trabajar `financial`, verificar si su auditoria historica vive directamente bajo un bloque propio o dentro de `auditoria/additional`;
- no asumir por nombre de carpeta;
- leer primero `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/` y `certification/` relacionados.

## 10. Como debe continuar el siguiente agente

Flujo por dataset:

1. Confirmar Git limpio y rama correcta.
2. Leer esta nota y contratos obligatorios.
3. Inventariar `01_foundations` existente para el dataset.
4. Leer auditoria y certification historicas preservadas.
5. Inspeccionar root fisico en modo read-only.
6. No tocar datos raw.
7. Crear o actualizar script residente en `scripts/inspection/<dataset>`.
8. Generar solo artefactos ligeros bajo `01_foundations`.
9. Crear o actualizar:
   - schema si falta;
   - dataset contract;
   - registry entry;
   - consumption policy;
   - validators;
   - inspection dossier;
   - readout;
   - build guide;
   - integration notes;
   - indices compartidos;
   - changelog.
10. Validar:
    - YAML parsea;
    - builders compilan;
    - imagenes existen si se generan;
    - no hay outputs fuera del proyecto;
    - no hay `TODO/TBD` sin bloqueo formal;
    - no hay `C:\Users` ni `C:\tmp`;
    - no hay parquets pesados copiados a foundation salvo contrato explicito;
    - `git diff --check`;
    - `git status -sb`.
11. Parar y pedir revision humana antes del siguiente dataset.

## 11. Regla sobre notebooks e imagenes

No repetir el error de tratar notebooks como almacenes de codigo.

Regla:

- la logica pesada vive en scripts residentes;
- notebooks solo son inspectores, launchers, widgets o drilldown humano;
- cualquier conclusion estable debe promoverse a markdown/readout/manifest;
- imagenes no son decoracion;
- cada visual relevante debe declarar:
  - que muestra;
  - que responde;
  - que no responde;
  - consecuencia.

## 12. Criterio de cierre final de la auditoria

No declarar un dataset como cerrado solo porque exista un markdown.

El minimo moderno es:

- source/historical audit leida;
- root fisico auditado read-only;
- contrato;
- registry;
- policy;
- validators;
- dossier;
- evidence assets;
- readout;
- integration notes;
- changelog;
- validaciones reproducibles;
- estado de consumo honesto.

Estados permitidos siguen siendo conservadores:

- `not_started`
- `inventory_only`
- `foundation_minimal`
- `modernization_gap_documented`
- `modern_dossier_partial`
- `modern_dossier_complete`
- `blocked_needs_human_decision`
- `not_consumable_no_active_consumer`

No usar `done`, `clean`, `ok` o `closed` como estado final sin contrato, consumidor y evidencia.

## 13. Ultima regla

El siguiente agente no debe reempezar desde cero.

Debe asumir que `reference` y `halts` ya estan promovidos, leer sus readouts si necesita entender el patron, y continuar con el siguiente dataset pendiente aplicando la misma calidad, sin tocar data raw y parando al terminar cada bloque.
