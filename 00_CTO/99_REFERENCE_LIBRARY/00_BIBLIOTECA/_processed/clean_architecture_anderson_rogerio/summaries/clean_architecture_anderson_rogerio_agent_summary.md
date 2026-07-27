# Clean Architecture

**book_id:** `clean_architecture_anderson_rogerio`  
**Autor/Fuente:** Rogerio Anderson  
**Tipo:** Libro PDF  
**Fuente original:** `_OceanofPDF.com_Clean_Architecture_-_Anderson_Rogerio.pdf`  
**Estado:** `needs_ocr`  
**Unidades extraidas:** 157 `page`  
**Caracteres extraidos:** 15  
**OCR/revision:** `True`

## Menu Rapido

- [Rol En TSIS](#rol-en-tsis)
- [Como Deben Usarlo Los Agentes](#como-deben-usarlo-los-agentes)
- [Secciones Resumidas](#secciones-resumidas)
- [Mapa TOC/Fuente Extraido](#mapa-tocfuente-extraido)
- [Componentes TSIS Afectados](#componentes-tsis-afectados)
- [Checklist Para Agentes](#checklist-para-agentes)

## Rol En TSIS

Referencia de arquitectura limpia para mantener el core de backtesting independiente de datos, broker, UI y almacenamiento.

**Utilidad principal:** refuerzo pragmatico para separar dominio TSIS de infraestructura y frameworks.

## Como Deben Usarlo Los Agentes

- El dominio del backtester no debe depender de DuckDB, Polars, Polygon, DAS ni formatos fisicos.
- Los casos de uso coordinan componentes; las entidades contienen reglas estables del dominio.
- Las dependencias deben apuntar hacia el dominio, con adaptadores en los bordes.
- Los tests del core deben ejecutarse con fakes/in-memory sin requerir datos reales masivos.

## Secciones Resumidas

### Capas Y Dependencias

Separacion de entidades, casos de uso, interfaces y frameworks.

**Encaje TSIS:** Core boundaries.

### SOLID En Practica

Principios para modularidad, testabilidad y bajo acoplamiento.

**Encaje TSIS:** Component contracts.

### Adaptadores

Puertos para datos, broker, persistence y UI.

**Encaje TSIS:** Adapters.

### Testing

Core testable por contratos, fakes y casos de uso.

**Encaje TSIS:** Acceptance/unit tests.

### Aplicacion TSIS

Backtest engine como nucleo limpio con adaptadores Polygon/DAS/Parquet.

**Encaje TSIS:** Clean TSIS architecture.

## Mapa TOC/Fuente Extraido

| # | Titulo detectado | Unidad |
|---|---|---|
| - | No se pudo extraer TOC estructurado; usar source_map y stats. | - |

Consultar el mapa completo en:

- `../index/clean_architecture_anderson_rogerio_source_map.md`
- `../extracted/clean_architecture_anderson_rogerio_toc.json`

## Componentes TSIS Afectados

- `DomainCore`, `UseCaseService`, `Port`, `Adapter`
- `BacktestRunUseCase`, `OrderExecutionPort`
- `MarketDataPort`, `LedgerRepository`
- `DependencyInversionBoundary`

## Checklist Para Agentes

- Abrir primero este resumen.
- Abrir despues `../index/clean_architecture_anderson_rogerio_concept_index.md` para localizar conceptos.
- Abrir `../index/clean_architecture_anderson_rogerio_source_map.md` antes del PDF/EPUB.
- Si se toma una decision de arquitectura, citar `book_id`, seccion y artefacto TSIS afectado.
- No copiar texto largo del libro; convertirlo en decision, contrato, test o tarea.

## Aviso OCR

Este PDF no tiene una capa de texto util. Los artefactos actuales sirven como marcador bibliografico y orientacion TSIS, pero no como resumen validado desde el contenido interno. Requiere OCR antes de usarlo como fuente primaria.
