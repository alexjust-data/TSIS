# AGENTS — Backtest Engine authority operating contract

Status: `ACTIVE`

## Scope

Authorized authority root:

```text
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE
```

Governed implementation root:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE
```

## Mandatory behavior

Before changing the backtester, resolve the applicable `policy_id`, `decision_id`, contract and gate. Fail closed if the intended change has no authority.

Every completed increment must update, when applicable:

```text
DECISION_LEDGER.json
POLICY_REGISTER.json
TRACEABILITY_MATRIX.json
EXCEPTION_AND_WAIVER_REGISTER.json
GATE_REGISTER.json
CHANGELOG.md
```

No gate may be recorded as closed without:

- bounded scope;
- explicit authorization;
- implementation bindings;
- acceptance-test bindings;
- evidence-run bindings when physical behavior is claimed;
- limitations and non-claims;
- status consistency across living documents.

## Current gate

```text
BT-GATE-012 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
BT-GATE-012_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED

CURRENT_GATE =
BT-GATE-013 / PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1

BT-GATE-013_CONTRACT =
CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW

BT-GATE-013_IMPLEMENTATION =
NOT_AUTHORIZED

PHYSICAL_RUN =
NOT_AUTHORIZED
```

Historical BT-GATE-006, BT-GATE-009 and BT-GATE-010 sections are superseded by this current-state block. They remain relevant as closed evidence, not as current gates.

## Frozen boundaries

Do not open through this authority increment:

```text
StateReplayFeed
Market State
Event State
state bundle physical reads
strategy state consumption
borrow or locate realism
broker realism
production
downstream
edge claims
```

Historical sections must be labeled `HISTORICAL_SNAPSHOT` or `SUPERSEDED`; they must not compete with the current-state block.

## Applied Architecture boundary

The root `AGENTS.md`, `README.md` and `CHANGELOG.md` of
`00_CTO_APPLIED_ARCHITECTURE` are context only. The
`09_STATE_CONSUMPTION_BOUNDARY/README.md` may be inspected only to maintain:

```text
FUTURE_PROVIDER_REGISTRY_INTEGRATION = NOT_AUTHORIZED
StateReplayFeed = NOT_AUTHORIZED
backtest_strategy_execution = false
state_bundle_physical_read = BLOCKED
```

Provider responsibilities are validation, resolution, construction/reuse and
StateBundle references. The Consumption Boundary would authorize a bounded
physical opening. A future consumer would read, type, order and replay under
its own contracts. None of those consumer actions is authorized now.

## Autoridad de mantenimiento

El agente del backtester está autorizado para mantener sincronizados los
registros de governance con evidencia verificable producida por
`02_TSIS_BACKTEST_ENGINE`.

Puede:

- registrar hechos demostrados;
- actualizar paths y referencias;
- añadir tests y runs como evidencia;
- corregir estados documentales obsoletos;
- abrir registros pendientes;
- marcar contradicciones;
- regenerar validaciones y manifests.

No puede, salvo instrucción explícita:

- autorizar una capacidad previamente NOT_AUTHORIZED;
- cerrar un gate que requiera revisión externa o aprobación humana;
- eliminar limitaciones sin evidencia;
- convertir una implementación en autoridad;
- activar consumo de Market State/Event State;
- autorizar StateReplayFeed o lectura física de StateBundles.

## 2026-07-29 | Historical BT-GATE-012 implementation acceptance evidence

```text
BT-GATE-012 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
BT-GATE-012_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED
ENGINE_TEST_SUITE = 106 tests OK
BT-GATE-012_VALIDATION_STATUS = PASS
BT-GATE-012_DETERMINISM_STATUS = PASS
BT-GATE-012_DETERMINISTIC_OUTPUT_HASH = 414aceb2bc80836f8fa821cd4d14071e54c86f3c7855c0a34c82ffd8b1c79182
NEXT_GATE = BT-GATE-013 / PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1_CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
```

BT-GATE-012 later closed as accepted. StateReplayFeed, Market State, Event State and provider integration remain closed.

## 2026-07-29 | BT-GATE-013 boundary corrected

```text
BT-GATE-013_NAME = PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
BT-GATE-013_NEW_BOUNDARY = PHYSICAL_013_ROWS_TO_ACCEPTED_REPLAY_ENGINE
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
SMALL_CAPS_RIGOROUS_RESEARCH_RUNNER = FUTURE_GATE_FAMILY_NOT_YET_OPEN
```

`BT-GATE-013` is not a small-caps research runner. It is the physical historical replay bridge from `013_ohlcv_1m_quote_guarded` rows into the accepted replay/portfolio engine. Future small-caps rigorous research capability remains deferred until the physical bar boundary, Market/Event State consumption gates, scaling/batch gates, tradability/execution-realism gates and statistical validation gates are separately authorized.

## 2026-07-29 | BT-GATE-013 contract draft placed in canonical backtester docs

```text
BT-GATE-013 = PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
BT-GATE-013_CONTRACT = HISTORICAL_CONTRACT_DRAFT_PENDING_OWNER_REVIEW_SUPERSEDED_BY_CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
CONTRACT_ARTIFACT = docs/00_system/14_BT_GATE_013_PHYSICAL_HISTORICAL_REPLAY_SLICE_CONTRACT_V0_1.md
```

The contract draft was copied into the canonical backtester document location. This does not authorize implementation, Market State consumption, Event State consumption, StateReplayFeed, provider modification or full 2005-2026 execution.

## 2026-07-29 | BT-GATE-013 corrected contract pending final owner review

```text
READ_ONLY_REVIEW = ACCEPTED
BT-GATE-013_CONTRACT = CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
PROVIDER_EVIDENCE_REQUIRED = false
```

No implementation, physical run, StateReplayFeed, Market State, Event State or provider modification is authorized by this correction.

