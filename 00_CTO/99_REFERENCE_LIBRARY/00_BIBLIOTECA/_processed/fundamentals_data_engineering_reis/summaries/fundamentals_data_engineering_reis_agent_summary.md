# Fundamentals of Data Engineering - Joe Reis / Matt Housley

        Resumen operativo para agentes TSIS.

        ## Menu

        - [Resumen ejecutivo](#resumen-ejecutivo)
        - [Rol dentro de TSIS](#rol-dentro-de-tsis)
        - [Mapa rapido](#mapa-rapido)
        - [Blueprint TSIS derivado](#blueprint-tsis-derivado)
        - [Quality gates para agentes](#quality-gates-para-agentes)
        - [Limitaciones](#limitaciones)

        ## Resumen ejecutivo

        Mapa completo del ciclo de vida de datos: generation, storage, ingestion, transformation, serving, DataOps, architecture, security, governance, orchestration y live data stack.

        ## Rol dentro de TSIS

        Fuente principal para convertir Polygon/DAS/haltes/corporate actions/outputs Parquet en una data foundation gobernada.

        ## Mapa rapido

        | Bloque | Paginas | Uso TSIS |
        |---|---:|---|
        | Data engineering described | 18-57 | Roles, responsabilidades y madurez. |
| Data engineering lifecycle | 60-108 | Generation, storage, ingestion, transformation, serving y undercurrents. |
| Data architecture | 111-165 | Principios: failure, scalability, loose coupling, reversible decisions, event-driven, lambda/kappa/dataflow. |
| Technology choices | 171-222 | Build/buy, modularity, containers, performance, orchestration. |
| Source systems | 225-272 | Files, APIs, OLTP, CDC, logs, messages, streams, types of time. |
| Storage | 275-336 | Object storage, streaming storage, indexes, partitioning, schema, retention. |
| Ingestion | 338-387 | Bounded/unbounded, ordering, replay, DLQ, CDC, queues. |
| Modeling/transformation | 388-450 | Query performance, streaming modeling, transformations. |
| Serving/security/future | 453-521 | Data products, ML serving, reverse ETL, security/privacy, live data stack. |

        ## Blueprint TSIS derivado

        - `TSISDataLifecycle`
- `DataOpsPractice`
- `DataArchitecturePrinciples`
- `SourceSystemContract`
- `StorageAndRetentionPolicy`
- `IngestionReliabilityPolicy`
- `DataProductContract`

        ## Quality gates para agentes

        - No convertir esta fuente en arquitectura TSIS sin definir primero el componente afectado.
        - Anclar cada decision a un artefacto TSIS concreto: contrato, clase, ledger, test, policy o ADR.
        - Si una recomendacion introduce complejidad distribuida, documentar el tradeoff antes de implementarla.
        - Toda idea que afecte replay/live debe acabar con test de equivalencia historico-online.
        - Los conceptos de datos deben traducirse a schema, lineage, retention, replay y validation gates.

        ## Limitaciones

        Amplio y general. Usar para gobernanza de datos; complementar con Database Internals para bajo nivel y Streaming Systems para event-time.
