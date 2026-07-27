# Software Engineering at Google - Titus Winters / Tom Manshreck / Hyrum Wright - Concept Index

        ## Menu

        - [Conceptos principales](#conceptos-principales)
        - [Activos TSIS sugeridos](#activos-tsis-sugeridos)
        - [Prioridad](#prioridad)

        ## Conceptos principales

        | Concepto | Paginas | Artefacto TSIS |
        |---|---:|---|
        | Time/change/scale | 19-51 | `LongTermEngineeringPolicy` |
| Canonical knowledge | 82-118 | `CanonicalDocsPolicy` |
| Engineering metrics | 209-233 | `EngineeringMetricsPolicy` |
| Code review | 276-305 | `CodeReviewPolicy` |
| Test suite design | 343-380 | `TestSuiteStrategy` |
| Maintainable unit tests | 382-417 | `MaintainableTestPolicy` |
| Fakes and realism | 419-453 | `FakeVsRealTestDoublePolicy` |
| Large tests | 454-500 | `IntegrationAndSystemTestPolicy` |
| Dependency management | 684-729 | `DependencyGovernance` |
| CI/CD | 766-823 | `CICDPolicy` |

        ## Activos TSIS sugeridos

        - `LongTermEngineeringPolicy`
- `CanonicalDocsPolicy`
- `CodeReviewPolicy`
- `TestSuiteStrategy`
- `DependencyGovernance`
- `CICDPolicy`

        ## Prioridad

        ```text
        v0.1: extraer solo contratos/tests/gates que afectan al vertical slice
        v0.2: formalizar arquitectura y data lifecycle
        v0.3: automatizar CI/CD, metrics, risk reviews y governance
        ```
