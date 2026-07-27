# Database Internals - Alex Petrov - Source Map

        ## Menu

        - [Lectura por tarea](#lectura-por-tarea)
        - [Como citar en tareas TSIS](#como-citar-en-tareas-tsis)

        ## Lectura por tarea

        | Tarea / bloque | Paginas | Para que sirve |
        |---|---:|---|
        | DBMS architecture | 24-42 | Row/column layout, data/index files, immutability, ordering. |
| File formats | 67-84 | Binary encoding, page structure, versioning, checksums. |
| Transactions/recovery | 106-142 | Buffering, log semantics, ARIES, isolation, MVCC, locks. |
| LSM storage | 167-207 | LSM, SSTables, Bloom filters, amplification. |
| Distributed systems overview | 216-243 | Clocks, partial failures, partitions, failure models. |
| Replication/consistency | 267-299 | CAP, ordering, linearizability, eventual/tunable consistency. |
| Distributed transactions | 319-343 | 2PC/3PC, partitioning, coordination avoidance. |
| Consensus | 346-383 | Paxos/Raft y broadcast atomico. |

        ## Como citar en tareas TSIS

        Usar esta fuente como:

        ```text
        Referencia de fundamentos de almacenamiento y sistemas distribuidos: file formats, B-trees, LSM, WAL/recovery, concurrency, MVCC, consistency, anti-entropy, transactions y consensus.
        ```

        Regla para agentes:

        ```text
        abrir primero este source_map, despues el agent_summary, y solo entonces el PDF original si hace falta detalle de pagina.
        ```
