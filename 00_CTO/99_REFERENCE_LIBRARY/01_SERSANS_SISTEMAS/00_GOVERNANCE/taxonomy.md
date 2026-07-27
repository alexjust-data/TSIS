# Taxonomy v0.2

## 1. Propósito

Definir un lenguaje inicial para organizar el conocimiento extraído de SersanSistemas sin limitar de antemano lo que puede descubrirse.

Esta taxonomía es:

```text
Abierta
Evolutiva
Versionada
Facetada
No exhaustiva
No obligatoriamente exclusiva
```

Las categorías incluidas son semillas. No constituyen una lista cerrada.

## 2. Entidades principales

### 2.1 Source

Unidad original de procedencia.

Ejemplos:

- práctica;
- vídeo;
- transcripción;
- Markdown;
- imagen;
- código;
- documento;
- libro;
- paper;
- documentación de una aplicación.

### 2.2 Source Fragment

Porción localizable de una Source.

Ejemplos:

- líneas 320–345;
- imagen `038.png`;
- región de una captura;
- bloque de código;
- pregunta y respuesta;
- secuencia de una demostración.

### 2.3 Evidence Item

Unidad canónica de captura. Conserva algo potencialmente valioso observado en un Source Fragment.

No necesita:

- pertenecer inmediatamente a un Topic;
- convertirse en Asset;
- tener clasificación definitiva;
- tener destino TSIS.

Sí necesita:

- anclaje;
- contenido identificable;
- contexto suficiente;
- separación entre evidencia e interpretación.

### 2.4 Topic

Dominio de aprendizaje descubierto a partir de las fuentes.

Ejemplos iniciales:

```text
Continuous Charts
Donchian
Performance Evaluation
Regimes
Walk Forward
Portfolio Backtesting
Multidata Alignment
```

Un Topic:

- puede abarcar varias prácticas;
- puede relacionarse con otros Topics;
- puede evolucionar;
- no es necesariamente un capítulo;
- no es un contenedor obligatorio de toda evidencia.

### 2.5 Knowledge Record

Representación consolidada e interpretada de conocimiento apoyado por uno o más Evidence Items.

Puede contener:

- definición canónica;
- alcance;
- condiciones;
- excepciones;
- evidencias favorables;
- evidencias contradictorias;
- validación;
- relaciones;
- posibles destinos.

### 2.6 Asset

Materialización reutilizable de conocimiento.

Un Asset existe para ser consultado, aplicado, implementado, probado o reutilizado.

### 2.7 External Reference

Referencia a una fuente externa mencionada o recomendada.

Ejemplos:

- libro;
- paper;
- autor;
- documentación;
- aplicación;
- página web;
- curso;
- librería software.

Una mención no implica validación ni aprobación.

### 2.8 Open Finding

Hallazgo que debe preservarse, pero no puede todavía resolverse o clasificarse adecuadamente.

Ejemplos:

- nombre mal transcrito;
- contradicción;
- afirmación pendiente de comprobar;
- imagen huérfana;
- relación incierta;
- posible categoría emergente.

### 2.9 Materialization

Resultado producido a partir de conocimiento consolidado.

Ejemplos:

- Asset;
- decisión;
- tarea;
- prueba;
- checklist;
- procedimiento;
- entrada del libro;
- investigación pendiente.

## 3. Facetas de clasificación

Las facetas son independientes. Un elemento puede recibir varios valores cuando esté justificado.

### 3.1 Form

Describe la forma observable del contenido.

```text
Statement
Question
Answer
Definition
Explanation
Example
Counterexample
Demonstration
Code
Formula
Table
Chart
Screenshot
Configuration
Procedure
Recommendation
Reference
Narrative
Unknown
```

### 3.2 Knowledge Nature

Describe la naturaleza epistemológica.

```text
Observed Fact
Technical Fact
Definition
Convention
Formula
Expert Judgment
Practitioner Experience
Heuristic
Hypothesis
Opinion
Recommendation
Warning
Best Practice
Limitation
Assumption
Research Claim
Unresolved Claim
Unknown
```

### 3.3 Functional Role

Describe para qué podría servir.

```text
Explanation
Design Input
Implementation Input
Validation Input
Risk Control
Operational Guidance
Pedagogical Example
Benchmark
Testing Fixture
Book Content
External Research
Reference Only
Unknown
```

### 3.4 Subject

Describe de qué trata.

Los Subjects no se cierran en esta versión. Se crean y consolidan durante el descubrimiento de Topics.

### 3.5 Validation Status

```text
Unreviewed
Source Confirmed
Internally Consistent
Requires External Validation
Externally Supported
Empirically Tested
Contradicted
Context Dependent
Unresolved
Rejected
```

### 3.6 Confidence

```text
Unknown
Low
Medium
High
```

La confianza expresa el estado de la interpretación, no la autoridad absoluta de la fuente.

### 3.7 Possible Use

```text
Topic Organization
Knowledge Consolidation
Asset Candidate
TSIS Proposal
TSIS Decision Candidate
Implementation Task
Test Candidate
Book View
Bibliography
Research Queue
Reference Only
No Current Use
```

## 4. Formas semilla de conocimiento práctico

Estas formas existen para impedir que el proyecto pierda conocimiento que no parece inicialmente un Asset:

```text
Expert Commentary
Expert Judgment
Practical Trick
Heuristic
Practitioner Workflow
Decision Pattern
Operational Procedure
Configuration Practice
Failure Mode
Common Mistake
Student Question
Expert Answer
Misconception
Concrete Example
Case Study
Counterexample
Tool Observation
Tool Capability
Tool Limitation
Tool Comparison
External Recommendation
Open Question
Contradiction
Anecdote
```

Son categorías semilla y pueden fusionarse, dividirse o sustituirse.

## 5. Categorías semilla de Asset

```text
Metric
Algorithm
Indicator
Pattern
Parameter
Component
Class
Interface Contract
Data Contract
UI Capability
Report
Decision
Warning
Best Practice
Procedure
Workflow
Checklist
Task
Test
Benchmark
Reference Entry
```

No todo elemento de estas categorías debe materializarse como archivo independiente.

## 6. Relaciones iniciales

```text
source HAS_FRAGMENT source_fragment
source_fragment SUPPORTS evidence_item
evidence_item SPOKEN_BY person
evidence_item DEPICTS tool_or_concept
evidence_item RELATES_TO topic
evidence_item SUPPORTS knowledge_record
evidence_item CONTRADICTS knowledge_record
evidence_item CLARIFIES evidence_item
question ANSWERED_BY answer
knowledge_record CONSOLIDATES evidence_item
knowledge_record RELATES_TO topic
knowledge_record PRODUCES materialization
knowledge_record REFERENCES external_reference
asset SUPPORTED_BY knowledge_record
asset MAPS_TO tsis_module
asset MOTIVATES engineering_decision
engineering_decision CREATES implementation_task
book_section DERIVES_FROM knowledge_record
```

Las relaciones también son evolutivas.

## 7. Regla para categorías nuevas

Una categoría nueva puede proponerse cuando:

- aparecen varios elementos con la misma estructura;
- una categoría existente pierde información relevante;
- un hallazgo singular tiene alto valor o riesgo;
- se necesita una política de validación diferente;
- se necesita recuperar esos elementos como conjunto;
- aparece una materialización no representada.

Toda propuesta debe registrar:

```yaml
proposed_category:
definition:
why_needed:
examples:
overlap_with_existing:
proposed_action:
status:
```

Estados:

```text
Proposed
Under Review
Admitted
Merged
Rejected
Deprecated
```

## 8. Regla de no forzado

Si un elemento no encaja:

```text
No se descarta.
No se deforma.
No se clasifica por aproximación silenciosa.
```

Se conserva como:

```text
classification: Unknown
review_status: Pending Review
```

Puede además generar un `Open Finding` o una propuesta de categoría.

## 9. Regla de rareza

Una evidencia no necesita repetirse para ser valiosa.

La recurrencia aumenta la probabilidad de consolidación, pero un elemento singular puede promoverse por:

- riesgo crítico;
- poder explicativo;
- impacto arquitectónico;
- utilidad práctica;
- capacidad para generar una prueba;
- contradicción relevante.

## 10. Regla de granularidad

La taxonomía clasifica registros, no obliga a crear un archivo por registro.

Se preferirán:

- registros estructurados;
- catálogos consolidados;
- relaciones;
- vistas generadas;

frente a miles de documentos Markdown aislados.

## 11. Gobierno de versiones

Toda modificación de la taxonomía debe registrar:

- versión;
- fecha;
- categorías añadidas;
- categorías fusionadas;
- categorías deprecadas;
- motivo;
- impacto sobre registros existentes;
- necesidad o no de migración.

Una categoría deprecada no elimina la evidencia histórica asociada.

