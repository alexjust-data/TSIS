# Database Internals - Alex Petrov - Concept Index

        ## Menu

        - [Conceptos principales](#conceptos-principales)
        - [Activos TSIS sugeridos](#activos-tsis-sugeridos)
        - [Prioridad](#prioridad)

        ## Conceptos principales

        | Concepto | Paginas | Artefacto TSIS |
        |---|---:|---|
        | Column vs row storage | 30-34 | `StorageFormatDecision` |
| File format/version/checksum | 67-84 | `CanonicalFileContract` |
| WAL/recovery | 118-123 | `LedgerRecoveryPolicy` |
| Isolation/MVCC | 124-132 | `ConcurrentRunIsolation` |
| LSM/SSTable/Bloom | 167-194 | `IndexingAndCachePolicy` |
| Consistency models | 267-299 | `ConsistencyContract` |
| Consensus/Raft | 346-383 | `FutureDistributedCoordinator` |

        ## Activos TSIS sugeridos

        - `CanonicalFileContract`
- `LedgerRecoveryPolicy`
- `ConcurrentRunIsolation`
- `IndexingAndCachePolicy`
- `ConsistencyContract`

        ## Prioridad

        ```text
        v0.1: extraer solo contratos/tests/gates que afectan al vertical slice
        v0.2: formalizar arquitectura y data lifecycle
        v0.3: automatizar CI/CD, metrics, risk reviews y governance
        ```
