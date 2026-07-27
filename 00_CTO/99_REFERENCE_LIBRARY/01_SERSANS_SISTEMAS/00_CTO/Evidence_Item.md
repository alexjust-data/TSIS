Tu planteamiento es correcto, pero haría un cambio estructural todavía más importante: introducir una unidad canónica anterior a `Topic` y `Asset`.

Los tres documentos actuales son demasiado cerrados. Obligan a seguir:

```text
Source → Practice → Topic → Asset → TSIS
```

Eso provocaría exactamente la pérdida que señalas. Un comentario experto, una forma de trabajar, una pregunta reveladora o una recomendación bibliográfica podrían no ser propiamente un Topic ni un Asset.

## La unidad que falta: Evidence Item

El flujo debería ser:

```text
Source
  ↓
Source Fragment
  ↓
Evidence Item
  ├─→ Topic
  ├─→ Asset
  ├─→ Practical Knowledge
  ├─→ External Reference
  ├─→ Question
  ├─→ Example / Case
  ├─→ Tool Observation
  ├─→ Open Finding
  └─→ Rejected
```

Un `Evidence Item` es cualquier unidad potencialmente valiosa extraída de una fuente y conservada con su contexto.

Ejemplo:

```yaml
evidence_id: EI-SERSAN-P02-0047
source:
  practice: 12-practice-02
  file: practica_02_donchain.md
  source_range: lines 1090-1104
  speaker: Sergi Sánchez
evidence_form: expert_judgment
content: >
  En caso de duda, no añadir el filtro, porque filtrar es una
  de las formas más sencillas de sobreoptimizar un sistema.
context:
  subject: market_regime_filters
  applies_to: strategy_research
epistemic_status: practitioner_judgment
extraction_status: captured
classification_status: provisional
possible_destinations:
  - Best Practice
  - Warning
  - TSIS validation protocol
```

Esto conserva el comentario aunque todavía no sepamos si terminará siendo:

* Una advertencia.
* Una buena práctica.
* Una regla metodológica.
* Una cita en el libro.
* Una decisión de TSIS.
* Simplemente evidencia histórica de cómo trabaja Sersan.

## Tres niveles que no deben confundirse

### 1. Evidencia

Lo que realmente aparece en la fuente:

```text
Qué dijo
Quién lo dijo
Dónde
En qué contexto
Qué imagen lo acompaña
```

No necesita tener todavía un destino.

### 2. Conocimiento interpretado

Lo que creemos que representa:

```text
Opinión experta
Heurística
Procedimiento
Ejemplo
Advertencia
Pregunta
Recomendación
Capacidad de una herramienta
```

La clasificación puede ser provisional y múltiple.

### 3. Materialización

Lo que decidimos construir a partir de ello:

```text
Asset
Engineering Decision
Task
Book Section
Reference Entry
Test
Checklist
Research Question
```

Solo en este tercer nivel debe exigirse un destino concreto.

## Qué sucedería con tus ejemplos

| Contenido encontrado          | Conservación primaria    | Posibles materializaciones                 |
| ----------------------------- | ------------------------ | ------------------------------------------ |
| Comentario sabio del profesor | `Expert Judgment`        | Principio, warning, libro, decisión        |
| Truco práctico                | `Practical Technique`    | Checklist, procedimiento, test             |
| Forma de trabajar del gestor  | `Practitioner Workflow`  | Workflow, componente, protocolo            |
| Libro recomendado             | `External Reference`     | Bibliografía, tarea de investigación       |
| Pregunta de un alumno         | `Question`               | FAQ, open question, misconception          |
| Respuesta del profesor        | `Expert Answer`          | Explicación, principio, evidencia          |
| Ejemplo concreto              | `Case / Example`         | Caso de estudio, test fixture              |
| Aplicación o plataforma       | `Tool Observation`       | Catálogo de herramientas, comparación      |
| Pantalla de TradeStation      | `Interface Evidence`     | Métricas, parámetros, capacidades          |
| Limitación de un software     | `Tool Limitation`        | Requisito TSIS, riesgo, decisión           |
| Forma de configurar algo      | `Configuration Practice` | Parámetro, procedimiento, preset           |
| Duda no resuelta              | `Open Finding`           | Tarea de investigación                     |
| Contradicción entre clases    | `Contradiction`          | Revisión, decisión, aclaración             |
| Anécdota de mercado           | `Practitioner Anecdote`  | Referencia hasta que pueda validarse       |
| Regla aproximada              | `Heuristic`              | Hipótesis o protocolo, no hecho científico |

Estas denominaciones son semillas descriptivas, no una lista cerrada.

## Matiz a tu regla sobre la repetición

Cambiaría:

```text
Lo repetido genera categorías nuevas.
```

por:

```text
La repetición es una señal para promover una categoría,
pero no es una condición obligatoria.
```

Porque un hallazgo puede aparecer una sola vez y ser crítico. Por ejemplo:

```text
Una regla de TradeStation introduce look-ahead.
```

Aunque solo aparezca una vez, debe conservarse y posiblemente generar inmediatamente un `Warning` y una investigación.

Una categoría nueva debería poder surgir por:

* Recurrencia.
* Alto valor.
* Riesgo crítico.
* Necesidad de recuperación posterior.
* Existencia de varios elementos con estructura común.
* Necesidad de gobernanza específica.

## Taxonomía facetada, no clasificación rígida

No obligaría a que cada elemento pertenezca exactamente a una categoría. Usaría varias facetas independientes:

```yaml
form:
  - statement
  - question
  - image
  - example
  - code
  - configuration

knowledge_nature:
  - fact
  - expert_judgment
  - heuristic
  - procedure
  - hypothesis
  - recommendation
  - anecdote

subject:
  - performance_evaluation
  - portfolio
  - filters
  - data_adjustment

possible_use:
  - book
  - TSIS
  - research
  - implementation
  - reference

validation:
  - source_confirmed
  - requires_external_validation
  - contradicted
  - unresolved
```

Así, una respuesta del profesor puede ser simultáneamente:

```text
form = answer
knowledge_nature = expert_judgment
subject = regime_filters
possible_use = validation_protocol
validation = requires_external_validation
```

No tenemos que deformarla para introducirla en una sola caja.

## Cómo evitamos entonces millones de notas

La apertura taxonómica no significa ausencia de control. El control se consigue con promoción y consolidación:

```text
Captured
↓
Anchored
↓
Interpreted
↓
Reviewed
├─ Rejected
├─ Reference
├─ Pending
├─ Consolidated
└─ Materialized
```

Reglas:

1. Todo lo capturado debe estar anclado a una fuente.
2. No todo lo capturado debe convertirse en conocimiento canónico.
3. Varios Evidence Items pueden consolidarse en un solo conocimiento.
4. Un Evidence Item puede alimentar varios destinos.
5. Los elementos dudosos permanecen como `Pending`, no se fuerzan.
6. Los elementos repetidos enriquecen el registro canónico existente.
7. Lo materializado mantiene trazabilidad hacia todas sus evidencias.

## documentos actuales

`knowledge_protocol.md`  
`extraction_protocol.md`  
`taxonomy.md`  



