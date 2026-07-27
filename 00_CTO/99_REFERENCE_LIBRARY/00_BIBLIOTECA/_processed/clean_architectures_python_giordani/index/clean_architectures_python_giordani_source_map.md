# Source Map - Clean Architectures in Python

**book_id:** `clean_architectures_python_giordani`  
**Fuente original:** `_OceanofPDF.com_Clean_Architectures_in_Python_-_Leonardo_Giordani.pdf`  
**Tipo de unidad:** `page`  
**Unidades:** 200  

## Mapa Estructural Extraido

| # | Nivel | Titulo/descripcion | Unidad |
|---|---|---|---|
| 1 | 0 | Clean Architectures in Python |  |
| 2 | 0 | Table of Contents |  |
| 3 | 0 | Dedication |  |
| 4 | 0 | Introduction |  |
| 5 | 1 | What is a software architecture? |  |
| 6 | 1 | Why is it called "clean"? |  |
| 7 | 1 | Why "architectures"? |  |
| 8 | 1 | Why Python? |  |
| 9 | 1 | Acknowledgments |  |
| 10 | 0 | About the book |  |
| 11 | 1 | Prerequisites and structure of the book |  |
| 12 | 1 | Typographic conventions |  |
| 13 | 1 | Why this book comes for free |  |
| 14 | 1 | Submitting issues or patches |  |
| 15 | 1 | About the author |  |
| 16 | 1 | Changes in the second edition |  |
| 17 | 0 | Chapter 1. A day in the life of a clean system |  |
| 18 | 1 | 1.1. The data flow |  |
| 19 | 1 | 1.2. Advantages of a layered architecture |  |
| 20 | 0 | Chapter 2. Components of a clean architecture |  |
| 21 | 1 | 2.1. Divide et impera |  |
| 22 | 1 | 2.2. Data types |  |
| 23 | 1 | 2.3. The main four layers |  |
| 24 | 1 | 2.4. Communication between layers |  |
| 25 | 1 | 2.5. APIs and shades of grey |  |
| 26 | 0 | Chapter 3. A basic example |  |
| 27 | 1 | 3.1. Project setup |  |
| 28 | 1 | 3.2. Domain models |  |
| 29 | 1 | 3.3. Serializers |  |
| 30 | 1 | 3.4. Use cases |  |
| 31 | 1 | 3.5. The storage system |  |
| 32 | 1 | 3.6. A command-line interface |  |
| 33 | 1 | 3.7. Conclusions |  |
| 34 | 0 | Chapter 4. Add a Web application |  |
| 35 | 1 | 4.1. Flask setup |  |
| 36 | 1 | 4.2. Test and create an HTTP endpoint |  |
| 37 | 1 | 4.3. WSGI |  |
| 38 | 1 | 4.4. Conclusions |  |
| 39 | 0 | Chapter 5. Error management |  |
| 40 | 1 | 5.1. Request and responses |  |
| 41 | 1 | 5.2. Basic structure |  |
| 42 | 1 | 5.3. Requests and responses in a use case |  |
| 43 | 1 | 5.4. Request validation |  |
| 44 | 1 | 5.5. Responses and failures |  |
| 45 | 1 | 5.6. Error management in a use case |  |
| 46 | 1 | 5.7. Integrating external systems |  |
| 47 | 1 | 5.8. Conclusions |  |
| 48 | 0 | Chapter 6. Integration with a real external system - PostgreSQL |  |
| 49 | 1 | 6.1. Decoupling with interfaces |  |
| 50 | 1 | 6.2. A repository based on PostgreSQL |  |
| 51 | 1 | 6.3. Label integration tests |  |
| 52 | 1 | 6.4. Create SQLAlchemy classes |  |
| 53 | 1 | 6.5. Orchestration management |  |
| 54 | 1 | 6.6. Database fixtures |  |
| 55 | 1 | 6.7. Integration tests |  |
| 56 | 1 | 6.8. Conclusions |  |
| 57 | 0 | Chapter 7. Integration with a real external system - MongoDB |  |
| 58 | 1 | 7.1. Fixtures |  |
| 59 | 1 | 7.2. Docker Compose configuration |  |
| 60 | 1 | 7.3. Application configuration |  |
| 61 | 1 | 7.4. Integration tests |  |
| 62 | 1 | 7.5. The MongoDB repository |  |
| 63 | 1 | 7.6. Conclusions |  |
| 64 | 0 | Chapter 8. Run a production-ready system |  |
| 65 | 1 | 8.1. Build a web stack |  |
| 66 | 1 | 8.2. Connect to a production-ready database |  |
| 67 | 1 | 8.3. Conclusions |  |
| 68 | 0 | Appendix A: Changelog |  |
| 69 | 0 | Postface |  |

## Crosswalk TSIS

| Extraer | Encaja en TSIS | Secciones/Unidades | Prioridad |
|---|---|---|---|
| Python clean architecture layout | `domain/`, `application/`, `adapters/`, `infrastructure/` | Project structure chapters | Critica |
| Repository pattern | `LedgerRepository`, `MarketDataRepository` | Repository chapters | Alta |
| Use case DTOs | `BacktestRunRequest`, `BacktestRunResult` | Use case chapters | Alta |
| In-memory tests | `FakeMarketDataSource`, `InMemoryLedger` | Testing chapters | Alta |

## Nota

Este mapa no sustituye a la fuente original. Sirve para que un agente encuentre rapido la zona probable antes de abrir el PDF/EPUB.
