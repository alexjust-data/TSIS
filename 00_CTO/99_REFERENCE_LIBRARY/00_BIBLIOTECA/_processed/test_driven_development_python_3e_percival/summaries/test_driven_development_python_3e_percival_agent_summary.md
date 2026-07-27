# Test-Driven Development with Python, 3rd Edition - Harry J. W. Percival

        Resumen operativo para agentes TSIS.

        ## Menu

        - [Resumen ejecutivo](#resumen-ejecutivo)
        - [Rol dentro de TSIS](#rol-dentro-de-tsis)
        - [Mapa rapido](#mapa-rapido)
        - [Blueprint TSIS derivado](#blueprint-tsis-derivado)
        - [Quality gates para agentes](#quality-gates-para-agentes)
        - [Limitaciones](#limitaciones)

        ## Resumen ejecutivo

        Fuente practica de TDD en Python: functional tests, unit tests, red/green/refactor, regression tests, test isolation, Docker, env vars, deployment automation.

        ## Rol dentro de TSIS

        Sirve para convertir el backtester en software verificable: cada bug de temporalidad, fill, ledger o replay debe acabar como test.

        ## Mapa rapido

        | Bloque | Paginas | Uso TSIS |
        |---|---:|---|
        | Functional test first | 45-76 | Test funcional para definir el comportamiento visible. |
| Unit tests and cycle | 80-105 | Unit tests, view/function cycle y tracebacks. |
| Refactoring/TDD process | 113-141 | Refactor y double-loop TDD. |
| Database tests | 145-200 | Testing DB/migrations y pruebas de persistencia. |
| Functional test isolation | 205-215 | Isolation y waits correctos. |
| Incremental work/regression | 225-292 | Pasos pequenos, regression tests y refactor. |
| Docker/production | 335-409 | Container, env vars, logging y production readiness. |
| IaC/deploy | 417-452 | Ansible y despliegue automatizado. |

        ## Blueprint TSIS derivado

        - `BacktesterAcceptanceTest`
- `UnitTestCycle`
- `OutsideInTDDWorkflow`
- `RegressionTestHarness`
- `TestIsolationPolicy`
- `RuntimeTestEnvironment`

        ## Quality gates para agentes

        - No convertir esta fuente en arquitectura TSIS sin definir primero el componente afectado.
        - Anclar cada decision a un artefacto TSIS concreto: contrato, clase, ledger, test, policy o ADR.
        - Si una recomendacion introduce complejidad distribuida, documentar el tradeoff antes de implementarla.
        - Toda idea que afecte replay/live debe acabar con test de equivalencia historico-online.
        - Los conceptos de datos deben traducirse a schema, lineage, retention, replay y validation gates.

        ## Limitaciones

        Django-web oriented. Extraer disciplina de tests, no frameworks web.
