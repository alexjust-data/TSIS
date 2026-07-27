# Clean Architectures in Python

**book_id:** `clean_architectures_python_giordani`  
**Autor/Fuente:** Leonardo Giordani  
**Tipo:** Libro PDF  
**Fuente original:** `_OceanofPDF.com_Clean_Architectures_in_Python_-_Leonardo_Giordani.pdf`  
**Estado:** `indexed`  
**Unidades extraidas:** 200 `page`  
**Caracteres extraidos:** 205873  
**OCR/revision:** `False`

## Menu Rapido

- [Rol En TSIS](#rol-en-tsis)
- [Como Deben Usarlo Los Agentes](#como-deben-usarlo-los-agentes)
- [Secciones Resumidas](#secciones-resumidas)
- [Mapa TOC/Fuente Extraido](#mapa-tocfuente-extraido)
- [Componentes TSIS Afectados](#componentes-tsis-afectados)
- [Checklist Para Agentes](#checklist-para-agentes)

## Rol En TSIS

Aterriza arquitectura limpia en Python con entidades, casos de uso, repositorios y tests.

**Utilidad principal:** puente directo para implementar Clean Architecture en el backtester propio Python.

## Como Deben Usarlo Los Agentes

- El core Python debe expresar entidades de dominio simples y casos de uso testeables.
- Repositorios y adapters deben esconder Parquet/DuckDB/Polars al dominio.
- La estructura de carpetas de TSIS_BACKTEST_ENGINE puede basarse en domain/application/adapters/infrastructure.
- Usar fixtures y repositorios in-memory para golden tests de ordenes/fills/portfolio.

## Secciones Resumidas

### Dominio Python

Entidades, value objects y errores de dominio.

**Encaje TSIS:** Domain model.

### Casos De Uso

Interactors y coordinacion de reglas sin framework.

**Encaje TSIS:** Application services.

### Repositorios

Puertos de persistence con implementaciones intercambiables.

**Encaje TSIS:** Repository pattern.

### Testing

Tests unitarios y de integracion sobre casos de uso.

**Encaje TSIS:** TDD core.

### Aplicacion TSIS

Plantilla de carpetas y contratos para Camino B.

**Encaje TSIS:** Python implementation.

## Mapa TOC/Fuente Extraido

| # | Titulo detectado | Unidad |
|---|---|---|
| 1 | Clean Architectures in Python |  |
| 2 | Table of Contents |  |
| 3 | Dedication |  |
| 4 | Introduction |  |
| 5 | What is a software architecture? |  |
| 6 | Why is it called "clean"? |  |
| 7 | Why "architectures"? |  |
| 8 | Why Python? |  |
| 9 | Acknowledgments |  |
| 10 | About the book |  |
| 11 | Prerequisites and structure of the book |  |
| 12 | Typographic conventions |  |
| 13 | Why this book comes for free |  |
| 14 | Submitting issues or patches |  |
| 15 | About the author |  |
| 16 | Changes in the second edition |  |
| 17 | Chapter 1. A day in the life of a clean system |  |
| 18 | 1.1. The data flow |  |
| 19 | 1.2. Advantages of a layered architecture |  |
| 20 | Chapter 2. Components of a clean architecture |  |
| 21 | 2.1. Divide et impera |  |
| 22 | 2.2. Data types |  |
| 23 | 2.3. The main four layers |  |
| 24 | 2.4. Communication between layers |  |
| 25 | 2.5. APIs and shades of grey |  |
| 26 | Chapter 3. A basic example |  |
| 27 | 3.1. Project setup |  |
| 28 | 3.2. Domain models |  |
| 29 | 3.3. Serializers |  |
| 30 | 3.4. Use cases |  |

Consultar el mapa completo en:

- `../index/clean_architectures_python_giordani_source_map.md`
- `../extracted/clean_architectures_python_giordani_toc.json`

## Componentes TSIS Afectados

- `domain/`, `application/`, `adapters/`, `infrastructure/`
- `RepositoryPort`, `InMemoryRepository`, `ParquetRepository`
- `UseCaseRequest`, `UseCaseResponse`, `DependencyProvider`

## Checklist Para Agentes

- Abrir primero este resumen.
- Abrir despues `../index/clean_architectures_python_giordani_concept_index.md` para localizar conceptos.
- Abrir `../index/clean_architectures_python_giordani_source_map.md` antes del PDF/EPUB.
- Si se toma una decision de arquitectura, citar `book_id`, seccion y artefacto TSIS afectado.
- No copiar texto largo del libro; convertirlo en decision, contrato, test o tarea.
