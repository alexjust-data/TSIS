# Dataset Contract Template - Modulo 01

## 1. Rol del documento

Este documento define la plantilla minima para contratos de dataset del modulo:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps`

Su objetivo es asegurar que todos los dataset contracts relevantes compartan una estructura base coherente.

## 2. Principio rector

Un dataset institucional no debe describirse con texto libre desordenado.

Debe tener, como minimo:

- identidad;
- propietario;
- semantica;
- policy de consumo;
- trazabilidad;
- y limites conocidos.

## 3. Estructura minima obligatoria

Todo dataset contract institucional debe incluir, como minimo, las siguientes secciones.

### 3.1 dataset_identity

Debe responder:

- como se llama el dataset;
- a que dominio pertenece;
- cual es su version logica;
- y si sustituye o complementa otra identidad previa.

### 3.2 status

Debe incluir:

- promotion state;
- fecha de emision o version del contrato;
- owner responsable;
- y estado de vigencia.

### 3.3 purpose

Debe responder:

- para que existe el dataset;
- que necesidad del modulo cubre;
- y que no pretende cubrir.

### 3.4 semantic_scope

Debe fijar:

- que representa exactamente el dataset;
- unidad semantica principal;
- nivel temporal o estructural;
- y limites de interpretacion.

### 3.5 source_lineage

Debe documentar:

- fuente o fuentes upstream;
- procesos relevantes de transformacion;
- referencias a auditoria o certificacion;
- y dependencia de otros contracts o manifests.

### 3.6 schema

Debe definir o enlazar:

- schema canonico aplicable;
- claves principales;
- campos criticos;
- y supuestos estructurales relevantes.

### 3.7 coverage

Debe documentar, cuando aplique:

- horizonte temporal;
- cobertura de instrumentos;
- cobertura de archivos u objetos;
- y limitaciones cuantitativas relevantes.

### 3.8 quality_policy

Debe fijar:

- taxonomia de calidad aplicable;
- significado de los estados usados;
- bucketizacion relevante;
- y politica de interpretacion de residuos o excepciones.

### 3.9 allowed_consumers

Debe listar:

- consumidores permitidos;
- consumidores restringidos;
- y consumidores prohibidos.

Debe enlazar con `consumer_classes.md` y con las `data_consumption_policies/` vigentes.

### 3.10 validators

Debe declarar:

- validators requeridos;
- checks estructurales;
- checks semanticos;
- y criterio minimo de aprobacion.

### 3.11 known_limitations

Debe documentar:

- riesgos conocidos;
- limitaciones de coverage;
- condicionantes de interpretacion;
- y buckets residuales relevantes.

### 3.12 change_policy

Debe fijar:

- que cambios requieren nueva version logica;
- que cambios son compatibles;
- y que cambios disparan revisiones downstream.

## 4. Plantilla base sugerida

```yaml
dataset_identity:
  name:
  domain:
  logical_version:
  supersedes:

status:
  promotion_state:
  contract_version:
  owner:
  active:

purpose:
  summary:
  intended_role:
  out_of_scope:

semantic_scope:
  representation:
  primary_unit:
  temporal_level:
  interpretation_limits:

source_lineage:
  upstream_sources: []
  transformation_summary:
  audit_references: []
  certification_references: []
  dependencies: []

schema:
  canonical_schema:
  primary_keys: []
  critical_fields: []
  structural_assumptions: []

coverage:
  time_range:
  instrument_scope:
  object_scope:
  quantitative_limits: []

quality_policy:
  taxonomy:
  state_meanings: {}
  bucket_rules: []
  residual_handling:

allowed_consumers:
  permitted: []
  restricted: []
  prohibited: []

validators:
  required: []
  structural_checks: []
  semantic_checks: []
  pass_criteria:

known_limitations:
  risks: []
  coverage_gaps: []
  interpretation_caveats: []
  residual_buckets: []

change_policy:
  version_bump_rules: []
  compatible_changes: []
  downstream_review_triggers: []
```

## 5. Reglas de uso

Esta plantilla no obliga a que todos los datasets tengan exactamente el mismo detalle cuantitativo.

Si obliga a que todos los dataset contracts respondan la misma clase de preguntas institucionales.

## 6. Relacion con auditoria y certificacion

Cuando el dataset proceda de trabajo ya auditado o certificado, el contract debe:

- enlazar la evidencia existente;
- no duplicar innecesariamente closeouts completos;
- y encapsular las conclusiones estables con forma consumible.

## 7. Regla final

Si un dataset no puede rellenar esta plantilla de forma coherente, todavia no esta listo para promocion institucional completa.
