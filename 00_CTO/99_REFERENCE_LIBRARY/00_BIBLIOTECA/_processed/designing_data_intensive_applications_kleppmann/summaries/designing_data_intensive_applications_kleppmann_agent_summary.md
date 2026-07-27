# Designing Data-Intensive Applications

**book_id:** `designing_data_intensive_applications_kleppmann`  
**Autor/Fuente:** Martin Kleppmann  
**Tipo:** Libro PDF  
**Fuente original:** `Martin-Kleppmann---Designing-Data-Intensive-Applications_-O’Reilly-Media-(2017).pdf`  
**Estado:** `indexed`  
**Unidades extraidas:** 491 `page`  
**Caracteres extraidos:** 1129830  
**OCR/revision:** `False`

## Menu Rapido

- [Rol En TSIS](#rol-en-tsis)
- [Como Deben Usarlo Los Agentes](#como-deben-usarlo-los-agentes)
- [Secciones Resumidas](#secciones-resumidas)
- [Mapa TOC/Fuente Extraido](#mapa-tocfuente-extraido)
- [Componentes TSIS Afectados](#componentes-tsis-afectados)
- [Checklist Para Agentes](#checklist-para-agentes)

## Rol En TSIS

Fuente clave para pensar TSIS como sistema de datos: logs, estado, streams, storage, consistency y evolucion.

**Utilidad principal:** base de arquitectura de datos para datasets, ledgers, replay, event logs y evolucion de esquemas TSIS.

## Como Deben Usarlo Los Agentes

- Los ledgers del backtester son logs de eventos que permiten reconstruir estado, auditar decisiones y hacer replay.
- La evolucion de esquemas debe tratarse como contrato de largo plazo, no como columnas sueltas.
- Replicacion, particionado y transacciones importan si TSIS escala a pipelines concurrentes.
- Conecta directamente con Streaming Systems y Database Internals para semantica de datos historico/online.

## Secciones Resumidas

### Fundamentos De Sistemas De Datos

Fiabilidad, escalabilidad, mantenibilidad y modelos de datos.

**Encaje TSIS:** Data architecture.

### Storage E Indices

Como se guardan y consultan datos persistentes.

**Encaje TSIS:** Ledger/storage.

### Replicacion, Particionado Y Transacciones

Consistencia, concurrencia y fallos.

**Encaje TSIS:** Pipeline reliability.

### Batch Y Streaming

Datos derivados, event logs y procesamiento continuo.

**Encaje TSIS:** Replay/online semantics.

### Aplicacion TSIS

Ledgers reproducibles y arquitectura historico/live.

**Encaje TSIS:** TSIS data platform.

## Mapa TOC/Fuente Extraido

| # | Titulo detectado | Unidad |
|---|---|---|
| 1 | Cover |  |
| 2 | Copyright |  |
| 3 | Table of Contents |  |
| 4 | About this Book |  |
| 5 | Who Should Read this Book? |  |
| 6 | Scope of this Book |  |
| 7 | Outline of this Book |  |
| 8 | Early Release Status and Feedback |  |
| 9 | Part I. Foundations of Data Systems |  |
| 10 | Chapter 1. Reliable, Scalable and Maintainable Applications |  |
| 11 | Thinking About Data Systems |  |
| 12 | Reliability |  |
| 13 | Hardware faults |  |
| 14 | Software errors |  |
| 15 | Human errors |  |
| 16 | How important is reliability? |  |
| 17 | Scalability |  |
| 18 | Describing load |  |
| 19 | Describing performance |  |
| 20 | Approaches for coping with load |  |
| 21 | Maintainability |  |
| 22 | Operability: making life easy for operations |  |
| 23 | Simplicity: managing complexity |  |
| 24 | Evolvability: making change easy |  |
| 25 | Summary |  |
| 26 | Chapter 2. Data Models and Query Languages |  |
| 27 | Relational Model vs. Document Model |  |
| 28 | The birth of NoSQL |  |
| 29 | The object-relational mismatch |  |
| 30 | Many-to-one and many-to-many relationships |  |

Consultar el mapa completo en:

- `../index/designing_data_intensive_applications_kleppmann_source_map.md`
- `../extracted/designing_data_intensive_applications_kleppmann_toc.json`

## Componentes TSIS Afectados

- `EventLog`, `Ledger`, `StateRebuilder`
- `SchemaVersioning`, `DataContract`, `MigrationPlan`
- `BatchPipeline`, `StreamPipeline`, `ReplaySemantics`
- `ConsistencyPolicy`, `IdempotencyKey`

## Checklist Para Agentes

- Abrir primero este resumen.
- Abrir despues `../index/designing_data_intensive_applications_kleppmann_concept_index.md` para localizar conceptos.
- Abrir `../index/designing_data_intensive_applications_kleppmann_source_map.md` antes del PDF/EPUB.
- Si se toma una decision de arquitectura, citar `book_id`, seccion y artefacto TSIS afectado.
- No copiar texto largo del libro; convertirlo en decision, contrato, test o tarea.
