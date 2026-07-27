# Software Engineering at Google - Titus Winters / Tom Manshreck / Hyrum Wright

        Resumen operativo para agentes TSIS.

        ## Menu

        - [Resumen ejecutivo](#resumen-ejecutivo)
        - [Rol dentro de TSIS](#rol-dentro-de-tsis)
        - [Mapa rapido](#mapa-rapido)
        - [Blueprint TSIS derivado](#blueprint-tsis-derivado)
        - [Quality gates para agentes](#quality-gates-para-agentes)
        - [Limitaciones](#limitaciones)

        ## Resumen ejecutivo

        Referencia de ingenieria a largo plazo: time/change/scale, Hyrum's Law, knowledge sharing, documentation, code review, test strategy, fakes, large tests, version control, build systems, static analysis, dependencies, large-scale changes, CI/CD.

        ## Rol dentro de TSIS

        Fuente para gobernar el trabajo con agentes: cambios pequenos, docs canonicas, tests mantenibles, review, dependencia controlada y evolucion segura.

        ## Mapa rapido

        | Bloque | Paginas | Uso TSIS |
        |---|---:|---|
        | Software engineering thesis | 19-51 | Programar bajo tiempo, cambio, escala y tradeoffs. |
| Knowledge/docs/culture | 56-118, 307-342 | No esconder codigo, fuentes canonicas, documentacion como codigo. |
| Productivity metrics | 209-233 | Goals, signals, metrics. |
| Style/code review | 237-305 | Reglas, review flow, small changes. |
| Testing overview/unit tests/test doubles/large tests | 343-500 | Test size/scope, maintainability, fakes, large tests. |
| Version/build/static analysis/deps | 523-729 | VCS, build philosophy, static analysis, dependency management. |
| Large-scale changes | 733-763 | Infra y proceso para cambios amplios. |
| CI/CD/compute | 766-868 | CI, CD, feature flags, release train, managed compute. |

        ## Blueprint TSIS derivado

        - `LongTermEngineeringPolicy`
- `CanonicalDocsPolicy`
- `CodeReviewPolicy`
- `TestSuiteStrategy`
- `DependencyGovernance`
- `CICDPolicy`

        ## Quality gates para agentes

        - No convertir esta fuente en arquitectura TSIS sin definir primero el componente afectado.
        - Anclar cada decision a un artefacto TSIS concreto: contrato, clase, ledger, test, policy o ADR.
        - Si una recomendacion introduce complejidad distribuida, documentar el tradeoff antes de implementarla.
        - Toda idea que afecte replay/live debe acabar con test de equivalencia historico-online.
        - Los conceptos de datos deben traducirse a schema, lineage, retention, replay y validation gates.

        ## Limitaciones

        Practicas de Google no se copian literalmente. Extraer principios escalables para un sistema local con agentes.
