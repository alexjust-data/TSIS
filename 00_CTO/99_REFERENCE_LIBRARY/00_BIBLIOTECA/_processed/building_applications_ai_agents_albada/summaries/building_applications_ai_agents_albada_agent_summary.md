# Building Applications with AI Agents

**book_id:** `building_applications_ai_agents_albada`  
**Autor/Fuente:** Michael Albada  
**Tipo:** Libro PDF  
**Fuente original:** `_OceanofPDF.com_Building_Applications_with_AI_Agents_-_Michael_Albada.pdf`  
**Estado:** `indexed`  
**Unidades extraidas:** 253 `page`  
**Caracteres extraidos:** 303646  
**OCR/revision:** `False`

## Menu Rapido

- [Rol En TSIS](#rol-en-tsis)
- [Como Deben Usarlo Los Agentes](#como-deben-usarlo-los-agentes)
- [Secciones Resumidas](#secciones-resumidas)
- [Mapa TOC/Fuente Extraido](#mapa-tocfuente-extraido)
- [Componentes TSIS Afectados](#componentes-tsis-afectados)
- [Checklist Para Agentes](#checklist-para-agentes)

## Rol En TSIS

Fuente de diseno para convertir agentes en operadores de conocimiento y no solo generadores de texto.

**Utilidad principal:** patrones para agentes que consultan biblioteca, graphify, knowledge assets y tareas TSIS.

## Como Deben Usarlo Los Agentes

- Separar rol del agente, herramientas disponibles, memoria/contexto, criterios de salida y auditoria de acciones.
- Usar evaluaciones y trazabilidad para saber si un agente encontro la fuente correcta antes de tomar decisiones de arquitectura.
- No mezclar RAG, planificacion y ejecucion: cada agente debe tener contratos de entrada/salida y permisos claros.
- Aplicable a la biblioteca TSIS: los agentes deben consultar indices, source maps y graphify antes de abrir PDFs completos.

## Secciones Resumidas

### Arquitectura De Agentes

Roles, ciclos de razonamiento, herramientas, memoria y coordinacion.

**Encaje TSIS:** AgentWorkflowProtocol.

### RAG Y Fuentes

Recuperacion aumentada, chunking, referencias y grounded answers.

**Encaje TSIS:** ReferenceLibrary, Graphify.

### Multiagente

Division de responsabilidades, handoffs y supervision.

**Encaje TSIS:** AgentOrchestrator.

### Evaluacion Y Guardrails

Comprobaciones de calidad, seguridad, errores y observabilidad.

**Encaje TSIS:** AgentEvaluationHarness.

### Aplicacion TSIS

Patron para agentes que leen libros, curso Sersan y artefactos de backtesting.

**Encaje TSIS:** KnowledgeEngineeringOps.

## Mapa TOC/Fuente Extraido

| # | Titulo detectado | Unidad |
|---|---|---|
| 1 | Brief Table of Contents (Not Yet Final) |  |
| 2 | 1. Introduction to Agents |  |
| 3 | What are Agents? |  |
| 4 | Similarities and Differences from Traditional Machine Learning |  |
| 5 | Recent Advancements |  |
| 6 | From Synchronous to Asynchronous |  |
| 7 | When Are Agents Useful? |  |
| 8 | Managing Expectations |  |
| 9 | Use Cases for Agents |  |
| 10 | Customer Support Agent |  |
| 11 | Personal Assistant Agent |  |
| 12 | Legal Agent |  |
| 13 | Advertising Agent |  |
| 14 | Building with Change in Mind |  |
| 15 | Scalability |  |
| 16 | Modularity |  |
| 17 | Continuous Learning |  |
| 18 | Resilience |  |
| 19 | Future-Proofing |  |
| 20 | Towards Multi-Agent Systems |  |
| 21 | Foundation Models and Autonomous Agents |  |
| 22 | Conclusion |  |
| 23 | 2. Overview of Designing Agent Systems |  |
| 24 | Scenario Selection and Task Definition |  |
| 25 | Defining the Problem: Scoping Tasks for Agents |  |
| 26 | Avoiding Common Pitfalls in Task Definition |  |
| 27 | Great Example Scenarios |  |
| 28 | Core Components of Agent Systems |  |
| 29 | Model Selection |  |
| 30 | Skills |  |

Consultar el mapa completo en:

- `../index/building_applications_ai_agents_albada_source_map.md`
- `../extracted/building_applications_ai_agents_albada_toc.json`

## Componentes TSIS Afectados

- `AgentWorkflowProtocol`, `KnowledgeRetrievalAgent`
- `ToolUsePolicy`, `EvidenceLedger`
- `GraphifyQueryWorkflow`, `KnowledgeGovernance`
- `AgentEvaluationHarness`

## Checklist Para Agentes

- Abrir primero este resumen.
- Abrir despues `../index/building_applications_ai_agents_albada_concept_index.md` para localizar conceptos.
- Abrir `../index/building_applications_ai_agents_albada_source_map.md` antes del PDF/EPUB.
- Si se toma una decision de arquitectura, citar `book_id`, seccion y artefacto TSIS afectado.
- No copiar texto largo del libro; convertirlo en decision, contrato, test o tarea.
