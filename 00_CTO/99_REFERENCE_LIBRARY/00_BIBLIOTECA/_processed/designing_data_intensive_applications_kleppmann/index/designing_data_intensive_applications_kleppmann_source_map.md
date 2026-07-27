# Source Map - Designing Data-Intensive Applications

**book_id:** `designing_data_intensive_applications_kleppmann`  
**Fuente original:** `Martin-Kleppmann---Designing-Data-Intensive-Applications_-O’Reilly-Media-(2017).pdf`  
**Tipo de unidad:** `page`  
**Unidades:** 491  

## Mapa Estructural Extraido

| # | Nivel | Titulo/descripcion | Unidad |
|---|---|---|---|
| 1 | 0 | Cover |  |
| 2 | 0 | Copyright |  |
| 3 | 0 | Table of Contents |  |
| 4 | 0 | About this Book |  |
| 5 | 1 | Who Should Read this Book? |  |
| 6 | 1 | Scope of this Book |  |
| 7 | 1 | Outline of this Book |  |
| 8 | 1 | Early Release Status and Feedback |  |
| 9 | 0 | Part I. Foundations of Data Systems |  |
| 10 | 0 | Chapter 1. Reliable, Scalable and Maintainable Applications |  |
| 11 | 1 | Thinking About Data Systems |  |
| 12 | 1 | Reliability |  |
| 13 | 2 | Hardware faults |  |
| 14 | 2 | Software errors |  |
| 15 | 2 | Human errors |  |
| 16 | 2 | How important is reliability? |  |
| 17 | 1 | Scalability |  |
| 18 | 2 | Describing load |  |
| 19 | 2 | Describing performance |  |
| 20 | 2 | Approaches for coping with load |  |
| 21 | 1 | Maintainability |  |
| 22 | 2 | Operability: making life easy for operations |  |
| 23 | 2 | Simplicity: managing complexity |  |
| 24 | 2 | Evolvability: making change easy |  |
| 25 | 1 | Summary |  |
| 26 | 0 | Chapter 2. Data Models and Query Languages |  |
| 27 | 1 | Relational Model vs. Document Model |  |
| 28 | 2 | The birth of NoSQL |  |
| 29 | 2 | The object-relational mismatch |  |
| 30 | 2 | Many-to-one and many-to-many relationships |  |
| 31 | 2 | Are document databases repeating history? |  |
| 32 | 2 | Relational vs. document databases today |  |
| 33 | 1 | Query Languages for Data |  |
| 34 | 2 | Declarative queries on the web |  |
| 35 | 2 | MapReduce querying |  |
| 36 | 1 | Graph-like Data Models |  |
| 37 | 2 | Property graphs |  |
| 38 | 2 | The Cypher query language |  |
| 39 | 2 | Graph queries in SQL |  |
| 40 | 2 | Triple-stores and SPARQL |  |
| 41 | 2 | The foundation: Datalog |  |
| 42 | 1 | Summary |  |
| 43 | 0 | Chapter 3. Storage and Retrieval |  |
| 44 | 1 | Data Structures that Power Your Database |  |
| 45 | 2 | Hash indexes |  |
| 46 | 2 | SSTables and LSM-trees |  |
| 47 | 2 | B-trees |  |
| 48 | 2 | Other indexing structures |  |
| 49 | 2 | Keeping everything in memory |  |
| 50 | 1 | Transaction Processing or Analytics? |  |
| 51 | 2 | Data warehousing |  |
| 52 | 2 | Stars and snowflakes: schemas for analytics |  |
| 53 | 1 | Column-oriented storage |  |
| 54 | 2 | Column compression |  |
| 55 | 2 | Sort order in column storage |  |
| 56 | 2 | Writing to column-oriented storage |  |
| 57 | 2 | Aggregation: Data cubes and materialized views |  |
| 58 | 1 | Summary |  |
| 59 | 0 | Chapter 4. Encoding and Evolution |  |
| 60 | 1 | Formats for Encoding Data |  |
| 61 | 2 | Language-specific formats |  |
| 62 | 2 | JSON, XML and binary variants |  |
| 63 | 2 | Thrift and Protocol Buffers |  |
| 64 | 2 | Avro |  |
| 65 | 2 | The merits of schemas |  |
| 66 | 1 | Modes of Data Flow |  |
| 67 | 2 | Data flow through databases |  |
| 68 | 2 | Data flow through services: REST and RPC |  |
| 69 | 2 | Message passing data flow |  |
| 70 | 1 | Summary |  |
| 71 | 0 | Part II. Distributed Data |  |
| 72 | 0 | Chapter 5. Replication |  |
| 73 | 1 | Leaders and Followers |  |
| 74 | 2 | Synchronous vs. asynchronous replication |  |
| 75 | 2 | Setting up new followers |  |
| 76 | 2 | Handling node outages |  |
| 77 | 2 | Implementation of replication logs |  |
| 78 | 1 | Problems With Replication Lag |  |
| 79 | 2 | Reading your own writes |  |
| 80 | 2 | Monotonic reads |  |
| 81 | 2 | Consistent prefix reads |  |
| 82 | 2 | Solutions for replication lag |  |
| 83 | 1 | Multi-leader replication |  |
| 84 | 2 | Use cases for multi-leader replication |  |
| 85 | 2 | Handling write conflicts |  |
| 86 | 2 | Multi-leader replication topologies |  |
| 87 | 1 | Leaderless replication |  |
| 88 | 2 | Writing to the database when a node is down |  |
| 89 | 2 | Limitations of quorum consistency |  |
| 90 | 2 | Sloppy quorums and hinted handoff |  |
| 91 | 2 | Detecting concurrent writes |  |
| 92 | 1 | Summary |  |
| 93 | 0 | Chapter 6. Partitioning |  |
| 94 | 1 | Partitioning and replication |  |
| 95 | 1 | Partitioning of key-value data |  |
| 96 | 2 | Partitioning by key range |  |
| 97 | 2 | Partitioning by hash of key |  |
| 98 | 2 | Skewed workloads and relieving hot spots |  |
| 99 | 1 | Partitioning and secondary indexes |  |
| 100 | 2 | Partitioning secondary indexes by document |  |
| 101 | 2 | Partitioning secondary indexes by term |  |
| 102 | 1 | Rebalancing partitions |  |
| 103 | 2 | Strategies for rebalancing |  |
| 104 | 2 | Operations: automatic or manual rebalancing |  |
| 105 | 1 | Request routing |  |
| 106 | 2 | Parallel query execution |  |
| 107 | 1 | Summary |  |
| 108 | 0 | Chapter 7. Transactions |  |
| 109 | 1 | The slippery concept of a transaction |  |
| 110 | 2 | The meaning of ACID |  |
| 111 | 2 | Single-object and multi-object operations |  |
| 112 | 1 | Weak isolation levels |  |
| 113 | 2 | Read committed |  |
| 114 | 2 | Snapshot isolation and repeatable read |  |
| 115 | 2 | Preventing lost updates |  |
| 116 | 2 | Preventing write skew and phantoms |  |
| 117 | 1 | Serializability |  |
| 118 | 2 | Actual serial execution |  |
| 119 | 2 | Two-phase locking (2PL) |  |
| 120 | 2 | Serializable snapshot isolation (SSI) |  |

## Crosswalk TSIS

| Extraer | Encaja en TSIS | Secciones/Unidades | Prioridad |
|---|---|---|---|
| Event logs as system of record | `EventLog`, `Ledger`, `StateRebuilder` | Batch/stream/log chapters | Critica |
| Schema evolution | `SchemaVersioning`, `DataContract` | Encoding/schema evolution | Critica |
| Storage/index tradeoffs | `LedgerStorage`, `SymbolDateIndex` | Storage/index chapters | Alta |
| Consistency/idempotency | `IdempotencyKey`, `ConsistencyPolicy` | Distributed data chapters | Alta |
| Batch vs streaming views | `BatchPipeline`, `StreamPipeline`, `ReplaySemantics` | Batch/stream chapters | Critica |

## Nota

Este mapa no sustituye a la fuente original. Sirve para que un agente encuentre rapido la zona probable antes de abrir el PDF/EPUB.
