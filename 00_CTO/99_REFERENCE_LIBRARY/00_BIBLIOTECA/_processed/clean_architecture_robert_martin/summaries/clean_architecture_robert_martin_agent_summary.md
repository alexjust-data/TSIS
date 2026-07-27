# Clean Architecture

**book_id:** `clean_architecture_robert_martin`  
**Autor/Fuente:** Robert C. Martin  
**Tipo:** Libro EPUB  
**Fuente original:** `_OceanofPDF.com_Clean_Architecture_-_Robert_C_Marti.epub`  
**Estado:** `indexed`  
**Unidades extraidas:** 104 `epub_section`  
**Caracteres extraidos:** 530028  
**OCR/revision:** `False`

## Menu Rapido

- [Rol En TSIS](#rol-en-tsis)
- [Como Deben Usarlo Los Agentes](#como-deben-usarlo-los-agentes)
- [Secciones Resumidas](#secciones-resumidas)
- [Mapa TOC/Fuente Extraido](#mapa-tocfuente-extraido)
- [Componentes TSIS Afectados](#componentes-tsis-afectados)
- [Checklist Para Agentes](#checklist-para-agentes)

## Rol En TSIS

Define la disciplina conceptual: separar politica de negocio de detalles tecnicos y mantener dependencias hacia adentro.

**Utilidad principal:** fuente canonica para definir la regla de dependencias del core TSIS.

## Como Deben Usarlo Los Agentes

- TSIS debe proteger su politica central: clock/event loop, strategy contract, order lifecycle, portfolio/accounting y risk.
- DuckDB, Polars, Parquet, DAS, notebooks y UI son detalles; deben enchufarse por adaptadores.
- La arquitectura debe retrasar decisiones irreversibles y permitir tests del dominio sin infraestructura.
- El documento `TSIS_BACKTEST_ENGINE_ARCHITECTURE_V0_1` deberia declarar explicitamente sus boundaries.

## Secciones Resumidas

### SOLID Y Componentes

Principios de diseno, cohesion, acoplamiento y estabilidad.

**Encaje TSIS:** Component policy.

### Regla De Dependencias

Las dependencias del codigo deben apuntar hacia las reglas de negocio.

**Encaje TSIS:** Dependency boundary.

### Boundaries

Separar UI, DB, frameworks y dispositivos del nucleo.

**Encaje TSIS:** Adapters.

### Testing Y Arquitectura

Arquitectura que facilita reemplazar detalles por dobles de prueba.

**Encaje TSIS:** Test strategy.

### Aplicacion TSIS

Core de backtest independiente de infraestructura y broker.

**Encaje TSIS:** Core architecture.

## Mapa TOC/Fuente Extraido

| # | Titulo detectado | Unidad |
|---|---|---|
| 1 | Cover @page {padding: 0pt; margin:0pt} body { text-align: center; p... | 1 |
| 2 | About This E-Book About This E-Book EPUB is an open, industry-stand... | 2 |
| 3 | Clean Architecture OceanofPDF.com | 3 |
| 4 | Clean Architecture Clean Architecture A C RAFTSMAN’S G UIDE TO S OF... | 4 |
| 5 | Clean Architecture Many of the designations used by manufacturers a... | 5 |
| 6 | Clean Architecture This book is dedicated to my lovely wife, my fou... | 6 |
| 7 | Clean Architecture C ONTENTS Foreword Preface Acknowledgments About... | 7 |
| 8 | Clean Architecture F OREWORD What do we talk about when we talk abo... | 8 |
| 9 | Clean Architecture P REFACE The title of this book is Clean Archite... | 9 |
| 10 | Acknowledgments A CKNOWLEDGMENTS The people who played a part in th... | 10 |
| 11 | About the Author A BOUT THE A UTHOR Robert C. Martin (Uncle Bob) ha... | 11 |
| 12 | Clean Architecture I I NTRODUCTION It doesn’t take a huge amount of... | 12 |
| 13 | Chapter 1 What Is Design and Architecture? 1 W HAT I S D ESIGN AND ... | 13 |
| 14 | Clean Architecture 2 A T ALE OF T WO V ALUES Every software system ... | 14 |
| 15 | Clean Architecture II S TARTING WITH THE B RICKS : P ROGRAMMING P A... | 15 |
| 16 | Clean Architecture 3 P ARADIGM O VERVIEW The three paradigms includ... | 16 |
| 17 | Clean Architecture 4 S TRUCTURED P ROGRAMMING Edsger Wybe Dijkstra ... | 17 |
| 18 | Clean Architecture 5 O BJECT-ORIENTED P ROGRAMMING As we will see, ... | 18 |
| 19 | Clean Architecture 6 F UNCTIONAL P ROGRAMMING In many ways, the con... | 19 |
| 20 | Clean Architecture III D ESIGN P RINCIPLES Good software systems be... | 20 |
| 21 | Clean Architecture 7 SRP: T HE S INGLE R ESPONSIBILITY P RINCIPLE O... | 21 |
| 22 | Clean Architecture 8 OCP: T HE O PEN -C LOSED P RINCIPLE The Open-C... | 22 |
| 23 | Clean Architecture 9 LSP: T HE L ISKOV S UBSTITUTION P RINCIPLE In ... | 23 |
| 24 | Chapter 10 ISP: The Interface Segregation Principle 10 ISP: T HE I ... | 24 |
| 25 | Chapter 11 DIP: The Dependency Inversion Principle 11 DIP: T HE D E... | 25 |
| 26 | Clean Architecture IV C OMPONENT P RINCIPLES If the SOLID principle... | 26 |
| 27 | Chapter 12 Components 12 C OMPONENTS Components are the units of de... | 27 |
| 28 | Chapter 13 Component Cohesion 13 C OMPONENT C OHESION Which classes... | 28 |
| 29 | Chapter 14 Component Coupling 14 C OMPONENT C OUPLING The next thre... | 29 |
| 30 | Clean Architecture V A RCHITECTURE OceanofPDF.com | 30 |

Consultar el mapa completo en:

- `../index/clean_architecture_robert_martin_source_map.md`
- `../extracted/clean_architecture_robert_martin_toc.json`

## Componentes TSIS Afectados

- `Entities`, `UseCases`, `InterfaceAdapters`, `FrameworksDrivers`
- `BacktestEngineCore`, `BrokerAdapter`, `DataAdapter`
- `RunManifest`, `BoundaryTests`

## Checklist Para Agentes

- Abrir primero este resumen.
- Abrir despues `../index/clean_architecture_robert_martin_concept_index.md` para localizar conceptos.
- Abrir `../index/clean_architecture_robert_martin_source_map.md` antes del PDF/EPUB.
- Si se toma una decision de arquitectura, citar `book_id`, seccion y artefacto TSIS afectado.
- No copiar texto largo del libro; convertirlo en decision, contrato, test o tarea.
