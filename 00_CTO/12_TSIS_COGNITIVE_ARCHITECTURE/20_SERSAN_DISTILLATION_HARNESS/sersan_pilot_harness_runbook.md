# Sersan Pilot Harness Runbook

Fecha: 2026-06-11
Estado: runbook v0.1
Ambito: piloto Sersan Distillation Harness
Depende de:

- `00_SHARED_HARNESS_KERNEL/agentic_harness_architecture_reference.md`
- `20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_protocol.md`
- `20_SERSAN_DISTILLATION_HARNESS/sersan_lesson_pack_contract.md`
- `00_SHARED_HARNESS_KERNEL/harness_toolchain_traceability_contract.md`
- `sersan_distillation_artifacts/_corpus_inventory/sersan_corpus_manifest.csv`

## 0. Proposito

Este runbook define como debe ejecutarse el primer piloto de Sersan Distillation
Harness.

El objetivo del piloto no es destilar todo el curso.
El objetivo es demostrar que el metodo funciona:

```text
lesson pack
-> secciones
-> evidencia visual
-> reglas mecanicas
-> traduccion TSIS
-> quality report
-> revision humana
```

Este documento responde:

- como trabajan los agentes;
- si deben iterar en bucle;
- cuando paran;
- como sabemos que lo hicieron bien;
- que imagenes se incrustan;
- que debe revisar el humano;
- que outputs deben existir para aceptar el piloto.

## 1. Principio operativo

Un Harness no es un agente libre.

Un Harness es un sistema de ejecucion con:

- objetivo definido;
- contrato de artefactos;
- fases;
- validadores;
- trazas;
- criterios de parada;
- revision humana.

Regla:

```text
el agente no termina porque "cree" que termino;
termina cuando sus artefactos pasan contrato o quedan bloqueados con evidencia.
```

## 2. Lesson packs piloto

El piloto se ejecuta sobre tres lesson packs:

| Orden | lesson_id | Fuente | Imagenes | Razon |
|---:|---|---|---:|---|
| 1 | `sersan_practice_02_donchain` | `practica_02_donchain.md` | 60 | Base, Donchian, BRaC, robustez inicial |
| 2 | `sersan_practice_09_revision_apolo` | `practica_09_revision_apolo.md` | 171 | Revision real, optimizacion, zonas robustas, OOS, execution realism |
| 3 | `sersan_practice_15_revised` | `practica_15_revised.md` | 206 | Money management, position sizing, portfolio |

Los tres estan actualmente en estado `assets_resolved`.

## 3. Output esperado por lesson pack

Cada piloto debe producir:

```text
sersan_distillation_artifacts/<lesson_id>/
  lesson_pack_manifest.json
  lesson_sections.jsonl
  image_evidence_index.csv
  image_evidence_notes/
    <image_id>.md
  mechanical_rules.yaml
  lesson_distillation.md
  tsis_translation_map.csv
  open_questions.md
  quality_report.md
  run_manifest.json
```

El manifest ya existe por inventario. El piloto debe completar el resto.

## 4. Fases del run



### 4.0 Toolchain preflight

Antes de ejecutar cualquier generador, el Harness debe confirmar:

```text
[ ] generator/prompt/validator lives under project path
[ ] no accepted generator path is C:\Users, C:\tmp or Downloads
[ ] run_manifest.json will record command and toolchain hashes
[ ] temporary exploratory scripts are not final source of truth
```

Si el agente necesita crear una herramienta nueva, debe crearla bajo:

```text
00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/harness_toolchain/sersan_distillation/
```

Un run producido desde una ruta temporal solo puede considerarse borrador. Para
aceptarlo hay que promover la toolchain al proyecto y re-ejecutar desde esa
ruta.
### 4.1 Phase 0: Preflight

Objetivo:

- confirmar que existe `lesson_pack_manifest.json`;
- confirmar que el status es `assets_resolved`;
- leer contrato;
- leer MD fuente;
- preparar run id.

Checks:

```text
[ ] lesson_pack_manifest.json exists
[ ] source_md exists
[ ] image_dir exists
[ ] missing image refs = 0
[ ] contract_version = sersan_lesson_pack_contract_v0_1
```

Si falla:

```text
stop -> quality_report = fail
```

### 4.2 Phase 1: Sectionization

Objetivo:

- dividir el MD en secciones semanticas;
- asignar `section_id`;
- preservar rangos de linea;
- asociar imagenes cercanas.

Output:

```text
lesson_sections.jsonl
```

Reglas:

- no resumir el MD completo como una sola seccion;
- no crear secciones sin `line_start` y `line_end`;
- si una imagen sostiene una lectura, `requires_image_reading=true`;
- preguntas y respuestas deben marcarse como `qa`;
- bloques de optimizacion deben marcarse como `optimization`;
- money management debe marcarse como `money_management`;
- ejecucion, halts y fills irreales deben marcarse como `execution_realism`.

### 4.3 Phase 2: Image evidence reading

Objetivo:

- leer imagenes relevantes;
- clasificarlas;
- extraer valores si contienen numeros;
- decidir si sostienen una regla.

Output:

```text
image_evidence_index.csv
image_evidence_notes/<image_id>.md
```

Regla importante:

```text
no se incrustan todas las imagenes; se incrustan solo las doctrinalmente relevantes.
```

### 4.4 Phase 3: Mechanical rule extraction

Objetivo:

- extraer reglas mecanicas candidatas;
- separar regla dura, warning, heuristica y pregunta abierta;
- anclar cada regla a texto e imagen.

Output:

```text
mechanical_rules.yaml
```

Regla:

```text
una regla sin source_anchor es invalida.
```

### 4.5 Phase 4: TSIS translation

Objetivo:

- mapear reglas a artefactos TSIS candidatos.

Output:

```text
tsis_translation_map.csv
```

Targets validos:

- `strategy_evaluator`
- `backtest_checklist`
- `execution_realism_check`
- `money_management_policy`
- `portfolio_evaluator`
- `AlphaEvolve_constraint`
- `human_review_checklist`
- `research_protocol`
- `documentation_only`

### 4.6 Phase 5: Human-readable distillation

Objetivo:

- crear un documento legible por humano;
- incrustar imagenes clave;
- resumir reglas y dudas.

Output:

```text
lesson_distillation.md
open_questions.md
```

### 4.7 Phase 6: Quality report

Objetivo:

- declarar si el lesson pack pasa contrato;
- listar warnings;
- listar bloqueos;
- marcar puntos de revision humana.

Output:

```text
quality_report.md
```

Valores permitidos:

- `pass`
- `pass_with_warnings`
- `needs_human_review`
- `fail`

## 5. Politica de bucle

Los agentes pueden iterar, pero no indefinidamente.

Bucle permitido:

```text
generar artefacto
-> validar contrato
-> detectar fallos
-> corregir fallos concretos
-> validar otra vez
```

Limites:

- maximo 3 iteraciones por fase;
- si el mismo error aparece 3 veces, parar y marcar `needs_human_review` o `fail`;
- no reescribir fases anteriores si no hay fallo concreto;
- no ampliar alcance a otras practicas durante el piloto;
- no promocionar doctrina.

## 6. Politica de imagenes incrustadas

### 6.1 Principio

Las imagenes son evidencia.

Pero incrustar todo destruye legibilidad.

Por tanto:

```text
image_evidence_index.csv registra todas las imagenes;
lesson_distillation.md incrusta solo imagenes relevantes.
```

### 6.2 Reglas de incrustacion

| doctrine_relevance | Accion en `lesson_distillation.md` |
|---|---|
| `critical` | incrustar obligatoriamente |
| `high` | incrustar obligatoriamente |
| `medium` | incrustar si sostiene una regla; si no, enlazar |
| `low` | solo registrar en CSV |
| `none` | solo registrar en CSV si fue referenciada |

### 6.3 Imagenes que deben considerarse high/critical

Marcar como `high` o `critical` si la imagen contiene:

- mapa de optimizacion usado para zona robusta;
- comparativa IS/OOS/AllData;
- robustness, TSI, ES, PPC o fitness;
- tabla de parametros/rangos/incrementos;
- equity curve usada como evidencia;
- drawdown usado como advertencia;
- performance report con metricas;
- ejemplo de halt o fill irreal;
- money management que cambia lectura de riesgo;
- portfolio report usado para regla de cartera;
- codigo que implementa una penalizacion o constraint.

### 6.4 Formato de incrustacion

Usar Markdown con ruta relativa desde `lesson_distillation.md` al asset original
o al asset copiado si se decide copiar.

Formato recomendado:

```md
### Evidencia visual: zona robusta

Fuente:

- section_id: `...`
- image_id: `...`
- original: `...`

![Zona robusta - mapa de optimizacion](../../../../99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/19-practice-09/img/126.png)

Lectura:

...
```

### 6.5 No hacer

No hacer:

- incrustar 100 imagenes sin lectura;
- incrustar imagenes sin `image_id`;
- usar imagenes sin source anchor;
- copiar imagenes sin registrar origen;
- declarar regla desde imagen no leida.

## 7. Como sabemos que trabaja bien

Un lesson pack trabaja bien si:

- todos los artefactos obligatorios existen;
- `run_manifest.json` declara toolchain residente en proyecto y hashes;
- todos los artefactos parsean;
- los conteos cuadran;
- toda regla tiene source anchor;
- toda imagen high/critical fue leida e incrustada;
- toda imagen medium fue leida y enlazada/incrustada segun necesidad;
- cada translation referencia una regla existente;
- `quality_report.md` declara decision;
- las dudas quedan en `open_questions.md`;
- ninguna regla queda como `promoted`.

## 8. Que debe revisar el humano

El humano no debe releer todo el MD.

Debe revisar:

1. `quality_report.md`
2. `mechanical_rules.yaml`
3. `tsis_translation_map.csv`
4. imagenes con:
   - `doctrine_relevance=high`;
   - `doctrine_relevance=critical`;
   - `requires_human_review=true`.
5. `open_questions.md`

Revision humana minima:

```text
aprobar si las reglas tienen sentido;
rechazar si el agente sobredeclara;
pedir ajuste si falta evidencia visual;
marcar reglas candidatas para doctrina posterior.
```

## 9. Señales de mala ejecucion

Mala señal si el agente:

- resume sin anclas;
- ignora imagenes;
- no distingue hard rule de heuristica;
- llama doctrina a lo que es opinion;
- no deja dudas abiertas;
- no marca human review;
- no genera `quality_report.md`;
- no puede explicar por que incrusto una imagen;
- no puede reconstruir fuente de una regla;
- genera outputs finales desde `C:\Users`, `C:\tmp` o una ruta no trazada;
- mezcla practica 02, 09 y 15 en un solo output.

## 10. Criterios de aceptacion del piloto completo

El piloto completo puede considerarse aceptado si:

- las tres practicas producen todos los artefactos;
- al menos dos practicas reciben `pass_with_warnings` o mejor;
- ninguna practica recibe `fail` por schema;
- las imagenes high/critical estan incrustadas;
- se identifican reglas reutilizables;
- se documentan ajustes necesarios al contrato;
- el humano puede revisar sin volver al corpus completo.

No se exige `pass` perfecto en v0.1.

El objetivo es validar el metodo y ajustar el contrato.

## 11. Orden de ejecucion recomendado

### 11.1 Primero: practica 02

Razon:

- contiene base conceptual;
- menor cantidad de imagenes;
- introduce BRaC y robustez inicial;
- buen test de sectionization.

### 11.2 Segundo: practica 09

Razon:

- caso real y complejo;
- Apolo exige leer mapas, parametros, robustness, OOS y ejecucion;
- prueba fuerte para imagenes high/critical.

### 11.3 Tercero: practica 15

Razon:

- money management y portfolio pueden enganar visualmente;
- fuerza al Harness a separar curva bonita de riesgo real;
- conecta con futuros evaluadores y AlphaEvolve constraints.

## 12. Run naming

Formato recomendado:

```text
sersan_pilot_<lesson_id>_<YYYYMMDD>_v01
```

Ejemplo:

```text
sersan_pilot_sersan_practice_02_donchain_20260611_v01
```

Cada run debe registrarse en:

```text
sersan_distillation_artifacts/<lesson_id>/run_manifest.json
```

Minimo:

```json
{
  "run_id": "sersan_pilot_sersan_practice_02_donchain_20260611_v01",
  "lesson_id": "sersan_practice_02_donchain",
  "contract_version": "sersan_lesson_pack_contract_v0_1",
  "toolchain_traceability_contract": "00_SHARED_HARNESS_KERNEL/harness_toolchain_traceability_contract.md",
  "mode": "pilot",
  "status": "running",
  "started_at_utc": "...",
  "completed_at_utc": null,
  "toolchain_artifacts": []
}
```

## 13. Decision v0.1

Empezar el piloto por:

```text
sersan_practice_02_donchain
```

No pasar a `practica_09` hasta que `practica_02` haya producido:

- `lesson_sections.jsonl`;
- `image_evidence_index.csv`;
- `mechanical_rules.yaml`;
- `tsis_translation_map.csv`;
- `lesson_distillation.md`;
- `quality_report.md`.

La primera practica validara si el contrato esta suficientemente claro para
seguir.
