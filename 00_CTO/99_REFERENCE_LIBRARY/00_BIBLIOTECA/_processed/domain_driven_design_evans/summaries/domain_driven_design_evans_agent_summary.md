# Domain-Driven Design

**book_id:** `domain_driven_design_evans`  
**Autor/Fuente:** Eric Evans  
**Tipo:** Libro PDF  
**Fuente original:** `_OceanofPDF.com_Domain-Driven_Design_-_Eric_Evans.pdf`  
**Estado:** `indexed`  
**Unidades extraidas:** 572 `page`  
**Caracteres extraidos:** 888663  
**OCR/revision:** `False`

## Menu Rapido

- [Rol En TSIS](#rol-en-tsis)
- [Como Deben Usarlo Los Agentes](#como-deben-usarlo-los-agentes)
- [Secciones Resumidas](#secciones-resumidas)
- [Mapa TOC/Fuente Extraido](#mapa-tocfuente-extraido)
- [Componentes TSIS Afectados](#componentes-tsis-afectados)
- [Checklist Para Agentes](#checklist-para-agentes)

## Rol En TSIS

Ayuda a construir un lenguaje ubicuo y boundaries estables para el motor.

**Utilidad principal:** base de modelado de dominio para Strategy, Order, Fill, Position, Portfolio, Ledger y bounded contexts TSIS.

## Como Deben Usarlo Los Agentes

- Antes de programar clases hay que fijar vocabulario: signal, decision, order, order event, fill, trade, position, snapshot no son sinonimos.
- Los agregados deben proteger invariantes: una posicion se actualiza por fills, no por una tabla de trades reconstruida tarde.
- Repositorios no son simples carpetas; son contratos de persistencia del modelo.
- Bounded contexts evitan mezclar research, backtesting, execution, data foundation y reporting.

## Secciones Resumidas

### Lenguaje Ubicuo

Vocabulario comun entre investigacion, backtest, ejecucion y reporting.

**Encaje TSIS:** TSIS glossary.

### Bloques Del Modelo

Entities, value objects, services, modules, aggregates, repositories y factories.

**Encaje TSIS:** Domain model.

### Invariantes

Proteccion de reglas internas del dominio mediante agregados.

**Encaje TSIS:** Order/Portfolio invariants.

### Bounded Contexts

Separacion de subdominios y mapas de contexto.

**Encaje TSIS:** Architecture map.

### Aplicacion TSIS

Contrato semantico historico/replay/live.

**Encaje TSIS:** Domain-driven backtester.

## Mapa TOC/Fuente Extraido

| # | Titulo detectado | Unidad |
|---|---|---|
| 1 | Domain-Driven Design: Tackling Complexity in the Heart of Software |  |
| 2 | Table of Contents |  |
| 3 | Copyright |  |
| 4 | Praise for Domain-Driven Design |  |
| 5 | Foreword |  |
| 6 | Preface |  |
| 7 | Contrasting Three Projects |  |
| 8 | The Challenge of Complexity |  |
| 9 | Design Versus Development Process |  |
| 10 | The Structure of This Book |  |
| 11 | Who Should Read This Book |  |
| 12 | A Domain-Driven Team |  |
| 13 | Acknowledgments |  |
| 14 | Part I: Putting the Domain Model to Work |  |
| 15 | Chapter One. Crunching Knowledge |  |
| 16 | Ingredients of Effective Modeling |  |
| 17 | Knowledge Crunching |  |
| 18 | Continuous Learning |  |
| 19 | Knowledge-Rich Design |  |
| 20 | Deep Models |  |
| 21 | Chapter Two. Communication and the Use of Language |  |
| 22 | Ubiquitous Language |  |
| 23 | Modeling Out Loud |  |
| 24 | One Team, One Language |  |
| 25 | Documents and Diagrams |  |
| 26 | Explanatory Models |  |
| 27 | Chapter Three. Binding Model and Implementation |  |
| 28 | Model-Driven Design |  |
| 29 | Modeling Paradigms and Tool Support |  |
| 30 | Letting the Bones Show: Why Models Matter to Users |  |

Consultar el mapa completo en:

- `../index/domain_driven_design_evans_source_map.md`
- `../extracted/domain_driven_design_evans_toc.json`

## Componentes TSIS Afectados

- `UbiquitousLanguage`, `BoundedContextMap`
- `OrderAggregate`, `PortfolioAggregate`, `StrategySpec`
- `DomainEvent`, `Repository`, `Factory`
- `DecisionLedger`, `TradeLedger`

## Checklist Para Agentes

- Abrir primero este resumen.
- Abrir despues `../index/domain_driven_design_evans_concept_index.md` para localizar conceptos.
- Abrir `../index/domain_driven_design_evans_source_map.md` antes del PDF/EPUB.
- Si se toma una decision de arquitectura, citar `book_id`, seccion y artefacto TSIS afectado.
- No copiar texto largo del libro; convertirlo en decision, contrato, test o tarea.
