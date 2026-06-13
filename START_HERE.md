# START_HERE - TSIS

Fecha de creacion: 2026-06-12

Este documento es la primera nota humana de arranque de TSIS.

No sustituye a `AGENTS.md`, `PROJECT_OPERATING_SYSTEM.md` ni a los contratos locales. Su funcion es que, al abrir el proyecto, el humano tenga claro:

- como arrancar Codex dentro de TSIS;
- como verificar que la sesion tiene permisos correctos;
- que prompt usar para ponerse al dia;
- que prompt usar si la sesion no es autonoma;
- como tratar Git sin repetir problemas de procesos colgados, pushes ambiguos o cambios destructivos.

## 1. Arranque correcto de Codex para TSIS

Abrir PowerShell o Windows Terminal y ejecutar:

```powershell
powershell -ExecutionPolicy Bypass -File C:\TSIS_Data\START_CODEX_TSIS_AUTONOMOUS.ps1
```

La pantalla de Codex debe mostrar algo equivalente a:

```text
directory:   C:\TSIS_Data
permissions: YOLO mode
```

Si no aparece `directory: C:\TSIS_Data`, la sesion no esta situada en el proyecto.

Si no aparece `YOLO mode`, la sesion puede volver a pedir permisos continuamente o quedarse bloqueada leyendo rutas de `C:\TSIS_Data`.

No empezar trabajos largos de Harness desde una sesion mal situada.

## 2. Que hace el lanzador

`C:\TSIS_Data\START_CODEX_TSIS_AUTONOMOUS.ps1` ejecuta:

```powershell
Set-Location -LiteralPath 'C:\TSIS_Data'

codex `
  -p tsis `
  -C 'C:\TSIS_Data' `
  --sandbox danger-full-access `
  --ask-for-approval never
```

Esto arranca Codex con:

- workspace en `C:\TSIS_Data`;
- perfil local `tsis`;
- acceso completo al filesystem local;
- aprobaciones desactivadas;
- capacidad de operar sin pedir permiso paso a paso.

Usar este modo solo para sesiones TSIS de confianza.

## 3. Prompt 1 - Puesta al dia normal en sesion autonoma

Usar este prompt cuando la pantalla de Codex muestre:

```text
directory:   C:\TSIS_Data
permissions: YOLO mode
```

Prompt:

```text
Te tienes que poner al dia con este proyecto.

Estas dentro de C:\TSIS_Data y la sesion esta en YOLO mode. No necesitas pedir permisos para leer archivos del proyecto.

Lee completos, antes de hacer cualquier otra cosa:

C:\TSIS_Data\PROJECT_RULES.md
C:\TSIS_Data\AGENTS.md
C:\TSIS_Data\ARCHITECTURE_OVERVIEW.md
C:\TSIS_Data\CHANGELOG.md
C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md
C:\TSIS_Data\VERSIONING_STANDARDS.md
C:\TSIS_Data\RESEARCH_PHILOSOPHY.md
C:\TSIS_Data\README.md

Despues lee completos estos contratos del modulo SmallCaps:

C:\TSIS_Data\01_TSIS_backtest_SmallCaps\README.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\AGENTS.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\CHANGELOG.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\LOCAL_RULES.md

No modifiques nada todavia.

Cuando hayas leido y entendido todo, responde solo:

ok
```

## 4. Prompt 2 - Puesta al dia desde sesion no autonoma o fuera del workspace

Usar este prompt solo si la sesion de Codex NO esta arrancada desde `C:\TSIS_Data` en `YOLO mode`, por ejemplo si aparece:

```text
directory: C:\Users\AlexJ
```

Prompt:

```text
Te tienes que poner al dia con este proyecto:

C:\TSIS_Data\PROJECT_RULES.md
C:\TSIS_Data\AGENTS.md
C:\TSIS_Data\ARCHITECTURE_OVERVIEW.md
C:\TSIS_Data\CHANGELOG.md
C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md
C:\TSIS_Data\VERSIONING_STANDARDS.md
C:\TSIS_Data\RESEARCH_PHILOSOPHY.md
C:\TSIS_Data\README.md

Dentro hemos ido trabajando en la auditoria de la data descargada desde Polygon:

C:\TSIS_Data\01_TSIS_backtest_SmallCaps\README.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\AGENTS.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\CHANGELOG.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\LOCAL_RULES.md

Lee todos esos archivos completos y ponte al dia antes de hacer cualquier otra cosa.
Cuando los hayas leido y entendido, responde solo:

ok

IMPORTANTE SOBRE EL ENTORNO:
Los archivos estan en C:\TSIS_Data, fuera del workspace principal C:\Users\AlexJ.
En sesiones anteriores, las lecturas normales dentro del sandbox se quedaron colgadas incluso con pruebas minimas como:

Test-Path -LiteralPath 'C:\TSIS_Data\PROJECT_RULES.md'

Esa misma prueba ejecutada con sandbox_permissions: "require_escalated" respondio en 0.3s con True.

Por tanto, no intentes leer esos archivos con comandos sandboxed normales porque puede parecer que estas leyendo durante muchos minutos, pero en realidad el wrapper se queda bloqueado.

Usa directamente comandos con sandbox_permissions: "require_escalated" para las lecturas de C:\TSIS_Data.
Hazlo de forma eficiente, archivo por archivo o en bloques razonables, pero lee el contenido completo.
```

## 5. Prompt 3 - Git seguro, recuperacion de push o publicacion

Usar este prompt cuando haya dudas sobre Git, commits creados, pushes que hicieron timeout, upstream ambiguo o procesos Git que pudieron quedar vivos.

Antes de usarlo, sustituir:

- `<RAMA>` por la rama real;
- `<COMMIT>` por el commit esperado, si existe;
- `<OBJETIVO_GIT>` por lo que se quiere conseguir.

Prompt:

```text
Tienes que continuar una tarea Git en C:\TSIS_Data.

Objetivo Git:
<OBJETIVO_GIT>

Rama esperada:
<RAMA>

Commit esperado, si aplica:
<COMMIT>

IMPORTANTE:
- No hagas reset.
- No hagas checkout destructivo.
- No hagas revert salvo que el humano lo pida explicitamente.
- No descartes cambios locales.
- No hagas push hasta verificar procesos, estado local, rama, upstream y remoto.
- Si la sesion esta en C:\TSIS_Data con YOLO mode, ejecuta comandos Git normales.
- Si la sesion esta fuera de C:\TSIS_Data o tiene sandbox, usa sandbox_permissions: "require_escalated" para comandos sobre C:\TSIS_Data.

Lo primero que debes hacer:

1. Comprobar si hay procesos Git activos:

   Get-Process git -ErrorAction SilentlyContinue

2. Si hay procesos Git activos, inspeccionarlos y esperar o verificar antes de lanzar otro push.

3. Verificar estado local:

   git -C C:\TSIS_Data status -sb
   git -C C:\TSIS_Data branch -vv
   git -C C:\TSIS_Data log --oneline --decorate -1

4. Verificar remoto:

   git -C C:\TSIS_Data remote -v
   git -C C:\TSIS_Data ls-remote --heads origin <RAMA>

5. Si el objetivo es publicar y la rama no esta en remoto, ejecutar:

   git -C C:\TSIS_Data push -u origin HEAD

6. Confirmar al final:

   - working tree limpio o explicar exactamente que queda pendiente;
   - rama actual;
   - upstream configurado o no;
   - commit local HEAD;
   - si <COMMIT> esta o no en origin;
   - cualquier proceso Git vivo restante.
```

## 6. Prompt 4 - Puesta al dia CTO completa

Usar este prompt cuando el trabajo toque cualquiera de estas areas:

- vision arquitectonica de TSIS;
- `00_CTO`;
- Harness agentic;
- SersanSistemas;
- AlphaEvolve;
- automatizacion;
- Data Quality Harness;
- arquitectura de backtest;
- decisiones de sistema.

Este prompt no sustituye al Prompt 1. Primero debe ejecutarse la puesta al dia general y despues esta puesta al dia CTO completa.

Prompt:

```text
Te tienes que poner al dia con la capa CTO completa de TSIS antes de proponer cambios.

Contexto:
La capa CTO vive en:

C:\TSIS_Data\00_CTO

Esta capa contiene pensamiento arquitectonico, contratos Harness, protocolos de automatizacion, SersanSistemas, Data Quality Harness, AlphaEvolve y referencias que pueden estar en distintos niveles de madurez.

Objetivo:
No quiero que leas solo una lista fija de archivos. Quiero que inventories, leas y clasifiques todo lo relevante dentro de C:\TSIS_Data\00_CTO para entender la verdad actual del sistema.

Reglas obligatorias:

1. Inventaria la estructura real de C:\TSIS_Data\00_CTO antes de asumir nada.

2. Lee completos todos los README.md, CHANGELOG.md, AGENTS.md y LOCAL_RULES.md que existan dentro de C:\TSIS_Data\00_CTO.

3. Lee completos todos los documentos contractuales y operativos bajo:

   C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE

   Incluyendo, como minimo, si existen:

   - 00_SHARED_HARNESS_KERNEL
   - 10_DATA_QUALITY_HARNESS
   - 20_SERSAN_DISTILLATION_HARNESS

4. No asumas que los README estan actualizados. Verifica cada README contra la estructura real de carpetas y archivos.

5. Si encuentras documentos en:

   C:\TSIS_Data\00_CTO\00_private

   tratalos como pensamiento exploratorio o fuente de ideas, no como contrato operativo, salvo que otro documento canonico los haya promovido explicitamente.

6. Si el trabajo toca SersanSistemas, lee tambien:

   C:\TSIS_Data\00_CTO\99_REFERENCE_LIBRARY\SersanSistemas

   y los contratos/artifacts existentes bajo:

   C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\20_SERSAN_DISTILLATION_HARNESS

7. Si el trabajo toca auditoria de datos o Data Quality Harness, lee tambien:

   C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\10_DATA_QUALITY_HARNESS
   C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations

   No te fies solo de documentos resumen. Verifica contra la auditoria real.

8. Antes de escribir nada, responde con un mapa breve pero claro:

   - que carpetas existen bajo 00_CTO;
   - que documentos parecen contractuales;
   - que documentos parecen exploratorios;
   - que partes estan formalizadas;
   - que partes parecen obsoletas, incompletas o pendientes;
   - que documentos deberian mandar para la tarea concreta.

9. No modifiques nada hasta que ese mapa este hecho y el humano confirme el siguiente paso.
```
## 7. Regla operativa

No usar `/review` al arrancar salvo que el objetivo sea revisar cambios Git.

Para continuar un Harness, no basta con la puesta al dia minima. Primero ejecutar el Prompt 1 y despues el Prompt 4 de puesta al dia CTO completa.

Despues usar el runbook o contrato del Harness correspondiente:

- Data Quality Harness:
  `C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\10_DATA_QUALITY_HARNESS`
- Sersan Distillation Harness:
  `C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\20_SERSAN_DISTILLATION_HARNESS`

Nada importante debe quedar solo en conversaciones. Si una regla, decision, protocolo, resultado o excepcion va a ser reutilizada, debe vivir en un documento, contrato, manifest, changelog o artefacto trazable dentro del proyecto.


# Sersan Distillation Harness

Cuando termine de ponerse al día, haga primero un readiness gate y después ejecute el Harness solo si el contrato está suficientemente
cerrado.

Prompt recomendado:

Cuando termines la puesta al día general y la puesta al día CTO completa, no preguntes por el siguiente paso salvo que encuentres un bloqueo real.

Objetivo:

Ejecutar el Sersan Distillation Harness de forma autónoma sobre el corpus completo, siguiendo los contratos ya existentes.

Antes de ejecutar:
1. Confirma qué Harness vas a ejecutar.
2. Confirma qué contratos mandan.
3. Confirma qué corpus entra en scope.
4. Confirma qué artefactos deben generarse.
5. Confirma qué validaciones deben pasar.
6. Confirma dónde se escribirán outputs, manifests, reports y changelog.

Si todo está claro, ejecuta.

Si falta una pieza contractual crítica, no improvises. Detente y entrega:
- readiness_report.md;
- blockers;
- propuesta concreta de contrato faltante.

Durante la ejecución:
- no trabajes desde C:\Users ni C:\tmp;
- todo script/generador debe vivir dentro del proyecto;
- todo output debe tener run_manifest;
- todo resultado debe tener quality_report;
- no sobrescribas artefactos institucionales sin versión o justificación;
- actualiza changelog si hay cambio semántico;
- valida rutas, hashes, manifiestos y ausencia de fugas fuera del proyecto.

Al terminar:
- resume corpus procesado;
- lecciones procesadas;
- artefactos creados;
- warnings;
- blockers;
- estado final: pass, pass_with_warnings o fail;
- siguiente acción recomendada.


## prompt 

Confirmado. Ejecuta el Sersan Distillation Harness completo.
```
Objetivo:
Destilar todo el corpus SersanSistemas de principio a fin siguiendo los contratos existentes, sin inventar formatos propios.

Scope:
- Fuente bruta:
   C:\TSIS_Data\00_CTO\99_REFERENCE_LIBRARY\SersanSistemas
- Harness:
   C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\20_SERSAN_DISTILLATION_HARNESS
- Kernel compartido:
   C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\00_SHARED_HARNESS_KERNEL

Contratos que mandan:
- sersan_distillation_protocol.md
- sersan_lesson_pack_contract.md
- sersan_pilot_harness_runbook.md
- harness_toolchain_traceability_contract.md
- shared_run_manifest_contract.md
- shared_validation_principles.md

Instrucciones:
1. Ejecuta un readiness gate final.
2. Si el readiness gate pasa, no preguntes más y continúa.
3. Usa el inventario de corpus existente.
4. Procesa todos los lesson packs pendientes.
5. No rehagas pilotos ya completados salvo que sea necesario para normalizar schema o validar compatibilidad.
6. Todo generador, validador, config o script debe vivir dentro del proyecto, no en C:\Users ni C:\tmp.
7. Todo output debe ir bajo:
   C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\20_SERSAN_DISTILLATION_HARNESS\sersan_distillation_artifacts
8. Cada lesson pack debe producir, como mínimo:
   - lesson_pack_manifest.json
   - lesson_sections.jsonl
   - image_evidence_index.csv
   - mechanical_rules.yaml
   - tsis_translation_map.csv
   - quality_report.md
   - run_manifest.json
9. Lee las imágenes referenciadas cuando sean relevantes para entender reglas mecánicas, gráficos, setups, mapas, optimización o evidencia visual.
10. Si un lesson pack tiene bloqueo crítico, márcalo como blocked con explicación y continúa con el siguiente. No detengas todo el corpus por un bloqueo
local salvo que afecte al contrato global.
11. Valida rutas, hashes, schemas, manifests y ausencia de fugas fuera del proyecto.
12. Al final crea un corpus-level report con:
   - lesson packs procesados;
   - lesson packs pass;
   - pass_with_warnings;
   - blocked;
   - fail;
   - reglas mecánicas extraídas;
   - mapas TSIS creados;
   - warnings repetidos;
   - deuda contractual;
   - recomendación de promoción o siguiente fase.
13. Actualiza 00_CTO/CHANGELOG.md si hay cambio institucional.

Modo de trabajo:
Actúa en fases internas:
- Supervisor: planifica lotes y readiness gate.
- Worker: procesa lesson packs.
- Validator: valida contrato y artefactos.
- Auditor: resume desviaciones, warnings y estado final.
```

La arquitectura ideal es:

Humano
   -> Supervisor
      -> Agente A
      -> Agente B
      -> Agente C
      -> Validador
      -> Auditor

Pero lo que tenemos hoy es esto:

Humano
   -> 1 agente Codex
      -> fase Supervisor
      -> fase Worker
      -> fase Validator
      -> fase Auditor

Es decir: hemos construido los contratos, carpetas, artefactos y reglas del Harness, pero todavía no hemos implementado un orquestador real que lance
varios agentes independientes en paralelo.

Para esta fase Sersan, eso está bien. Primero necesitamos demostrar que el ciclo completo funciona de forma secuencial y trazable. Después, si escala
mal o tarda demasiado, el siguiente paso sería construir el orquestador multi-agente real.