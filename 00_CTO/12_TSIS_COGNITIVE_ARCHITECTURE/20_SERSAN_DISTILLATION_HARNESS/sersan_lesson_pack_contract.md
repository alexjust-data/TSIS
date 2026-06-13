# Sersan Lesson Pack Artifact Contract

Fecha: 2026-06-12
Estado: contract v0.1.1
Ambito: `C:\TSIS_Data\00_CTO\99_REFERENCE_LIBRARY\SersanSistemas`
Depende de:

- `20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_protocol.md`
- `00_SHARED_HARNESS_KERNEL/harness_toolchain_traceability_contract.md`

## 0. Proposito

Este documento fija los contratos exactos de artefactos que deben producir los
futuros Harness agents al destilar cada lesson pack del corpus SersanSistemas.

Sin este contrato, cada agente podria destilar el curso con formato propio y la
consolidacion final seria fragil. Con este contrato, cada clase produce outputs
comparables, validables, auditables y consolidables.

Regla base:

```text
un lesson pack no se considera destilado si no produce todos los artefactos de
este contrato y si esos artefactos no pasan validacion estructural.
```

## 1. Scope

### 1.1 Incluido

Este contrato define:

- estructura de carpeta de salida por lesson pack;
- naming convention;
- estados permitidos;
- schemas de:
  - `lesson_pack_manifest.json`;
  - `lesson_sections.jsonl`;
  - `image_evidence_index.csv`;
  - `mechanical_rules.yaml`;
  - `tsis_translation_map.csv`;
  - `quality_report.md`;
- reglas de validacion;
- criterios de aceptacion;
- errores bloqueantes.

### 1.2 No incluido

Este contrato no define:

- implementacion de agentes;
- prompts finales;
- codigo de validadores;
- promocion canonica de doctrina;
- evaluadores finales de trading;
- formato definitivo de AlphaEvolve sandbox.

## 2. Conceptos

### 2.1 Lesson pack

Unidad minima de destilacion:

```text
lesson_pack =
  MD revisado
  + workshop folder asociada
  + imagenes asociadas
  + codigo asociado
  + xlsx/txt/html asociados cuando existan
  + notas de resolucion de assets
```

### 2.2 Lesson id

Identificador estable, ASCII, snake_case:

```text
sersan_practice_09_revision_apolo
```

Formato:

```regex
^sersan_practice_[0-9]{2}_[a-z0-9_]+$
```

Casos especiales:

- material extra puede usar `sersan_extra_<slug>`;
- material sin practica puede usar `sersan_unmapped_<slug>` hasta revision.

### 2.3 Source anchor

Referencia trazable a la fuente:

```yaml
source_anchor:
  lesson_id: sersan_practice_09_revision_apolo
  md_path: 03_only_md_revised/practica_09_revision_apolo.md
  section_id: sersan_practice_09_revision_apolo_sec_0017
  line_start: 1686
  line_end: 1874
  image_ids:
    - sersan_practice_09_revision_apolo_img_126
```

### 2.4 Artifact root

Root recomendado para outputs de destilacion:

```text
C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\20_SERSAN_DISTILLATION_HARNESS\sersan_distillation_artifacts\
```

Este root no se crea en este contrato. Solo se define como ubicacion
recomendada para ejecuciones futuras.

## 3. Estructura de salida obligatoria


### 3.1 Trazabilidad obligatoria de toolchain

Este contrato define los artefactos del lesson pack. Desde 2026-06-11, una
destilacion completa tambien debe cumplir:

```text
00_SHARED_HARNESS_KERNEL/harness_toolchain_traceability_contract.md
```

Regla:

```text
ningun lesson pack se acepta si su generador, validador, prompt operativo o
template propio solo existe en C:\Users, C:\tmp, Downloads o una conversacion.
```

La toolchain propia debe vivir en ruta de proyecto, preferentemente:

```text
00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/harness_toolchain/sersan_distillation/
```

Ademas de los artefactos del lesson pack, cada ejecucion aceptable debe dejar:

```text
run_manifest.json
```

Ese manifest debe declarar:

- comando de ejecucion;
- generadores;
- validadores si existen;
- prompts operativos si existen;
- hashes SHA256 de toolchain;
- inputs;
- outputs;
- limitaciones;
- decision de aceptacion.

Si un script temporal se uso durante exploracion, el output queda no aceptado
hasta que la toolchain se promueva al proyecto y se re-ejecute desde esa ruta o
se documente una excepcion bloqueante.

Cada lesson pack debe producir:

```text
<distillation_root>/<lesson_id>/
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

Este contrato cubre seis artefactos obligatorios:

```text
lesson_pack_manifest.json
lesson_sections.jsonl
image_evidence_index.csv
mechanical_rules.yaml
tsis_translation_map.csv
quality_report.md
```

Los otros tres son auxiliares, pero deben existir en una destilacion completa:

```text
image_evidence_notes/
lesson_distillation.md
open_questions.md
```

## 4. Estados canonicos

### 4.1 Estado de lesson pack

Valores permitidos:

- `not_started`
- `inventory_only`
- `assets_resolved`
- `sectionized`
- `images_read`
- `rules_extracted`
- `translated`
- `reviewed`
- `blocked`

### 4.2 Estado de imagen

Valores permitidos:

- `resolved_direct`
- `resolved_lesson_fallback`
- `external_reference`
- `missing`
- `duplicate_reference`
- `not_required_duplicate`
- `needs_human_review`

### 4.2.1 Extraccion de referencias visuales

Los agentes y generadores del Sersan Distillation Harness deben extraer
referencias de imagen desde, como minimo, estas dos sintaxis:

- Markdown image syntax: `![alt](path/to/image.png)`;
- HTML inline image syntax: `<img src="path/to/image.png" ...>`.

Razon:

```text
practice_09 usa etiquetas HTML <img src=...>. Si el parser solo acepta
Markdown image syntax, el lesson pack puede parecer valido con 0 imagenes
leidas aunque el MD contenga evidencia visual critica.
```

Regla:

```text
un lesson pack con imagenes en el MD no puede aceptarse si `image_refs_total`
queda en 0 por limitacion del parser.
```

### 4.3 Tipo de seccion

Valores permitidos:

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

### 4.4 Tipo visual

Valores permitidos:

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
- `ui_navigation`
- `unknown`

### 4.5 Dominio doctrinal

Valores permitidos:

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
- `other`

### 4.6 Rule type

Valores permitidos:

- `hard_rule`
- `soft_rule`
- `warning`
- `heuristic`
- `open_question`

### 4.7 Promotion state

Valores permitidos:

- `source_observation`
- `interpreted_claim`
- `mechanical_rule_candidate`
- `tsis_translation_candidate`
- `reviewed_doctrine_candidate`
- `promoted`
- `rejected`

### 4.8 Confidence

Valores permitidos:

- `low`
- `medium`
- `high`
- `requires_human_review`

### 4.9 TSIS target

Valores permitidos:

- `strategy_evaluator`
- `backtest_checklist`
- `data_quality_gate`
- `feature_leakage_check`
- `execution_realism_check`
- `portfolio_evaluator`
- `money_management_policy`
- `AlphaEvolve_constraint`
- `human_review_checklist`
- `research_protocol`
- `do_not_promote_rule`
- `documentation_only`
- `open_question`

## 5. Contract: `lesson_pack_manifest.json`

### 5.1 Purpose

Manifest estructural del lesson pack. Debe permitir saber que se proceso, que
assets existen, que rutas se resolvieron y que estado tiene la destilacion.

### 5.2 Cardinalidad

Un archivo por lesson pack.

### 5.3 JSON Schema v0.1

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "tsis.sersan.lesson_pack_manifest.v0_1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "contract_version",
    "generated_at_utc",
    "generated_by",
    "lesson_id",
    "practice_number",
    "title",
    "status",
    "source_md",
    "workshop_dir",
    "image_dir",
    "asset_resolution",
    "source_hashes",
    "counts",
    "known_issues"
  ],
  "properties": {
    "contract_version": {
      "type": "string",
      "const": "sersan_lesson_pack_contract_v0_1"
    },
    "generated_at_utc": {
      "type": "string",
      "format": "date-time"
    },
    "generated_by": {
      "type": "string",
      "minLength": 1
    },
    "lesson_id": {
      "type": "string",
      "pattern": "^sersan_(practice_[0-9]{2}|extra|unmapped)_[a-z0-9_]+$"
    },
    "practice_number": {
      "type": ["integer", "null"],
      "minimum": 0,
      "maximum": 99
    },
    "title": {
      "type": "string",
      "minLength": 1
    },
    "status": {
      "type": "string",
      "enum": [
        "not_started",
        "inventory_only",
        "assets_resolved",
        "sectionized",
        "images_read",
        "rules_extracted",
        "translated",
        "reviewed",
        "blocked"
      ]
    },
    "source_md": {
      "type": "string",
      "minLength": 1
    },
    "workshop_dir": {
      "type": ["string", "null"]
    },
    "image_dir": {
      "type": ["string", "null"]
    },
    "pdf_role": {
      "type": "string",
      "enum": ["duplicate_md", "layout_reference", "primary_source", "not_present", "unknown"],
      "default": "duplicate_md"
    },
    "video_role": {
      "type": "string",
      "enum": ["out_of_scope", "not_present", "primary_source", "unknown"],
      "default": "out_of_scope"
    },
    "asset_resolution": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "resolver_version",
        "image_refs_total",
        "resolved_direct",
        "resolved_lesson_fallback",
        "external_reference",
        "missing",
        "needs_human_review"
      ],
      "properties": {
        "resolver_version": {"type": "string"},
        "image_refs_total": {"type": "integer", "minimum": 0},
        "resolved_direct": {"type": "integer", "minimum": 0},
        "resolved_lesson_fallback": {"type": "integer", "minimum": 0},
        "external_reference": {"type": "integer", "minimum": 0},
        "missing": {"type": "integer", "minimum": 0},
        "needs_human_review": {"type": "integer", "minimum": 0}
      }
    },
    "source_hashes": {
      "type": "object",
      "additionalProperties": {"type": "string"},
      "minProperties": 1
    },
    "counts": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "md_lines",
        "sections",
        "images",
        "code_artifacts",
        "xlsx_artifacts",
        "rules",
        "translations",
        "open_questions"
      ],
      "properties": {
        "md_lines": {"type": "integer", "minimum": 0},
        "sections": {"type": "integer", "minimum": 0},
        "images": {"type": "integer", "minimum": 0},
        "code_artifacts": {"type": "integer", "minimum": 0},
        "xlsx_artifacts": {"type": "integer", "minimum": 0},
        "rules": {"type": "integer", "minimum": 0},
        "translations": {"type": "integer", "minimum": 0},
        "open_questions": {"type": "integer", "minimum": 0}
      }
    },
    "known_issues": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}
```

### 5.4 Example

```json
{
  "contract_version": "sersan_lesson_pack_contract_v0_1",
  "generated_at_utc": "2026-06-11T20:00:00Z",
  "generated_by": "sersan_corpus_inventory_agent_v0_1",
  "lesson_id": "sersan_practice_09_revision_apolo",
  "practice_number": 9,
  "title": "Revision Apolo",
  "status": "assets_resolved",
  "source_md": "03_only_md_revised/practica_09_revision_apolo.md",
  "workshop_dir": "02_workshops/19-practice-09",
  "image_dir": "02_workshops/19-practice-09/img",
  "pdf_role": "duplicate_md",
  "video_role": "out_of_scope",
  "asset_resolution": {
    "resolver_version": "lesson_pack_resolver_v0_1",
    "image_refs_total": 171,
    "resolved_direct": 171,
    "resolved_lesson_fallback": 0,
    "external_reference": 0,
    "missing": 0,
    "needs_human_review": 0
  },
  "source_hashes": {
    "03_only_md_revised/practica_09_revision_apolo.md": "sha256:<hash>"
  },
  "counts": {
    "md_lines": 2400,
    "sections": 0,
    "images": 171,
    "code_artifacts": 0,
    "xlsx_artifacts": 0,
    "rules": 0,
    "translations": 0,
    "open_questions": 0
  },
  "known_issues": []
}
```

## 6. Contract: `lesson_sections.jsonl`

### 6.1 Purpose

Line-delimited JSON con las secciones semanticas del MD. Es la base para que
los agentes no destilen texto como bloque gigante.

### 6.2 Cardinalidad

Un record JSON por seccion.

### 6.3 Required fields

Cada linea debe cumplir:

```json
{
  "contract_version": "sersan_lesson_sections_v0_1",
  "lesson_id": "sersan_practice_09_revision_apolo",
  "section_id": "sersan_practice_09_revision_apolo_sec_0017",
  "heading_path": ["Practice 9", "Revision de Apolo", "Limitacion fundamental"],
  "section_type": "optimization",
  "line_start": 1686,
  "line_end": 1874,
  "raw_text_hash": "sha256:<hash>",
  "summary": "Short factual summary of this section.",
  "keywords": ["optimization", "overfitting", "robustness"],
  "nearby_image_ids": [
    "sersan_practice_09_revision_apolo_img_126"
  ],
  "contains_code": false,
  "contains_table": true,
  "contains_question": false,
  "requires_image_reading": true,
  "requires_human_review": false,
  "notes": []
}
```

### 6.4 Field contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `contract_version` | string | yes | Must equal `sersan_lesson_sections_v0_1` |
| `lesson_id` | string | yes | Must match manifest |
| `section_id` | string | yes | Unique within lesson |
| `heading_path` | array[string] | yes | Ordered from top heading to local heading |
| `section_type` | enum | yes | Must use canonical section types |
| `line_start` | integer | yes | 1-based line number |
| `line_end` | integer | yes | >= `line_start` |
| `raw_text_hash` | string | yes | SHA256 of exact section text |
| `summary` | string | yes | Factual, no doctrine promotion |
| `keywords` | array[string] | yes | Lowercase slug terms |
| `nearby_image_ids` | array[string] | yes | Empty allowed |
| `contains_code` | boolean | yes | True if code appears |
| `contains_table` | boolean | yes | True if table/HTML table appears |
| `contains_question` | boolean | yes | True for Q&A |
| `requires_image_reading` | boolean | yes | True if image changes interpretation |
| `requires_human_review` | boolean | yes | True if ambiguous or high impact |
| `notes` | array[string] | yes | Empty allowed |

### 6.5 Validation rules

- `section_id` must be unique.
- `line_start` and `line_end` must not overlap unless explicit duplicate block.
- Every `nearby_image_id` must exist in `image_evidence_index.csv`.
- If `requires_image_reading=true`, at least one nearby image must exist or an
  open question must be created.
- Section summaries must not contain final TSIS promotion language such as
  `promoted`, `mandatory` or `canonical` unless the section itself is about
  promotion status.

## 7. Contract: `image_evidence_index.csv`

### 7.1 Purpose

Indice estructurado de imagenes asociadas al lesson pack. Debe permitir que una
imagen sea trazable desde el MD hasta una regla mecanica.

### 7.2 Required CSV header

El header exacto debe ser:

```csv
contract_version,lesson_id,image_id,source_ref,resolved_path,resolution_status,referenced_from_section_ids,visual_type,contains_numbers,contains_code,contains_chart,contains_platform_config,extracted_values_ref,technical_reading_ref,doctrine_relevance,requires_human_review,notes
```

### 7.3 Field contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `contract_version` | string | yes | `sersan_image_evidence_index_v0_1` |
| `lesson_id` | string | yes | Must match manifest |
| `image_id` | string | yes | Unique stable id |
| `source_ref` | string | yes | Original MD ref or external URL |
| `resolved_path` | string | yes | Empty only for external/missing |
| `resolution_status` | enum | yes | Canonical image status |
| `referenced_from_section_ids` | pipe-list | yes | `sec_001|sec_002` |
| `visual_type` | enum | yes | Canonical visual type |
| `contains_numbers` | boolean | yes | `true`/`false` |
| `contains_code` | boolean | yes | `true`/`false` |
| `contains_chart` | boolean | yes | `true`/`false` |
| `contains_platform_config` | boolean | yes | `true`/`false` |
| `extracted_values_ref` | string | yes | Path to note or empty if none |
| `technical_reading_ref` | string | yes | Path to image note |
| `doctrine_relevance` | enum | yes | `none`, `low`, `medium`, `high`, `critical` |
| `requires_human_review` | boolean | yes | `true`/`false` |
| `notes` | string | yes | May be empty |

### 7.4 Image id

Formato recomendado:

```text
<lesson_id>_img_<number_or_slug>
```

Ejemplo:

```text
sersan_practice_09_revision_apolo_img_142
```

### 7.5 Required image note

Si una imagen tiene `doctrine_relevance` en `medium`, `high` o `critical`, debe
existir un archivo:

```text
image_evidence_notes/<image_id>.md
```

Con este formato minimo:

```markdown
# <image_id>

## Source

- lesson_id:
- source_ref:
- resolved_path:
- referenced_from_sections:

## Visual Type

## Extracted Values

## Technical Reading

## Doctrine Relevance

## Open Questions
```

### 7.6 Validation rules

- Every image referenced by a section must appear in the CSV.
- Every `resolved_path` with local path must exist.
- `missing` images must be listed in `quality_report.md`.
- `external_reference` must not be treated as missing if intentionally external.
- If `contains_numbers=true`, `extracted_values_ref` should not be empty unless
  `requires_human_review=true`.
- If `visual_type=unknown` and `doctrine_relevance` is not `none`, human review
  is required.

## 8. Contract: `mechanical_rules.yaml`

### 8.1 Purpose

Reglas mecanicas candidatas extraidas desde texto + imagen + codigo. Este
archivo no promociona doctrina por si mismo.

### 8.2 Top-level schema

```yaml
contract_version: sersan_mechanical_rules_v0_1
lesson_id: sersan_practice_09_revision_apolo
generated_at_utc: "2026-06-11T20:00:00Z"
generated_by: mechanical_rule_extractor_agent_v0_1
rules:
  - rule_id: sersan_practice_09_revision_apolo_rule_0001
    promotion_state: mechanical_rule_candidate
    confidence: high
    rule_type: hard_rule
    domains:
      - optimization
      - robustness
      - overfitting
    statement: "A parameter set is not acceptable only because it ranks well; it must belong to a robust zone."
    trigger: "Selecting parameter sets after optimization."
    action: "Require robust-zone evidence before accepting the set."
    failure_mode_if_ignored: "Overfit parameter selection from ranking noise."
    required_evidence:
      - optimization_map
      - IS_OOS_comparison
      - robustness_metric
    source_anchors:
      - lesson_id: sersan_practice_09_revision_apolo
        md_path: 03_only_md_revised/practica_09_revision_apolo.md
        section_id: sersan_practice_09_revision_apolo_sec_0017
        line_start: 1686
        line_end: 1874
        image_ids:
          - sersan_practice_09_revision_apolo_img_126
          - sersan_practice_09_revision_apolo_img_127
    caveats:
      - "Needs human review before becoming canonical TSIS doctrine."
    related_rules: []
```

### 8.3 Required rule fields

| Field | Type | Required | Rule |
|---|---|---:|---|
| `rule_id` | string | yes | Unique stable id |
| `promotion_state` | enum | yes | Must not be `promoted` unless already canonized elsewhere |
| `confidence` | enum | yes | Canonical confidence |
| `rule_type` | enum | yes | Canonical rule type |
| `domains` | array[enum] | yes | At least one |
| `statement` | string | yes | Direct rule wording |
| `trigger` | string | yes | When this rule applies |
| `action` | string | yes | What TSIS should do or check |
| `failure_mode_if_ignored` | string | yes | Risk created if ignored |
| `required_evidence` | array[string] | yes | Empty only for open_question |
| `source_anchors` | array[object] | yes | At least one |
| `caveats` | array[string] | yes | Empty allowed only if confidence high |
| `related_rules` | array[string] | yes | Empty allowed |

### 8.4 Rule quality constraints

A mechanical rule is invalid if:

- it has no source anchor;
- it has no trigger;
- it has no failure mode;
- it turns one anecdote into a universal hard rule without caveat;
- it promotes itself to canonical doctrine;
- it ignores linked images when images are relevant;
- it uses vague wording like "be careful" without operational action.

### 8.5 Good vs bad rule

Bad:

```yaml
statement: "Avoid overfitting."
```

Good:

```yaml
statement: "Do not select an optimized parameter set only by ranking; require evidence that the set lies inside a robust zone."
trigger: "Parameter selection after optimization."
action: "Check local neighborhood stability and IS/OOS/AllData agreement."
failure_mode_if_ignored: "The chosen set may be an isolated optimum."
```

## 9. Contract: `tsis_translation_map.csv`

### 9.1 Purpose

Mapea reglas mecanicas a artefactos TSIS candidatos: evaluadores, policies,
checklists, gates o constraints.

### 9.2 Required CSV header

```csv
contract_version,lesson_id,translation_id,rule_id,target,tsis_artifact_candidate,action_type,priority,blocking_power,consumer_scope,implementation_hint,requires_human_review,source_anchor_refs,notes
```

### 9.3 Field contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `contract_version` | string | yes | `sersan_tsis_translation_map_v0_1` |
| `lesson_id` | string | yes | Must match manifest |
| `translation_id` | string | yes | Unique stable id |
| `rule_id` | string | yes | Must exist in `mechanical_rules.yaml` |
| `target` | enum | yes | Canonical TSIS target |
| `tsis_artifact_candidate` | string | yes | Candidate doc/policy/evaluator name |
| `action_type` | enum | yes | `require`, `warn`, `block`, `score`, `document`, `review` |
| `priority` | enum | yes | `low`, `medium`, `high`, `critical` |
| `blocking_power` | enum | yes | `none`, `soft_gate`, `hard_gate`, `human_review_gate` |
| `consumer_scope` | pipe-list | yes | e.g. `backtest|ML|AlphaEvolve` |
| `implementation_hint` | string | yes | Concrete engineering hint |
| `requires_human_review` | boolean | yes | `true`/`false` |
| `source_anchor_refs` | pipe-list | yes | Rule/source ids |
| `notes` | string | yes | May be empty |

### 9.4 Example row

```csv
contract_version,lesson_id,translation_id,rule_id,target,tsis_artifact_candidate,action_type,priority,blocking_power,consumer_scope,implementation_hint,requires_human_review,source_anchor_refs,notes
sersan_tsis_translation_map_v0_1,sersan_practice_09_revision_apolo,sersan_practice_09_revision_apolo_tr_0001,sersan_practice_09_revision_apolo_rule_0001,strategy_evaluator,TSIS_EVALUATOR_CONTRACT_TRADING_v0_1,require,critical,hard_gate,backtest|AlphaEvolve,"Require robust-zone evidence before accepting optimized params.",true,sersan_practice_09_revision_apolo_rule_0001,"Candidate only; needs doctrine review."
```

### 9.5 Validation rules

- Every `rule_id` must exist.
- Every `critical` translation must require human review unless already
  promoted elsewhere.
- `AlphaEvolve` scope with `blocking_power=none` is invalid for rules about
  overfitting, leakage, data quality, execution realism or money management.
- `implementation_hint` must be actionable.

## 10. Contract: `quality_report.md`

### 10.1 Purpose

Reporte humano y auditor que declara si la destilacion del lesson pack es
aceptable.

### 10.2 Required structure

El archivo debe tener exactamente estas secciones top-level:

```markdown
# Quality Report: <lesson_id>

## 1. Summary

## 2. Input Coverage

## 3. Asset Resolution

## 4. Sectionization Quality

## 5. Image Reading Quality

## 6. Mechanical Rule Quality

## 7. TSIS Translation Quality

## 8. Open Questions

## 9. Blocking Issues

## 10. Acceptance Decision
```

### 10.3 Required metrics

`## 1. Summary` debe contener una tabla:

```markdown
| Metric | Value |
|---|---:|
| lesson_id | ... |
| status | ... |
| md_lines | ... |
| sections | ... |
| image_refs_total | ... |
| images_resolved | ... |
| images_missing | ... |
| images_read | ... |
| rules_extracted | ... |
| translations_created | ... |
| open_questions | ... |
| blocking_issues | ... |
```

### 10.4 Acceptance decision

Valores permitidos:

- `pass`
- `pass_with_warnings`
- `needs_human_review`
- `fail`

### 10.5 Pass criteria

Una destilacion puede recibir `pass` solo si:

- existe `lesson_pack_manifest.json`;
- existe `lesson_sections.jsonl`;
- existe `image_evidence_index.csv`;
- existe `mechanical_rules.yaml`;
- existe `tsis_translation_map.csv`;
- existe `quality_report.md`;
- todas las secciones tienen source line ranges;
- todas las imagenes referenciadas estan resueltas, externalizadas o justificadas;
- toda imagen de relevancia `medium` o superior tiene note;
- toda regla tiene source anchor;
- toda traduccion referencia una regla existente;
- no hay blocking issues.

### 10.6 Fail criteria

Una destilacion debe recibir `fail` si:

- faltan artefactos obligatorios;
- hay schema invalid;
- hay imagenes relevantes ignoradas;
- hay reglas sin source anchor;
- se promociona doctrina sin autorizacion;
- se mezclan fuentes no trazadas;
- el agente declara una conclusion sin evidencia;
- se omite `quality_report.md`;
- el output no puede consolidarse con otros lesson packs.

## 11. Cross-artifact consistency rules

### 11.1 Manifest vs sections

- `counts.sections` debe coincidir con el numero de lineas de
  `lesson_sections.jsonl`.
- `lesson_id` debe ser igual en todos los records.

### 11.2 Sections vs images

- Todo `nearby_image_id` en sections debe existir en `image_evidence_index.csv`.
- Toda imagen con `referenced_from_section_ids` debe referir secciones existentes.

### 11.3 Images vs rules

- Toda regla que use `image_ids` debe referir imagenes existentes.
- Si una imagen tiene `doctrine_relevance=critical`, debe existir al menos una
  regla o una open question que la mencione.

### 11.4 Rules vs translations

- Toda traduccion debe referir una regla existente.
- No toda regla requiere traduccion, pero las reglas `hard_rule` y `warning`
  con confidence `high` deben traducirse o justificarse en `quality_report.md`.

### 11.5 Quality report vs everything

- El reporte debe listar cualquier discrepancia.
- El reporte no puede declarar `pass` si hay discrepancia bloqueante.

## 12. Naming conventions

### 12.1 Section id

```text
<lesson_id>_sec_<4-digit-number>
```

Example:

```text
sersan_practice_09_revision_apolo_sec_0017
```

### 12.2 Image id

```text
<lesson_id>_img_<source-number-or-slug>
```

Example:

```text
sersan_practice_09_revision_apolo_img_142
```

### 12.3 Rule id

```text
<lesson_id>_rule_<4-digit-number>
```

Example:

```text
sersan_practice_09_revision_apolo_rule_0001
```

### 12.4 Translation id

```text
<lesson_id>_tr_<4-digit-number>
```

Example:

```text
sersan_practice_09_revision_apolo_tr_0001
```

## 13. Minimal validator checklist

Antes de aceptar un lesson pack, el Harness debe comprobar:

```text
[ ] Manifest exists.
[ ] Manifest JSON parses.
[ ] Manifest contract_version matches.
[ ] Sections JSONL parses line by line.
[ ] Sections have unique section_id.
[ ] Image CSV header is exact.
[ ] Image local paths exist or are justified.
[ ] Mechanical rules YAML parses.
[ ] Every rule has source anchor.
[ ] Translation CSV header is exact.
[ ] Every translation references an existing rule.
[ ] Quality report has all required headings.
[ ] run_manifest.json exists.
[ ] run_manifest declares project-resident toolchain hashes.
[ ] No generator/validator/prompt path points to C:\\Users, C:\\tmp or Downloads.
[ ] Acceptance decision is valid.
[ ] Cross-artifact counts match.
```

## 14. Pilot acceptance targets

Para los tres pilotos iniciales:

1. `practica_02_donchain.md`
2. `practica_09_revision_apolo.md`
3. `practica_15_revised.md`

Se aceptan `pass_with_warnings` o `needs_human_review` si las warnings estan
trazadas. No se exige `pass` en el primer piloto porque el objetivo es ajustar
el contrato.

Para el corpus completo:

```text
no se debe consolidar doctrina si hay lesson packs en fail.
```

## 15. Errors and severity

### 15.1 Blocking

- Missing required artifact.
- Invalid JSON/YAML/CSV.
- Rule without source anchor.
- Unread critical image.
- Unsupported promotion to `promoted`.
- AlphaEvolve translation without gate for high-risk rule.

### 15.2 Warning

- Missing non-critical image.
- Low confidence rule.
- Section type `unclear`.
- External reference not downloaded.
- Duplicate image reference.
- Translation marked `documentation_only`.

### 15.3 Info

- PDF duplicate ignored.
- Video out of scope.
- HTML layout ignored.
- Code artifact exists but not yet analyzed.

## 16. Relationship to future agents

Este contrato habilita agentes, pero no los implementa.

Agentes futuros:

- `sersan_corpus_inventory_agent`
- `lesson_pack_resolver_agent`
- `text_sectionizer_agent`
- `image_evidence_reader_agent`
- `mechanical_rule_extractor_agent`
- `tsis_translation_agent`
- `doctrine_reviewer_agent`
- `evaluator_mapping_agent`

Cada agente debe leer este contrato antes de producir outputs.

## 17. Relationship to TSIS doctrine

Los outputs de este contrato no son doctrina canonica.

Son candidatos trazables.

Camino de promocion:

```text
mechanical_rules.yaml
-> doctrine review
-> domain doctrine document
-> evaluator requirement
-> canonical project rule/policy/validator
```

## 18. Contract evolution

Si este contrato cambia:

- crear nueva version;
- no romper artefactos ya producidos sin migracion;
- documentar cambios;
- actualizar validadores;
- registrar en changelog si se promociona a regla operativa.

Version actual:

```text
sersan_lesson_pack_contract_v0_1
```

## 19. Decision v0.1

El siguiente paso operativo despues de este contrato es:

```text
crear el inventario completo del corpus SersanSistemas con lesson_pack_manifest
para todas las practicas revisadas
```

Despues:

```text
piloto de destilacion en practica_02, practica_09 y practica_15
```

No se debe lanzar destilacion completa del curso hasta que los tres pilotos
validen o ajusten este contrato.
