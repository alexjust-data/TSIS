# Grokking Streaming Systems - Josh Fischer - Concept Index

        ## Menu

        - [Conceptos principales](#conceptos-principales)
        - [Activos TSIS sugeridos](#activos-tsis-sugeridos)
        - [Prioridad](#prioridad)

        ## Conceptos principales

        | Concepto | Paginas | Artefacto TSIS |
        |---|---:|---|
        | Event stream graph | 123-161 | `EventPipelineGraph` |
| Delivery semantics | 162-207 | `EventDeliveryContract` |
| Windowed computation | 223-263 | `WindowPolicy` |
| Stream joins | 264-296 | `TemporalJoinPolicy` |
| Backpressure | 297-328 | `ReplayBackpressurePolicy` |
| Stateful computation | 329-362 | `OnlineStateStore` |

        ## Activos TSIS sugeridos

        - `EventPipelineGraph`
- `EventDeliveryContract`
- `WindowPolicy`
- `TemporalJoinPolicy`
- `ReplayBackpressurePolicy`
- `OnlineStateStore`

        ## Prioridad

        ```text
        v0.1: extraer solo contratos/tests/gates que afectan al vertical slice
        v0.2: formalizar arquitectura y data lifecycle
        v0.3: automatizar CI/CD, metrics, risk reviews y governance
        ```
