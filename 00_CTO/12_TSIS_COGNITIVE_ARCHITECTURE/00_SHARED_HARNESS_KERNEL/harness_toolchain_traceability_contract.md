# Harness Toolchain Traceability Contract

Fecha: 2026-06-11
Estado: contract v0.1
Ambito: todos los Harness TSIS en fase CTO, piloto u operacion

## 0. Proposito

Este contrato existe para impedir que un output Harness dependa de codigo,
prompts, validadores o scripts invisibles fuera del proyecto.

Regla base:

```text
ningun artefacto Harness puede aceptarse si no puede reconstruirse desde
toolchain residente en el proyecto + hashes + run_manifest + inputs declarados.
```

Esto aplica a:

- generadores de artefactos;
- validadores;
- scripts de inventario;
- prompts operativos;
- templates;
- configs;
- notebooks si producen outputs;
- wrappers de OCR/vision;
- pipelines que transformen corpus, data audit o research outputs.

## 1. Diferencia entre runtime y toolchain

Runtime externo permitido:

- `python`;
- PowerShell;
- librerias instaladas;
- sistema operativo;
- APIs o modelos usados como motor.

Toolchain que debe vivir en el proyecto:

- codigo propio que genera artefactos;
- codigo propio que valida artefactos;
- prompts o instrucciones que gobiernan un agente;
- configuraciones de ejecucion;
- schemas;
- templates;
- listas de inputs;
- reglas de seleccion.

El runtime puede estar fuera del proyecto. La toolchain TSIS no.

## 2. Rutas permitidas

La arquitectura de carpetas de Harness queda fijada asi:

```text
00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/
  00_SHARED_HARNESS_KERNEL/
  10_DATA_QUALITY_HARNESS/
  20_SERSAN_DISTILLATION_HARNESS/
```

Reglas:

- contratos, principios y schemas compartidos viven en `00_SHARED_HARNESS_KERNEL/`;
- cada Harness operativo vive en su propia carpeta numerada;
- cada Harness debe contener su propia `harness_toolchain/` si tiene generadores, validadores, prompts o configs propios;
- cada Harness debe contener sus propios `artifacts/` o artifact roots;
- ningun Harness debe escribir outputs finales en la raiz de `12_TSIS_COGNITIVE_ARCHITECTURE/`;
- ningun Harness debe depender de toolchain de otro Harness sin declararlo en `run_manifest.json`.

Rutas canonicas actuales:

```text
00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/
00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/
00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/
00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/harness_toolchain/
00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/
```

Rutas no aceptables como fuente final de un run:

```text
C:\Users\<user>\...
C:\tmp\...
%TEMP%\...
Downloads\...
scripts pegados solo en una conversacion
```

Estas rutas pueden usarse durante exploracion local, pero el output queda
`experimental_unaccepted` hasta que la toolchain se promueva al proyecto y se
re-ejecute o se justifique formalmente.

## 3. Run manifest obligatorio

Todo run Harness aceptable debe dejar:

```text
<artifact_root>/<run_or_lesson_id>/run_manifest.json
```

Campos minimos:

```json
{
  "run_id": "...",
  "lesson_id_or_scope": "...",
  "contract_version": "...",
  "toolchain_traceability_contract": "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/harness_toolchain_traceability_contract.md",
  "mode": "pilot|replay|shadow_live|live|manual_repair",
  "status": "running|pass|pass_with_warnings|needs_human_review|fail|blocked",
  "started_at_utc": "...",
  "completed_at_utc": "...",
  "execution_command": "...",
  "toolchain_artifacts": [
    {
      "tool_id": "...",
      "role": "generator|validator|prompt|template|config|schema",
      "project_relative_path": "...",
      "sha256": "sha256:...",
      "runtime": "python|powershell|llm|manual",
      "project_resident": true
    }
  ],
  "input_artifacts": [
    {
      "path": "...",
      "sha256": "sha256:..."
    }
  ],
  "output_artifacts": [
    {
      "path": "...",
      "sha256": "sha256:..."
    }
  ],
  "non_project_artifacts_used": [],
  "known_limitations": []
}
```

### 3.1 Self-hash policy

`run_manifest.json` is self-referential. Therefore it must not be required to
include its own SHA256 inside `output_artifacts`, because writing that hash would
change the file again.

Accepted policy:

```text
run_manifest.json is declared by existence and parser validation;
all other produced artifacts must carry hashes;
if a self-hash is required later, write it to an external sidecar file.
```

## 4. Hash policy

Cada toolchain artifact propio debe registrarse con SHA256.

Si el artefacto cambia:

- el hash cambia;
- el run anterior no se reinterpreta retroactivamente;
- el siguiente run debe declarar el nuevo hash.

## 5. Prompts operativos

Si un Harness usa prompts estables para agentes, esos prompts son toolchain.

No pueden vivir solo en una conversacion.

Deben guardarse como:

```text
harness_toolchain/<harness_name>/prompts/<prompt_id>.md
```

El prompt debe tener:

- objetivo;
- inputs permitidos;
- outputs esperados;
- criterios de parada;
- prohibiciones;
- contrato que debe leer;
- version.

## 6. Validadores

Un output no debe aceptarse solo porque el generador lo escribio.

Debe existir una validacion:

- automatica si hay schema;
- manual estructurada si aun no hay validador;
- registrada en `quality_report.md` o `run_manifest.json`.

El validador propio tambien es toolchain y debe estar hasheado.

## 7. Regla de re-ejecucion

Si un artefacto fue creado inicialmente con un script temporal fuera del
proyecto, hay dos opciones:

1. mover la toolchain al proyecto, registrar hash y re-ejecutar desde la ruta
   del proyecto;
2. marcar el output como `experimental_unaccepted` hasta que se haga lo
   anterior.

Para outputs que alimenten doctrina, evaluadores, AlphaEvolve o Data Quality
Harness, la opcion 1 es obligatoria.

## 8. Checklist de aceptacion

Antes de aceptar un run Harness:

```text
[ ] run_manifest.json exists.
[ ] Every project tool is under a project path.
[ ] No generator path points to C:\Users, C:\tmp or Downloads.
[ ] Every toolchain artifact has SHA256.
[ ] Every input artifact is declared.
[ ] Every output artifact is declared or covered by artifact contract.
[ ] Validator or quality report exists.
[ ] Human-review gates are explicit.
[ ] The run can be reconstructed without reading chat history.
```

## 9. Aplicacion a Sersan Distillation Harness

Sersan lesson packs must comply with this contract in addition to the Sersan
lesson-pack artifact contract.

The lesson-pack schema defines what is produced.

This contract defines how the producing toolchain is made traceable.

## 10. Aplicacion a Data Quality Harness

Data Quality Harness must apply the same policy before replay offline, shadow
live or live gating.

Checks, validators and report generators must live under project toolchain
paths and be declared by `run_manifest.json`.

## 11. Decision v0.1

From 2026-06-11 onward, no TSIS Harness output should be considered accepted if
its producing toolchain only exists in an agent conversation, `C:\Users`,
`C:\tmp` or another non-project temporary path.

