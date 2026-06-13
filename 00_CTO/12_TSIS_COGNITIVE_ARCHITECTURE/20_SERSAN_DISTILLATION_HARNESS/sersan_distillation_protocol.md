# Sersan Distillation Protocol

Fecha: 2026-06-11
Estado: protocol v0.1
Ambito: `C:\TSIS_Data\00_CTO\99_REFERENCE_LIBRARY\SersanSistemas`
Destino: preparar Harness agentic para destilar el curso Sersan de principio a fin.

## 0. Proposito

Este protocolo define como TSIS debe destilar el corpus SersanSistemas sin
convertirlo en resumen superficial ni en doctrina automatica.

El objetivo no es "resumir el curso". El objetivo es transformar un curso
experto de trading algoritmico en artefactos operativos TSIS:

- doctrina mecanica;
- reglas de backtest;
- criterios de robustez;
- anti-patrones;
- checklists;
- candidatos a evaluadores;
- restricciones para AlphaEvolve;
- memoria trazable para Harness.

Regla base:

```text
SersanSistemas es fuente experta.
No gobierna TSIS directamente.
Primero se destila, se traza, se revisa y solo despues se promociona.
```

## 1. Alcance v0.1

### 1.1 Incluido

Se incluyen como fuentes primarias:

- MD revisados bajo `03_only_md_revised`;
- imagenes asociadas a cada practica bajo `02_workshops/<lesson>/img`;
- codigo y artefactos de practica cuando existan (`.ELD`, `.tsw`, `.wsp`,
  `.xlsx`, `.txt`, `.html`, etc.);
- resumentes o indices markdown existentes;
- PDFs solo como respaldo de layout cuando haga falta.

### 1.2 Excluido

Queda fuera de alcance v0.1:

- video;
- subtitulos;
- transcripciones no necesarias si el MD revisado ya es la fuente consolidada;
- PDFs como fuente independiente, porque en este corpus los PDFs asociados son
  conversiones de los MD;
- promocion automatica a reglas canonicas de proyecto;
- implementacion de agentes productivos.

## 2. Observaciones reales del corpus

Antes de escribir este protocolo se inspecciono la estructura real del corpus.

### 2.1 Estructura principal

El corpus SersanSistemas contiene dos carpetas principales:

- `02_workshops`
- `03_only_md_revised`

`03_only_md_revised` contiene 17 MD principales revisados:

- `practica_02_donchain.md`
- `practica_03_donchain.md`
- `practica_04_donchain.md`
- `practica_05_donchain.md`
- `practica_06_ORB.md`
- `practica_07_ORB.md`
- `practica_08_ORB.md`
- `practica_09_revision_apolo.md`
- `practica_10_bollinger_bands.md`
- `practica_11_bollinger_Aberration.md`
- `practica_12_revised.md`
- `practica_13_revised.md`
- `practica_14_revised.md`
- `practica_15_revised.md`
- `practica_16_revised.md`
- `practica_17_revised.md`
- `xxx_revised.md`

### 2.2 Imagenes

Los MD revisados contienen 2,108 referencias a imagenes.

Con resolucion directa desde el MD, muchas referencias parecen faltantes porque
varias practicas usan rutas heredadas como `../img/...`.

Con un resolver por lesson pack que mapea:

```text
03_only_md_revised/practica_NN_*.md
-> 02_workshops/<NN+10>-practice-NN/img/
```

casi todas las imagenes se recuperan. Quedan tres referencias problematicas
detectadas inicialmente:

- `practica_03_donchain.md` -> `../../12-practice-02/img/002.png`
- `practica_07_ORB.md` -> badge externo de PDF
- `practica_12_revised.md` -> `../img/41.png`

Esto implica que el Harness no debe confiar solo en rutas Markdown. Debe tener
un resolver de assets por lesson pack.

### 2.3 Tipos de imagen observados

Las imagenes no son decorativas. Pueden contener:

- mapas de optimizacion;
- tablas Excel con parametros, rangos, fitness y robustness;
- pantallas TradeStation;
- performance reports;
- equity curves;
- drawdowns;
- portfolio analysis;
- MSA reports;
- codigo;
- configuraciones de slippage/comisiones;
- casos de halts o ejecucion irreal;
- comparativas IS/OOS/AllData;
- seleccion de sets;
- advertencias implicitas que no aparecen completas en texto.

Por tanto, toda destilacion valida debe leer texto e imagen.

## 3. Unidad minima: lesson pack

La unidad de trabajo no es un archivo. Es un lesson pack.

Un lesson pack se define como:

```text
lesson_pack =
  MD revisado
  + workshop folder asociada
  + imagenes asociadas
  + codigo asociado
  + xlsx/txt/html asociados cuando existan
  + notas de resolucion de assets
```

Ejemplo:

```text
03_only_md_revised/practica_09_revision_apolo.md
-> 02_workshops/19-practice-09/
```

Cada lesson pack debe tener un identificador estable:

```text
sersan_practice_09_revision_apolo
```

## 4. Principio de trazabilidad

Ninguna regla debe sobrevivir sin ancla de fuente.

Cada afirmacion destilada debe incluir:

- `lesson_id`;
- `source_md`;
- linea o seccion aproximada;
- imagenes asociadas si aplica;
- codigo asociado si aplica;
- nivel de confianza;
- tipo de artefacto destino;
- estado de promocion.

Formato recomendado de ancla:

```text
source_anchor:
  lesson_id: sersan_practice_09_revision_apolo
  md_path: 03_only_md_revised/practica_09_revision_apolo.md
  section: "Limitacion fundamental: dejar elegir entre 8.000 combinaciones es sobreoptimizar"
  image_refs:
    - 02_workshops/19-practice-09/img/126.png
    - 02_workshops/19-practice-09/img/127.png
    - 02_workshops/19-practice-09/img/128.png
```

## 5. Estados de promocion

La destilacion debe usar estos estados:

1. `source_observation`

   Observacion literal desde texto, imagen o codigo.

2. `interpreted_claim`

   Interpretacion tecnica del contenido.

3. `mechanical_rule_candidate`

   Regla accionable candidata.

4. `tsis_translation_candidate`

   Traduccion a lenguaje TSIS: backtest, evaluator, policy, validator, feature
   gate, AlphaEvolve constraint, etc.

5. `reviewed_doctrine_candidate`

   Candidato revisado y listo para promocion posterior.

6. `promoted`

   Ya incorporado en un documento canonico, policy, evaluator, validator o
   contrato del proyecto.

Regla:

```text
un agente puede proponer hasta reviewed_doctrine_candidate;
la promocion final exige revision humana o proceso canonico definido.
```

## 6. Pipeline Harness

### 6.1 Fase A: Corpus inventory

Objetivo:

- crear un inventario completo y estable del corpus;
- detectar lesson packs;
- contar assets;
- detectar referencias rotas;
- separar fuentes primarias de duplicados.

Output:

```text
sersan_corpus_manifest.csv
sersan_corpus_manifest.md
```

Campos minimos:

- `lesson_id`
- `practice_number`
- `title`
- `source_md`
- `workshop_dir`
- `image_dir`
- `code_dir`
- `pdf_count`
- `pdf_role`
- `image_ref_count`
- `image_resolved_count`
- `unresolved_image_refs`
- `code_artifacts_count`
- `xlsx_count`
- `status`

Regla:

```text
PDF role = duplicate_md unless explicitly proven otherwise.
```

### 6.2 Fase B: Lesson pack resolver

Objetivo:

- resolver rutas reales de imagenes y codigo;
- crear un mapa texto -> imagen -> artefacto;
- registrar assets que el MD referencia mal pero que existen en la carpeta de
  practica.

Output:

```text
lesson_pack_manifest.json
image_resolution_report.csv
```

Estados de imagen:

- `resolved_direct`;
- `resolved_lesson_fallback`;
- `external_reference`;
- `missing`;
- `not_required_duplicate`;
- `needs_human_review`.

### 6.3 Fase C: Text sectionizer

Objetivo:

- dividir el MD en secciones semanticas;
- separar preguntas, respuestas, teoria, codigo, tablas, advertencias y resumenes
  generados;
- asociar cada seccion con imagenes cercanas.

Output:

```text
lesson_sections.jsonl
```

Campos:

- `section_id`
- `heading_path`
- `start_line`
- `end_line`
- `section_type`
- `nearby_image_refs`
- `keywords`
- `raw_text_hash`

Tipos de seccion:

- `concept`
- `procedure`
- `warning`
- `qa`
- `code_explanation`
- `optimization`
- `validation`
- `portfolio`
- `money_management`
- `execution_realism`
- `image_only_context`
- `unclear`

### 6.4 Fase D: Image evidence reading

Objetivo:

- leer cada imagen relevante;
- extraer informacion visual que pueda cambiar la doctrina;
- no limitarse a describir la imagen.

Output:

```text
image_evidence_index.csv
image_evidence_notes/<image_id>.md
```

Campos minimos:

- `image_id`
- `lesson_id`
- `image_path`
- `referenced_from_section`
- `visual_type`
- `contains_numbers`
- `contains_code`
- `contains_chart`
- `contains_platform_config`
- `extracted_values`
- `technical_reading`
- `doctrine_relevance`
- `requires_human_review`

Tipos visuales:

- `optimization_map`
- `excel_parameter_grid`
- `fitness_summary`
- `performance_report`
- `equity_curve`
- `drawdown_curve`
- `portfolio_report`
- `platform_settings`
- `code_screenshot`
- `trade_example`
- `execution_anomaly`
- `concept_diagram`
- `unknown`

Regla critica:

```text
si la imagen contiene parametros, fitness, robustness, drawdown, comision,
slippage, OOS, IS, AllData, equity o portfolio metrics, debe extraerse como
dato estructurado o quedar marcado como needs_human_review.
```

### 6.5 Fase E: Mechanical rule extraction

Objetivo:

- convertir texto + imagen en reglas accionables;
- separar opinion, contexto, heuristica y regla mecanica.

Output:

```text
mechanical_rules.yaml
mechanical_rules.md
```

Schema recomendado:

```yaml
rule_id: sersan_rule_0001
lesson_id: sersan_practice_09_revision_apolo
source_anchor: ...
domain:
  - optimization
  - robustness
rule_type: hard_rule | soft_rule | warning | heuristic | open_question
statement: "A set is not valid only because it ranks well; it must live inside a robust zone."
trigger: "Selecting parameter sets after optimization."
required_evidence:
  - optimization_map
  - IS/OOS comparison
  - robustness metric
tsis_translation:
  target: strategy_evaluator
  action: require_zone_robustness_check
confidence: high
promotion_state: mechanical_rule_candidate
```

### 6.6 Fase F: TSIS translation

Objetivo:

- traducir reglas Sersan a artefactos TSIS.

Destinos posibles:

- `strategy_evaluator`;
- `backtest_checklist`;
- `data_quality_gate`;
- `feature_leakage_check`;
- `execution_realism_check`;
- `portfolio_evaluator`;
- `money_management_policy`;
- `AlphaEvolve_constraint`;
- `human_review_checklist`;
- `research_protocol`;
- `do_not_promote_rule`.

Output:

```text
tsis_translation_map.csv
tsis_translation_notes.md
```

### 6.7 Fase G: Doctrine review

Objetivo:

- revisar contradicciones;
- detectar reglas duplicadas;
- elevar confianza o rebajarla;
- decidir si una regla queda como doctrina candidata o solo como nota.

Output:

```text
doctrine_candidates.md
open_questions.md
contradiction_log.md
```

### 6.8 Fase H: Promotion package

Objetivo:

- preparar un paquete listo para promocion canonica.

Output:

```text
promotion_package/<domain>/README.md
promotion_package/<domain>/rules.yaml
promotion_package/<domain>/evaluator_requirements.md
promotion_package/<domain>/source_trace.csv
```

No se promociona automaticamente.

## 7. Dominios doctrinales

Toda regla debe clasificarse al menos en uno de estos dominios:

- `data_semantics`
- `price_view`
- `bar_construction`
- `setup_logic`
- `entry_logic`
- `exit_logic`
- `stop_loss`
- `take_profit`
- `filters`
- `optimization`
- `overfitting`
- `robustness`
- `BRaC`
- `walk_forward`
- `IS_OOS`
- `sample_size`
- `trade_distribution`
- `execution_realism`
- `commissions_slippage`
- `halts`
- `money_management`
- `position_sizing`
- `portfolio`
- `correlation`
- `regime`
- `market_microstructure`
- `small_caps_transfer`
- `AlphaEvolve_constraints`

## 8. Reglas ya observadas que el protocolo debe capturar

Estas reglas no son aun doctrina canonica. Son ejemplos observados para probar
que el protocolo extrae bien.

### 8.1 Apolo: set dentro de zona robusta

Observacion:

- En `practica_09_revision_apolo.md`, la revision de Apolo enfatiza que un set
  no es valido solo por ranking.
- Debe estar dentro de una zona robusta del mapa.
- El Excel y los mapas visuales son evidencia obligatoria.

Traduccion TSIS candidata:

```text
strategy_evaluator debe exigir prueba de vecindad/region robusta antes de
aceptar parametros optimizados.
```

### 8.2 Apolo: 8,000 combinaciones pueden sobreoptimizar

Observacion:

- Permitir seleccionar entre 8,000 combinaciones IS puede inducir
  sobreoptimizacion.
- El proceso reduce a 250 sets para facilitar seleccion y evitar sesgo.

Traduccion TSIS candidata:

```text
AlphaEvolve no puede seleccionar candidatos solo por ranking bruto; necesita
constraints de diversidad, OOS, robustness y region estable.
```

### 8.3 Apolo: ejecucion irreal por halt

Observacion:

- Se introduce una penalizacion por un caso de halt COVID donde el precio
  marcado no era ejecutable.

Traduccion TSIS candidata:

```text
execution_realism_check debe penalizar fills imposibles y eventos de halt.
```

### 8.4 BRaC y muestra significativa

Observacion:

- BRaC se presenta como comparacion Build/Reveal/Compare.
- Tambien se matiza que con muestra muy grande, distribucion uniforme de trades,
  idea simple y mapa estable, distintas metodologias pueden converger.

Traduccion TSIS candidata:

```text
strategy_evaluator debe medir robustez por varios caminos y no convertir una
metodologia concreta en religion si la evidencia estadistica es fuerte.
```

### 8.5 Money management puede enganar

Observacion:

- Money management agresivo produce curvas atractivas pero puede ocultar
  drawdowns muy fuertes.
- Si se usa money management, debe evaluarse en porcentaje.
- Si no se usa, puede mirarse retorno bruto.

Traduccion TSIS candidata:

```text
money_management_policy debe exigir evaluacion en porcentaje, drawdown real y
sensibilidad a agresividad de sizing.
```

## 9. Agentes propuestos para cuando el protocolo este validado

No se deben implementar todavia como agentes productivos. Esta es la division
de responsabilidades futura.

### 9.1 `sersan_corpus_inventory_agent`

Responsabilidad:

- construir inventario;
- detectar lesson packs;
- contar y validar assets.

### 9.2 `lesson_pack_resolver_agent`

Responsabilidad:

- resolver rutas;
- mapear MD a workshop;
- asociar imagenes y codigo.

### 9.3 `text_sectionizer_agent`

Responsabilidad:

- dividir el MD en unidades semanticas;
- detectar secciones de alto valor.

### 9.4 `image_evidence_reader_agent`

Responsabilidad:

- leer imagenes;
- extraer valores;
- clasificar tipo visual;
- marcar imagenes que requieren revision humana.

### 9.5 `mechanical_rule_extractor_agent`

Responsabilidad:

- extraer reglas;
- separar literalidad de interpretacion;
- generar YAML de reglas.

### 9.6 `tsis_translation_agent`

Responsabilidad:

- traducir reglas a checks, policies, evaluadores o constraints.

### 9.7 `doctrine_reviewer_agent`

Responsabilidad:

- detectar contradicciones;
- fusionar duplicados;
- preparar promotion package.

### 9.8 `evaluator_mapping_agent`

Responsabilidad:

- convertir doctrina revisada en requisitos de evaluador.

## 10. Control de calidad de la destilacion

Una destilacion falla si:

- resume sin source anchors;
- ignora imagenes;
- convierte opinion en regla dura;
- no separa contexto de regla;
- no conserva incertidumbre;
- no distingue clase, practica, codigo e imagen;
- no detecta contradicciones;
- no produce artefactos estructurados;
- promueve reglas sin revision;
- no indica como se usaria en TSIS.

Una destilacion pasa si:

- cada regla tiene trazabilidad;
- cada imagen relevante fue leida o marcada;
- cada regla tiene tipo y dominio;
- cada regla tiene destino TSIS candidato;
- cada incertidumbre queda abierta;
- los outputs son reproducibles;
- otro agente puede continuar desde los artefactos.

## 11. Output por lesson pack

Cada lesson pack destilado debe producir esta carpeta:

```text
<distillation_root>/<lesson_id>/
  lesson_pack_manifest.json
  lesson_sections.jsonl
  image_evidence_index.csv
  image_evidence_notes/
  mechanical_rules.yaml
  lesson_distillation.md
  tsis_translation_map.csv
  open_questions.md
  quality_report.md
```

### 11.1 `lesson_distillation.md`

Debe contener:

- resumen ejecutivo;
- que ensena la clase;
- reglas mecanicas;
- advertencias;
- anti-patrones;
- imagenes clave;
- codigo relevante;
- traduccion TSIS;
- dudas abiertas;
- estado de promocion.

### 11.2 `quality_report.md`

Debe responder:

- cuantas imagenes fueron leidas;
- cuantas quedaron pendientes;
- cuantas reglas se extrajeron;
- cuantas son hard/soft/warning/heuristic;
- que dominios cubre;
- que contradicciones aparecen;
- que parte requiere revision humana.

## 12. Orden recomendado de trabajo

El orden recomendado no es numerico puro. Debe combinar fundamento y bloques
criticos.

### Fase 1: Inventario completo

Crear manifest de todo el corpus y validar assets.

Done cuando:

- todos los MD tienen lesson_id;
- cada MD esta vinculado a su workshop folder;
- las imagenes tienen estado de resolucion;
- los PDFs estan marcados como duplicados;
- los problemas de rutas quedan registrados.

### Fase 2: Probar protocolo en tres clases

Clases piloto:

1. `practica_02_donchain.md`
2. `practica_09_revision_apolo.md`
3. `practica_15_revised.md`

Razon:

- Donchian cubre construccion inicial, BRaC y robustez base.
- Apolo cubre revision real, optimizacion, zonas robustas, OOS y ejecucion.
- Practica 15 cubre money management, sizing y portfolio.

### Fase 3: Ajustar schema

No avanzar al corpus entero hasta que los tres pilotos produzcan artefactos
comparables.

### Fase 4: Destilar corpus completo

Procesar practicas 02 a 17.

### Fase 5: Consolidacion doctrinal

Fusionar reglas duplicadas y generar documentos por dominio:

- `robustness_doctrine.md`
- `optimization_doctrine.md`
- `walk_forward_brac_doctrine.md`
- `money_management_doctrine.md`
- `portfolio_doctrine.md`
- `execution_realism_doctrine.md`
- `backtest_minimum_evaluator_requirements.md`

### Fase 6: Mapping a TSIS evaluators

Convertir doctrina revisada en especificaciones de evaluador.

## 13. Relacion con Data Quality Harness

El Data Quality Harness y el Sersan Distillation Harness son frentes distintos,
pero se conectan.

Data Quality Harness responde:

```text
que data puedo usar y bajo que flags
```

Sersan Distillation Harness responde:

```text
como debo evaluar si una estrategia/backtest es mecanicamente defendible
```

AlphaEvolve solo debe operar cuando ambos frentes produzcan constraints:

```text
data gated + evaluator locked + doctrine constraints
```

## 14. Reglas para AlphaEvolve derivadas del protocolo

AlphaEvolve no debe:

- tocar evaluadores;
- elegir parametros solo por ranking;
- usar data sin estado de calidad;
- ignorar comisiones/slippage;
- ignorar halts o ejecucion irreal;
- optimizar filtros sin penalizar sobreoptimizacion;
- usar money management agresivo para maquillar edge;
- promocionar candidatos sin region robusta;
- ampliar OOS despues de ver resultados;
- ocultar lineage de imagenes/reglas que justifican constraints.

AlphaEvolve si puede:

- proponer candidatos;
- mejorar rendimiento tecnico del backtester;
- buscar filtros bajo constraints;
- explorar features con leakage checks;
- proponer sizing heuristics bajo evaluador bloqueado;
- generar variantes para estudio, no para promocion automatica.

## 15. Primer siguiente paso

El siguiente documento despues de este protocolo debe ser:

```text
20_SERSAN_DISTILLATION_HARNESS/sersan_lesson_pack_contract.md
```

Debe fijar schemas exactos de:

- `lesson_pack_manifest.json`;
- `lesson_sections.jsonl`;
- `image_evidence_index.csv`;
- `mechanical_rules.yaml`;
- `tsis_translation_map.csv`;
- `quality_report.md`.

Justificacion:

Sin contrato de artefactos, cada agente destilara con formato propio y el corpus
no podra consolidarse.

## 16. Decision v0.1

El enfoque correcto para SersanSistemas es:

```text
inventario -> lesson pack -> texto + imagen -> regla mecanica -> traduccion TSIS -> revision -> promocion
```

No se empieza creando agentes finales.

Primero se fija el protocolo, despues los contratos de output, despues tres
pilotos, y solo entonces se ejecuta la destilacion completa del curso.
