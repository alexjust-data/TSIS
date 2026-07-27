# Streaming Systems - Tyler Akidau, Slava Chernyak, Reuven Lax - Concept Index

        ## Menu

        - [Conceptos principales](#conceptos-principales)
        - [Activos TSIS sugeridos](#activos-tsis-sugeridos)
        - [Prioridad](#prioridad)

        ## Conceptos principales

        | Concepto | Paginas | Artefacto TSIS |
        |---|---:|---|
        | Event time vs processing time | 23-35 | `EventClockPolicy` |
| Watermarks | 85-122 | `WatermarkPolicy` |
| Triggers and lateness | 59-76 | `LateDataPolicy` |
| Exactly once and side effects | 149-170 | `IdempotentSinkContract` |
| Streams and tables | 174-236 | `StateTableMaterialization` |
| Windowed joins | 334-340 | `WindowedTemporalJoin` |

        ## Activos TSIS sugeridos

        - `EventClockPolicy`
- `WatermarkPolicy`
- `LateDataPolicy`
- `IdempotentSinkContract`
- `StateTableMaterialization`
- `WindowedTemporalJoin`

        ## Prioridad

        ```text
        v0.1: extraer solo contratos/tests/gates que afectan al vertical slice
        v0.2: formalizar arquitectura y data lifecycle
        v0.3: automatizar CI/CD, metrics, risk reviews y governance
        ```
