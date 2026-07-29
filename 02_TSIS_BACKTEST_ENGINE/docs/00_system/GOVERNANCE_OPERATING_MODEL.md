# Governance Operating Model

Status: LIVE_POLICY
Last updated: 2026-07-29

## Principio

```text
Un gate = una capacidad científicamente utilizable
```

La governance protege rigor, reproducibilidad y trazabilidad. No debe sustituir
el desarrollo ni convertir correcciones menores en ciclos de autorización
separados.

## Qué Es Un Gate De Capacidad

Un gate de capacidad debe cerrar una unidad que pueda utilizarse o auditarse
como parte real del backtester:

- data preflight;
- replay determinista;
- event loop integrado;
- fill simulator;
- accounting;
- run manifest;
- trade ledger;
- portfolio slice;
- research runner.

## Qué No Debe Ser Un Gate Independiente

```text
un documento
una autorización intermedia
una corrección de imports
una corrección de packaging
una actualización de manifests
una sincronización rutinaria de governance
una corrección menor de tests o evidencia
```

Estas correcciones se resuelven dentro del gate abierto.

## Cuándo Reabrir Decisión

Una corrección requiere decisión nueva solo si altera materialmente:

- alcance;
- semántica;
- contrato;
- datos consumidos;
- modelo de ejecución;
- contabilidad;
- frontera arquitectónica congelada;
- riesgo de look-ahead;
- capacidad autorizada.

## Ciclo Operativo

```text
contrato y aceptación completos
→ autorización del incremento completo
→ implementación continua
→ tests y run
→ paquete final
→ revisión externa final
```

Si la revisión externa encuentra defectos menores de implementación, tests,
imports, evidencia o packaging, el gate permanece abierto y se corrige dentro
del mismo gate.

## Evidencia Económica

Antes del realismo específico small caps, los runs solo validan motor:

```text
ENGINE_VALIDATION_RUN
NOT_EDGE_EVIDENCE
NOT_ECONOMICALLY_REALISTIC
```

No se puede afirmar edge, rentabilidad o validez económica sin modelar las
restricciones materiales aplicables.

## Estado De Frontera De Estados

Este modelo operativo no autoriza:

```text
StateReplayFeed
Market State consumption
Event State consumption
state_bundle_physical_read
strategy access to Market/Event State
```
