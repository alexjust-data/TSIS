# Backtest Engine Governance Update Protocol

## Propósito

Definir cómo debe sincronizarse la autoridad documental de:

C:\TSIS_Data\00_CTO\14_BACKTEST_ENGINE

con la evidencia ejecutable generada en:

C:\TSIS_Data\02_TSIS_BACKTEST_ENGINE

## Principio de separación

00_CTO\14_BACKTEST_ENGINE contiene:

- autoridad;
- decisiones;
- políticas;
- arquitectura;
- gates;
- trazabilidad;
- excepciones;
- estado institucional.

02_TSIS_BACKTEST_ENGINE contiene:

- código;
- contratos locales;
- configuraciones;
- tests;
- runs;
- manifests;
- evidencia ejecutable.

Governance referencia la evidencia del backtester, pero no debe duplicar código,
runs ni datasets.

## Cuándo es obligatoria la actualización

La actualización es obligatoria cuando un incremento:

1. cambia una decisión o política;
2. modifica un contrato;
3. abre o cierra un gate;
4. implementa una capacidad;
5. cambia una autorización;
6. genera nuevas pruebas o evidencia;
7. introduce limitaciones o excepciones;
8. sustituye documentación viva;
9. cambia el siguiente incremento autorizado.

Las correcciones tipográficas sin efecto semántico solo requieren changelog
cuando alteren un artefacto gobernado.

## Secuencia obligatoria

### 1. Clasificar el incremento

Declarar:

- increment_id;
- domain;
- scope;
- change_type;
- authorization_before;
- authorization_after;
- affected_artifacts.

### 2. Resolver la autoridad

Determinar si el incremento está:

- AUTHORIZED;
- DOCUMENTATION_ONLY;
- PENDING_REVIEW;
- NOT_AUTHORIZED;
- SUPERSEDED;
- BLOCKED.

La existencia de código no demuestra autorización.

### 3. Actualizar los registros afectados

Revisar:

- DECISION_LEDGER.json;
- POLICY_REGISTER.json;
- TRACEABILITY_MATRIX.json;
- EXCEPTION_AND_WAIVER_REGISTER.json;
- gate o review correspondiente.

No es obligatorio modificar todos los registros si el incremento no los afecta,
pero debe evaluarse cada uno.

### 4. Registrar trazabilidad

Toda capacidad cerrada debe poder recorrer:

decision_id
→ policy_id
→ contract_artifact
→ implementation_artifact
→ acceptance_test
→ evidence_run
→ limitation_or_exception
→ gate_id

Los elementos inexistentes deben declararse explícitamente como:

- NOT_APPLICABLE;
- NOT_IMPLEMENTED;
- NOT_EXECUTED;
- MISSING_EVIDENCE;
- PENDING_AUTHORIZATION.

### 5. Actualizar documentación viva

Revisar:

- README.md;
- AGENTS.md;
- LOCAL_RULES.md;
- GOVERNANCE_README.md;
- guía técnica afectada;
- CHANGELOG.md.

Debe eliminarse cualquier puntero vivo contradictorio con el nuevo estado.

### 6. Validar

Antes de cerrar:

- todos los JSON deben parsear;
- los identificadores referenciados deben existir;
- no debe haber decision_id, policy_id o gate_id duplicado;
- los paths referenciados deben ser exactos;
- las afirmaciones de tests deben coincidir con resultados disponibles;
- debe distinguirse evidencia reproducida de evidencia histórica reportada;
- las restricciones NOT_AUTHORIZED deben permanecer cerradas;
- PACKAGE_MANIFEST.json debe regenerarse si controla hashes del contenido.

### 7. Emitir resultado

El agente debe informar:

- archivos del backtester modificados;
- archivos de governance modificados;
- decisiones y políticas afectadas;
- gate anterior;
- gate resultante;
- tests ejecutados;
- evidencia generada;
- limitaciones;
- siguiente gate;
- autorizaciones que continúan cerradas.

## Regla de cierre

Un incremento no puede declararse completamente cerrado cuando su governance
aplicable esté desactualizado.

En ese caso debe utilizarse un estado como:

IMPLEMENTATION_COMPLETE_GOVERNANCE_SYNC_PENDING

o:

DOCUMENT_CORRECTED_PENDING_GOVERNANCE_UPDATE

## Restricciones del State Provider

Hasta autorización explícita:

- FUTURE_PROVIDER_REGISTRY_INTEGRATION = NOT_AUTHORIZED
- StateReplayFeed = NOT_AUTHORIZED
- state_bundle_physical_read = BLOCKED
- backtest_strategy_execution_with_states = false
- Market State consumption = NOT_AUTHORIZED
- Event State consumption = NOT_AUTHORIZED

La documentación raíz de 00_CTO_APPLIED_ARCHITECTURE solo puede utilizarse
como contexto arquitectónico general.

09_STATE_CONSUMPTION_BOUNDARY\README.md solo puede referenciarse como frontera
futura cerrada.