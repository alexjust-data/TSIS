# Streaming Systems - Tyler Akidau, Slava Chernyak, Reuven Lax

        Resumen operativo para agentes TSIS.

        ## Menu

        - [Resumen ejecutivo](#resumen-ejecutivo)
        - [Rol dentro de TSIS](#rol-dentro-de-tsis)
        - [Mapa rapido](#mapa-rapido)
        - [Blueprint TSIS derivado](#blueprint-tsis-derivado)
        - [Quality gates para agentes](#quality-gates-para-agentes)
        - [Limitaciones](#limitaciones)

        ## Resumen ejecutivo

        Referencia rigurosa para event time, processing time, windowing, triggers, watermarks, allowed lateness, accumulation, exactly-once, side effects, streams/tables, SQL y joins.

        ## Rol dentro de TSIS

        Fuente principal para definir la semantica temporal de replay/live y evitar que el motor historico procese datos con reglas distintas al online.

        ## Mapa rapido

        | Bloque | Paginas | Uso TSIS |
        |---|---:|---|
        | Streaming 101 | 22-45 | Event time vs processing time; bounded/unbounded data. |
| What/Where/When/How | 48-80 | Transformaciones, windowing, triggers, watermarks, allowed lateness y accumulation. |
| Watermarks | 85-122 | Watermark creation/propagation y output timestamps. |
| Advanced windowing | 124-147 | Processing-time windows, session windows y custom windows. |
| Exactly-once and side effects | 149-170 | Determinismo, sources, sinks, side effects y archivos/BigQuery como sinks. |
| Streams and tables | 174-236 | Relaciones stream/table y materializacion. |
| SQL / joins | 238-357 | Streaming SQL y joins windowed/unwindowed. |
| Evolution of data processing | 360-407 | MapReduce, Flink, Kafka, Beam y modelos modernos. |

        ## Blueprint TSIS derivado

        - `EventClockPolicy`
- `WatermarkPolicy`
- `LateDataPolicy`
- `IdempotentSinkContract`
- `StateTableMaterialization`
- `WindowedTemporalJoin`

        ## Quality gates para agentes

        - No convertir esta fuente en arquitectura TSIS sin definir primero el componente afectado.
        - Anclar cada decision a un artefacto TSIS concreto: contrato, clase, ledger, test, policy o ADR.
        - Si una recomendacion introduce complejidad distribuida, documentar el tradeoff antes de implementarla.
        - Toda idea que afecte replay/live debe acabar con test de equivalencia historico-online.
        - Los conceptos de datos deben traducirse a schema, lineage, retention, replay y validation gates.

        ## Limitaciones

        No es un libro de trading. Su valor es semantica temporal y procesamiento de datos; adaptar con cuidado a market replay.
