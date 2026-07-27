# Fundamentals of Software Architecture, 2nd Edition - Mark Richards / Neal Ford

        Resumen operativo para agentes TSIS.

        ## Menu

        - [Resumen ejecutivo](#resumen-ejecutivo)
        - [Rol dentro de TSIS](#rol-dentro-de-tsis)
        - [Mapa rapido](#mapa-rapido)
        - [Blueprint TSIS derivado](#blueprint-tsis-derivado)
        - [Quality gates para agentes](#quality-gates-para-agentes)
        - [Limitaciones](#limitaciones)

        ## Resumen ejecutivo

        Referencia principal de arquitectura: characteristics, tradeoffs, modularity, fitness functions, styles, event-driven, modular monolith, microservices, ADRs, risk storming, diagrams y team effectiveness.

        ## Rol dentro de TSIS

        Sirve para escribir `TSIS_BACKTEST_ENGINE_ARCHITECTURE_V0_1.md` con criterios explicitos, ADRs y fitness functions.

        ## Mapa rapido

        | Bloque | Paginas | Uso TSIS |
        |---|---:|---|
        | Architecture thinking | 19-73 | Decision making, tradeoffs, business drivers. |
| Modularity/characteristics | 75-181 | Cohesion, coupling, architecture characteristics, fitness functions. |
| Components/scope | 185-236 | Architectural quanta, logical components y coupling. |
| Styles | 244-647 | Layered, modular monolith, pipeline, microkernel, service-based, event-driven, space-based, microservices. |
| Choosing style / patterns | 647-690 | Decision criteria, CQRS, orchestration/choreography. |
| ADRs | 692-723 | Architecture decision records y standards. |
| Risk/diagrams/teams | 726-805 | Risk storming, C4/UML/ArchiMate, checklists. |
| Intersections/laws | 837-886 | Architecture with data, engineering practices, sync vs async, why over how. |

        ## Blueprint TSIS derivado

        - `ArchitectureCharacteristicCatalog`
- `ArchitectureFitnessFunction`
- `TSISModularMonolith`
- `EventDrivenArchitectureStyle`
- `ArchitectureDecisionRecord`
- `ArchitectureRiskRegister`
- `ArchitectureDiagramSet`

        ## Quality gates para agentes

        - No convertir esta fuente en arquitectura TSIS sin definir primero el componente afectado.
        - Anclar cada decision a un artefacto TSIS concreto: contrato, clase, ledger, test, policy o ADR.
        - Si una recomendacion introduce complejidad distribuida, documentar el tradeoff antes de implementarla.
        - Toda idea que afecte replay/live debe acabar con test de equivalencia historico-online.
        - Los conceptos de datos deben traducirse a schema, lineage, retention, replay y validation gates.

        ## Limitaciones

        No decide por TSIS. Obliga a documentar tradeoffs y fitness functions antes de elegir estilos.
