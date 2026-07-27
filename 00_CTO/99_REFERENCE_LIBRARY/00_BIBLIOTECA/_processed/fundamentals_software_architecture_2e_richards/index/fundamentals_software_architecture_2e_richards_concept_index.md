# Fundamentals of Software Architecture, 2nd Edition - Mark Richards / Neal Ford - Concept Index

        ## Menu

        - [Conceptos principales](#conceptos-principales)
        - [Activos TSIS sugeridos](#activos-tsis-sugeridos)
        - [Prioridad](#prioridad)

        ## Conceptos principales

        | Concepto | Paginas | Artefacto TSIS |
        |---|---:|---|
        | Architecture characteristics | 109-181 | `ArchitectureCharacteristicCatalog` |
| Fitness functions | 170-181 | `ArchitectureFitnessFunction` |
| Modular monolith | 305-326 | `TSISModularMonolith` |
| Pipeline style | 333-353 | `DataProcessingPipelineStyle` |
| Event-driven architecture | 414-511 | `EventDrivenArchitectureStyle` |
| Microservices tradeoff | 598-643 | `MicroservicesDecisionGate` |
| ADR | 692-723 | `ArchitectureDecisionRecord` |
| Risk storming | 726-754 | `ArchitectureRiskRegister` |
| C4 diagrams | 755-768 | `ArchitectureDiagramSet` |

        ## Activos TSIS sugeridos

        - `ArchitectureCharacteristicCatalog`
- `ArchitectureFitnessFunction`
- `TSISModularMonolith`
- `EventDrivenArchitectureStyle`
- `ArchitectureDecisionRecord`
- `ArchitectureRiskRegister`
- `ArchitectureDiagramSet`

        ## Prioridad

        ```text
        v0.1: extraer solo contratos/tests/gates que afectan al vertical slice
        v0.2: formalizar arquitectura y data lifecycle
        v0.3: automatizar CI/CD, metrics, risk reviews y governance
        ```
