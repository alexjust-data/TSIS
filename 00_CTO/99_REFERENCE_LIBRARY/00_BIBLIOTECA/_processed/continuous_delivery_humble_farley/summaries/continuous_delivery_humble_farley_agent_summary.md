# Continuous Delivery - Jez Humble / David Farley

        Resumen operativo para agentes TSIS.

        ## Menu

        - [Resumen ejecutivo](#resumen-ejecutivo)
        - [Rol dentro de TSIS](#rol-dentro-de-tsis)
        - [Mapa rapido](#mapa-rapido)
        - [Blueprint TSIS derivado](#blueprint-tsis-derivado)
        - [Quality gates para agentes](#quality-gates-para-agentes)
        - [Limitaciones](#limitaciones)

        ## Resumen ejecutivo

        Referencia para pipeline de entrega: configuration management, CI, test strategy, deployment pipeline, acceptance tests, capacity tests, releases, environments, data migrations y auditoria.

        ## Rol dentro de TSIS

        Convierte TSIS en software reproducible: cada cambio al backtester debe pasar tests, gates, fixtures, datos/versiones y pipeline antes de confiar en resultados.

        ## Mapa rapido

        | Bloque | Paginas | Uso TSIS |
        |---|---:|---|
        | Delivery problem and principles | 37-63 | Antipatterns de release y principios de entrega. |
| Configuration management | 65-88 | Version control, dependencies, environments. |
| Continuous integration | 89-116 | Commit frecuente, feedback rapido, practicas esenciales. |
| Testing strategy | 117-135 | Tipos de tests y proceso. |
| Deployment pipeline | 139-174 | Commit stage, acceptance gate, release prep y metrics. |
| Acceptance/capacity tests | 221-282 | Acceptance, NFRs, capacity y performance. |
| Deploy/release | 283-307 | Rollback, zero downtime, emergency fixes. |
| Infrastructure/data/dependencies | 311-413 | Infra, monitoring, database scripting, test data, dependency graph. |
| Management/audit | 451-476 | Risk management, compliance, audit. |

        ## Blueprint TSIS derivado

        - `BacktesterDeliveryPipeline`
- `CommitGate`
- `AcceptanceTestGate`
- `ReplayCapacityTest`
- `DataSchemaMigrationPolicy`
- `RunAuditTrail`

        ## Quality gates para agentes

        - No convertir esta fuente en arquitectura TSIS sin definir primero el componente afectado.
        - Anclar cada decision a un artefacto TSIS concreto: contrato, clase, ledger, test, policy o ADR.
        - Si una recomendacion introduce complejidad distribuida, documentar el tradeoff antes de implementarla.
        - Toda idea que afecte replay/live debe acabar con test de equivalencia historico-online.
        - Los conceptos de datos deben traducirse a schema, lineage, retention, replay y validation gates.

        ## Limitaciones

        Libro de delivery general; adaptar a entorno local TSIS sin sobredimensionar infra.
