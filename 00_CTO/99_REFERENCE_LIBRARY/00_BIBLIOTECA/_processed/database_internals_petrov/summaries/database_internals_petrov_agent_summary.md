# Database Internals - Alex Petrov

        Resumen operativo para agentes TSIS.

        ## Menu

        - [Resumen ejecutivo](#resumen-ejecutivo)
        - [Rol dentro de TSIS](#rol-dentro-de-tsis)
        - [Mapa rapido](#mapa-rapido)
        - [Blueprint TSIS derivado](#blueprint-tsis-derivado)
        - [Quality gates para agentes](#quality-gates-para-agentes)
        - [Limitaciones](#limitaciones)

        ## Resumen ejecutivo

        Referencia de fundamentos de almacenamiento y sistemas distribuidos: file formats, B-trees, LSM, WAL/recovery, concurrency, MVCC, consistency, anti-entropy, transactions y consensus.

        ## Rol dentro de TSIS

        No hay que construir una base de datos; sirve para tomar mejores decisiones sobre Parquet/DuckDB/indices/caches/logs, durabilidad y consistencia de ledgers.

        ## Mapa rapido

        | Bloque | Paginas | Uso TSIS |
        |---|---:|---|
        | DBMS architecture | 24-42 | Row/column layout, data/index files, immutability, ordering. |
| File formats | 67-84 | Binary encoding, page structure, versioning, checksums. |
| Transactions/recovery | 106-142 | Buffering, log semantics, ARIES, isolation, MVCC, locks. |
| LSM storage | 167-207 | LSM, SSTables, Bloom filters, amplification. |
| Distributed systems overview | 216-243 | Clocks, partial failures, partitions, failure models. |
| Replication/consistency | 267-299 | CAP, ordering, linearizability, eventual/tunable consistency. |
| Distributed transactions | 319-343 | 2PC/3PC, partitioning, coordination avoidance. |
| Consensus | 346-383 | Paxos/Raft y broadcast atomico. |

        ## Blueprint TSIS derivado

        - `CanonicalFileContract`
- `LedgerRecoveryPolicy`
- `ConcurrentRunIsolation`
- `IndexingAndCachePolicy`
- `ConsistencyContract`

        ## Quality gates para agentes

        - No convertir esta fuente en arquitectura TSIS sin definir primero el componente afectado.
        - Anclar cada decision a un artefacto TSIS concreto: contrato, clase, ledger, test, policy o ADR.
        - Si una recomendacion introduce complejidad distribuida, documentar el tradeoff antes de implementarla.
        - Toda idea que afecte replay/live debe acabar con test de equivalencia historico-online.
        - Los conceptos de datos deben traducirse a schema, lineage, retention, replay y validation gates.

        ## Limitaciones

        Muy bajo nivel. Usar para decisiones de datos/consistencia, no para implementar storage engine propio.
