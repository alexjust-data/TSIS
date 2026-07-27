# Architecture Patterns with Python - Harry Percival / Bob Gregory

        Resumen operativo para agentes TSIS.

        ## Menu

        - [Resumen ejecutivo](#resumen-ejecutivo)
        - [Rol dentro de TSIS](#rol-dentro-de-tsis)
        - [Mapa rapido](#mapa-rapido)
        - [Blueprint TSIS derivado](#blueprint-tsis-derivado)
        - [Quality gates para agentes](#quality-gates-para-agentes)
        - [Limitaciones](#limitaciones)

        ## Resumen ejecutivo

        Fuente practica para DDD tactico en Python: domain model, repository, service layer, unit of work, aggregates, message bus, commands/events, CQRS, dependency injection y validation.

        ## Rol dentro de TSIS

        Probablemente la mejor fuente de esta tanda para el Camino B: motor Python propio con dominio limpio, puertos/adaptadores y testabilidad.

        ## Mapa rapido

        | Bloque | Paginas | Uso TSIS |
        |---|---:|---|
        | Introduction | 29-37 | Encapsulation, layering, dependency inversion y domain model. |
| Domain model | 43-65 | Value objects, entities y domain services. |
| Repository pattern | 70-91 | Abstraccion de persistencia y fake repositories. |
| Service layer | 116-136 | Use cases separados de frameworks/API. |
| TDD high/low gear | 142-154 | Tipo de test segun capa. |
| Unit of Work | 156-172 | Transacciones, commit/rollback y repositorios. |
| Aggregates | 177-203 | Consistency boundaries y concurrencia optimista. |
| Message bus | 212-260 | Domain events y handlers. |
| Commands / events / CQRS / DI | 263-347 | Command handlers, read models y bootstrapping. |
| Validation | 408-419 | Validacion sintactica, semantica y pragmatica. |

        ## Blueprint TSIS derivado

        - `TSISDomainModel`
- `RepositoryPort`
- `ApplicationService`
- `UnitOfWork`
- `BacktestRunAggregate`
- `DomainEventBus`
- `CommandHandler`
- `ReadModelProjection`
- `BootstrapContainer`

        ## Quality gates para agentes

        - No convertir esta fuente en arquitectura TSIS sin definir primero el componente afectado.
        - Anclar cada decision a un artefacto TSIS concreto: contrato, clase, ledger, test, policy o ADR.
        - Si una recomendacion introduce complejidad distribuida, documentar el tradeoff antes de implementarla.
        - Toda idea que afecte replay/live debe acabar con test de equivalencia historico-online.
        - Los conceptos de datos deben traducirse a schema, lineage, retention, replay y validation gates.

        ## Limitaciones

        Ejemplos de negocio distintos, pero patrones directamente transferibles al backtester TSIS.
