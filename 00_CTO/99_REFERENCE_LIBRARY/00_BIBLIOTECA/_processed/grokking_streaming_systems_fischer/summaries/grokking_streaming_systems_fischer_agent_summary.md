# Grokking Streaming Systems - Josh Fischer

        Resumen operativo para agentes TSIS.

        ## Menu

        - [Resumen ejecutivo](#resumen-ejecutivo)
        - [Rol dentro de TSIS](#rol-dentro-de-tsis)
        - [Mapa rapido](#mapa-rapido)
        - [Blueprint TSIS derivado](#blueprint-tsis-derivado)
        - [Quality gates para agentes](#quality-gates-para-agentes)
        - [Limitaciones](#limitaciones)

        ## Resumen ejecutivo

        Introduccion practica a streaming: queues, stream graph, parallelization, delivery semantics, windows, joins, backpressure y stateful computation.

        ## Rol dentro de TSIS

        Sirve para aterrizar el event loop y el replay de TSIS como flujo de eventos con estado, no como batch disfrazado.

        ## Mapa rapido

        | Bloque | Paginas | Uso TSIS |
        |---|---:|---|
        | Getting started / Hello streaming | 27-84 | Diferencia backend request/response, batch y stream; queues como fundamento. |
| Parallelization and grouping | 85-122 | Particionado, grouping y paralelismo para feed historico/replay. |
| Stream graph | 123-161 | DAG del pipeline; equivalente al grafo DataFeed -> State -> Strategy -> Ledger. |
| Delivery semantics | 162-207 | At-most/at-least/exactly-once como contrato de eventos y outputs. |
| Windowed computations | 223-263 | Ventanas para features, bars, sessions y agregaciones. |
| Join operations | 264-296 | Unir feeds/eventos sin introducir leakage temporal. |
| Backpressure | 297-328 | Control de capacidad si replay o live supera consumo. |
| Stateful computation | 329-362 | Estado online como ciudadano de primera clase. |

        ## Blueprint TSIS derivado

        - `EventPipelineGraph`
- `EventDeliveryContract`
- `WindowPolicy`
- `TemporalJoinPolicy`
- `ReplayBackpressurePolicy`
- `OnlineStateStore`

        ## Quality gates para agentes

        - No convertir esta fuente en arquitectura TSIS sin definir primero el componente afectado.
        - Anclar cada decision a un artefacto TSIS concreto: contrato, clase, ledger, test, policy o ADR.
        - Si una recomendacion introduce complejidad distribuida, documentar el tradeoff antes de implementarla.
        - Toda idea que afecte replay/live debe acabar con test de equivalencia historico-online.
        - Los conceptos de datos deben traducirse a schema, lineage, retention, replay y validation gates.

        ## Limitaciones

        Libro pedagogico. Para semantica avanzada de event-time/watermarks/exactly-once usar Akidau et al.
