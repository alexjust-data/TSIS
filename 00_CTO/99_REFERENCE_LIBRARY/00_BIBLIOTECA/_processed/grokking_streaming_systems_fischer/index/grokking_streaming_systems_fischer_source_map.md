# Grokking Streaming Systems - Josh Fischer - Source Map

        ## Menu

        - [Lectura por tarea](#lectura-por-tarea)
        - [Como citar en tareas TSIS](#como-citar-en-tareas-tsis)

        ## Lectura por tarea

        | Tarea / bloque | Paginas | Para que sirve |
        |---|---:|---|
        | Getting started / Hello streaming | 27-84 | Diferencia backend request/response, batch y stream; queues como fundamento. |
| Parallelization and grouping | 85-122 | Particionado, grouping y paralelismo para feed historico/replay. |
| Stream graph | 123-161 | DAG del pipeline; equivalente al grafo DataFeed -> State -> Strategy -> Ledger. |
| Delivery semantics | 162-207 | At-most/at-least/exactly-once como contrato de eventos y outputs. |
| Windowed computations | 223-263 | Ventanas para features, bars, sessions y agregaciones. |
| Join operations | 264-296 | Unir feeds/eventos sin introducir leakage temporal. |
| Backpressure | 297-328 | Control de capacidad si replay o live supera consumo. |
| Stateful computation | 329-362 | Estado online como ciudadano de primera clase. |

        ## Como citar en tareas TSIS

        Usar esta fuente como:

        ```text
        Introduccion practica a streaming: queues, stream graph, parallelization, delivery semantics, windows, joins, backpressure y stateful computation.
        ```

        Regla para agentes:

        ```text
        abrir primero este source_map, despues el agent_summary, y solo entonces el PDF original si hace falta detalle de pagina.
        ```
