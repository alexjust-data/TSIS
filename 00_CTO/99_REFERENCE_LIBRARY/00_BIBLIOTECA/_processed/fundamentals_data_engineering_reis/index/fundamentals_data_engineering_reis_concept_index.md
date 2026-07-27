# Fundamentals of Data Engineering - Joe Reis / Matt Housley - Concept Index

        ## Menu

        - [Conceptos principales](#conceptos-principales)
        - [Activos TSIS sugeridos](#activos-tsis-sugeridos)
        - [Prioridad](#prioridad)

        ## Conceptos principales

        | Concepto | Paginas | Artefacto TSIS |
        |---|---:|---|
        | Data lifecycle | 60-82 | `TSISDataLifecycle` |
| DataOps | 98-104 | `DataOpsPractice` |
| Good data architecture | 111-165 | `DataArchitecturePrinciples` |
| Source systems and CDC | 225-240 | `SourceSystemContract` |
| Storage lifecycle/schema | 275-336 | `StorageAndRetentionPolicy` |
| Ingestion ordering/replay/DLQ | 338-362 | `IngestionReliabilityPolicy` |
| Streaming transformations | 432-445 | `StreamingFeaturePipeline` |
| Data products/serving | 453-483 | `DataProductContract` |

        ## Activos TSIS sugeridos

        - `TSISDataLifecycle`
- `DataOpsPractice`
- `DataArchitecturePrinciples`
- `SourceSystemContract`
- `StorageAndRetentionPolicy`
- `IngestionReliabilityPolicy`
- `DataProductContract`

        ## Prioridad

        ```text
        v0.1: extraer solo contratos/tests/gates que afectan al vertical slice
        v0.2: formalizar arquitectura y data lifecycle
        v0.3: automatizar CI/CD, metrics, risk reviews y governance
        ```
