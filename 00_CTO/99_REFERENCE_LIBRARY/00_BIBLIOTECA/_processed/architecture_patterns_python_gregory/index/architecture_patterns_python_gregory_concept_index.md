# Architecture Patterns with Python - Harry Percival / Bob Gregory - Concept Index

        ## Menu

        - [Conceptos principales](#conceptos-principales)
        - [Activos TSIS sugeridos](#activos-tsis-sugeridos)
        - [Prioridad](#prioridad)

        ## Conceptos principales

        | Concepto | Paginas | Artefacto TSIS |
        |---|---:|---|
        | Domain model | 43-65 | `TSISDomainModel` |
| Repository pattern | 70-91 | `RepositoryPort` |
| Service layer | 116-136 | `ApplicationService` |
| Unit of Work | 156-172 | `UnitOfWork` |
| Aggregate boundary | 177-203 | `BacktestRunAggregate` |
| Message bus | 212-260 | `DomainEventBus` |
| Commands and handlers | 263-276 | `CommandHandler` |
| CQRS | 297-318 | `ReadModelProjection` |
| Dependency injection | 321-347 | `BootstrapContainer` |
| Validation | 408-419 | `ValidationLayer` |

        ## Activos TSIS sugeridos

        - `TSISDomainModel`
- `RepositoryPort`
- `ApplicationService`
- `UnitOfWork`
- `BacktestRunAggregate`
- `DomainEventBus`
- `CommandHandler`
- `ReadModelProjection`
- `BootstrapContainer`

        ## Prioridad

        ```text
        v0.1: extraer solo contratos/tests/gates que afectan al vertical slice
        v0.2: formalizar arquitectura y data lifecycle
        v0.3: automatizar CI/CD, metrics, risk reviews y governance
        ```
