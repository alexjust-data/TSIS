# Continuous Delivery - Jez Humble / David Farley - Concept Index

        ## Menu

        - [Conceptos principales](#conceptos-principales)
        - [Activos TSIS sugeridos](#activos-tsis-sugeridos)
        - [Prioridad](#prioridad)

        ## Conceptos principales

        | Concepto | Paginas | Artefacto TSIS |
        |---|---:|---|
        | Deployment pipeline | 139-174 | `BacktesterDeliveryPipeline` |
| Commit stage | 203-219 | `CommitGate` |
| Acceptance tests | 221-256 | `AcceptanceTestGate` |
| Capacity testing | 259-282 | `ReplayCapacityTest` |
| Database/data changes | 359-377 | `DataSchemaMigrationPolicy` |
| Audit/compliance | 451-476 | `RunAuditTrail` |

        ## Activos TSIS sugeridos

        - `BacktesterDeliveryPipeline`
- `CommitGate`
- `AcceptanceTestGate`
- `ReplayCapacityTest`
- `DataSchemaMigrationPolicy`
- `RunAuditTrail`

        ## Prioridad

        ```text
        v0.1: extraer solo contratos/tests/gates que afectan al vertical slice
        v0.2: formalizar arquitectura y data lifecycle
        v0.3: automatizar CI/CD, metrics, risk reviews y governance
        ```
